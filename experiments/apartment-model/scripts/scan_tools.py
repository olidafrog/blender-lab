"""Scan measuring helpers (numpy only; run with Blender's bundled python).

Loads the Polycam OBJ once into an .npz cache, aligns it (yaw from wall normals, floor to 0),
and writes plan/section rasters as PNG so the shell can be measured in metres.
Scan frame after align: x, y horizontal (metres), z up, floor z = 0.
"""
import struct
import sys
import zlib
from pathlib import Path

import numpy as np

EXP = Path(__file__).resolve().parents[1]
OBJ = EXP / "references/scans/03_10_2026 2/03_10_2026.obj"
CACHE = EXP / "assets/cache/scan.npz"


def write_png(path, img):
    """img: HxW or HxWx3 uint8."""
    img = np.ascontiguousarray(img)
    if img.ndim == 2:
        img = np.stack([img] * 3, -1)
    h, w, _ = img.shape
    raw = b"".join(b"\x00" + img[r].tobytes() for r in range(h))
    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b"")
    Path(path).write_bytes(png)


def load_raw():
    if CACHE.exists():
        d = np.load(CACHE)
        return d["v"], d["f"]
    v, f = [], []
    for line in open(OBJ):
        if line.startswith("v "):
            v.append(line.split()[1:4])
        elif line.startswith("f "):
            f.append([int(t.split("/")[0]) for t in line.split()[1:4]])
    v = np.array(v, dtype=np.float64)
    f = np.array(f, dtype=np.int64) - 1
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    np.savez(CACHE, v=v, f=f)
    return v, f


def face_data(v, f):
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    n = np.cross(b - a, c - a)
    ar = np.linalg.norm(n, axis=1) / 2
    n = n / (2 * ar[:, None] + 1e-12)
    return n, ar, (a + b + c) / 3


def align(v, f, yaw_deg=None):
    """OBJ is Y-up. Return z-up verts rotated so walls are axis-aligned, floor at z=0."""
    p = np.stack([v[:, 0], -v[:, 2], v[:, 1]], 1)       # (x, -z, y): right-handed z-up
    n, ar, c = face_data(p, f)
    if yaw_deg is None:
        wall = np.abs(n[:, 2]) < 0.15
        ang = np.arctan2(n[wall, 1], n[wall, 0])
        # 4-fold circular mean
        z = (ar[wall] * np.exp(4j * ang)).sum()
        yaw_deg = -np.degrees(np.angle(z) / 4)
    t = np.radians(yaw_deg)
    R = np.array([[np.cos(t), -np.sin(t), 0], [np.sin(t), np.cos(t), 0], [0, 0, 1]])
    p = p @ R.T
    n, ar, c = face_data(p, f)
    up = (n[:, 2] > 0.95) & (c[:, 2] < np.percentile(c[:, 2], 20))
    floor = np.median(c[up, 2])
    p[:, 2] -= floor
    return p, yaw_deg, floor


def slice_segments(p, f, h):
    """Triangle/plane z=h intersection segments, (N,2,2)."""
    z = p[f, 2] - h                                      # (F,3)
    s = np.sign(z)
    m = (s.min(1) < 0) & (s.max(1) > 0)
    tri, zz = p[f[m]], z[m]
    segs = []
    for i, j in ((0, 1), (1, 2), (2, 0)):
        cross = np.sign(zz[:, i]) != np.sign(zz[:, j])
        t = zz[:, i] / (zz[:, i] - zz[:, j] + 1e-12)
        pt = tri[:, i, :2] + (tri[:, j, :2] - tri[:, i, :2]) * t[:, None]
        segs.append(np.where(cross[:, None], pt, np.nan))
    segs = np.stack(segs, 1)                             # (M,3,2) two of three valid
    out = []
    for row in segs:
        ok = row[~np.isnan(row[:, 0])]
        if len(ok) >= 2:
            out.append(ok[:2])
    return np.array(out)


if __name__ == "__main__":
    v, f = load_raw()
    p, yaw, floor = align(v, f)
    print(f"yaw {yaw:.3f} deg, floor offset {floor:.3f}")
    print("bounds", p.min(0).round(3), p.max(0).round(3))
