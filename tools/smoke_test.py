"""Headless smoke test: builds a small scene, renders a PNG, saves the .blend.

Run:
  tools/blender.sh tools/smoke_test.py

Also builds the new-experiment template at 10% scale, 4 samples (5.x only).
Outputs go to the system temp dir; nothing lands in the repo.
"""
import math
import sys
import time
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import enable_gpu  # noqa: E402

import tempfile  # noqa: E402

TMP = Path(tempfile.gettempdir())
OUT = {"render": TMP / "smoke_test.png", "blend": TMP / "smoke_test.blend"}

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Geometry
bpy.ops.mesh.primitive_plane_add(size=20)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1), segments=64, ring_count=32)
bpy.ops.object.shade_smooth()
sphere = bpy.context.active_object

mat = bpy.data.materials.new("Clay")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.9, 0.35, 0.2, 1)
bsdf.inputs["Roughness"].default_value = 0.35
sphere.data.materials.append(mat)

# Light
bpy.ops.object.light_add(type="AREA", location=(3, -3, 5))
light = bpy.context.active_object
light.data.energy = 800
light.data.size = 4
light.rotation_euler = (math.radians(40), 0, math.radians(45))

# World
world = bpy.data.worlds.new("World")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.3
scene.world = world

# Camera
bpy.ops.object.camera_add(location=(6, -6, 4))
cam = bpy.context.active_object
direction = sphere.location - cam.location
cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
scene.camera = cam

# Render
scene.render.engine = "CYCLES"
enable_gpu(scene)  # after read_factory_settings, which resets prefs
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.filepath = str(OUT["render"])
t0 = time.perf_counter()
bpy.ops.render.render(write_still=True)
print(f"RENDER TIME {time.perf_counter() - t0:.2f}s")

bpy.ops.wm.save_as_mainfile(filepath=str(OUT["blend"]))
print(f"Saved {OUT['render']}")


def template_check():
    """Build the new-experiment template at a tiny size, so API drift in nodes.py and comp.py
    shows up here and not in the next experiment. Runs in a temp copy of the repo layout."""
    import runpy
    import shutil

    repo = Path(__file__).resolve().parents[1]
    if bpy.app.version < (5, 0, 0):
        print("[out] TEMPLATE SKIPPED: the template uses the 5.x compositor API")
        return
    root = TMP / "blender-lab-smoke"
    shutil.rmtree(root, ignore_errors=True)
    shutil.copytree(repo / "tools", root / "tools", ignore=shutil.ignore_patterns("__pycache__"))
    script = root / "experiments" / "smoke" / "scripts" / "build.py"
    script.parent.mkdir(parents=True)
    src = (repo / ".claude/skills/new-experiment/templates/build.py").read_text(encoding="utf-8")
    script.write_text(src.replace("__NAME__", "smoke"), encoding="utf-8")
    argv = sys.argv
    sys.argv = [argv[0], "--", "--out", "smoke", "--scale", "0.1", "--samples", "4", "--save"]
    try:
        runpy.run_path(str(script), run_name="__main__")
    finally:
        sys.argv = argv
    exp = script.parents[1]
    for f in (exp / "renders/smoke.png", exp / "renders/smoke_raw.exr", exp / "output/smoke.blend"):
        if not f.exists():
            sys.exit(f"TEMPLATE FAILED: missing {f}")
    print("[out] TEMPLATE OK")


template_check()
print("SMOKE TEST OK")
