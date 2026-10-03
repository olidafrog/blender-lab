"""Plan slices and sections of the aligned scan, 1 px = 1 cm, grid every 0.5 m (1 m darker)."""
import sys
import numpy as np
from scan_tools import load_raw, align, slice_segments, write_png, face_data, EXP

OUT = EXP / "assets/scan_views"
OUT.mkdir(parents=True, exist_ok=True)
v, f = load_raw()
p, yaw, floor = align(v, f)
PX = 100  # px per metre


def canvas(x0, x1, y0, y1):
    W, H = int((x1 - x0) * PX) + 1, int((y1 - y0) * PX) + 1
    img = np.full((H, W, 3), 255, np.uint8)
    for g in np.arange(np.ceil(x0 * 2) / 2, x1, 0.5):
        img[:, int((g - x0) * PX)] = (200, 200, 255) if g % 1 else (120, 120, 255)
    for g in np.arange(np.ceil(y0 * 2) / 2, y1, 0.5):
        img[H - 1 - int((g - y0) * PX)] = (200, 200, 255) if g % 1 else (120, 120, 255)
    return img


def draw_segs(img, segs, x0, y0, col):
    H = img.shape[0]
    for a, b in segs:
        n = int(np.hypot(*(b - a)) * PX * 2) + 2
        t = np.linspace(0, 1, n)[:, None]
        q = a + (b - a) * t
        cx = ((q[:, 0] - x0) * PX).astype(int)
        cy = H - 1 - ((q[:, 1] - y0) * PX).astype(int)
        ok = (cx >= 0) & (cx < img.shape[1]) & (cy >= 0) & (cy < H)
        img[cy[ok], cx[ok]] = col


x0, x1 = p[:, 0].min() - 0.1, p[:, 0].max() + 0.1
y0, y1 = p[:, 1].min() - 0.1, p[:, 1].max() + 0.1
cols = {0.3: (0, 0, 0), 1.0: (220, 0, 0), 2.5: (0, 150, 0), 3.85: (255, 140, 0)}
img = canvas(x0, x1, y0, y1)
for h, col in cols.items():
    draw_segs(img, slice_segments(p, f, h), x0, y0, col)
write_png(OUT / "plan_slices.png", img)
print("plan origin", round(x0, 2), round(y0, 2), "size", img.shape)

# sections: swap axes so the cut plane is horizontal for slice_segments
for name, axis, vals in (("long", 1, [-2.0, 0.0, 2.0]), ("cross", 0, [-3.5, -1.0, 2.0, 4.5])):
    q = p.copy()
    other = 1 - axis
    q2 = np.stack([q[:, other], q[:, 2], q[:, axis]], 1)  # (horizontal, up, cut axis)
    a0, a1 = q2[:, 0].min() - 0.1, q2[:, 0].max() + 0.1
    img = canvas(a0, a1, -0.3, 4.5)
    palette = [(0, 0, 0), (220, 0, 0), (0, 150, 0), (255, 140, 0)]
    for val, col in zip(vals, palette):
        draw_segs(img, slice_segments(q2, f, val), a0, -0.3, col)
    write_png(OUT / f"section_{name}.png", img)
    print(name, "origin", round(a0, 2), -0.3, "cuts", vals)
