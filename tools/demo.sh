#!/bin/bash
# Engega el timbre en MODE DEMO (sense so, sense Raspberry) per provar la web
# en qualsevol ordinador Linux/Mac/WSL.
#
#   bash tools/demo.sh            -> http://localhost:8099  (contrasenya: la que triïs)
#
# Requisits: python3, pip install flask waitress mutagen ; ffmpeg (opcional, per
# crear cançons de prova amb durada real).
set -e
ARREL="$(cd "$(dirname "$0")/.." && pwd)"
DEMO="$ARREL/.demo"
mkdir -p "$DEMO/musica"

if [ -z "$(ls -A "$DEMO/musica" 2>/dev/null)" ] && command -v ffmpeg >/dev/null; then
  echo "Creant cançons de prova (tons sinusoidals)..."
  for n in "Bon dia sol" "Happy - Cançó de prova" "Here Comes the Sun" "La flor de la vida" "Sweet Caroline" "Viva la vida"; do
    ffmpeg -loglevel error -f lavfi -i "sine=frequency=440:duration=$((90 + RANDOM % 150))" -b:a 32k "$DEMO/musica/$n.mp3"
  done
fi

echo "Web de proves a http://localhost:8099  (Ctrl+C per aturar)"
TIMBRE_DIR="$DEMO" TIMBRE_PORT=8099 TIMBRE_DEMO=1 python3 "$ARREL/timbre.py"
