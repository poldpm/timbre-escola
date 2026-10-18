#!/bin/bash
# Instal·lacio del timbre musical. Executa-ho des de la carpeta descomprimida:
#   bash installa.sh
set -e
ORIGEN="$(cd "$(dirname "$0")" && pwd)"
DESTI="$HOME/timbre"

echo "== Instal·lant programes (pot trigar uns minuts) =="
sudo apt update
sudo apt install -y mpv rclone python3-gpiozero python3-lgpio

echo "== Copiant fitxers a $DESTI =="
mkdir -p "$DESTI/musica"
cp "$ORIGEN/timbre.py" "$ORIGEN/sincronitza.sh" "$DESTI/"
chmod +x "$DESTI/timbre.py" "$DESTI/sincronitza.sh"

echo "== Creant el servei que arrenca sol =="
sudo tee /etc/systemd/system/timbre.service > /dev/null <<EOF
[Unit]
Description=Timbre musical de l'escola
After=sound.target

[Service]
User=$USER
WorkingDirectory=$DESTI
ExecStart=/usr/bin/python3 $DESTI/timbre.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now timbre

echo "== Programant la sincronitzacio amb Drive (cada nit i en engegar) =="
( crontab -l 2>/dev/null | grep -v sincronitza.sh
  echo "30 2 * * * $DESTI/sincronitza.sh"
  echo "@reboot sleep 90 && $DESTI/sincronitza.sh"
) | crontab -

sudo timedatectl set-timezone Europe/Madrid

echo
echo "FET! Falta: configurar Google Drive (rclone config) i posar reserva.mp3"
echo "Mira la GUIA, passos 6 i 7."
