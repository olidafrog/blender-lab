"""Side-by-side review material: reference | render, full frame and 1:1 crops at the same points.

    python3 experiments/wax-seal-chaos/scripts/sbs.py v01 [x,y ...]

Writes reviews/sbs_<v>/full.png and crop_<x>_<y>.png. The render must be the reference's size.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

EXP = Path(__file__).resolve().parents[1]
POINTS = [(150, 650), (1050, 650), (1000, 1050), (450, 950), (600, 500), (100, 1000)]


def label(im, text):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 8 * len(text) + 12, 20), fill=(0, 0, 0))
    d.text((6, 4), text, fill=(255, 255, 255))
    return im


def pair(a, b, gap=8):
    c = Image.new("RGB", (a.width + b.width + gap, max(a.height, b.height)), (0, 0, 0))
    c.paste(a, (0, 0)); c.paste(b, (a.width + gap, 0))
    return c


if __name__ == "__main__":
    v = sys.argv[1]
    pts = [tuple(int(n) for n in p.split(",")) for p in sys.argv[2:]] or POINTS
    ref = Image.open(EXP / "references" / "ref_clean.png").convert("RGB")
    ren = Image.open(EXP / "renders" / f"{v}.png").convert("RGB")
    assert ren.size == ref.size, f"render {ren.size} != reference {ref.size}"
    out = EXP / "reviews" / f"sbs_{v}"
    out.mkdir(parents=True, exist_ok=True)
    half = (ref.width // 2, ref.height // 2)
    pair(label(ref.resize(half), "REFERENCE"), label(ren.resize(half), "RENDER")).save(out / "full.png")
    s = 256
    for x, y in pts:
        box = (max(0, x - s), max(0, y - s), min(ref.width, x + s), min(ref.height, y + s))
        pair(label(ref.crop(box), f"REF {x},{y}"), label(ren.crop(box), f"RENDER {x},{y}")).save(out / f"crop_{x}_{y}.png")
    print(f"[out] {out}")
