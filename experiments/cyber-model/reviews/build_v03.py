"""cyber-model: a sci-fi handheld radio in the hard-surface style, built from nothing, rendered, saved.

Run from the repo root:
  tools/blender.sh experiments/cyber-model/scripts/build.py --out v01 --samples 128 --scale 0.5
  ... --view plan          orthographic top-down, pixel-aligned to assets/ref_plan_rectified.png
  ... --set key=value      override any value in P
  ... --clay / --mirror    debug material overrides (correctness pass)
  ... --save               also save output/cyber-model.blend

Layout is traced from the plan-view rectification of the reference: LAYOUT and the part positions are in
plan px (3.6 px per mm, origin at plan (500, 480), +x right, +y up). Lengths in the kit are millimetres.
"""
import argparse
import ast
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import enable_gpu, experiment_paths  # noqa: E402
from nodes import auto_layout, group, how_to_tweak, material_from_group  # noqa: E402
from comp import LEGACY, compositor, post_group, use_saved_render  # noqa: E402
from hs_kit import (MM, box, circle_outline, cut, cylinder, extrude_outline, gear, hard_edges,  # noqa: E402
                    helix_cord, join, knurled_cylinder, offset_outline, rect_outline, ring_cutter,
                    rounded_outline, tube, weight_edges)

EXP = experiment_paths(__file__)

# Every value a designer might tune lives here. Override with --set key=value.
P = {
    "res_x": 1600,
    "res_y": 1200,
    # camera (device turned cam_azim degrees; looks down cam_elev degrees)
    "cam_elev": 48.65,
    "cam_azim": 41.0,
    "cam_lens": 200.0,
    "cam_dist": 1.485,              # m
    "cam_target": (451.5, 380.5),   # plan px, the point the camera looks at (fit_camera.py)
    "cam_shift": (0.0, 0.0),        # lens shift, fraction of frame
    "view": "Standard",
    # light
    "key_power": 7.5,
    "key_size": 0.7,
    "key_dist": 0.40,           # key height above the target, m
    "key_side": 0.30,           # key offset toward camera-right, m
    "key_far": 0.30,            # key offset away from the camera, m
    "fill_power": 2.5,
    "fill_front": 0.35,         # fill distance in front of the target, toward the camera, m
    "fill_height": 0.06,
    "fill_size": 0.5,
    "fill_linked": True,          # light-link the fill to the device so walls lift without lifting the backdrop
    "world_strength": 0.03,
    "exposure": 0.0,
    # plates: heights in mm, floor to top
    "gap_mm": 0.5,
    "bevel_plate_mm": 0.7,
    "bevel_small_mm": 0.35,
    "bevel_hull_mm": 1.0,
    "bevel_segments": 2,
    # materials
    "poly_colour": (0.062, 0.062, 0.067, 1.0),
    "ao_dist_mm": 2.2,
    "ao_floor": 0.12,
    "poly_rough": 0.42,
    "wear": 0.5,
    "edge_lift": 1.9,
    "scratch": 0.16,
    "groove_mm": 0.7,
    "grain": 0.25,
    "steel_colour": (0.42, 0.43, 0.45, 1.0),
    "steel_rough": 0.32,
    "rubber_colour": (0.03, 0.03, 0.033, 1.0),
    "green_colour": (0.048, 0.052, 0.058, 1.0),
    "lcd_strength": 1.2,
    "backdrop_colour": (0.16, 0.16, 0.17, 1.0),
    "backdrop_grain": 3.0,
    # cord
    "cord_turns": 21,
    "cord_coil_r": 6.2,
    "cord_wire_r": 1.35,
    "antenna_len": 72.0,
    "clay": False,
    "mirror": False,
}

HOW_TO_TWEAK = """\
cyber-model — how to tweak

Each material is one node. Select the object, open the Shader Editor, and change
the inputs on its group node (Polymer, Steel, Rubber, LCD). Hover an input for its range.

- Polymer: Colour, Roughness, Edge Wear, Wear Width mm, Scratches, Grain.
- Steel: Colour, Roughness, Grain.  Rubber: Colour, Roughness, Grain.
- LCD: Strength (backlight).
- Lights: select "Key" or "Fill", change Power and Size in Object Data.
- Post: open the Compositing tab. The backdrop shows the saved render. Change the
  inputs on the "Post" node and it updates at once, no re-render. Tab into it to see the
  nodes inside. After a new render (F12), set "Source" to Off to use it.

Built by experiments/cyber-model/scripts/build.py. Changes made here are lost on rebuild;
copy good values back into P.
"""

# ------------------------------------------------------------------ layout (plan px)

S_PX = 3.6          # plan px per mm
ORG = (500.0, 480.0)


def pp(x, y):
    """Plan px to device mm (+x right, +y up)."""
    return ((x - ORG[0]) / S_PX, -(y - ORG[1]) / S_PX)


def pl(pts):
    return [pp(x, y) for x, y in pts]


LAYOUT = {
    "base": [(300, 200), (500, 196), (522, 152), (690, 152), (702, 182), (704, 740), (696, 796), (500, 812),
             (312, 818), (300, 560), (318, 400), (300, 352)],
    "tm": [(348, 198), (492, 198), (550, 152), (676, 152), (692, 172), (692, 430), (348, 430)],
    "sh": [(405, 395), (425, 358), (670, 355), (692, 372), (700, 557), (665, 567), (635, 577), (605, 610),
           (570, 650), (500, 656), (500, 540), (485, 505), (418, 440)],
    "wing": [(303, 398), (405, 398), (418, 440), (485, 505), (500, 540), (500, 558), (303, 558)],
    "ms": [(425, 556), (500, 556), (500, 722), (470, 760), (425, 760)],
    "lb": [(318, 552), (425, 552), (425, 760), (470, 796), (330, 802), (318, 782)],
    "lr": [(500, 660), (570, 652), (605, 610), (635, 578), (665, 568), (700, 558), (704, 730), (500, 730)],
    "ec": [(430, 735), (700, 722), (704, 780), (690, 795), (480, 805), (430, 790)],
    "lug": [(262, 446), (320, 438), (322, 488), (262, 480)],
    "wedge": [(250, 255), (338, 190), (348, 198), (348, 400), (322, 405), (318, 360), (280, 352), (255, 300)],
    "lid": [(552, 394), (650, 394), (668, 412), (676, 536), (608, 560), (552, 560)],
}

