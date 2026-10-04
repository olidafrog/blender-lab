"""Refine a fitted camera by matching edges of the textured scan render to the photo (Nelder-Mead).

  tools/blender.sh experiments/apartment-model/scripts/refine_cam.py <n> [--iters 250]
Reads assets/cams/<n>.json ("fit" from fit_cam.py), writes "refined" back, and saves
assets/cams/<n>_overlay.png: the photo in grey with scan edges in red (before: blue).
"""
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "library/models/interior-kit"))  # shell_kit, cam_util, fit_cam
from scan_render import load_scan  # noqa: E402
from cam_util import undistort  # noqa: E402

EXP = Path(__file__).resolve().parents[1]
RW, RH = (768, 576) if "hires" in sys.argv else (512, 384)


def blur(a, r=2):
    k = np.ones(2 * r + 1) / (2 * r + 1)
    a = np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 0, a)
    return np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 1, a)


def edges(lum):
    gx = np.zeros_like(lum); gy = np.zeros_like(lum)
    gx[:, 1:-1] = lum[:, 2:] - lum[:, :-2]
    gy[1:-1] = lum[2:] - lum[:-2]
    e = np.hypot(gx, gy)
    e = e / (np.percentile(e, 99) + 1e-6)
    return blur(np.clip(e, 0, 1), 2)


def load_photo(n):
    img = bpy.data.images.load(str(EXP / f"references/{n}.jpeg"))
    img.scale(RW, RH)
    a = np.array(img.pixels[:], dtype=np.float32).reshape(RH, RW, 4)[::-1]
    return a[..., :3] @ np.array([0.2126, 0.7152, 0.0722]), img


