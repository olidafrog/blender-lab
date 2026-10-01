"""Edge crispness and fine-detail energy, reference against a render (from aztechno-building) (numpy + Pillow, via uv).

  uv run --with numpy --with pillow python tools/sharpness.py <reference.png> <render.png>

Edge ratio: mean ratio of 1 px to 3 px luma gradient over the strongest 2 % of edges (a soft image is
lower; match the reference, which this script measures itself). Fine detail: std of (image - gaussian 1.5 px), render / ref.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter



def load(p):
    im = Image.open(p).convert("L")
    if p != sys.argv[1]:
        im = im.resize(Image.open(sys.argv[1]).size, Image.LANCZOS)
    return im, np.asarray(im, dtype=np.float32)


def edge_ratio(a):
    g1 = np.abs(a[:, 1:] - a[:, :-1])[:, 1:-1]
    g3 = np.abs(a[:, 3:] - a[:, :-3]) / 3.0
    g1 = g1[:, : g3.shape[1]]
    k = g3 > np.percentile(g3, 98)
    return float(np.mean(g1[k] / np.maximum(g3[k], 1e-3)))


def fine(im, a):
    b = np.asarray(im.filter(ImageFilter.GaussianBlur(1.5)), dtype=np.float32)
    return float(np.std(a - b))


r_im, r = load(sys.argv[1])
x_im, x = load(sys.argv[2])
print(f"[out] edge ratio  ref {edge_ratio(r):.2f}  render {edge_ratio(x):.2f}  (target: the reference value +-0.08)")
print(f"[out] fine detail render/ref {fine(x_im, x) / fine(r_im, r):.2f}  (target 0.9-1.1)")
