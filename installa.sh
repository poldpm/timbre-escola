#!/bin/bash
# Instal·lacio del timbre musical amb web de gestio.
# Executa-ho des de la carpeta del repositori:   bash installa.sh
# Per actualitzar: git pull && bash installa.sh  (les dades de ~/timbre no es toquen)
set -e
ORIGEN="$(cd "$(dirname "$0")" && pwd)"
DESTI="$HOME/timbre"

echo "== Instal·lant programes (pot trigar uns minuts) =="
sudo apt update
sudo apt install -y mpv python3-flask python3-waitress python3-mutagen alsa-utils

echo "== Copiant fitxers a $DESTI =="
mkdir -p "$DESTI/musica" "$DESTI/web"
cp "$ORIGEN/timbre.py" "$DESTI/"
cp "$ORIGEN/web/index.html" "$DESTI/web/"

echo "== Rellotge i so =="
sudo timedatectl set-timezone Europe/Madrid
sudo systemctl enable --now systemd-timesyncd || true
amixer -c Headphones sset PCM 100% unmute >/dev/null 2>&1 || true

echo "== Creant el servei que arrenca sol =="
sudo tee /etc/systemd/system/timbre.service > /dev/null <<EOF
[Unit]
Description=Timbre musical de l'escola (web + horari)
After=sound.target network-online.target time-sync.target
Wants=network-online.target

[Service]
User=$USER
WorkingDirectory=$DESTI
ExecStart=/usr/bin/python3 $DESTI/timbre.py
AmbientCapabilities=CAP_NET_BIND_SERVICE
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable timbre
sudo systemctl restart timbre

IP=$(hostname -I | awk '{print $1}')
echo
echo "FET! Obre la web des d'un mòbil o ordinador de la mateixa wifi:"
echo "    http://$(hostname).local    o    http://$IP"
echo "El primer cop et demanarà que triïs una contrasenya."
