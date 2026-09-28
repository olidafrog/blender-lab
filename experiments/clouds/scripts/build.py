"""clouds: a modular volumetric cloud system. Builds one preset scene, renders, saves.

Run from the repo root:
  tools/blender.sh experiments/clouds/scripts/build.py --set preset='"pink_rod"' --out v01
  ... --set key=value      override any value in P (after the preset is applied)
  ... --save               also save output/clouds.blend

Parts (each is one control node in the .blend):
  seed points (Python, tiers of lobes) → "Cloud Shape" geometry nodes → `density` grid
  "Cloud Material" shader group: albedo colour, density, phase, darkness
  "Neon" emission group for objects placed in the cloud
"""
import argparse
import ast
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from common import enable_gpu, experiment_paths  # noqa: E402
from nodes import auto_layout, how_to_tweak, material_from_group  # noqa: E402
from comp import LEGACY, compositor, post_group, use_saved_render  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "library" / "node-groups"))
from build_clouds import cloud_material_group, neon_group, seed_points, shape_group, volume_material  # noqa: E402

EXP = experiment_paths(__file__)

# Every value a designer might tune lives here. Override with --set key=value.
P = {
    "preset": "pink_rod",
    "res_x": 1400,
    "res_y": 1712,
    # --- cloud shape (seed tiers) ---
    "form": "puff",            # puff | cumulus | tower | plume
    "seed": 7,
    "size": 3.0,               # cloud width, m
    "aspect": (1.0, 0.8, 0.7), # x, y, z stretch of the main body
    "tiers": (14, 70, 500, 2500, 9000),  # lobes per tier, big → tiny puffs; each tier sits on the last
    "tier_radius": (0.26, 0.1, 0.042, 0.018, 0.009),  # lobe radius as a fraction of size
    "up_bias": 0.1,            # 0 = lobes all round, 1 = lobes only on top
    "base_soft": 0.4,          # m over which the flat base fades in
    "base_cut": -0.5,          # flat base height (fraction of size/2); -9 = off
    # --- Cloud Shape node (geometry nodes) ---
    "voxel": 0.007,            # m
    "smooth": 0,               # smoothing passes: fuses lobes
    "billow_scale": 9.0,       # 1/m, fine billow noise
    "billow": 0.0,             # billow noise strength
    "edge": 0.04,              # edge softness (0 crisp … 0.3 misty)
    # --- Cloud Material node ---
    "albedo": (1.0, 1.0, 1.0, 1.0),
    "density": 100.0,          # extinction per metre. Keep the free path (1/density) well under a lobe
    "darkness": 0.0,           # absorption 0..1 (smoke, storm)
    "droplet": 12.0,           # Mie droplet diameter µm; smaller = broader, softer forward glow
    "forward": 1.0,            # 1 = Mie (physical), 0 = isotropic
    # --- light ---
    "sun_elev": 35.0,          # degrees
    "sun_azim": -30.0,         # degrees, 0 = behind camera … 180 = behind cloud
    "sun_power": 15.0,
    "sun_color": (1.0, 0.9, 0.8, 1.0),
    "fill_power": 0.0,         # warm fill from opposite the sun, W/m²; ~4% of sun_power
    "fill_color": (1.0, 0.7, 0.65, 1.0),
    "sky": "gradient",         # gradient | physical | split (see world())
    "sky_top": (0.05, 0.14, 0.32, 1.0),
    "sky_bottom": (0.25, 0.37, 0.48, 1.0),
    "sky_light": 0.1,          # physical sky brightness (it is far brighter than a designed gradient)
    "sky_rot_offset": 90.0,    # physical sky: aligns its sun with the Sun lamp
    "air": 1.0,                # physical sky air density
    "aerosol": 1.0,            # physical sky haze; 2–5 = warmer, hazier dusk
    "sky_below": None,         # colour below the horizon; None = same as sky_bottom
    "sky_strength": 1.0,
    "sky_span": 0.35,          # sin(elevation) where the gradient reaches sky_top; ~ the frame's top edge
    "ground": False,
    "ground_color": (0.6, 0.62, 0.64, 1.0),
    # --- props in the cloud ---
    "prop": "rod",             # none | rod | ring
    "neon_color": (1.0, 0.35, 0.45, 1.0),
    "neon_strength": 800.0,
    "neon_radius": 0.012,      # m, tube radius
    "prop_offset": (0.05, -0.3, 0.02),    # prop position, fraction of size (y < 0 = toward camera)
    "rod_dir": (0.8, 0.1, -0.62),       # rod axis (x right, y away, z up)
    "ring_normal": (-0.3, -0.28, 0.91), # ring axis; near vertical = seen almost edge-on
    # --- camera / render ---
    "lens": 50.0,
    "cam_dist": 9.0,
    "cam_elev": 2.0,           # degrees
    "exposure": -1.0,
    "view": "Khronos PBR Neutral",            # AgX | Khronos PBR Neutral | Standard
    "look": "AgX - Base Contrast",
    "volume_bounces": 128,
    "grain": 0.03,
    "glow": 0.6,
    "glow_size": 0.35,          # 0..1 reach of the bloom
}