# z: floor and top of each plate, mm. v01 was a thin tray (base 6 mm, steps 3-5 mm); the reference walls
# measure about 13 mm, so the slab is 13 mm and the steps 4-8 mm (review v01, problem 1).
Z = {"base": (0.03, 13.0), "tm": (13.0, 19.0), "sh": (13.0, 25.0), "wing": (13.0, 17.0), "ms": (13.0, 15.5),
     "lb": (13.0, 18.0), "lr": (13.0, 17.0), "ec": (13.0, 19.0), "wedge": (13.0, 19.0), "lug": (0.03, 17.0)}
T = {k: v[1] for k, v in Z.items()}      # top of each plate

LCD_C = (473.5, 265.0)      # plan px
LCD_BEZEL = (64.7, 36.1)    # mm
LCD_GLASS = (60.6, 32.2)


# ------------------------------------------------------------------ materials

def _n(nt, kind, **props):
    n = nt.nodes.new(kind)
    for k, v in props.items():
        setattr(n, k, v)
    return n


def _l(nt, a, b):
    nt.links.new(a, b)


def _mapr(nt, val, lo, hi, out_lo=0.0, out_hi=1.0, clamp=True):
    m = _n(nt, "ShaderNodeMapRange")
    m.clamp = clamp
    m.inputs[1].default_value, m.inputs[2].default_value = lo, hi
    m.inputs[3].default_value, m.inputs[4].default_value = out_lo, out_hi
    if hasattr(val, "bl_rna"):
        _l(nt, val, m.inputs[0])
    else:
        m.inputs[0].default_value = val
    return m.outputs[0]


def _math(nt, op, a, b=None, clamp=False):
    m = _n(nt, "ShaderNodeMath", operation=op, use_clamp=clamp)
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if hasattr(v, "bl_rna"):
            _l(nt, v, m.inputs[i])
        else:
            m.inputs[i].default_value = v
    return m.outputs[0]


def _mix_col(nt, fac, a, b):
    m = _n(nt, "ShaderNodeMix", data_type="RGBA")
    for i, v in ((0, fac), (6, a), (7, b)):
        if hasattr(v, "bl_rna"):
            _l(nt, v, m.inputs[i])
        else:
            m.inputs[i].default_value = v
    return m.outputs[2]


def _mix_f(nt, fac, a, b):
    m = _n(nt, "ShaderNodeMix", data_type="FLOAT")
    for i, v in ((0, fac), (2, a), (3, b)):
        if hasattr(v, "bl_rna"):
            _l(nt, v, m.inputs[i])
        else:
            m.inputs[i].default_value = v
    return m.outputs[0]


def _noise_bump(nt, coord, scale, strength_socket, dist=0.0002, detail=2.0, vec_scale=None):
    """Bump normal from a noise height. coord: a vector socket."""
    src = coord
    if vec_scale is not None:
        mp = _n(nt, "ShaderNodeMapping")
        mp.inputs["Scale"].default_value = vec_scale
        _l(nt, coord, mp.inputs["Vector"])
        src = mp.outputs[0]
    nz = _n(nt, "ShaderNodeTexNoise", noise_dimensions="3D")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = detail
    _l(nt, src, nz.inputs["Vector"])
    bp = _n(nt, "ShaderNodeBump")
    bp.inputs["Distance"].default_value = dist
    _l(nt, nz.outputs["Fac"], bp.inputs["Height"])
    if hasattr(strength_socket, "bl_rna"):
        _l(nt, strength_socket, bp.inputs["Strength"])
    else:
        bp.inputs["Strength"].default_value = strength_socket
    return bp.outputs["Normal"], nz.outputs["Fac"]


