"""wax-seal: a sealing-wax seal with a raised, swappable emblem. Builds the scene, renders, saves.

Run from the repo root:
  tools/blender.sh experiments/wax-seal/scripts/build.py --out v01 --samples 256 --scale 1
  ... --set key=value      override any value in P
  ... --save               also save output/wax-seal.blend

The seal is one live geometry-nodes heightfield ("Wax Seal" modifier on the Seal object):
rim bead + stamped field + emblem relief. The emblem is any curve or mesh object on the
modifier's Emblem input, auto-fitted to Emblem Size.
"""
import argparse
import ast
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from common import LIBRARY, enable_gpu, experiment_paths  # noqa: E402
from nodes import auto_layout, group, how_to_tweak, material_from_group  # noqa: E402
from comp import compositor, post_group, use_saved_render  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "library" / "node-groups"))
from build_wax_seal import G, gn_input, seal_group  # noqa: E402

EXP = experiment_paths(__file__)

# Every value a designer might tune lives here. Override with --set key=value.
# Lengths in mm unless named otherwise.
P = {
    "res_x": 1212, "res_y": 1442,       # the reference crop's size, so compare.py lines up
    # --- seal shape (GN inputs) ---
    "seal_radius": 16.4,        # outer radius before wobble
    "oval": 1.03,               # >1 widens left-right
    "stamp_radius": 13.0,       # the stamp's circle; the rim is the wax squeezed outside it
    "field_height": 1.4,        # stamped field above the paper
    "dish": 0.08,               # field sinks this much toward the centre
    "rim_height": 2.4,          # rim bead crest
    "rim_peak": 0.3,            # 0..1 across the rim: where the crest sits (low = crest near the stamp)
    "rim_blend": 0.5,           # fillet between field and rim
    "wobble": 0.06,             # outline irregularity (fraction of radius)
    "wobble_scale": 1.6,        # lumps around the outline
    "bulge": 0.05,              # extra lobe of wax (fraction of radius)
    "bulge_angle": -35.0,       # degrees, 0 = right, -90 = bottom
    "bulge_width": 50.0,        # degrees
    "rim_lumps": 0.08,          # crest height noise (fraction)
    "pool": 0.6,                # wax pooled in the bulge: a taller, wrinkled lump (0 off)
    "flow": 0.03,               # low undulation over the whole seal
    "seed": 3.0,
    "detail": 0.045,            # grid spacing; smaller = finer relief, slower
    # --- emblem (GN inputs) ---
    "emblem": "wonder",         # wonder (library curve) | text (a Text curve) | monkey (a mesh) — swap tests
    "emblem_size": 17.0,        # longest side
    "emblem_rotation": 0.0,     # degrees
    "emblem_x": 0.0, "emblem_y": 0.0,
    "relief": 0.45,             # height of the raised emblem (negative = pressed in)
    "bevel": 0.15,              # width of the edge rounding
    "bevel_shape": 0.7,        # 0 chamfer … 1 round
    "soften": 2,                # blur passes over the relief (mesh emblems rely on this)
    # --- wax material ---
    "wax_color": (0.66, 0.58, 0.76, 1.0),
    "roughness": 0.6,          # stamped field
    "rim_roughness": 0.65,       # rim sets matte before pressing
    "scatter_mm": 0.07,         # SSS scale; keep well under the 1.4 mm field or the colour leaks out the bottom
    "relief_lift": 0.0,         # paler wax on the raised emblem (0 = same as the field)
    "sheen": 0.35,               # satin layer on top (Coat weight)
    "sheen_roughness": 0.22,
    "scatter_rgb": (1.0, 0.5, 1.2),  # per-channel reach; low green = light travelling inside turns violet
    "micro_bump": 0.15,
    "flow_lines": 0.5,
    # --- scene ---
    "paper_color": (0.80, 0.76, 0.73, 1.0),
    "key_power": 5.0,
    "key_size": 0.12,          # small: the reference shadow edge is ~10 px           # m
    "key_azimuth": 40.0,        # degrees from +x (screen right) toward screen top
    "key_elevation": 36.0,
    "key_distance": 0.5,        # m
    "world_strength": 0.14,
    "world_color": (1.0, 0.88, 0.78, 1.0),   # warm bounce from the card: warms the shadow core
    "cam_tilt": 16.0,           # degrees off straight down
    "lens": 100.0,
    "frame_mm": 37.5,           # frame width at the seal
    "view": "Khronos PBR Neutral",
    "exposure": -0.55,
    "glow": 0.0,
    "clay": False,              # debug: grey diffuse override
    "mirror": False,            # debug: mirror override (bad normals, domes)
}

