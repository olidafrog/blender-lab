"""Render the textured Polycam scan: top-down ortho plan (ceiling cut away) and optional views.

  tools/blender.sh experiments/apartment-model/scripts/scan_render.py [--cut 1.8] [--out plan_top]
Scan frame after import: the OBJ importer gives z-up; we apply the same yaw and floor offset
as scan_tools.align so coordinates agree with the measuring scripts.
"""
import math
import sys
from pathlib import Path

import bpy

EXP = Path(__file__).resolve().parents[1]
OBJ = EXP / "references/scans/03_10_2026 2/03_10_2026.obj"
YAW, FLOOR = 0.544, -1.232       # from scan_tools.align


def load_scan():
    bpy.ops.wm.obj_import(filepath=str(OBJ), forward_axis="NEGATIVE_Z", up_axis="Y")
    parts = list(bpy.context.selected_objects)          # the OBJ holds one object per texture
    root = bpy.data.objects.new("Scan", None)
    bpy.context.scene.collection.objects.link(root)
    for o in parts:
        o.parent = root
    root.rotation_euler = (0, 0, math.radians(YAW))
    root.location = (0, 0, -FLOOR)
    bpy.context.view_layer.update()
    return parts[0]


def grid(path, cam, res):
    """Overlay a metric grid in the camera's image plane: 0.1 m faint, 0.5 m mid, 1 m strong (labelled by colour)."""
    import numpy as np
    img = bpy.data.images.load(path)
    W, H = res
    a = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)      # bottom row first
    s = cam.data.ortho_scale / W                                          # metres per px
    m = cam.matrix_world
    right, up = m.col[0].xyz.normalized(), m.col[1].xyz.normalized()
    c = m.translation
    u0 = c.dot(right) - W / 2 * s                                         # world coord along right at px 0
    v0 = c.dot(up) - H / 2 * s
    for axis, n, origin in ((1, W, u0), (0, H, v0)):
        coords = origin + (np.arange(n) + 0.5) * s
        for step, col, w in ((0.1, (0.3, 0.3, 1.0), 0.25), (0.5, (0.1, 0.1, 1.0), 0.5), (1.0, (1.0, 0.0, 0.0), 0.8)):
            hit = np.abs((coords / step) - np.round(coords / step)) * step < s / 2
            idx = np.nonzero(hit)[0]
            if axis == 1:
                a[:, idx, :3] = a[:, idx, :3] * (1 - w) + np.array(col) * w
            else:
                a[idx, :, :3] = a[idx, :, :3] * (1 - w) + np.array(col) * w
    img.pixels[:] = a.ravel()
    img.save()
    print(f"[out] grid: px 0 = {u0:.3f} m (right), bottom row = {v0:.3f} m (up), {1/s:.1f} px/m")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    cut = float(argv[argv.index("--cut") + 1]) if "--cut" in argv else 1.8
    out = argv[argv.index("--out") + 1] if "--out" in argv else "plan_top"
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    ob = load_scan()
    bb = [ob.matrix_world @ __import__("mathutils").Vector(c) for c in ob.bound_box]
    print("[out] bounds", [round(min(v[i] for v in bb), 3) for i in range(3)], [round(max(v[i] for v in bb), 3) for i in range(3)])
    cam_data = bpy.data.cameras.new("Top")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 11.6
    cam_data.clip_start = 0.01
    cam_data.clip_end = 100
    cam = bpy.data.objects.new("Top", cam_data)
    scene.collection.objects.link(cam)
    view = argv[argv.index("--view") + 1] if "--view" in argv else "top"
    # ortho views; the camera sits at the cut, so everything nearer than `cut` along the view is clipped
    views = {
        "top": ((0.7, 0.0, cut), (0, 0, 0), 11.6, (1740, 1000)),
        "windows": ((cut, 0.0, 2.1), (math.radians(90), 0, math.radians(90)), 6.4, (1600, 1200)),   # look -x
        "mezz": ((cut, 0.0, 2.1), (math.radians(90), 0, math.radians(-90)), 6.4, (1600, 1200)),    # look +x
        "west": ((-1.6, cut, 2.1), (math.radians(90), 0, math.radians(180)), 10.0, (2000, 1000)),  # look -y
        "east": ((-1.6, cut, 2.1), (math.radians(90), 0, 0), 10.0, (2000, 1000)),                  # look +y
    }
    loc, rot, scale, res = views[view]
    cam.location, cam.rotation_euler, cam_data.ortho_scale = loc, rot, scale
    scene.camera = cam
    scene.render.engine = "BLENDER_WORKBENCH"
    sh = scene.display.shading
    sh.light = "FLAT"
    sh.color_type = "TEXTURE"
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.filepath = str(EXP / f"assets/scan_views/{out}.png")
    bpy.ops.render.render(write_still=True)
    grid(scene.render.filepath, cam, res)
    print("[out] wrote", scene.render.filepath)


if __name__ == "__main__":
    main()
