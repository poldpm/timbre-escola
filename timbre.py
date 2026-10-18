#!/usr/bin/env python3
"""
Timbre musical de l'escola - Raspberry Pi 3
Programador d'horaris + reproductor + web de gestio, tot en un.

La Raspberry toca una canco a l'atzar a cada hora de l'horari i l'apaga amb
un fos. Tot es gestiona des de la web: http://timbre.local (o la IP).

El rellotge Theben continua engegant l'amplificador: les hores de l'horari
han de coincidir amb les del rellotge.

Us:
  python3 timbre.py                -> servei normal (web + horari)
  python3 timbre.py --prova        -> toca una canco 20 s per provar el so
  python3 timbre.py --contrasenya  -> canvia la contrasenya de la web
"""

import functools
import getpass
import hashlib
import json
import logging
import os
import random
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import time
from datetime import date, datetime, time as dtime, timedelta
from pathlib import Path

# ----------------------------------------------------------------- AJUSTOS FIXOS
CODI = Path(__file__).resolve().parent
BASE = Path(os.environ.get("TIMBRE_DIR", CODI))
MUSICA = BASE / "musica"
WEB = CODI / "web"
CONFIG = BASE / "config.json"
CONFIG_BAK = BASE / "config.bak"      # copia identica, per si config.json es fa malbe
ESTAT = BASE / "estat.json"
HISTORIAL = BASE / "historial.jsonl"
RESERVA = BASE / "reserva.mp3"
CLAU = BASE / ".clau_sessio"
PORT = int(os.environ.get("TIMBRE_PORT", "80"))
DEMO = os.environ.get("TIMBRE_DEMO") == "1"          # proves sense so
SORTIDA_AUDIO = os.environ.get("TIMBRE_AUDIO", "alsa/plughw:CARD=Headphones,DEV=0")
EXTENSIONS = {".mp3", ".m4a", ".ogg", ".wav", ".flac", ".opus", ".aac"}
SOCKET_MPV = "/tmp/timbre-mpv.sock"
MPV_LOG = BASE / "mpv.log"            # errors de l'ultim cop que ha sonat
COMPROVA_INICI = 1.5  # s: si mpv s'atura abans d'aixo, no ha sonat
MARGE_RETARD = 30   # s: si la Raspberry arrenca tard, encara toca si fa menys d'aixo
INTENTS_LLIURES = 5            # errors de contrasenya seguits abans de bloquejar
ESPAI_RESERVAT = 300 * 1024 * 1024   # bytes lliures que sempre han de quedar a la SD

