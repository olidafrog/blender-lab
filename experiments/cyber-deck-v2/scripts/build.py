"""cyber-deck-v2: the DT-03 radio as CAD-style moulded parts, built from nothing, rendered, saved.

Run from the repo root:
  tools/blender.sh experiments/cyber-deck-v2/scripts/build.py --out v01 --samples 128 --scale 0.5
  ... --view plan          orthographic top-down, pixel-aligned to experiments/cyber-model/assets/ref_plan_rectified.png
  ... --set key=value      override any value in P
  ... --clay / --mirror    debug material overrides (correctness pass)
  ... --save               also save output/cyber-deck-v2.blend

Every shell is a plan outline lofted through a designed section (hs2.py): wall, 55 degree slope and a
2-3 mm top fillet, like the Fusion 360 original. Layout is v1's plan traced on the rectified reference
(plan px, 3.6 px per mm, origin at plan (500, 480), +x right, +y up); lengths in the kit are millimetres.
"""
import argparse
import ast
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import enable_gpu, experiment_paths  # noqa: E402
from nodes import auto_layout, group, how_to_tweak, material_from_group  # noqa: E402
from comp import LEGACY, compositor, post_group, use_saved_render  # noqa: E402
import hs2  # noqa: E402
from hs2 import MM, Outline, circle, cut, loft, rod, rrect, sec_cutter, sec_rod, sec_slab, sec_step, toothed  # noqa: E402

EXP = experiment_paths(__file__)

# Every value a designer might tune lives here. Override with --set key=value.
P = {
    "res_x": 1600,
    "res_y": 1200,
    # camera: v1's landmark fit (experiments/cyber-model/scripts/fit_camera.py)
    "cam_elev": 48.65,
    "cam_azim": 41.0,
    "cam_lens": 200.0,
    "cam_dist": 1.485,
    "cam_target": (451.5, 380.5),   # plan px
    "cam_shift": (0.0, 0.0),
    "view": "Standard",
    "exposure": 0.0,
    # light: backdrop key (far side, linked to the backdrop), device key (camera side, linked to the device),
    # metal card (linked to the steel parts). Keep big sources out of the flat tops' mirror direction.
    "key_power": 9.6,
    "key_size": 0.9,
    "key_dist": 0.50,
    "key_side": 0.30,
    "key_far": 0.30,
    "key_on_device": False,     # True: the far-side key also lights the device, so parts cast shadows toward the camera
    # device key: ONE small source at camera-left (advisor, v06 consult). Two 0.9 m softboxes wrapped light into
    # every gap and made tops, slopes and walls read the same; a small key casts real shadows between parts.
    "dev_power": 9.0,
    "dev_size": 0.25,
    "dev_front": 0.35,
    "dev_side": -0.45,
    "dev_height": 0.55,
    "dev_on_table": False,      # True: the device key also lights the table (the device casts its shadow there)
    "fill_power": 0.0,          # camera fill off: it lifted the gaps
    "fill_size": 1.2,
    "slope_card": 10.0,         # a big dim glossy-only card behind the camera: camera-facing slopes reflect it, tops do not
    "slope_card_size": 1.5,
    "metal_power": 10.0,         # was 24: steel read as chrome (review v07)
    "metal_size": 2.5,
    "metal_far": 0.6,
    "metal_height": 1.2,
    "world_strength": 0.12,     # the dim dome is the only ambient
    # form: heights in mm from the table, sections
    "base_top": 13.0,
    "tm_top": 22.0,
    "ub_top": 20.0,             # upper body: switches, middle strip, lower right
    "sh_top": 26.5,             # logo plate: a 6-7 mm moulded step above the upper body (review v09: 2 mm read as a bead)
    "slope_deg": 50.0,
    "fillet_step": 1.2,         # top edge of a sloped step: small, so the step reads as a flat band (reviews v09, advisor)
    "fillet_shield": 1.4,
    "moat_mm": 1.0,             # black channel cut into the lower part along the foot of each higher part
    "moat_depth": 3.0,
    "crease_mm": 0.4,           # wall-to-slope crease
    "fillet_shell": 3.0,        # top fillet of vertical-walled shells (reference 3-5 mm)
    "fillet_plate": 2.0,
    "fillet_small": 0.8,
    "gap_mm": 0.8,              # between neighbouring plates, over a black liner (review v01: gaps not black)
    "lcd_frame": 3.0,           # the raised black frame round the LCD: height above the top module, mm
    "foot_z": 1.5,              # the outer shells start this far above the table
    "undercut": (2.0, 2.5),     # ...on a foot inset 2 mm, 2.5 mm tall: the dark line round the bottom of the device
    "lcd_depth": 5.0,           # the black shield round the LCD: pocket depth and wall angle
    "lcd_wall_deg": 55.0,
    # materials
    "poly_colour": (0.085, 0.085, 0.09, 1.0),   # lighter, more diffuse polymer under a small key (advisor)
    "poly_rough": 0.36,          # satin, not clay (review v07)
    "poly_grain": 0.40,         # albedo speckle, +/- fraction (reference plates: luma std 13-26 at 1:1)
    "bead": 0.0,                 # bead-blast bump strength (0.2 at 0.4 mm read as orange peel, review v07)
    "wear": 0.5,
    "scratch": 0.35,
    "ao_dist_mm": 4.0,
    "ao_power": 2.0,
    "ao_floor": 0.05,
    "steel_colour": (0.55, 0.56, 0.58, 1.0),
    "steel_rough": 0.30,
    "rubber_colour": (0.03, 0.03, 0.033, 1.0),
    "green_colour": (0.048, 0.052, 0.058, 1.0),
    "lcd_strength": 1.5,
    "backdrop_colour": (0.16, 0.16, 0.17, 1.0),
    "backdrop_grain": 7.0,
    "contact_mm": 12.0,
    "contact_power": 2.5,
    # cord, antenna
    "cord_turns": 34,
    "cord_coil_r": 5.2,
    "cord_wire_r": 1.15,
    "antenna_len": 62.0,
    "pod_r": 4.9,                # ~10 mm barrels (review v07: 1.5x too big at 6.2)
    "pod_z": 3.0,               # pod axis above the top module (v01-v04: 5.8, the pods stood proud of the frame)
    "gear_r": 19.0,
    "alu_colour": (0.42, 0.42, 0.43, 1.0),   # light satin aluminium, rough so it never reads chrome (review v08 sampled ~125)
    "alu_rough": 0.55,
    "antenna_tilt": 6.0,        # degrees down from level; the reference tip stays off the table
    "pod_top_px": (104, 98),    # plan px of the pod tops (rectified reference: ~25 mm pods)
    "clay": False,
    "mirror": False,
    "black_albedo": False,      # debug: polymer albedo 0 (what remains is reflection)
}

