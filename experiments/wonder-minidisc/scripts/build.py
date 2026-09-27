"""wonder-minidisc: the Wonder logomark as a diffraction-grating disc inside a moulded
translucent case whose outline follows the logo. Build the whole scene, render, save.

Run from the repo root:
  tools/blender.sh experiments/wonder-minidisc/scripts/build.py --out v01 --samples 256 --scale 0.5
  ... --set key=value      override any value in P
  ... --save               also save output/wonder-minidisc.blend
"""
import argparse
import ast
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))
sys.path.insert(0, str(HERE))
from common import LIBRARY, enable_gpu, experiment_paths  # noqa: E402
from nodes import auto_layout, how_to_tweak, material_from_group  # noqa: E402
from comp import LEGACY, compositor, post_group, use_saved_render  # noqa: E402
import geometry  # noqa: E402
sys.path.insert(0, str(LIBRARY / "materials"))
import build_materials as materials  # noqa: E402  (library: cd_diffraction, tinted_plastic)

EXP = experiment_paths(__file__)
ASSETS = EXP["root"] / "assets"

# Every value a designer might tune lives here. Override with --set key=value.
P = {
    "res_x": 1600,
    "res_y": 1280,
    # --- shape (logo units: the logomark is 124 x 128; mm where named) ---
    "mm_per_unit": 64.0 / 124.0,   # logomark as wide as a MiniDisc disc (64 mm)
    "case_offset": 11.0,           # case outline distance from the logo
    "case_close": 7.0,             # rounds the notches between the strokes
    "case_h": 5.0,                 # mm, MiniDisc thickness
    "plate": 1.0,                  # mm, top and bottom shell plates
    "side_wall": 1.3,              # mm, perimeter wall
    "edge_round": 0.6,             # mm, outer edge fillet
    "inner_round": 0.3,            # mm, inner fillet
    "well_gap": 2.4,               # units, air gap round each disc piece
    "well_rib": 0.8,               # mm, ring wall round each well
    "rib_h": 0.9,                  # mm, height of each ring rib (top and bottom shell); gap between
    "bosses": [(-24.5, 54.0), (25.0, 54.0), (1.8, -54.0), (-24.5, 8.0)],  # screw posts, units
    "boss_r": 3.6,                 # units
    "boss_hole_r": 1.4,            # units
    "disc_t": 1.2,                 # mm
    "groove_centre": (0.0, 8.0),   # units; the tracks circle this point
    "hub_r": 6.0,                  # units, steel clamping plate
    "hub_t": 0.25,                 # mm
    "yaw": -14.0,                  # degrees, object turn on the table
    "show_case": True,             # debug: False renders the disc alone
    "clay": False,                 # debug: flat grey override to check geometry
    "round_disc": False,           # debug: a plain round disc to check the grating shader
    # --- disc material ---
    "spectrum": 1.0,
    "saturation": 1.0,
    "pitch_um": 1.6,
    "spread": 0.08,
    "aniso": 0.3,
    "mirror": 0.35,
    "mirror_tint": (1.0, 0.72, 0.82, 1.0),  # pink magneto-optical layer of a recordable MD; tints every order
    "clear_hub_mm": 4.2,
    "order2": 0.15,
    # --- case material ---
    "case_colour": (0.30, 0.85, 0.78, 1.0),  # teal, as seen through one wall at colour_depth_mm
    "colour_depth_mm": 3.0,        # thin plates near-clear, thick walls deep: the spectrum survives
    "clarity": 1.0,
    "frost": 0.02,
    "scratches": 0.08,
    "fingerprints": 0.08,
    "dust": 0.2,
    "shadow_light": 0.9, 
    "imperf_scale": 6.0,           # map repeats per metre x this... (object space, metres)
    "steel_colour": (0.55, 0.55, 0.56, 1.0),
    "steel_rough": 0.45,
    # --- studio ---
    "sweep_colour": (0.9, 0.9, 0.9, 1.0),
    "sweep_gloss": 0.35,
    "sweep_coat_rough": 0.1,
    "sweep_back": 0.8,             # m; a nearer back wall shows up in the disc's colour bands as white
    "hdri": "studio_small_09_4k.exr",
    "hdri_strength": 0.0,          # off: shadow-invisible flag cannot stop the disc sampling the HDRI
    "hdri_rot": 0.0,               # degrees
    # Big lights sit behind the black flag or > 62 deg off the mirror direction, where no
    # diffracted order can reach them (printed as [out] angles at build time).
    "key_power": 4.0,              # W, big softbox over the camera: lights the table, never reflected
    "key_size": 0.50,              # m
    "key_pos": (0.0, -0.40, 0.40),
    "strip_power": 1.5,            # W, thin strip on the camera side for a crisp edge line
    "strip_size": (0.02, 0.35),
    "strip_pos": (-0.26, -0.16, 0.12),
    "back_power": 1.5,             # W, fill over the far table so the background stays white
    "back_pos": (0.0, 0.30, 0.35),
    "back_size": 0.5,
    "big_lights_reflect": False,   # True lets key/strip/back show up in reflections (they wash the disc)
    # the disc is a mirror: it must see dark where it reflects the camera's view, and bright
    # sources around that spot for the diffracted colours to pick up
    "flag_size": 3.0,              # m, black card on the mirror direction, seen only in reflections
    "flag_dist": 0.40,
    # Wedge lights: short arcs round the mirror direction. Each arc makes one radial colour sector
    # on the disc; its angle off the mirror direction picks the hue (first order: lambda = d sin(angle),
    # 15 deg violet, 17 blue, 19 cyan, 21 green, 23 orange, 25 red).
    "wedges": [(15.5, 0.0), (21.0, 45.0), (24.5, 90.0), (18.5, 135.0),
               (23.0, 180.0), (16.5, 225.0), (20.0, 270.0), (25.5, 315.0)],  # (angle deg, azimuth deg)
    "wedge_span": 28.0,            # degrees of azimuth each arc covers: sector width
    "ring_dist": 0.30,
    "ring_power": 0.006,           # W per arc
    "ring_width": 0.012,           # m, radial thickness of each arc
    # --- camera ---
    "cam_elev": 58.0,              # degrees above the table
    "cam_azim": -8.0,              # degrees around from the front
    "cam_dist": 0.30,              # m
    "focal": 85.0,
    "fstop": 16.0,
    "view": "Standard",
    "look": "None",
    "exposure": -0.4,
    # --- post ---
    "glow": 0.2,
    "glow_size": 0.5,
    "glow_threshold": 1.0,
    "chroma": 0.003,
}

