"""Photographic output stage (plain python3 + Pillow): what a camera and its processing do to an image.

  python3 tools/photo_finish.py <in.png> <out.png> <width> <height> <sharpen_px> <sharpen_pct> <jpeg_q>

Downsamples the supersampled render with Lanczos, applies an unsharp mask, and round-trips through
JPEG at the given quality. From aztechno-building: the reference is a sharpened, pixel-crisp JPEG (edge ratio 3.44 against a
raw render's 2.25: fork advisor, round 7). jpeg_q 0 skips the JPEG step.
"""
import io
import sys

from PIL import Image, ImageFilter

src, dst = sys.argv[1], sys.argv[2]
w, h, rad, pct, q = int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])
im = Image.open(src).convert("RGB")
if im.size != (w, h):
    im = im.resize((w, h), Image.LANCZOS)
if rad > 0 and pct > 0:
    im = im.filter(ImageFilter.UnsharpMask(radius=rad, percent=pct, threshold=0))
if q > 0:
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, subsampling=0)
    buf.seek(0)
    im = Image.open(buf).convert("RGB")
im.save(dst)
print(f"[out] photo finish {src} -> {dst} ({w}x{h}, unsharp {rad}px {pct}%, jpeg q{q})")
