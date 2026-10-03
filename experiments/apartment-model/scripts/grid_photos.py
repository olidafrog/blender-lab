"""Gridded copies of the reference photos for reading landmark pixels: 50 px faint, 100 px blue, 500 px red.
  tools/blender.sh experiments/apartment-model/scripts/grid_photos.py
"""
from pathlib import Path
import bpy
import numpy as np

EXP = Path(__file__).resolve().parents[1]
out = EXP / "assets/grid"
out.mkdir(parents=True, exist_ok=True)
for i in range(1, 9):
    img = bpy.data.images.load(str(EXP / f"references/{i}.jpeg"))
    W, H = img.size
    a = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)[::-1].copy()   # top row first
    for step, col, w in ((50, (0.2, 0.9, 0.9), 0.35), (100, (0.0, 0.2, 1.0), 0.6), (500, (1.0, 0.0, 0.0), 0.9)):
        a[::step, :, :3] = a[::step, :, :3] * (1 - w) + np.array(col) * w
        a[:, ::step, :3] = a[:, ::step, :3] * (1 - w) + np.array(col) * w
    o = bpy.data.images.new(f"g{i}", W, H)
    o.pixels[:] = a[::-1].ravel()
    o.filepath_raw = str(out / f"{i}_grid.png")
    o.file_format = "PNG"
    o.save()
    print("[out] wrote", o.filepath_raw)
