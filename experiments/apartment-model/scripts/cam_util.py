"""Radial lens distortion for the iPhone photos: undistort a photo to the pinhole the renders use.

Model: a pinhole pixel u (centre c, focal f_px) is imaged at c + (u - c) * (1 + k1 * r^2), r = |u - c| / f_px.
k1 > 0 is pincushion, k1 < 0 barrel. Fitted per camera in refine_cam.py; 0 means a pure pinhole.
"""
import numpy as np


def undistort(img, k1, lens, sensor_w, out_w, out_h):
    """img: HxWxC float (any size, same aspect). Returns out_h x out_w x C sampled bilinearly."""
    H, W = img.shape[:2]
    f = lens / sensor_w * out_w
    yy, xx = np.mgrid[0:out_h, 0:out_w].astype(np.float32)
    cx, cy = out_w / 2, out_h / 2
    dx, dy = (xx + 0.5 - cx), (yy + 0.5 - cy)
    s = 1 + k1 * (dx * dx + dy * dy) / (f * f)
    sx = (cx + dx * s) * (W / out_w) - 0.5
    sy = (cy + dy * s) * (H / out_h) - 0.5
    x0 = np.clip(np.floor(sx).astype(int), 0, W - 2); y0 = np.clip(np.floor(sy).astype(int), 0, H - 2)
    fx = np.clip(sx - x0, 0, 1)[..., None]; fy = np.clip(sy - y0, 0, 1)[..., None]
    if img.ndim == 2:
        img = img[..., None]
    a = img[y0, x0] * (1 - fx) + img[y0, x0 + 1] * fx
    b = img[y0 + 1, x0] * (1 - fx) + img[y0 + 1, x0 + 1] * fx
    out = a * (1 - fy) + b * fy
    inside = ((sx >= 0) & (sx <= W - 1) & (sy >= 0) & (sy <= H - 1))[..., None]
    return np.where(inside, out, 0.0).squeeze()