PRESETS = {
    # ref 02: pink popcorn cloud, neon rod, clear blue sky
    "pink_rod": dict(form="puff", base_cut=-9, sky_strength=2.0, albedo=(1.0, 0.66, 0.72, 1.0), prop="rod",
                     seed=11, aspect=(1.3, 1.0, 1.0), tiers=(3, 40, 400, 2500, 9000),
                     tier_radius=(0.26, 0.12, 0.045, 0.018, 0.009),
                     sun_elev=30, sun_azim=-60, sun_color=(1.0, 0.82, 0.66, 1.0), sky="gradient"),
    # ref 01: pink plume over white quarry, neon ring
    "pink_ring": dict(form="plume", base_cut=-9, aspect=(0.75, 0.75, 0.75), tiers=(16, 80, 600, 3000, 10000),
                      tier_radius=(0.2, 0.09, 0.04, 0.018, 0.009), seed=4, albedo=(1.0, 0.6, 0.7, 1.0),
                      prop="ring", neon_strength=500.0, edge=0.08, sky="gradient", sky_top=(0.5, 0.58, 0.68, 1.0), sky_bottom=(0.6, 0.64, 0.68, 1.0),
                      sky_strength=2.4, sun_power=2.0, sun_elev=35, sun_azim=-40, sun_color=(1.0, 0.92, 0.85, 1.0),
                      ground=True, ground_color=(0.5, 0.56, 0.6, 1.0), cam_elev=4, cam_dist=10, lens=45),
    # ref 03: lone cumulus at sunset
    "sunset": dict(form="cumulus", up_bias=0.5, aspect=(1.5, 0.6, 0.5), seed=5, tiers=(5, 60, 500, 2500, 9000),
                   tier_radius=(0.24, 0.1, 0.04, 0.018, 0.009), prop="none", sun_elev=4, sun_azim=85, base_cut=-0.35,
                   sky="split", sky_light=0.015, aerosol=1.5, fill_power=0.6,
                   sun_color=(1.0, 0.5, 0.25, 1.0), sun_power=14.0,
                   sky_top=(0.022, 0.097, 0.19, 1.0), sky_bottom=(0.127, 0.11, 0.125, 1.0),
                   sky_below=(0.03, 0.025, 0.045, 1.0), sky_strength=2.0,
                   sky_span=0.2, cam_dist=30, lens=85, cam_elev=-3),
    # ref 04: towering cumulonimbus
    "tower": dict(form="tower", up_bias=0.4, size=6.0, aspect=(1.0, 0.8, 1.3), tiers=(24, 120, 800, 4000, 14000), prop="none",
                  sun_elev=45, sun_azim=40, cam_dist=16, cam_elev=12, lens=35,
                  sky_top=(0.01, 0.03, 0.1, 1.0), sky_bottom=(0.1, 0.15, 0.25, 1.0)),
    # ref 05: plume lit from below by a hot source
    "plume": dict(form="plume", base_cut=-9, size=4.0, aspect=(0.8, 0.8, 1.6), tiers=(22, 100, 700, 3500, 12000), prop="lava",
                  sun_elev=30, sun_azim=-40, sun_power=6.0, darkness=0.002,
                  sky_top=(0.12, 0.13, 0.14, 1.0), sky_bottom=(0.2, 0.21, 0.22, 1.0), cam_dist=14, lens=40),
}

