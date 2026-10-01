"""aztechno-building: Freddy Mamani's Crucero del Sur (El Alto) as a photoreal architectural render.

The facade is traced in reference pixels (scripts/facade.py) and built at true scale (P["ppm"] px per
metre at the facade plane): every moulding is a filled 2D curve with holes, extruded to its depth and
round-bevelled, so the sun casts real shadows. Sky: 5.x multiple-scattering Sky Texture at El Alto's
altitude, with a matching Sun lamp. Camera: level, shift lens, framed so the facade plane lands on the
reference's pixels.

Run from the repo root:
  tools/blender.sh experiments/aztechno-building/scripts/build.py --out v01 --samples 128 --scale 0.5
  ... --set key=value      override any value in P
  ... --save               also save output/aztechno-building.blend
  ... --preflight          no render: the correctness sheet to reviews/preflight_<out>.png
"""
import argparse
import ast
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
sys.path.insert(0, str(HERE))
from common import enable_gpu, experiment_paths  # noqa: E402
from nodes import auto_layout, group, how_to_tweak, material_from_group, use  # noqa: E402
from comp import LEGACY, compositor, post_group, use_saved_render  # noqa: E402
from preflight import sheet  # noqa: E402
import facade as F  # noqa: E402

EXP = experiment_paths(__file__)
TEX = EXP["assets"] / "textures"

P = {
    "res_x": 1400, "res_y": 979,
    "ppm": 38.0,                # reference px per metre on the facade plane
    "cam_d": 24.0,              # camera distance from the facade (m)
    "cam_h": 9.0,               # camera height (m)
    "cam_x": 0.0,               # camera offset from the facade axis (m)
    "sun_elev": 35.0,           # degrees above the horizon
    "sun_az": 45.0,             # degrees from the facade normal, + = from the camera's right
    "sun_strength": 135.0,      # W/m^2, Blender units (the sky model's own disc is ~138 at 4000 m)
    "sun_angle": 0.53,          # apparent sun diameter, degrees
    "sky_strength": 1.5,
    "sky_grad": 0.55,           # camera-ray sky darkens toward the top of the frame (grad filter / polariser)
    "sky_sat": 0.7,             # saturation of the sky the camera sees (the photo's sky is hazier)
    "sky_air": 2.0, "sky_aerosol": 1.0, "sky_ozone": 1.0,   # air 2 = the photo's paler blue
    "sky_view": 3.0,            # sky x this for camera and glossy rays (the photo's sky exposure)
    "film_exposure": 0.043,     # 2^-5: linear, before the compositor (research: no glare veil)
    "altitude": 4000.0,         # El Alto, metres
    "sky_rot_fix": 0.0,
    "clouds": 0.8, "cloud_angle": 35.0, "cloud_seed": 2.0,   # cirrus seen by the camera and in glass
    "walk": 2.9,                # sidewalk depth (m)
    "exposure": 0.0,
    "view": "Khronos PBR Neutral",
    "look": "None",
    # paint albedo (linear)
    "red": (0.55, 0.035, 0.045, 1), "orange": (0.66, 0.19, 0.08, 1), "yellow": (0.80, 0.66, 0.22, 1),
    "cream": (0.72, 0.68, 0.50, 1), "white": (0.78, 0.77, 0.72, 1),
    "gf_cream": (0.70, 0.57, 0.40, 1), "gf_base": (0.42, 0.10, 0.06, 1), "gf_stripe": (0.66, 0.24, 0.09, 1),
    "tank": (0.62, 0.26, 0.20, 1),
    "paint_rough": 0.62, "paint_var": 0.6, "grime": 0.3, "chalk": 0.15,
    "base_dirt": 0.35,          # splash zone: dirt fading up to ~0.8 m on ground-floor walls
    # glass
    "glass_tint": (0.012, 0.010, 0.008, 1), "glass_refl": 0.35, "glass_rough": 0.02, "glass_wobble": 0.5,
    "glass_see": 0.0,           # thin-wall transmission; 0 = opaque coated glass (v05, won the calibration)
    "sky_glossy": False,        # also lift the sky for glossy rays (v06-v07 float-glass mechanism)
    "mullion": (0.20, 0.15, 0.08, 1),
    "wing_y1": -0.8, "wing_y2": -2.0,  # depth (m) of the left wing far edges (u 118, u 47); negative = toward the street (the reference lights its cream pier, so it faces the sun)
    "interior": 0.18,           # albedo of the rooms behind the glass
    "context": True,            # opposite street, only in reflections
    "glow": 0.0, "glow_size": 0.35, "glow_threshold": 1.5, "chroma": 0.0,     # post off until it earns its place
    "relief": 2.8,
    "layer_step": 0.018,        # each outline layer of a moulding sits this far behind the next              # depth multiplier for every moulding (1 = the traced depths)
    "tank_y": 3.0,              # roof tanks, metres behind the facade
    "supersample": 2,           # photographic output stage (fork): render at 2x, Lanczos down,
    "sharpen_px": 1.0, "sharpen_pct": 40, "jpeg_q": 85,   # unsharp mask, JPEG round trip
    "brick_scale": 1.7, "brick_tint": (0.95, 0.85, 0.85, 1), "brick_sat": 0.45,   # pale hollow brick
    "refl_hdri": "construction_yard_4k.hdr",   # "" = reflections see the modelled street and sky
    "refl_hdri_rot": 300.0, "refl_hdri_gain": 20.0,
    "refl_hdri_pitch": -12.0,    # tip the photo down: shot at 1.7 m, the windows are 12-17 m up
    "diamond_px": 30.0, "diamond_y": 0.45,   # gem width in reference px; its centre, m proud of the wall
    "clay": False,
}

HOW_TO_TWEAK = """\
aztechno-building — how to tweak

Each material is one node: select an object, open the Shader Editor, change the inputs on its group
node (hover an input for its range). Paint colours: the "Paint" node on each paint material.
Glass: the "Curtain Glass" node. Sun: the "Sun" lamp (rotation, strength) and the World's Sky node
(same sun angles; keep them together). Post: Compositing tab, "Post" node.

Built by experiments/aztechno-building/scripts/build.py. Changes made here are lost on rebuild;
copy good values back into P.
"""

# ---------------------------------------------------------------- coordinates


def X(u):
    return (u - F.AXIS) / P["ppm"]


def Z(v):
    return (F.GROUND - v) / P["ppm"]


def at_depth(u, v, y):
    """World (x, z) of a point at depth y (m behind the facade plane, + away from the camera) that lands
    on reference pixel (u, v): for parts set back from the facade (roof tanks, far wings)."""
    k = (P["cam_d"] + y) / P["cam_d"]
    u_axis = F.AXIS + P["cam_x"] * P["ppm"]
    v_h = F.GROUND - P["cam_h"] * P["ppm"]
    return P["cam_x"] + (u - u_axis) / P["ppm"] * k, P["cam_h"] + (v_h - v) / P["ppm"] * k


