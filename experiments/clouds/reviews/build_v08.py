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
import random
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from common import enable_gpu, experiment_paths  # noqa: E402
from nodes import auto_layout, group, how_to_tweak, material_from_group, use  # noqa: E402
from comp import LEGACY, compositor, post_group, use_saved_render  # noqa: E402

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
    "base_cut": -0.5,          # flatten below this height (fraction of size/2); -9 = off
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
    "sky": "gradient",         # gradient | physical
    "sky_top": (0.05, 0.14, 0.32, 1.0),
    "sky_bottom": (0.25, 0.37, 0.48, 1.0),
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
    "pink_ring": dict(form="puff", base_cut=-9, sky_strength=2.0, aspect=(0.75, 0.75, 1.1), albedo=(1.0, 0.45, 0.6, 1.0), prop="ring",
                      sky="gradient", sky_top=(0.55, 0.62, 0.72, 1.0), sky_bottom=(0.62, 0.66, 0.7, 1.0),
                      sun_power=5.0, sun_elev=15, sun_azim=60, ground=True, cam_elev=6),
    # ref 03: lone cumulus at sunset
    "sunset": dict(form="cumulus", up_bias=0.5, aspect=(1.0, 0.45, 0.32), tiers=(26, 90, 500, 2500, 9000),
                   tier_radius=(0.15, 0.08, 0.04, 0.018, 0.009), prop="none", sun_elev=8, sun_azim=60,
                   sun_color=(1.0, 0.55, 0.3, 1.0), sun_power=10.0,
                   sky_top=(0.022, 0.097, 0.19, 1.0), sky_bottom=(0.127, 0.11, 0.125, 1.0), sky_strength=2.0,
                   sky_span=0.2, cam_dist=40, lens=85, cam_elev=-3),
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

The cloud is three parts. Select "Cloud".
- Shape: Modifier panel, "Cloud Shape" node inputs: Voxel Size (detail vs speed),
  Smooth (fuse lobes), Billow Scale / Billow (small puffs), Edge (crisp → misty).
  The lobes themselves are the vertices of the Cloud mesh (a 'radius' attribute each).
  Move, add or delete vertices in Edit Mode to re-shape the cloud.
- Look: Shader Editor, "Cloud Material" node: Colour (albedo — pale colours saturate
  with depth, so go paler than you think), Density (how thick: 5 soft, 20 cumulus,
  60 storm), Darkness (smoke), Droplet (µm; smaller = softer silver lining),
  Forward (1 physical, 0 flat).
- Neon props: "Neon" node: Colour and Strength. Move the Rod/Ring freely through the cloud;
  it lights the cloud from inside.
- Sun: select "Sun"; rotate it. Sky: World shader.
- Post: Compositing tab, "Post" node (Glow, Grain). After a new render (F12), set
  "Source" to Off.

