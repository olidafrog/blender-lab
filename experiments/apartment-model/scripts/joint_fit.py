"""Joint fit: model dimensions (P) and camera poses against all reference photos at once.

  tools/blender.sh experiments/apartment-model/scripts/joint_fit.py -- [--stage cams|model|all] [--sweeps 3]

Residual: for each photo, the model's edges (Workbench object-colour render, furniture edges masked) are
scored by their truncated distance to edges in the photo (an L1 distance transform). Coordinate search,
with a soft prior that keeps each P value near its scan-measured start (sigma per value).
Writes assets/joint_fit.json: the solved P values and cameras ("joint" key in each cams/<n>.json).
"""
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build as B  # noqa: E402
from cam_util import undistort  # noqa: E402

EXP = HERE.parent
RW, RH = 768, 576
VIEWS = ["1", "2", "3", "5", "6", "7", "8"]
TRUNC = 12.0
LAM = 0.02

# (key, index or None, step, sigma) — the start value is the current P
PARAMS = [
    ("cove_z", None, 0.04, 0.10), ("cove_in", 0, 0.02, 0.04), ("cove_in", 1, 0.02, 0.04),
    ("pilaster_proud", 0, 0.03, 0.05), ("pilaster_proud", 1, 0.03, 0.05), ("pilaster_x", 0, 0.04, 0.06),
    ("col_w", None, 0.02, 0.04), ("col_y", None, 0.03, 0.05),
    ("beam_z", None, 0.02, 0.03), ("beam_w", None, 0.03, 0.05),
    ("girder_x0", None, 0.03, 0.05), ("girder_z", None, 0.02, 0.03),
    ("win_w", None, 0.03, 0.06), ("win_w_frame", None, 0.03, 0.05), ("win_spring", None, 0.03, 0.05),
    ("win_rise", None, 0.03, 0.05), ("pier_top", None, 0.03, 0.05), ("pier_proud", None, 0.02, 0.04),
    ("mezz_x", None, 0.02, 0.03), ("soffit_z", None, 0.02, 0.02),
    ("radiator", 3, 0.04, 0.10),
]


def dist_l1(edges):
    """Exact L1 distance to the nearest True pixel (separable 1D passes)."""
    INF = 1e6
    d = np.where(edges, 0.0, INF)
    for axis in (1, 0):
        a = np.moveaxis(d, axis, -1).copy()
        n = a.shape[-1]
        idx = np.arange(n, dtype=np.float64)
        fwd = np.minimum.accumulate(a - idx, axis=-1) + idx
        bwd = (np.minimum.accumulate((a + idx)[..., ::-1], axis=-1))[..., ::-1] - idx
        a = np.minimum(fwd, bwd)
        d = np.moveaxis(a, -1, axis)
    return d


PHOTO = {}


def photo_dist(n, k1=0.0, lens=14.0):
    if n not in PHOTO:
        img = bpy.data.images.load(str(EXP / f"references/{n}.jpeg"))
        img.scale(RW * 2, RH * 2)
        PHOTO[n] = np.array(img.pixels[:], dtype=np.float32).reshape(RH * 2, RW * 2, 4)[::-1, :, :3] @ np.array([0.2126, 0.7152, 0.0722])
        bpy.data.images.remove(img)
    lum = undistort(PHOTO[n], k1, lens, 34.62, RW, RH)
    gx = np.zeros_like(lum); gy = np.zeros_like(lum)
    gx[:, 1:-1] = lum[:, 2:] - lum[:, :-2]
    gy[1:-1] = lum[2:] - lum[:-2]
    g = np.hypot(gx, gy)
    e = g > np.percentile(g, 88)
    return np.minimum(dist_l1(e), TRUNC)