HOW_TO_TWEAK = """\
wax-seal — how to tweak

SEAL SHAPE AND EMBLEM
Select "Seal", open the Modifier panel ("Wax Seal"). Every input is live.
- Emblem: pick any object. Curves (an imported SVG) get a true bevel; meshes are
  projected from above (their top face heights) and softened by Soften.
  The object's own location/rotation/scale are ignored: it is auto-fitted.
- Emblem Size (mm, longest side), Emblem Rotation, Emblem X/Y.
- Relief (mm, negative = pressed in), Bevel (mm edge width), Bevel Shape (0 chamfer,
  1 round), Soften (blur passes).
- Rim: Rim Height, Rim Peak, Rim Blend, Stamp Radius. Outline: Wobble, Bulge, Seed.
- Detail (mm): mesh spacing. Lower for tiny emblem detail (slower).
To swap the emblem: File > Import > SVG (or any mesh), then pick it in Emblem.
Hide the source object from render.

WAX
Select Seal, Shader Editor, the "Wax" node:
- Colour: the wax. Pastel wax reads lilac lit and violet in shadow.
- Roughness (field) / Rim Roughness: the rim set matte before the stamp pressed.
- Scatter (mm): how far light travels inside. 0.05-0.1 is opaque sealing wax;
  above ~0.15 the creases glow purple.
- Relief Lift: paler wax on the raised emblem (0 = same as the field).
- Sheen / Sheen Roughness: the satin layer on top.
- Micro Bump, Flow Lines: surface texture; flow lines stay on the field.

LIGHT
"Key" area light: Power, Size (small = crisp shadow edge, as in the reference).
Rotate the "Key Rig" empty about Z to move the light around the seal.
World: strength and colour are the warm fill that sets the shadow depth.

POST
Compositing tab: the "Post" node updates live on the saved render.

Built by experiments/wax-seal/scripts/build.py. Changes here are lost on rebuild;
copy good values back into P.
"""


# --- materials ---------------------------------------------------------------------------------

