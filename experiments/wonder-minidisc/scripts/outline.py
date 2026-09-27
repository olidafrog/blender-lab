"""Logomark outlines as 2D polygons, and rounded offsets of them.

Pure numpy, so it runs in Blender and in system Python. Units are SVG units
(the logomark spans 124 x 128), y up, origin at the SVG centre (64, 64).

    parts = logomark_parts()                 # [N x 2 arrays], one per logo piece
    rings = offset(parts, +6.0)              # rounded outward offset of their union
    rings = offset(parts, +12.0, close=5.0)  # offset, then round concave corners by 5
"""
import re
from pathlib import Path

import numpy as np

SVG = Path(__file__).resolve().parents[3] / "library/models/wonder-logos/logomark/logomark-Light.svg"
CENTRE = np.array([64.0, 64.0])


def _bezier(p0, p1, p2, p3, n):
    t = np.linspace(0, 1, n, endpoint=False)[:, None]
    return ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3


def logomark_parts(step=1.0):
    """Each <path> as a closed polygon, sampled about every `step` units along curves."""
    parts = []
    for d in re.findall(r'<path d="([^"]+)"', SVG.read_text()):
        toks = re.findall(r"[MCHVZ]|-?\d*\.?\d+(?:e-?\d+)?", d)
        pts, cur, i, cmd = [], np.zeros(2), 0, None
        while i < len(toks):
            if toks[i] in "MCHVZ":
                cmd = toks[i]; i += 1
                if cmd == "Z":
                    continue
            if cmd == "M":
                cur = np.array([float(toks[i]), float(toks[i + 1])]); i += 2
                pts.append(cur[None])
            elif cmd == "C":
                c = np.array([float(t) for t in toks[i:i + 6]]).reshape(3, 2); i += 6
                n = max(4, int(np.linalg.norm(c[2] - cur) / step) + 1)
                pts.append(_bezier(cur, c[0], c[1], c[2], n)[1:])
                pts.append(c[2][None]); cur = c[2]
            elif cmd in "HV":
                v = float(toks[i]); i += 1
                nxt = np.array([v, cur[1]]) if cmd == "H" else np.array([cur[0], v])
                n = max(1, int(np.linalg.norm(nxt - cur) / step))
                pts.append(cur + (nxt - cur) * np.linspace(0, 1, n + 1)[1:, None]); cur = nxt
        p = np.concatenate(pts)
        keep = np.r_[True, np.linalg.norm(np.diff(p, axis=0), axis=1) > 1e-6]
        p = p[keep]
        if np.linalg.norm(p[0] - p[-1]) < 1e-6:
            p = p[:-1]
        p = (p - CENTRE) * np.array([1, -1])  # y up, centred
        if _area(p) < 0:
            p = p[::-1]  # counter-clockwise
        parts.append(p)
    return parts


def _area(p):
    x, y = p[:, 0], p[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)


def signed_distance(rings, xs, ys):
    """Signed distance (negative inside) from grid points to the union of polygons."""
    X, Y = np.meshgrid(xs, ys)
    P = np.stack([X.ravel(), Y.ravel()], 1)
    d = np.full(len(P), np.inf)
    inside = np.zeros(len(P), bool)
    for r in rings:
        a, b = r, np.roll(r, -1, 0)
        for s in range(0, len(a), 64):  # chunk segments to bound memory
            A, B = a[s:s + 64], b[s:s + 64]
            AB = B - A
            AP = P[:, None, :] - A[None]
            t = np.clip((AP * AB).sum(-1) / (AB * AB).sum(-1), 0, 1)
            q = AP - t[..., None] * AB
            d = np.minimum(d, np.sqrt((q * q).sum(-1)).min(1))
            # even-odd crossing test for inside
            y0, y1 = A[:, 1][None], B[:, 1][None]
            cond = (y0 > P[:, 1:2]) != (y1 > P[:, 1:2])
            xc = A[:, 0][None] + (P[:, 1:2] - y0) * (B[:, 0] - A[:, 0])[None] / np.where(y1 - y0 == 0, 1e-12, y1 - y0)
            inside ^= (cond & (P[:, 0:1] < xc)).sum(1) % 2 == 1
    return np.where(inside, -d, d).reshape(X.shape)


