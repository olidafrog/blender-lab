"""Fit a Blender camera to a photo from 2D-3D landmarks (numpy, Levenberg-Marquardt).

  <blender python> fit_cam.py ../assets/cams/2.json
JSON: {"size": [2048,1536], "equiv_mm": 14, "init": {"loc": [x,y,z], "rot_deg": [rx,ry,rz]},
       "points": {"name": [[X,Y,Z], [u,v]]},
       "lines":  {"name": [[[X,Y,Z],[X,Y,Z]], [[u,v], ...]]}}      # pixels on the image of a 3D line
Scene frame: the aligned scan (metres, z up, floor 0). Camera: Blender convention (looks -Z, up +Y),
rotation_euler XYZ in degrees. Focal length is fitted within +-8% of the EXIF 35mm-equivalent
(diagonal equivalence: a 4:3 frame is 34.62 mm wide). Writes "fit" back into the JSON.
"""
import json
import sys

import numpy as np

SENSOR_W = 34.62


def rot(rx, ry, rz):
    a, b, c = np.radians([rx, ry, rz])
    Rx = np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])
    Ry = np.array([[np.cos(b), 0, np.sin(b)], [0, 1, 0], [-np.sin(b), 0, np.cos(b)]])
    Rz = np.array([[np.cos(c), -np.sin(c), 0], [np.sin(c), np.cos(c), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def project(params, P, W, H):
    loc, ang, lens = params[:3], params[3:6], params[6]
    k1 = params[7] if len(params) > 7 else 0.0
    q = (np.asarray(P) - loc) @ rot(*ang)          # rows: R^T (P - C)
    f = lens / SENSOR_W * W
    z = -q[:, 2]
    x, y = f * q[:, 0] / z, -f * q[:, 1] / z
    s = 1 + k1 * (x * x + y * y) / (f * f)         # radial distortion, as cam_util.undistort inverts
    return np.stack([W / 2 + x * s, H / 2 + y * s], 1), z


def residuals(params, d, W, H, lens0):
    r = []
    if d["points"]:
        P = np.array([v[0] for v in d["points"].values()])
        uv = np.array([v[1] for v in d["points"].values()])
        pr, z = project(params, P, W, H)
        r.append(((pr - uv) * (z[:, None] > 0) + (z[:, None] <= 0) * 1e4).ravel())
    for (A, B), pix in d.get("lines", {}).values():
        ab, z = project(params, np.array([A, B]), W, H)
        t = ab[1] - ab[0]
        nrm = np.array([-t[1], t[0]]) / (np.linalg.norm(t) + 1e-9)
        r.append((np.array(pix) - ab[0]) @ nrm)
    r.append(np.array([(params[6] - lens0) / lens0 * 200]))   # weak prior on focal length
    return np.concatenate(r)


def lm(params, d, W, H, lens0, iters=200):
    lam = 1e-2
    res = residuals(params, d, W, H, lens0)
    for _ in range(iters):
        J = np.zeros((len(res), len(params)))
        for k in range(len(params)):
            e = np.zeros(len(params)); e[k] = 1e-5 if (k < 3 or k == 7) else 1e-4
            J[:, k] = (residuals(params + e, d, W, H, lens0) - res) / e[k]
        g = J.T @ res
        A = J.T @ J
        step = np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-9), -g)
        new = params + step
        nres = residuals(new, d, W, H, lens0)
        if (nres ** 2).sum() < (res ** 2).sum():
            params, res, lam = new, nres, lam * 0.3
            if np.abs(step).max() < 1e-7:
                break
        else:
            lam *= 10
    return params, res


def main(path):
    d = json.load(open(path))
    W, H = d["size"]
    lens0 = d["equiv_mm"]
    p0 = np.array(d["init"]["loc"] + d["init"]["rot_deg"] + [lens0] + ([0.0] if d.get("fit_k1") else []), dtype=float)
    best = None
    rng = np.random.default_rng(1)
    for trial in range(12):
        start = p0 + (0 if trial == 0 else np.concatenate([rng.normal(0, 0.4, 3), rng.normal(0, 6, 3), [0] * (len(p0) - 6)]))
        p, res = lm(start, d, W, H, lens0)
        cost = (res ** 2).sum()
        if best is None or cost < best[0]:
            best = (cost, p, res)
    cost, p, res = best
    n = len(d["points"])
    pt_res = res[:2 * n].reshape(-1, 2) if n else np.zeros((0, 2))
    print(f"k1 {p[7] if len(p) > 7 else 0:.4f}  loc {p[:3].round(3)}  rot {p[3:6].round(2)}  lens {p[6]:.2f} mm  rms(points) {np.sqrt((pt_res**2).mean()) if n else 0:.1f} px")
    for name, e in zip(d["points"], pt_res):
        print(f"  {name:16s} {np.hypot(*e):6.1f} px")
    d["fit"] = {"loc": p[:3].round(4).tolist(), "rot_deg": p[3:6].round(3).tolist(), "lens": round(float(p[6]), 3),
                "sensor_w": SENSOR_W, "k1": round(float(p[7]), 4) if len(p) > 7 else 0.0, "rms_px": round(float(np.sqrt((pt_res ** 2).mean())) if n else 0, 2)}
    json.dump(d, open(path, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