def colour_objects(scene):
    rng = np.random.default_rng(7)
    furn = set(o.name for o in bpy.data.collections["Furniture"].objects) if "Furniture" in bpy.data.collections else set()
    for o in scene.objects:
        if o.type != "MESH":
            continue
        if o.name in furn:
            o.color = (0, 0, 0, 1)
        else:
            c = rng.uniform(0.15, 1.0, 3)
            o.color = (*c, 1)
        if o.users_collection and o.users_collection[0].name == "Outside":
            o.hide_render = True
    for o in scene.objects:
        if o.type == "LIGHT":
            o.hide_render = True


def setup_render(scene):
    scene.render.engine = "BLENDER_WORKBENCH"
    sh = scene.display.shading
    sh.light, sh.color_type = "FLAT", "OBJECT"
    scene.view_settings.view_transform = "Standard"
    scene.render.resolution_x, scene.render.resolution_y = RW, RH
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.filepath = str(EXP / "assets/cache/_joint.png")


def model_edges(scene):
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(scene.render.filepath, check_existing=False)
    a = np.array(img.pixels[:], dtype=np.float32).reshape(RH, RW, 4)[::-1]
    bpy.data.images.remove(img)
    rgb = a[..., :3]
    furn = (rgb.sum(-1) < 0.02) & (a[..., 3] > 0.5)
    e = np.zeros((RH, RW), bool)
    dx = np.abs(rgb[:, 1:] - rgb[:, :-1]).sum(-1) > 0.02
    dy = np.abs(rgb[1:] - rgb[:-1]).sum(-1) > 0.02
    e[:, 1:] |= dx; e[1:] |= dy
    near_furn = furn.copy()
    near_furn[:, 1:] |= furn[:, :-1]; near_furn[:, :-1] |= furn[:, 1:]
    near_furn[1:] |= furn[:-1]; near_furn[:-1] |= furn[1:]
    return e & ~near_furn


def cam_params(ob):
    return [*ob.location, *(math.degrees(r) for r in ob.rotation_euler), ob.data.lens]


USE_K1 = False
CAMS_ONLY = None


def set_cam(ob, p):
    ob.location = p[:3]
    ob.rotation_euler = [math.radians(v) for v in p[3:6]]
    ob.data.lens = p[6]


class Fit:
    def __init__(self):
        self.D = {}
        self.k1 = {n: 0.0 for n in VIEWS}
        self.P0 = {k: (list(v) if isinstance(v, (list, tuple)) else v) for k, v in B.P.items()}
        self.campose = {}
        self.rebuild()

    def rebuild(self):
        self.scene, self.cams = B.build_scene()
        colour_objects(self.scene)
        setup_render(self.scene)
        for n, p in self.campose.items():
            set_cam(self.cams[n], p[:7])

    def dist(self, n):
        key = (n, round(self.k1[n], 4), round(self.cams[n].data.lens, 2))
        if key not in self.D:
            self.D[key] = photo_dist(n, self.k1[n], self.cams[n].data.lens)
        return self.D[key]

    def view_cost(self, n):
        self.scene.camera = self.cams[n]
        e = model_edges(self.scene)
        if e.sum() < 50:
            return TRUNC
        return float(self.dist(n)[e].mean())

    def total(self):
        return float(np.mean([self.view_cost(n) for n in VIEWS]))

    def prior(self):
        s = 0.0
        for key, idx, _, sig in PARAMS:
            v, v0 = getv(key, idx), getv0(self.P0, key, idx)
            s += ((v - v0) / sig) ** 2
        return LAM * s


def getv(key, idx):
    v = B.P[key]
    return v if idx is None else v[idx]


def getv0(P0, key, idx):
    v = P0[key]
    return v if idx is None else v[idx]


def setv(key, idx, val):
    if idx is None:
        B.P[key] = val
    else:
        v = list(B.P[key]); v[idx] = val; B.P[key] = tuple(v)


