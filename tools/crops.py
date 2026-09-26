"""1:1 crops of a render for review: the centre plus the centre of each quadrant.

Run:
  tools/blender.sh tools/crops.py <render.png> [size] [out_dir]
  tools/blender.sh tools/crops.py <render.png> <size> <out_dir> <x,y> [<x,y> ...]

Default size 512 px. Extra x,y points (pixels from top-left) add crops centred there.
Writes <out_dir>/<stem>_crop_<label>.png; out_dir defaults to the render's folder.
"""
import sys
from pathlib import Path

import bpy
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
src = Path(argv[0]).resolve()
size = int(argv[1]) if len(argv) > 1 else 512
out_dir = Path(argv[2]).resolve() if len(argv) > 2 else src.parent
out_dir.mkdir(parents=True, exist_ok=True)

img = bpy.data.images.load(str(src))
w, h = img.size
px = np.empty(w * h * 4, dtype=np.float32)
img.pixels.foreach_get(px)
px = px.reshape(h, w, 4)  # bottom-up rows

points = {"centre": (w // 2, h // 2), "tl": (w // 4, h // 4), "tr": (3 * w // 4, h // 4),
          "bl": (w // 4, 3 * h // 4), "br": (3 * w // 4, 3 * h // 4)}
for p in argv[3:]:
    x, y = map(int, p.split(","))
    points[f"{x}_{y}"] = (x, y)

s = min(size, w, h)
for label, (cx, cy) in points.items():
    x0 = max(0, min(w - s, cx - s // 2))
    y0 = max(0, min(h - s, cy - s // 2))
    rows = slice(h - y0 - s, h - y0)  # flip: top-left coords to bottom-up rows
    crop = np.ascontiguousarray(px[rows, x0:x0 + s])
    out = bpy.data.images.new(f"crop_{label}", s, s, alpha=True)
    out.pixels.foreach_set(crop.ravel())
    out.filepath_raw = str(out_dir / f"{src.stem}_crop_{label}.png")
    out.file_format = "PNG"
    out.save()
    print(f"Saved {out.filepath_raw}")
