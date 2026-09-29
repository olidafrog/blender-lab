"""Print an object's top-surface height along a line, straight from an experiment's build.py.

    tools/blender.sh tools/mesh_profile.py <build.py> <object> [x0,y0 x1,y1] [step_mm] [key=value ...]
    tools/blender.sh tools/mesh_profile.py experiments/wax-seal-chaos/scripts/build.py Seal -18,0 -8,0 0.25 voxel=0.1

Builds the scene (no render), evaluates the object and prints max z (mm) of the vertices within
half a step of each sample point. Use it to check a shape (rim height, field level, a step or dip)
in seconds instead of reading it off a render. key=value pairs override the build's P.
"""
import ast
import importlib.util
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
build, name = argv[0], argv[1]
rest = argv[2:]
pts = [a for a in rest if "," in a and "=" not in a]
sets = [a for a in rest if "=" in a]
nums = [a for a in rest if a not in pts and a not in sets]
a = Vector([float(v) for v in (pts[0] if pts else "-18,0").split(",")] + [0])
b = Vector([float(v) for v in (pts[1] if len(pts) > 1 else "0,0").split(",")] + [0])
step = float(nums[0]) if nums else 0.25

spec = importlib.util.spec_from_file_location("build", build)
mod = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0], "--"]
spec.loader.exec_module(mod)
for kv in sets:
    k, v = kv.split("=", 1)
    mod.P[k] = ast.literal_eval(v)
mod.build_scene()

ob = bpy.data.objects[name]
me = ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
mw = ob.matrix_world
vs = [mw @ v.co * 1000 for v in me.vertices]  # mm
n = max(1, int((b - a).length / step))
out = []
for i in range(n + 1):
    p = a + (b - a) * (i / n)
    zs = [v.z for v in vs if abs(v.x - p.x) < step / 2 and abs(v.y - p.y) < step / 2]
    out.append(f"{p.x:.2f},{p.y:.2f}:{max(zs):.2f}" if zs else f"{p.x:.2f},{p.y:.2f}:-")
print("[out] x,y(mm):top z(mm)  " + "  ".join(out))
