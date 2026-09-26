#!/bin/zsh
# Rasterise an A5 SVG artboard (148x210mm) to a transparent PNG the Blender scene reads.
# Usage: ./render_artwork.sh [in.svg] [out.png]   (defaults: artwork.svg -> artwork.png)
cd "${0:A:h}"
IN=${1:-artwork.svg}; OUT=${2:-${IN:r}.png}
inkscape "$IN" --export-type=png --export-filename="$OUT" --export-width=3496 --export-background-opacity=0 && echo "wrote $OUT"
