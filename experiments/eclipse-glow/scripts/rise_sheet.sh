#!/usr/bin/env bash
# Shared, any sequence: tools/video_sheet.sh. This one keeps the eclipse-glow frame picks.
# Review material for a rise sequence: a contact sheet (frames 1 24 60 96 132 168 204 228 288,
# left to right, top to bottom; this ffmpeg has no drawtext) and 1:1 crops.
#   experiments/eclipse-glow/scripts/rise_sheet.sh <out>   → reviews/rise/crops_<out>/
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
seq="$here/renders/${NAME:-eclipse_rise}_$1"; dst="$here/reviews/${REVIEW:-rise}/crops_$1"
mkdir -p "$dst"
args=()
for n in 1 24 60 96 132 168 204 228 288; do
  args+=(-i "$seq/$(printf %04d $n).png")
done
filt=""; i=0
for n in 1 24 60 96 132 168 204 228 288; do
  filt+="[$i:v]scale=640:360[s$i];"
  i=$((i+1))
done
filt+="$(for j in $(seq 0 8); do printf '[s%d]' $j; done)xstack=inputs=9:layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0|0_h0+h1|w0_h0+h1|w0+w1_h0+h1"
ffmpeg -loglevel error -y "${args[@]}" -filter_complex "$filt" "$dst/sheet.png"
# Horizon at 1:1 on two consecutive frames (shimmer must move), and the rested logo.
for n in 160 161; do
  ffmpeg -loglevel error -y -i "$seq/$(printf %04d $n).png" -vf "crop=960:480:480:560" "$dst/horizon_f$n.png"
done
# Six consecutive frames of the same 480×240 patch at the horizon, 1:1, in a 3×2 grid (motion).
ins=(); for n in 160 161 162 163 164 165; do ins+=(-i "$seq/$(printf %04d $n).png"); done
ffmpeg -loglevel error -y "${ins[@]}" -filter_complex \
  "$(for j in 0 1 2 3 4 5; do printf '[%d:v]crop=480:240:720:620[c%d];' $j $j; done)[c0][c1][c2][c3][c4][c5]xstack=inputs=6:layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0" \
  "$dst/horizon_f160-165.png"
ffmpeg -loglevel error -y -i "$seq/0270.png" -vf "crop=1100:900:410:40" "$dst/rested_f270.png"
ls "$dst"
# Contact moment and lift-off gap, 1:1 at the horizon.
for n in 140 210; do
  ffmpeg -loglevel error -y -i "$seq/$(printf %04d $n).png" -vf "crop=960:400:480:600" "$dst/contact_f$n.png"
done
