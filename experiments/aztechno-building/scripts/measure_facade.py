"""Same-procedure measured table for the reference and a render (numpy + Pillow, via uv).

  uv run --with numpy --with pillow python scripts/measure_facade.py <render.png> [--md]

Both images are resized to 1400x979. Paint rows use the paint-class masks of scripts/labels.py inside
the facade box, split into sunlit and shade on V (max channel), since red has low luma even in sun. Other rows are
fixed boxes. Values are sRGB medians (0-255); "lit/shade" is the luma ratio.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import labels as LB  # noqa: E402

BOXES = {"sky top": (200, 5, 500, 40), "sky low right": (1300, 300, 1390, 400),
         "pavement": (300, 892, 600, 915), "street": (300, 950, 700, 975),
         "brick neighbour": (1275, 520, 1395, 700), "gf cream": (240, 800, 270, 835),
         "gf base": (475, 850, 510, 875)}
SPLIT = {"red": 170, "cream": 170, "yellow": 180, "orange": 170}   # on V = max channel, not luma


def luma(a):
    return a @ np.array([0.2126, 0.7152, 0.0722])


def table(path):
    im = np.asarray(Image.open(path).convert("RGB").resize((1400, 979), Image.LANCZOS), dtype=np.float32)
    lab, names = LB.labels(path)
    fac = im[LB.BOX[1]:LB.BOX[3], LB.BOX[0]:LB.BOX[2]]
    L = luma(fac)
    V = fac.max(axis=2)
    rows = {}
    for n, t in SPLIT.items():
        m = lab == names.index(n)
        lit, sh = m & (V >= t), m & (V < t) & (V > 40)
        rows[f"{n} lit"] = np.median(fac[lit], 0) if lit.any() else np.zeros(3)
        rows[f"{n} shade"] = np.median(fac[sh], 0) if sh.any() else np.zeros(3)
        rows[f"{n} shade share"] = sh.sum() / max(m.sum(), 1)
    g = lab == names.index("glass")
    vv = np.arange(LB.BOX[1], LB.BOX[3])[:, None] + np.zeros(fac.shape[:2])
    for nm, (v0, v1) in (("glass upper", (185, 360)), ("glass lower", (520, 730))):
        m = g & (vv >= v0) & (vv < v1)
        rows[nm] = np.median(fac[m], 0)
        rows[nm + " p90 luma"] = np.percentile(L[m], 90)
    for k, (u0, v0, u1, v1) in BOXES.items():
        rows[k] = np.median(im[v0:v1, u0:u1].reshape(-1, 3), 0)
    return rows


def fmt(v):
    return f"{v:.2f}" if np.ndim(v) == 0 else "(" + ", ".join(f"{x:.0f}" for x in v) + ")"


def main():
    ref = table(LB.REF)
    ren = table(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None
    md = "--md" in sys.argv
    if md:
        print("| Row | Reference | Render |\n|---|---|---|")
    for k, v in ref.items():
        r = fmt(ren[k]) if ren else "-"
        print(f"| {k} | {fmt(v)} | {r} |" if md else f"[out] {k:22s} ref {fmt(v):18s} render {r}")


if __name__ == "__main__":
    main()