def load_photo_big(n):
    img = bpy.data.images.load(str(EXP / f"references/{n}.jpeg"))
    img.scale(RW * 2, RH * 2)
    a = np.array(img.pixels[:], dtype=np.float32).reshape(RH * 2, RW * 2, 4)[::-1]
    return a[..., :3] @ np.array([0.2126, 0.7152, 0.0722])


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    n = argv[0]
    iters = int(argv[argv.index("--iters") + 1]) if "--iters" in argv else 250
    path = EXP / f"assets/cams/{n}.json"
    d = json.load(open(path))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    load_scan()
    cd = bpy.data.cameras.new("Cam")
    cam = bpy.data.objects.new("Cam", cd)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cd.sensor_fit = "HORIZONTAL"
    cd.sensor_width = 34.62
    cd.clip_start = 0.05
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "FLAT"
    scene.display.shading.color_type = "TEXTURE"
    scene.render.resolution_x, scene.render.resolution_y = RW, RH
    scene.view_settings.view_transform = "Standard"
    out = str(EXP / f"assets/cams/_tmp_{n}.png")
    scene.render.filepath = out
    lum_ref, _ = load_photo(n)
    use_k1 = "k1" in sys.argv
    big = load_photo_big(n) if use_k1 else None
    e_ref = edges(lum_ref)
    mask_ref = e_ref - e_ref.mean()
    ref_cache = {}

    def ref_edges(k1, lens):
        if not use_k1:
            return mask_ref
        key = (round(k1, 4), round(lens, 2))
        if key not in ref_cache:
            e = edges(undistort(big, k1, lens, 34.62, RW, RH))
            ref_cache.clear(); ref_cache[key] = e - e.mean()
        return ref_cache[key]

    def render(p):
        cam.location = p[:3]
        cam.rotation_euler = [math.radians(v) for v in p[3:6]]
        cd.lens = p[6]
        bpy.ops.render.render(write_still=True)
        img = bpy.data.images.load(out, check_existing=False)
        a = np.array(img.pixels[:], dtype=np.float32).reshape(RH, RW, 4)[::-1]
        bpy.data.images.remove(img)
        lum = a[..., :3] @ np.array([0.2126, 0.7152, 0.0722])
        return lum, a[..., 3]

    fixlens = None
    for a in sys.argv:
        if a.startswith("fixlens="):
            fixlens = float(a.split("=")[1])

    def cost(p):
        if fixlens:
            p = p.copy(); p[6] = fixlens
        lum, alpha = render(p)
        e = edges(lum) * (blur(alpha, 3) > 0.99)        # ignore scan holes and their borders
        e = e - e.mean()
        mr = ref_edges(p[7] if len(p) > 7 else 0.0, p[6])
        return -float((e * mr).sum() / (np.linalg.norm(e) * np.linalg.norm(mr) + 1e-9))

    if "fit" not in d:                                   # no landmarks: coarse search from the plan position
        d["fit"] = {"loc": d["init"]["loc"], "rot_deg": d["init"]["rot_deg"], "lens": d["equiv_mm"], "sensor_w": 34.62}
        f = d["fit"]
        base = np.array(f["loc"] + f["rot_deg"] + [f["lens"]], dtype=float)
        best = (1e9, base)
        wide = "wide" in sys.argv
        dxy = (-0.5, 0, 0.5) if wide else (0,)
        lens_mults = (1.0, 1.17, 1.46) if "lens" in sys.argv else (1.0,)
        for lm in lens_mults:
          for drz in range(-36 if wide else -24, 37 if wide else 25, 6):
            for drx in (-8, 0, 8):
                for dz in (-0.2, 0.1):
                    for dx in dxy:
                        for dy in dxy:
                            p = base + np.array([dx, dy, dz, drx, 0, drz, 0])
                            p[6] = base[6] * lm
                            c = cost(p)
                            if c < best[0]:
                                best = (c, p)
        print(f"[out] coarse best {best[1].round(2)} corr {-best[0]:.4f}")
        f["loc"], f["rot_deg"], f["lens"] = best[1][:3].tolist(), best[1][3:6].tolist(), float(best[1][6])
    f = d["refined"] if ("again" in sys.argv and "refined" in d) else d["fit"]
    p0 = np.array(f["loc"] + f["rot_deg"] + [f["lens"]] + ([f.get("k1", 0.0)] if use_k1 else []))
    if fixlens:
        p0[6] = fixlens
    steps = np.array([0.15, 0.15, 0.08, 2.0, 1.5, 3.0, 0.4]) if "coarse" in sys.argv else np.array([0.08, 0.08, 0.05, 1.0, 1.0, 1.0, 0.4])
    if use_k1:
        steps = np.append(steps, 0.05)
    D = len(p0)
    # Nelder-Mead
    idx = [k for k in range(D) if not (fixlens and k == 6)]
    simplex = [p0] + [p0 + np.eye(D)[k] * steps[k] for k in idx]
    vals = [cost(s) for s in simplex]
    c0 = vals[0]
    for it in range(iters):
        order = np.argsort(vals); simplex = [simplex[i] for i in order]; vals = [vals[i] for i in order]
        cen = np.mean(simplex[:-1], 0)
        xr = cen + (cen - simplex[-1]); fr = cost(xr)
        if fr < vals[0]:
            xe = cen + 2 * (cen - simplex[-1]); fe = cost(xe)
            simplex[-1], vals[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < vals[-2]:
            simplex[-1], vals[-1] = xr, fr
        else:
            xc = cen + 0.5 * (simplex[-1] - cen); fc = cost(xc)
            if fc < vals[-1]:
                simplex[-1], vals[-1] = xc, fc
            else:
                simplex = [simplex[0]] + [simplex[0] + 0.5 * (s - simplex[0]) for s in simplex[1:]]
                vals = [vals[0]] + [cost(s) for s in simplex[1:]]
    b = int(np.argmin(vals)); pb = simplex[b]
    print(f"[out] edge corr {-c0:.4f} -> {-vals[b]:.4f}")
    print(f"[out] loc {pb[:3].round(3)} rot {pb[3:6].round(2)} lens {pb[6]:.2f}")
    d["refined"] = {"loc": pb[:3].round(4).tolist(), "rot_deg": pb[3:6].round(3).tolist(), "lens": round(float(pb[6]), 3),
                    "sensor_w": f.get("sensor_w", 34.62), "edge_corr": round(-vals[b], 4),
                    "k1": round(float(pb[7]), 4) if use_k1 else 0.0}
    print(f"[out] k1 {d['refined']['k1']}")
    json.dump(d, open(path, "w"), indent=1)
    # overlay at render size: photo grey, before-edges blue, after-edges red
    lum0, al0 = render(p0); lum1, al1 = render(pb)
    e0 = edges(lum0) * (al0 > 0.5); e1 = edges(lum1) * (al1 > 0.5)
    g = np.clip(lum_ref, 0, 1) ** (1 / 2.2) * 0.7
    rgb = np.stack([g, g, g], -1)
    rgb[..., 2] = np.maximum(rgb[..., 2], np.clip(e0 * 1.5, 0, 1))
    rgb[..., 0] = np.maximum(rgb[..., 0], np.clip(e1 * 1.5, 0, 1))
    o = bpy.data.images.new("ov", RW, RH)
    o.pixels[:] = np.concatenate([rgb, np.ones((RH, RW, 1))], -1)[::-1].ravel()
    o.filepath_raw = str(EXP / f"assets/cams/{n}_overlay.png"); o.file_format = "PNG"; o.save()
    # side by side: photo | textured scan from the refined camera
    render(pb)
    sc = bpy.data.images.load(out, check_existing=False)
    b = np.array(sc.pixels[:], dtype=np.float32).reshape(RH, RW, 4)[::-1][..., :3]
    ph = np.array(bpy.data.images.load(str(EXP / f"references/{n}.jpeg")).pixels[:], dtype=np.float32)
    _, pimg = load_photo(n)
    a = np.array(pimg.pixels[:], dtype=np.float32).reshape(RH, RW, 4)[::-1][..., :3]
    sbs = np.concatenate([a, np.ones((RH, 8, 3)), b], 1)
    o = bpy.data.images.new("sbs", sbs.shape[1], RH)
    o.pixels[:] = np.concatenate([sbs, np.ones((RH, sbs.shape[1], 1))], -1)[::-1].ravel()
    o.filepath_raw = str(EXP / f"assets/cams/{n}_sbs.png"); o.file_format = "PNG"; o.save()


main()
