#!/usr/bin/env bash
# Encode a rendered rise sequence with its music.
#   experiments/eclipse-glow/scripts/make_video.sh <out> [music.wav|.mp3]
# Shared, any sequence: tools/video_encode.sh. This wrapper keeps the eclipse-glow names.
# NAME=eclipse_sunrise for build_sunrise.py. <out> is build_rise.py's --out (frames in renders/eclipse_rise_<out>/).
# Music defaults to output/eclipse_rise_score.wav (score.py). Pass your own licensed track to swap it.
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
out="$1"; music="${2:-$here/output/eclipse_rise_score.wav}"
frames="$here/renders/${NAME:-eclipse_rise}_$out"
mp4="$here/renders/${NAME:-eclipse_rise}_$out.mp4"
ffmpeg -loglevel error -y -framerate 24 -i "$frames/%04d.png" -i "$music" \
  -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p -tune grain \
  -c:a aac -b:a 256k -af "afade=t=out:st=11.4:d=0.6" -shortest -movflags +faststart "$mp4"
echo "[out] WROTE $mp4"