def polymer_group():
    """Satin polymer. Two materials share this group: faces (Is Edge 0) and the chamfer faces that the
    Bevel modifier writes into slot 1 (Is Edge 1). Chamfers are lighter, glossier and patchily worn;
    faces carry sparse short scratches and a micro grain. No shader Bevel node: on geometry that already
    has a real bevel it only sees the creases between bevel segments (advisor)."""
    ng, gi, go = group("Polymer", [
        ("Colour", "NodeSocketColor", P["poly_colour"], None, None),
        ("Roughness", "NodeSocketFloat", P["poly_rough"], 0.0, 1.0),
        ("Edge Wear", "NodeSocketFloat", P["wear"], 0.0, 1.0),
        ("Edge Lift", "NodeSocketFloat", P["edge_lift"], 1.0, 4.0),
        ("Scratches", "NodeSocketFloat", P["scratch"], 0.0, 1.0),
        ("Grain", "NodeSocketFloat", P["grain"], 0.0, 1.0),
        ("Is Edge", "NodeSocketFloat", 0.0, 0.0, 1.0),
    ("Crease Depth mm", "NodeSocketFloat", P["ao_dist_mm"], 0.2, 8.0),
    ("Crease Black", "NodeSocketFloat", P["ao_floor"], 0.0, 1.0),
    ], [("Shader", "NodeSocketShader")])
    tc = _n(ng, "ShaderNodeTexCoord")
    # ambient occlusion: real blacks at the foot of every step and in the gaps (review v02, problem 3)
    aoN = _n(ng, "ShaderNodeAmbientOcclusion", samples=8, inside=False, only_local=False)
    _l(ng, _math(ng, "MULTIPLY", gi.outputs["Crease Depth mm"], 0.001), aoN.inputs["Distance"])
    aov = _mix_f(ng, aoN.outputs["AO"], gi.outputs["Crease Black"], 1.0)
    # patchy wear on chamfer faces
    pn = _n(ng, "ShaderNodeTexNoise", noise_dimensions="3D")
    pn.inputs["Scale"].default_value, pn.inputs["Detail"].default_value = 90.0, 3.0
    _l(ng, tc.outputs["Object"], pn.inputs["Vector"])
    patch = _mapr(ng, pn.outputs["Fac"], 0.40, 0.62, 0.0, 1.0)
    edge_mask = _math(ng, "MULTIPLY", patch, _math(ng, "MULTIPLY", gi.outputs["Edge Wear"], 2.0), clamp=True)
    # sparse short scratches, clustered by a low-frequency mask
    cl = _n(ng, "ShaderNodeTexNoise", noise_dimensions="3D")
    cl.inputs["Scale"].default_value, cl.inputs["Detail"].default_value = 28.0, 1.0
    _l(ng, tc.outputs["Object"], cl.inputs["Vector"])
    cluster = _mapr(ng, cl.outputs["Fac"], 0.50, 0.66, 0.0, 1.0)
    sc = []
    for rot, seed in ((0.5, 0.0), (-1.0, 7.3), (1.9, 3.1)):
        mp = _n(ng, "ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (1900.0, 110.0, 110.0)
        mp.inputs["Rotation"].default_value = (0.0, 0.0, rot)
        mp.inputs["Location"].default_value = (seed, seed, seed)
        _l(ng, tc.outputs["Object"], mp.inputs["Vector"])
        nz = _n(ng, "ShaderNodeTexNoise", noise_dimensions="3D")
        nz.inputs["Scale"].default_value, nz.inputs["Detail"].default_value = 1.0, 0.0
        _l(ng, mp.outputs[0], nz.inputs["Vector"])
        sc.append(_mapr(ng, nz.outputs["Fac"], 0.72, 0.75, 0.0, 1.0))
    scr = _math(ng, "MULTIPLY", _math(ng, "MAXIMUM", _math(ng, "MAXIMUM", sc[0], sc[1]), sc[2]), cluster)
    scr = _math(ng, "MULTIPLY", scr, gi.outputs["Scratches"])
    mask = _mix_f(ng, gi.outputs["Is Edge"], _math(ng, "MULTIPLY", scr, 0.7), edge_mask)
    bump, _ = _noise_bump(ng, tc.outputs["Object"], 2600.0, gi.outputs["Grain"], dist=0.00015, detail=1.0)
    bsdf = _n(ng, "ShaderNodeBsdfPrincipled")
    scuff = _n(ng, "ShaderNodeRGB")
    scuff.outputs[0].default_value = (0.20, 0.20, 0.21, 1.0)
    lift = _math(ng, "ADD", 1.0, _math(ng, "MULTIPLY", gi.outputs["Is Edge"], _math(ng, "SUBTRACT", gi.outputs["Edge Lift"], 1.0)))
    lifted = _n(ng, "ShaderNodeVectorMath", operation="SCALE")
    _l(ng, gi.outputs["Colour"], lifted.inputs[0])
    _l(ng, lift, lifted.inputs["Scale"])
    dark = _n(ng, "ShaderNodeVectorMath", operation="SCALE")
    _l(ng, _mix_col(ng, mask, lifted.outputs[0], scuff.outputs[0]), dark.inputs[0])
    _l(ng, aov, dark.inputs["Scale"])
    _l(ng, dark.outputs[0], bsdf.inputs["Base Color"])
    _l(ng, aov, bsdf.inputs["Specular IOR Level"])
    rough = _math(ng, "MULTIPLY", gi.outputs["Roughness"], _math(ng, "SUBTRACT", 1.0, _math(ng, "MULTIPLY", gi.outputs["Is Edge"], 0.35)))
    _l(ng, _mix_f(ng, mask, rough, 0.62), bsdf.inputs["Roughness"])
    _l(ng, bump, bsdf.inputs["Normal"])
    _l(ng, bsdf.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def steel_group():
    ng, gi, go = group("Steel", [
        ("Colour", "NodeSocketColor", P["steel_colour"], None, None),
        ("Roughness", "NodeSocketFloat", P["steel_rough"], 0.0, 1.0),
        ("Grain", "NodeSocketFloat", 0.35, 0.0, 1.0),
    ], [("Shader", "NodeSocketShader")])
    tc = _n(ng, "ShaderNodeTexCoord")
    bump, _ = _noise_bump(ng, tc.outputs["Object"], 3500.0, gi.outputs["Grain"], dist=0.0001, detail=1.0,
                          vec_scale=(1.0, 6.0, 1.0))
    b = _n(ng, "ShaderNodeBsdfPrincipled")
    b.inputs["Metallic"].default_value = 1.0
    _l(ng, gi.outputs["Colour"], b.inputs["Base Color"])
    _l(ng, gi.outputs["Roughness"], b.inputs["Roughness"])
    _l(ng, bump, b.inputs["Normal"])
    _l(ng, b.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def rubber_group():
    ng, gi, go = group("Rubber", [
        ("Colour", "NodeSocketColor", P["rubber_colour"], None, None),
        ("Roughness", "NodeSocketFloat", 0.72, 0.0, 1.0),
        ("Grain", "NodeSocketFloat", 0.4, 0.0, 1.0),
    ], [("Shader", "NodeSocketShader")])
    tc = _n(ng, "ShaderNodeTexCoord")
    bump, _ = _noise_bump(ng, tc.outputs["Object"], 3000.0, gi.outputs["Grain"], dist=0.00015)
    b = _n(ng, "ShaderNodeBsdfPrincipled")
    _l(ng, gi.outputs["Colour"], b.inputs["Base Color"])
    _l(ng, gi.outputs["Roughness"], b.inputs["Roughness"])
    _l(ng, bump, b.inputs["Normal"])
    _l(ng, b.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def lcd_group():
    ng, gi, go = group("LCD", [("Strength", "NodeSocketFloat", P["lcd_strength"], 0.0, 4.0)],
                       [("Shader", "NodeSocketShader")])
    img = bpy.data.images.load(str(EXP["assets"] / "lcd.png"))
    img.colorspace_settings.name = "sRGB"
    tx = _n(ng, "ShaderNodeTexImage", image=img, interpolation="Linear")
    b = _n(ng, "ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (0.004, 0.006, 0.006, 1.0)
    b.inputs["Roughness"].default_value = 0.5
    b.inputs["Coat Weight"].default_value = 1.0
    b.inputs["Coat Roughness"].default_value = 0.03
    _l(ng, tx.outputs["Color"], b.inputs["Emission Color"])
    _l(ng, gi.outputs["Strength"], b.inputs["Emission Strength"])
    _l(ng, b.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def emit_material(name, colour, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = colour
    b.inputs["Emission Color"].default_value = colour
    b.inputs["Emission Strength"].default_value = strength
    b.inputs["Roughness"].default_value = 0.2
    return m


def backdrop_material():
    m = bpy.data.materials.new("Backdrop")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = _n(nt, "ShaderNodeOutputMaterial")
    b = _n(nt, "ShaderNodeBsdfPrincipled")
    _l(nt, b.outputs[0], out.inputs[0])
    tc = _n(nt, "ShaderNodeTexCoord")
    nz = _n(nt, "ShaderNodeTexNoise", noise_dimensions="3D")
    nz.inputs["Scale"].default_value, nz.inputs["Detail"].default_value = 1100.0, 4.0
    nz.inputs["Roughness"].default_value = 0.65
    _l(nt, tc.outputs["Object"], nz.inputs["Vector"])
    grain = _math(nt, "MULTIPLY", _math(nt, "SUBTRACT", nz.outputs["Fac"], 0.5), P["backdrop_grain"] * 2.0)
    fac = _math(nt, "ADD", grain, 1.0)
    col = _n(nt, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY")
    col.inputs[0].default_value = 1.0
    col.inputs[6].default_value = P["backdrop_colour"]
    _l(nt, fac, col.inputs[7])
    _l(nt, col.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.88
    bp = _n(nt, "ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.6
    bp.inputs["Distance"].default_value = 0.0004
    _l(nt, nz.outputs["Fac"], bp.inputs["Height"])
    _l(nt, bp.outputs["Normal"], b.inputs["Normal"])
    return m


# ------------------------------------------------------------------ parts

MAT = {}


def mats():
    pg = polymer_group()
    MAT["poly"] = material_from_group("Polymer", pg)
    MAT["polyedge"] = material_from_group("Polymer Edge", pg)
    MAT["polyedge"].node_tree.nodes["Group"].inputs["Is Edge"].default_value = 1.0
    gm = material_from_group("Gunmetal", steel_group())
    gm.node_tree.nodes["Group"].inputs["Colour"].default_value = (0.09, 0.09, 0.10, 1.0)
    gm.node_tree.nodes["Group"].inputs["Roughness"].default_value = 0.34
    MAT["gunmetal"] = gm
    gl = material_from_group("Gloss Black", rubber_group())
    gl.node_tree.nodes["Group"].inputs["Colour"].default_value = (0.018, 0.018, 0.02, 1.0)
    gl.node_tree.nodes["Group"].inputs["Roughness"].default_value = 0.2
    gl.node_tree.nodes["Group"].inputs["Grain"].default_value = 0.1
    MAT["gloss"] = gl
    vd = material_from_group("Void", rubber_group())
    vd.node_tree.nodes["Group"].inputs["Colour"].default_value = (0.006, 0.006, 0.007, 1.0)
    vd.node_tree.nodes["Group"].inputs["Grain"].default_value = 0.0
    MAT["void"] = vd
    MAT["steel"] = material_from_group("Steel", steel_group())
    MAT["rubber"] = material_from_group("Rubber", rubber_group())
    MAT["lcd"] = material_from_group("LCD", lcd_group())
    MAT["red"] = emit_material("RedLED", (1.0, 0.03, 0.02, 1.0), 6.0)
    green = material_from_group("RubberGreen", rubber_group())
    green.node_tree.nodes["Group"].inputs["Colour"].default_value = P["green_colour"]
    MAT["green"] = green
    MAT["backdrop"] = backdrop_material()


def put(ob, mat, bevel=None, segs=None):
    """Assign material and bevel a small part by angle (tier width in mm)."""
    ob.data.materials.append(MAT[mat])
    if bevel is not False:
        hard_edges(ob, width_mm=bevel if bevel else P["bevel_plate_mm"], segments=segs or P["bevel_segments"])
    return ob


def plate(key, mat="poly", bevel=None, r=3.0, cutters=(), name=None, z=None, edge="auto", groove=0.0):
    """A plate from a traced outline: booleans first, then edge weights by class, then a weighted bevel.
    Chamfer faces go to a second material (polymer edge, or steel for a machined look)."""
    z0, z1 = z or Z[key]
    out = rounded_outline(pl(LAYOUT[key]), r, 4)
    ob = extrude_outline(name or key, out, z0, z1 - z0)
    cutters = list(cutters)
    if groove:
        cutters.append(ring_cutter(f"ring_{key}", out, groove, P["groove_mm"], z1 - 0.5, z1 + 1.5))
    if cutters:
        cut(ob, cutters)
    weight_edges(ob, top=1.0, vert=0.35)
    ob.data.materials.clear()
    ob.data.materials.append(MAT[mat])
    em = -1
    if edge == "auto":
        edge = "polyedge" if mat == "poly" else None
    if edge:
        ob.data.materials.append(MAT[edge])
        em = 1
    hard_edges(ob, width_mm=bevel or P["bevel_plate_mm"], segments=P["bevel_segments"], weighted=True, edge_material=em)
    return ob


def rr_box(name, cx_px, cy_px, w, h, z0, z1, r=1.0, rot=0.0):
    cx, cy = pp(cx_px, cy_px)
    return extrude_outline(name, rect_outline(cx, cy, w, h, r, rot, 4), z0, z1 - z0)


def build_body():
    tm_cut = []
    # LCD pocket, rack pocket, ON/OFF slot
    lx, ly = pp(*LCD_C)
    tm_cut.append(extrude_outline("c_lcd", rect_outline(lx, ly, LCD_BEZEL[0] + 6.5, LCD_BEZEL[1] + 6.5, 8.0, 0, 5), T["tm"] - 3.5, 10))
    rx, ry = pp(657, 261)
    tm_cut.append(box("c_rack", (11.6, 31.0, 8.0), (rx, ry, T["tm"] - 3.0 + 4.0)))
    sx, sy = pp(381, 437)
    tm_cut.append(box("c_slot", (13.0, 7.2, 4.0), (sx, sy, T["tm"] - 1.2 + 2.0)))
    plate("base", "void", P["bevel_hull_mm"], r=8.0, edge="void")
    plate("tm", "poly", P["bevel_plate_mm"], r=5.0, cutters=tm_cut, groove=2.4)
    lid_o = extrude_outline("c_lid", rounded_outline(pl(LAYOUT["lid"]), 3.0, 4), T["sh"] - 1.1, 6.0)
    plate("sh", "poly", P["bevel_plate_mm"], r=5.0, cutters=[lid_o], groove=2.8)
    plate("wing", "poly", P["bevel_plate_mm"], r=3.6, groove=2.2)
    plate("ms", "poly", P["bevel_plate_mm"], r=2.0)
    plate("lr", "poly", P["bevel_plate_mm"], r=4.2, groove=2.4, cutters=[
        extrude_outline("c_plug", rect_outline(*pp(708, 640), 26.0, 14.0, 6.0, math.radians(45), 5), T["lr"] - 2.5, 6.0)])
    # end cap with vent window and six slots
    vw = rr_box("c_vent", 550, 758, 33.0, 14.5, T["ec"] - 1.4, T["ec"] + 3.0, r=1.5)
    slots = []
    for row, yy in enumerate((750, 766)):
        for i in range(3):
            xx = 512 + i * 36
            slots.append(rr_box(f"c_slot{row}{i}", xx, yy, 6.5, 1.6, T["ec"] - 3.0, T["ec"] + 1.0, r=0.5))
    plate("ec", "poly", P["bevel_plate_mm"], r=3.0, cutters=[vw] + slots)
    # lower-left battery block with a steel frame
    lb_out = rounded_outline(pl(LAYOUT["lb"]), 3.0, 4)
    fr = extrude_outline("frame", offset_outline(lb_out, 1.8), 13.0, T["lb"] - 13.0 - 1.4)
    put(fr, "steel", P["bevel_small_mm"], 1)
    gx, gy = pp(372, 668)
    gcut = box("c_bar", (2.6, 46.0, 4.0), (gx, gy, T["lb"] - 0.9 + 2.0), rot_z=math.radians(-14))
    plate("lb", "green", P["bevel_plate_mm"], r=4.6, edge="steel", groove=3.0, cutters=[gcut])
    plate("wedge", "steel", P["bevel_plate_mm"], r=2.0, edge=None)
    plate("lug", "poly", P["bevel_plate_mm"], r=4.0)


def build_lcd():
    lx, ly = pp(*LCD_C)
    outer = rect_outline(lx, ly, LCD_BEZEL[0], LCD_BEZEL[1], 6.0, 0, 6)
    inner = rect_outline(lx, ly, LCD_BEZEL[0] - 4.4, LCD_BEZEL[1] - 4.4, 3.8, 0, 6)
    bez = extrude_outline("bezel", outer, T["tm"] - 3.4, 7.0)
    cut(bez, [extrude_outline("c_bez", inner, T["tm"] - 2.0, 8.0)])
    put(bez, "steel", P["bevel_small_mm"] * 1.2, 2)
    # glass quad with UVs
    import bmesh
    bm = bmesh.new()
    w, h = LCD_GLASS[0] * MM / 2, LCD_GLASS[1] * MM / 2
    zz = (T["tm"] + 2.7) * MM
    vs = [bm.verts.new((lx * MM + sx * w, ly * MM + sy * h, zz)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    f = bm.faces.new(vs)
    uv = bm.loops.layers.uv.new("UVMap")
    for loop, (u, v) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop[uv].uv = (u, v)
    me = bpy.data.meshes.new("glass")
    bm.to_mesh(me)
    bm.free()
    gl = bpy.data.objects.new("glass", me)
    bpy.context.scene.collection.objects.link(gl)
    gl.data.materials.append(MAT["lcd"])
    # dark box under the glass so nothing shows through the gap
    under = box("lcd_under", (LCD_GLASS[0] + 1, LCD_GLASS[1] + 1, 5.0), (lx, ly, T["tm"] - 0.1))
    put(under, "rubber", False)
    # corner screws on the bezel
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        s = tube("bscrew", (lx + sx * 30.3, ly + sy * 15.4, T["tm"] + 3.6), (lx + sx * 30.3, ly + sy * 15.4, T["tm"] + 4.3), 0.9, segs=16)
        put(s, "steel", 0.15, 1)


def build_antenna():
    # pods: two parallel cylinders on the top edge, on a dark saddle
    xl, y_top_l = pp(398, 113)
    _, y_bot_l = pp(398, 195)
    xr, y_top_r = pp(460, 95)
    _, y_bot_r = pp(460, 195)
    z = T["tm"] + 8.0
    sad = extrude_outline("saddle", rect_outline(*pp(430, 172), 34.0, 20.0, 1.5, 0, 3), 13.0, T["tm"] + 0.5 - 13.0)
    put(sad, "poly", P["bevel_small_mm"], 1)
    for nm, x, y0, y1, r in (("podL", xl, y_bot_l, y_top_l, 8.6), ("podR", xr, y_bot_r, y_top_r, 8.2)):
        body = tube(nm, (x, y0, z), (x, y1, z), r, segs=48)
        put(body, "gunmetal", P["bevel_small_mm"], 2)
        for t in (0.28, 0.62):
            yy = y0 + (y1 - y0) * t
            ring = tube(nm + "ring", (x, yy - 0.7, z), (x, yy + 0.7, z), r + 0.18, segs=48)
            put(ring, "steel", 0.15, 1)
        cap = tube(nm + "cap", (x, y1 - 0.2, z), (x, y1 + 2.2, z), r * 0.72, r * 0.6, segs=32)
        put(cap, "steel", 0.2, 1)
    # antenna: steel collar, rubber whip, resting its tip on the table
    ax, ay0 = xl, y_top_l + 2.2
    tilt = math.radians(14.0)
    lean = math.radians(-6.0)
    d = Vector((math.sin(lean) * math.cos(tilt), math.cos(lean) * math.cos(tilt), -math.sin(tilt)))
    p0 = Vector((ax, ay0, z))

    def at(s):
        return p0 + d * s
    collar = tube("collar", at(0), at(12.0), 3.7, segs=40)
    put(collar, "steel", 0.15, 1)
    for t in (1.2, 6.0, 10.8):
        band = tube("collarband", at(t - 0.5), at(t + 0.5), 3.95, segs=40)
        put(band, "steel", 0.1, 1)
    whip = tube("whip", at(12.0), at(P["antenna_len"]), 3.2, 2.6, segs=32)
    put(whip, "gloss", 0.2, 2)
    ring = tube("whipring", at(P["antenna_len"] - 1.0), at(P["antenna_len"] + 0.4), 3.0, segs=32)
    put(ring, "steel", 0.1, 1)
    tip = tube("tip", at(P["antenna_len"] + 0.4), at(P["antenna_len"] + 7.5), 3.9, 4.1, segs=32)
    put(tip, "rubber", 0.6, 2)


def build_dial():
    dx, dy = pp(277, 310)
    gx, gy = pp(263, 323)
    g = gear("gearwheel", 26, 17.0, 14.5, 4.2, z0_mm=T["wedge"] - 5.0, centre=(gx, gy))
    put(g, "rubber", 0.3, 1)
    disc = tube("dial", (dx, dy, T["wedge"]), (dx, dy, T["wedge"] + 4.0), 14.2, segs=64)
    put(disc, "steel", 0.5, 2)
    face = tube("dialface", (dx, dy, T["wedge"] + 4.0), (dx, dy, T["wedge"] + 4.5), 9.8, segs=64)
    put(face, "rubber", 0.15, 1)
    cap = tube("dialcap", (dx, dy, T["wedge"] + 4.5), (dx, dy, T["wedge"] + 5.4), 6.4, segs=48)
    put(cap, "rubber", 0.2, 1)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        b = box("ymark", (4.6, 0.7, 0.4), (dx + math.cos(a) * 2.4, dy + math.sin(a) * 2.4, T["wedge"] + 5.6), rot_z=a)
        put(b, "steel", False)
    pin = tube("pin", (pp(292, 285)[0], pp(292, 285)[1], T["wedge"] + 4.0), (pp(305, 268)[0], pp(305, 268)[1], T["wedge"] + 6.4), 0.9, segs=16)
    put(pin, "steel", 0.15, 1)
    # left screw boss with a screw
    bx, by = pp(278, 460)
    boss = tube("boss", (bx, by, T["lug"] - 0.5), (bx, by, T["lug"] + 5.0), 6.2, segs=32)
    put(boss, "rubber", 0.4, 1)
    sc = tube("bossscrew", (bx, by, T["lug"] + 5.0), (bx, by, T["lug"] + 6.1), 2.8, segs=24)
    put(sc, "steel", 0.2, 1)
    # locking dial, lower-left
    lx, ly = pp(335, 770)
    ld = tube("lockdial", (lx, ly, T["lb"]), (lx, ly, T["lb"] + 1.8), 6.3, segs=48)
    put(ld, "steel", 0.3, 1)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        b = box("lockmark", (3.4, 0.6, 0.3), (lx + math.cos(a) * 1.8, ly + math.sin(a) * 1.8, T["lb"] + 1.9), rot_z=a)
        put(b, "rubber", False)


def build_controls():
    # selector knob with lever
    kx, ky = pp(377, 368)
    ring = tube("knobring", (kx, ky, T["tm"]), (kx, ky, T["tm"] + 1.0), 6.4, segs=48)
    put(ring, "rubber", 0.2, 1)
    knob = tube("knob", (kx, ky, T["tm"] + 1.0), (kx, ky, T["tm"] + 6.0), 5.0, 4.6, segs=48)
    put(knob, "rubber", 0.4, 2)
    lev = box("lever", (3.4, 10.0, 4.4), (kx + 0.6, ky + 4.0, T["tm"] + 8.2))
    put(lev, "rubber", 0.4, 2)
    # LED
    lx, ly = pp(413, 358)
    led = tube("led", (lx, ly, T["tm"]), (lx, ly, T["tm"] + 1.4), 2.2, 1.8, segs=24)
    led.data.materials.append(MAT["red"])
    hard_edges(led, 0.5, 3)
    # ON/OFF slider
    sx, sy = pp(381, 437)
    sl = box("slider", (6.2, 5.0, 3.4), (sx, sy, T["tm"] - 1.2 + 1.7))
    put(sl, "steel", 0.3, 1)
    for k in (-1, 0, 1):
        r = box("sgroove", (0.5, 4.2, 0.3), (sx + k * 1.3, sy, T["tm"] + 2.3), )
        put(r, "rubber", False)
    # round button
    bx, by = pp(660, 350)
    btn = tube("button", (bx, by, T["tm"]), (bx, by, T["tm"] + 1.8), 4.6, 4.2, segs=40)
    put(btn, "poly", 0.5, 2)
    # thumb rack
    rx, ry = pp(657, 261)
    ribs = []
    for i in range(9):
        ribs.append(box("rib", (8.0, 2.1, 3.0), (rx, ry - 13.6 + i * 3.4, T["tm"] - 3.0 + 1.5)))
    rk = join(ribs, "rack")
    put(rk, "gunmetal", 0.25, 1)
    # tabs and latches
    tx, ty = pp(577, 148)
    put(box("tab", (4.2, 11.0, 11.0), (tx, ty, 13.0 + 5.5)), "poly", P["bevel_small_mm"], 1)
    hx, hy = pp(358, 172)
    put(box("hook", (6.0, 7.0, 8.0), (hx, hy, 13.0 + 4.0)), "steel", P["bevel_small_mm"], 1)
    # lid latch
    lx2, ly2 = pp(662, 492)
    put(box("latch", (8.0, 5.6, 2.4), (lx2, ly2, T["sh"] - 1.1 + 0.7)), "rubber", P["bevel_small_mm"], 1)
    # screws
    for px_, py_, zt in ((480, 474, T["sh"]), (535, 601, T["sh"]), (657, 594, T["lr"])):
        x, y = pp(px_, py_)
        s = tube("screw", (x, y, zt), (x, y, zt + 0.9), 1.9, segs=24)
        put(s, "steel", 0.15, 1)
    # end cap: steel cylinder with a knurled ring, and the cord plug
    cx, cy = pp(652, 757)
    cy_ = tube("pivot", (cx - 11.0, cy, T["ec"] + 1.0), (cx + 11.0, cy, T["ec"] + 1.0), 7.4, segs=48)
    put(cy_, "steel", 0.4, 2)
    nx, ny = pp(693, 745)
    kn = knurled_cylinder("endknurl", 5.4, 3.0, 40, 0.5, (nx, ny, T["ec"] + 1.0), "X")
    put(kn, "rubber", 0.1, 1)


def decal_material(png):
    m = bpy.data.materials.new("Decal " + png)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    img = bpy.data.images.load(str(EXP["assets"] / png))
    img.colorspace_settings.name = "sRGB"
    tx = _n(nt, "ShaderNodeTexImage", image=img, interpolation="Linear")
    _l(nt, tx.outputs["Color"], b.inputs["Base Color"])
    _l(nt, tx.outputs["Alpha"], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = 0.55
    b.inputs["Specular IOR Level"].default_value = 0.2
    return m


def decal(name, png, uv, centre_px, size_mm, z_mm, rot_deg=0.0):
    """A flat printed-label plane 0.02 mm above a surface. uv = (u0, v0, u1, v1) crop of the image."""
    import bmesh
    if png not in MAT:
        MAT[png] = decal_material(png)
    cx, cy = pp(*centre_px)
    w, h = size_mm[0] * MM / 2, size_mm[1] * MM / 2
    ca, sa = math.cos(math.radians(rot_deg)), math.sin(math.radians(rot_deg))
    bm = bmesh.new()
    vs = []
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        x, y = sx * w, sy * h
        vs.append(bm.verts.new((cx * MM + x * ca - y * sa, cy * MM + x * sa + y * ca, z_mm * MM)))
    f = bm.faces.new(vs)
    lay = bm.loops.layers.uv.new("UVMap")
    for loop, (u, v) in zip(f.loops, ((uv[0], uv[1]), (uv[2], uv[1]), (uv[2], uv[3]), (uv[0], uv[3]))):
        loop[lay].uv = (u, v)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(MAT[png])
    ob.visible_shadow = False
    return ob


def build_decals():
    """Tertiary detail: logo, lid text, panel labels and arrows (drawn by make_decals.py)."""
    decal("logo", "dec_logo.png", (0, 0, 1, 1), (466, 418), (19.0, 7.6), T["sh"] + 0.02)
    decal("lidtext", "dec_lid.png", (0, 0, 1, 1), (601, 413), (15.0, 4.7), T["sh"] - 1.1 + 0.02)
    cell = lambda k, row: (k / 4, 0.75 - 0.25 * row if row == 0 else 0.25, (k + 1) / 4, 1.0 if row == 0 else 0.5)
    decal("lab_power", "dec_labels.png", cell(0, 0), (446, 341), (9.5, 2.4), T["tm"] + 0.02)
    decal("lab_onoff", "dec_labels.png", cell(1, 0), (372, 412), (9.5, 2.4), T["tm"] + 0.02)
    decal("lab_insert", "dec_labels.png", cell(2, 0), (398, 588), (9.0, 2.3), T["lb"] + 0.02)
    for i, (x, y, z) in enumerate(((497, 466, T["sh"] + 0.02), (561, 584, T["sh"] + 0.02), (680, 606, T["lr"] + 0.02))):
        decal(f"arrow{i}", "dec_labels.png", cell(i, 1), (x, y), (3.6, 3.6), z, 180.0 if i == 2 else 0.0)


def build_cord():
    # jack cylinder on the top-right corner
    jx, jy = pp(684, 168)
    jz = T["tm"] + 3.5
    jack = tube("jack", (jx - 8.0, jy, jz), (jx + 12.0, jy - 1.5, jz), 3.4, segs=32)
    put(jack, "rubber", 0.3, 1)
    jr = tube("jackring", (jx + 6.0, jy - 0.7, jz), (jx + 9.0, jy - 1.0, jz), 3.7, segs=32)
    put(jr, "steel", 0.15, 1)
    end = Vector((jx + 12.0, jy - 1.5, jz))
    # cord path on the table, right of the body
    pts = [end, Vector(pp(722, 190) + (14.0,)), Vector(pp(738, 214) + (9.6,)),
           Vector(pp(752, 270) + (7.6,)), Vector(pp(760, 360) + (7.6,)), Vector(pp(762, 450) + (7.6,)),
           Vector(pp(758, 530) + (7.6,)), Vector(pp(744, 566) + (8.4,))]
    cord = helix_cord("cord", pts, P["cord_coil_r"], P["cord_wire_r"], P["cord_turns"], ramp_mm=9.0, wobble=0.04)
    cord.data.materials.append(MAT["rubber"])
    # plug in its pocket
    px_, py_ = pp(708, 640)
    d = Vector((math.cos(math.radians(45)), math.sin(math.radians(45)), 0))
    c = Vector((px_, py_, T["lr"] - 2.5 + 4.6))
    plug = tube("plug", c - d * 9.5, c + d * 9.5, 5.6, segs=40)
    put(plug, "rubber", 1.2, 2)
    gloss = tube("plugcap", c + d * 9.5, c + d * 11.0, 4.2, 3.0, segs=32)
    put(gloss, "steel", 0.3, 1)
    # thin lead from the last coil loop to the plug (was missing in v01: the plug floated)
    a0 = Vector(pp(744, 566) + (8.4,))
    a1 = Vector((a0.x - 1.5, a0.y - 7.0, 11.0))
    a2 = Vector((c.x + d.x * 9.0, c.y + d.y * 9.0, c.z + 3.0))
    for n_, (p, q) in enumerate(((a0, a1), (a1, a2))):
        put(tube(f"lead{n_}", p, q, 0.9, segs=16), "rubber", False)


# ------------------------------------------------------------------ scene

def add_backdrop():
    bpy.ops.mesh.primitive_plane_add(size=2.5, location=(0, 0, 0))
    bd = bpy.context.active_object
    bd.name = "Backdrop"
    bd.data.materials.append(MAT["backdrop"])
    return bd


def add_camera(scene, view):
    tx, ty = pp(*P["cam_target"])
    if view == "plan":
        cx, cy = pp(475, 475)
        bpy.ops.object.camera_add(location=(cx * MM, cy * MM, 0.6))
        cam = bpy.context.active_object
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = 950.0 / S_PX * MM
        scene.render.resolution_x = scene.render.resolution_y = 950
        scene.camera = cam
        return cam
    phi, elev = math.radians(P["cam_azim"]), math.radians(P["cam_elev"])
    f = Vector((math.sin(phi), math.cos(phi), 0.0))
    tgt = Vector((tx * MM, ty * MM, 0.008))
    loc = tgt - f * P["cam_dist"] * math.cos(elev) + Vector((0, 0, P["cam_dist"] * math.sin(elev)))
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.active_object
    cam.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = P["cam_lens"]
    cam.data.sensor_width = 36.0
    cam.data.shift_x, cam.data.shift_y = P["cam_shift"]
    cam.data.clip_start = 0.02
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = P["res_x"], P["res_y"]
    return cam


def group_device():
    """Everything except the backdrop goes into one collection, so the fill can be linked to the device only."""
    dev = bpy.data.collections.new("Device")
    bpy.context.scene.collection.children.link(dev)
    for ob in list(bpy.context.scene.collection.objects):
        if ob.type in {"MESH", "CURVE"} and ob.name != "Backdrop":
            bpy.context.scene.collection.objects.unlink(ob)
            dev.objects.link(ob)
    return dev


def add_lights(scene, view, dev=None):
    phi = math.radians(P["cam_azim"])
    f = Vector((math.sin(phi), math.cos(phi), 0.0))
    r = Vector((math.cos(phi), -math.sin(phi), 0.0))       # camera right on the ground
    tx, ty = pp(*P["cam_target"])
    tgt = Vector((tx * MM, ty * MM, 0.01))
    if view == "plan":
        pos = tgt + Vector((0, 0, 0.5))
    else:
        pos = tgt + r * P["key_side"] + f * P["key_far"] + Vector((0, 0, P["key_dist"]))
    bpy.ops.object.light_add(type="AREA", location=pos)
    key = bpy.context.active_object
    key.name = "Key"
    key.data.shape, key.data.size = "SQUARE", P["key_size"]
    key.data.energy = 6.0 if view == "plan" else P["key_power"]
    key.rotation_euler = (tgt - pos).to_track_quat("-Z", "Y").to_euler()
    fpos = tgt - f * P["fill_front"] - r * 0.05 + Vector((0, 0, P["fill_height"]))
    bpy.ops.object.light_add(type="AREA", location=fpos)
    fill = bpy.context.active_object
    fill.name = "Fill"
    fill.data.shape, fill.data.size = "SQUARE", P["fill_size"]
    fill.data.energy = 0.0 if view == "plan" else P["fill_power"]
    fill.rotation_euler = (tgt - fpos).to_track_quat("-Z", "Y").to_euler()
    if dev is not None and P["fill_linked"]:
        fill.light_linking.receiver_collection = dev     # the fill lights the device, not the backdrop
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Strength"].default_value = P["world_strength"]
    bg.inputs["Color"].default_value = (0.55, 0.55, 0.58, 1.0)
    scene.world = world


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="wip", help="render name, saved to renders/<out>.png")
    ap.add_argument("--samples", type=int, default=128)
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--view", default="hero", choices=("hero", "plan"))
    ap.add_argument("--clay", action="store_true")
    ap.add_argument("--mirror", action="store_true")
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
        ("Glow", "NodeSocketFloat", 0.0, 0.0, 2.0),
        ("Glow Size", "NodeSocketFloat", 0.3, 0.0, 1.0),
        ("Glow Threshold", "NodeSocketFloat", 1.5, 0.0, 4.0),
        ("Chroma", "NodeSocketFloat", 0.0, 0.0, 0.05),
    ])
    glare = ng.nodes.new("CompositorNodeGlare")
    lens = ng.nodes.new("CompositorNodeLensdist")
    ng.links.new(gi.outputs["Image"], glare.inputs["Image"])
    if LEGACY:
        glare.glare_type, glare.quality = "FOG_GLOW", "HIGH"
        glare.mix = -1.0
        glare.size = 7
        glare.threshold = 1.5
    else:
        glare.inputs["Type"].default_value = "Fog Glow"
        for src, dst in (("Glow", "Strength"), ("Glow Size", "Size"), ("Glow Threshold", "Threshold")):
            ng.links.new(gi.outputs[src], glare.inputs[dst])
    ng.links.new(glare.outputs["Image"], lens.inputs["Image"])
    ng.links.new(gi.outputs["Chroma"], lens.inputs["Dispersion"])
    ng.links.new(lens.outputs["Image"], go.inputs["Image"])
    auto_layout(ng)
    return ng


def build_scene(view="hero"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    enable_gpu(scene)
    mats()
    add_backdrop()
    build_body()
    build_lcd()
    build_antenna()
    build_dial()
    build_controls()
    build_cord()
    build_decals()
    dev = group_device()
    add_camera(scene, view)
    add_lights(scene, view, dev)
    scene.view_settings.view_transform = P["view"]
    scene.view_settings.exposure = P["exposure"]
    scene.cycles.use_denoising = True
    scene.cycles.denoising_input_passes = "RGB_ALBEDO_NORMAL"
    scene.cycles.denoising_prefilter = "ACCURATE"
    scene.cycles.sample_clamp_indirect = 3.0
    scene.cycles.filter_width = 1.2
    scene.cycles.max_bounces = 6
    scene.cycles.glossy_bounces = 4
    scene.cycles.caustics_reflective = False
    scene.cycles.caustics_refractive = False
    if P["clay"] or P["mirror"]:
        ov = bpy.data.materials.new("Override")
        ov.use_nodes = True
        b = ov.node_tree.nodes["Principled BSDF"]
        if P["mirror"]:
            b.inputs["Metallic"].default_value, b.inputs["Roughness"].default_value = 1.0, 0.02
            b.inputs["Base Color"].default_value = (0.9, 0.9, 0.9, 1.0)
        else:
            b.inputs["Base Color"].default_value, b.inputs["Roughness"].default_value = (0.5, 0.5, 0.5, 1.0), 0.6
        scene.view_layers[0].material_override = ov
    how_to_tweak(HOW_TO_TWEAK)
    return scene


if __name__ == "__main__":
    args = parse_args()
    if args.clay:
        P["clay"] = True
    if args.mirror:
        P["mirror"] = True
    scene = build_scene(args.view)
    raw = EXP["renders"] / f"{args.out}_raw.exr"
    compositor(scene, post(), raw_exr=raw)
    scene.cycles.samples = args.samples
    scene.render.resolution_percentage = 100 if args.view == "plan" else round(args.scale * 100)
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
