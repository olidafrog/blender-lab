"""Per-colour-class table for a reference and a render, with regions masked out (numpy + Pillow, via uv).

  uv run --with numpy --with pillow python tools/measure_classes.py <ref> <render> --classes <classes.json>
      [--box u0,v0,u1,v1] [--exclude <mask.png>] [--dark 70] [--split 170] [--md]

For subjects painted in a few flat colours (a facade, a toy, packaging). Each pixel in the box gets the
nearest class by chroma (colour / its max channel, so sun and shade of one paint share a class); pixels
darker than --dark (luma) and pixels white in --exclude (a mask the size of the reference, e.g. the glazing
drawn from a traced spec) are left out of every class. Per class: share of the box, IoU against the
reference, sunlit median and shade median (split on the max channel at --split, since a sunlit red has low
luma), and the shade share. classes.json: {"red": [226, 50, 61], ...}, sRGB from the reference.
From aztechno-building, where an unmasked version counted grey glass as shaded cream and misled four rounds.
"""
import argparse
import json

import numpy as np
from PIL import Image


def load(path, size=None):
    im = Image.open(path).convert("RGB")
    if size and im.size != size:
        im = im.resize(size, Image.LANCZOS)
    return np.asarray(im, dtype=np.float32)


def classify(a, names, ref_cols, dark):
    chroma = a / np.maximum(a.max(axis=2, keepdims=True), 1)
    d = ((chroma[:, :, None, :] - ref_cols[None, None]) ** 2).sum(-1)
    lab = d.argmin(-1)
    lab[a @ np.array([0.2126, 0.7152, 0.0722]) < dark] = -1
    return lab


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref"), ap.add_argument("render")
    ap.add_argument("--classes", required=True)
    ap.add_argument("--box", default=None)
    ap.add_argument("--exclude", default=None)
    ap.add_argument("--dark", type=float, default=70)
    ap.add_argument("--split", type=float, default=170)
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    cls = json.load(open(a.classes))
    names = list(cls)
    cols = np.array([np.array(cls[n], np.float32) / max(cls[n]) for n in names])
    ref = load(a.ref)
    h, w = ref.shape[:2]
    ren = load(a.render, (w, h))
    u0, v0, u1, v1 = [int(x) for x in a.box.split(",")] if a.box else (0, 0, w, h)
    keep = np.ones((h, w), bool)
    if a.exclude:
        keep = np.asarray(Image.open(a.exclude).convert("L").resize((w, h)), np.uint8) < 128
    sl = (slice(v0, v1), slice(u0, u1))
    keep = keep[sl]
    out = {}
    labs = {}
    for tag, img in (("ref", ref), ("render", ren)):
        x = img[sl]
        lab = classify(x, names, cols, a.dark)
        lab[~keep] = -2
        labs[tag] = lab
        V = x.max(axis=2)
        for i, n in enumerate(names):
            m = lab == i
            lit, sh = m & (V >= a.split), m & (V < a.split)
            out[(tag, n)] = dict(share=m.mean(), lit=np.median(x[lit], 0) if lit.any() else np.zeros(3),
                                 shade=np.median(x[sh], 0) if sh.any() else np.zeros(3),
                                 shade_share=sh.sum() / max(m.sum(), 1))
    rows = []
    for i, n in enumerate(names):
        r, x = out[("ref", n)], out[("render", n)]
        iou = ((labs["ref"] == i) & (labs["render"] == i)).sum() / max(((labs["ref"] == i) | (labs["render"] == i)).sum(), 1)
        f = lambda c: "(" + ", ".join(f"{v:.0f}" for v in c) + ")"
        rows.append((f"{n} lit", f(r["lit"]), f(x["lit"])))
        rows.append((f"{n} shade", f(r["shade"]), f(x["shade"])))
        rows.append((f"{n} shade share", f"{r['shade_share']:.2f}", f"{x['shade_share']:.2f}"))
        rows.append((f"{n} share / IoU", f"{r['share']:.3f}", f"{x['share']:.3f} / {iou:.3f}"))
    if a.md:
        print("| Row | Reference | Render |\n|---|---|---|")
        for k, r, x in rows:
            print(f"| {k} | {r} | {x} |")
    else:
        for k, r, x in rows:
            print(f"[out] {k:22s} ref {r:18s} render {x}")
    print(f"[out] excluded {100 * (~keep).mean():.1f} % of the box")


if __name__ == "__main__":
    main()
