#!/bin/bash
# Render one build.py once per variant and tile the results side by side with labels.
#
#   tools/sweep.sh <build.py> <name> "<variant>" ["<variant>" ...] [-- extra build args]
#   tools/sweep.sh experiments/clouds/scripts/build.py sun "sun_azim=-60" "sun_azim=-110 sun_elev=25" -- --scale 0.3 --samples 48
#
# A variant is space-separated key=value pairs, each passed as its own --set (quote values
# with spaces or tuples as usual: 'albedo=(1,0.6,0.7,1)'). Variants render one after another
# as <name>_1, <name>_2 … in the experiment's renders/, then tile into renders/<name>_sweep.png.
# This is bash on purpose: zsh does not word-split, and a zsh loop silently drops every --set.
set -euo pipefail
cd "$(dirname "$0")/.."
build=$1; name=$2; shift 2
variants=(); extra=()
while [ $# -gt 0 ]; do
  if [ "$1" = "--" ]; then shift; extra=("$@"); break; fi
  variants+=("$1"); shift
done
[ ${#extra[@]} -eq 0 ] && extra=(--scale 0.3 --samples 48)
renders="$(dirname "$(dirname "$build")")/renders"
files=(); labels=()
i=0
for v in "${variants[@]}"; do
  i=$((i + 1))
  args=()
  read -r -a pairs <<< "$v"
  for kv in "${pairs[@]}"; do args+=(--set "$kv"); done
  tools/blender.sh "$build" --out "${name}_$i" "${extra[@]}" "${args[@]+"${args[@]}"}" \
    | grep -E "Error|Traceback" && { echo "[out] variant $i failed: $v"; exit 1; }
  files+=("$renders/${name}_$i.png"); labels+=("$v")
  echo "[out] $i: $v"
done
tools/blender.sh tools/tile.py "$renders/${name}_sweep.png" "${files[@]}" -- "${labels[@]}" | grep "\[out\]"