def wax_group():
    ng, gi, go = group("Wax", [
        ("Colour", "NodeSocketColor", P["wax_color"], None, None),
        ("Roughness", "NodeSocketFloat", P["roughness"], 0.0, 1.0),
        ("Rim Roughness", "NodeSocketFloat", P["rim_roughness"], 0.0, 1.0),
        ("Scatter", "NodeSocketFloat", P["scatter_mm"], 0.0, 10.0),        # mm
        ("Relief Lift", "NodeSocketFloat", P["relief_lift"], 0.0, 1.0),     # paler raised emblem
        ("Sheen", "NodeSocketFloat", P["sheen"], 0.0, 1.0),                 # satin layer
        ("Sheen Roughness", "NodeSocketFloat", P["sheen_roughness"], 0.0, 1.0),
        ("Micro Bump", "NodeSocketFloat", P["micro_bump"], 0.0, 2.0),
        ("Flow Lines", "NodeSocketFloat", P["flow_lines"], 0.0, 2.0),
    ], [("Shader", "NodeSocketShader")])
    g = G(ng); N, L, I = g.N, g.L, gi.outputs

    def attr(name):
        a = N.new("ShaderNodeAttribute"); a.attribute_name = name
        return a.outputs["Fac"]
    rim = attr("rim")
    co = N.new("ShaderNodeTexCoord").outputs["Object"]

    bsdf = N.new("ShaderNodeBsdfPrincipled")
    bsdf.subsurface_method = "RANDOM_WALK"
    lift = N.new("ShaderNodeMix"); lift.data_type = "RGBA"; lift.blend_type = "SCREEN"
    L(g.m("MULTIPLY", I["Relief Lift"], attr("relief")), lift.inputs[0])
    L(I["Colour"], lift.inputs[6]); L(I["Colour"], lift.inputs[7])
    L(lift.outputs[2], bsdf.inputs["Base Color"])
    bsdf.inputs["Subsurface Weight"].default_value = 1.0
    bsdf.inputs["Subsurface Radius"].default_value = P["scatter_rgb"]
    L(g.m("MULTIPLY", I["Scatter"], 0.001), bsdf.inputs["Subsurface Scale"])
    bsdf.inputs["IOR"].default_value = 1.5
    L(g.mix(I["Roughness"], I["Rim Roughness"], rim), bsdf.inputs["Roughness"])
    L(I["Sheen"], bsdf.inputs["Coat Weight"]); L(I["Sheen Roughness"], bsdf.inputs["Coat Roughness"])
    bsdf.inputs["Coat IOR"].default_value = 1.45

    # Micro surface: fine noise everywhere. Flow lines: hairline contours of a warped noise (curved,
    # meandering, like wax that flowed under the stamp), in patches, on the field only.
    micro = g.m("MULTIPLY", g.noise(co, 2500.0, detail=4.0), I["Micro Bump"])
    warp = N.new("ShaderNodeTexNoise"); L(co, warp.inputs["Vector"]); warp.inputs["Scale"].default_value = 40.0
    wv = g.vm("ADD", co, g.vm("SCALE", warp.outputs["Color"], scale=0.003))
    contour = g.m("ABSOLUTE", g.m("SUBTRACT", g.noise(wv, 150.0, detail=0.6), 0.5))
    line = g.m("SUBTRACT", 1.0, g.clamp01(g.m("DIVIDE", contour, 0.008)))
    sparse = g.clamp01(g.m("MULTIPLY", g.m("SUBTRACT", g.noise(co, 45.0, detail=2.0), 0.48), 5.0))
    flow = g.m("MULTIPLY", g.m("MULTIPLY", line, sparse), g.m("MULTIPLY", g.m("MULTIPLY", I["Flow Lines"], 2.5), g.m("SUBTRACT", 1.0, g.m("MAXIMUM", rim, attr("relief")))))
    bump = N.new("ShaderNodeBump")
    bump.inputs["Distance"].default_value = 0.00003
    L(g.m("ADD", micro, flow), bump.inputs["Height"])
    L(bump.outputs["Normal"], bsdf.inputs["Normal"]); L(bump.outputs["Normal"], bsdf.inputs["Coat Normal"])
    L(bsdf.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def paper_group():
    ng, gi, go = group("Paper", [
        ("Colour", "NodeSocketColor", P["paper_color"], None, None),
        ("Roughness", "NodeSocketFloat", 0.85, 0.0, 1.0),
    ], [("Shader", "NodeSocketShader")])
    g = G(ng); N, L, I = g.N, g.L, gi.outputs
    bsdf = N.new("ShaderNodeBsdfPrincipled")
    L(I["Colour"], bsdf.inputs["Base Color"]); L(I["Roughness"], bsdf.inputs["Roughness"])
    co = N.new("ShaderNodeTexCoord").outputs["Object"]
    bump = N.new("ShaderNodeBump"); bump.inputs["Distance"].default_value = 0.00002
    L(g.noise(co, 900.0, detail=6.0), bump.inputs["Height"])
    L(bump.outputs["Normal"], bsdf.inputs["Normal"])
    L(bsdf.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


# --- scene -------------------------------------------------------------------------------------

def load_emblem(scene):
    """The Wonder logomark curve from the library, modifiers stripped. Hidden from render:
    the seal's modifier reads its shape."""
    with bpy.data.libraries.load(str(LIBRARY / "models/wonder-logos/wonder_logos.blend")) as (_, dst):
        dst.objects = ["wonder_logomark"]
    obj = dst.objects[0]
    scene.collection.objects.link(obj)
    obj.name = "Emblem_Wonder"
    for mod in list(obj.modifiers):
        obj.modifiers.remove(mod)
    obj.data.extrude = obj.data.bevel_depth = 0.0
    obj.location = (0.06, 0, 0)
    obj.hide_render = True
    return obj


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="wip", help="render name, saved to renders/<out>.png")
    ap.add_argument("--samples", type=int, default=256)
    ap.add_argument("--scale", type=float, default=1.0)
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


def post():
    ng, gi, go = post_group("Post", [
        ("Glow", "NodeSocketFloat", P["glow"], 0.0, 2.0),
    ])
    glare = ng.nodes.new("CompositorNodeGlare")
    glare.inputs["Type"].default_value = "Fog Glow"
    glare.inputs["Size"].default_value = 0.5
    ng.links.new(gi.outputs["Image"], glare.inputs["Image"])
    ng.links.new(gi.outputs["Glow"], glare.inputs["Strength"])
    ng.links.new(glare.outputs["Image"], go.inputs["Image"])
    auto_layout(ng)
    return ng


def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    enable_gpu(scene)
    scene.unit_settings.length_unit = "MILLIMETERS"

    material_from_group("Wax", wax_group())

    # Paper
    bpy.ops.mesh.primitive_plane_add(size=0.5)
    paper = bpy.context.active_object
    paper.name = "Paper"
    paper.data.materials.append(material_from_group("Paper", paper_group()))

    # Seal: an empty mesh carrying the geometry-nodes seal.
    emblem = load_emblem(scene)
    if P["emblem"] == "text":
        td = bpy.data.curves.new("Emblem_Text", "FONT"); td.body = "W&Co"; td.align_x = "CENTER"
        emblem = bpy.data.objects.new("Emblem_Text", td); scene.collection.objects.link(emblem)
        emblem.hide_render = True
    elif P["emblem"] == "monkey":
        bpy.ops.mesh.primitive_monkey_add(location=(0.1, 0, 0))
        emblem = bpy.context.active_object; emblem.hide_render = True
    mesh = bpy.data.meshes.new("Seal")
    seal = bpy.data.objects.new("Seal", mesh)
    scene.collection.objects.link(seal)
    mod = seal.modifiers.new("Wax Seal", "NODES")
    mod.node_group = seal_group(bpy.data.materials["Wax"], P)
    gn_input(mod, "Emblem", emblem)
    seal.data.materials.append(bpy.data.materials["Wax"])

    # Key light on a rig: rotate the rig about Z to move the light around the seal.
    rig = bpy.data.objects.new("Key Rig", None)
    scene.collection.objects.link(rig)
    rig.rotation_euler = (0, 0, math.radians(P["key_azimuth"]))
    kd = bpy.data.lights.new("Key", "AREA")
    kd.energy, kd.size = P["key_power"], P["key_size"]
    key = bpy.data.objects.new("Key", kd)
    scene.collection.objects.link(key)
    key.parent = rig
    el = math.radians(P["key_elevation"])
    key.location = (P["key_distance"] * math.cos(el), 0, P["key_distance"] * math.sin(el))
    key.rotation_euler = (0, math.radians(90) - el, 0)  # face the origin: local -Z toward the seal

    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = P["world_color"]
    bg.inputs["Strength"].default_value = P["world_strength"]
    scene.world = world

    # Camera: near top-down, tilted toward screen bottom; frame width set at the seal.
    tilt = math.radians(P["cam_tilt"])
    dist = P["frame_mm"] * 0.001 * P["lens"] / 36.0
    cd = bpy.data.cameras.new("Camera")
    cd.lens, cd.sensor_width, cd.sensor_fit = P["lens"], 36.0, "HORIZONTAL"
    cd.clip_start = 0.01
    cam = bpy.data.objects.new("Camera", cd)
    scene.collection.objects.link(cam)
    cam.location = (0, -dist * math.sin(tilt), dist * math.cos(tilt) + 0.0015)
    cam.rotation_euler = (tilt, 0, 0)
    scene.camera = cam

    scene.render.resolution_x, scene.render.resolution_y = P["res_x"], P["res_y"]
    scene.view_settings.view_transform = P["view"]
    scene.view_settings.exposure = P["exposure"]
    scene.cycles.use_denoising = True
    scene.cycles.sample_clamp_indirect = 5.0
    if P["clay"] or P["mirror"]:
        ov = bpy.data.materials.new("Override")
        ov.use_nodes = True
        b = ov.node_tree.nodes["Principled BSDF"]
        if P["mirror"]:
            b.inputs["Metallic"].default_value, b.inputs["Roughness"].default_value = 1.0, 0.02
        scene.view_layers[0].material_override = ov
    how_to_tweak(HOW_TO_TWEAK)
    return scene


if __name__ == "__main__":
    args = parse_args()
    scene = build_scene()
    raw = EXP["renders"] / f"{args.out}_raw.exr"
    compositor(scene, post(), raw_exr=raw)
    scene.cycles.samples = args.samples
    scene.render.resolution_percentage = round(args.scale * 100)
    if not args.norender:
        scene.render.filepath = str(EXP["renders"] / f"{args.out}.png")
        bpy.ops.render.render(write_still=True)
    if args.save:
        if not args.norender:
            use_saved_render(scene, raw, EXP["output"])
        blend = EXP["output"] / f"{EXP['name']}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        blend.with_suffix(".blend1").unlink(missing_ok=True)
    print("BUILD OK")