def fit_cameras(F, sweeps):
    steps0 = np.array([0.03, 0.03, 0.02, 0.3, 0.3, 0.3, 0.15, 0.02])
    for n in (CAMS_ONLY or VIEWS):
        ob = F.cams[n]
        p = np.array(cam_params(ob) + [F.k1[n]]); steps = steps0.copy()
        F.scene.camera = ob
        best = F.view_cost(n); start = best
        for _ in range(sweeps):
            improved = False
            for k in range(8 if USE_K1 else 7):
                for sgn in (1, -1):
                    q = p.copy(); q[k] += sgn * steps[k]
                    set_cam(ob, q); F.k1[n] = q[7]
                    c = F.view_cost(n)
                    if c < best - 1e-4:
                        best, p, improved = c, q, True
                        break
                set_cam(ob, p); F.k1[n] = p[7]
            if not improved:
                steps *= 0.5
        F.campose[n] = p.tolist()
        print(f"[out] cam {n}: {start:.3f} -> {best:.3f} px  loc {np.round(p[:3], 3)} rot {np.round(p[3:6], 2)} lens {p[6]:.2f} k1 {p[7]:.3f}", flush=True)


def fit_model(F, sweeps):
    best = F.total() + F.prior()
    print(f"[out] model start cost {best:.4f}", flush=True)
    steps = {(k, i): s for k, i, s, _ in PARAMS}
    for sw in range(sweeps):
        for key, idx, _, _ in PARAMS:
            v0 = getv(key, idx)
            for sgn in (1, -1):
                setv(key, idx, round(v0 + sgn * steps[(key, idx)], 4))
                F.rebuild()
                c = F.total() + F.prior()
                if c < best - 1e-4:
                    best = c
                    print(f"[out]   sweep {sw} {key}[{idx}] {v0} -> {getv(key, idx)}  cost {best:.4f}", flush=True)
                    break
                setv(key, idx, v0)
            else:
                steps[(key, idx)] *= 0.5
        F.rebuild()
    print(f"[out] model end cost {best:.4f}", flush=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    stage = argv[argv.index("--stage") + 1] if "--stage" in argv else "all"
    sweeps = int(argv[argv.index("--sweeps") + 1]) if "--sweeps" in argv else 3
    global USE_K1, CAMS_ONLY
    USE_K1 = "--k1" in argv
    if "--only" in argv:
        CAMS_ONLY = argv[argv.index("--only") + 1].split(",")
    F = Fit()
    for n in VIEWS:                               # start from the cameras already solved
        d = json.load(open(EXP / f"assets/cams/{n}.json"))
        if "joint" in d:
            F.campose[n] = d["joint"]["loc"] + d["joint"]["rot_deg"] + [d["joint"]["lens"]]
            F.k1[n] = d["joint"].get("k1", 0.0)
    F.rebuild()
    print(f"[out] start: mean edge distance {F.total():.3f} px per view", flush=True)
    if stage in ("cams", "all"):
        fit_cameras(F, sweeps)
    if stage in ("model", "all"):
        fit_model(F, sweeps)
        fit_cameras(F, 2)
    print(f"[out] final mean edge distance {F.total():.3f} px per view", flush=True)
    out = {"P": {k: getv(k, i) if i is None else list(B.P[k]) for k, i, _, _ in PARAMS}, "cams": F.campose}
    out["P"]["cove_z"], out["P"]["cove_in"] = B.P["cove_z"], list(B.P["cove_in"])
    (EXP / "assets/joint_fit.json").write_text(json.dumps(out, indent=1))
    for n, p in F.campose.items():
        path = EXP / f"assets/cams/{n}.json"
        d = json.load(open(path))
        d["joint"] = {"loc": [round(v, 4) for v in p[:3]], "rot_deg": [round(v, 3) for v in p[3:6]],
                      "lens": round(p[6], 3), "sensor_w": 34.62, "k1": round(F.k1[n], 4)}
        json.dump(d, open(path, "w"), indent=1)
    print("[out] wrote assets/joint_fit.json")


main()