CONFIG_PER_DEFECTE = {
    "actiu": True,
    "silenci_data": None,
    "tocs": [
        {"nom": "Entrada del matí", "hora": "09:00", "durada": 60, "dies": [0, 1, 2, 3, 4], "actiu": True},
        {"nom": "Sortida al pati", "hora": "11:00", "durada": 60, "dies": [0, 1, 2, 3, 4], "actiu": True},
        {"nom": "Tornada del pati", "hora": "11:30", "durada": 60, "dies": [0, 1, 2, 3, 4], "actiu": True},
        {"nom": "Entrada de la tarda", "hora": "15:00", "durada": 60, "dies": [0, 1, 2, 3, 4], "actiu": True},
    ],
    "festius": [],
    "cancons": {},
    "seleccio": {"mode": "cada_toc", "canco_fixa": None},
    "ajustos": {"volum": 100, "retard_inici": 3, "durada_fos": 3, "normalitza": True, "no_repetir": 20},
    "contrasenya": None,
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger("timbre")


# ----------------------------------------------------------------- CONFIGURACIO
LOCK = threading.RLock()
CFG = {}


def escriu_atomic(cami, text):
    """Escriu el fitxer sencer o gens: si marxa la llum a mig desar, queda l'anterior."""
    tmp = cami.with_name(cami.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(cami)
    try:
        fd = os.open(cami.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    except OSError:
        pass


def llegeix_config_desada():
    """Llegeix config.json o, si falta o esta malmes, la copia config.bak.
    Un fitxer malmes no s'esborra mai: es reanomena per poder-lo recuperar a ma."""
    for cami in (CONFIG, CONFIG_BAK):
        try:
            dades = json.loads(cami.read_text(encoding="utf-8"))
            if not isinstance(dades, dict):
                raise ValueError("no es un objecte JSON")
        except FileNotFoundError:
            continue
        except Exception as e:
            nom = f"config.malmes-{datetime.now():%Y%m%d-%H%M%S}"
            apartat, i = cami.with_name(nom + cami.suffix), 2
            while apartat.exists():
                apartat, i = cami.with_name(f"{nom}-{i}{cami.suffix}"), i + 1
            cami.replace(apartat)
            log.error("%s malmes (%s): l'aparto com a %s", cami.name, e, apartat.name)
            continue
        if cami == CONFIG_BAK:
            log.warning("config.json no es pot llegir: recupero la copia config.bak")
        return dades
    return None


def carrega_config():
    global CFG
    dades = json.loads(json.dumps(CONFIG_PER_DEFECTE))
    desada = llegeix_config_desada()
    if desada is not None:
        dades.update(desada)
        dades["ajustos"] = {**CONFIG_PER_DEFECTE["ajustos"], **dades.get("ajustos", {})}
        dades["seleccio"] = {**CONFIG_PER_DEFECTE["seleccio"], **dades.get("seleccio", {})}
    elif list(BASE.glob("config.malmes-*")):
        log.error("No hi ha cap configuracio bona: faig servir els valors per defecte")
    CFG = dades
    desa_config()


def desa_config():
    with LOCK:
        text = json.dumps(CFG, ensure_ascii=False, indent=1)
        escriu_atomic(CONFIG, text)
        escriu_atomic(CONFIG_BAK, text)


def cfg():
    with LOCK:
        return json.loads(json.dumps(CFG))


def valida_contrasenya_nova(text):
    """La contrasenya es un codi de 4 xifres (decisio d'en Pol, 18/10)."""
    if not codi_valid(text):
        raise Invalid("La contrasenya ha de ser un codi de 4 xifres")
    return text


def codi_valid(text):
    return isinstance(text, str) and len(text) == 4 and text.isascii() and text.isdigit()


def hash_contrasenya(text, sal=None):
    sal = sal or secrets.token_hex(8)
    h = hashlib.pbkdf2_hmac("sha256", text.encode(), sal.encode(), 120_000).hex()
    return f"{sal}${h}"


def comprova_contrasenya(text):
    desat = cfg().get("contrasenya")
    if not desat or not isinstance(text, str):
        return False
    sal = desat.split("$")[0]
    return secrets.compare_digest(hash_contrasenya(text, sal), desat)


# ----------------------------------------------------------------- VALIDACIO
class Invalid(Exception):
    pass


def enter(valor, minim, maxim, nom):
    try:
        return max(minim, min(maxim, int(valor)))
    except (TypeError, ValueError):
        raise Invalid(f"{nom} ha de ser un número")


def valida_tocs(tocs):
    res = []
    for t in tocs:
        try:
            h, m = (int(x) for x in str(t["hora"]).split(":")[:2])
            assert 0 <= h < 24 and 0 <= m < 60
            durada = int(t["durada"])
            assert 5 <= durada <= 900
            dies = sorted({int(d) for d in t.get("dies", []) if 0 <= int(d) <= 6})
        except Exception:
            raise Invalid(f"Toc incorrecte: {t.get('nom') or t.get('hora')}")
        res.append({"nom": str(t.get("nom", "")).strip()[:60] or f"Toc de les {h:02d}:{m:02d}",
                    "hora": f"{h:02d}:{m:02d}", "durada": durada, "dies": dies,
                    "actiu": bool(t.get("actiu", True))})
    return sorted(res, key=lambda x: x["hora"])


def valida_festius(festius):
    res = []
    for f in festius:
        try:
            ini = date.fromisoformat(f["inici"])
            fi = date.fromisoformat(f.get("fi") or f["inici"])
        except Exception:
            raise Invalid("Data de festiu incorrecta")
        if fi < ini:
            ini, fi = fi, ini
        res.append({"inici": ini.isoformat(), "fi": fi.isoformat(), "nom": str(f.get("nom", "")).strip()[:60]})
    return sorted(res, key=lambda x: x["inici"])


MODES = {"cada_toc", "dia", "setmana", "fixa"}


def valida_seleccio(d):
    mode = d.get("mode")
    if mode not in MODES:
        raise Invalid("Mode de selecció desconegut")
    fixa = d.get("canco_fixa") or None
    if fixa and (fixa != nom_segur(fixa) or not (MUSICA / fixa).is_file()):
        raise Invalid("Aquesta cançó no existeix")
    if mode == "fixa" and not fixa:
        raise Invalid("Tria quina cançó ha de sonar sempre")
    return {"mode": mode, "canco_fixa": fixa}


def valida_ajustos(a):
    try:
        return {
            "volum": max(0, min(100, int(a["volum"]))),
            "retard_inici": max(0.0, min(20.0, float(a["retard_inici"]))),
            "durada_fos": max(0.0, min(10.0, float(a["durada_fos"]))),
            "normalitza": bool(a["normalitza"]),
            "no_repetir": max(0, min(100, int(a["no_repetir"]))),
        }
    except Exception:
        raise Invalid("Ajustos incorrectes")


# ----------------------------------------------------------------- HORARI
def festiu_de(dia, c):
    d = dia.isoformat()
    for f in c["festius"]:
        if f["inici"] <= d <= f["fi"]:
            return f["nom"] or "Festiu"
    return None


def motiu_silenci(dia, c):
    if not c["actiu"]:
        return "Timbre aturat"
    if c.get("silenci_data") == dia.isoformat():
        return "Silenci avui"
    return festiu_de(dia, c)


def tocs_del_dia(dia, c):
    res = []
    for t in c["tocs"]:
        if not t["actiu"] or dia.weekday() not in t["dies"]:
            continue
        h, m = (int(x) for x in t["hora"].split(":"))
        res.append((datetime.combine(dia, dtime(h, m)), t))
    return sorted(res, key=lambda x: x[0])


def proper_toc(ara, c, marge=0):
    for d in range(0, 60):
        dia = (ara + timedelta(days=d)).date()
        if motiu_silenci(dia, c):
            continue
        for moment, t in tocs_del_dia(dia, c):
            if moment + timedelta(seconds=marge) > ara:
                return moment, t
    return None


# ----------------------------------------------------------------- CANCONS
_durades = {}
try:
    from mutagen import File as MutagenFile
except Exception:
    MutagenFile = None


def cancons():
    if not MUSICA.exists():
        return []
    return sorted((p for p in MUSICA.iterdir()
                   if p.is_file() and p.suffix.lower() in EXTENSIONS and not p.name.startswith(".")),
                  key=lambda p: p.name.lower())


def durada_de(p):
    if MutagenFile is None:
        return None
    clau = (p.name, p.stat().st_mtime)
    if clau not in _durades:
        try:
            _durades[clau] = round(MutagenFile(p).info.length)
        except Exception:
            _durades[clau] = None
    return _durades[clau]


def nom_segur(nom):
    nom = Path(nom.replace("\\", "/")).name
    nom = "".join(ch for ch in nom if ch.isalnum() or ch in " ._-()'&,!")
    return nom.strip(" .")


ESTAT_LOCK = threading.RLock()   # estat.json el toquen el programador i la web alhora


def llegeix_estat():
    try:
        return json.loads(ESTAT.read_text(encoding="utf-8"))
    except Exception:
        return {"tocades": []}


def desa_estat(estat):
    try:
        escriu_atomic(ESTAT, json.dumps(estat, ensure_ascii=False))
    except Exception:
        log.exception("No puc desar estat.json")


def actives(c):
    return [p for p in cancons() if c["cancons"].get(p.name, {}).get("activa", True)]


def tria_aleatoria(c, excepte=None):
    """Canco a l'atzar entre les actives, evitant les ultimes que han sonat."""
    with ESTAT_LOCK:
        return _tria_aleatoria(c, excepte)


def _tria_aleatoria(c, excepte):
    llista = actives(c)
    if not llista:
        if RESERVA.exists():
            log.warning("No hi ha cap canco activa: toco la de reserva")
            return RESERVA
        log.error("No hi ha cap canco!")
        return None
    estat = llegeix_estat()
    recents = estat.get("tocades", [])
    n = min(len(llista) // 2, c["ajustos"]["no_repetir"])
    evitar = set(recents[-n:]) if n else set()
    if excepte:
        evitar.add(excepte)
    triada = random.choice([p for p in llista if p.name not in evitar] or llista)
    estat["tocades"] = (recents + [triada.name])[-200:]
    desa_estat(estat)
    return triada


def clau_periode(mode, dia):
    if mode == "dia":
        return dia.isoformat()
    any_, setmana, _ = dia.isocalendar()
    return f"{any_}-S{setmana:02d}"


def canco_del_periode(c, dia=None, nova=False, forcada=None):
    """Mode dia/setmana: retorna la canco del periode actual (la tria si cal)."""
    with ESTAT_LOCK:
        return _canco_del_periode(c, dia, nova, forcada)


def _canco_del_periode(c, dia, nova, forcada):
    mode = c["seleccio"]["mode"]
    clau = clau_periode(mode, dia or date.today())
    estat = llegeix_estat()
    per = estat.get("periode") or {}
    actual = per.get("canco") if per.get("mode") == mode and per.get("clau") == clau else None
    valides = {p.name for p in actives(c)}
    if forcada:
        triada = MUSICA / forcada
    elif actual in valides and not nova:
        return MUSICA / actual
    else:
        triada = tria_aleatoria(c, excepte=actual if nova else None)
        if triada is None or triada == RESERVA:
            return triada
    estat = llegeix_estat()
    estat["periode"] = {"mode": mode, "clau": clau, "canco": triada.name}
    desa_estat(estat)
    log.info("Canco del periode %s: %s", clau, triada.name)
    return triada


def tria_canco(c):
    """Decideix quina canco sona segons el mode triat a la web."""
    mode = c["seleccio"]["mode"]
    if mode == "fixa":
        nom = c["seleccio"].get("canco_fixa")
        if nom and (MUSICA / nom).is_file():
            return MUSICA / nom
        log.warning("La canco fixa no existeix: en trio una a l'atzar")
        return tria_aleatoria(c)
    if mode in ("dia", "setmana"):
        return canco_del_periode(c)
    return tria_aleatoria(c)


# ----------------------------------------------------------------- HISTORIAL
SONATS = {}   # moment del toc (iso) -> canco
FALLATS = {}  # moment del toc (iso) -> {"canco", "error"}: ho ha intentat i no ha sonat


def registra(canco, motiu, segons, toc=None, error=None):
    entrada = {"t": datetime.now().isoformat(timespec="seconds"), "canco": canco,
               "motiu": motiu, "segons": round(segons)}
    if error:
        entrada["error"] = error
    if toc:
        entrada["toc"] = toc.isoformat()
        if error:
            FALLATS[entrada["toc"]] = {"canco": canco, "error": error}
        else:
            SONATS[entrada["toc"]] = canco
    try:
        with HISTORIAL.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entrada, ensure_ascii=False) + "\n")
    except Exception:
        pass


def llegeix_historial(n=200):
    try:
        linies = HISTORIAL.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    res = []
    for l in linies[-n:]:
        try:
            res.append(json.loads(l))
        except Exception:
            pass
    return res


def prepara_historial():
    try:
        linies = HISTORIAL.read_text(encoding="utf-8").splitlines()
        if len(linies) > 3000:
            HISTORIAL.write_text("\n".join(linies[-2000:]) + "\n", encoding="utf-8")
    except FileNotFoundError:
        pass
    for e in llegeix_historial(300):
        if "toc" in e:
            if e.get("error"):
                FALLATS[e["toc"]] = {"canco": e["canco"], "error": e["error"]}
            else:
                SONATS[e["toc"]] = e["canco"]


# ----------------------------------------------------------------- REPRODUCTOR
def ordre_mpv(ordre):
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            s.connect(SOCKET_MPV)
            s.sendall((json.dumps({"command": ordre}) + "\n").encode())
    except Exception:
        pass


def explica_error_mpv(codi):
    """Tradueix el que ha escrit mpv a un missatge entenedor per a la web."""
    try:
        linies = [l.strip() for l in MPV_LOG.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
    except Exception:
        linies = []
    text = "\n".join(linies).lower()
    if "audio device" in text or "audio driver" in text:
        return f"No s'ha pogut obrir la sortida d'àudio ({SORTIDA_AUDIO})"
    if "file format" in text or "no such file" in text:
        return "El fitxer no es pot reproduir (potser està malmès)"
    if codi == 0:
        return "La cançó s'ha acabat de seguida (mira on comença)"
    return (linies[-1][:200] if linies else f"El reproductor ha fallat (codi {codi})")


class Reproductor:
    def __init__(self):
        self.lock = threading.Lock()
        self.proc = None
        self.info = None
        self.gen = 0

    def toca(self, canco, segons, motiu, toc=None):
        c = cfg()
        aj = c["ajustos"]
        inici = c["cancons"].get(canco.name, {}).get("inici", 0) if canco.parent == MUSICA else 0
        if DEMO:
            args = ["sleep", str(int(segons) + 2)]
        else:
            args = ["mpv", "--no-video", "--msg-level=all=error", "--input-terminal=no", "--term-osd=no",
                    f"--audio-device={SORTIDA_AUDIO}", f"--volume={aj['volum']}",
                    f"--input-ipc-server={SOCKET_MPV}"]
            if inici:
                args.append(f"--start={inici}")
            if aj["normalitza"]:
                args.append("--af=lavfi=[loudnorm=I=-16:TP=-1.5:LRA=11]")
            args.append(str(canco))
        error = None
        with self.lock:
            self._mata()
            self.gen += 1
            g = self.gen
            try:
                with MPV_LOG.open("w", encoding="utf-8") as sortida:
                    self.proc = subprocess.Popen(args, stdin=subprocess.DEVNULL,
                                                 stdout=subprocess.DEVNULL, stderr=sortida)
            except OSError as e:
                self.proc = None
                error = f"No s'ha pogut engegar el reproductor ({e.strerror or e})"
            proc = self.proc
            ara = time.time()
            self.info = proc and {"canco": canco.name, "motiu": motiu, "inici": ara, "fi": ara + segons}
        if proc:
            # Si mpv no pot obrir l'audio o el fitxer, s'atura de seguida
            try:
                error = explica_error_mpv(proc.wait(timeout=COMPROVA_INICI))
            except subprocess.TimeoutExpired:
                pass
        if error:
            with self.lock:
                if g == self.gen:
                    self.proc = None
                    self.info = None
            log.error("NO HA SONAT %s (%s): %s", canco.name, motiu, error)
            registra(canco.name, motiu, 0, toc, error=error)
            return error
        log.info("Toca: %s (%s, %d s)", canco.name, motiu, segons)
        registra(canco.name, motiu, segons, toc)
        threading.Thread(target=self._vigila, args=(g, segons, aj["durada_fos"], aj["volum"]),
                         daemon=True).start()
        return None

    def _vigila(self, g, segons, fos, volum):
        limit = time.monotonic() + max(segons - fos, 1)
        while time.monotonic() < limit:
            with self.lock:
                if g != self.gen or self.proc is None or self.proc.poll() is not None:
                    break
            time.sleep(0.1)
        self._fos_i_atura(g, fos, volum)

    def _fos_i_atura(self, g, fos, volum):
        passos = 30
        for i in range(passos, -1, -1):
            with self.lock:
                if g != self.gen or self.proc is None or self.proc.poll() is not None:
                    break
            ordre_mpv(["set_property", "volume", volum * i / passos])
            time.sleep(fos / passos)
        with self.lock:
            if g == self.gen:
                self._mata()
                self.info = None

    def atura(self):
        with self.lock:
            g = self.gen
        aj = cfg()["ajustos"]
        threading.Thread(target=self._fos_i_atura, args=(g, min(aj["durada_fos"], 1.5), aj["volum"]),
                         daemon=True).start()

    def _mata(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self.proc = None

    def estat(self):
        with self.lock:
            if self.info and self.proc and self.proc.poll() is None:
                return dict(self.info)
        return None


REPRODUCTOR = Reproductor()


def programador():
    fets = set()
    log.info("Programador en marxa. %d cancons.", len(cancons()))
    while True:
        try:
            c = cfg()
            ara = datetime.now()
            p = proper_toc(ara, c, MARGE_RETARD)
            if p:
                moment, t = p
                if moment not in fets and moment + timedelta(seconds=c["ajustos"]["retard_inici"]) <= ara:
                    fets.add(moment)
                    restant = t["durada"] - (ara - moment).total_seconds()
                    if restant > 5:
                        canco = tria_canco(c)
                        if canco:
                            REPRODUCTOR.toca(canco, restant, t["nom"], toc=moment)
                    fets = {f for f in fets if f > ara - timedelta(days=1)}
        except Exception:
            log.exception("Error al programador")
        time.sleep(0.5)


# ----------------------------------------------------------------- SISTEMA
def hora_sincronitzada():
    try:
        r = subprocess.run(["timedatectl", "show", "-p", "NTPSynchronized", "--value"],
                           capture_output=True, text=True, timeout=3)
        return r.stdout.strip() == "yes"
    except Exception:
        return None


def ip_local():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))
            return s.getsockname()[0]
    except Exception:
        return None


# ----------------------------------------------------------------- WEB
from flask import Flask, abort, jsonify, request, send_file, send_from_directory, session  # noqa: E402

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024
app.permanent_session_lifetime = timedelta(days=90)
# La web va per http dins l'escola: per aixo no es posa SESSION_COOKIE_SECURE
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")

FALLADES = {}   # ip -> (errors seguits, bloquejat fins a [monotonic])
FALLADES_LOCK = threading.Lock()


def segons_bloquejat(ip):
    with FALLADES_LOCK:
        return max(0.0, FALLADES.get(ip, (0, 0))[1] - time.monotonic())


def apunta_fallada(ip):
    """A partir del 5e error seguit, bloqueja 30 s, 1 min, 2 min... fins a 15 min."""
    with FALLADES_LOCK:
        n = FALLADES.get(ip, (0, 0))[0] + 1
        espera = 0 if n < INTENTS_LLIURES else min(30 * 2 ** (n - INTENTS_LLIURES), 900)
        FALLADES[ip] = (n, time.monotonic() + espera)
    if espera:
        log.warning("%d contrasenyes incorrectes seguides des de %s: bloquejat %d s", n, ip, espera)


def clau_sessio():
    try:
        return CLAU.read_text().strip()
    except FileNotFoundError:
        k = secrets.token_hex(32)
        CLAU.write_text(k)
        return k


def cal_login(f):
    @functools.wraps(f)
    def embolcall(*a, **k):
        if not session.get("ok"):
            return jsonify(error="Cal entrar"), 401
        return f(*a, **k)
    return embolcall


@app.errorhandler(Invalid)
def error_invalid(e):
    return jsonify(error=str(e)), 400


@app.get("/")
def pagina():
    return send_from_directory(WEB, "index.html")


@app.get("/api/sessio")
def api_sessio():
    return jsonify(configurada=bool(cfg().get("contrasenya")), ok=bool(session.get("ok")))


@app.post("/api/configura")
def api_configura():
    if cfg().get("contrasenya"):
        abort(403)
    text = valida_contrasenya_nova((request.json or {}).get("contrasenya", ""))
    with LOCK:
        CFG["contrasenya"] = hash_contrasenya(text)
        desa_config()
    session.permanent = True
    session["ok"] = True
    return jsonify(ok=True)


@app.post("/api/login")
def api_login():
    ip = request.remote_addr or "?"
    espera = segons_bloquejat(ip)
    if espera:
        minuts = max(1, round(espera / 60))
        return jsonify(error=f"Massa intents fallits. Torna-ho a provar d'aquí a {minuts} min."), 429
    time.sleep(0.4)
    if comprova_contrasenya((request.json or {}).get("contrasenya", "")):
        with FALLADES_LOCK:
            FALLADES.pop(ip, None)
        session.permanent = True
        session["ok"] = True
        return jsonify(ok=True)
    apunta_fallada(ip)
    return jsonify(error="Contrasenya incorrecta"), 401


@app.post("/api/logout")
def api_logout():
    session.clear()
    return jsonify(ok=True)


@app.get("/api/estat")
@cal_login
def api_estat():
    c = cfg()
    ara = datetime.now()
    avui = ara.date()
    silenci = motiu_silenci(avui, c)
    llista = []
    for moment, t in tocs_del_dia(avui, c):
        clau = moment.isoformat()
        canco = SONATS.get(clau)
        error = None
        if silenci:
            e = "silenci"
        elif clau in SONATS:
            e = "sonat"
        elif clau in FALLATS:
            e = "error"
            canco, error = FALLATS[clau]["canco"], FALLATS[clau]["error"]
        elif moment + timedelta(seconds=t["durada"]) < ara:
            e = "passat"
        elif moment <= ara:
            e = "ara"
        else:
            e = "pendent"
        llista.append({"hora": t["hora"], "nom": t["nom"], "durada": t["durada"],
                       "estat": e, "canco": canco, "error": error})
    p = proper_toc(ara, c)
    son = REPRODUCTOR.estat()
    totes = cancons()
    actives = [x for x in totes if c["cancons"].get(x.name, {}).get("activa", True)]
    return jsonify(
        ara=ara.isoformat(timespec="seconds"),
        sincronitzada=hora_sincronitzada(),
        ip=ip_local(),
        sonant=son and {"canco": son["canco"], "motiu": son["motiu"],
                        "transcorregut": round(time.time() - son["inici"], 1),
                        "total": round(son["fi"] - son["inici"], 1)},
        proper=p and {"moment": p[0].isoformat(), "nom": p[1]["nom"], "durada": p[1]["durada"]},
        avui=llista,
        silenci_avui=silenci,
        actiu=c["actiu"],
        silenci_data=c.get("silenci_data") == avui.isoformat(),
        seleccio=info_seleccio(c),
        n_cancons=len(totes),
        n_actives=len(actives),
        reserva=RESERVA.exists(),
        demo=DEMO,
    )


def info_seleccio(c):
    mode = c["seleccio"]["mode"]
    canco = None
    if mode == "fixa":
        canco = c["seleccio"].get("canco_fixa")
    elif mode in ("dia", "setmana") and actives(c):
        p = canco_del_periode(c)
        canco = p.name if p else None
    return {"mode": mode, "canco": canco}


@app.post("/api/periode")
@cal_login
def api_periode():
    """Canvia la canco d'avui / d'aquesta setmana (a l'atzar o una de concreta)."""
    c = cfg()
    if c["seleccio"]["mode"] not in ("dia", "setmana"):
        raise Invalid("Només es pot fer en els modes «cada dia» o «cada setmana»")
    nom = (request.json or {}).get("canco")
    if nom:
        nom = cami_canco(nom).name
    p = canco_del_periode(c, nova=not nom, forcada=nom)
    return jsonify(ok=True, canco=p.name if p else None)


@app.get("/api/config")
@cal_login
def api_config():
    c = cfg()
    c.pop("contrasenya", None)
    c.pop("cancons", None)
    return jsonify(c)


@app.patch("/api/config")
@cal_login
def api_config_canvia():
    d = request.json or {}
    nou = {}
    if "tocs" in d:
        nou["tocs"] = valida_tocs(d["tocs"])
    if "festius" in d:
        nou["festius"] = valida_festius(d["festius"])
    if "ajustos" in d:
        nou["ajustos"] = valida_ajustos(d["ajustos"])
    if "seleccio" in d:
        nou["seleccio"] = valida_seleccio(d["seleccio"])
    if "actiu" in d:
        nou["actiu"] = bool(d["actiu"])
    if "silenci_avui" in d:
        nou["silenci_data"] = date.today().isoformat() if d["silenci_avui"] else None
    with LOCK:
        CFG.update(nou)
        desa_config()
    return api_config()


@app.get("/api/cancons")
@cal_login
def api_cancons():
    c = cfg()
    recents = llegeix_estat().get("tocades", [])
    res = []
    for p in cancons():
        meta = c["cancons"].get(p.name, {})
        res.append({"nom": p.name, "mida": p.stat().st_size, "durada": durada_de(p),
                    "activa": meta.get("activa", True), "inici": meta.get("inici", 0),
                    "vegades": recents.count(p.name)})
    return jsonify(cancons=res, reserva=RESERVA.exists(), seleccio=info_seleccio(c))


@app.post("/api/cancons")
@cal_login
def api_puja():
    MUSICA.mkdir(parents=True, exist_ok=True)
    desades, rebutjades, sense_espai = [], [], []
    for f in request.files.getlist("fitxers"):
        nom = nom_segur(f.filename or "")
        p = Path(nom)
        if not nom or p.suffix.lower() not in EXTENSIONS:
            rebutjades.append(f.filename)
            continue
        mida = f.stream.seek(0, os.SEEK_END)
        f.stream.seek(0)
        if shutil.disk_usage(MUSICA).free - mida < ESPAI_RESERVAT:
            sense_espai.append(f.filename)
            continue
        desti = MUSICA / nom
        i = 2
        while desti.exists():
            desti = MUSICA / f"{p.stem} ({i}){p.suffix}"
            i += 1
        f.save(desti)
        desades.append(desti.name)
    log.info("Pujades: %s", desades)
    if sense_espai:
        log.warning("Sense espai a la targeta per a: %s", sense_espai)
    return jsonify(desades=desades, rebutjades=rebutjades, sense_espai=sense_espai)


def cami_canco(nom):
    if not isinstance(nom, str) or not nom or nom != nom_segur(nom):
        abort(404)
    p = MUSICA / nom
    if not p.is_file():
        abort(404)
    return p


@app.patch("/api/cancons/<path:nom>")
@cal_login
def api_canco_canvia(nom):
    cami_canco(nom)
    d = request.json or {}
    with LOCK:
        meta = CFG["cancons"].setdefault(nom, {})
        if "activa" in d:
            meta["activa"] = bool(d["activa"])
        if "inici" in d:
            meta["inici"] = enter(d["inici"] or 0, 0, 3600, "El segon d'inici")
        desa_config()
    return jsonify(ok=True)


@app.delete("/api/cancons/<path:nom>")
@cal_login
def api_canco_esborra(nom):
    cami_canco(nom).unlink()
    with LOCK:
        CFG["cancons"].pop(nom, None)
        if CFG["seleccio"].get("canco_fixa") == nom:
            CFG["seleccio"] = {"mode": "cada_toc", "canco_fixa": None}
        desa_config()
    return jsonify(ok=True)


@app.get("/api/cancons/<path:nom>/audio")
@cal_login
def api_canco_audio(nom):
    return send_file(cami_canco(nom), conditional=True)


@app.post("/api/toca")
@cal_login
def api_toca():
    d = request.json or {}
    c = cfg()
    segons = enter(d.get("segons", 30), 5, 600, "La durada")
    canco = cami_canco(d["canco"]) if d.get("canco") else tria_canco(c)
    if not canco:
        raise Invalid("No hi ha cap cançó per tocar")
    error = REPRODUCTOR.toca(canco, segons, "Manual (web)")
    if error:
        raise Invalid(f"No ha sonat: {error}")
    return jsonify(ok=True, canco=canco.name)


@app.post("/api/atura")
@cal_login
def api_atura():
    REPRODUCTOR.atura()
    return jsonify(ok=True)


@app.get("/api/historial")
@cal_login
def api_historial():
    return jsonify(historial=list(reversed(llegeix_historial(300))))


@app.post("/api/contrasenya")
@cal_login
def api_contrasenya():
    d = request.json or {}
    if not comprova_contrasenya(d.get("actual", "")):
        raise Invalid("La contrasenya actual no és correcta")
    nova = valida_contrasenya_nova(d.get("nova", ""))
    with LOCK:
        CFG["contrasenya"] = hash_contrasenya(nova)
        desa_config()
    return jsonify(ok=True)


@app.get("/api/copia")
@cal_login
def api_copia():
    c = cfg()
    c.pop("contrasenya", None)
    r = app.response_class(json.dumps(c, ensure_ascii=False, indent=1), mimetype="application/json")
    r.headers["Content-Disposition"] = f"attachment; filename=timbre-config-{date.today()}.json"
    return r


# ----------------------------------------------------------------- INICI
def main():
    BASE.mkdir(parents=True, exist_ok=True)
    MUSICA.mkdir(exist_ok=True)
    carrega_config()

    if "--contrasenya" in sys.argv:
        while True:
            nova = getpass.getpass("Contrasenya nova per a la web (codi de 4 xifres): ")
            if not codi_valid(nova):
                print("Ha de ser un codi de 4 xifres, per exemple 4071.")
            elif getpass.getpass("Repeteix-la: ") != nova:
                print("No coincideixen. Torna-hi.")
            else:
                break
        with LOCK:
            CFG["contrasenya"] = hash_contrasenya(nova)
            desa_config()
        print("Contrasenya desada.")
        return

    if "--prova" in sys.argv:
        canco = tria_canco(cfg())
        if canco:
            error = REPRODUCTOR.toca(canco, 20, "Prova")
            if error:
                sys.exit(f"NO HA SONAT: {error}")
            time.sleep(21)
        return

    prepara_historial()
    app.secret_key = clau_sessio()
    threading.Thread(target=programador, daemon=True).start()
    log.info("Web a http://%s:%d", ip_local() or "localhost", PORT)
    try:
        from waitress import serve
        serve(app, host="0.0.0.0", port=PORT, threads=8, max_request_body_size=500 * 1024 * 1024)
    except ImportError:
        app.run(host="0.0.0.0", port=PORT, threaded=True)


if __name__ == "__main__":
    main()
