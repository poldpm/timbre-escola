#!/usr/bin/env python3
"""
Timbre musical de l'escola - Raspberry Pi 3 (versio amb horari propi)

La Raspberry sap les hores per internet i llegeix l'horari del fitxer
"horari.txt" de la carpeta de Drive. A cada hora del timbre toca una canco
a l'atzar (sense repetir les ultimes) i l'apaga amb un fos al final.

El rellotge Theben continua engegant l'amplificador com sempre: la Raspberry
nomes posa la musica. Per aixo les hores de horari.txt han de coincidir amb
les del rellotge.

Us:
  python3 timbre.py           -> mode normal (el que executa el servei)
  python3 timbre.py --prova   -> toca una canco ara mateix (20 s) per provar el so
  python3 timbre.py --llista  -> mostra cancons, horari i proper toc
"""

import json
import logging
import random
import socket
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# ----------------------------------------------------------------- AJUSTOS
BASE = Path(__file__).resolve().parent
MUSICA = BASE / "musica"             # carpeta sincronitzada amb Google Drive
HORARI = MUSICA / "horari.txt"       # horari editable des de Drive
RESERVA = BASE / "reserva.mp3"       # canco de seguretat si la carpeta es buida
ESTAT = BASE / "estat.json"          # historial de cancons tocades
HISTORIAL = BASE / "historial.log"   # registre llegible de cada toc

RETARD_INICI = 3          # s despres de l'hora: dona temps a l'amplificador
DURADA_PER_DEFECTE = 60   # s si una linia de l'horari no diu la durada
DURADA_FOS = 3.0          # s del fos de sortida al final
MARGE_RETARD = 30         # s: si arrenca tard (reinici), encara toca si fa menys d'aixo
VOLUM = 100               # volum de la Raspberry (0-100); ajusta a l'amplificador
NORMALITZA = True         # iguala el volum entre cancons diferents
SORTIDA_AUDIO = "alsa/plughw:CARD=Headphones,DEV=0"   # sortida jack 3,5 mm
EXTENSIONS = {".mp3", ".m4a", ".ogg", ".wav", ".flac", ".opus", ".aac"}
SOCKET_MPV = "/tmp/timbre-mpv.sock"
DIES = {"dl": 0, "dt": 1, "dc": 2, "dj": 3, "dv": 4, "ds": 5, "dg": 6}
# -------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("timbre")


# ---------------------------------------------------------------- HORARI
def dies_de(text):
    """'dl-dv' -> {0..4}; 'dl,dc,dv' -> {0,2,4}"""
    resultat = set()
    for tros in text.lower().split(","):
        tros = tros.strip()
        if "-" in tros:
            a, b = (DIES[x.strip()] for x in tros.split("-"))
            resultat.update(range(a, b + 1))
        elif tros:
            resultat.add(DIES[tros])
    return resultat


def llegeix_horari():
    """Retorna (tocs, festius). tocs = [(hora, minut, durada, dies)]."""
    tocs, festius = [], set()
    if not HORARI.exists():
        return tocs, festius
    for n, linia in enumerate(HORARI.read_text(encoding="utf-8").splitlines(), 1):
        linia = linia.split("#")[0].strip()
        if not linia:
            continue
        parts = linia.split()
        try:
            if parts[0].lower() == "festiu":
                for data in parts[1:]:
                    if ".." in data:
                        ini, fi = (datetime.strptime(x, "%Y-%m-%d").date() for x in data.split(".."))
                        while ini <= fi:
                            festius.add(ini)
                            ini += timedelta(days=1)
                    else:
                        festius.add(datetime.strptime(data, "%Y-%m-%d").date())
                continue
            h, m = (int(x) for x in parts[0].split(":"))
            durada = int(parts[1]) if len(parts) > 1 else DURADA_PER_DEFECTE
            dies = dies_de(parts[2]) if len(parts) > 2 else set(range(5))
            tocs.append((h, m, durada, dies))
        except Exception:
            log.warning("horari.txt linia %d no s'entén, la salto: %s", n, linia)
    return tocs, festius


def proper_toc(ara, tocs, festius):
    millor = None
    for dies_endavant in range(0, 15):
        dia = (ara + timedelta(days=dies_endavant)).date()
        if dia in festius:
            continue
        for h, m, durada, dies in tocs:
            if dia.weekday() not in dies:
                continue
            moment = datetime.combine(dia, datetime.min.time()).replace(hour=h, minute=m)
            if moment + timedelta(seconds=MARGE_RETARD) > ara and (millor is None or moment < millor[0]):
                millor = (moment, durada)
        if millor:
            return millor
    return None


# ---------------------------------------------------------------- CANCONS
def cancons():
    if not MUSICA.exists():
        return []
    return sorted(
        p for p in MUSICA.rglob("*")
        if p.is_file() and p.suffix.lower() in EXTENSIONS and not p.name.startswith(".")
    )


def llegeix_estat():
    try:
        return json.loads(ESTAT.read_text(encoding="utf-8"))
    except Exception:
        return {"tocades": []}


