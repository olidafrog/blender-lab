"""Same-procedure measured table for a reference image and a render (plain python3 + Pillow).

  python3 tools/measure.py <reference> <render> [--md]

Both images are scaled to 736 px wide, then measured the same way:
- backdrop level (luma median) in the four frame corners (boxes are frame fractions),
- the subject: pixels darker than 0.82 x the median corner level; its share of the frame, median, p5, p95,
  and the share of subject pixels under luma 12 (the blacks),
- an accent row (median RGB of saturated cyan pixels, e.g. an LCD), printed only if the reference has one,
- backdrop grain: luma std in a flat lower-left patch.
Judge the small rows ("<12 %", grain std) by ratio, not by level. --md prints a markdown table for a reviewer.
Used by cyber-model and cyber-deck-v2 (their scripts/measure.py call this with their reference).
"""
import statistics as st
import sys

from PIL import Image

BOXES = {"backdrop TL": (0.03, 0.15, 0.16, 0.35), "backdrop TR": (0.72, 0.10, 0.95, 0.22),
         "backdrop BL": (0.20, 0.75, 0.40, 0.90), "backdrop BR": (0.82, 0.78, 0.98, 0.98)}


def _px(im, b):
    w, h = im.size
    return list(im.crop((int(b[0] * w), int(b[1] * h), int(b[2] * w), int(b[3] * h))).get_flattened_data())


def luma(p):
    return 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]


def stats(path):
    im = Image.open(path).convert("RGB")
    im.thumbnail((736, 552))
    out, bd = {}, []
    for k, b in BOXES.items():
        out[k] = round(st.median(luma(q) for q in _px(im, b)))
        bd.append(out[k])
    level = st.median(bd)
    data = list(im.get_flattened_data())
    sub = sorted(luma(p) for p in data if luma(p) < level * 0.82 and not (p[2] - p[0] > 30))
    out["subject share %"] = round(100 * len(sub) / len(data))
    out["subject median"] = round(st.median(sub))
    out["subject p5"] = round(sub[int(len(sub) * 0.05)])
    out["subject p95"] = round(sub[int(len(sub) * 0.95)])
    out["subject <12 %"] = round(100 * sum(1 for v in sub if v < 12) / len(sub), 1)
    cy = [p for p in data if p[2] - p[0] > 35 and p[1] > 100]
    out["LCD median RGB"] = tuple(round(st.median(p[i] for p in cy)) for i in range(3)) if cy else None
    out["backdrop grain std"] = round(st.pstdev(luma(q) for q in _px(im, (0.2, 0.75, 0.4, 0.9))), 1)
    return out


def table(ref_path, render_path, md=False):
    ref, ren = stats(ref_path), stats(render_path)
    rows = ["| Measure (script, sRGB 0-255) | Reference | This render |", "|---|---|---|"] if md else []
    for k in ref:
        if k == "LCD median RGB" and ref[k] is None:
            continue
        rows.append(f"| {k} | {ref[k]} | {ren[k]} |" if md else f"{k:22s} ref {str(ref[k]):16s} render {ren[k]}")
    return "\n".join(rows)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    print(table(args[0], args[1], "--md" in sys.argv))
