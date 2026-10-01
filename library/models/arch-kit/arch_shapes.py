"""Architecture kit, plain-python part: 2D shapes in reference pixels (u right, v down), no bpy.

Used by a traced facade spec (experiments/aztechno-building/scripts/facade.py) and by arch_kit.py.
    import sys; sys.path.insert(0, "<repo>/library/models/arch-kit")
    from arch_shapes import rect, cham, rrect, circle, area, offset, simple_polygon
"""
import math


def rect(u0, v0, u1, v1):
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


def cham(u0, v0, u1, v1, c, corners="tl tr br bl"):
    """Rectangle with 45-degree chamfers of c px on the named corners."""
    pts = []
    for name, (u, v), a, b in (("tl", (u0, v0), (0, c), (c, 0)), ("tr", (u1, v0), (-c, 0), (0, c)),
                               ("br", (u1, v1), (0, -c), (-c, 0)), ("bl", (u0, v1), (c, 0), (0, -c))):
        if name in corners.split():
            pts += [(u + a[0], v + a[1]), (u + b[0], v + b[1])]
        else:
            pts.append((u, v))
    return pts


def rrect(u0, v0, u1, v1, r, corners="tl tr br bl", n=8):
    """Rectangle with round corners of r px on the named corners."""
    pts = []
    spec = (("tl", u0 + r, v0 + r, 180), ("tr", u1 - r, v0 + r, 270), ("br", u1 - r, v1 - r, 0), ("bl", u0 + r, v1 - r, 90))
    for name, cu, cv, a0 in spec:
        corner = {"tl": (u0, v0), "tr": (u1, v0), "br": (u1, v1), "bl": (u0, v1)}[name]
        if name in corners.split():
            for i in range(n + 1):
                a = math.radians(a0 + 90 * i / n)
                pts.append((cu + r * math.cos(a), cv + r * math.sin(a)))
        else:
            pts.append(corner)
    return pts


def circle(cu, cv, r, n=40):
    return [(cu + r * math.cos(2 * math.pi * i / n), cv + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def area(pts):
    return 0.5 * sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts)))


def offset(pts, k):
    """Miter offset of a simple polygon by k px (positive grows it), whatever its winding. Orthogonal and
    45-degree shapes only need k below half the shortest edge."""
    if k == 0:
        return list(pts)
    out = _offset(pts, k, 1)
    if (abs(area(out)) > abs(area(pts))) != (k > 0):     # went the wrong way for this winding
        out = _offset(pts, k, -1)
    return out


def _offset(pts, k, s):
    out, n = [], len(pts)
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]

        def nrm(a, b):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1.0
            return (-dy / L * s, dx / L * s)
        n0, n1 = nrm(p0, p1), nrm(p1, p2)
        bx, by = n0[0] + n1[0], n0[1] + n1[1]
        bl = math.hypot(bx, by)
        if bl < 1e-6:
            out.append((p1[0] + n0[0] * k, p1[1] + n0[1] * k))
            continue
        bx, by = bx / bl, by / bl
        cosh = bx * n0[0] + by * n0[1]
        m = k / max(cosh, 0.3)
        out.append((p1[0] - bx * m, p1[1] - by * m))
    return out


def simple_polygon(pts):
    """True if no two non-adjacent edges cross (a crossing polygon fills as triangles)."""
    n = len(pts)

    def cross(a, b, c, d):
        def o(p, q, r):
            return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
        return o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            if cross(pts[i], pts[(i + 1) % n], pts[j], pts[(j + 1) % n]):
                return False
    return True