HOW_TO_TWEAK = """\
cyber-deck-v2 — how to tweak

Every material is ONE group node. Select an object, open the Shader Editor, change the inputs on that node.
Hover an input for its range.

- Polymer   (all dark shells)  Colour, Roughness, Fine Grain (albedo speckle), Bead Blast (micro bump),
            Wear (light wear on the rounded edges: the faces tagged "wear" by the build), Scratches,
            Crease Depth mm / Crease Black (occlusion in creases).
- Steel     (antenna collar, small steel parts)   Colour, Roughness, Grain, Wear (bright specks on rounded edges).
  The same Steel node, with its own values, drives:
    Gunmetal (pods, thumb wheels, battery strip, pivot), Aluminium (dial bracket and ring),
    Screw (domed screw heads), Bezel (LCD frame).
- DialFace / Ticks  the dial's dark face and maroon tick marks (Rubber node).
- Rubber    (cord, gear, knob, plug)   Colour, Roughness, Grain.
- LCD       (object "glass")   Strength = backlight. The text is assets/lcd.png (packed).
- Backdrop  Colour, Grain, Contact Reach mm (dark halo round the device), Contact Black.

Lights (Object Data tab: Power, Size)
- "Key Backdrop"  the table only: gradient and cast shadow.
- "Key Device"    the device only: ONE small (0.25 m) light at camera-left. It casts the shadows between parts
                  that make the gaps black. Make it bigger and the blacks go grey.
- "Card Slopes"   big dim card behind the camera, seen only in reflections: lifts the camera-facing slopes.
                  Trade-off: more lifts the slopes but greys the black gaps (25 W: p5 12 -> 19).
- "Card Metal"    a card only the steel parts see.

Post (Compositing tab): the "Post" node updates the saved render live. After F12, set "Source" to Off.

Geometry comes from experiments/cyber-deck-v2/scripts/build.py (plan outline x designed section, hs2.py).
Changes made by hand here are lost on rebuild; copy good values back into P.
"""

# ------------------------------------------------------------------ layout (plan px, v1)

S_PX = 3.6
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
    "ub": [(303, 380), (700, 380), (704, 730), (500, 730), (470, 760), (425, 760), (425, 558), (303, 558)],
    "lb": [(318, 552), (425, 552), (425, 760), (470, 796), (330, 802), (318, 782)],
    "ec": [(430, 735), (700, 722), (704, 780), (690, 795), (480, 805), (430, 790)],
    "lug": [(262, 446), (320, 438), (322, 488), (262, 480)],
    "wedge": [(250, 255), (318, 196), (328, 204), (328, 400), (318, 405), (314, 360), (280, 352), (255, 300)],
    "lid": [(552, 394), (650, 394), (668, 412), (676, 536), (608, 560), (552, 560)],
}
SCREWS = {"sh": [(480, 474), (535, 601)], "ub": [(657, 594), (330, 424), (345, 534)], "lb": [(346, 580), (402, 580)]}
LCD_C = (473.5, 265.0)
LCD_BEZEL = (64.7, 36.1)
LCD_GLASS = (58.8, 30.4)                  # a ~3 mm flat bezel round the glass (review v08: chrome tube)


def tops():
    b = P["base_top"]
    return {"base": b, "tm": P["tm_top"], "sh": P["sh_top"], "ub": P["ub_top"], "lb": b + 2.0,
            "ec": b + 8.0, "wedge": P["tm_top"] - 0.5, "lug": b + 5.0}


# ------------------------------------------------------------------ node helpers

def _n(nt, kind, **props):
    n = nt.nodes.new(kind)
    for k, v in props.items():
        setattr(n, k, v)
    return n


def _l(nt, a, b):
    nt.links.new(a, b)


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


def _mapr(nt, val, lo, hi, out_lo=0.0, out_hi=1.0):
    m = _n(nt, "ShaderNodeMapRange", clamp=True)
    m.inputs[1].default_value, m.inputs[2].default_value = lo, hi
    m.inputs[3].default_value, m.inputs[4].default_value = out_lo, out_hi
    _l(nt, val, m.inputs[0])
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


def _noise(nt, coord, scale, detail=2.0, rough=0.5):
    nz = _n(nt, "ShaderNodeTexNoise", noise_dimensions="3D")
    nz.inputs["Scale"].default_value, nz.inputs["Detail"].default_value = scale, detail
    nz.inputs["Roughness"].default_value = rough
    _l(nt, coord, nz.inputs["Vector"])
    return nz.outputs["Fac"]


def _bump(nt, height, strength, dist):
    bp = _n(nt, "ShaderNodeBump")
    bp.inputs["Distance"].default_value = dist
    _l(nt, height, bp.inputs["Height"])
    if hasattr(strength, "bl_rna"):
        _l(nt, strength, bp.inputs["Strength"])
    else:
        bp.inputs["Strength"].default_value = strength
    return bp.outputs["Normal"]


# ------------------------------------------------------------------ materials

