"""Fit the hero camera to the reference from landmark pairs (pure Python, no numpy).
   python3 scripts/fit_camera.py
Landmarks: 3D points in device mm (built by build.py) and their pixel positions in the 736x552 reference."""
import math, random

S_PX, ORG = 3.6, (500.0, 480.0)
pp = lambda x, y: ((x - ORG[0]) / S_PX, -(y - ORG[1]) / S_PX)

LM = {  # name: (plan px x, y, z mm) -> ref pixel
    "lcd":     ((473.5, 265.0, 13.7), (325, 204)),
    "led":     ((413, 358, 12.4), (334, 271)),
    "dial":    ((277, 310, 15.5), (226, 305)),
    "knob":    ((377, 368, 17.0), (320, 290)),
    "button":  ((660, 350, 12.8), (472, 172)),
    "latch":   ((662, 492, 14.0), (550, 242)),
    "screw1":  ((480, 474, 14.9), (431, 296)),
    "screw2":  ((535, 601, 14.9), (527, 330)),
    "screw3":  ((657, 594, 10.9), (596, 284)),
    "lockdial": ((335, 770, 14.3), (495, 482)),
    "boss":    ((278, 460, 13.6), (310, 368)),
    "plug":    ((708, 640, 12.6), (650, 275)),
}
W, H = 736.0, 552.0


def project(p, phi, elev, dist, tx, ty, lens):
    phi, elev = math.radians(phi), math.radians(elev)
    f = (math.sin(phi), math.cos(phi), 0.0)
    T = (tx, ty, 8.0)
    C = (T[0] - f[0] * dist * math.cos(elev), T[1] - f[1] * dist * math.cos(elev), T[2] + dist * math.sin(elev))
    w = [T[i] - C[i] for i in range(3)]
    n = math.sqrt(sum(v * v for v in w)); w = [v / n for v in w]
    r = (w[1] * 1 - w[2] * 0, w[2] * 0 - w[0] * 1, 0.0)   # w x up(0,0,1)
    rn = math.hypot(r[0], r[1]); r = (r[0] / rn, r[1] / rn, 0.0)
    u = (r[1] * w[2] - r[2] * w[1], r[2] * w[0] - r[0] * w[2], r[0] * w[1] - r[1] * w[0])
    d = [p[i] - C[i] for i in range(3)]
    x = sum(d[i] * r[i] for i in range(3)); y = sum(d[i] * u[i] for i in range(3)); z = sum(d[i] * w[i] for i in range(3))
    fpx = lens / 36.0 * W
    return W / 2 + x / z * fpx, H / 2 - y / z * fpx


def err(params):
    phi, elev, dist, tx, ty, lens = params
    if not (5 < elev < 85 and dist > 100 and 25 < lens < 200):
        return 1e9
    e = 0.0
    for (px, py, z), (u, v) in LM.values():
        x, y = pp(px, py)
        a, b = project((x, y, z), phi, elev, dist, tx, ty, lens)
        e += (a - u) ** 2 + (b - v) ** 2
    return e


def nelder_mead(f, x0, step, iters=4000):
    n = len(x0)
    pts = [list(x0)] + [[x0[j] + (step[j] if j == i else 0) for j in range(n)] for i in range(n)]
    vals = [f(p) for p in pts]
    for _ in range(iters):
        order = sorted(range(n + 1), key=lambda i: vals[i]); pts = [pts[i] for i in order]; vals = [vals[i] for i in order]
        c = [sum(p[j] for p in pts[:-1]) / n for j in range(n)]
        xr = [c[j] + (c[j] - pts[-1][j]) for j in range(n)]; fr = f(xr)
        if fr < vals[0]:
            xe = [c[j] + 2 * (c[j] - pts[-1][j]) for j in range(n)]; fe = f(xe)
            pts[-1], vals[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < vals[-2]:
            pts[-1], vals[-1] = xr, fr
        else:
            xc = [c[j] + 0.5 * (pts[-1][j] - c[j]) for j in range(n)]; fc = f(xc)
            if fc < vals[-1]:
                pts[-1], vals[-1] = xc, fc
            else:
                for i in range(1, n + 1):
                    pts[i] = [pts[0][j] + 0.5 * (pts[i][j] - pts[0][j]) for j in range(n)]; vals[i] = f(pts[i])
    i = min(range(n + 1), key=lambda i: vals[i])
    return pts[i], vals[i]


if __name__ == "__main__":
    best = None
    random.seed(3)
    for trial in range(30):
        x0 = [random.uniform(30, 55), random.uniform(35, 65), random.uniform(350, 900), random.uniform(-10, 60), random.uniform(-30, 30), random.uniform(50, 130)]
        p, v = nelder_mead(err, x0, [4, 4, 60, 8, 8, 10])
        if best is None or v < best[1]:
            best = (p, v)
    p, v = best
    print("phi elev dist(mm) tx ty(mm) lens:", [round(x, 2) for x in p], " rms px:", round(math.sqrt(v / len(LM)), 2))
    for k, ((px, py, z), (u, v_)) in LM.items():
        x, y = pp(px, py)
        a, b = project((x, y, z), *p)
        print(f"  {k:9s} ref ({u},{v_})  model ({a:.0f},{b:.0f})  d=({a-u:+.0f},{b-v_:+.0f})")
