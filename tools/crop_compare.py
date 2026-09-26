"""Zoomed side-by-side of one region of a reference and a render (nearest-neighbour upscale).

Run:
  tools/blender.sh tools/crop_compare.py <reference> <render> <x0> <y0> <x1> <y1> [zoom] [out.png]

Coordinates are pixels from the top-left. Useful when a judge flags a small area (a rim, an edge).
"""
import sys
from pathlib import Path

import bpy
import numpy as np


def load(path):
    img = bpy.data.images.load(str(Path(path).resolve()))
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    return px.reshape(h, w, 4)[::-1, :, :3]


argv = sys.argv[sys.argv.index("--") + 1:]
ref, ren = load(argv[0]), load(argv[1])
x0, y0, x1, y1 = map(int, argv[2:6])
zoom = int(argv[6]) if len(argv) > 6 else 3
out = Path(argv[7] if len(argv) > 7 else Path(argv[1]).with_name(Path(argv[1]).stem + "_crop.png")).resolve()

crops = [np.kron(a[y0:y1, x0:x1], np.ones((zoom, zoom, 1))) for a in (ref, ren)]
h = crops[0].shape[0]
sbs = np.concatenate([crops[0], np.ones((h, 8, 3)), crops[1]], axis=1)
H, W, _ = sbs.shape
img = bpy.data.images.new("crop", W, H, alpha=False)
img.pixels.foreach_set(np.concatenate([sbs, np.ones((H, W, 1))], axis=2)[::-1].astype(np.float32).ravel())
img.filepath_raw = str(out)
img.file_format = "PNG"
img.save()
print(f"CROP {out}")
