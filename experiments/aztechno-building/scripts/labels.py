"""Paint-colour label maps of the reference and a render, and per-colour IoU (numpy + Pillow, via uv).

  uv run --with numpy --with pillow python scripts/labels.py <render.png> [--out overlay.png]

Both images are resized to 1400x979 and every pixel in the facade box is given the nearest paint class
(red, orange, yellow, cream, glass = dark or sky-reflecting) by colour after normalising brightness, so the
same sun and shade move both images alike. Prints IoU per class and a mean; --out writes
reference labels | render labels | disagreement (magenta).
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

REF = Path(__file__).parents[1] / "references/ref_main.png"
BOX = (191, 100, 1263, 768)          # facade above the ground floor
CLASSES = {"red": (226, 50, 61), "orange": (231, 150, 95), "yellow": (250, 232, 150), "cream": (232, 226, 200),
           "glass": (120, 135, 160)}          # cool grey: glass that reflects sky
SHOW = {"red": (220, 40, 50), "orange": (240, 140, 70), "yellow": (250, 230, 60), "cream": (240, 240, 225),
        "dark": (20, 20, 30), "glass": (20, 20, 30)}


def labels(path):
    im = np.asarray(Image.open(path).convert("RGB").resize((1400, 979), Image.LANCZOS), dtype=np.float32)
    im = im[BOX[1]:BOX[3], BOX[0]:BOX[2]]
    luma = im @ np.array([0.2126, 0.7152, 0.0722])
    chroma = im / np.maximum(im.max(axis=2, keepdims=True), 1)          # hue and saturation, not level
    names = list(CLASSES)
    ref = np.array([np.array(CLASSES[n]) / max(CLASSES[n]) for n in names])
    d = ((chroma[:, :, None, :] - ref[None, None]) ** 2).sum(-1)
    lab = d.argmin(-1)
    lab[luma < 70] = names.index("glass")                               # dark glass and deep shadow
    return lab, names


def main():
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    a, names = labels(REF)
    b, _ = labels(sys.argv[1])
    ious = []
    for i, n in enumerate(names):
        inter, union = ((a == i) & (b == i)).sum(), ((a == i) | (b == i)).sum()
        ious.append(inter / max(union, 1))
        print(f"[out] {n:7s} IoU {ious[-1]:.3f}  ref share {(a == i).mean():.3f}  render share {(b == i).mean():.3f}")
    print(f"[out] mean IoU {np.mean(ious):.3f}")
    if out:
        pal = np.array([SHOW[n] for n in names], dtype=np.uint8)
        dis = np.where((a != b)[..., None], np.array([255, 0, 255], np.uint8), pal[a] // 3 + 120)
        Image.fromarray(np.concatenate([pal[a], pal[b], dis.astype(np.uint8)], 1)).save(out)


if __name__ == "__main__":
    main()