def desa_estat(estat):
    try:
        ESTAT.write_text(json.dumps(estat, ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception as e:
        log.warning("No he pogut desar l'estat: %s", e)


def tria_canco():
    """Tria a l'atzar evitant les ultimes tocades (fins a la meitat de la llista)."""
    llista = cancons()
    if not llista:
        if RESERVA.exists():
            log.warning("Carpeta de musica buida: toco la canco de reserva")
            return RESERVA
        log.error("No hi ha cap canco ni canco de reserva!")
        return None

    estat = llegeix_estat()
    recents = estat.get("tocades", [])
    n_evitar = min(len(llista) // 2, 20)
    evitar = set(recents[-n_evitar:]) if n_evitar else set()
    candidates = [p for p in llista if p.name not in evitar] or llista
    triada = random.choice(candidates)

    estat["tocades"] = (recents + [triada.name])[-100:]
    desa_estat(estat)
    return triada


# ---------------------------------------------------------------- SO
def ordre_mpv(ordre):
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            s.connect(SOCKET_MPV)
            s.sendall((json.dumps({"command": ordre}) + "\n").encode())
    except Exception:
        pass


def toca(canco):
    args = [
        "mpv", "--no-video", "--really-quiet", "--no-terminal",
        f"--audio-device={SORTIDA_AUDIO}",
        f"--volume={VOLUM}",
        f"--input-ipc-server={SOCKET_MPV}",
    ]
    if NORMALITZA:
        args.append("--af=lavfi=[loudnorm=I=-16:TP=-1.5:LRA=11]")
    args.append(str(canco))
    log.info("Toca: %s", canco.name)
    try:
        with HISTORIAL.open("a", encoding="utf-8") as f:
            f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S}  {canco.name}\n")
    except Exception:
        pass
    return subprocess.Popen(args)


def fos_i_atura(proc):
    passos = 30
    for i in range(passos, -1, -1):
        if proc.poll() is not None:
            return
        ordre_mpv(["set_property", "volume", VOLUM * i / passos])
        time.sleep(DURADA_FOS / passos)
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()


def toca_durant(segons):
    """Toca una canco com a maxim 'segons' (inclou el fos final)."""
    canco = tria_canco()
    if not canco:
        return
    proc = toca(canco)
    limit = time.monotonic() + max(segons - DURADA_FOS, 1)
    try:
        while proc.poll() is None and time.monotonic() < limit:
            time.sleep(0.1)
    finally:
        fos_i_atura(proc)


def hora_sincronitzada():
    try:
        r = subprocess.run(["timedatectl", "show", "-p", "NTPSynchronized", "--value"],
                           capture_output=True, text=True, timeout=5)
        return r.stdout.strip() == "yes"
    except Exception:
        return True   # fora de la Raspberry no ho comprovem


# ---------------------------------------------------------------- MODES
def mode_prova():
    toca_durant(20)


def mode_llista():
    llista = cancons()
    print(f"{len(llista)} cancons a {MUSICA}:")
    for p in llista:
        print("  -", p.name)
    tocs, festius = llegeix_horari()
    print(f"\nHorari ({HORARI}):")
    if not tocs:
        print("  (buit o no trobat!)")
    inv = {v: k for k, v in DIES.items()}
    for h, m, durada, dies in sorted(tocs):
        print(f"  {h:02d}:{m:02d}  {durada:>3} s  {','.join(inv[d] for d in sorted(dies))}")
    if festius:
        print(f"  Festius: {len(festius)} dies")
    p = proper_toc(datetime.now(), tocs, festius)
    print(f"\nProper toc: {p[0]:%A %d/%m %H:%M} ({p[1]} s)" if p else "\nProper toc: cap")
    print(f"Hora sincronitzada per internet: {'SI' if hora_sincronitzada() else 'NO!'}")
    print("\nUltimes tocades:")
    for nom in llegeix_estat().get("tocades", [])[-10:]:
        print("  -", nom)
    print(f"\nCanco de reserva: {'SI' if RESERVA.exists() else 'NO (recomanat posar-ne una)'}")


def mode_normal():
    log.info("Timbre a punt. %d cancons disponibles.", len(cancons()))
    fets = set()
    avis_hora = False
    while True:
        if not hora_sincronitzada():
            if not avis_hora:
                log.warning("L'hora encara no està sincronitzada per internet")
                avis_hora = True
        else:
            avis_hora = False

        tocs, festius = llegeix_horari()     # es rellegeix: els canvis de Drive s'apliquen sols
        ara = datetime.now()
        p = proper_toc(ara, tocs, festius)
        if p:
            moment, durada = p
            inici = moment + timedelta(seconds=RETARD_INICI)
            if moment not in fets and inici <= ara:
                fets.add(moment)
                restant = durada - (ara - moment).total_seconds()
                if restant > DURADA_FOS + 2:
                    log.info("Toc de les %s", moment.strftime("%H:%M"))
                    toca_durant(restant)
                fets = {f for f in fets if f > ara - timedelta(days=1)}
                continue
        time.sleep(0.5)


if __name__ == "__main__":
    if "--prova" in sys.argv:
        mode_prova()
    elif "--llista" in sys.argv:
        mode_llista()
    else:
        mode_normal()
