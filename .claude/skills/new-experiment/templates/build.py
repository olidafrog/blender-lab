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
from nodes import auto_layout, group, how_to_tweak, material_from_group  # noqa: E402

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

Each material is one node. Select the object, open the Shader Editor, and change
the inputs on its group node. Hover an input for its range.

- Look: Colour, Gloss (0 matte → 1 mirror).
- Key light: select "Key", change Power and Size in Object Data.

Built by experiments/__NAME__/scripts/build.py. Changes made here are lost on rebuild;
copy good values back into P.
"""


def look_group():
    """The designer-facing control node. Keep internals inside; expose 3-8 inputs."""
    ng, gi, go = group("Look", [
        ("Colour", "NodeSocketColor", P["base_color"], None, None),
        ("Gloss", "NodeSocketFloat", 1 - P["roughness"], 0.0, 1.0),  # 0 matte, 1 mirror
    ], [("Shader", "NodeSocketShader")])
    bsdf = ng.nodes.new("ShaderNodeBsdfPrincipled")
    inv = ng.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    ng.links.new(gi.outputs["Gloss"], inv.inputs[1])
    ng.links.new(gi.outputs["Colour"], bsdf.inputs["Base Color"])
    ng.links.new(inv.outputs[0], bsdf.inputs["Roughness"])
    ng.links.new(bsdf.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


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

    subject.data.materials.append(material_from_group("Subject", look_group()))

    bpy.ops.object.light_add(type="AREA", location=(3, -3, 5))
    key = bpy.context.active_object
    key.name = "Key"
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
    how_to_tweak(HOW_TO_TWEAK)
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
