"""__NAME__: build the whole scene from nothing, render, save.

Run from the repo root:
  tools/blender.sh experiments/__NAME__/scripts/build.py --out v01 --samples 128 --scale 0.5
  ... --set key=value      override any value in P
  ... --save               also save output/__NAME__.blend
"""
import argparse
import ast
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from common import enable_gpu, experiment_paths  # noqa: E402

EXP = experiment_paths(__file__)

# Every value a designer might tune lives here. Override with --set key=value.
P = {
    "res_x": 1600,
    "res_y": 1200,
    "cam_distance": 6.0,
    "cam_height": 2.0,
    "key_power": 800.0,
    "key_size": 4.0,
    "world_strength": 0.3,
    "base_color": (0.8, 0.8, 0.8, 1.0),
    "roughness": 0.4,
}

HOW_TO_TWEAK = """\
__NAME__ — how to tweak
- Material controls: select the object, Shader Editor, "Look" group inputs.
- Rebuild from scripts/build.py rather than hand-editing this file.
"""


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="wip", help="render name, saved to renders/<out>.png")
    ap.add_argument("--samples", type=int, default=128)
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--norender", action="store_true")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    a = ap.parse_args(argv)
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in P:
            sys.exit(f"unknown P key: {k}")
        P[k] = ast.literal_eval(v)
    return a


def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    enable_gpu(scene)  # after the factory reset, which clears the GPU choice

    bpy.ops.mesh.primitive_plane_add(size=40)
    bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 1))
    subject = bpy.context.active_object
    subject.modifiers.new("Subdiv", "SUBSURF").levels = 2
    bpy.ops.object.shade_smooth()

    mat = bpy.data.materials.new("Look")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = P["base_color"]
    bsdf.inputs["Roughness"].default_value = P["roughness"]
    subject.data.materials.append(mat)

    bpy.ops.object.light_add(type="AREA", location=(3, -3, 5))
    key = bpy.context.active_object
    key.data.energy = P["key_power"]
    key.data.size = P["key_size"]
    key.rotation_euler = (math.radians(40), 0, math.radians(45))

    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = P["world_strength"]
    scene.world = world

    bpy.ops.object.camera_add(location=(0, -P["cam_distance"], P["cam_height"]))
    cam = bpy.context.active_object
    cam.rotation_euler = (subject.location - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam

    scene.render.resolution_x = P["res_x"]
    scene.render.resolution_y = P["res_y"]
    txt = bpy.data.texts.new("HOW_TO_TWEAK")
    txt.write(HOW_TO_TWEAK)
    return scene


if __name__ == "__main__":
    args = parse_args()
    scene = build_scene()
    scene.cycles.samples = args.samples
    scene.render.resolution_percentage = round(args.scale * 100)
    if not args.norender:
        scene.render.filepath = str(EXP["renders"] / f"{args.out}.png")
        bpy.ops.render.render(write_still=True)
    if args.save:
        blend = EXP["output"] / f"{EXP['name']}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        blend.with_suffix(".blend1").unlink(missing_ok=True)
    print("BUILD OK")