def contours(F, xs, ys, level=0.0):
    """Marching squares: closed polylines where the grid F crosses `level`."""
    G = F - level
    h, w = G.shape
    segs = {}
    # edge id -> interpolated point. Edges: ('h', j, i) between (j,i)-(j,i+1); ('v', j, i) between (j,i)-(j+1,i)
    def pt(e):
        k, j, i = e
        if k == "h":
            a, b = G[j, i], G[j, i + 1]; t = a / (a - b)
            return np.array([xs[i] + t * (xs[i + 1] - xs[i]), ys[j]])
        a, b = G[j, i], G[j + 1, i]; t = a / (a - b)
        return np.array([xs[i], ys[j] + t * (ys[j + 1] - ys[j])])
    links = {}
    inside = G < 0
    for j in range(h - 1):
        row = inside[j:j + 2]
        cols = np.nonzero((row[0, :-1] != row[0, 1:]) | (row[1, :-1] != row[1, 1:]) | (row[0, :-1] != row[1, :-1]))[0]
        for i in cols:
            c = inside[j, i] * 1 | inside[j, i + 1] * 2 | inside[j + 1, i + 1] * 4 | inside[j + 1, i] * 8
            B, R, T, L = ("h", j, i), ("v", j, i + 1), ("h", j + 1, i), ("v", j, i)
            table = {1: [(L, B)], 2: [(B, R)], 3: [(L, R)], 4: [(R, T)], 5: [(L, T), (R, B)], 6: [(B, T)],
                     7: [(L, T)], 8: [(T, L)], 9: [(T, B)], 10: [(T, R), (B, L)], 11: [(T, R)], 12: [(R, L)],
                     13: [(R, B)], 14: [(B, L)]}
            for a, b in table.get(c, []):
                links[a] = b
    rings = []
    while links:
        start, nxt = links.popitem()
        ring = [start]
        cur = nxt
        while cur != start and cur in links:
            ring.append(cur)
            cur = links.pop(cur)
        if len(ring) > 8:
            p = np.array([pt(e) for e in ring])
            if _area(p) < 0:
                p = p[::-1]
            rings.append(p)
    return rings


def resample(p, step):
    """Even spacing along a closed polyline, with light smoothing to remove grid wobble."""
    for _ in range(2):
        p = 0.25 * np.roll(p, 1, 0) + 0.5 * p + 0.25 * np.roll(p, -1, 0)
    seg = np.linalg.norm(np.roll(p, -1, 0) - p, axis=1)
    s = np.r_[0, np.cumsum(seg)]
    n = max(16, int(s[-1] / step))
    t = np.linspace(0, s[-1], n, endpoint=False)
    q = np.concatenate([p, p[:1]])
    return np.stack([np.interp(t, s, q[:, 0]), np.interp(t, s, q[:, 1])], 1)


def offset(rings, r, close=0.0, res=0.5, step=0.5):
    """Rounded offset of the union of `rings` by r (negative shrinks).
    `close` > 0 then rounds concave corners: offset by r + close, back by -close."""
    pad = abs(r) + close + 4
    lo = np.min([p.min(0) for p in rings], 0) - pad
    hi = np.max([p.max(0) for p in rings], 0) + pad
    xs, ys = np.arange(lo[0], hi[0], res), np.arange(lo[1], hi[1], res)
    F = signed_distance(rings, xs, ys)
    out = contours(F, xs, ys, r + close)
    if close > 0:
        out = [resample(p, step) for p in out]
        F = signed_distance(out, xs, ys)
        out = contours(F, xs, ys, -close)
    return [resample(p, step) for p in out]


if __name__ == "__main__":
    import sys
    from PIL import Image, ImageDraw
    parts = logomark_parts()
    print("parts", [len(p) for p in parts])
    S, o = 4, 120
    im = Image.new("RGB", (int(260 * S / 1.3), int(260 * S / 1.3)), "white")
    dr = ImageDraw.Draw(im)
    def poly(p, col, w=1):
        q = [(float(x) * S + o * S / 1.5 + 20, float(-y) * S + o * S / 1.5 + 20) for x, y in p]
        dr.line(q + q[:1], fill=col, width=w)
    for p in parts:
        poly(p, "black", 2)
    for rr, cl, col in ((2, 0, "blue"), (14, 6, "red"), (11.5, 6, "orange")):
        for p in offset(parts, rr, cl):
            poly(p, col)
    im.save(sys.argv[1] if len(sys.argv) > 1 else "outline_test.png")
