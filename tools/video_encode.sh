#!/usr/bin/env bash
# Encode a PNG sequence to H.264 MP4, optionally with audio (generalised from eclipse-glow).
#   tools/video_encode.sh <frames_dir> <out.mp4> [audio] [-- fps=24 crf=14 fade=0.6]
# Frames are <frames_dir>/%04d.png. The audio fades out over the last `fade` s and is cut to the video.
# Prints the frame count it encoded, so a stale or wrong folder shows at once.
set -euo pipefail
frames="$1"; mp4="$2"; audio="${3:-}"; shift $(( $# < 3 ? $# : 3 ))
fps=24; crf=14; fade=0.6
[ "${1:-}" = "--" ] && shift
for kv in "$@"; do case "${kv%%=*}" in fps) fps="${kv#*=}";; crf) crf="${kv#*=}";; fade) fade="${kv#*=}";; *) echo "[out] unknown option $kv"; exit 1;; esac; done
n=$(ls "$frames"/[0-9][0-9][0-9][0-9].png | wc -l | tr -d ' ')
[ "$n" -gt 0 ] || { echo "[out] no frames in $frames"; exit 1; }
dur=$(awk "BEGIN{print $n/$fps}")
if [ -n "$audio" ]; then
  ffmpeg -loglevel error -y -framerate "$fps" -i "$frames/%04d.png" -i "$audio" \
    -c:v libx264 -preset slow -crf "$crf" -pix_fmt yuv420p -tune grain \
    -c:a aac -b:a 256k -af "afade=t=out:st=$(awk "BEGIN{print $dur-$fade}"):d=$fade" -shortest \
    -movflags +faststart "$mp4"
else
  ffmpeg -loglevel error -y -framerate "$fps" -i "$frames/%04d.png" \
    -c:v libx264 -preset slow -crf "$crf" -pix_fmt yuv420p -tune grain -movflags +faststart "$mp4"
fi
echo "[out] WROTE $mp4 ($n frames, ${dur}s, $(du -h "$mp4" | cut -f1))"
