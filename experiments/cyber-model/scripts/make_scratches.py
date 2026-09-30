"""Scratch mask (assets/scratches.png, grey, 2048^2) drawn with PIL. Run once with system python3.

  python3 experiments/cyber-model/scripts/make_scratches.py

Covers a 250 x 250 mm square, x -100..150 mm, y -110..140 mm, top-down in device coordinates
(0.122 mm per px). Short, mostly straight, light strokes, clustered on the lid and the right plate,
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
    dx, dy = math.cos(ang) * length / 2, math.sin(ang) * length / 2
    # slightly bowed: two segments through a nudged midpoint
    mx, my = cx + random.uniform(-0.25, 0.25), cy + random.uniform(-0.25, 0.25)
    pts = [to_px(cx - dx, cy - dy), to_px(mx, my), to_px(cx + dx, cy + dy)]
    d.line(pts, fill=val, width=w)


# clusters: (centre x, centre y, radius mm, count) in device mm; lid, right plate, shield, lower block, wing
for cx, cy, rad, count in ((47, 2, 20, 46), (52, -28, 16, 22), (12, -8, 26, 22), (-25, -70, 18, 10), (-35, -22, 16, 8)):
    for _ in range(count):
        r = rad * math.sqrt(random.random())
        a = random.uniform(0, 2 * math.pi)
        base = random.choice((0.5, 0.65, 2.4, 2.6))       # a dominant stroke direction (radians)
        stroke(cx + r * math.cos(a), cy + r * math.sin(a), base + random.uniform(-0.25, 0.25),
               random.uniform(1.5, 5.5), random.choice((1, 2, 2)), random.randint(110, 255))
# a thin uniform scatter
for _ in range(60):
    stroke(random.uniform(-90, 90), random.uniform(-100, 130), random.uniform(0, math.pi), random.uniform(1.5, 5.0), 2, random.randint(70, 170))
im = im.filter(ImageFilter.GaussianBlur(0.6))
out = Path(__file__).resolve().parents[1] / "assets" / "scratches.png"
im.save(out)
print("saved", out)
