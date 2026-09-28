"""Tile images side by side at one height (Blender's Python; system python3 has no numpy).

    tools/blender.sh tools/tile.py <out.png> <a.png> <b.png> ... [-- "label a" "label b" ...]

Labels are printed with each tile's x position, left to right in argument order; they are not
drawn on the image.
"""
import sys
from pathlib import Path

import bpy
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
if "--" in argv:
    k = argv.index("--")
    paths, labels = argv[:k], argv[k + 1:]
else:
    paths, labels = argv, []
out, srcs = Path(paths[0]).resolve(), [Path(p).resolve() for p in paths[1:]]

imgs = []
for p in srcs:
    im = bpy.data.images.load(str(p))
    w, h = im.size
    px = np.empty(w * h * 4, dtype=np.float32)
    im.pixels.foreach_get(px)
    imgs.append(px.reshape(h, w, 4))
H = min(i.shape[0] for i in imgs)


def resize(a, h):  # nearest-neighbour to height h, keeps aspect
    w = round(a.shape[1] * h / a.shape[0])
    ys = (np.arange(h) * a.shape[0] / h).astype(int)
    xs = (np.arange(w) * a.shape[1] / w).astype(int)
    return a[ys][:, xs]


tiles = [resize(i, H) for i in imgs]
gap = np.ones((H, 8, 4), dtype=np.float32)
row = np.concatenate(sum(([t, gap] for t in tiles), [])[:-1], axis=1)
W = row.shape[1]
res = bpy.data.images.new("tile", W, H, alpha=True)
res.pixels.foreach_set(row.ravel())
res.filepath_raw, res.file_format = str(out), "PNG"
res.save()
x = 0
for i, t in enumerate(tiles):
    lab = labels[i] if i < len(labels) else srcs[i].stem
    print(f"[out] tile {i + 1} at x={x}: {lab}")
    x += t.shape[1] + 8
print(f"[out] wrote {out}")
