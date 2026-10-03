"""Pre-review gate: did the change reach the pixels? Also cheap image stats.

Run from the repo root:
  tools/blender.sh tools/metrics.py <render>                          # stats of one render
  tools/blender.sh tools/metrics.py <prev> <cur>                      # what changed, frame and quadrants
  tools/blender.sh tools/metrics.py <prev> <cur> <x,y[,size]> ...     # plus target crops (the area you fixed)

Options (after the paths): --size N  default crop size (512)   --thresh T  changed-pixel threshold (2/255)
  --expect-same  for refactors (a clean-up, a move to the library): the goal is NO change, so the
                 verdict passes only when every region is under 1% changed, and says not to review.

Stats per region: mean and std (0-255 sRGB luma), clipped share (>=251), black share (<=4),
lit share (>25), mean gradient on lit pixels, and the share of lit pixels with gradient >20 and >40.
Diff per region: MAE, max diff, changed-pixel share (any channel differs by more than --thresh).

Verdict: if target crops are given, each must have >= 1% changed pixels (or >= 0.05% moved by more
than 64 levels: a thin-line geometry change); with none, the whole
frame must. "NO CHANGE" means do not spend a review on this version. EXR input is converted
from linear to sRGB first. Images of different sizes: cur is resampled to prev's size.
"""
import sys
from pathlib import Path

import bpy
import numpy as np

MIN_CHANGED = 1.0  # percent of pixels in a target region


def load(path):
    img = bpy.data.images.load(str(path))
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    rgb = px.reshape(h, w, 4)[::-1, :, :3]  # top-down
    if img.is_float or path.suffix.lower() == ".exr":
        rgb = np.clip(rgb, 0, 1)
        rgb = np.where(rgb <= 0.0031308, rgb * 12.92, 1.055 * np.power(rgb, 1 / 2.4) - 0.055)
    return rgb * 255.0


def resample(a, h, w):
    ys = (np.arange(h) * a.shape[0] / h).astype(int)
    xs = (np.arange(w) * a.shape[1] / w).astype(int)
    return a[ys][:, xs]


def luma(a):
    return a @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def stats(a):
    L = luma(a)
    g = np.zeros_like(L)
    g[:, :-1] += np.abs(np.diff(L, axis=1))
    g[:-1, :] += np.abs(np.diff(L, axis=0))
    lit = a.max(axis=2) > 25
    lg = g[lit]
    n = max(lg.size, 1)
    return dict(mean=L.mean(), std=L.std(), clip=100 * (L >= 251).mean(), black=100 * (L <= 4).mean(),
                lit=100 * lit.mean(), grad=lg.mean() if lg.size else 0.0,
                g20=100 * (lg > 20).sum() / n, g40=100 * (lg > 40).sum() / n)


def fmt_stats(s):
    return (f"mean {s['mean']:6.1f} std {s['std']:5.1f} clip {s['clip']:5.2f}% black {s['black']:5.1f}% "
            f"lit {s['lit']:5.1f}% grad {s['grad']:5.2f} g20 {s['g20']:5.2f}% g40 {s['g40']:5.2f}%")


def regions(h, w, size, targets):
    out = [("frame", 0, h, 0, w, False)]
    pts = {"centre": (w // 2, h // 2), "tl": (w // 4, h // 4), "tr": (3 * w // 4, h // 4),
           "bl": (w // 4, 3 * h // 4), "br": (3 * w // 4, 3 * h // 4)}
    for label, (x, y) in pts.items():
        out.append((label, *box(x, y, size, h, w), False))
    for (x, y, s) in targets:
        out.append((f"target {x},{y}", *box(x, y, s, h, w), True))
    return out


def box(x, y, s, h, w):
    s = min(s, h, w)
    y0 = min(max(y - s // 2, 0), h - s)
    x0 = min(max(x - s // 2, 0), w - s)
    return y0, y0 + s, x0, x0 + s


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    size, thresh, paths, targets, same = 512, 2.0, [], [], False
    it = iter(argv)
    for a in it:
        if a == "--size":
            size = int(next(it))
        elif a == "--thresh":
            thresh = float(next(it))
        elif a == "--expect-same":
            same = True
        elif "," in a and not Path(a).exists():
            v = [int(float(t)) for t in a.split(",")]
            targets.append((v[0], v[1], v[2] if len(v) > 2 else None))
        else:
            paths.append(Path(a).resolve())
    if not paths or len(paths) > 2:
        sys.exit(__doc__)
    targets = [(x, y, s or size) for x, y, s in targets]

    if len(paths) == 1:
        a = load(paths[0])
        h, w, _ = a.shape
        print(f"[out] {paths[0].name}  {w}x{h}")
        for label, y0, y1, x0, x1, _ in regions(h, w, size, targets):
            print(f"[out]   {label:>16}  {fmt_stats(stats(a[y0:y1, x0:x1]))}")
        return

    prev, cur = load(paths[0]), load(paths[1])
    h, w, _ = prev.shape
    if cur.shape != prev.shape:
        print(f"[out] note: resampled {paths[1].name} {cur.shape[1]}x{cur.shape[0]} to {w}x{h}")
        cur = resample(cur, h, w)
    print(f"[out] prev {paths[0].name}  cur {paths[1].name}  {w}x{h}  threshold {thresh:g}/255")
    verdict = []
    for label, y0, y1, x0, x1, is_target in regions(h, w, size, targets):
        p, c = prev[y0:y1, x0:x1], cur[y0:y1, x0:x1]
        d = np.abs(c - p)
        changed = 100 * (d.max(axis=2) > thresh).mean()
        strong = 100 * (d.max(axis=2) > 64).mean()   # hard edges moved: thin-line geometry (an arch outline, a bar)
        sp, sc = stats(p), stats(c)
        print(f"[out]   {label:>16}  MAE {d.mean():6.2f}  max {d.max():5.0f}  changed {changed:6.2f}%  "
              f"mean {sp['mean']:.1f}->{sc['mean']:.1f}  std {sp['std']:.1f}->{sc['std']:.1f}  "
              f"clip {sp['clip']:.2f}->{sc['clip']:.2f}%  g20 {sp['g20']:.2f}->{sc['g20']:.2f}%")
        if is_target or (not targets and label == "frame"):
            verdict.append((label, changed, strong))
    if same:
        moved = [f"{lab} ({pct:.2f}%)" for lab, pct, _ in verdict if pct >= MIN_CHANGED]
        if moved:
            print(f"[out] VERDICT: CHANGED in {', '.join(moved)}. A refactor should not move pixels; find what changed.")
        else:
            print("[out] VERDICT: NO CHANGE, as expected for a refactor. Do not spend a review.")
        return
    # a thin-line geometry change moves few pixels but moves them hard; GPU noise never does
    dead = [f"{lab} ({pct:.2f}%)" for lab, pct, st in verdict if pct < MIN_CHANGED and st < 0.05]
    if dead:
        print(f"[out] VERDICT: NO CHANGE in {', '.join(dead)}. Do not spend a review; find why the change did not reach the pixels.")
    else:
        print(f"[out] VERDICT: changed ({', '.join(f'{lab} {pct:.1f}%' for lab, pct, _ in verdict)}). OK to review.")


main()