def link(ob, coll=None):
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def coll(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


# ---------------------------------------------------------------- geometry builders

_mesh_cache = []


def slab(name, loops_px, d0, d1, mat, bev=0.01, collection=None):
    """Filled 2D outline (outer + holes, in px) extruded from depth d0 to d1 (m, toward the street),
    round-bevelled, converted to a mesh."""
    bad = [i for i, lp in enumerate(loops_px) if not F.simple_polygon(lp)]
    assert not bad, f"{name}: self-intersecting loop(s) {bad}"
    bev = max(0.0, min(bev, (d1 - d0) / 2 - 0.002))
    bpx = bev * P["ppm"]
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    for i, lp in enumerate(loops_px):
        lp = F.offset(lp, -bpx if i == 0 else bpx) if bpx > 0.05 else lp
        sp = cu.splines.new("POLY")
        sp.points.add(len(lp) - 1)
        for p, (u, v) in zip(sp.points, lp):
            p.co = (X(u), Z(v), 0, 1)
        sp.use_cyclic_u = True
    cu.extrude = max((d1 - d0) / 2 - bev, 0.0005)
    cu.bevel_depth = bev
    cu.bevel_resolution = 2
    ob = bpy.data.objects.new(name, cu)
    link(ob)
    ob.rotation_euler = (math.pi / 2, 0, 0)
    ob.location = (0, -(d0 + d1) / 2, 0)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    me.transform(ob.matrix_world)
    me.use_auto_texspace = True          # the curve's texture space is stale after the transform
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    assert len(me.polygons) > 0, f"empty slab {name}"
    me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = False
    mo = bpy.data.objects.new(name, me)
    link(mo, collection)
    return mo


def box(name, x0, x1, y0, y1, z0, z1, mat, collection=None):
    me = bpy.data.meshes.new(name)
    v = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    me.from_pydata(v, [], f)
    me.materials.append(mat)
    return link(bpy.data.objects.new(name, me), collection)


def plane_px(name, pts, d, mat, collection=None):
    """Flat polygon (px) at depth d, facing the street."""
    return slab(name, [pts], d - 0.0005, d + 0.0005, mat, bev=0.0, collection=collection)


def scan(pts, axis, value):
    """Intervals of the polygon on the line u=value (axis 0) or v=value (axis 1), even-odd."""
    xs = []
    n = len(pts)
    for i in range(n):
        a, b = pts[i - 1], pts[i]
        if (a[axis] <= value < b[axis]) or (b[axis] <= value < a[axis]):
            t = (value - a[axis]) / (b[axis] - a[axis])
            xs.append(a[1 - axis] + t * (b[1 - axis] - a[1 - axis]))
    xs.sort()
    return list(zip(xs[0::2], xs[1::2]))


def bar_step(lo, hi, pitch):
    """The spacing bars() really uses: the span divided evenly (whole span when there are no bars)."""
    n = int((hi - lo) / pitch + 0.5) if pitch else 1
    return (hi - lo) / max(n, 1)


def bars(pts, pitch, axis, width_px):
    """Mullion bars across a polygon every `pitch` px: vertical bars for axis 0 (u = const)."""
    lo = min(p[axis] for p in pts)
    hi = max(p[axis] for p in pts)
    out = []
    n = int((hi - lo) / pitch + 0.5)
    if n < 2:
        return out
    step = (hi - lo) / n
    for i in range(1, n):
        c = lo + i * step
        for a, b in scan(pts, axis, c):
            if axis == 0:
                out.append(F.rect(c - width_px / 2, a, c + width_px / 2, b))
            else:
                out.append(F.rect(a, c - width_px / 2, b, c + width_px / 2))
    return out


# ---------------------------------------------------------------- materials


def tex_image(nt, path, non_color=False):
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = bpy.data.images.load(str(Path(path).resolve()), check_existing=True)
    if non_color:
        n.image.colorspace_settings.name = "Non-Color"
    n.projection = "BOX"
    n.projection_blend = 0.2
    return n


def paint_group():
    """Exterior acrylic paint on cement render: colour, large mottling, crevice grime, plaster bump."""
    ng, gi, go = group("Paint", [
        ("Colour", "NodeSocketColor", P["red"], None, None),
        ("Roughness", "NodeSocketFloat", P["paint_rough"], 0.0, 1.0),
        ("Variation", "NodeSocketFloat", P["paint_var"], 0.0, 1.0),   # sun-faded mottling
        ("Grime", "NodeSocketFloat", P["grime"], 0.0, 1.0),           # dirt in corners and under ledges
        ("Waviness", "NodeSocketFloat", 0.5, 0.0, 1.0),                # low-frequency unevenness of cast render
        ("Chalk", "NodeSocketFloat", P["chalk"], 0.0, 1.0),            # pale sun-faded blotches (roller patches)
    ], [("Shader", "NodeSocketShader")])
    N = ng.nodes.new
    L = ng.links.new
    tc = N("ShaderNodeTexCoord")
    # large mottling: value +-(variation * 18 %)
    mot = N("ShaderNodeTexNoise")
    mot.inputs["Scale"].default_value = 0.45
    mot.inputs["Detail"].default_value = 4.0
    L(tc.outputs["Object"], mot.inputs["Vector"])
    fine = N("ShaderNodeTexNoise")
    fine.inputs["Scale"].default_value = 9.0
    fine.inputs["Detail"].default_value = 2.0
    L(tc.outputs["Object"], fine.inputs["Vector"])
    mix_n = N("ShaderNodeMix")
    mix_n.data_type = "FLOAT"
    mix_n.inputs[0].default_value = 0.35
    L(mot.outputs["Fac"], mix_n.inputs[2])
    L(fine.outputs["Fac"], mix_n.inputs[3])
    cen = N("ShaderNodeMath")
    cen.operation = "SUBTRACT"
    L(mix_n.outputs[0], cen.inputs[0])
    cen.inputs[1].default_value = 0.5
    amt = N("ShaderNodeMath")
    amt.operation = "MULTIPLY"
    L(cen.outputs[0], amt.inputs[0])
    L(gi.outputs["Variation"], amt.inputs[1])
    gain = N("ShaderNodeMath")
    gain.operation = "MULTIPLY_ADD"
    L(amt.outputs[0], gain.inputs[0])
    gain.inputs[1].default_value = 0.9
    gain.inputs[2].default_value = 1.0
    col = N("ShaderNodeMix")
    col.data_type = "RGBA"
    col.blend_type = "MULTIPLY"
    col.inputs[0].default_value = 1.0
    L(gi.outputs["Colour"], col.inputs[6])
    comb = N("ShaderNodeCombineColor")
    for i in range(3):
        L(gain.outputs[0], comb.inputs[i])
    L(comb.outputs[0], col.inputs[7])
    # grime (advisor): streaks just below ledges (local AO x a vertically stretched noise) plus dust on
    # up-facing tops; freshly painted, so keep it light
    ao = N("ShaderNodeAmbientOcclusion")
    ao.samples = 8
    ao.only_local = True
    ao.inputs["Distance"].default_value = 0.15
    inv = N("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    L(ao.outputs["AO"], inv.inputs[1])
    mp = N("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (6.0, 6.0, 0.5)
    L(tc.outputs["Object"], mp.inputs["Vector"])
    st = N("ShaderNodeTexNoise")
    st.inputs["Scale"].default_value = 3.0
    st.inputs["Detail"].default_value = 3.0
    L(mp.outputs[0], st.inputs["Vector"])
    sm = N("ShaderNodeMath")
    sm.operation = "MULTIPLY"
    L(inv.outputs[0], sm.inputs[0])
    L(st.outputs["Fac"], sm.inputs[1])
    geo = N("ShaderNodeNewGeometry")
    gz = N("ShaderNodeSeparateXYZ")
    L(geo.outputs["Normal"], gz.inputs[0])
    up = N("ShaderNodeMath")
    up.operation = "MAXIMUM"
    L(gz.outputs["Z"], up.inputs[0])
    up.inputs[1].default_value = 0.0
    tot = N("ShaderNodeMath")
    tot.operation = "MULTIPLY_ADD"
    L(sm.outputs[0], tot.inputs[0])
    tot.inputs[1].default_value = 2.0
    L(up.outputs[0], tot.inputs[2])
    gm0 = N("ShaderNodeMath")
    gm0.operation = "MULTIPLY"
    L(tot.outputs[0], gm0.inputs[0])
    L(gi.outputs["Grime"], gm0.inputs[1])
    # splash zone at the foot of walls: 1 at the ground, 0 by 0.8 m, broken by the streak noise
    pz = N("ShaderNodeSeparateXYZ")
    L(tc.outputs["Object"], pz.inputs[0])
    foot = N("ShaderNodeMapRange")
    L(pz.outputs["Z"], foot.inputs["Value"])
    foot.inputs["From Min"].default_value = 0.0
    foot.inputs["From Max"].default_value = 0.8
    foot.inputs["To Min"].default_value = 1.0
    foot.inputs["To Max"].default_value = 0.0
    fz = N("ShaderNodeMath")
    fz.operation = "MULTIPLY"
    L(foot.outputs[0], fz.inputs[0])
    L(st.outputs["Fac"], fz.inputs[1])
    fb = N("ShaderNodeMath")
    fb.operation = "MULTIPLY"
    L(fz.outputs[0], fb.inputs[0])
    fb.inputs[1].default_value = P["base_dirt"] * 1.6
    gm = N("ShaderNodeMath")
    gm.operation = "ADD"
    gm.use_clamp = True
    L(gm0.outputs[0], gm.inputs[0])
    L(fb.outputs[0], gm.inputs[1])
    dirt = N("ShaderNodeMix")
    dirt.data_type = "RGBA"
    dirt.blend_type = "MIX"
    L(gm.outputs[0], dirt.inputs[0])
    L(col.outputs[2], dirt.inputs[6])
    dirt.inputs[7].default_value = (0.30, 0.26, 0.21, 1)
    # low-frequency plaster waviness (cast render is never flat); fine grain is invisible at this distance
    bn = N("ShaderNodeTexNoise")
    bn.inputs["Scale"].default_value = 0.6
    bn.inputs["Detail"].default_value = 3.0
    L(tc.outputs["Object"], bn.inputs["Vector"])
    bs = N("ShaderNodeMath")
    bs.operation = "MULTIPLY"
    L(gi.outputs["Waviness"], bs.inputs[0])
    bs.inputs[1].default_value = 0.4
    bump = N("ShaderNodeBump")
    bump.inputs["Distance"].default_value = 0.02
    L(bs.outputs[0], bump.inputs["Strength"])
    L(bn.outputs["Fac"], bump.inputs["Height"])
    # chalky fade: pale, rougher blotches 10-30 cm across (reference red wall at 1:1)
    ck = N("ShaderNodeTexNoise")
    ck.inputs["Scale"].default_value = 3.5
    ck.inputs["Detail"].default_value = 8.0
    ck.inputs["Roughness"].default_value = 0.65
    L(tc.outputs["Object"], ck.inputs["Vector"])
    ckm = N("ShaderNodeMapRange")
    L(ck.outputs["Fac"], ckm.inputs["Value"])
    ckm.inputs["From Min"].default_value = 0.52
    ckm.inputs["From Max"].default_value = 0.72
    ckf = N("ShaderNodeMath")
    ckf.operation = "MULTIPLY"
    L(ckm.outputs[0], ckf.inputs[0])
    L(gi.outputs["Chalk"], ckf.inputs[1])
    pale = N("ShaderNodeMix")                      # the paint's own colour, lifted and greyed
    pale.data_type = "RGBA"
    pale.inputs[0].default_value = 0.35
    L(gi.outputs["Colour"], pale.inputs[6])
    pale.inputs[7].default_value = (0.75, 0.72, 0.68, 1)
    ckc = N("ShaderNodeMix")
    ckc.data_type = "RGBA"
    L(ckf.outputs[0], ckc.inputs[0])
    L(dirt.outputs[2], ckc.inputs[6])
    L(pale.outputs[2], ckc.inputs[7])
    b = N("ShaderNodeBsdfPrincipled")
    L(ckc.outputs[2], b.inputs["Base Color"])
    rv = N("ShaderNodeMath")
    rv.operation = "MULTIPLY_ADD"
    L(amt.outputs[0], rv.inputs[0])
    rv.inputs[1].default_value = 0.8
    L(gi.outputs["Roughness"], rv.inputs[2])
    L(rv.outputs[0], b.inputs["Roughness"])
    b.inputs["Specular IOR Level"].default_value = 0.3 if P["sky_glossy"] else 0.5
    L(bump.outputs["Normal"], b.inputs["Normal"])
    L(b.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def paint(name, colour, rough=None, var=None, grime=None):
    ng = paint_group() if "Paint" not in bpy.data.node_groups else bpy.data.node_groups["Paint"]
    m = material_from_group(name, ng)
    g = [n for n in m.node_tree.nodes if n.bl_idname == "ShaderNodeGroup"][0]
    g.inputs["Colour"].default_value = colour
    if rough is not None:
        g.inputs["Roughness"].default_value = rough
    if var is not None:
        g.inputs["Variation"].default_value = var
    if grime is not None:
        g.inputs["Grime"].default_value = grime
    return m


def glass_group():
    """Reflective tinted curtain-wall glass: a near-black dielectric whose IOR sets the coated
    reflectance (research: 3x less noise than transmission), optional thin-wall see-through for the
    rooms behind, and a small random tilt per pane so neighbouring panes reflect slightly different
    things."""
    ng, gi, go = group("Curtain Glass", [
        ("Tint", "NodeSocketColor", P["glass_tint"], None, None),          # body colour seen through the coating
        ("Reflectance", "NodeSocketFloat", P["glass_refl"], 0.02, 0.6),    # at normal incidence: 0.04 clear, 0.25 coated
        ("Roughness", "NodeSocketFloat", P["glass_rough"], 0.0, 0.3),
        ("See Through", "NodeSocketFloat", P["glass_see"], 0.0, 1.0),      # thin-wall transmission to the rooms
        ("Pane Wobble", "NodeSocketFloat", P["glass_wobble"], 0.0, 1.0),
    ], [("Shader", "NodeSocketShader")])
    N = ng.nodes.new
    L = ng.links.new
    # pane cell from the opening's own mullion grid (object attributes pane_x0, pane_z0, pane_pu, pane_pv)
    geo0 = N("ShaderNodeNewGeometry")
    sp = N("ShaderNodeSeparateXYZ")
    L(geo0.outputs["Position"], sp.inputs[0])
    cell = N("ShaderNodeCombineXYZ")
    for ax, key in (("X", "x"), ("Z", "z")):
        o = N("ShaderNodeAttribute")
        o.attribute_type = "OBJECT"
        o.attribute_name = f"pane_{key}0"
        pch = N("ShaderNodeAttribute")
        pch.attribute_type = "OBJECT"
        pch.attribute_name = "pane_pu" if key == "x" else "pane_pv"
        sub = N("ShaderNodeMath")
        sub.operation = "SUBTRACT"
        L(sp.outputs[ax], sub.inputs[0])
        L(o.outputs["Fac"], sub.inputs[1])
        dv = N("ShaderNodeMath")
        dv.operation = "DIVIDE"
        L(sub.outputs[0], dv.inputs[0])
        L(pch.outputs["Fac"], dv.inputs[1])
        fl = N("ShaderNodeMath")
        fl.operation = "FLOOR"
        L(dv.outputs[0], fl.inputs[0])
        L(fl.outputs[0], cell.inputs[ax])
    oi = N("ShaderNodeObjectInfo")
    L(oi.outputs["Random"], cell.inputs["Y"])
    wn = N("ShaderNodeTexWhiteNoise")
    wn.noise_dimensions = "3D"
    L(cell.outputs[0], wn.inputs["Vector"])
    sep = N("ShaderNodeSeparateColor")
    L(wn.outputs["Color"], sep.inputs[0])
    tilt = N("ShaderNodeCombineXYZ")
    for i, ax in enumerate(("X", "Z")):
        m = N("ShaderNodeMath")
        m.operation = "MULTIPLY_ADD"
        L(sep.outputs[i], m.inputs[0])
        m.inputs[1].default_value = 0.035           # +-1 degree at Pane Wobble 1
        m.inputs[2].default_value = -0.0175
        sc = N("ShaderNodeMath")
        sc.operation = "MULTIPLY"
        L(m.outputs[0], sc.inputs[0])
        L(gi.outputs["Pane Wobble"], sc.inputs[1])
        L(sc.outputs[0], tilt.inputs[ax])
    # reflectance +-20 % per pane
    rv = N("ShaderNodeMath")
    rv.operation = "MULTIPLY_ADD"
    L(sep.outputs[2], rv.inputs[0])
    rv.inputs[1].default_value = 0.4
    rv.inputs[2].default_value = 0.8
    refl = N("ShaderNodeMath")
    refl.operation = "MULTIPLY"
    L(gi.outputs["Reflectance"], refl.inputs[0])
    L(rv.outputs[0], refl.inputs[1])
    geo = N("ShaderNodeNewGeometry")
    add = N("ShaderNodeVectorMath")
    add.operation = "ADD"
    L(geo.outputs["Normal"], add.inputs[0])
    L(tilt.outputs[0], add.inputs[1])
    nn = N("ShaderNodeVectorMath")
    nn.operation = "NORMALIZE"
    L(add.outputs[0], nn.inputs[0])
    # IOR from reflectance: n = (1 + sqrt R) / (1 - sqrt R)
    sq = N("ShaderNodeMath")
    sq.operation = "SQRT"
    L(refl.outputs[0], sq.inputs[0])
    num = N("ShaderNodeMath")
    num.operation = "ADD"
    num.inputs[0].default_value = 1.0
    L(sq.outputs[0], num.inputs[1])
    den = N("ShaderNodeMath")
    den.operation = "SUBTRACT"
    den.inputs[0].default_value = 1.0
    L(sq.outputs[0], den.inputs[1])
    ior = N("ShaderNodeMath")
    ior.operation = "DIVIDE"
    L(num.outputs[0], ior.inputs[0])
    L(den.outputs[0], ior.inputs[1])
    b = N("ShaderNodeBsdfPrincipled")
    L(gi.outputs["Tint"], b.inputs["Base Color"])
    L(gi.outputs["Roughness"], b.inputs["Roughness"])
    L(ior.outputs[0], b.inputs["IOR"])
    L(gi.outputs["See Through"], b.inputs["Transmission Weight"])
    b.inputs["Thin Wall"].default_value = True
    L(nn.outputs[0], b.inputs["Normal"])
    # shadow rays pass straight through (tinted), so the sun reaches the rooms behind
    tr = N("ShaderNodeBsdfTransparent")
    L(gi.outputs["Tint"], tr.inputs["Color"])
    lp = N("ShaderNodeLightPath")
    sh = N("ShaderNodeMixShader")
    L(lp.outputs["Is Shadow Ray"], sh.inputs[0])
    L(b.outputs[0], sh.inputs[1])
    L(tr.outputs[0], sh.inputs[2])
    L(sh.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def simple(name, colour, rough=0.5, metal=0.0, emit=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = colour
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = emit[0]
        b.inputs["Emission Strength"].default_value = emit[1]
    return m


def decal(name, image, slats=0, rough=0.5, metal=0.0, emit=0.0):
    """Painted image across one flat part (Generated coords: x across, z up). slats = count of
    horizontal roll-up slats for a bump; emit lights a shop interior a little."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    uv = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(sep.outputs["X"], uv.inputs["X"])
    nt.links.new(sep.outputs["Z"], uv.inputs["Y"])
    im = nt.nodes.new("ShaderNodeTexImage")
    im.image = bpy.data.images.load(str((EXP["assets"] / "generated" / image).resolve()), check_existing=True)
    im.extension = "EXTEND"
    im.interpolation = "Cubic"
    nt.links.new(uv.outputs[0], im.inputs[0])
    nt.links.new(im.outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        nt.links.new(im.outputs[0], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emit
    if slats:
        wv = nt.nodes.new("ShaderNodeTexWave")
        wv.wave_type = "BANDS"
        wv.bands_direction = "Z"
        wv.wave_profile = "SIN"
        wv.inputs["Scale"].default_value = slats / 2.0
        nt.links.new(tc.outputs["Generated"], wv.inputs["Vector"])
        bu = nt.nodes.new("ShaderNodeBump")
        bu.inputs["Strength"].default_value = 0.6
        bu.inputs["Distance"].default_value = 0.01
        nt.links.new(wv.outputs["Fac"], bu.inputs["Height"])
        nt.links.new(bu.outputs["Normal"], b.inputs["Normal"])
    return m


def pavement(name, folder, scale, tint, pitch, angle, tone=0.12, dust=0.25):
    """Cast concrete slabs: the scanned texture, slanted saw-cut joints every `pitch` m across the walk
    (reference: joints run at an angle), one joint along the facade line, a tone per slab, and dust."""
    m = textured(name, folder, scale, tint=tint)
    nt = m.node_tree
    N, L = nt.nodes.new, nt.links.new
    b = nt.nodes["Principled BSDF"]
    base = b.inputs["Base Color"].links[0].from_socket
    tc = N("ShaderNodeTexCoord")
    sp = N("ShaderNodeSeparateXYZ")
    L(tc.outputs["Object"], sp.inputs[0])
    a = math.radians(angle)
    rot = N("ShaderNodeMath")                           # coordinate across the joints
    rot.operation = "MULTIPLY_ADD"
    L(sp.outputs["X"], rot.inputs[0])
    rot.inputs[1].default_value = math.cos(a) / pitch
    yk = N("ShaderNodeMath")
    yk.operation = "MULTIPLY"
    L(sp.outputs["Y"], yk.inputs[0])
    yk.inputs[1].default_value = math.sin(a) / pitch
    L(yk.outputs[0], rot.inputs[2])
    fr = N("ShaderNodeMath")
    fr.operation = "FRACT"
    L(rot.outputs[0], fr.inputs[0])
    jd = N("ShaderNodeMath")                            # distance to the nearest joint, in slab units
    jd.operation = "PINGPONG"
    L(fr.outputs[0], jd.inputs[0])
    jd.inputs[1].default_value = 0.5
    joint = N("ShaderNodeMath")
    joint.operation = "LESS_THAN"
    L(jd.outputs[0], joint.inputs[0])
    joint.inputs[1].default_value = 0.012 / pitch
    fl = N("ShaderNodeMath")
    fl.operation = "FLOOR"
    L(rot.outputs[0], fl.inputs[0])
    wn = N("ShaderNodeTexWhiteNoise")
    wn.noise_dimensions = "1D"
    L(fl.outputs[0], wn.inputs["W"])
    tn = N("ShaderNodeMapRange")
    L(wn.outputs["Value"], tn.inputs["Value"])
    tn.inputs["To Min"].default_value = 1.0 - tone
    tn.inputs["To Max"].default_value = 1.0 + tone
    mul = N("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs[0].default_value = 1.0
    L(base, mul.inputs[6])
    cc = N("ShaderNodeCombineColor")
    for i in range(3):
        L(tn.outputs[0], cc.inputs[i])
    L(cc.outputs[0], mul.inputs[7])
    du = N("ShaderNodeTexNoise")                        # dust drifts: lighter, flatter
    du.inputs["Scale"].default_value = 0.7
    du.inputs["Detail"].default_value = 5.0
    L(tc.outputs["Object"], du.inputs["Vector"])
    dm = N("ShaderNodeMapRange")
    L(du.outputs["Fac"], dm.inputs["Value"])
    dm.inputs["From Min"].default_value = 0.45
    dm.inputs["From Max"].default_value = 0.7
    dm.inputs["To Max"].default_value = dust
    dmix = N("ShaderNodeMix")
    dmix.data_type = "RGBA"
    L(dm.outputs[0], dmix.inputs[0])
    L(mul.outputs[2], dmix.inputs[6])
    dmix.inputs[7].default_value = (0.55, 0.50, 0.44, 1)
    jm = N("ShaderNodeMix")
    jm.data_type = "RGBA"
    L(joint.outputs[0], jm.inputs[0])
    L(dmix.outputs[2], jm.inputs[6])
    jm.inputs[7].default_value = (0.05, 0.045, 0.04, 1)
    L(jm.outputs[2], b.inputs["Base Color"])
    return m


def textured(name, folder, scale, tint=(1, 1, 1, 1), rough_mult=1.0, bump=0.4, sat=1.0):
    """Poly Haven / ambientCG set (diff, rough, nor_gl) box-projected in object space; scale = metres per tile."""
    d = TEX / folder
    files = {k: next((f for f in d.iterdir() if k in f.name.lower()), None) for k in ("diff", "rough", "nor_gl")}
    if files["diff"] is None:
        files["diff"] = next(f for f in d.iterdir() if "color" in f.name.lower())
        files["rough"] = next((f for f in d.iterdir() if "roughness" in f.name.lower()), None)
        files["nor_gl"] = next((f for f in d.iterdir() if "normalgl" in f.name.lower()), None)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / scale,) * 3
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    di = tex_image(nt, files["diff"])
    nt.links.new(mp.outputs[0], di.inputs[0])
    tm = nt.nodes.new("ShaderNodeMix")
    tm.data_type = "RGBA"
    tm.blend_type = "MULTIPLY"
    tm.inputs[0].default_value = 1.0
    if sat != 1.0:
        hs = nt.nodes.new("ShaderNodeHueSaturation")
        hs.inputs["Saturation"].default_value = sat
        nt.links.new(di.outputs[0], hs.inputs["Color"])
        nt.links.new(hs.outputs[0], tm.inputs[6])
    else:
        nt.links.new(di.outputs[0], tm.inputs[6])
    tm.inputs[7].default_value = tint
    nt.links.new(tm.outputs[2], b.inputs["Base Color"])
    if files["rough"]:
        ri = tex_image(nt, files["rough"], True)
        nt.links.new(mp.outputs[0], ri.inputs[0])
        rm = nt.nodes.new("ShaderNodeMath")
        rm.operation = "MULTIPLY"
        rm.use_clamp = True
        nt.links.new(ri.outputs[0], rm.inputs[0])
        rm.inputs[1].default_value = rough_mult
        nt.links.new(rm.outputs[0], b.inputs["Roughness"])
    if files["nor_gl"]:
        ni = tex_image(nt, files["nor_gl"], True)
        nt.links.new(mp.outputs[0], ni.inputs[0])
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.inputs["Strength"].default_value = bump
        nt.links.new(ni.outputs[0], nm.inputs["Color"])
        nt.links.new(nm.outputs[0], b.inputs["Normal"])
    return m


# ---------------------------------------------------------------- the building


def both(pts, mirror):
    return [pts, F.mirror_pts(pts)] if mirror else [pts]


def build_facade(M):
    c = coll("Facade")
    # wall plate with every opening cut through it (reveals are its hole walls)
    holes = [q for o in F.OPEN for q in both(o["pts"], o["mirror"])]
    slab("Wall", [F.rect(191, 150, 1263, 769)] + holes, -0.30, 0.0, M["red"], bev=0.0, collection=c)
    # building mass behind, hollow: rooms behind the glass
    x0, x1 = X(191), X(1263)
    zt = Z(150)
    box("Mass_back", x0, x1, 7.8, 8.0, 0, zt, M["interior"], c)
    for z in [Z(v) for v in (769, 520, 398, 292, 186)] + [zt]:
        box("Slab", x0, x1, 0.45, 8.0, z - 0.25, z, M["interior_slab"], c)
    box("Roof", x0, x1, 0.3, 8.0, zt - 0.1, zt + 0.3, M["roof"], c)
    box("Side_R", x1 - 0.3, x1, 0.0, 8.0, 0, zt, M["red"], c)
    # mouldings
    R = P["relief"]
    for i, e in enumerate(F.EL):
        mat = M[e["mat"]]
        if e["line"]:                                   # paint film on the host's face
            d0, d1, bev = e["d1"] * R - 0.004, e["d1"] * R + 0.003, 0.0
        elif e["core"] is not None:                    # a layer of a stacked moulding
            d0, d1, bev = -0.02, e["core"] * R - e["rank"] * P["layer_step"], e["bev"]
        else:
            d0, d1, bev = e["d0"] * R - 0.02, e["d1"] * R, e["bev"]
        for k, pts in enumerate(both(e["pts"], e["mirror"])):
            hs = e["holes"] if k == 0 else [F.mirror_pts(h) for h in e["holes"]]
            slab(f"M_{e['name']}_{i}_{k}", [pts] + hs, d0, d1, mat, bev, c)
    # portholes: ring + dark glass disc
    for dsc in F.DISCS:
        for cu in ([dsc["cu"], 2 * F.AXIS - dsc["cu"]] if dsc["mirror"] else [dsc["cu"]]):
            R, r = dsc["r"] + dsc["ring"], dsc["r"]
            dd = dsc["d"] * P["relief"]
            slab("Porthole_ring", [F.circle(cu, dsc["cv"], R, 32), F.circle(cu, dsc["cv"], r, 32)],
                 0.0, dd + 0.04, M[dsc["mat"]], 0.01, c)
            plane_px("Porthole_glass", F.circle(cu, dsc["cv"], r + 0.5, 32), dd + 0.008, M["dark_glass"], c)
    # glazing: pane, perimeter frame, mullions
    g = coll("Glazing")
    for gl in F.GLASS:
        for pts in both(gl["pts"], gl["mirror"]):
            opaque = gl["name"] in ("pier_win", "tower_glass")
            pane = plane_px(f"Glass_{gl['name']}", pts, gl["d"], M["dark_glass"] if opaque else M["glass"], g)
            us, vs = [p[0] for p in pts], [p[1] for p in pts]
            pane["pane_x0"], pane["pane_z0"] = X(min(us)), Z(max(vs))
            pane["pane_pu"] = bar_step(min(us), max(us), gl["mull_u"]) / P["ppm"]    # same cells as bars()
            pane["pane_pv"] = bar_step(min(vs), max(vs), gl["mull_v"]) / P["ppm"]
            fmat = {"dark": M["frame_dark"], "grey": M["frame_grey"]}.get(gl["frame"], M["mullion"])
            slab(f"Frame_{gl['name']}", [F.offset(pts, 0.3), F.offset(pts, -1.6)], gl["d"] - 0.04, gl["d"] + 0.05,
                 fmat, 0.0, g)
            bw = 1.3
            for axis, pitch in ((0, gl["mull_u"]), (1, gl["mull_v"])):
                if pitch:
                    for b in bars(pts, pitch, axis, bw):
                        slab("Mullion", [b], gl["d"] - 0.03, gl["d"] + 0.04, fmat, 0.0, g)


def build_ground_floor(M):
    c = coll("GroundFloor")
    holes = F.ground_floor()
    x_l = 118
    slab("GF_wall", [F.rect(x_l, F.GF_TOP, 1227, F.GROUND + 2)] + holes, -0.25, 0.0, M["gf_cream"], 0.0, c)
    for k, r in enumerate(F.between(x_l, 1227, 841, 847)):
        slab(f"GF_stripe_{k}", [r], 0.0, 0.006, M["gf_stripe"], 0.0, c)
    for k, r in enumerate(F.between(x_l, 1227, 847, F.GROUND + 2)):
        slab(f"GF_base_{k}", [r], 0.0, 0.012, M["gf_base"], 0.0, c)
    for i, (u0, u1) in enumerate(F.SHUTTERS):
        plane_px(f"Shutter_{i}", F.rect(u0, F.GF_OPEN_TOP, u1, F.GROUND), -0.10, M["shutter"], c)
    plane_px("Door", F.rect(F.DOOR[0], F.GF_OPEN_TOP, F.DOOR[1], F.GROUND), -0.12, M["door"], c)
    plane_px("Shop", F.rect(F.SHOP[0], F.GF_OPEN_TOP, F.SHOP[1], F.GROUND), -0.8, M["shop"], c)
    plane_px("Banner", F.rect(381, 785, 490, 806), 0.04, M["banner"], c)
    plane_px("Entrance", F.rect(118, 772, 215, F.GROUND), 0.03, M["entrance"], c)
    slab("Corner_fascia", [F.rect(110, 700, 192, 769)], 0.0, 0.22 * P["relief"], M["red"], 0.015, c)
    slab("Corner_fascia_line", [F.rect(110, 697, 192, 703)], 0.0, 0.26 * P["relief"], M["yellow"], 0.01, c)
    box("GF_mass", X(x_l), X(1227), 1.2, 8.0, 0.0, Z(F.GF_TOP), M["interior"], c)
    # soffit under the first-floor fascia
    box("Soffit", X(191), X(1263), -0.22, 0.0, Z(769) - 0.02, Z(769), M["red"], c)


def build_ground(M):
    c = coll("Street")
    walk = P["walk"]
    box("Sidewalk", -40, 40, -walk, 0.0, -0.18, 0.0, M["sidewalk"], c)
    box("Kerb", -40, 40, -walk - 0.14, -walk, -0.20, 0.0, M["kerb"], c)
    box("Road", -60, 60, -40, -walk - 0.14, -0.5, -0.16, M["road"], c)
    box("Side_street", -80, X(191) - 0.5, -walk, 40, -0.5, -0.12, M["road"], c)
    box("Side_walk", -80, X(191) - 0.5, -walk, -0.2, -0.3, 0.0, M["sidewalk"], c)
    box("Wall_left", -60, -24, 11.5, 11.8, -0.12, 2.2, M["brick"], c)


def build_neighbours(M):
    """Right neighbour, traced from the reference (u 1227-1400): an unfinished hollow-brick house on a
    concrete frame. Brick infill, two bronze-glass windows over projecting concrete ledges, a deep
    column on the right that throws a wide shadow, a projecting first-floor slab, columns with rebar
    above the roof, a grey roller shutter below."""
    c = coll("Neighbours")
    far = 1480
    wins = [F.rect(1270, 560, 1375, 613), F.rect(1270, 660, 1375, 715)]
    slab("NB_wall", [F.rect(1263.5, 505, far, 757)] + wins, -0.25, 0.0, M["brick"], 0.0, c)
    shutter = F.rect(1266, 783, 1340, F.GROUND + 1)
    slab("NB_ground", [F.rect(1227.5, 770, far, F.GROUND + 2), shutter], -0.25, 0.0, M["brick"], 0.0, c)
    for k, w in enumerate(wins):
        pane = plane_px(f"NB_glass_{k}", w, -0.10, M["glass"], c)
        pane["pane_x0"], pane["pane_z0"] = X(1270), Z(w[2][1])
        pane["pane_pu"], pane["pane_pv"] = 26 / P["ppm"], 60 / P["ppm"]
        slab(f"NB_frame_{k}", [F.offset(w, 0.3), F.offset(w, -1.4)], -0.14, -0.04, M["frame_grey"], 0.0, c)
        for u in (1296, 1322, 1349):
            slab("NB_mullion", [F.rect(u - 0.7, w[0][1], u + 0.7, w[2][1])], -0.13, -0.06, M["frame_grey"], 0.0, c)
        v = w[2][1]
        slab(f"NB_ledge_{k}", [F.rect(1262, v, 1381, v + 6)], 0.0, 0.3, M["concrete"], 0.01, c)
    slab("NB_column", [F.rect(1374, 458, 1392, 770)], -0.1, 1.0, M["concrete"], 0.01, c)
    slab("NB_column_l", [F.rect(1288, 480, 1297, 506)], -0.2, 0.05, M["concrete"], 0.0, c)
    slab("NB_column_far", [F.rect(1392, 480, far, 506)], -0.2, 0.0, M["brick"], 0.0, c)
    slab("NB_slab", [F.rect(1262, 757, far, 768)], 0.0, 0.35, M["concrete"], 0.01, c)
    slab("NB_beam_top", [F.rect(1263.5, 500, far, 507)], 0.0, 0.05, M["concrete"], 0.0, c)
    for u0, vtop, n in ((1289, 450, 3), (1364, 425, 4)):     # rebar out of the column tops
        for i in range(n):
            u = u0 + 1.2 + i * 2.2
            slab("NB_rebar", [F.rect(u - 0.3, vtop + i * 2, u + 0.3, 482)], 0.05, 0.07, M["frame_dark"], 0.0, c)
    plane_px("NB_shutter", shutter, -0.12, M["metal_shutter"], c)
    slab("NB_shutter_box", [F.rect(1266, 783, 1340, 793)], -0.12, -0.02, M["metal_shutter"], 0.0, c)
    box("NB_mass", X(1263), X(far), 0.25, 10.0, 0.0, Z(505), M["concrete"], c)
    box("NB_roof", X(1263), X(far), 0.0, 10.0, Z(505) - 0.2, Z(505), M["concrete"], c)


def build_wing(M):
    """Left corner (the chamfer and side facade seen obliquely). Its plan is two straight segments whose
    ends land on reference pixels at chosen depths: corner u 191 at y 0, u 118 at wing_y1, u 47 at
    wing_y2. Every part is a polygon of reference (u, v) points on one segment, so it lands on the
    reference whatever the depths; the depths only set how it catches the sun."""
    c = coll("Wing")
    D = P["cam_d"]
    ua = F.AXIS + P["cam_x"] * P["ppm"]
    v_h = F.GROUND - P["cam_h"] * P["ppm"]
    pts = []
    for u, y in ((191, 0.0), (118, P["wing_y1"]), (47, P["wing_y2"])):
        x, _ = at_depth(u, v_h, y)
        pts.append(Vector((x, y, 0)))

    def on(seg, u):
        """World point (z = 0) on segment seg (or its extension) that projects to reference column u."""
        p1, p2 = pts[seg], pts[seg + 1]
        d = p2 - p1
        du = u - ua
        t = (P["ppm"] * D * (p1.x - P["cam_x"]) - du * (D + p1.y)) / (du * d.y - P["ppm"] * D * d.x)
        return p1 + d * t

    def normal(seg):
        d = (pts[seg + 1] - pts[seg]).normalized()
        n = Vector((d.y, -d.x, 0))
        return -n if n.y > 0 else n                       # outward, toward the street

    def poly(name, seg, uvs, off, mat, thick=0.2):
        """Prism from a convex polygon of reference (u, v) points on segment seg, off m proud of it."""
        n = normal(seg)
        front = [on(seg, u) + Vector((0, 0, P["cam_h"] + (v_h - v) / P["ppm"] * (D + on(seg, u).y) / D))
                 for u, v in uvs]
        vs = [tuple(p + n * off) for p in front] + [tuple(p + n * (off - thick)) for p in front]
        k = len(front)
        faces = [tuple(range(k)), tuple(range(2 * k - 1, k - 1, -1))]
        faces += [(i, (i + 1) % k, k + (i + 1) % k, k + i) for i in range(k)]
        me = bpy.data.meshes.new(name)
        me.from_pydata(vs, [], faces)
        me.validate()
        me.normals_split_custom_set(None) if False else None
        me.materials.append(mat)
        ob = link(bpy.data.objects.new(name, me), c)
        # outward-facing winding
        bm_center = sum((Vector(v) for v in vs), Vector()) / len(vs)
        if me.polygons[0].normal.dot(n) < 0:
            me.flip_normals()
        return ob

    def part(name, seg, u0, u1, v0, v1, off, mat, thick=0.2):
        return poly(name, seg, [(u1, v0), (u0, v0), (u0, v1), (u1, v1)], off, mat, thick)

    # segment 0, the chamfer: glass curtain from the tower top down to a sloped sill
    part("Wing_mass0", 0, 118, 191, 175, 700, -0.35, M["interior"], thick=4.0)
    poly("Wing_glass", 0, [(190, 176), (119, 176), (119, 640), (190, 660)], -0.12, M["glass"], thick=0.01)
    for k in range(1, 6):
        u = 119 + (190 - 119) * k / 6
        part("Wing_mull", 0, u - 1.0, u + 1.0, 176, 655, -0.08, M["mullion"], thick=0.06)
    poly("Wing_sill", 0, [(190, 660), (118, 640), (118, 646), (190, 666)], 0.12, M["yellow"], thick=0.4)
    poly("Wing_sill_red", 0, [(190, 666), (118, 646), (118, 700), (190, 700)], 0.10, M["red"], thick=0.4)
    # the red hook frame: upper pier by the tower, a 45-degree step, the lower pier on the side facade
    part("Wing_hook_up", 0, 111, 150, 172, 287, 0.18, M["red"], thick=0.5)
    part("Wing_hook_up_o", 0, 142, 150, 180, 287, 0.21, M["orange"], thick=0.5)
    poly("Wing_hook_step", 0, [(150, 287), (111, 287), (80, 326), (118, 326)], 0.18, M["red"], thick=0.5)
    part("Wing_hook_cap", 0, 106, 152, 166, 174, 0.3, M["red"], thick=0.9)
    part("Wing_hook_low", 1, 80, 100, 326, 640, 0.14, M["red"], thick=0.4)
    part("Wing_hook_low_o", 1, 100, 118, 326, 640, 0.10, M["orange"], thick=0.4)
    # segment 1: cream pier with oculi, red edge and cap, cream corner post
    part("Wing_mass1", 1, 47, 118, 330, 700, -0.35, M["interior"], thick=1.0)
    part("Wing_pier", 1, 55, 80, 372, 640, 0.05, M["cream"], thick=0.3)
    part("Wing_edge", 1, 47, 55, 362, 700, 0.12, M["red"], thick=0.3)
    part("Wing_cap", 1, 25, 82, 368, 380, 0.3, M["red"], thick=0.8)
    part("Wing_post", 1, 80, 118, 640, 769, 0.08, M["cream"], thick=0.3)
    part("Wing_mass1_low", 1, 80, 118, 640, 769, -0.3, M["interior"], thick=1.0)
    for v in (425, 482, 540, 598):
        part("Wing_oculus", 1, 63, 76, v - 13, v + 13, 0.07, M["dark_glass"], thick=0.02)
        part("Wing_oculus_ring", 1, 60, 79, v - 16, v + 16, 0.06, M["orange"], thick=0.02)
    # far brick houses at the left edge
    for i, (u0, u1, vt, y) in enumerate(((0, 40, 462, 28.0), (0, 22, 520, 20.0))):
        x0, zt = at_depth(u0, vt, y)
        x1, _ = at_depth(u1, vt, y)
        box(f"BG_left_{i}", x0 - 6, x1, y, y + 8, -0.2, zt, M["brick"], c)


def build_sign(M):
    """Bronze 3D letters on the corner fascia: an arc of 'SALON DE EVENTOS' over 'CRUCERO DEL SUR'."""
    c = coll("Sign")
    font = None
    for f in ("/System/Library/Fonts/Supplemental/Copperplate.ttc", "/System/Library/Fonts/Supplemental/Arial Black.ttf"):
        if Path(f).exists():
            font = bpy.data.fonts.load(f, check_existing=True)
            break

    def letters(text, size_px, place):
        for i, ch in enumerate(text):
            if ch == " ":
                continue
            u, v, rot = place(i)
            cu = bpy.data.curves.new("SignChar", "FONT")
            cu.body = ch
            if font:
                cu.font = font
            cu.size = size_px / P["ppm"] * 1.35
            cu.extrude = 0.02
            cu.bevel_depth = 0.004
            cu.align_x, cu.align_y = "CENTER", "CENTER"
            ob = bpy.data.objects.new("SignChar", cu)
            link(ob, c)
            ob.location = (X(u), -0.22 * P["relief"] - 0.02, Z(v))
            ob.rotation_euler = (math.pi / 2, rot, 0)
            ob.data.materials.append(M["bronze"])
    main = "CRUCERO DEL SUR"
    letters(main, 13, lambda i: (112 + (215 - 112) * (i + 0.5) / len(main), 748, 0.0))
    arc = "SALON DE EVENTOS"
    cu0, cv0, r = 163.0, 790.0, 60.0

    def on_arc(i):
        a = math.radians(152 - (152 - 28) * i / (len(arc) - 1))
        return cu0 + r * math.cos(a), cv0 - r * math.sin(a), a - math.pi / 2
    letters(arc, 8, on_arc)


def build_roof_extras(M):
    """Two salmon tanks on a low plinth behind the parapet (Nio's oblique), placed so their outlines
    land on the reference: centre u, top v, diameter px."""
    c = coll("Roof")
    y = P["tank_y"]
    zr = Z(150)
    for u, v_top, dia_px in ((552, 68, 45), (608, 90, 41)):
        x, zt = at_depth(u, v_top, y)
        r = dia_px / 2 / P["ppm"] * (P["cam_d"] + y) / P["cam_d"]
        h = zt - r - (zr - 0.3)
        bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=r, depth=h, location=(x, y, zr - 0.3 + h / 2))
        cyl = bpy.context.active_object
        bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=24, radius=r, location=(x, y, zt - r))
        sph = bpy.context.active_object
        for ob in (cyl, sph):
            ob.data.materials.append(M["tank"])
            ob.data.shade_smooth()
            for col in ob.users_collection:
                col.objects.unlink(ob)
            c.objects.link(ob)
    box("Tank_plinth", X(520), X(640), y - 1.2, y + 1.2, zr - 0.3, zr + 0.9, M["tank"], c)


def build_diamonds(M):
    """Faceted chrome gems in the two tower oculi (Granser close-up: about 40 % of the ring's width,
    table up, point down, standing proud of the dark glass). Vertical axis, 12-sided brilliant cut."""
    c = coll("Diamonds")
    n = 12
    for cv in (210, 322):
        r = P["diamond_px"] / 2 / P["ppm"]
        cx, cz = X(F.AXIS), Z(cv) + r * 0.2
        cy = -P["diamond_y"]
        verts = []
        for i in range(n):                                   # table ring
            a = 2 * math.pi * (i + 0.5) / n
            verts.append((cx + 0.55 * r * math.cos(a), cy + 0.55 * r * math.sin(a), cz + 0.42 * r))
        for i in range(n):                                   # girdle
            a = 2 * math.pi * i / n
            verts.append((cx + r * math.cos(a), cy + r * math.sin(a), cz))
        verts.append((cx, cy, cz - 1.05 * r))                # culet
        faces = [tuple(range(n))]
        for i in range(n):
            j = (i + 1) % n
            faces.append((i, n + j, n + i) if False else (n + i, n + j, j, i) if False else (i, n + i, n + j))
            faces.append((i, n + j, j))
            faces.append((n + j, n + i, 2 * n))
        me = bpy.data.meshes.new("Diamond")
        me.from_pydata(verts, [], faces)
        me.validate()
        me.normals_make_consistent(inside=False) if hasattr(me, "normals_make_consistent") else None
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me)
        bm.free()
        me.materials.append(M["chrome"])
        link(bpy.data.objects.new("Diamond", me), c)


def build_context(M):
    """The street behind the camera, seen only in the glass (advisor, round 5): a staggered row of 3-4
    storey brick houses 16 m away with gaps, setbacks, unfinished tops with rebar, taller houses behind,
    poles and a cable, and a snowy peak far down the street. Camera-invisible and shadowless."""
    c = coll("Context")
    rng = random.Random(7)
    y0 = -(P["walk"] + 10.5 + P["walk"])
    x = -50.0
    while x < 50:
        w = rng.uniform(4.5, 9.0)
        floors = rng.choice((1, 2, 2, 3))
        h = floors * 2.8 + rng.uniform(-0.2, 0.4)
        yf = y0 - rng.uniform(0.0, 2.5)                        # setbacks
        mat = M["ctx_brick"] if rng.random() < 0.72 else M[rng.choice(("ctx_a", "ctx_b", "ctx_c"))]
        box("Ctx", x, x + w, yf - 9, yf, 0, h, mat, c)
        for f in range(floors):                               # windows: dark, some with pale curtains
            zb = f * 2.8 + 0.9
            for k in range(max(1, int(w / 3.2))):
                xw = x + 0.8 + k * 3.2
                wm = M["ctx_win"] if rng.random() < 0.7 else M["ctx_curtain"]
                box("Ctx_win", xw, xw + 1.6, yf + 0.01, yf + 0.05, zb, zb + 1.3, wm, c)
        box("Ctx_slab", x - 0.05, x + w + 0.05, yf - 0.1, yf + 0.12, h - 0.2, h, M["concrete"], c)
        if rng.random() < 0.45:                               # unfinished top: columns and rebar
            for xc in (x + 0.1, x + w - 0.35):
                box("Ctx_col", xc, xc + 0.25, yf - 0.3, yf - 0.05, h, h + 1.2, M["concrete"], c)
                for i in range(4):
                    box("Ctx_rebar", xc + 0.03 + i * 0.06, xc + 0.045 + i * 0.06, yf - 0.2, yf - 0.185, h + 1.2,
                        h + 1.8, M["frame_dark"], c)
        if rng.random() < 0.25:                               # a taller house behind
            hb = h + rng.uniform(1.5, 3.5)
            box("Ctx_back", x + rng.uniform(0, 2), x + w - rng.uniform(0, 2), yf - 20, yf - 12, 0, hb, M["ctx_brick"], c)
        x += w + (rng.uniform(1.0, 3.0) if rng.random() < 0.25 else 0.0)   # gaps show sunlit side walls
    for xp in range(-40, 41, 18):                             # poles on the far kerb and one cable
        box("Ctx_pole", xp, xp + 0.22, y0 + 1.2, y0 + 1.42, 0, 9.0, M["concrete"], c)
    cab = bpy.data.curves.new("Ctx_cable", "CURVE")
    cab.dimensions = "3D"
    cab.bevel_depth = 0.012
    sp = cab.splines.new("POLY")
    xs = list(range(-40, 41, 2))
    sp.points.add(len(xs) - 1)
    for p, xv in zip(sp.points, xs):
        sag = 0.8 * (1 - ((xv % 18) / 9 - 1) ** 2)
        p.co = (xv, y0 + 1.3, 8.6 - sag, 1)
    cob = bpy.data.objects.new("Ctx_cable", cab)
    cob.data.materials.append(M["frame_dark"])
    link(cob, c)
    # snowy peak (Huayna Potosi) far down the street, for the angled glass
    me = bpy.data.meshes.new("Ctx_peak")
    yv, rng2 = -2500.0, random.Random(3)
    ridge = [(-1400 + 100 * i, yv, 120 + (380 if i == 14 else rng2.uniform(60, 260))) for i in range(29)]
    base = [(v[0], yv, -50) for v in ridge]
    me.from_pydata(ridge + base, [], [(i, i + 1, 29 + i + 1, 29 + i) for i in range(28)])
    me.materials.append(M["snow"])
    link(bpy.data.objects.new("Ctx_peak", me), c)
    for ob in c.objects:            # seen by diffuse rays: across a 16 m street the houses block a slice
        ob.visible_camera = False   # of the sky, which keeps the shade side dark. With the reflection HDRI
        ob.visible_shadow = False   # the glass sees the photographed street instead
        # modelled low houses in front of the photo's sky: the glass sees them, then the HDRI above


def build_interior(M):
    """Rooms behind the see-through glass: dark, with pale floor slabs the sun reaches, columns, and
    curtains or blinds hung in some bays (advisor: the bright streaks are sunlit interiors)."""
    c = coll("Interior")
    rng = random.Random(11)
    x0, x1 = X(191), X(1263)
    for xc in [x0 + 0.5 + i * 4.8 for i in range(int((x1 - x0) / 4.8) + 1)]:
        box("Column", xc, xc + 0.35, 1.2, 1.55, 0, Z(150), M["interior_col"], c)
    for v_top, v_bot in ((186, 250), (292, 360), (400, 478), (522, 731)):
        for xb in [x0 + i * 2.2 for i in range(int((x1 - x0) / 2.2))]:
            if rng.random() < 0.3:
                mat = M["curtain"] if rng.random() < 0.6 else M["blind"]
                box("Curtain", xb, xb + rng.uniform(1.2, 2.1), 0.5, 0.52, Z(v_bot) + 0.05,
                    Z(v_top) - rng.uniform(0.0, 0.5), mat, c)
    box("Side_L", x0, x0 + 0.3, 0.0, 8.0, Z(769), Z(150), M["interior"], c)


# ---------------------------------------------------------------- light, camera, render


def sun_dir():
    el, az = math.radians(P["sun_elev"]), math.radians(P["sun_az"])
    return Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))  # toward the sun


def build_light(scene):
    s = sun_dir()
    bpy.ops.object.light_add(type="SUN")
    sun = bpy.context.active_object
    sun.name = "Sun"
    sun.data.energy = P["sun_strength"]
    sun.data.angle = math.radians(P["sun_angle"])
    sun.rotation_euler = (-s).to_track_quat("-Z", "Y").to_euler()
    w = bpy.data.worlds.new("Sky")
    w.use_nodes = True
    nt = w.node_tree
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "MULTIPLE_SCATTERING"
    sky.sun_disc = False
    sky.sun_elevation = math.radians(P["sun_elev"])
    sky.sun_rotation = math.atan2(s.x, s.y) + math.radians(P["sky_rot_fix"])   # checked by a sun-disc test
    sky.altitude = P["altitude"]
    sky.air_density = P["sky_air"]
    sky.aerosol_density = P["sky_aerosol"]
    sky.ozone_density = P["sky_ozone"]
    bg = nt.nodes["Background"]
    bg.inputs["Strength"].default_value = P["sky_strength"]
    # the photo's sky is ~0.85 of a lit cream wall, the physical sky ~0.4: lift it for camera rays
    # only, so reflections and the light it casts stay physical (advisor, plan stage)
    lp = nt.nodes.new("ShaderNodeLightPath")
    seen = nt.nodes.new("ShaderNodeMath")            # camera or glossy (advisor, round 5): mullions, glass
    seen.operation = "MAXIMUM"                        # and chrome reflect the photo's sky
    nt.links.new(lp.outputs["Is Camera Ray"], seen.inputs[0])
    if P["sky_glossy"]:
        nt.links.new(lp.outputs["Is Glossy Ray"], seen.inputs[1])
    else:
        seen.inputs[1].default_value = 0.0
    gain = nt.nodes.new("ShaderNodeMath")
    gain.operation = "MULTIPLY_ADD"
    nt.links.new(seen.outputs[0], gain.inputs[0])
    gain.inputs[1].default_value = P["sky_view"] - 1.0
    gain.inputs[2].default_value = 1.0
    hsv = nt.nodes.new("ShaderNodeHueSaturation")
    nt.links.new(sky.outputs[0], hsv.inputs["Color"])
    sat = nt.nodes.new("ShaderNodeMath")
    sat.operation = "MULTIPLY_ADD"                     # saturation: sky_sat for camera rays, 1 otherwise
    nt.links.new(seen.outputs[0], sat.inputs[0])
    sat.inputs[1].default_value = P["sky_sat"] - 1.0
    sat.inputs[2].default_value = 1.0
    nt.links.new(sat.outputs[0], hsv.inputs["Saturation"])
    # grad: 1 - sky_grad * clamp(elevation / 30 deg), camera rays only (Geometry Incoming points back)
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    dz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Incoming"], dz.inputs[0])
    el = nt.nodes.new("ShaderNodeMath")
    el.operation = "MULTIPLY"
    el.use_clamp = True
    nt.links.new(dz.outputs["Z"], el.inputs[0])
    el.inputs[1].default_value = -2.0                   # -z of Incoming = sin(elevation); /0.5
    gr = nt.nodes.new("ShaderNodeMath")
    gr.operation = "MULTIPLY"
    nt.links.new(el.outputs[0], gr.inputs[0])
    nt.links.new(lp.outputs["Is Camera Ray"], gr.inputs[1])   # the grad filter is on the lens only
    gd = nt.nodes.new("ShaderNodeMath")
    gd.operation = "MULTIPLY_ADD"
    nt.links.new(gr.outputs[0], gd.inputs[0])
    gd.inputs[1].default_value = -P["sky_grad"]
    gd.inputs[2].default_value = 1.0
    gg = nt.nodes.new("ShaderNodeMath")
    gg.operation = "MULTIPLY"
    nt.links.new(gain.outputs[0], gg.inputs[0])
    nt.links.new(gd.outputs[0], gg.inputs[1])
    # cirrus: streaky noise on a plane over the scene (direction / its height), camera and glossy rays
    # only, faded out toward the horizon; clouds are the sky's own light, greyed and brightened
    inc = nt.nodes.new("ShaderNodeVectorMath")
    inc.operation = "SCALE"
    nt.links.new(geo.outputs["Incoming"], inc.inputs[0])
    inc.inputs["Scale"].default_value = -1.0
    dz2 = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(inc.outputs[0], dz2.inputs[0])
    zc = nt.nodes.new("ShaderNodeMath")
    zc.operation = "MAXIMUM"
    nt.links.new(dz2.outputs["Z"], zc.inputs[0])
    zc.inputs[1].default_value = 0.02
    proj = nt.nodes.new("ShaderNodeVectorMath")
    proj.operation = "DIVIDE"
    nt.links.new(inc.outputs[0], proj.inputs[0])
    cz = nt.nodes.new("ShaderNodeCombineXYZ")
    for k in ("X", "Y", "Z"):
        nt.links.new(zc.outputs[0], cz.inputs[k])
    nt.links.new(cz.outputs[0], proj.inputs[1])
    cm = nt.nodes.new("ShaderNodeMapping")
    cm.inputs["Rotation"].default_value = (0, 0, math.radians(P["cloud_angle"]))
    cm.inputs["Scale"].default_value = (0.9, 3.5, 1.0)          # stretched: wisps
    nt.links.new(proj.outputs[0], cm.inputs["Vector"])
    cn = nt.nodes.new("ShaderNodeTexNoise")
    cn.noise_dimensions = "4D"                                  # before touching W: the socket appears with it
    cn.inputs["Scale"].default_value = 1.3
    cn.inputs["Detail"].default_value = 10.0
    cn.inputs["Roughness"].default_value = 0.62
    cn.inputs["W"].default_value = P["cloud_seed"]
    nt.links.new(cm.outputs[0], cn.inputs["Vector"])
    cr = nt.nodes.new("ShaderNodeMapRange")
    nt.links.new(cn.outputs["Fac"], cr.inputs["Value"])
    cr.inputs["From Min"].default_value = 0.52
    cr.inputs["From Max"].default_value = 0.78
    hz = nt.nodes.new("ShaderNodeMapRange")                     # fade near the horizon
    nt.links.new(dz2.outputs["Z"], hz.inputs["Value"])
    hz.inputs["From Min"].default_value = 0.05
    hz.inputs["From Max"].default_value = 0.35
    cmask = nt.nodes.new("ShaderNodeMath")
    cmask.operation = "MULTIPLY"
    nt.links.new(cr.outputs[0], cmask.inputs[0])
    nt.links.new(hz.outputs[0], cmask.inputs[1])
    camt = nt.nodes.new("ShaderNodeMath")
    camt.operation = "MULTIPLY"
    nt.links.new(cmask.outputs[0], camt.inputs[0])
    camt.inputs[1].default_value = P["clouds"]
    cseen = nt.nodes.new("ShaderNodeMath")
    cseen.operation = "MULTIPLY"
    nt.links.new(camt.outputs[0], cseen.inputs[0])
    nt.links.new(seen.outputs[0], cseen.inputs[1])
    bw = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(hsv.outputs[0], bw.inputs[0])
    cw = nt.nodes.new("ShaderNodeMath")
    cw.operation = "MULTIPLY"
    nt.links.new(bw.outputs[0], cw.inputs[0])
    cw.inputs[1].default_value = 1.9
    cwc = nt.nodes.new("ShaderNodeCombineColor")
    for i in range(3):
        nt.links.new(cw.outputs[0], cwc.inputs[i])
    cmix = nt.nodes.new("ShaderNodeMix")
    cmix.data_type = "RGBA"
    nt.links.new(cseen.outputs[0], cmix.inputs[0])
    nt.links.new(hsv.outputs[0], cmix.inputs[6])
    nt.links.new(cwc.outputs[0], cmix.inputs[7])
    mul = nt.nodes.new("ShaderNodeVectorMath")
    mul.operation = "SCALE"
    nt.links.new(cmix.outputs[2], mul.inputs[0])
    nt.links.new(gg.outputs[0], mul.inputs["Scale"])
    if P["refl_hdri"]:
        # glossy rays (not camera) see a photographed street instead of the procedural sky (fork
        # replacement 2): the glass reflects real buildings, ground and cloud
        env = nt.nodes.new("ShaderNodeTexEnvironment")
        env.image = bpy.data.images.load(str((EXP["assets"] / "hdri" / P["refl_hdri"]).resolve()), check_existing=True)
        etc = nt.nodes.new("ShaderNodeTexCoord")
        emp = nt.nodes.new("ShaderNodeMapping")
        emp.inputs["Rotation"].default_value = (math.radians(P["refl_hdri_pitch"]), 0, math.radians(P["refl_hdri_rot"]))
        nt.links.new(etc.outputs["Generated"], emp.inputs["Vector"])
        nt.links.new(emp.outputs[0], env.inputs["Vector"])
        eg = nt.nodes.new("ShaderNodeVectorMath")
        eg.operation = "SCALE"
        eg.inputs["Scale"].default_value = P["refl_hdri_gain"]
        nt.links.new(env.outputs[0], eg.inputs[0])
        gl_only = nt.nodes.new("ShaderNodeMath")
        gl_only.operation = "SUBTRACT"
        gl_only.use_clamp = True
        nt.links.new(lp.outputs["Is Glossy Ray"], gl_only.inputs[0])
        nt.links.new(lp.outputs["Is Camera Ray"], gl_only.inputs[1])
        em = nt.nodes.new("ShaderNodeMix")
        em.data_type = "RGBA"
        nt.links.new(gl_only.outputs[0], em.inputs[0])
        nt.links.new(mul.outputs[0], em.inputs[6])
        nt.links.new(eg.outputs[0], em.inputs[7])
        nt.links.new(em.outputs[2], bg.inputs[0])
    else:
        nt.links.new(mul.outputs[0], bg.inputs[0])
    scene.world = w
    return sun


def build_camera(scene):
    D, h = P["cam_d"], P["cam_h"]
    W = P["res_x"]
    f_px = P["ppm"] * D
    bpy.ops.object.camera_add(location=(P["cam_x"], -D, h))
    cam = bpy.context.active_object
    cam.rotation_euler = (math.pi / 2, 0, 0)
    cd = cam.data
    cd.sensor_fit = "HORIZONTAL"
    cd.sensor_width = 36.0
    cd.lens = 36.0 * f_px / W
    u_axis = F.AXIS + P["cam_x"] * P["ppm"]           # where the optical axis meets the facade, in px
    v_h = F.GROUND - h * P["ppm"]
    cd.shift_x = (W / 2 - u_axis) / W                 # + moves the frame right, the content left
    cd.shift_y = (v_h - P["res_y"] / 2) / W
    cd.clip_end = 5000
    scene.camera = cam
    return cam


def materials():
    M = {}
    for k in ("red", "orange", "yellow", "cream", "white", "gf_cream", "gf_base", "gf_stripe", "tank"):
        M[k] = paint(k.capitalize(), P[k])
    M["dark"] = simple("Dark liner", (0.02, 0.025, 0.035, 1), 0.3)
    M["glass"] = material_from_group("Glass", glass_group())
    M["dark_glass"] = simple("Glass opaque", (0.01, 0.012, 0.018, 1), 0.04)
    M["dark_glass"].node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 1.2
    M["mullion"] = simple("Anodised gold", P["mullion"], 0.35, 1.0)
    M["frame_dark"] = simple("Frame dark", (0.03, 0.03, 0.035, 1), 0.4, 0.5)
    M["frame_grey"] = simple("Frame grey", (0.10, 0.10, 0.11, 1), 0.45, 0.8)
    M["interior"] = simple("Interior", (P["interior"],) * 3 + (1,), 0.8)
    M["interior_slab"] = simple("Interior slab", (0.25, 0.24, 0.22, 1), 0.8)
    M["roof"] = simple("Roof", (0.3, 0.28, 0.26, 1), 0.9)
    M["chrome"] = simple("Chrome", (0.95, 0.95, 0.97, 1), 0.04, 1.0)
    M["shutter"] = decal("Shutter", "shutter.png", slats=30, rough=0.45)
    M["door"] = decal("Door", "door.png", rough=0.35, metal=0.4)
    M["shop"] = decal("Shop", "shop.png", rough=0.6, emit=0.4)
    M["banner"] = decal("Banner", "banner.png", rough=0.7)
    M["entrance"] = decal("Entrance", "entrance.png", rough=0.55)
    M["bronze"] = simple("Bronze letters", (0.45, 0.30, 0.16, 1), 0.35, 1.0)
    M["metal_shutter"] = simple("Metal shutter", (0.5, 0.5, 0.52, 1), 0.4, 0.7)
    if (TEX / "painted_metal_shutter").exists():
        M["metal_shutter"] = textured("Metal shutter", "painted_metal_shutter", 2.0, tint=(1.7, 1.7, 1.75, 1), bump=0.8, sat=0.2)
    M["concrete"] = simple("Concrete", (0.38, 0.36, 0.33, 1), 0.85)
    M["ctx_a"] = simple("Ctx A", (0.5, 0.45, 0.35, 1), 0.8)
    M["ctx_b"] = simple("Ctx B", (0.2, 0.3, 0.45, 1), 0.8)
    M["ctx_win"] = simple("Ctx win", (0.02, 0.02, 0.02, 1), 0.1)
    M["ctx_curtain"] = simple("Ctx curtain", (0.55, 0.5, 0.45, 1), 0.9)
    M["ctx_c"] = simple("Ctx C", (0.45, 0.42, 0.40, 1), 0.85)
    M["snow"] = simple("Snow", (0.8, 0.82, 0.86, 1), 0.6)
    M["interior_col"] = simple("Interior column", (0.2, 0.19, 0.18, 1), 0.8)
    M["curtain"] = simple("Curtain", (0.62, 0.56, 0.48, 1), 0.9)
    M["blind"] = simple("Blind", (0.45, 0.45, 0.44, 1), 0.7)
    try:
        M["brick"] = textured("Brick", "large_red_bricks", P["brick_scale"], tint=P["brick_tint"], bump=0.6,
                              sat=P["brick_sat"])
        M["sidewalk"] = pavement("Sidewalk", "painted_plaster_wall", 4.0, (0.95, 0.9, 0.86, 1), 1.9, 55.0)
        M["road"] = textured("Road", "cobblestone_03", 2.0, tint=(1.5, 1.5, 1.45, 1))
        M["ctx_brick"] = textured("Ctx brick", "large_red_bricks", 3.4, tint=(0.22, 0.20, 0.22, 1), bump=0.6)
    except (StopIteration, FileNotFoundError) as e:
        print("[out] texture missing", e)
        M.setdefault("brick", simple("Brick", (0.35, 0.16, 0.1, 1), 0.85))
        M.setdefault("ctx_brick", M["brick"])
        M.setdefault("sidewalk", simple("Sidewalk", (0.42, 0.38, 0.33, 1), 0.8))
        M.setdefault("road", simple("Road", (0.35, 0.32, 0.29, 1), 0.85))
    M["kerb"] = simple("Kerb", (0.5, 0.47, 0.42, 1), 0.8)
    return M


def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    enable_gpu(scene)
    M = materials()
    build_facade(M)
    build_ground_floor(M)
    build_ground(M)
    build_neighbours(M)
    build_wing(M)
    build_sign(M)
    build_roof_extras(M)
    build_diamonds(M)
    build_interior(M)
    if P["context"]:
        build_context(M)
    build_light(scene)
    build_camera(scene)
    scene.render.resolution_x = P["res_x"]
    scene.render.resolution_y = P["res_y"]
    vs = scene.view_settings
    vs.view_transform = P["view"]
    if P["look"] != "None":
        vs.look = P["look"]
    vs.exposure = P["exposure"]
    cy = scene.cycles
    cy.use_denoising = True
    cy.max_bounces = 8
    cy.glossy_bounces = 4
    cy.transparent_max_bounces = 16
    cy.sample_clamp_indirect = 0.0     # 10 crushed the shadow side at physical light values
    cy.film_exposure = P["film_exposure"]
    cy.adaptive_threshold = 0.01
    scene.view_layers[0].cycles.denoising_store_passes = True
    if P["clay"]:
        clay = bpy.data.materials.new("Clay")
        clay.use_nodes = True
        scene.view_layers[0].material_override = clay
    how_to_tweak(HOW_TO_TWEAK)
    n = sum(len(o.data.polygons) for o in scene.objects if o.type == "MESH")
    print(f"[out] objects {len(scene.objects)}  polygons {n}")
    return scene


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="wip", help="render name, saved to renders/<out>.png")
    ap.add_argument("--samples", type=int, default=128)
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--norender", action="store_true")
    ap.add_argument("--preflight", action="store_true")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    a = ap.parse_args(argv)
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in P:
            sys.exit(f"unknown P key: {k}")
        P[k] = ast.literal_eval(v) if not isinstance(P[k], str) else v
    return a


def post():
    """Compositor controls on one node: a faint glow off glass glints and slight lens fringing."""
    ng, gi, go = post_group("Post", [
        ("Glow", "NodeSocketFloat", P["glow"], 0.0, 2.0),
        ("Glow Size", "NodeSocketFloat", P["glow_size"], 0.0, 1.0),
        ("Glow Threshold", "NodeSocketFloat", P["glow_threshold"], 0.0, 4.0),
        ("Chroma", "NodeSocketFloat", P["chroma"], 0.0, 0.05),
    ])
    glare = ng.nodes.new("CompositorNodeGlare")
    lens = ng.nodes.new("CompositorNodeLensdist")
    ng.links.new(gi.outputs["Image"], glare.inputs["Image"])
    glare.inputs["Type"].default_value = "Fog Glow"
    for src, dst in (("Glow", "Strength"), ("Glow Size", "Size"), ("Glow Threshold", "Threshold")):
        ng.links.new(gi.outputs[src], glare.inputs[dst])
    ng.links.new(glare.outputs["Image"], lens.inputs["Image"])
    ng.links.new(gi.outputs["Chroma"], lens.inputs["Dispersion"])
    ng.links.new(lens.outputs["Image"], go.inputs["Image"])
    auto_layout(ng)
    return ng


if __name__ == "__main__":
    args = parse_args()
    scene = build_scene()
    raw = EXP["renders"] / f"{args.out}_raw.exr"
    compositor(scene, post(), raw_exr=raw)
    scene.cycles.samples = args.samples
    scene.render.resolution_percentage = round(args.scale * 100)
    if args.preflight:
        sheet(scene, EXP["reviews"] / f"preflight_{args.out}.png", tiles_dir=EXP["renders"] / f"preflight_{args.out}")
        args.norender, args.save = True, False
    if not args.norender:
        ss = P["supersample"]
        final = EXP["renders"] / f"{args.out}.png"
        if ss > 1:
            scene.render.resolution_percentage = round(args.scale * 100 * ss)
            raw_png = EXP["renders"] / f"{args.out}_{ss}x.png"
        else:
            raw_png = final
        scene.render.filepath = str(raw_png)
        bpy.ops.render.render(write_still=True)
        if ss > 1:
            import subprocess
            w, h = round(P["res_x"] * args.scale), round(P["res_y"] * args.scale)
            r = subprocess.run(["python3", str(HERE / "photo_finish.py"), str(raw_png), str(final), str(w), str(h),
                                str(P["sharpen_px"] * args.scale), str(P["sharpen_pct"]), str(P["jpeg_q"])],
                               capture_output=True, text=True)
            print(r.stdout.strip() or r.stderr.strip())
            assert final.exists(), "photo finish failed"
    if args.save:
        if not args.norender:
            use_saved_render(scene, raw, EXP["output"])
        blend = EXP["output"] / f"{EXP['name']}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        blend.with_suffix(".blend1").unlink(missing_ok=True)
    print("BUILD OK")
