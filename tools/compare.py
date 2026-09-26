"""Compare a render against a reference: side-by-side PNG + numeric diagnostics.

Run:
  tools/blender.sh tools/compare.py <reference> <render> [out.png]

Prints mean absolute error (0-255, sRGB) overall and for the centre, and sampled colours along the
vertical and horizontal centre lines of both images. Images must be the same size.
"""
import sys
from pathlib import Path

import bpy
import numpy as np


def load(path):
    img = bpy.data.images.load(str(path))
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    # Blender stores bottom-up and (for 8-bit files) already in display sRGB values 0-1.
    arr = px.reshape(h, w, 4)[::-1, :, :3] * 255.0
    return img, arr


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    # bpy.data.images.load doesn't resolve paths against the shell's cwd; make them absolute.
    ref_path, ren_path = Path(argv[0]).resolve(), Path(argv[1]).resolve()
    out_path = Path(argv[2]).resolve() if len(argv) > 2 else ren_path.with_name(ren_path.stem + "_vs_ref.png")
    _, ref = load(ref_path)
    _, ren = load(ren_path)
    if ref.shape != ren.shape:
        sys.exit(f"size mismatch {ref.shape} vs {ren.shape}")
    h, w, _ = ref.shape
    diff = np.abs(ref - ren)
    print(f"[out] MAE overall {diff.mean():.1f}")
    ys, xs = slice(h // 5, 4 * h // 5), slice(w // 10, 9 * w // 10)
    print(f"[out] MAE subject-box {diff[ys, xs].mean():.1f}")

    def row(label, pts):
        print(f"[out] {label}")
        for (y, x) in pts:
            r = ref[y - 2:y + 3, x - 2:x + 3].reshape(-1, 3).mean(0).astype(int)
            n = ren[y - 2:y + 3, x - 2:x + 3].reshape(-1, 3).mean(0).astype(int)
            print(f"[out]   y={y:4d} x={x:4d}  ref {tuple(r)}  ren {tuple(n)}")

    cx = w // 2
    row("vertical centre", [(y, cx) for y in range(180, 1100, 30)])
    cy = int(h * 0.5)
    row("horizontal centre", [(cy, x) for x in list(range(20, 220, 15)) + [416] + list(range(620, 820, 15))])

    # Side-by-side: reference left, render right.
    sbs = np.concatenate([ref, np.full((h, 16, 3), 255.0), ren], axis=1)
    H, W, _ = sbs.shape
    out = bpy.data.images.new("sbs", W, H, alpha=False)
    rgba = np.concatenate([sbs / 255.0, np.ones((H, W, 1))], axis=2)[::-1].astype(np.float32)
    out.pixels.foreach_set(rgba.ravel())
    out.filepath_raw = str(out_path)
    out.file_format = "PNG"
    out.save()
    print(f"[out] SIDE-BY-SIDE {out_path}")


main()