Built by experiments/clouds/scripts/build.py. Changes made here are lost on rebuild;
copy good values back into P.
"""


# ---------------------------------------------------------------- seed points

def _sphere_dir(rng, up_bias):
    while True:
        d = Vector((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1)))
        if d.length < 1e-6:
            continue
        d.normalize()
        if rng.random() < (1 - up_bias) + up_bias * max(0.0, d.z) * 1.5:
            return d


def _body(rng, form, n, r, asp, size):
    """Tier-0 lobe centres for each cloud form, in metres."""
    h = size / 2
    pts = []
    for i in range(n):
        if form == "tower":
            t = i / max(1, n - 1)                                  # stacked turrets, widening up
            z = (-0.8 + 1.9 * t) * h * asp[2]
            spread = h * (0.45 + 0.35 * t)
            pts.append(Vector((rng.gauss(0, spread * 0.5) * asp[0], rng.gauss(0, spread * 0.4) * asp[1], z)))
        elif form == "plume":
            t = rng.random()
            z = (-1.0 + 2.0 * t) * h * asp[2]
            spread = h * (0.15 + 0.55 * t)
            pts.append(Vector((rng.gauss(0, spread * 0.45), rng.gauss(0, spread * 0.45), z)))
        else:                                                      # puff, cumulus: a row of big lobes
            t = (i + 0.5) / n * 2 - 1 + rng.uniform(-0.5, 0.5) / n  # spread evenly along x
            pts.append(Vector((t * (h - r) * asp[0], rng.gauss(0, 0.25) * (h - r) * asp[1],
                               rng.gauss(0, 0.3) * (h - r) * asp[2])))
    return pts


def seed_points():
    rng = random.Random(P["seed"])
    size, asp = P["size"], P["aspect"]
    radii = [f * size for f in P["tier_radius"]]
    cut = P["base_cut"] * size / 2
    centres, rads = [], []
    for c in _body(rng, P["form"], P["tiers"][0], radii[0], asp, size):
        s = 1.0 + (0.35 * (c.z / (size / 2)) if P["form"] == "tower" else 0.0)
        centres.append(c)
        rads.append(radii[0] * rng.uniform(0.7, 1.25) * s)
    # Each finer tier sits on the exposed skin of everything so far, so it covers the
    # whole surface (lobes on lobes on lobes), not just the previous tier.
    C = np.array([tuple(c) for c in centres])
    R = np.array(rads)
    for tier in range(1, len(P["tiers"])):
        want, tries = P["tiers"][tier], 0
        added = 0
        cdf = np.cumsum(R ** 2)                # pick parents by surface area
        while added < want and tries < want * 40:
            tries += 1
            i = min(int(np.searchsorted(cdf, rng.random() * cdf[-1])), len(cdf) - 1)
            r = radii[tier] * rng.uniform(0.6, 1.4)
            d = _sphere_dir(rng, P["up_bias"])
            p = np.array(C[i]) + np.array(d) * R[i] * rng.uniform(0.85, 1.0)
            if p[2] < cut:
                continue
            gap = np.linalg.norm(C - p, axis=1) - R
            gap[i] = 0.0
            if gap.min() < -0.25 * r:          # buried inside another lobe
                continue
            C = np.vstack([C, p])
            R = np.append(R, r)
            added += 1
    centres = [Vector(c) for c in C]
    rads = list(R)
    if cut > -9:  # flat base: pull lobes below the cut up to it and shrink them
        for i, c in enumerate(centres):
            if c.z - rads[i] < cut:
                rads[i] = max(rads[i] * 0.5, c.z - cut + rads[i] * 0.35)
    me = bpy.data.meshes.new("Cloud")
    me.from_pydata([tuple(c) for c in centres], [], [])
    a = me.attributes.new("radius", "FLOAT", "POINT")
    a.data.foreach_set("value", rads)
    print(f"[out] seed points {len(centres)}")
    return me


# ---------------------------------------------------------------- Cloud Shape (GN)

def shape_group(material):
    ng, gi, go = group("Cloud Shape", [
        ("Geometry", "NodeSocketGeometry", None, None, None),
        ("Voxel Size", "NodeSocketFloat", P["voxel"], 0.004, 0.2),
        ("Smooth", "NodeSocketInt", P["smooth"], 0, 8),
        ("Billow Scale", "NodeSocketFloat", P["billow_scale"], 0.5, 60.0),
        ("Billow", "NodeSocketFloat", P["billow"], 0.0, 1.0),
        ("Edge", "NodeSocketFloat", P["edge"], 0.005, 0.5),
    ], [("Geometry", "NodeSocketGeometry")], kind="GeometryNodeTree")
    N, L = ng.nodes, ng.links

    def node(t, **ins):
        x = N.new(t)
        for k, v in ins.items():
            if hasattr(v, "bl_rna"):
                L.new(v, x.inputs[k])
            else:
                x.inputs[k].default_value = v
        return x

    def m(op, a, b=None, c=None):
        x = N.new("ShaderNodeMath")
        x.operation = op
        for i, v in enumerate((a, b, c)):
            if v is None:
                continue
            if hasattr(v, "bl_rna"):
                L.new(v, x.inputs[i])
            else:
                x.inputs[i].default_value = v
        return x.outputs[0]

    rad = N.new("GeometryNodeInputNamedAttribute")
    rad.data_type = "FLOAT"
    rad.inputs["Name"].default_value = "radius"
    pts = node("GeometryNodeMeshToPoints", Mesh=gi.outputs["Geometry"], Radius=rad.outputs[0])
    vol = node("GeometryNodePointsToVolume", Points=pts.outputs[0], Radius=rad.outputs[0],
               **{"Voxel Size": gi.outputs["Voxel Size"]})
    vol.inputs["Resolution Mode"].default_value = "Size"
    raw = node("GeometryNodeGetNamedGrid", Volume=vol.outputs[0], Name="density")
    # room for billows and the soft edge outside the lobes
    dil = node("GeometryNodeGridDilateAndErode", Grid=raw.outputs["Grid"], Steps=8)
    mean = node("GeometryNodeGridMean", Grid=dil.outputs[0], Width=2, Iterations=gi.outputs["Smooth"])
    f2g = N.new("GeometryNodeFieldToGrid")
    f2g.data_type = "FLOAT"
    f2g.grid_items.new("FLOAT", "density")
    L.new(dil.outputs[0], f2g.inputs["Topology"])
    pos = N.new("GeometryNodeInputPosition")
    smp = node("GeometryNodeSampleGrid", Grid=mean.outputs[0], Position=pos.outputs[0])
    # billows: rounded cells (1 - Voronoi F1) at two scales, plus noise to break the cells
    v1 = node("ShaderNodeTexVoronoi", Vector=pos.outputs[0], Scale=gi.outputs["Billow Scale"])
    v2 = node("ShaderNodeTexVoronoi", Vector=pos.outputs[0], Scale=m("MULTIPLY", gi.outputs["Billow Scale"], 2.3))
    nz = node("ShaderNodeTexNoise", Vector=pos.outputs[0], Scale=m("MULTIPLY", gi.outputs["Billow Scale"], 0.4), Detail=3.0)
    b = m("ADD", m("MULTIPLY", m("SUBTRACT", 1.0, v1.outputs["Distance"]), 0.6),
          m("MULTIPLY", m("SUBTRACT", 1.0, v2.outputs["Distance"]), 0.25))
    b = m("ADD", b, m("MULTIPLY", nz.outputs["Fac"], 0.3))
    field = m("MULTIPLY_ADD", m("SUBTRACT", b, 0.72), gi.outputs["Billow"], smp.outputs["Value"])
    mr = N.new("ShaderNodeMapRange")
    L.new(field, mr.inputs["Value"])
    L.new(m("SUBTRACT", 0.5, gi.outputs["Edge"]), mr.inputs["From Min"])
    L.new(m("ADD", 0.5, gi.outputs["Edge"]), mr.inputs["From Max"])
    # smoothstep-ish: square the ramp so the edge fades in softly and the core is solid
    L.new(m("POWER", mr.outputs[0], 1.5), f2g.inputs["density"])
    store = N.new("GeometryNodeStoreNamedGrid")
    store.data_type = "FLOAT"
    store.inputs["Name"].default_value = "density"   # Cycles only rendered a grid named density
    # Field to Grid leaves a non-zero background: Cycles then fills the whole bounding box
    bg = node("GeometryNodeSetGridBackground", Grid=f2g.outputs["density"])
    L.new(bg.outputs[0], store.inputs["Grid"])
    # the volume made here carries no material: without this Cycles renders default grey smoke
    setm = node("GeometryNodeSetMaterial", Geometry=store.outputs[0])
    setm.inputs["Material"].default_value = material
    L.new(setm.outputs[0], go.inputs["Geometry"])
    auto_layout(ng)
    return ng


# ---------------------------------------------------------------- Cloud Material

def math_node(ng, op, a, b=None, c=None):
    x = ng.nodes.new("ShaderNodeMath")
    x.operation = op
    for i, v in enumerate((a, b, c)):
        if v is None:
            continue
        if hasattr(v, "bl_rna"):
            ng.links.new(v, x.inputs[i])
        else:
            x.inputs[i].default_value = v
    return x.outputs[0]


def cloud_material_group():
    ng, gi, go = group("Cloud Material", [
        ("Colour", "NodeSocketColor", P["albedo"], None, None),
        ("Density", "NodeSocketFloat", P["density"], 0.0, 200.0),
        ("Darkness", "NodeSocketFloat", P["darkness"], 0.0, 1.0),
        ("Droplet", "NodeSocketFloat", P["droplet"], 5.0, 50.0),
        ("Forward", "NodeSocketFloat", P["forward"], 0.0, 1.0),
    ], [("Volume", "NodeSocketShader")])
    N, L = ng.nodes, ng.links
    att = N.new("ShaderNodeAttribute")
    att.attribute_type, att.attribute_name = "GEOMETRY", "density"
    dens = N.new("ShaderNodeMath")
    dens.operation = "MULTIPLY"
    L.new(att.outputs["Fac"], dens.inputs[0])
    L.new(gi.outputs["Density"], dens.inputs[1])
    mie = N.new("ShaderNodeVolumeScatter")
    mie.phase = "MIE"
    iso = N.new("ShaderNodeVolumeScatter")
    iso.phase = "HENYEY_GREENSTEIN"
    iso.inputs["Anisotropy"].default_value = 0.0
    # Colour is how the lit cloud should look. Many bounces compound the albedo, so invert
    # the multiple-scattering albedo per channel (Christensen & Burley 2015):
    # a = 1 - (4.09712 + 4.20863 C - sqrt(9.59217 + 41.6808 C + 17.7126 C^2))^2
    sep = N.new("ShaderNodeSeparateColor")
    L.new(gi.outputs["Colour"], sep.inputs[0])
    comb = N.new("ShaderNodeCombineColor")
    for ch in range(3):
        c = sep.outputs[ch]
        root = math_node(ng, "SQRT", math_node(ng, "ADD", 9.59217, math_node(ng, "ADD",
               math_node(ng, "MULTIPLY", c, 41.6808),
               math_node(ng, "MULTIPLY", math_node(ng, "MULTIPLY", c, c), 17.7126))))
        t = math_node(ng, "SUBTRACT", math_node(ng, "MULTIPLY_ADD", c, 4.20863, 4.09712), root)
        L.new(math_node(ng, "SUBTRACT", 1.0, math_node(ng, "MULTIPLY", t, t)), comb.inputs[ch])
    for sc in (mie, iso):
        L.new(dens.outputs[0], sc.inputs["Density"])
    L.new(gi.outputs["Droplet"], mie.inputs["Diameter"])
    mix = N.new("ShaderNodeMixShader")
    L.new(gi.outputs["Forward"], mix.inputs[0])
    L.new(iso.outputs[0], mix.inputs[1])
    L.new(mie.outputs[0], mix.inputs[2])
    ab = N.new("ShaderNodeVolumeAbsorption")
    ab.inputs["Color"].default_value = (0.0, 0.0, 0.0, 1.0)
    adens = N.new("ShaderNodeMath")
    adens.operation = "MULTIPLY"
    L.new(dens.outputs[0], adens.inputs[0])
    L.new(gi.outputs["Darkness"], adens.inputs[1])
    L.new(adens.outputs[0], ab.inputs["Density"])
    # Scatter Color alone only changes each channel's free path (the cloud stays white and
    # its shadows go complementary). Albedo needs absorption of 1 - albedo at the same density.
    tint = N.new("ShaderNodeVolumeAbsorption")
    L.new(comb.outputs[0], tint.inputs["Color"])
    L.new(dens.outputs[0], tint.inputs["Density"])
    add = N.new("ShaderNodeAddShader")
    L.new(mix.outputs[0], add.inputs[0])
    L.new(ab.outputs[0], add.inputs[1])
    add2 = N.new("ShaderNodeAddShader")
    L.new(add.outputs[0], add2.inputs[0])
    L.new(tint.outputs[0], add2.inputs[1])
    L.new(add2.outputs[0], go.inputs["Volume"])
    auto_layout(ng)
    return ng


def neon_group():
    ng, gi, go = group("Neon", [
        ("Colour", "NodeSocketColor", P["neon_color"], None, None),
        ("Strength", "NodeSocketFloat", P["neon_strength"], 0.0, 5000.0),
    ], [("Shader", "NodeSocketShader")])
    em = ng.nodes.new("ShaderNodeEmission")
    ng.links.new(gi.outputs["Colour"], em.inputs["Color"])
    ng.links.new(gi.outputs["Strength"], em.inputs["Strength"])
    ng.links.new(em.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def volume_material(name, ng):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    g = use(nt, ng)
    g.width = 260
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (360, 0)
    nt.links.new(g.outputs["Volume"], out.inputs["Volume"])
    return m


# ---------------------------------------------------------------- scene

def add_props(scene, cloud_centre):
    kind = P["prop"]
    if kind == "none":
        return
    mat = material_from_group("Neon", neon_group())
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
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()


def world(scene):
    w = bpy.data.worlds.new("Sky")
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    bg.inputs["Strength"].default_value = P["sky_strength"]
    if P["sky"] == "physical":
        sky = nt.nodes.new("ShaderNodeTexSky")
        sky.sky_type = "MULTIPLE_SCATTERING"
        sky.sun_disc = False
        sky.sun_elevation = math.radians(P["sun_elev"])
        sky.sun_rotation = math.radians(P["sun_azim"] + 90)
        nt.links.new(sky.outputs[0], bg.inputs["Color"])
    else:
        # vertical gradient by view direction: bottom at the horizon, top at 60°
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(geo.outputs["Incoming"], sep.inputs[0])
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = 0.0
        mr.inputs["From Max"].default_value = -P["sky_span"]  # Incoming points back to the camera
        nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        nt.links.new(mr.outputs[0], mix.inputs[0])
        mix.inputs[6].default_value = P["sky_bottom"]
        mix.inputs[7].default_value = P["sky_top"]
        nt.links.new(mix.outputs[2], bg.inputs["Color"])
    scene.world = w


def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    enable_gpu(scene)

    me = seed_points()
    cloud = bpy.data.objects.new("Cloud", me)
    scene.collection.objects.link(cloud)
    mod = cloud.modifiers.new("Cloud Shape", "NODES")
    mat = volume_material("Cloud", cloud_material_group())
    me.materials.append(mat)
    mod.node_group = shape_group(mat)
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
