"""Silhouette gate: how well a render's subject outline matches the reference's.

Run from the repo root:
  tools/blender.sh tools/silhouette.py <ref_mask.png> <render_mask.png> [--size 1000] [--bands 8]
  tools/blender.sh tools/silhouette.py --make-ref <reference.png> <out_mask.png> [--ratio 0.38] [--skip x0,y0,x1,y1]

Masks:
- Reference mask: black subject on white. --make-ref thresholds a reference on (R-B)/R, which
  separates warm clay from a warm backdrop where luma fails (floor shadows are as dark as lit
  clay). --skip blanks a box (a logo), in pixels from the top-left. Check the result by eye.
- Render mask: an RGBA render whose alpha is the subject. Render it with Workbench, FLAT light,
  SINGLE black colour, film transparent and the backdrop hidden (roman-model build.py --mask).

Prints IoU, both bounding boxes, and per horizontal band the widths and the missing / extra
share, so a miss points at a body part. Writes <render_mask>_overlay.png: dark = both,
red = reference only (missing), blue = render only (too much).
IoU catches gross pose and proportion errors; it goes flat near 0.8, so do not rank close
versions by it (knowledge/gotchas/modelling.md).
"""
import sys
from pathlib import Path

import bpy
import numpy as np


def load(path, size=None):
    img = bpy.data.images.load(str(Path(path).resolve()))
    if size:
        img.scale(size, size)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    return px.reshape(h, w, 4)[::-1]            # top-down rows


def save(rgb, path):
    h, w, _ = rgb.shape
    img = bpy.data.images.new(Path(path).stem, w, h, alpha=True)
    rgba = np.concatenate([rgb, np.ones((h, w, 1), np.float32)], axis=2)[::-1]
    img.pixels.foreach_set(rgba.ravel())
    img.filepath_raw = str(Path(path).resolve())
    img.file_format = "PNG"
    img.save()


def opt(argv, name, default):
    return argv[argv.index(name) + 1] if name in argv else default


def make_ref(argv):
    src, out = argv[1], argv[2]
    px = load(src)
    r, b = px[..., 0], px[..., 2]
    mask = (r - b) / np.maximum(r, 1e-4) > float(opt(argv, "--ratio", 0.38))
    skip = opt(argv, "--skip", None)
    if skip:
        x0, y0, x1, y1 = map(int, skip.split(","))
        mask[y0:y1, x0:x1] = False
    v = np.where(mask, 0.0, 1.0).astype(np.float32)
    save(np.stack([v, v, v], axis=2), out)
    print(f"[out] reference mask {out}: subject {mask.mean() * 100:.1f}% of the frame")


def compare(argv):
    size = int(opt(argv, "--size", 1000))
    nb = int(opt(argv, "--bands", 8))
    ref = load(argv[0], size)[..., 0] < 0.5
    ours = load(argv[1], size)[..., 3] > 0.5
    iou = (ref & ours).sum() / max(1, (ref | ours).sum())
    print(f"[out] IoU {iou:.3f}   area ref {ref.mean() * 100:.1f}%  ours {ours.mean() * 100:.1f}%")
    for name, m in (("ref", ref), ("ours", ours)):
        ys, xs = np.where(m)
        if len(xs):
            print(f"[out] bbox {name:4s} x {xs.min()}–{xs.max()}  y {ys.min()}–{ys.max()}")
    ys = np.where(ref.any(1))[0]
    edges = np.linspace(ys.min(), ys.max() + 1, nb + 1).astype(int)
    for y0, y1 in zip(edges, edges[1:]):
        rr, oo = ref[y0:y1], ours[y0:y1]
        miss = (rr & ~oo).sum() / max(1, rr.sum())
        extra = (oo & ~rr).sum() / max(1, rr.sum())
        print(f"[out] y {y0:4d}–{y1:4d}  width ref {rr.sum(1).mean():5.0f} ours {oo.sum(1).mean():5.0f}"
              f"  missing {miss * 100:3.0f}%  extra {extra * 100:3.0f}%")
    rgb = np.ones((size, size, 3), np.float32)
    rgb[ref & ours] = (0.16, 0.16, 0.16)
    rgb[ref & ~ours] = (0.90, 0.24, 0.20)
    rgb[~ref & ours] = (0.20, 0.43, 0.90)
    out = Path(argv[1]).with_name(Path(argv[1]).stem + "_overlay.png")
    save(rgb, out)
    print(f"[out] overlay {out}")


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:]
    make_ref(argv) if argv[0] == "--make-ref" else compare(argv)