HOW_TO_TWEAK = """\
clouds — how to tweak

The cloud is a point cloud of lobes turned into a volume. Select "Cloud".

Shape — Modifier panel, "Cloud Shape" node:
- Voxel Size (m): detail vs speed. 0.007 shows the tiny puffs; 0.02 previews fast.
- Smooth (0–8): fuses lobes. 0 = crisp popcorn, 2+ = soft blobs.
- Edge (0.005–0.5): silhouette softness. 0.04 crisp cumulus, 0.1+ smoke, 0.3 mist.
- Base Height (m) / Base Softness (m): flat, slightly ragged cloud base.
  Set Base Height to -100 for no base (puffs, plumes).
- Billow Scale / Billow: extra noise on the surface; small effect, keep Billow low.
The lobes themselves are the Cloud mesh's vertices, each with a 'radius'. In Edit Mode,
move or delete vertices to re-shape it. For a new random cloud, rebuild with
--set seed=N (and tiers / tier_radius / aspect for lobe counts, sizes and proportions).

Look — Shader Editor, "Cloud Material" node:
- Colour: how the lit cloud should look. It is converted to albedo, so colour deepens
  in the core and shadows by itself. Go paler than you think.
- Density (per m): 100 = crisp cumulus. Lower (20–40) = soft, see-through, lobes blur.
- Darkness (0–1): absorption. 0 = water cloud, 0.002 = steam, 0.05+ = smoke.
- Droplet (µm, 5–50): the Mie forward glow. Smaller = softer silver lining.
- Forward (0–1): 1 = physical Mie, 0 = flat isotropic (brighter, whiter).

Light:
- "Sun": rotate it. Its colour and strength set the key. "Fill" (sunset only): warm
  bounce from the far side, ~4% of the Sun.
- World: a designed gradient sky. Sunset uses "split": the camera sees the gradient,
  the cloud is also lit by the physical sky at low strength.

Objects in the cloud — "Neon" node (Colour, Strength). Move the Rod or Ring anywhere.
It lights the cloud from inside; it shows through only within ~0.3 m of the surface.
Emitters do not cast shadows.

Post — Compositing tab, "Post" node: Glow, Grain. After a new render (F12), set
"Source" to Off.

Presets: rebuild with --set preset='"pink_rod"' | '"pink_ring"' | '"sunset"' |
'"tower"' | '"plume"'. Built by experiments/clouds/scripts/build.py. Changes made here
are lost on rebuild; copy good values back into P.
"""


# ---------------------------------------------------------------- seed points

# ---------------------------------------------------------------- scene

def add_props(scene, cloud_centre):
    kind = P["prop"]
    if kind == "none":
        return
    mat = material_from_group("Neon", neon_group(P))
    s = P["size"]
    if kind == "rod":
        bpy.ops.mesh.primitive_cylinder_add(radius=P["neon_radius"], depth=s * 2.2, vertices=24,
                                            location=cloud_centre + Vector(P["prop_offset"]) * s)
        o = bpy.context.active_object
        o.rotation_euler = Vector(P["rod_dir"]).to_track_quat("Z", "Y").to_euler()
    elif kind == "ring":
        bpy.ops.mesh.primitive_torus_add(major_radius=s * 0.62, minor_radius=P["neon_radius"],
                                         major_segments=256, minor_segments=16, location=cloud_centre)
        o = bpy.context.active_object
        o.rotation_euler = Vector(P["ring_normal"]).to_track_quat("Z", "Y").to_euler()
    elif kind == "lava":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=s * 0.22, location=cloud_centre + Vector((0, 0, -s * 0.95)))
        o = bpy.context.active_object
        o.scale = (1.6, 1.2, 0.35)
        mat.node_tree.nodes[0].inputs["Colour"].default_value = (1.0, 0.18, 0.04, 1.0)
        mat.node_tree.nodes[0].inputs["Strength"].default_value = 25.0
    o.name = kind.capitalize()
    o.visible_shadow = False  # an emitter should light, not shade
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()


