#!/usr/bin/env python3
"""
Timbre musical de l'escola - Raspberry Pi 3

Quan el rellotge Theben dona corrent a l'endoll del timbre, un carregador USB
envia 5 V (rebaixats a 3,3 V amb dues resistencies) al pin GPIO17.
Aquest programa ho detecta, espera uns segons perque l'amplificador s'engegui
i toca una canco a l'atzar de la carpeta "musica" sense repetir les ultimes.
Si el rellotge talla el corrent abans que acabi, la canco s'apaga amb un fos.

Us:
  python3 timbre.py           -> mode normal (el que executa el servei)
  python3 timbre.py --prova   -> toca una canco ara mateix (20 s) per provar el so
  python3 timbre.py --llista  -> mostra les cancons i les ultimes tocades
"""

import json
import logging
import random
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ----------------------------------------------------------------- AJUSTOS
BASE = Path(__file__).resolve().parent
MUSICA = BASE / "musica"            # carpeta sincronitzada amb Google Drive
RESERVA = BASE / "reserva.mp3"      # canco de seguretat si la carpeta es buida
ESTAT = BASE / "estat.json"         # historial de cancons tocades
HISTORIAL = BASE / "historial.log"  # registre llegible de cada toc

PIN_SENYAL = 17           # GPIO17 = pin fisic 11
TEMPS_CONFIRMACIO = 0.5   # s que el senyal ha d'estar actiu per fer-lo valid
RETARD_INICI = 2.0        # s d'espera perque l'amplificador acabi d'engegar
DURADA_FOS = 2.5          # s del fos de sortida quan es talla el corrent
VOLUM = 100               # volum de la Raspberry (0-100); ajusta a l'amplificador
NORMALITZA = True         # iguala el volum entre cancons diferents
SORTIDA_AUDIO = "alsa/plughw:CARD=Headphones,DEV=0"   # sortida jack 3,5 mm
EXTENSIONS = {".mp3", ".m4a", ".ogg", ".wav", ".flac", ".opus", ".aac"}
SOCKET_MPV = "/tmp/timbre-mpv.sock"
# -------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("timbre")


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


def ordre_mpv(ordre):
    """Envia una ordre a mpv pel seu socket (per controlar el volum)."""
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
    passos = 25
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


def mode_prova():
    canco = tria_canco()
    if not canco:
        sys.exit(1)
    proc = toca(canco)
    try:
        for _ in range(200):          # 20 segons
            if proc.poll() is not None:
                return
            time.sleep(0.1)
        fos_i_atura(proc)
    except KeyboardInterrupt:
        fos_i_atura(proc)


def mode_llista():
    llista = cancons()
    print(f"{len(llista)} cancons a {MUSICA}:")
    for p in llista:
        print("  -", p.name)
    print("\nUltimes tocades:")
    for nom in llegeix_estat().get("tocades", [])[-10:]:
        print("  -", nom)
    print(f"\nCanco de reserva: {'SI' if RESERVA.exists() else 'NO (recomanat posar-ne una)'}")


def mode_normal():
    from gpiozero import DigitalInputDevice   # nomes cal a la Raspberry

    senyal = DigitalInputDevice(PIN_SENYAL, pull_up=False)
    log.info("Timbre a punt. %d cancons disponibles. Esperant el rellotge...", len(cancons()))

    while True:
        senyal.wait_for_active()
        time.sleep(TEMPS_CONFIRMACIO)
        if not senyal.is_active:
            continue                      # soroll electric, no es un toc

        log.info("Senyal del rellotge rebut")
        time.sleep(RETARD_INICI)
        if not senyal.is_active:
            continue

        canco = tria_canco()
        if canco:
            proc = toca(canco)
            while proc.poll() is None:
                if not senyal.is_active:
                    time.sleep(0.3)       # confirma que el tall es real
                    if not senyal.is_active:
                        log.info("El rellotge ha tallat: fos de sortida")
                        fos_i_atura(proc)
                        break
                time.sleep(0.1)

        # No tornem a tocar fins que el rellotge hagi apagat
        senyal.wait_for_inactive()
        log.info("Toc acabat. Esperant el seguent...")


if __name__ == "__main__":
    if "--prova" in sys.argv:
        mode_prova()
    elif "--llista" in sys.argv:
        mode_llista()
    else:
        mode_normal()
