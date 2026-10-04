"""A tileable detail texture from a flat, evenly lit patch of a photo (a product close-up of the real material).

  uv run --with numpy --with pillow python tools/seamless_patch.py <photo> <x0,y0,x1,y1> <out.png> [blur_px]

Takes the box from the photo, divides its luminance by a heavy blur (removes the lighting gradient, keeps the
weave, grain and heather; mean 0.5 after), and makes it seamless: a half-offset copy blended in with a sine
window, so the original's edges never show. Prints the strongest period of the pattern from an FFT, in pixels:
divide the tile's width by it and multiply by the real period (e.g. the thread pitch) to get the tile size in
metres. Colour stays a measured input in the shader; this is a luminance detail map (from apartment-model's
sofa fabric: a Swyft close-up of Pumice, 512 px patch, 5 px weave period, 11 cm tile).
"""
import math
import sys

import numpy as np
from PIL import Image, ImageChops, ImageFilter

src, box, dst = sys.argv[1], [int(v) for v in sys.argv[2].split(",")], sys.argv[3]
blur = float(sys.argv[4]) if len(sys.argv) > 4 else 30.0

lum = Image.open(src).convert("L").crop(box)
a = np.asarray(lum, dtype=np.float32)
b = np.asarray(lum.filter(ImageFilter.GaussianBlur(blur)), dtype=np.float32)
det = Image.fromarray(np.clip(a / np.maximum(b, 1.0) * 128.0, 0, 255).astype(np.uint8))

w, h = det.size
off = ImageChops.offset(det, w // 2, h // 2)
yy, xx = np.mgrid[0:h, 0:w]
mask = (np.sin(math.pi * (xx + 0.5) / w) * np.sin(math.pi * (yy + 0.5) / h)) ** 0.6
tile = Image.composite(det, off, Image.fromarray((mask * 255).astype(np.uint8)))
tile.save(dst)

f = a - a.mean()
F = np.abs(np.fft.fftshift(np.fft.fft2(f * np.hanning(h)[:, None] * np.hanning(w)[None])))
cy, cx = h // 2, w // 2
F[cy - 3:cy + 4, cx - 3:cx + 4] = 0
iy, ix = np.unravel_index(np.argmax(F), F.shape)
period = w / max(math.hypot(ix - cx, (iy - cy) * w / h), 1e-6)
t = np.asarray(tile, dtype=np.float32)
print(f"[out] {dst}: {w}x{h}, mean {t.mean() / 255:.3f}, std {t.std() / 255:.3f}, strongest period {period:.2f} px")