def world(scene):
    """sky = gradient: the designed gradient lights and shows.
    sky = physical: the physical sky (Belt of Venus, warm horizon) lights and shows.
    sky = split: the camera sees the gradient; the cloud is lit by gradient + physical sky."""
    w = bpy.data.worlds.new("Sky")
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    bg.inputs["Strength"].default_value = P["sky_strength"]
    phys = grad = None
    if P["sky"] in ("physical", "split"):
        sky = nt.nodes.new("ShaderNodeTexSky")
        sky.sky_type = "MULTIPLE_SCATTERING"
        sky.sun_disc = False
        sky.sun_elevation = math.radians(P["sun_elev"])
        sky.sun_rotation = math.radians(P["sun_azim"] + P["sky_rot_offset"])
        sky.air_density, sky.aerosol_density = P["air"], P["aerosol"]
        k = nt.nodes.new("ShaderNodeMix")
        k.data_type, k.blend_type = "RGBA", "MULTIPLY"
        k.inputs[0].default_value = 1.0
        nt.links.new(sky.outputs[0], k.inputs[6])
        k.inputs[7].default_value = (P["sky_light"],) * 3 + (1.0,)
        phys = k.outputs[2]
    if P["sky"] in ("gradient", "split"):
        # vertical gradient by view elevation: sky_below → sky_bottom (horizon) → sky_top
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(geo.outputs["Incoming"], sep.inputs[0])
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = P["sky_span"]    # Incoming points back to the camera
        mr.inputs["From Max"].default_value = -P["sky_span"]
        nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        e = ramp.color_ramp.elements
        e[0].position, e[0].color = 0.0, P["sky_below"] or P["sky_bottom"]
        e[1].position, e[1].color = 1.0, P["sky_top"]
        mid = e.new(0.5)
        mid.color = P["sky_bottom"]
        nt.links.new(mr.outputs[0], ramp.inputs[0])
        grad = ramp.outputs[0]
    if phys and grad:
        lp = nt.nodes.new("ShaderNodeLightPath")
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
        both = nt.nodes.new("ShaderNodeMix")          # light rays: gradient + physical sky
        both.data_type, both.blend_type, both.clamp_factor = "RGBA", "ADD", False
        both.inputs[0].default_value = 1.0
        nt.links.new(grad, both.inputs[6])
        nt.links.new(phys, both.inputs[7])
        nt.links.new(both.outputs[2], mix.inputs[6])
        nt.links.new(grad, mix.inputs[7])
        nt.links.new(mix.outputs[2], bg.inputs["Color"])
    else:
        nt.links.new(phys or grad, bg.inputs["Color"])
    scene.world = w


