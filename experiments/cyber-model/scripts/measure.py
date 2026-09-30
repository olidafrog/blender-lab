"""Measured targets for a render vs the reference, same procedure on both (PIL only).
   python3 scripts/measure.py renders/v01.png            prints a table; --md prints markdown for the reviewer prompt
Regions are frame fractions, so any resolution works. Subject = pixels well below the local backdrop level."""
import statistics as st
import sys
from pathlib import Path

from PIL import Image

root = Path(__file__).resolve().parents[1]
BOXES = {"backdrop TL": (0.03, 0.15, 0.16, 0.35), "backdrop TR": (0.72, 0.10, 0.95, 0.22),
         "backdrop BL": (0.20, 0.75, 0.40, 0.90), "backdrop BR": (0.82, 0.78, 0.98, 0.98)}


def px(im, b):
    w, h = im.size
    return list(im.crop((int(b[0] * w), int(b[1] * h), int(b[2] * w), int(b[3] * h))).convert("RGB").getdata())


def luma(p):
    return 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]


def stats(path):
    im = Image.open(path).convert("RGB")
    im.thumbnail((736, 552))
    out = {}
    bd = []
    for k, b in BOXES.items():
        p = px(im, b)
        out[k] = round(st.median(luma(q) for q in p))
        bd.append(out[k])
    level = st.median(bd)
    data = list(im.getdata())
    sub = [luma(p) for p in data if luma(p) < level * 0.82 and not (p[2] - p[0] > 30)]
    sub.sort()
    out["subject share %"] = round(100 * len(sub) / len(data))
    out["subject median"] = round(st.median(sub))
    out["subject p5"] = round(sub[int(len(sub) * 0.05)])
    out["subject p95"] = round(sub[int(len(sub) * 0.95)])
    out["subject <12 %"] = round(100 * sum(1 for v in sub if v < 12) / len(sub), 1)
    cy = [p for p in data if p[2] - p[0] > 35 and p[1] > 100]
    out["LCD median RGB"] = tuple(round(st.median(p[i] for p in cy)) for i in range(3)) if cy else None
    out["backdrop grain std"] = round(st.pstdev(luma(q) for q in px(im, (0.2, 0.75, 0.4, 0.9))), 1)
    return out


if __name__ == "__main__":
    ref, ren = stats(root / "references/ref_radio.jpg"), stats(sys.argv[1])
    md = "--md" in sys.argv
    if md:
        print("| Measure (script, sRGB 0-255) | Reference | This render |\n|---|---|---|")
    for k in ref:
        print(f"| {k} | {ref[k]} | {ren[k]} |" if md else f"{k:22s} ref {str(ref[k]):16s} render {ren[k]}")
