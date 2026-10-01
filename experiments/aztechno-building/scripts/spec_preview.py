"""Draw the facade spec (scripts/facade.py) over the reference: flat colours or outlines (plain python3).

  python3 scripts/spec_preview.py <out.png> [--flat]
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).parent))
import facade as F

COL = {"cream": (232, 226, 200), "orange": (235, 150, 95), "yellow": (250, 232, 140), "red": (220, 50, 60),
       "white": (245, 245, 240), "dark": (30, 30, 35)}
ref = Image.open(Path(__file__).parents[1] / "references/ref_main.png").convert("RGB")
flat = "--flat" in sys.argv
im = Image.new("RGB", ref.size, (140, 180, 215)) if flat else ref.copy()
d = ImageDraw.Draw(im)


def loops(e):
    yield e["pts"], e["holes"]
    if e["mirror"]:
        yield F.mirror_pts(e["pts"]), [F.mirror_pts(h) for h in e["holes"]]


if flat:
    d.polygon(F.rect(191, F.TOP, 1263, 768), fill=COL["red"])
    for o in F.OPEN:
        for p in [o["pts"]] + ([F.mirror_pts(o["pts"])] if o["mirror"] else []):
            d.polygon(p, fill=(25, 22, 22))
for e in sorted(F.EL, key=lambda e: e["d1"]):
    for p, hs in loops(e):
        if flat:
            d.polygon(p, fill=COL.get(e["mat"], (255, 0, 255)))
            for h in hs:
                d.polygon(h, fill=(25, 22, 22) if e["name"] not in ("column", "tower", "ctower") else None)
        else:
            d.line(p + [p[0]], fill=(0, 255, 0), width=1)
            for h in hs:
                d.line(h + [h[0]], fill=(0, 255, 255), width=1)
for c in F.DISCS:
    for cu in [c["cu"]] + ([2 * F.AXIS - c["cu"]] if c["mirror"] else []):
        r, R = c["r"], c["r"] + c["ring"]
        if flat:
            d.ellipse((cu - R, c["cv"] - R, cu + R, c["cv"] + R), fill=COL[c["mat"]])
            d.ellipse((cu - r, c["cv"] - r, cu + r, c["cv"] + r), fill=(40, 50, 60))
        else:
            d.ellipse((cu - R, c["cv"] - R, cu + R, c["cv"] + R), outline=(255, 0, 255))
if not flat:
    for o in F.OPEN:
        for p in [o["pts"]] + ([F.mirror_pts(o["pts"])] if o["mirror"] else []):
            d.line(p + [p[0]], fill=(255, 255, 0), width=1)
im.save(sys.argv[1])
print("[out] saved", sys.argv[1])