HOW_TO_TWEAK = """wonder-minidisc — how to tweak

Each material is one node. Select the object, open the Shader Editor, change the inputs on
its group node. Hover an input for its range.

CASE (object "Case", group "Case Plastic")
- Colour: the colour you see through "Colour Depth mm" of plastic. Any colour works; thick
  walls go deeper, thin plates paler, like real tinted polycarbonate.
- Colour Depth mm: THE key trade-off. Small (1.5) = strongly tinted plates, the disc glows in
  the case colour (like the red Sony MiniDisc). Large (5) = pale plates, the disc keeps its full
  rainbow. 3 is the middle. A teal/green case always removes pinks: that is physics.
- Clarity: 1 clear, 0 opaque plastic.   Frost: surface haze on everything seen through it.
- Scratches, Fingerprints, Dust: wear on the surface reflection only (never blurs the disc).
- Shadow Light: how much light gets inside the case and through to the table. Lower = deeper,
  richer colour and a darker coloured shadow; higher = lighter, glassier webs.

DISC (object "Disc", group "Disc") — a real diffraction grating, lit by the "Wedge" lights
- Spectrum: strength of the rainbow.   Saturation: 1 = CD, ~0.35 = pastel holographic foil.
- Track Pitch um: groove spacing (1.6 = real CD). Smaller = colours fan further from the lights.
- Spread: softness of each colour band.   Streak: radial streaking.
- Mirror: the plain mirror between the colours.  Mirror Tint: colour of the reflective layer;
  it tints every colour (pink = recordable MiniDisc).
- Second Order: the outer, fainter rainbow.   Clear Hub mm: clear ring round the steel hub.

HUB (object "Hub", group "Hub Steel"): Colour, Roughness.
TABLE (object "Sweep", group "Sweep"): Colour, Gloss.

LIGHTS — the disc is a mirror, so its colours ARE the lights it reflects.
- "Wedge0..7": small arcs round the disc's mirror direction, visible only in reflections.
  Each one paints one radial colour sector. Its angle off the mirror direction sets the hue
  (about 15 deg violet, 19 cyan, 21 green, 23 orange, 25 red). Move or rotate them to move the
  sectors; change their Power for brighter colour.
- "Flag": a black card only reflections can see. It keeps the mirror dark between the colours.
  Remove it and the disc goes white.
- "Key" (over the camera), "Back" (far table), "Strip" (edge line): light the case and table.
  They are hidden from reflections on purpose: if the disc could see them it would wash white.
- Post: open the Compositing tab; the backdrop shows the saved render.

Built by experiments/wonder-minidisc/scripts/build.py (every value in its P dict, --set to
override). Changes made here are lost on rebuild; copy good values back into P.
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


def post():
    """Compositor controls on one node. Tab into it in Blender to see the parts."""
    ng, gi, go = post_group("Post", [
        ("Glow", "NodeSocketFloat", P["glow"], 0.0, 2.0),
        ("Glow Size", "NodeSocketFloat", P["glow_size"], 0.0, 1.0),
        ("Glow Threshold", "NodeSocketFloat", P["glow_threshold"], 0.0, 4.0),
        ("Chroma", "NodeSocketFloat", P["chroma"], 0.0, 0.05),
    ])
    glare = ng.nodes.new("CompositorNodeGlare")
    lens = ng.nodes.new("CompositorNodeLensdist")
    ng.links.new(gi.outputs["Image"], glare.inputs["Image"])
    if LEGACY:  # 4.4: Glare settings are node properties; the group inputs cannot drive them
        glare.glare_type, glare.quality = "FOG_GLOW", "HIGH"
        glare.mix = P["glow"] - 1.0
        glare.size = max(6, min(9, round(6 + 3 * P["glow_size"])))
        glare.threshold = P["glow_threshold"]
    else:
        glare.inputs["Type"].default_value = "Fog Glow"
        for src, dst in (("Glow", "Strength"), ("Glow Size", "Size"), ("Glow Threshold", "Threshold")):
            ng.links.new(gi.outputs[src], glare.inputs[dst])
    ng.links.new(glare.outputs["Image"], lens.inputs["Image"])
    ng.links.new(gi.outputs["Chroma"], lens.inputs["Dispersion"])
    ng.links.new(lens.outputs["Image"], go.inputs["Image"])
    auto_layout(ng)
    return ng


def sweep():
    """Seamless table: a floor that curves up into a back wall."""
    import bmesh
    bm = bmesh.new()
    b = P["sweep_back"]  # where the floor starts to curve up; keep it behind the flag
    prof = [(y, 0.0) for y in (-0.8, -0.2, 0.0, b)]
    R = 0.25
    for i in range(1, 13):
        t = i / 12 * math.pi / 2
        prof.append((b + R * math.sin(t), R - R * math.cos(t)))
    prof.append((b + R, 1.2))
    W = 1.5
    rows = [[bm.verts.new((x, y, z)) for (y, z) in prof] for x in (-W, W)]
    for i in range(len(prof) - 1):
        bm.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
    me = bpy.data.meshes.new("Sweep")
    bm.to_mesh(me); bm.free()
    for f in me.polygons:
        f.use_smooth = True
    ob = bpy.data.objects.new("Sweep", me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def area(name, power, size, pos, target=(0, 0, 0), shape="SQUARE", glossy=True, transmission=True, diffuse=True,
         up=None):
    """Area light at pos facing target. `up`: world direction for the light's local Y (its size_y)."""
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy = power
    if isinstance(size, (tuple, list)):
        ld.shape, ld.size, ld.size_y = "RECTANGLE", size[0], size[1]
    else:
        ld.shape, ld.size = shape, size
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = pos
    if up is None:
        ob.rotation_euler = (Vector(target) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    else:
        from mathutils import Matrix
        z = (Vector(pos) - Vector(target)).normalized()
        y = (Vector(up) - z * Vector(up).dot(z)).normalized()
        ob.rotation_euler = Matrix((y.cross(z), y, z)).transposed().to_euler()
    ob.visible_glossy, ob.visible_transmission, ob.visible_diffuse = glossy, transmission, diffuse
    return ob


def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    enable_gpu(scene)

    O = geometry.cached_outlines(P, ASSETS / "cache")
    case = geometry.build_case(P, O)
    disc, hub = geometry.build_disc(P, O)
    rig = bpy.data.objects.new("MiniDisc", None)
    scene.collection.objects.link(rig)
    lift = P["case_h"] / 2 * geometry.MM + 0.03 * geometry.MM  # a hair above the table: coplanar faces render black
    for ob in (case, disc):
        ob.parent = rig
    rig.location = (0, 0, lift)
    rig.rotation_euler = (0, 0, math.radians(P["yaw"]))

    imperf = materials.IMPERFECTIONS  # wear maps in library/textures
    m_case = material_from_group("Case Plastic", materials.case_group(P, imperf))
    g = next(n for n in m_case.node_tree.nodes if n.bl_idname == "ShaderNodeGroup")
    out = m_case.node_tree.nodes["Material Output"]
    m_case.node_tree.links.new(g.outputs["Volume"], out.inputs["Volume"])
    m_case.cycles.homogeneous_volume = True
    case.data.materials.append(m_case)
    case.hide_render = not P["show_case"]
    disc.data.materials.append(material_from_group("Disc", materials.disc_group(P)))
    hub.data.materials.append(material_from_group("Hub Steel", materials.steel_group(P)))
    sw = sweep()
    sw.data.materials.append(material_from_group("Sweep", materials.sweep_group(P)))

    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    wn = world.node_tree.nodes
    env = wn.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(str(ASSETS / "hdri" / P["hdri"]), check_existing=True)
    mp = wn.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (0, 0, math.radians(P["hdri_rot"]))
    tc = wn.new("ShaderNodeTexCoord")
    world.node_tree.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    world.node_tree.links.new(mp.outputs[0], env.inputs["Vector"])
    bg = wn["Background"]
    bg.inputs["Strength"].default_value = P["hdri_strength"]
    world.node_tree.links.new(env.outputs["Color"], bg.inputs["Color"])
    scene.world = world

    # The big softboxes light the case and table but not the disc: a grating lit by a big
    # source adds every colour band back to white. The disc takes its light from the ring.
    not_disc = bpy.data.collections.new("Not The Disc")
    not_disc.objects.link(disc)
    not_disc.collection_objects[0].light_linking.link_state = "EXCLUDE"  # index only; no name lookup
    # mirror direction: the camera's view reflected in the table plane
    el, az = math.radians(P["cam_elev"]), math.radians(P["cam_azim"])
    mdir = Vector((-math.cos(el) * math.sin(az), math.cos(el) * math.cos(az), math.sin(el)))
    centre = Vector((0, 0, P["case_h"] * geometry.MM))
    for name, pw, size, pos in (("Key", P["key_power"], P["key_size"], P["key_pos"]),
                                ("Strip", P["strip_power"], P["strip_size"], P["strip_pos"]),
                                ("Back", P["back_power"], P["back_size"], P["back_pos"])):
        if pw <= 0:
            continue
        # never seen in a reflection or through the plastic: only the ring lights paint the disc
        area(name, pw, size, pos, glossy=P["big_lights_reflect"],
             transmission=P["big_lights_reflect"]).light_linking.receiver_collection = not_disc
        v = Vector(pos) - centre
        ang = math.degrees(v.angle(mdir))
        behind = v.dot(mdir) > P["flag_dist"]
        print(f"[out] {name}: {ang:.0f} deg off mirror, behind flag {behind}, "
              f"{'OK' if behind or ang > 62 else 'DIFFRACTS (white wash on disc)'}")
    flag = bpy.data.meshes.new("Flag")
    h = P["flag_size"] / 2
    flag.from_pydata([(-h, -h, 0), (h, -h, 0), (h, h, 0), (-h, h, 0)], [], [(0, 1, 2, 3)])
    fo = bpy.data.objects.new("Flag", flag)
    scene.collection.objects.link(fo)
    fo.location = centre + mdir * P["flag_dist"]
    fo.rotation_euler = (-mdir).to_track_quat("-Z", "Y").to_euler()
    # a reflection matte: only glossy and transmission rays see it, so the table stays lit
    fo.visible_camera = fo.visible_diffuse = fo.visible_shadow = fo.visible_volume_scatter = False
    black = bpy.data.materials.new("Flag Black")
    black.use_nodes = True
    black.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.01, 0.01, 0.01, 1)
    black.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
    flag.materials.append(black)
    # ring lights: rotate the mirror direction off-axis by ring_angle, then around it
    from mathutils import Matrix
    perp = mdir.cross(Vector((0, 0, 1))).normalized()
    for i, (ang, az) in enumerate(P["wedges"]):
        d = Matrix.Rotation(math.radians(az), 3, mdir) @ (Matrix.Rotation(math.radians(ang), 3, perp) @ mdir)
        # seen only in reflections, so they can be bright without flooding the table
        pos = centre + d * P["ring_dist"]
        arc = P["ring_dist"] * math.sin(math.radians(ang)) * math.radians(P["wedge_span"])
        radial = d - mdir * d.dot(mdir)  # away from the ring's centre line
        area(f"Wedge{i}", P["ring_power"], (arc, P["ring_width"]), tuple(pos),
             target=tuple(centre), diffuse=False, up=tuple(radial))

    # camera aimed at the case top, focus on an empty there
    focus = bpy.data.objects.new("Focus", None)
    scene.collection.objects.link(focus)
    focus.location = (0, 0, P["case_h"] * geometry.MM)
    el, az = math.radians(P["cam_elev"]), math.radians(P["cam_azim"])
    cd = bpy.data.cameras.new("Camera")
    cam = bpy.data.objects.new("Camera", cd)
    scene.collection.objects.link(cam)
    cam.location = focus.location + Vector((P["cam_dist"] * math.cos(el) * math.sin(az),
                                             -P["cam_dist"] * math.cos(el) * math.cos(az),
                                             P["cam_dist"] * math.sin(el)))
    cam.rotation_euler = (focus.location - cam.location).to_track_quat("-Z", "Y").to_euler()
    cd.lens, cd.clip_start, cd.clip_end = P["focal"], 0.005, 10
    cd.dof.use_dof, cd.dof.focus_object, cd.dof.aperture_fstop = True, focus, P["fstop"]
    scene.camera = cam

    c = scene.cycles
    c.max_bounces, c.transmission_bounces, c.glossy_bounces, c.volume_bounces = 32, 24, 12, 4
    c.transparent_max_bounces = 32
    c.blur_glossy = 0.5
    c.sample_clamp_indirect = 10.0
    c.use_denoising = True
    c.denoiser = "OPENIMAGEDENOISE"
    try:
        c.denoising_prefilter = "ACCURATE"
    except Exception:
        pass
    scene.view_settings.view_transform = P["view"]
    scene.view_settings.look = P["look"]
    scene.view_settings.exposure = P["exposure"]
    scene.render.resolution_x = P["res_x"]
    scene.render.resolution_y = P["res_y"]
    if P["clay"]:
        clay = bpy.data.materials.new("Clay")
        clay.use_nodes = True
        clay.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1)
        scene.view_layers[0].material_override = clay
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
        for img in bpy.data.images:  # the wear maps live in assets/ (not in git): pack them
            if img.filepath and "imperfections" in img.filepath and not img.packed_file:
                img.pack()
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        blend.with_suffix(".blend1").unlink(missing_ok=True)
    print("BUILD OK")
