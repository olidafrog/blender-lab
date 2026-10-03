"""Rectify a photo onto a model plane with its fitted camera: an orthographic texture read in metres.

  tools/blender.sh experiments/apartment-model/scripts/rectify.py <photo n> floor  x0 x1 y0 y1 [px_per_m]
  tools/blender.sh experiments/apartment-model/scripts/rectify.py <photo n> window y0 y1 z0 z1 [px_per_m]

floor: plane z = 0, image rows run along x (window at the top). window: plane x = win_x, image columns run
along y (west at the left), rows down from z1. A 10 cm grid is drawn over the output; writes assets/mat/rect_<n>_<plane>.png
and a raw float copy (.npy) for colour measurement.
"""
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from scan_tools import write_png  # noqa: E402

EXP = HERE.parent
WIN_X = -4.40


def euler_matrix(rx, ry, rz):
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def main():
    a = sys.argv[sys.argv.index("--") + 1:]
    n, plane = a[0], a[1]
    r0, r1, c0, c1 = map(float, a[2:6])
    ppm = float(a[6]) if len(a) > 6 else 400
    cam = json.load(open(EXP / f"assets/cams/{n}.json"))["joint"]
    img = bpy.data.images.load(str(EXP / f"references/{n}.jpeg"))
    W, H = img.size
    pix = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)[::-1, :, :3]   # sRGB-encoded floats, top row first
    R = euler_matrix(*(math.radians(v) for v in cam["rot_deg"]))
    loc = np.array(cam["loc"])
    f = cam["lens"] / cam["sensor_w"] * W
    k1 = cam.get("k1", 0.0)
    if plane == "floor":       # rows: x from r0 (top) to r1; cols: y from c0 to c1
        rows = np.arange(r0, r1, 1 / ppm); cols = np.arange(c0, c1, 1 / ppm)
        X, Y = np.meshgrid(rows, cols, indexing="ij"); Z = np.zeros_like(X)
    else:                       # rows: z from c1 down to c0; cols: y from r0 to r1
        cols = np.arange(r0, r1, 1 / ppm); rows = np.arange(c1, c0, -1 / ppm)
        Z, Y = np.meshgrid(rows, cols, indexing="ij"); X = np.full_like(Y, WIN_X)
    p = np.stack([X, Y, Z], -1) - loc
    pc = p @ R                           # world -> camera (R^T p)
    zc = -pc[..., 2]
    u = W / 2 + f * pc[..., 0] / zc
    v = H / 2 - f * pc[..., 1] / zc
    du, dv = u - W / 2, v - H / 2
    s = 1 + k1 * (du * du + dv * dv) / (f * f)
    u, v = W / 2 + du * s, H / 2 + dv * s
    ok = (zc > 0) & (u >= 0) & (u < W - 1) & (v >= 0) & (v < H - 1)
    ui = np.clip(u, 0, W - 1).astype(int); vi = np.clip(v, 0, H - 1).astype(int)
    out = np.where(ok[..., None], pix[vi, ui], 0)
    np.save(EXP / f"assets/mat/rect_{n}_{plane}.npy", out.astype(np.float32))
    g = (out * 255).clip(0, 255).astype(np.uint8)
    step = int(round(ppm / 10))
    g[::step, :] = (g[::step, :] * 0.5 + np.array([0, 160, 255]) * 0.5).astype(np.uint8)
    g[:, ::step] = (g[:, ::step] * 0.5 + np.array([0, 160, 255]) * 0.5).astype(np.uint8)
    write_png(EXP / f"assets/mat/rect_{n}_{plane}.png", g)
    print(f"[out] rect {n} {plane} {g.shape[1]}x{g.shape[0]} px, {ppm:.0f} px/m, valid {ok.mean():.2f}")


main()
