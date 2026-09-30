"""Fit a camera to a reference image from landmark pairs (plain python3, no numpy).

  python3 tools/fit_camera.py <landmarks.json> [--size 736x552] [--target-z 8] [--trials 30]

landmarks.json: {"name": [[x_mm, y_mm, z_mm], [u_px, v_px]], ...}. 3D points in scene millimetres (+z up),
pixels measured from the top-left of the reference at --size. Read them off a gridded 2x copy of the
reference; 8-12 points spread over the subject and over different heights are enough.

Model: a camera orbiting a target point (tx, ty, target-z) at azimuth phi (degrees; 0 looks along +y),
elevation, distance (mm), with a 36 mm sensor and focal length `lens` (capped 25-200 mm). Nelder-Mead from
random starts. Prints the parameters, the rms error in px, and the residual per landmark. In the build:
target = (tx, ty, target_z) mm; location = target - f * dist*cos(elev) + z * dist*sin(elev), with
f = (sin phi, cos phi, 0); track -Z to the target, Y up; lens = lens, sensor_width = 36.
From cyber-model (azimuth 41.0, elevation 48.65, lens 200, rms 6 px); reused by cyber-deck-v2.
"""
import json
import math
import random
import sys


def project(p, phi, elev, dist, tx, ty, lens, W, H, tz):
    phi, elev = math.radians(phi), math.radians(elev)
    f = (math.sin(phi), math.cos(phi), 0.0)
    T = (tx, ty, tz)
    C = (T[0] - f[0] * dist * math.cos(elev), T[1] - f[1] * dist * math.cos(elev), T[2] + dist * math.sin(elev))
    w = [T[i] - C[i] for i in range(3)]
    n = math.sqrt(sum(v * v for v in w))
    w = [v / n for v in w]
    r = (w[1], -w[0], 0.0)                                     # w x up
    rn = math.hypot(r[0], r[1])
    r = (r[0] / rn, r[1] / rn, 0.0)
    u = (r[1] * w[2] - r[2] * w[1], r[2] * w[0] - r[0] * w[2], r[0] * w[1] - r[1] * w[0])
    d = [p[i] - C[i] for i in range(3)]
    x = sum(d[i] * r[i] for i in range(3))
    y = sum(d[i] * u[i] for i in range(3))
    z = sum(d[i] * w[i] for i in range(3))
    fpx = lens / 36.0 * W
    return W / 2 + x / z * fpx, H / 2 - y / z * fpx


def nelder_mead(f, x0, step, iters=4000):
    n = len(x0)
    pts = [list(x0)] + [[x0[j] + (step[j] if j == i else 0) for j in range(n)] for i in range(n)]
    vals = [f(p) for p in pts]
    for _ in range(iters):
        order = sorted(range(n + 1), key=lambda i: vals[i])
        pts = [pts[i] for i in order]
        vals = [vals[i] for i in order]
        c = [sum(p[j] for p in pts[:-1]) / n for j in range(n)]
        xr = [c[j] + (c[j] - pts[-1][j]) for j in range(n)]
        fr = f(xr)
        if fr < vals[0]:
            xe = [c[j] + 2 * (c[j] - pts[-1][j]) for j in range(n)]
            fe = f(xe)
            pts[-1], vals[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < vals[-2]:
            pts[-1], vals[-1] = xr, fr
        else:
            xc = [c[j] + 0.5 * (pts[-1][j] - c[j]) for j in range(n)]
            fc = f(xc)
            if fc < vals[-1]:
                pts[-1], vals[-1] = xc, fc
            else:
                for i in range(1, n + 1):
                    pts[i] = [pts[0][j] + 0.5 * (pts[i][j] - pts[0][j]) for j in range(n)]
                    vals[i] = f(pts[i])
    i = min(range(n + 1), key=lambda i: vals[i])
    return pts[i], vals[i]


def fit(lm, W, H, tz=8.0, trials=30, seed=3):
    def err(q):
        phi, elev, dist, tx, ty, lens = q
        if not (5 < elev < 85 and dist > 100 and 25 < lens < 200):
            return 1e9
        return sum((a - u) ** 2 + (b - v) ** 2 for p, (u, v) in lm.values()
                   for a, b in [project(p, phi, elev, dist, tx, ty, lens, W, H, tz)])
    random.seed(seed)
    best = None
    for _ in range(trials):
        x0 = [random.uniform(30, 55), random.uniform(35, 65), random.uniform(350, 900), random.uniform(-10, 60),
              random.uniform(-30, 30), random.uniform(50, 130)]
        q, v = nelder_mead(err, x0, [4, 4, 60, 8, 8, 10])
        if best is None or v < best[1]:
            best = (q, v)
    return best


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0].startswith("--"):
        sys.exit(__doc__)
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    W, H = (float(v) for v in opt("--size", "736x552").split("x"))
    tz, trials = float(opt("--target-z", 8.0)), int(opt("--trials", 30))
    lm = {k: (tuple(v[0]), tuple(v[1])) for k, v in json.load(open(a[0])).items()}
    q, v = fit(lm, W, H, tz, trials)
    print("phi elev dist(mm) tx ty(mm) lens:", [round(x, 2) for x in q], " rms px:", round(math.sqrt(v / len(lm)), 2))
    for k, (p, (u, v_)) in lm.items():
        x, y = project(p, *q, W, H, tz)
        print(f"  {k:9s} ref ({u},{v_})  model ({x:.0f},{y:.0f})  d=({x-u:+.0f},{y-v_:+.0f})")
