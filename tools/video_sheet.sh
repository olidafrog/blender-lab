#!/usr/bin/env bash
# Review material for a PNG sequence (generalised from eclipse-glow's rise_sheet.sh):
#   - sheet.png: a 3x3 contact sheet of nine frames (scaled to 640 wide),
#   - motion_<f>.png: six consecutive frames of one patch at 1:1 in a 3x2 grid (does it move?),
#   - crop_<f>.png: a 1:1 crop of each extra frame.
#   tools/video_sheet.sh <frames_dir> <out_dir> "<9 frame numbers>" <motion_start> <w:h:x:y> ["<extra frames>"]
# Example: tools/video_sheet.sh renders/rise_v07 reviews/rise/crops_v07 "1 24 60 96 132 168 204 228 288" 160 480:240:720:620 "140 210"
# Frames are <frames_dir>/%04d.png. A missing frame stops the script with its name.
set -euo pipefail
seq="$1"; dst="$2"; read -r -a pick <<< "$3"; m0="$4"; crop="$5"; read -r -a extra <<< "${6:-}"
[ "${#pick[@]}" -eq 9 ] || { echo "[out] give nine frame numbers"; exit 1; }
f() { local p="$seq/$(printf %04d "$1").png"; [ -f "$p" ] || { echo "[out] missing $p" >&2; exit 1; }; echo "$p"; }
mkdir -p "$dst"
args=(); filt=""
for i in "${!pick[@]}"; do args+=(-i "$(f "${pick[$i]}")"); filt+="[$i:v]scale=640:-2[s$i];"; done
filt+="[s0][s1][s2][s3][s4][s5][s6][s7][s8]xstack=inputs=9:layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0|0_h0+h1|w0_h0+h1|w0+w1_h0+h1"
ffmpeg -loglevel error -y "${args[@]}" -filter_complex "$filt" "$dst/sheet.png"
ins=(); mf=""
for j in 0 1 2 3 4 5; do ins+=(-i "$(f $((m0 + j)))"); mf+="[$j:v]crop=$crop[c$j];"; done
ffmpeg -loglevel error -y "${ins[@]}" -filter_complex \
  "${mf}[c0][c1][c2][c3][c4][c5]xstack=inputs=6:layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0" "$dst/motion_$m0.png"
for n in "${extra[@]}"; do
  [ -n "$n" ] && ffmpeg -loglevel error -y -i "$(f "$n")" -vf "crop=$crop" "$dst/crop_$n.png"
done
echo "[out] review material in $dst: $(ls "$dst" | tr '\n' ' ')"
