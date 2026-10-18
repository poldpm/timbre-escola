#!/bin/bash
# Descarrega les cancons i horari.txt de la carpeta de Google Drive.
# S'executa cada nit i en engegar. Es pot llançar a ma: ~/timbre/sincronitza.sh

REMOT="drive:Timbre escola"        # nom del remot de rclone : carpeta de Drive
DESTI="$HOME/timbre/musica"

mkdir -p "$DESTI"
rclone sync "$REMOT" "$DESTI" \
  --include "*.{mp3,m4a,ogg,wav,flac,opus,aac}" --include "horari.txt" --ignore-case \
  --drive-export-formats txt \
  --max-delete 30 \
  --log-file "$HOME/timbre/sincronitzacio.log" --log-level INFO
