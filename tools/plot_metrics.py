#!/usr/bin/env python3
"""Stroke statistics of plot SVGs (from tools/plot_svg.py), to check fragments without a reviewer.

Plain python3:
  python3 tools/plot_metrics.py <folder or file.svg> [--short 8] [--top 12]

Per plot: strokes on the "lines" layer, how many are shorter than --short mm, and the drawn length.
Sorted by the share of short strokes, worst first; the last line is the total. Compare two versions
of a build with it before spending a review on "fragments".
"""
import math
import re
import sys
from pathlib import Path


def lengths(svg):
    text = Path(svg).read_text(encoding="utf-8")
    body = text[text.index('id="lines"'):]
    body = body[:body.index("</g>")]
    out = []
    for d in re.findall(r'd="([^"]+)"', body):
        pts = [tuple(map(float, p.split(","))) for p in re.findall(r"[-\d.]+,[-\d.]+", d)]
        out.append(sum(math.dist(a, b) for a, b in zip(pts, pts[1:])))
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opt = dict(zip(sys.argv[1:], sys.argv[2:]))
    short, top = float(opt.get("--short", 8)), int(opt.get("--top", 12))
    args = [a for a in args if a not in (opt.get("--short"), opt.get("--top"))] or sys.exit(__doc__)
    src = Path(args[0])
    files = [src] if src.is_file() else sorted(f for f in src.glob("*.svg") if not f.stem.endswith(("_check", "_sheet")))
    rows = []
    for f in files:
        L = lengths(f)
        n = sum(l < short for l in L)
        rows.append((n / max(len(L), 1), f.stem, len(L), n, round(sum(L))))
    for share, name, total, n, drawn in sorted(rows, reverse=True)[:top]:
        print(f"{name:22s} strokes {total:4d}  under {short:g} mm {n:4d} ({share:.0%})  drawn {drawn} mm")
    print(f"[out] {len(rows)} plots, {sum(r[2] for r in rows)} strokes, {sum(r[3] for r in rows)} under {short:g} mm, "
          f"{sum(r[4] for r in rows)} mm drawn")
