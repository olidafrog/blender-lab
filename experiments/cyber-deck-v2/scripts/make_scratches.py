"""Scratch mask (assets/scratches.png, grey, 2048^2) drawn with PIL. Run once with system python3.

  python3 experiments/cyber-deck-v2/scripts/make_scratches.py

Covers a 250 x 250 mm square, x -100..150 mm, y -110..140 mm, top-down in device coordinates
(0.122 mm per px). Sparse straight light strokes, 5-20 mm, clustered on the lid and the right plate,
with a thin scatter elsewhere. The polymer material reads it in object space and lifts albedo and
roughness under it (stress whitening), it does not bump.
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

random.seed(11)
N = 2048
X0, Y0, SPAN = -100.0, 140.0, 250.0            # left edge x (mm), top edge y (mm), size (mm)
PXMM = N / SPAN
im = Image.new("L", (N, N), 0)
d = ImageDraw.Draw(im)


def to_px(x, y):
    return ((x - X0) * PXMM, (Y0 - y) * PXMM)


def stroke(cx, cy, ang, length, w, val):
    """A straight scratch (reference 4K: thin straight lines 5-20 mm long, never curly)."""
    dx, dy = math.cos(ang) * length / 2, math.sin(ang) * length / 2
    d.line([to_px(cx - dx, cy - dy), to_px(cx + dx, cy + dy)], fill=val, width=w)


# clusters: (centre x, centre y, radius mm, count) in device mm; lid, right plate, shield, lower block, wing
for cx, cy, rad, count in ((47, 2, 20, 16), (52, -28, 16, 9), (12, -8, 26, 8), (-25, -70, 18, 5), (-35, -22, 16, 4)):
    base = random.uniform(0, math.pi)                     # scratches in one spot share a direction
    for _ in range(count):
        r = rad * math.sqrt(random.random())
        a = random.uniform(0, 2 * math.pi)
        stroke(cx + r * math.cos(a), cy + r * math.sin(a), base + random.uniform(-0.35, 0.35),
               random.uniform(5.0, 20.0), 1, random.randint(120, 255))
# a thin scatter
for _ in range(22):
    stroke(random.uniform(-90, 90), random.uniform(-100, 130), random.uniform(0, math.pi), random.uniform(4.0, 12.0), 1,
           random.randint(80, 170))
im = im.filter(ImageFilter.GaussianBlur(0.4))
out = Path(__file__).resolve().parents[1] / "assets" / "scratches.png"
im.save(out)
print("saved", out)