def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    enable_gpu(scene)

    me = seed_points(P)
    cloud = bpy.data.objects.new("Cloud", me)
    scene.collection.objects.link(cloud)
    mod = cloud.modifiers.new("Cloud Shape", "NODES")
    mat = volume_material("Cloud", cloud_material_group(P))
    me.materials.append(mat)
    mod.node_group = shape_group(mat, P)
    centre = Vector((0, 0, 0))
    add_props(scene, centre)

    if P["ground"]:
        bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, -P["size"] * 0.9))
        g = bpy.context.active_object
        g.name = "Ground"
        gm = bpy.data.materials.new("Ground")
        gm.use_nodes = True
        b = gm.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = P["ground_color"]
        b.inputs["Roughness"].default_value = 0.95
        g.data.materials.append(gm)

    sun = bpy.data.lights.new("Sun", "SUN")
    sun.energy = P["sun_power"]
    sun.color = P["sun_color"][:3]
    sun.angle = math.radians(0.53)
    so = bpy.data.objects.new("Sun", sun)
    scene.collection.objects.link(so)
    # the sun shines along its -Z. Azimuth 0 = light comes from behind the camera.
    el, az = math.radians(P["sun_elev"]), math.radians(P["sun_azim"])
    to_sun = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    so.rotation_euler = to_sun.to_track_quat("Z", "Y").to_euler()
    if P["fill_power"] > 0:  # warm low fill from the side away from the sun (sky glow, ground bounce)
        fill = bpy.data.lights.new("Fill", "SUN")
        fill.energy, fill.color, fill.angle = P["fill_power"], P["fill_color"][:3], math.radians(30)
        fo = bpy.data.objects.new("Fill", fill)
        scene.collection.objects.link(fo)
        faz = az + math.pi
        to_fill = Vector((math.sin(faz) * math.cos(0.1), -math.cos(faz) * math.cos(0.1), math.sin(0.1)))
        fo.rotation_euler = to_fill.to_track_quat("Z", "Y").to_euler()
    world(scene)

    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    scene.collection.objects.link(cam)
    cam.data.lens = P["lens"]
    ce = math.radians(P["cam_elev"])
    cam.location = (0, -P["cam_dist"] * math.cos(ce), P["cam_dist"] * math.sin(ce))
    cam.rotation_euler = (centre - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam

    scene.render.resolution_x = P["res_x"]
    scene.render.resolution_y = P["res_y"]
    c = scene.cycles
    c.volume_bounces = P["volume_bounces"]
    c.max_bounces = max(P["volume_bounces"], 16)
    c.transparent_max_bounces = 16
    c.use_denoising = True
    scene.view_settings.view_transform = P["view"]
    if P["view"] == "AgX":
        scene.view_settings.look = P["look"]
    scene.view_settings.exposure = P["exposure"]
    how_to_tweak(HOW_TO_TWEAK)
    return scene


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
    sets = {}
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in P:
            sys.exit(f"unknown P key: {k}")
        sets[k] = ast.literal_eval(v)
    preset = sets.get("preset", P["preset"])
    P.update(PRESETS[preset])
    P["preset"] = preset
    P.update(sets)
    return a


def post():
    """Compositor controls on one node. Tab into it in Blender to see the parts."""
    ng, gi, go = post_group("Post", [
        ("Glow", "NodeSocketFloat", P["glow"], 0.0, 2.0),
        ("Grain", "NodeSocketFloat", P["grain"], 0.0, 0.2),
    ])
    glare = ng.nodes.new("CompositorNodeGlare")
    ng.links.new(gi.outputs["Image"], glare.inputs["Image"])
    glare.inputs["Type"].default_value = "Fog Glow"
    glare.inputs["Threshold"].default_value = 1.0
    glare.inputs["Size"].default_value = P["glow_size"]
    ng.links.new(gi.outputs["Glow"], glare.inputs["Strength"])
    # grain: white noise on pixel coordinates, centred on 0, scaled by Grain
    coords = ng.nodes.new("CompositorNodeImageCoordinates")
    noise = ng.nodes.new("ShaderNodeTexWhiteNoise")
    noise.noise_dimensions = "2D"
    ng.links.new(coords.outputs["Pixel"], noise.inputs["Vector"])
    centred = ng.nodes.new("ShaderNodeMath")
    centred.operation = "SUBTRACT"
    ng.links.new(noise.outputs["Value"], centred.inputs[0])
    centred.inputs[1].default_value = 0.5
    amt = ng.nodes.new("ShaderNodeMath")
    amt.operation = "MULTIPLY"
    ng.links.new(centred.outputs[0], amt.inputs[0])
    ng.links.new(gi.outputs["Grain"], amt.inputs[1])
    add = ng.nodes.new("ShaderNodeMix")
    add.data_type = "RGBA"
    add.blend_type = "ADD"
    add.clamp_factor = False
    add.inputs[0].default_value = 1.0
    ng.links.new(glare.outputs["Image"], add.inputs[6])
    ng.links.new(amt.outputs[0], add.inputs[7])
    ng.links.new(add.outputs[2], go.inputs["Image"])
    auto_layout(ng)
    return ng


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
