"""Measure a line screen or fine pattern: period (px) and line angle of the strongest FFT peaks.

Run:
  tools/blender.sh tools/screen_fft.py <image> <x> <y> <size>

Analyses the size x size square with its top-left corner at (x, y), in image pixels from the top.
Pick a flat tint with no edges. Run it on the reference and on the render, and compare.
Angles are in degrees, counter-clockwise from horizontal, 0-180. Ported from claude-photoshop.
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
    # Blender stores rows bottom-up; 8-bit files load as display sRGB 0-1.
    return px.reshape(h, w, 4)[::-1, :, :3] * 255.0


def peaks(a, n=4, rmin=8):
    a = a - a.mean()
    size = a.shape[0]
    F = np.abs(np.fft.fftshift(np.fft.fft2(a * np.outer(np.hanning(size), np.hanning(size)))))
    c = size // 2
    y, x = np.mgrid[-c:size - c, -c:size - c]
    # drop the DC region and the mirrored half of the spectrum
    F[np.hypot(x, y) < rmin] = 0
    F[y < 0] = 0
    F[(y == 0) & (x < 0)] = 0
    out = []
    for _ in range(n):
        i = np.unravel_index(F.argmax(), F.shape)
        fy, fx = i[0] - c, i[1] - c
        period = size / np.hypot(fx, fy)
        # lines run perpendicular to the frequency vector; image y points down
        angle = (np.degrees(np.arctan2(-fy, fx)) + 90) % 180
        out.append(f"{period:.2f} px @ {angle:.1f}°")
        F[max(0, i[0] - 3):i[0] + 4, max(0, i[1] - 3):i[1] + 4] = 0
    return out


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    path, x, y, size = Path(argv[0]).resolve(), int(argv[1]), int(argv[2]), int(argv[3])
    arr = load(path)
    crop = arr[y:y + size, x:x + size]
    print("[out] mean RGB", [round(float(v), 1) for v in crop.reshape(-1, 3).mean(0)])
    for name, ch in (("L", crop.mean(2)), ("R", crop[..., 0]), ("G", crop[..., 1]), ("B", crop[..., 2])):
        print(f"[out] {name}", ", ".join(peaks(ch)))


main()