def polymer_group():
    """Satin polymer, one node. Wear reads the FACE attribute "wear" that the loft writes on the convex top
    fillets (hs2.py): speckled, lighter, a little glossier, only on the rounded edges (reference 4K crops)."""
    ng, gi, go = group("Polymer", [
        ("Colour", "NodeSocketColor", P["poly_colour"], None, None),          # linear albedo
        ("Roughness", "NodeSocketFloat", P["poly_rough"], 0.0, 1.0),          # 0 gloss, 1 matte
        ("Fine Grain", "NodeSocketFloat", P["poly_grain"], 0.0, 0.5),         # albedo speckle, +/- fraction
        ("Bead Blast", "NodeSocketFloat", P["bead"], 0.0, 0.5),               # micro bump strength
        ("Wear", "NodeSocketFloat", P["wear"], 0.0, 1.0),                     # light wear on rounded edges
        ("Scratches", "NodeSocketFloat", P["scratch"], 0.0, 1.0),             # drawn stroke mask
        ("Crease Depth mm", "NodeSocketFloat", P["ao_dist_mm"], 0.5, 10.0),   # occlusion reach
        ("Crease Black", "NodeSocketFloat", P["ao_floor"], 0.0, 1.0),         # albedo left in the deepest crease
    ], [("Shader", "NodeSocketShader")])
    tc = _n(ng, "ShaderNodeTexCoord")
    ob = tc.outputs["Object"]
    # creases
    ao = _n(ng, "ShaderNodeAmbientOcclusion", samples=8, inside=False, only_local=False)
    _l(ng, _math(ng, "MULTIPLY", gi.outputs["Crease Depth mm"], 0.001), ao.inputs["Distance"])
    aov = _mix_f(ng, _math(ng, "POWER", ao.outputs["AO"], P["ao_power"]), gi.outputs["Crease Black"], 1.0)
    # mottle and fine grain on the albedo
    mot = _noise(ng, ob, 55.0)
    mot_c = _math(ng, "ADD", 0.9, _math(ng, "MULTIPLY", mot, 0.2))
    mot_r = _math(ng, "ADD", 0.8, _math(ng, "MULTIPLY", mot, 0.4))
    fr = _noise(ng, ob, 1900.0, 3.0)
    mot_r = _math(ng, "MULTIPLY", mot_r, _math(ng, "ADD", 0.8, _math(ng, "MULTIPLY", fr, 0.4)))   # speckle in the roughness
    fg = _noise(ng, ob, 1900.0, 3.0)
    grain_c = _math(ng, "ADD", _math(ng, "SUBTRACT", 1.0, gi.outputs["Fine Grain"]),
                    _math(ng, "MULTIPLY", fg, _math(ng, "MULTIPLY", gi.outputs["Fine Grain"], 2.0)))
    # wear: tagged faces x speckle
    at = _n(ng, "ShaderNodeAttribute", attribute_type="GEOMETRY", attribute_name="wear")
    spk = _mapr(ng, _noise(ng, ob, 900.0, 4.0, 0.6), 0.48, 0.62)
    patch = _mapr(ng, _noise(ng, ob, 60.0, 2.0), 0.35, 0.6)
    wear = _math(ng, "MULTIPLY", _math(ng, "MULTIPLY", at.outputs["Fac"], _math(ng, "MULTIPLY", spk, patch)),
                 gi.outputs["Wear"])
    # scratches: drawn stroke mask, top-down in object space
    simg = bpy.data.images.load(str(EXP["assets"] / "scratches.png"))
    simg.colorspace_settings.name = "Non-Color"
    mp = _n(ng, "ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (4.0, 4.0, 1.0)
    mp.inputs["Location"].default_value = (0.4, 0.44, 0.0)
    _l(ng, ob, mp.inputs["Vector"])
    st = _n(ng, "ShaderNodeTexImage", image=simg, interpolation="Linear", extension="CLIP")
    _l(ng, mp.outputs[0], st.inputs["Vector"])
    scr = _math(ng, "MULTIPLY", st.outputs["Color"], gi.outputs["Scratches"])
    marks = _math(ng, "MAXIMUM", wear, scr)
    scuff = _n(ng, "ShaderNodeRGB")
    scuff.outputs[0].default_value = (0.24, 0.24, 0.25, 1.0)
    base = _mix_col(ng, marks, gi.outputs["Colour"], scuff.outputs[0])
    sc = _n(ng, "ShaderNodeVectorMath", operation="SCALE")
    _l(ng, base, sc.inputs[0])
    _l(ng, _math(ng, "MULTIPLY", _math(ng, "MULTIPLY", aov, mot_c), grain_c), sc.inputs["Scale"])
    bsdf = _n(ng, "ShaderNodeBsdfPrincipled")
    _l(ng, sc.outputs[0], bsdf.inputs["Base Color"])
    _l(ng, aov, bsdf.inputs["Specular IOR Level"])
    _l(ng, _mix_f(ng, marks, _math(ng, "MULTIPLY", gi.outputs["Roughness"], mot_r), 0.36), bsdf.inputs["Roughness"])
    _l(ng, _bump(ng, _noise(ng, ob, 2200.0, 1.0), gi.outputs["Bead Blast"], 0.0002), bsdf.inputs["Normal"])
    _l(ng, bsdf.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def steel_group():
    ng, gi, go = group("Steel", [
        ("Colour", "NodeSocketColor", P["steel_colour"], None, None),
        ("Roughness", "NodeSocketFloat", P["steel_rough"], 0.0, 1.0),
        ("Grain", "NodeSocketFloat", 0.3, 0.0, 1.0),
        ("Wear", "NodeSocketFloat", 0.6, 0.0, 1.0),                # bright chipped specks on rounded edges
    ], [("Shader", "NodeSocketShader")])
    tc = _n(ng, "ShaderNodeTexCoord")
    mp = _n(ng, "ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 6.0, 1.0)
    _l(ng, tc.outputs["Object"], mp.inputs["Vector"])
    at = _n(ng, "ShaderNodeAttribute", attribute_type="GEOMETRY", attribute_name="wear")
    spk = _mapr(ng, _noise(ng, tc.outputs["Object"], 900.0, 4.0, 0.6), 0.5, 0.6)
    w = _math(ng, "MULTIPLY", _math(ng, "MULTIPLY", at.outputs["Fac"], spk), gi.outputs["Wear"])
    b = _n(ng, "ShaderNodeBsdfPrincipled")
    b.inputs["Metallic"].default_value = 1.0
    white = _n(ng, "ShaderNodeRGB")
    white.outputs[0].default_value = (0.9, 0.9, 0.92, 1.0)
    _l(ng, _mix_col(ng, w, gi.outputs["Colour"], white.outputs[0]), b.inputs["Base Color"])
    _l(ng, _mix_f(ng, w, gi.outputs["Roughness"], 0.15), b.inputs["Roughness"])
    _l(ng, _bump(ng, _noise(ng, mp.outputs[0], 3500.0, 1.0), gi.outputs["Grain"], 0.0001), b.inputs["Normal"])
    _l(ng, b.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def rubber_group():
    ng, gi, go = group("Rubber", [
        ("Colour", "NodeSocketColor", P["rubber_colour"], None, None),
        ("Roughness", "NodeSocketFloat", 0.62, 0.0, 1.0),
        ("Grain", "NodeSocketFloat", 0.4, 0.0, 1.0),
    ], [("Shader", "NodeSocketShader")])
    tc = _n(ng, "ShaderNodeTexCoord")
    b = _n(ng, "ShaderNodeBsdfPrincipled")
    _l(ng, gi.outputs["Colour"], b.inputs["Base Color"])
    _l(ng, gi.outputs["Roughness"], b.inputs["Roughness"])
    _l(ng, _bump(ng, _noise(ng, tc.outputs["Object"], 3000.0), gi.outputs["Grain"], 0.00015), b.inputs["Normal"])
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


def backdrop_group():
    ng, gi, go = group("Backdrop", [
        ("Colour", "NodeSocketColor", P["backdrop_colour"], None, None),
        ("Grain", "NodeSocketFloat", P["backdrop_grain"], 0.0, 12.0),
        ("Contact Reach mm", "NodeSocketFloat", P["contact_mm"], 1.0, 40.0),
        ("Contact Black", "NodeSocketFloat", 0.03, 0.0, 1.0),
    ], [("Shader", "NodeSocketShader")])
    b = _n(ng, "ShaderNodeBsdfPrincipled")
    tc = _n(ng, "ShaderNodeTexCoord")
    n1 = _noise(ng, tc.outputs["Object"], 2600.0, 0.0)
    n2 = _noise(ng, tc.outputs["Object"], 5200.0, 0.0)
    mix2 = _math(ng, "ADD", _math(ng, "MULTIPLY", n1, 0.6), _math(ng, "MULTIPLY", n2, 0.4))
    fac = _math(ng, "ADD", _math(ng, "MULTIPLY", _math(ng, "SUBTRACT", mix2, 0.5),
                                 _math(ng, "MULTIPLY", gi.outputs["Grain"], 2.0)), 1.0)
    col = _n(ng, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY")
    col.inputs[0].default_value = 1.0
    _l(ng, gi.outputs["Colour"], col.inputs[6])
    _l(ng, fac, col.inputs[7])
    cao = _n(ng, "ShaderNodeAmbientOcclusion", samples=16, inside=False, only_local=False)
    _l(ng, _math(ng, "MULTIPLY", gi.outputs["Contact Reach mm"], 0.001), cao.inputs["Distance"])
    cfac = _mix_f(ng, _math(ng, "POWER", cao.outputs["AO"], P["contact_power"]), gi.outputs["Contact Black"], 1.0)
    csc = _n(ng, "ShaderNodeVectorMath", operation="SCALE")
    _l(ng, col.outputs[2], csc.inputs[0])
    _l(ng, cfac, csc.inputs["Scale"])
    _l(ng, csc.outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.88
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


MAT = {}


def mats():
    MAT["poly"] = material_from_group("Polymer", polymer_group())
    if P["black_albedo"]:
        MAT["poly"].node_tree.nodes["Group"].inputs["Colour"].default_value = (0, 0, 0, 1)
    sg = steel_group()
    MAT["steel"] = material_from_group("Steel", sg)
    gm = material_from_group("Gunmetal", sg)
    gm.node_tree.nodes["Group"].inputs["Colour"].default_value = (0.24, 0.24, 0.25, 1.0)
    gm.node_tree.nodes["Group"].inputs["Roughness"].default_value = 0.38
    MAT["gunmetal"] = gm
    al = material_from_group("Aluminium", sg)
    al.node_tree.nodes["Group"].inputs["Colour"].default_value = P["alu_colour"]
    al.node_tree.nodes["Group"].inputs["Roughness"].default_value = P["alu_rough"]
    al.node_tree.nodes["Group"].inputs["Wear"].default_value = 0.9
    MAT["alu"] = al
    sc = material_from_group("Screw", sg)                  # matte steel: the domes read as white pearls (review v06)
    sc.node_tree.nodes["Group"].inputs["Colour"].default_value = (0.32, 0.32, 0.33, 1.0)
    sc.node_tree.nodes["Group"].inputs["Roughness"].default_value = 0.42
    MAT["screw"] = sc
    bz = material_from_group("Bezel", sg)
    bz.node_tree.nodes["Group"].inputs["Colour"].default_value = (0.30, 0.30, 0.31, 1.0)
    bz.node_tree.nodes["Group"].inputs["Roughness"].default_value = 0.42
    MAT["bezel"] = bz
    rg = rubber_group()
    MAT["rubber"] = material_from_group("Rubber", rg)
    gl = material_from_group("Gloss Black", rg)
    gl.node_tree.nodes["Group"].inputs["Colour"].default_value = (0.018, 0.018, 0.02, 1.0)
    gl.node_tree.nodes["Group"].inputs["Roughness"].default_value = 0.22
    MAT["gloss"] = gl
    vd = material_from_group("Void", rg)
    vd.node_tree.nodes["Group"].inputs["Colour"].default_value = (0.004, 0.004, 0.005, 1.0)
    vd.node_tree.nodes["Group"].inputs["Roughness"].default_value = 0.9
    MAT["void"] = vd
    green = material_from_group("RubberGreen", rg)
    green.node_tree.nodes["Group"].inputs["Colour"].default_value = P["green_colour"]
    MAT["green"] = green
    MAT["lcd"] = material_from_group("LCD", lcd_group())
    fc = material_from_group("DialFace", rg)
    fc.node_tree.nodes["Group"].inputs["Colour"].default_value = (0.045, 0.045, 0.048, 1.0)
    fc.node_tree.nodes["Group"].inputs["Roughness"].default_value = 0.5
    MAT["face"] = fc
    tk = material_from_group("Ticks", rg)
    tk.node_tree.nodes["Group"].inputs["Colour"].default_value = (0.20, 0.035, 0.03, 1.0)
    tk.node_tree.nodes["Group"].inputs["Grain"].default_value = 0.0
    MAT["tick"] = tk
    MAT["red"] = emit_material("RedLED", (1.0, 0.03, 0.02, 1.0), 6.0)
    MAT["backdrop"] = material_from_group("Backdrop", backdrop_group())


# ------------------------------------------------------------------ shells

def shell(key, sec, z0, mat="poly", r_cv=6.0, r_cc=3.0, gap=None, name=None, seg=10):
    """A shell from LAYOUT[key]: plan outline (gap/2 inset so neighbours part), lofted through sec."""
    o = Outline.auto(pl(LAYOUT[key]), r_cv, r_cc, seg=seg)
    g = P["gap_mm"] if gap is None else gap
    if g:
        o = o.inset(g / 2)
    hs2.check_outline(key, o, sec)
    return loft(name or key, o, sec, z0=z0, mat=MAT[mat])


def pocket(outline, depth, top, rim=1.0, floor=0.5, mat=None, name="c"):
    c = loft(name, outline, sec_cutter(depth, top, rim, floor))
    if mat:
        c.data.materials.append(MAT[mat])
    return c


def bracket_outline():
    """Plan outline of the dial bracket: an arc round the dial centre, then a tapered arm to the top."""
    cx, cy, R = 277.0, 310.0, 64.0                           # plan px (y down)
    pts = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for a in range(-12, 252, 12)]
    pts += [(282, 214), (318, 188), (338, 198), (340, 282)]
    return Outline.auto(pl(pts), 4.0, 3.0, seg=6, sweep=12.0)


def moat(upper, top_lower, width=None):
    """Cutter for the channel along the foot of LAYOUT[upper], cut into a lower neighbour whose top is top_lower.
    Black walls (Boolean material transfer)."""
    base = bracket_outline() if upper == "wedge" else Outline.auto(pl(LAYOUT[upper]), 6.0, 3.0)
    o = base.inset(-(P["gap_mm"] / 2 + (width or P["moat_mm"])))
    return loft("c_moat", o, [(0.0, top_lower - P["moat_depth"], "crisp"), (0.0, top_lower + 3.0, "crisp")], mat=MAT["void"])


def screw_dimple(xy, top):
    return pocket(circle(xy[0], xy[1], 3.0, 40), 1.0, top, rim=0.6, floor=0.3, name="c_dimple")


def screw_head(xy, top):
    """Domed steel button in its dimple (reference 4K crop)."""
    h = loft("screw", circle(xy[0], xy[1], 1.8, 40), sec_slab(1.1, top_r=0.7, foot=0.0, draft=0.0, seg=5),
             z0=top - 1.0 + 0.02, mat=MAT["screw"])
    return h


def build_body():
    T = tops()
    b = P["base_top"]
    sl = P["slope_deg"]
    # chassis: vertical wall, generous top fillet, the outer skin seen on the right and bottom
    # hidden black core: the outer shells come down to the table themselves (v01-v06 set them on this slab,
    # and its rounded rim read as a tray round the whole device); every gap between shells looks into black
    shell("base", sec_slab(b - 0.03, top_r=0.0, foot=0.0, draft=0.0), 0.03, mat="void", r_cv=6.0, r_cc=4.0, gap=6.0)
    F = P["foot_z"]
    # upper body: switches, middle strip and lower right are one moulding. Its lower-left edge is the big
    # light S-band stepping down to the battery block (brightened rectified plan); it stands on a stem.
    ub = shell("ub", sec_step(T["ub"] - F, T["ub"] - F - 5.0, 50.0, P["fillet_shield"], P["crease_mm"], under=P["undercut"]), F, r_cv=7.0, r_cc=3.0)
    wx, wy = pp(360, 486)
    sx, sy = pp(381, 437)
    cut(ub, [pocket(rrect(wx, wy - i * 3.6, 6.0, 1.5, 0.6), 2.0, T["ub"], rim=0.3, floor=0.0, mat="void", name="c_wv")
             for i in range(5)] +
        [screw_dimple(pp(*s_), T["ub"]) for s_ in SCREWS["ub"]] +
        [pocket(rrect(sx, sy, 13.0, 7.2, 1.6), 1.6, T["ub"], rim=0.5, floor=0.3, name="c_slot"),
         pocket(rrect(*pp(708, 640), 26.0, 14.0, 6.0, 45.0), 3.0, T["ub"], rim=1.0, floor=1.0, name="c_plug")])
    # top module round the LCD: sloped step, raised LCD frame, thumb-wheel slot
    tm = shell("tm", sec_step(T["tm"] - F, T["tm"] - F - 6.5, sl, P["fillet_step"], P["crease_mm"], under=P["undercut"]), F, r_cv=7.0, r_cc=3.0)
    lx, ly = pp(*LCD_C)
    rx, ry = pp(657, 261)
    ftop = T["tm"] + P["lcd_frame"]
    frame = loft("lcdframe", rrect(lx - 2.0, ly + 5.0, LCD_BEZEL[0] + 18.0, LCD_BEZEL[1] + 26.0, 10.0),
                 sec_step(ftop - (T["tm"] - 1.0), 1.0, 50.0, P["fillet_step"], P["crease_mm"]), z0=T["tm"] - 1.0, mat=MAT["poly"])
    cut(frame, [loft("c_lcdf", rrect(lx, ly, LCD_BEZEL[0] + 1.0, LCD_BEZEL[1] + 1.0, 6.5),
                     sec_cutter(P["lcd_depth"] + P["lcd_frame"], ftop, rim_r=1.0, floor_r=0.0, wall_deg=P["lcd_wall_deg"]))])
    cut(tm, [loft("c_lcd", rrect(lx, ly, LCD_BEZEL[0] + 1.0, LCD_BEZEL[1] + 1.0, 6.5),
                  sec_cutter(P["lcd_depth"], T["tm"], rim_r=0.0, floor_r=0.0, wall_deg=P["lcd_wall_deg"])),
             pocket(rrect(rx, ry, 11.0, 34.0, 2.5), 7.0, T["tm"], rim=0.8, floor=0.6, mat="void", name="c_rack")])
    # logo plate on the upper body: a smaller filleted step, the lid pocket
    sh = shell("sh", sec_step(T["sh"] - (T["ub"] - 1.0), 1.5, 48.0, P["fillet_step"], P["crease_mm"]), T["ub"] - 1.0, r_cv=8.0, r_cc=4.0)
    lid = Outline.auto(pl(LAYOUT["lid"]), 3.5, 2.0)
    cut(sh, [pocket(lid, 1.2, T["sh"], rim=1.0, floor=0.5, name="c_lid")] +
        [screw_dimple(pp(*s_), T["sh"]) for s_ in SCREWS["sh"]])
    # end cap with the vent window
    ec = shell("ec", sec_step(T["ec"] - F, T["ec"] - F - 2.5, 70.0, P["fillet_shell"], 0.3, under=P["undercut"]), F, r_cv=4.0, r_cc=2.5)
    vx, vy = pp(550, 758)
    cut(ec, [pocket(rrect(vx, vy, 33.0, 14.5, 2.0), 1.4, T["ec"], rim=0.6, floor=0.4, name="c_vent")] +
        [pocket(rrect(*pp(512 + i * 36, yy), 6.5, 1.6, 0.6), 3.0, T["ec"] - 1.4, rim=0.25, floor=0.0, mat="void", name="c_vs")
         for yy in (750, 766) for i in range(3)])
    # lower-left battery block: a separate removable block a step below the upper body, sloped top, a raised
    # diagonal panel, an INSERT latch, and a bent steel strip down its left side and bottom (reference 4K crop)
    lb = shell("lb", sec_step(T["lb"] - F, T["lb"] - F - 2.0, 55.0, P["fillet_plate"], 0.3, under=P["undercut"]), F, mat="green", r_cv=4.0, r_cc=2.5)
    ix, iy = pp(398, 590)
    cut(lb, [screw_dimple(pp(*s_), T["lb"]) for s_ in SCREWS["lb"]] +
        [pocket(rrect(ix, iy, 9.0, 3.0, 1.0), 2.0, T["lb"], rim=0.4, floor=0.0, mat="void", name="c_insert")])
    loft("latch_insert", rrect(ix, iy, 6.0, 1.6, 0.5), sec_slab(2.2, top_r=0.5, foot=0.0, draft=0.0), z0=T["lb"] - 1.8, mat=MAT["rubber"])
    lbp = Outline.auto(pl([(378, 604), (421, 604), (421, 756), (452, 784), (398, 792), (350, 712)]), 3.0, 3.0)
    loft("lb_panel", lbp, sec_step(2.3, 0.5, 50.0, 1.0, 0.3), z0=T["lb"] - 0.5, mat=MAT["green"])
    lbo = Outline.auto(pl(LAYOUT["lb"]), 4.0, 2.5)
    strip = loft("frame", lbo.inset(-2.8), sec_slab(T["lb"] - 0.8 - 5.0, top_r=0.8, foot=0.0, draft=0.0), z0=5.0, mat=MAT["gunmetal"])
    lx0, ly0 = pp(330, 560)
    cut(strip, [loft("c_frame", lbo.inset(-0.3), [(0.0, 0.0, "crisp"), (0.0, 40.0, "crisp")]),
                loft("c_frame2", Outline([(lx0 + 6.0, ly0 + 4.0), (lx0 + 60.0, ly0 + 4.0), (lx0 + 60.0, ly0 - 58.0), (lx0 + 6.0, ly0 - 58.0)], 0.0),
                     [(0.0, 0.0, "crisp"), (0.0, 40.0, "crisp")])])
    # dial bracket (steel wedge) and the left lug
    # dial bracket: a thin aluminium plate, a tapered arm up the left of the screen to the top-left corner and a
    # lobe round the dial, on a black mounting block (advisor, v06 consult; the reference 4K crop)
    br = bracket_outline()
    # the body carries the plate: a black housing under it down to the table (review v08: the teardrop hung
    # outside the body with the table showing under it)
    loft("wedgeblock", br.inset(-0.6), sec_step(T["wedge"] - 2.5 - F + 0.3, T["wedge"] - 2.5 - F - 1.5, 60.0, 1.0, 0.3,
                                                  under=P["undercut"]), z0=F, mat=MAT["poly"])
    loft("wedge", br, sec_step(2.5, 1.0, 60.0, 0.9, 0.2), z0=T["wedge"] - 2.5, mat=MAT["alu"])
    for sxy in ((300, 215), (318, 262), (322, 330)):
        screw_head(pp(*sxy), T["wedge"] + 0.6)
    shell("lug", sec_slab(T["lug"] - 0.03, top_r=P["fillet_plate"], foot=0.6), 0.03, r_cv=4.0, r_cc=2.0, gap=0.0)
    for key in ("sh", "ub", "lb"):
        for s_ in SCREWS[key]:
            screw_head(pp(*s_), T[key])
    # joins: a black channel in the lower part along the foot of each higher neighbour (review v03:
    # V-shaped gaps showed lit walls; the reference has near-black crease lines)
    parts = {"tm": tm, "ub": ub, "lb": lb}
    for lower, uppers in (("ub", ("sh", "tm", "ec", "wedge")), ("lb", ("ub", "ec"))):
        cut(parts[lower], [moat(u, T[lower], 1.8 if lower == "lb" else None) for u in uppers], name=lower + "_moat")
    cut(tm, [loft("c_moatf", rrect(lx - 2.0, ly + 5.0, LCD_BEZEL[0] + 18.0 + 2 * P["moat_mm"], LCD_BEZEL[1] + 26.0 + 2 * P["moat_mm"], 10.0 + P["moat_mm"]),
                  [(0.0, T["tm"] - P["moat_depth"], "crisp"), (0.0, T["tm"] + 3.0, "crisp")], mat=MAT["void"])], name="tm_moatf")


# ------------------------------------------------------------------ LCD, controls, antenna, dial

def build_lcd():
    T = tops()
    lx, ly = pp(*LCD_C)
    z0 = T["tm"] - P["lcd_depth"]
    bh = P["lcd_depth"] - 2.2                      # bezel top sits 2.2 mm below the shield top
    bez = loft("bezel", rrect(lx, ly, LCD_BEZEL[0], LCD_BEZEL[1], 6.0), sec_slab(bh, top_r=0.35, foot=0.0, draft=0.0),
               z0=z0 - 0.02, mat=MAT["bezel"])
    cut(bez, [pocket(rrect(lx, ly, LCD_GLASS[0] + 0.4, LCD_GLASS[1] + 0.4, 3.0), 1.2, z0 + bh, rim=0.3, floor=0.0, name="c_bez")])
    bm = bmesh.new()
    w, h = LCD_GLASS[0] * MM / 2, LCD_GLASS[1] * MM / 2
    zz = (z0 + bh - 1.1) * MM
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
    gl.visible_diffuse = False
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        loft("bscrew", circle(lx + sx * 30.3, ly + sy * 15.4, 0.9, 20), sec_slab(0.6, top_r=0.3, foot=0.0, draft=0.0, seg=3),
             z0=z0 + bh, mat=MAT["steel"])


def build_antenna():
    """Two dark gunmetal barrels in a black cradle, one raised band each, black end caps with a lug
    (reference 4K crop; v01-v04 read as "fat cans with teal caps")."""
    T = tops()
    xl, y_top_l = pp(402, P["pod_top_px"][0])
    _, y_bot_l = pp(402, 184)                 # lower ends at the LCD frame's edge, capped dark (bare gunmetal mirrored the LCD)
    xr, y_top_r = pp(444, P["pod_top_px"][1])
    _, y_bot_r = pp(444, 184)
    z = T["tm"] + P["pod_z"]
    rp = P["pod_r"]
    yb = min(y_bot_l, y_bot_r)
    cr = loft("cradle", Outline.auto([(xl - rp - 1.5, yb - 2.0), (xr + rp + 1.5, yb - 2.0), (xr + rp + 1.5, yb + 13.0),
                                      (xl - rp - 1.5, yb + 13.0)], 2.0, 2.0),
              sec_slab(z - 13.0 + 1.0, top_r=1.2, foot=0.0, draft=0.0), z0=13.0, mat=MAT["poly"])
    cut(cr, [rod("c_pod", (x, yb - 5.0, z), (x, yb + 20.0, z), sec_rod(0.0, 0.0), circle(0, 0, rp + 0.3, 48))
             for x in (xl, xr)])
    for nm, x, y0, y1 in (("podL", xl, y_bot_l, y_top_l), ("podR", xr, y_bot_r, y_top_r)):
        rod(nm, (x, y0, z), (x, y1 - 4.0, z), sec_rod(0.6, 0.6), circle(0, 0, rp, 64), mat=MAT["gunmetal"])
        yy = y0 + (y1 - y0) * 0.55
        rod(nm + "band", (x, yy - 0.9, z), (x, yy + 0.9, z), sec_rod(0.35, 0.35, 3), circle(0, 0, rp + 0.35, 64), mat=MAT["gunmetal"])
        rod(nm + "cap", (x, y1 - 4.2, z), (x, y1, z), sec_rod(1.0, 0.3), circle(0, 0, rp + 0.25, 48), mat=MAT["rubber"])
        rod(nm + "foot", (x, y0 - 1.0, z), (x, y0 + 3.0, z), sec_rod(0.3, 0.8), circle(0, 0, rp + 0.3, 48), mat=MAT["rubber"])
        loft(nm + "lug", rrect(x, y1 - 2.2, 2.2, 3.0, 0.6), sec_slab(2.2, top_r=0.6, foot=0.0, draft=0.0),
             z0=z + rp - 0.2, mat=MAT["rubber"])
    ax, ay0 = xl, y_top_l + 2.2
    tilt, lean = math.radians(P["antenna_tilt"]), math.radians(-6.0)
    d = Vector((math.sin(lean) * math.cos(tilt), math.cos(lean) * math.cos(tilt), -math.sin(tilt)))
    p0 = Vector((ax, ay0, z))

    def at(s):
        return tuple(p0 + d * s)
    # knurled collar about as wide as a pod, diagonal knurl (reference 4K crop)
    rod("collar", at(0), at(14.0), sec_rod(0.5, 0.5, 3), toothed(0, 0, 4.1, 4.5, 48, 0.45, 0.35), mat=MAT["steel"], twist_deg=38.0)
    for t in (0.7, 13.3):
        rod("collarband", at(t - 0.7), at(t + 0.7), sec_rod(0.3, 0.3, 2), circle(0, 0, 4.65, 48), mat=MAT["steel"])
    rod("collarneck", at(14.0), at(17.0), sec_rod(0.4, 0.4, 2), circle(0, 0, 3.4, 40), mat=MAT["steel"])
    p0 = p0 + d * 5.0
    rod("whip", at(12.0), at(P["antenna_len"]), sec_rod(0.4, 0.0), circle(0, 0, 3.2, 32), mat=MAT["gloss"])
    rod("whipring", at(P["antenna_len"] - 1.0), at(P["antenna_len"] + 0.4), sec_rod(0.2, 0.2, 2), circle(0, 0, 3.05, 32), mat=MAT["steel"])
    rod("tip", at(P["antenna_len"] + 0.4), at(P["antenna_len"] + 7.5), sec_rod(1.2, 0.3), circle(0, 0, 4.0, 32), mat=MAT["rubber"])


def build_dial():
    """Matte aluminium bracket ring round the dial, a dark face with maroon ticks, a black knob with a Y
    groove, and a thick black gear underneath (reference 4K crop)."""
    T = tops()
    dx, dy = pp(277, 310)
    gx, gy = pp(263, 323)
    zt = T["wedge"]
    loft("gearwheel", toothed(gx, gy, P["gear_r"] - 2.2, P["gear_r"], 36, 0.40, 0.42),
         [(0.3, 0.0, "crisp"), (0.0, 0.3, "crisp"), (0.0, 5.7, "crisp"), (0.3, 6.0, "crisp")], z0=zt - 2.5 - 6.2, mat=MAT["rubber"])
    ring = loft("dialring", circle(dx, dy, 14.2, 96), sec_slab(2.0, top_r=1.0, foot=0.0, draft=0.0), z0=zt - 0.5, mat=MAT["alu"])
    cut(ring, [pocket(circle(dx, dy, 10.8, 96), 1.0, zt + 1.5, rim=0.4, floor=0.0, name="c_dial")])
    loft("dialface", circle(dx, dy, 10.6, 96), sec_slab(0.6, top_r=0.2, foot=0.0, draft=0.0), z0=zt, mat=MAT["face"])
    for k in range(36):
        a = 2 * math.pi * k / 36
        loft("tick", rrect(dx + math.cos(a) * 8.7, dy + math.sin(a) * 8.7, 2.2 if k % 9 == 0 else 1.3, 0.3, 0.1, math.degrees(a)),
             [(0.0, 0.0, "crisp"), (0.0, 0.05, "crisp")], z0=zt + 0.6, mat=MAT["tick"])
    cap = loft("dialcap", circle(dx, dy, 6.6, 64), sec_slab(1.8, top_r=0.9, foot=0.0, draft=0.0), z0=zt + 0.5, mat=MAT["rubber"])
    cut(cap, [loft("c_y", rrect(dx + math.cos(math.radians(90 + 120 * k)) * 1.9, dy + math.sin(math.radians(90 + 120 * k)) * 1.9,
                                3.8, 0.7, 0.3, 90 + 120 * k), sec_cutter(0.6, zt + 2.3, rim_r=0.2, floor_r=0.0)) for k in range(3)])
    rod("pin", (dx - 2.0, dy + 12.2, zt + 1.2), (dx - 2.0, dy + 15.8, zt + 2.8), sec_rod(0.5, 0.0), circle(0, 0, 0.9, 20), mat=MAT["alu"])
    bx, by = pp(278, 460)
    loft("boss", circle(bx, by, 6.2, 40), sec_slab(T["lug"] + 5.0 - (T["lug"] - 0.5), top_r=1.2, foot=0.0, draft=0.0),
         z0=T["lug"] - 0.5, mat=MAT["rubber"])
    screw_head((bx, by), T["lug"] + 5.0 + 0.9)
    lx, ly = pp(335, 770)
    ld = loft("lockdial", circle(lx, ly, 6.3, 48), sec_slab(1.8, top_r=0.7, foot=0.0, draft=0.0), z0=T["lb"], mat=MAT["steel"])
    cut(ld, [loft("c_ly", rrect(lx + math.cos(math.radians(90 + 120 * k)) * 1.8, ly + math.sin(math.radians(90 + 120 * k)) * 1.8,
                                3.4, 0.7, 0.2, 90 + 120 * k), [(0.0, T["lb"] + 1.3, "crisp"), (0.0, T["lb"] + 4.0, "crisp")]) for k in range(3)])


def build_controls():
    T = tops()
    kx, ky = pp(377, 368)
    loft("knobring", circle(kx, ky, 6.4, 48), sec_slab(1.0, top_r=0.4, foot=0.0, draft=0.0), z0=T["tm"], mat=MAT["rubber"])
    loft("knob", circle(kx, ky, 5.0, 48), sec_slab(5.0, top_r=1.2, foot=0.0, draft=3.0), z0=T["tm"] + 1.0, mat=MAT["rubber"])
    loft("lever", rrect(kx - 1.6, ky + 2.0, 3.2, 7.0, 1.2, 30.0), sec_slab(3.6, top_r=1.2, foot=0.0, draft=0.0), z0=T["tm"] + 6.0, mat=MAT["rubber"])
    lx, ly = pp(413, 358)
    led = loft("led", circle(lx, ly, 2.2, 32), sec_slab(1.6, top_r=1.0, foot=0.0, draft=0.0), z0=T["tm"] - 0.2, mat=MAT["red"])
    led.visible_diffuse = led.visible_glossy = False     # the LED lit the ridge next to it (review v01)
    loft("ledring", circle(lx, ly, 3.2, 32), sec_slab(0.5, top_r=0.2, foot=0.0, draft=0.0), z0=T["tm"] - 0.2, mat=MAT["steel"])
    sx, sy = pp(381, 437)
    sl = loft("slider", rrect(sx - 2.0, sy, 6.2, 5.0, 0.8), sec_slab(2.6, top_r=0.5, foot=0.0, draft=0.0), z0=T["tm"] - 1.6, mat=MAT["steel"])
    cut(sl, [loft("c_sg", rrect(sx - 2.0 + k * 1.3, sy, 0.5, 4.4, 0.1), [(0.0, T["tm"] + 0.7, "crisp"), (0.0, T["tm"] + 3.0, "crisp")])
             for k in (-1, 0, 1)])
    bx, by = pp(660, 350)
    loft("button", circle(bx, by, 4.6, 40), sec_slab(1.8, top_r=0.9, foot=0.0, draft=2.0), z0=T["tm"], mat=MAT["poly"])
    # thumb wheels in the slot: two toothed wheels, axis along x
    rx, ry = pp(657, 261)
    for i, dyw in enumerate((-8.2, 8.2)):
        c = (rx - 4.2, ry + dyw, T["tm"] - 5.0)
        rod(f"wheel{i}", c, (c[0] + 8.4, c[1], c[2]), sec_rod(0.3, 0.3, 2), toothed(0, 0, 7.0, 7.9, 22, 0.42, 0.38), mat=MAT["gunmetal"])
    # tabs, hook, lid latch
    tx, ty = pp(577, 166)
    loft("tab", rrect(tx, ty, 4.2, 11.0, 1.0), sec_slab(11.0, top_r=1.0, foot=0.0), z0=13.0, mat=MAT["poly"])
    lx2, ly2 = pp(662, 492)
    loft("latch", rrect(lx2, ly2, 8.0, 5.6, 1.0), sec_slab(2.4, top_r=0.8, foot=0.0), z0=T["sh"] - 1.2, mat=MAT["rubber"])
    # end cap pivot: steel cylinder along x, knurled knob on its end
    cx, cy = pp(652, 757)
    zc = T["ec"] + 1.0
    rod("pivot", (cx - 11.0, cy, zc), (cx + 11.0, cy, zc), sec_rod(1.5, 1.5), circle(0, 0, 7.4, 64), mat=MAT["gunmetal"])
    nx, ny = pp(693, 745)
    rod("endknurl", (nx - 1.5, ny, zc), (nx + 1.5, ny, zc), sec_rod(0.3, 0.3, 2), toothed(0, 0, 5.0, 5.5, 40, 0.4, 0.4), mat=MAT["rubber"])


# ------------------------------------------------------------------ cord, decals

def build_cord():
    T = tops()
    jx, jy = pp(650, 186)
    jz = T["tm"] + 3.5
    loft("jackblock", rrect(jx - 1.0, jy, 13.0, 9.0, 1.5), sec_slab(T["tm"] + 6.5 - 13.0, top_r=1.2, foot=0.0), z0=13.0, mat=MAT["poly"])
    rod("jack", (jx - 10.0, jy, jz), (jx + 9.0, jy - 1.5, jz), sec_rod(1.2, 0.6), circle(0, 0, 3.4, 32), mat=MAT["rubber"])
    rod("jackring", (jx + 4.0, jy - 0.7, jz), (jx + 7.0, jy - 1.0, jz), sec_rod(0.3, 0.3, 2), toothed(0, 0, 3.55, 3.85, 36), mat=MAT["gunmetal"])
    end = Vector((jx + 9.0, jy - 1.5, jz))
    pts = [end, Vector(pp(724, 188) + (13.0,)), Vector(pp(746, 214) + (8.0,)),
           Vector(pp(770, 270) + (6.4,)), Vector(pp(786, 360) + (6.4,)), Vector(pp(788, 450) + (6.4,)),
           Vector(pp(774, 530) + (6.4,)), Vector(pp(748, 568) + (7.5,))]
    cord = hs2.helix_cord("cord", pts, P["cord_coil_r"], P["cord_wire_r"], P["cord_turns"], ramp_mm=9.0, wobble=0.04)
    cord.data.materials.append(MAT["rubber"])
    px_, py_ = pp(708, 640)
    d = Vector((math.cos(math.radians(45)), math.sin(math.radians(45)), 0))
    c = Vector((px_, py_, T["ub"] - 3.0 + 5.6))
    loft("plug", rrect(c.x, c.y, 20.0, 12.5, 6.0, 45.0), sec_slab(6.5, top_r=5.5, foot=0.0, draft=0.0), z0=T["ub"] - 3.0, mat=MAT["rubber"])
    c = c + d * 7.0                                     # lead enters the dome's far end
    a0 = Vector(pp(744, 566) + (8.4,))
    a1 = Vector((a0.x - 1.5, a0.y - 7.0, 11.0))
    a2 = Vector((c.x + d.x * 3.0, c.y + d.y * 3.0, c.z + 1.0))
    for n_, (p, q) in enumerate(((a0, a1), (a1, a2))):
        rod(f"lead{n_}", tuple(p), tuple(q), sec_rod(0.3, 0.3, 2), circle(0, 0, 0.9, 16), mat=MAT["rubber"])


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
    """A printed label: a plane 0.02 mm above a surface. uv = (u0, v0, u1, v1) crop of the image."""
    if png not in MAT:
        MAT[png] = decal_material(png)
    cx, cy = pp(*centre_px)
    w, h = size_mm[0] * MM / 2, size_mm[1] * MM / 2
    ca, sa = math.cos(math.radians(rot_deg)), math.sin(math.radians(rot_deg))
    bm = bmesh.new()
    vs = [bm.verts.new((cx * MM + x * ca - y * sa, cy * MM + x * sa + y * ca, z_mm * MM))
          for x, y in ((-w, -h), (w, -h), (w, h), (-w, h))]
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
    T = tops()
    decal("logo", "dec_logo.png", (0, 0, 1, 1), (466, 418), (19.0, 7.6), T["sh"] + 0.02)
    decal("lidtext", "dec_lid.png", (0, 0, 1, 1), (601, 413), (15.0, 4.7), T["sh"] - 1.2 + 0.02)
    cell = lambda k, row: (k / 4, 0.75 - 0.25 * row if row == 0 else 0.25, (k + 1) / 4, 1.0 if row == 0 else 0.5)
    decal("lab_power", "dec_labels.png", cell(0, 0), (446, 341), (9.5, 2.4), T["tm"] + 0.02)
    decal("lab_onoff", "dec_labels.png", cell(1, 0), (372, 412), (9.5, 2.4), T["tm"] + 0.02)
    decal("lab_insert", "dec_labels.png", cell(2, 0), (400, 578), (9.0, 2.3), T["lb"] + 0.02)
    for i, (x, y, z) in enumerate(((497, 466, T["sh"] + 0.02), (561, 584, T["sh"] + 0.02), (680, 606, T["ub"] + 0.02))):
        decal(f"arrow{i}", "dec_labels.png", cell(i, 1), (x, y), (3.6, 3.6), z, 180.0 if i == 2 else 0.0)


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
        cam_d = bpy.data.cameras.new("Camera")
        cam = bpy.data.objects.new("Camera", cam_d)
        scene.collection.objects.link(cam)
        cam.location = (cx * MM, cy * MM, 0.6)
        cam_d.type = "ORTHO"
        cam_d.ortho_scale = 950.0 / S_PX * MM
        scene.render.resolution_x = scene.render.resolution_y = 950
        scene.camera = cam
        return cam
    phi, elev = math.radians(P["cam_azim"]), math.radians(P["cam_elev"])
    f = Vector((math.sin(phi), math.cos(phi), 0.0))
    tgt = Vector((tx * MM, ty * MM, 0.008))
    loc = tgt - f * P["cam_dist"] * math.cos(elev) + Vector((0, 0, P["cam_dist"] * math.sin(elev)))
    cam_d = bpy.data.cameras.new("Camera")
    cam = bpy.data.objects.new("Camera", cam_d)
    scene.collection.objects.link(cam)
    cam.location = loc
    cam.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
    cam_d.lens = P["cam_lens"]
    cam_d.sensor_width = 36.0
    cam_d.shift_x, cam_d.shift_y = P["cam_shift"]
    cam_d.clip_start = 0.02
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = P["res_x"], P["res_y"]
    return cam


def group_device():
    dev = bpy.data.collections.new("Device")
    stage = bpy.data.collections.new("Stage")
    metal = bpy.data.collections.new("Metal")
    for c in (dev, stage, metal):
        bpy.context.scene.collection.children.link(c)
    for ob in list(bpy.context.scene.collection.objects):
        if ob.type not in {"MESH", "CURVE"}:
            continue
        bpy.context.scene.collection.objects.unlink(ob)
        (stage if ob.name == "Backdrop" else dev).objects.link(ob)
    for ob in dev.objects:
        ms = getattr(ob.data, "materials", None)
        if ms and ms[0] in (MAT["steel"], MAT["gunmetal"], MAT["alu"], MAT["screw"], MAT["bezel"]):
            metal.objects.link(ob)
    return dev, stage, metal


def area_light(name, pos, tgt, size, power, receivers=None):
    ld = bpy.data.lights.new(name, "AREA")
    ld.shape, ld.size, ld.energy = "SQUARE", size, power
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = pos
    ob.rotation_euler = (tgt - pos).to_track_quat("-Z", "Y").to_euler()
    if receivers is not None:
        ob.light_linking.receiver_collection = receivers
    return ob


def add_lights(scene, view, dev, stage, metal):
    phi = math.radians(P["cam_azim"])
    f = Vector((math.sin(phi), math.cos(phi), 0.0))
    r = Vector((math.cos(phi), -math.sin(phi), 0.0))
    tx, ty = pp(*P["cam_target"])
    tgt = Vector((tx * MM, ty * MM, 0.01))
    if view == "plan":
        area_light("Key", tgt + Vector((0, 0, 0.5)), tgt, 0.9, 6.0)
    else:
        area_light("Key Backdrop", tgt + r * P["key_side"] + f * P["key_far"] + Vector((0, 0, P["key_dist"])), tgt,
                   P["key_size"], P["key_power"], None if P["key_on_device"] else stage)
        area_light("Key Device", tgt - f * P["dev_front"] + r * P["dev_side"] + Vector((0, 0, P["dev_height"])), tgt,
                   P["dev_size"], P["dev_power"], None if P["dev_on_table"] else dev)
        cam = scene.camera.location
        area_light("Fill Device", tgt + (cam - tgt) * 0.45 - Vector((0, 0, (cam - tgt).z * 0.25)), tgt,
                   P["fill_size"], P["fill_power"], dev)
        sc_ = area_light("Card Slopes", tgt + (cam - tgt) * 0.85 + Vector((0, 0, 0.30)), tgt,
                         P["slope_card_size"], P["slope_card"], dev)
        sc_.visible_diffuse = False
        sc_.visible_transmission = False
        sc_.visible_volume_scatter = False
        area_light("Card Metal", tgt + f * P["metal_far"] + Vector((0, 0, P["metal_height"])), tgt,
                   P["metal_size"], P["metal_power"], metal)
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Strength"].default_value = P["world_strength"]
    bg.inputs["Color"].default_value = (0.55, 0.55, 0.58, 1.0)
    scene.world = world


def post():
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
        glare.glare_type, glare.quality, glare.mix, glare.size, glare.threshold = "FOG_GLOW", "HIGH", -1.0, 7, 1.5
    else:
        glare.inputs["Type"].default_value = "Fog Glow"
        for src, dst in (("Glow", "Strength"), ("Glow Size", "Size"), ("Glow Threshold", "Threshold")):
            ng.links.new(gi.outputs[src], glare.inputs[dst])
    ng.links.new(glare.outputs["Image"], lens.inputs["Image"])
    ng.links.new(gi.outputs["Chroma"], lens.inputs["Dispersion"])
    ng.links.new(lens.outputs["Image"], go.inputs["Image"])
    auto_layout(ng)
    return ng


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="wip")
    ap.add_argument("--samples", type=int, default=128)
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--view", default="hero", choices=("hero", "plan"))
    ap.add_argument("--clay", action="store_true")
    ap.add_argument("--mirror", action="store_true")
    ap.add_argument("--mask", action="store_true", help="Workbench subject mask for tools/silhouette.py")
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
    for row in hs2.LOG:
        print("[out] cut", *row)
    empty = [o.name for o in scene.objects if o.type == "MESH" and len(o.data.polygons) == 0]
    if empty:
        print("[out] WARN empty meshes:", empty)
    dev, stage, metal = group_device()
    add_camera(scene, view)
    add_lights(scene, view, dev, stage, metal)
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
    P["clay"] = P["clay"] or args.clay
    P["mirror"] = P["mirror"] or args.mirror
    scene = build_scene(args.view)
    raw = EXP["renders"] / f"{args.out}_raw.exr"
    compositor(scene, post(), raw_exr=raw)
    scene.cycles.samples = args.samples
    if args.mask:
        scene.render.engine = "BLENDER_WORKBENCH"
        sh = scene.display.shading
        sh.light, sh.color_type, sh.single_color = "FLAT", "SINGLE", (0, 0, 0)
        scene.render.film_transparent = True
        bpy.data.objects["Backdrop"].hide_render = True
        scene.view_settings.view_transform = "Standard"
        scene.render.use_compositing = False
    scene.render.resolution_percentage = 100 if args.view == "plan" else round(args.scale * 100)
    print("[out] faces", sum(len(o.data.polygons) for o in scene.objects if o.type == "MESH"))
    if not args.norender:
        scene.render.filepath = str(EXP["renders"] / f"{args.out}.png")
        bpy.ops.render.render(write_still=True)
    if args.save:
        if not args.norender:
            use_saved_render(scene, raw, EXP["output"])
        blend = EXP["output"] / f"{EXP['name']}.blend"
        bpy.ops.file.pack_all()
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        blend.with_suffix(".blend1").unlink(missing_ok=True)
    print("BUILD OK")
