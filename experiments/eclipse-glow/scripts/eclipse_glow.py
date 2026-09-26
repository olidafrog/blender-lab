"""Eclipse glow: recreation of references/eclipse_glow_ref.jpg as a reusable, object-agnostic effect.

Builds:
  - Material "Eclipse Glow": node groups "Eclipse Coords" + "Eclipse Shade", with colours on three
    top-level ColorRamps (body, side rim, bottom rim). Assign it to any object; colour is driven by
    camera-space normals and facing ratio, not object shape. Also writes two AOVs (halo, arc_glow).
  - Compositor frame "Eclipse Lens": soften, halo (tight + wide), arc glow, bloom, dispersion,
    film grain, shadow tint.

Run:
  blender -b --factory-startup --python-exit-code 1 -P scripts/eclipse_glow.py -- --tag v1
"""
import math
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from common import enable_gpu, experiment_paths  # noqa: E402

EXP = experiment_paths(__file__)

NAME = "eclipse_glow"
RES = (832, 1248)  # matches the reference


def srgb(r, g, b, a=1.0):
    """0-255 sRGB -> linear RGBA (what ramp/emission colours expect)."""
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (lin(r), lin(g), lin(b), a)


# --- Tunables (defaults baked into the .blend; all editable there) -------------------------------
BODY_STOPS = [  # (position 0=bottom 1=top, sRGB colour) — sampled from the reference
    (0.00, (205, 52, 32)),
    (0.045, (252, 128, 80)),
    (0.08, (247, 167, 144)),
    (0.12, (249, 179, 206)),
    (0.20, (239, 175, 229)),
    (0.30, (212, 186, 245)),
    (0.39, (170, 185, 224)),
    (0.465, (106, 173, 215)),
    (0.505, (65, 151, 208)),
    (0.55, (30, 112, 205)),
    (0.585, (18, 75, 182)),
    (0.625, (18, 48, 125)),
    (0.67, (21, 30, 64)),
    (0.735, (16, 15, 20)),
    (0.80, (12, 10, 9)),
    (1.00, (8, 6, 4)),
]
RIM_SIDE_STOPS = [  # (edge 0=facing camera 1=silhouette, sRGB colour, alpha = how much it covers body)
    (0.10, (85, 168, 218), 0.0),
    (0.34, (112, 194, 225), 0.3),
    (0.46, (100, 210, 225), 0.8),
    (0.52, (120, 225, 190), 0.9),
    (0.60, (185, 225, 165), 0.95),
    (0.68, (215, 222, 140), 1.0),
    (0.82, (228, 180, 90), 1.0),
    (0.93, (222, 150, 60), 1.0),
    (1.00, (225, 100, 40), 1.0),
]
RIM_BOTTOM_STOPS = [
    (0.12, (232, 214, 238), 0.0),
    (0.26, (235, 224, 240), 0.35),
    (0.36, (242, 222, 225), 0.55),
    (0.45, (246, 206, 212), 0.6),
    (0.54, (250, 200, 165), 0.75),
    (0.64, (250, 160, 105), 1.0),
    (0.74, (245, 118, 64), 1.0),
    (0.84, (222, 80, 45), 1.0),
    (1.00, (165, 52, 35), 1.0),
]
COORDS = {"Gradient Angle": 0.0, "Gradient Scale": 1.02, "Gradient Curve": 0.7, "Curve Top Fade Start": 0.35,
          "Curve Top Fade End": 0.75, "Gradient Offset": 0.02}
SHADE = {
    "Brightness": 1.0,
    "Rim Strength": 1.0,
    "Rim Warm Start": -0.5,
    "Rim Warm End": 0.0,
    "Rim Top Fade Start": -0.2,
    "Rim Top Fade End": 0.28,
    "Rim Bottom Fade": 0.75,
    "Rim Bottom Fade Start": -0.7,
    "Rim Bottom Fade End": -0.95,
    "Arc Color": srgb(248, 236, 236),
    "Arc Side Color": srgb(228, 128, 98),
    "Arc Strength": 0.3,
    "Arc Offset": 0.0,
    "Arc Radius": 0.985,
    "Arc Width": 0.014,
    "Arc Apex Width": 0.035,
    "Arc Start": -0.1,
    "Arc Taper": 4.0,
    "Arc Color Start": 0.85,
    "Arc Occlusion": 1.0,
    "Arc Occlusion Start": 0.15,
    "Arc Occlusion End": 0.45,
    "Arc Softness": 0.75,
    "Halo Top Color": srgb(255, 150, 70),
    "Halo Bottom Color": srgb(200, 50, 28),
    "Halo Power": 8.0,
    "Halo Strength": 10.0,
    "Halo Top Fade Start": -0.4,
    "Halo Top Fade End": 0.35,
    "Arc Glow Color": srgb(245, 185, 150),
    "Arc Glow Strength": 4.5,
    "Arc Glow Start": 0.9,
    "Arc Glow Side Amount": 0.0,
}
LENS = {
    "soften_px": 7,
    "halo_px": 30,
    "halo_wide_px": 80,
    "halo_wide_amount": 0.35,
    "halo_inside_kill": 0.85,
    "coverage_px": 10,
    "arc_lift_px": 0,
    "arc_glow_inside_kill": 0.55,
    "crescent_lift_px": 23,
    "crescent_scale": 0.969,
    "crescent_soft_px": 3,
    "crescent_color": (0.42, 0.18, 0.12, 1.0),
    "crescent_glow_px": 28,
    "crescent_glow_color": (3.0, 1.0, 0.3, 1.0),
    "crescent_glow_amount": 1.1,
    "crescent_amount": 1.0,
    "arc_cover_px": 16,
    "arc_glow_far_tint": (1.0, 0.45, 0.25, 1.0),
    "arc_glow_px": (12, 50, 150),
    "arc_glow_amounts": (1.0, 1.2, 0.5),  # near, mid, far  # near, mid, far (near is fixed at 1)
    "glow_threshold": 1.0,  # 4.4 ignored the old 0.1 and rendered the final at 1.0
    "glow_mix": -0.88,
    "glow_size": 9,
    "dispersion": 0.004,
    "grain": 0.18,
    "shadow_grain": 0.004,
    "shadow_tint": (0.002, 0.0014, 0.0008, 1.0),
}
# --------------------------------------------------------------------------------------------------


def link(tree, a, b):
    tree.links.new(a, b)


def _set(tree, sock, v):
    if isinstance(v, (int, float)):
        sock.default_value = v
    elif v is not None:
        link(tree, v, sock)


def math_node(tree, op, a=None, b=None, loc=(0, 0), clamp=False):
    n = tree.nodes.new("ShaderNodeMath")
    n.operation = op
    n.use_clamp = clamp
    n.location = loc
    _set(tree, n.inputs[0], a)
    _set(tree, n.inputs[1], b)
    return n.outputs[0]


def smoothstep(tree, value, lo, hi, loc=(0, 0)):
    """Explicit smoothstep (clamp + t*t*(3-2t))."""
    x, y = loc
    t = math_node(tree, "DIVIDE", math_node(tree, "SUBTRACT", value, lo, loc=(x - 300, y)),
                  math_node(tree, "SUBTRACT", hi, lo, loc=(x - 300, y - 60)), loc=(x - 150, y), clamp=True)
    tt = math_node(tree, "MULTIPLY", t, t, loc=(x, y + 60))
    k = math_node(tree, "MULTIPLY_ADD", t, -2.0, loc=(x, y - 60))
    k.node.inputs[2].default_value = 3.0
    return math_node(tree, "MULTIPLY", tt, k, loc=(x + 150, y))


def mix(tree, data_type, fac, a, b, loc=(0, 0)):
    """ShaderNodeMix; data_type FLOAT or RGBA. Socket indices differ by type."""
    n = tree.nodes.new("ShaderNodeMix")
    n.data_type = data_type
    n.clamp_factor = True
    n.location = loc
    ia, ib, out = (2, 3, 0) if data_type == "FLOAT" else (6, 7, 2)
    _set(tree, n.inputs[0], fac)
    _set(tree, n.inputs[ia], a)
    if isinstance(b, tuple):
        n.inputs[ib].default_value = b
    else:
        _set(tree, n.inputs[ib], b)
    return n.outputs[out]


def scale_color(tree, color, amount, loc=(0, 0)):
    """color * amount via Vector Math, so values can exceed 1 (HDR)."""
    n = tree.nodes.new("ShaderNodeVectorMath")
    n.operation = "SCALE"
    n.location = loc
    link(tree, color, n.inputs[0])
    _set(tree, n.inputs["Scale"], amount)
    return n.outputs[0]


def add_socket(ng, name, in_out, stype, default=None, lo=None, hi=None):
    s = ng.interface.new_socket(name, in_out=in_out, socket_type=stype)
    if default is not None:
        s.default_value = default
    if lo is not None:
        s.min_value = lo
    if hi is not None:
        s.max_value = hi
    return s


def build_coords_group():
    """Camera-space coordinates any mesh can use: vertical/horizontal from normals, edge from facing."""
    ng = bpy.data.node_groups.new("Eclipse Coords", "ShaderNodeTree")
    add_socket(ng, "Gradient Angle", "INPUT", "NodeSocketFloat", 0.0, -180.0, 180.0)
    add_socket(ng, "Gradient Offset", "INPUT", "NodeSocketFloat", 0.0, -2.0, 2.0)
    add_socket(ng, "Gradient Scale", "INPUT", "NodeSocketFloat", 1.0, 0.0, 4.0)
    add_socket(ng, "Gradient Curve", "INPUT", "NodeSocketFloat", 0.0, -2.0, 2.0)
    add_socket(ng, "Curve Top Fade Start", "INPUT", "NodeSocketFloat", 0.1, -1.0, 1.0)
    add_socket(ng, "Curve Top Fade End", "INPUT", "NodeSocketFloat", 0.5, -1.0, 1.0)
    add_socket(ng, "Vertical", "OUTPUT", "NodeSocketFloat")
    add_socket(ng, "Signed Vertical", "OUTPUT", "NodeSocketFloat")
    add_socket(ng, "Signed Horizontal", "OUTPUT", "NodeSocketFloat")
    add_socket(ng, "Edge", "OUTPUT", "NodeSocketFloat")
    add_socket(ng, "Curved Vertical", "OUTPUT", "NodeSocketFloat")
    t = ng
    gi = t.nodes.new("NodeGroupInput"); gi.location = (-900, 0)
    go = t.nodes.new("NodeGroupOutput"); go.location = (900, 0)
    I = gi.outputs

    geo = t.nodes.new("ShaderNodeNewGeometry"); geo.location = (-900, 300)
    vt = t.nodes.new("ShaderNodeVectorTransform"); vt.location = (-700, 300)
    vt.vector_type, vt.convert_from, vt.convert_to = "NORMAL", "WORLD", "CAMERA"
    link(t, geo.outputs["Normal"], vt.inputs[0])
    sep = t.nodes.new("ShaderNodeSeparateXYZ"); sep.location = (-500, 300)
    link(t, vt.outputs[0], sep.inputs[0])

    rad = math_node(t, "RADIANS", I["Gradient Angle"], loc=(-700, -100))
    sin_a = math_node(t, "SINE", rad, loc=(-500, -50))
    cos_a = math_node(t, "COSINE", rad, loc=(-500, -150))
    v = math_node(t, "ADD",
                  math_node(t, "MULTIPLY", sep.outputs["X"], sin_a, loc=(-300, 250)),
                  math_node(t, "MULTIPLY", sep.outputs["Y"], cos_a, loc=(-300, 150)), loc=(-100, 200))
    h = math_node(t, "SUBTRACT",
                  math_node(t, "MULTIPLY", sep.outputs["X"], cos_a, loc=(-300, -350)),
                  math_node(t, "MULTIPLY", sep.outputs["Y"], sin_a, loc=(-300, -450)), loc=(-100, -400))
    # Signed Vertical (used for masks, rim and arc) ignores Gradient Offset; only the colour bands shift.
    sv = math_node(t, "MULTIPLY", v, I["Gradient Scale"], loc=(100, 200))
    sv = math_node(t, "MINIMUM", math_node(t, "MAXIMUM", sv, -1.0, loc=(250, 250)), 1.0, loc=(400, 250))

    lw = t.nodes.new("ShaderNodeLayerWeight"); lw.location = (-100, -150)
    lw.inputs["Blend"].default_value = 0.5
    edge = lw.outputs["Facing"]

    # Curve bends the bands near the rim: lighter colours climb higher towards the silhouette.
    curve_w = math_node(t, "SUBTRACT", 1.0,
                        smoothstep(t, sv, I["Curve Top Fade Start"], I["Curve Top Fade End"], (250, -150)),
                        loc=(400, -150))
    bent = math_node(t, "SUBTRACT", math_node(t, "ADD", sv, I["Gradient Offset"], loc=(450, 250)),
                     math_node(t, "MULTIPLY",
                               math_node(t, "MULTIPLY", math_node(t, "MULTIPLY", edge, edge, loc=(250, 0)),
                                         I["Gradient Curve"], loc=(400, 0)),
                               curve_w, loc=(500, 0)), loc=(600, 100))
    vert = math_node(t, "MULTIPLY_ADD", bent, 0.5, loc=(700, 100), clamp=True)
    vert.node.inputs[2].default_value = 0.5

    link(t, vert, go.inputs["Vertical"])
    # Rim fades use the full (unfaded) curve so their cut-off follows the silhouette, not a straight line.
    curve_full = math_node(t, "SUBTRACT", sv,
                           math_node(t, "MULTIPLY", math_node(t, "MULTIPLY", edge, edge, loc=(250, -300)),
                                     I["Gradient Curve"], loc=(400, -300)), loc=(550, -300))
    link(t, curve_full, go.inputs["Curved Vertical"])
    link(t, sv, go.inputs["Signed Vertical"])
    link(t, math_node(t, "MULTIPLY", h, I["Gradient Scale"], loc=(100, -400)), go.inputs["Signed Horizontal"])
    link(t, edge, go.inputs["Edge"])
    return ng


def build_shade_group():
    ng = bpy.data.node_groups.new("Eclipse Shade", "ShaderNodeTree")
    S = "NodeSocketFloat"
    for name, stype, d, lo, hi in [
        ("Body Color", "NodeSocketColor", (0, 0, 0, 1), None, None),
        ("Rim Side Color", "NodeSocketColor", (1, 1, 1, 1), None, None),
        ("Rim Side Alpha", S, 0.0, 0.0, 1.0),
        ("Rim Bottom Color", "NodeSocketColor", (1, 1, 1, 1), None, None),
        ("Rim Bottom Alpha", S, 0.0, 0.0, 1.0),
        ("Signed Vertical", S, 0.0, -1.0, 1.0),
        ("Signed Horizontal", S, 0.0, -1.0, 1.0),
        ("Edge", S, 0.0, 0.0, 1.0),
        ("Curved Vertical", S, 0.0, -2.0, 2.0),
        ("Brightness", S, 1.0, 0.0, 20.0),
        ("Rim Strength", S, 1.0, 0.0, 1.0),
        ("Rim Warm Start", S, -0.75, -1.0, 1.0),
        ("Rim Warm End", S, -0.25, -1.0, 1.0),
        ("Rim Top Fade Start", S, 0.2, -1.0, 1.0),
        ("Rim Top Fade End", S, 0.5, -1.0, 1.0),
        ("Rim Bottom Fade", S, 0.0, 0.0, 1.0),
        ("Rim Bottom Fade Start", S, -0.7, -1.0, 1.0),
        ("Rim Bottom Fade End", S, -0.95, -1.0, 1.0),
        ("Arc Color", "NodeSocketColor", (1, 0.9, 0.9, 1), None, None),
        ("Arc Side Color", "NodeSocketColor", (1, 0.5, 0.3, 1), None, None),
        ("Arc Strength", S, 1.0, 0.0, 10.0),
        ("Arc Offset", S, 0.1, -1.0, 1.0),
        ("Arc Radius", S, 0.86, 0.0, 2.0),
        ("Arc Width", S, 0.025, 0.001, 0.5),
        ("Arc Apex Width", S, 0.04, 0.001, 0.5),
        ("Arc Start", S, 0.0, -1.0, 1.0),
        ("Arc Softness", S, 0.9, 0.001, 2.0),
        ("Arc Taper", S, 2.0, 0.1, 10.0),
        ("Arc Color Start", S, 0.8, -1.0, 1.0),
        ("Arc Occlusion", S, 1.0, 0.0, 1.0),
        ("Arc Occlusion Start", S, 0.15, -1.0, 1.0),
        ("Arc Occlusion End", S, 0.45, -1.0, 1.0),
        ("Halo Top Color", "NodeSocketColor", (1, 0.4, 0.15, 1), None, None),
        ("Halo Bottom Color", "NodeSocketColor", (1, 0.1, 0.03, 1), None, None),
        ("Halo Power", S, 5.0, 0.1, 30.0),
        ("Halo Strength", S, 6.0, 0.0, 50.0),
        ("Halo Top Fade Start", S, -0.1, -1.0, 1.0),
        ("Halo Top Fade End", S, 0.35, -1.0, 1.0),
        ("Arc Glow Color", "NodeSocketColor", (1, 0.4, 0.15, 1), None, None),
        ("Arc Glow Strength", S, 4.0, 0.0, 50.0),
        ("Arc Glow Start", S, 0.88, -1.0, 1.0),
        ("Arc Glow Side Amount", S, 0.25, 0.0, 1.0),
    ]:
        add_socket(ng, name, "INPUT", stype, d, lo, hi)
    add_socket(ng, "Shader", "OUTPUT", "NodeSocketShader")
    add_socket(ng, "Color", "OUTPUT", "NodeSocketColor")
    add_socket(ng, "Halo", "OUTPUT", "NodeSocketColor")
    add_socket(ng, "Arc Glow", "OUTPUT", "NodeSocketColor")
    t = ng
    gi = t.nodes.new("NodeGroupInput"); gi.location = (-1400, 0)
    go = t.nodes.new("NodeGroupOutput"); go.location = (1000, 0)
    I = gi.outputs
    sv = I["Signed Vertical"]

    # Arc: a circle offset upward in camera-normal space — tangent to the silhouette at the top and
    # cutting inside it towards the sides (the "two overlapping discs" eclipse look).
    arc_v = smoothstep(t, sv, I["Arc Start"], math_node(t, "ADD", I["Arc Start"], I["Arc Softness"],
                                                         loc=(-1100, -200)), (-900, -200))
    dy = math_node(t, "SUBTRACT", sv, I["Arc Offset"], loc=(-1100, -400))
    dist = math_node(t, "SQRT", math_node(t, "ADD",
                                          math_node(t, "MULTIPLY", I["Signed Horizontal"], I["Signed Horizontal"],
                                                    loc=(-950, -350)),
                                          math_node(t, "MULTIPLY", dy, dy, loc=(-950, -450)), loc=(-800, -400)),
                     loc=(-700, -400))
    # Width swells towards the apex so the crest reads as a lens, tapering to a hairline at the sides.
    width = mix(t, "FLOAT", smoothstep(t, sv, 0.8, 1.0, (-800, -600)), I["Arc Width"], I["Arc Apex Width"],
                (-600, -600))
    z = math_node(t, "DIVIDE", math_node(t, "SUBTRACT", dist, I["Arc Radius"], loc=(-600, -450)),
                  width, loc=(-500, -450))
    band = math_node(t, "EXPONENT", math_node(t, "MULTIPLY", math_node(t, "MULTIPLY", z, z, loc=(-400, -500)),
                                              -1.0, loc=(-300, -500)), loc=(-200, -500))
    # Rim: warm spectrum at the bottom blending to the cool/yellow spectrum on the sides, following
    # the silhouette all the way round; fades out towards the top where the arc takes over.
    warm = smoothstep(t, sv, I["Rim Warm Start"], I["Rim Warm End"], (-900, 500))
    rim_col = mix(t, "RGBA", warm, I["Rim Bottom Color"], I["Rim Side Color"], (-600, 550))
    rim_a = mix(t, "FLOAT", warm, I["Rim Bottom Alpha"], I["Rim Side Alpha"], (-600, 400))
    top_fade = math_node(t, "SUBTRACT", 1.0,
                         smoothstep(t, I["Curved Vertical"], I["Rim Top Fade Start"], I["Rim Top Fade End"],
                                    (-900, 250)),
                         loc=(-600, 250))
    # Bottom fade lets the body's own orange show through at the very bottom of the silhouette.
    bot_fade = math_node(t, "SUBTRACT", 1.0,
                         math_node(t, "MULTIPLY", I["Rim Bottom Fade"],
                                   smoothstep(t, sv, I["Rim Bottom Fade Start"], I["Rim Bottom Fade End"],
                                              (-900, 100)), loc=(-600, 100)), loc=(-450, 100))
    rim_fac = math_node(t, "MULTIPLY",
                        math_node(t, "MULTIPLY", math_node(t, "MULTIPLY", rim_a, top_fade, loc=(-400, 350)),
                                  bot_fade, loc=(-300, 250)),
                        I["Rim Strength"], loc=(-250, 350), clamp=True)
    col = mix(t, "RGBA", rim_fac, I["Body Color"], rim_col, (0, 300))
    # Arc occlusion: above the shoulders, whatever lies outside the arc circle goes dark, so the arc
    # reads as the disc's top edge.
    occ = math_node(t, "MULTIPLY",
                    math_node(t, "MULTIPLY",
                              smoothstep(t, dist, I["Arc Radius"],
                                         math_node(t, "ADD", I["Arc Radius"], I["Arc Width"], loc=(-100, 600)),
                                         (50, 650)),
                              smoothstep(t, sv, I["Arc Occlusion Start"], I["Arc Occlusion End"], (50, 500)),
                              loc=(250, 600)),
                    I["Arc Occlusion"], loc=(400, 600))
    col = mix(t, "RGBA", occ, col, (0, 0, 0, 1), (550, 400))

    arc_core = math_node(t, "POWER", arc_v, I["Arc Taper"], loc=(-200, -300))
    arc = math_node(t, "MULTIPLY", math_node(t, "MULTIPLY", arc_core, band, loc=(-50, -350)),
                    I["Arc Strength"], loc=(100, -350))
    total = t.nodes.new("ShaderNodeVectorMath"); total.operation = "ADD"; total.location = (400, 100)
    link(t, col, total.inputs[0])
    # Apex colour only near the very top; the rest of the arc takes the side colour.
    arc_col = mix(t, "RGBA", smoothstep(t, sv, I["Arc Color Start"], 1.0, (-50, -150)),
                  I["Arc Side Color"], I["Arc Color"], (100, -200))
    link(t, scale_color(t, arc_col, arc, (250, -300)), total.inputs[1])

    em = t.nodes.new("ShaderNodeEmission"); em.location = (700, 100)
    link(t, total.outputs[0], em.inputs["Color"])
    link(t, I["Brightness"], em.inputs["Strength"])
    link(t, em.outputs[0], go.inputs["Shader"])
    link(t, total.outputs[0], go.inputs["Color"])

    # Halo AOV: edge light only, blurred outward in the compositor. Colour graded bottom → top,
    # faded out towards the top so the top reads as the arc, not an outline.
    v01 = math_node(t, "MULTIPLY_ADD", sv, 0.5, loc=(-900, -750))
    v01.node.inputs[2].default_value = 0.5
    halo_col = mix(t, "RGBA", v01, I["Halo Bottom Color"], I["Halo Top Color"], (-700, -750))
    halo_top = math_node(t, "SUBTRACT", 1.0,
                         smoothstep(t, sv, I["Halo Top Fade Start"], I["Halo Top Fade End"], (-900, -950)),
                         loc=(-600, -950))
    halo_amt = math_node(t, "MULTIPLY",
                         math_node(t, "MULTIPLY",
                                   math_node(t, "POWER", I["Edge"], I["Halo Power"], loc=(-600, -1100)),
                                   I["Halo Strength"], loc=(-450, -1050)),
                         halo_top, loc=(-300, -1000))
    link(t, scale_color(t, halo_col, halo_amt, (0, -850)), go.inputs["Halo"])

    # Arc Glow AOV: the arc's own bloom, concentrated at the apex and lifted in the compositor.
    # Glow concentrated at the apex, with a fraction running down the arc's sides.
    apex = mix(t, "FLOAT", smoothstep(t, sv, I["Arc Glow Start"], 1.0, (-450, -1250)),
               math_node(t, "MULTIPLY", I["Arc Glow Side Amount"], arc_v, loc=(-450, -1400)), 1.0,
               (-300, -1250))
    glow_amt = math_node(t, "MULTIPLY", math_node(t, "MULTIPLY", apex, band, loc=(-150, -1250)),
                         I["Arc Glow Strength"], loc=(0, -1250))
    link(t, scale_color(t, I["Arc Glow Color"], glow_amt, (200, -1150)), go.inputs["Arc Glow"])
    return ng


def build_material():
    coords_ng, shade_ng = build_coords_group(), build_shade_group()
    mat = bpy.data.materials.new("Eclipse Glow")
    mat.use_nodes = True
    t = mat.node_tree
    t.nodes.clear()

    coords = t.nodes.new("ShaderNodeGroup"); coords.node_tree = coords_ng
    coords.location = (-900, 0); coords.label = "Eclipse Coords"
    for k, v in COORDS.items():
        coords.inputs[k].default_value = v

    def ramp(label, stops, loc, alpha=False):
        r = t.nodes.new("ShaderNodeValToRGB"); r.label = label; r.location = loc; r.width = 320
        cr = r.color_ramp
        cr.interpolation = "LINEAR"
        while len(cr.elements) > 1:
            cr.elements.remove(cr.elements[-1])
        for i, s in enumerate(stops):
            e = cr.elements[0] if i == 0 else cr.elements.new(s[0])
            e.position = s[0]
            e.color = srgb(*s[1], s[2] if alpha else 1.0)
        return r

    body = ramp("Body Gradient (bottom → top)", BODY_STOPS, (-500, 350))
    rim_side = ramp("Rim Sides (centre → edge; alpha = coverage)", RIM_SIDE_STOPS, (-500, 50), alpha=True)
    rim_bot = ramp("Rim Bottom (centre → edge; alpha = coverage)", RIM_BOTTOM_STOPS, (-500, -250), alpha=True)
    link(t, coords.outputs["Vertical"], body.inputs["Fac"])
    link(t, coords.outputs["Edge"], rim_side.inputs["Fac"])
    link(t, coords.outputs["Edge"], rim_bot.inputs["Fac"])

    shade = t.nodes.new("ShaderNodeGroup"); shade.node_tree = shade_ng
    shade.location = (0, 0); shade.label = "Eclipse Shade"; shade.width = 240
    link(t, body.outputs["Color"], shade.inputs["Body Color"])
    link(t, rim_side.outputs["Color"], shade.inputs["Rim Side Color"])
    link(t, rim_side.outputs["Alpha"], shade.inputs["Rim Side Alpha"])
    link(t, rim_bot.outputs["Color"], shade.inputs["Rim Bottom Color"])
    link(t, rim_bot.outputs["Alpha"], shade.inputs["Rim Bottom Alpha"])
    for k in ("Signed Vertical", "Signed Horizontal", "Edge", "Curved Vertical"):
        link(t, coords.outputs[k], shade.inputs[k])
    for k, v in SHADE.items():
        shade.inputs[k].default_value = v

    out = t.nodes.new("ShaderNodeOutputMaterial"); out.location = (350, 100)
    link(t, shade.outputs["Shader"], out.inputs["Surface"])
    for i, (aov_name, sock) in enumerate((("halo", "Halo"), ("arc_glow", "Arc Glow"))):
        aov = t.nodes.new("ShaderNodeOutputAOV"); aov.location = (350, -100 - 150 * i)
        aov.aov_name = aov_name
        link(t, shade.outputs[sock], aov.inputs["Color"])
    return mat


def film_grain_image():
    path = EXP["assets"] / f"film_grain_v3_{RES[0]}x{RES[1]}.png"
    if not path.exists():
        # Clumpy grain: fine noise plus half-resolution noise (2px clumps), like film rather than digital.
        rng = np.random.default_rng(7)
        fine = rng.normal(0, 1, (RES[1], RES[0]))
        coarse = np.kron(rng.normal(0, 1, (RES[1] // 2, RES[0] // 2)), np.ones((2, 2)))
        g = np.clip(0.5 + 0.18 * (0.85 * fine + 0.45 * coarse) / 0.96, 0, 1).astype(np.float32)
        img = bpy.data.images.new("film_grain_tmp", RES[0], RES[1], alpha=False)
        img.pixels.foreach_set(np.stack([g, g, g, np.ones_like(g)], axis=-1).ravel())
        img.filepath_raw = str(path)
        img.file_format = "PNG"
        img.save()
        bpy.data.images.remove(img)
    img = bpy.data.images.load(str(path))
    img.name = "Film Grain"
    img.colorspace_settings.name = "Non-Color"
    img.pack()
    return img


# 4.4 keeps the compositor on scene.node_tree; 5.x uses a node group and has no MixRGB or compositor
# Math, and moved most node settings onto input sockets.
LEGACY_COMP = "node_tree" in bpy.types.Scene.bl_rna.properties


def mix_in(n, which):
    """Mix node colour input A or B (4.4 CompositorNodeMixRGB / 5.x ShaderNodeMix)."""
    return n.inputs[{"A": 1, "B": 2}[which] if LEGACY_COMP else {"A": 6, "B": 7}[which]]


def out(n):
    """The node's main output. ShaderNodeMix lists its colour result third."""
    return n.outputs[2] if n.bl_idname == "ShaderNodeMix" else n.outputs[0]


def build_compositor(scene):
    if LEGACY_COMP:
        scene.use_nodes = True
        t = scene.node_tree
        t.nodes.clear()
    else:
        t = bpy.data.node_groups.new("Eclipse Compositor", "CompositorNodeTree")
        t.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        scene.compositing_node_group = t
        scene.render.use_compositing = True
    frame = t.nodes.new("NodeFrame"); frame.label = "Eclipse Lens — tweak here"; frame.label_size = 24
    nodes = []

    def node(kind, label, loc, **props):
        n = t.nodes.new(kind); n.label = label; n.location = loc
        for k, v in props.items():
            setattr(n, k, v)
        nodes.append(n)
        return n

    def blur(label, loc, px):
        if LEGACY_COMP:
            return node("CompositorNodeBlur", label, loc, filter_type="GAUSS", size_x=px, size_y=px)
        n = node("CompositorNodeBlur", label, loc)
        n.inputs["Size"].default_value = (px, px)
        n.inputs["Type"].default_value = "Gaussian"
        return n

    def mixrgb(label, loc, blend, fac=1.0):
        if LEGACY_COMP:
            n = node("CompositorNodeMixRGB", label, loc, blend_type=blend)
        else:
            # 4.4 MixRGB never clamped its factor; several amounts here are above 1.
            n = node("ShaderNodeMix", label, loc, data_type="RGBA", blend_type=blend, clamp_factor=False)
        n.inputs[0].default_value = fac
        return n

    def math(label, loc, op, clamp=False):
        return node("CompositorNodeMath" if LEGACY_COMP else "ShaderNodeMath", label, loc,
                    operation=op, use_clamp=clamp)

    def nearest(n):
        # 4.4 Translate/Transform sampled Nearest; 5.x defaults to Bilinear, which softens the crescent.
        if not LEGACY_COMP:
            n.inputs["Interpolation"].default_value = "Nearest"
        return n

    rl = t.nodes.new("CompositorNodeRLayers"); rl.location = (-1200, 0)
    soften = blur("Soften", (-900, 200), LENS["soften_px"])

    # Halo: masked to outside the object (halo *= 1 - coverage*kill), then tight + wide blurs.
    cover = blur("Object Coverage", (-900, -150), LENS["coverage_px"])
    kill = math("Halo Inside Kill (0 = glow inside too)", (-750, -150), "MULTIPLY", clamp=True)
    kill.inputs[1].default_value = LENS["halo_inside_kill"]
    outside = math("Outside Mask", (-600, -150), "SUBTRACT")
    outside.inputs[0].default_value = 1.0
    halo_tight = blur("Halo Spread", (-900, -350), LENS["halo_px"])
    halo_wide = blur("Halo Wide Spread", (-900, -550), LENS["halo_wide_px"])
    wide_mix = mixrgb("Halo Wide Amount", (-700, -450), "ADD", LENS["halo_wide_amount"])
    halo_masked = mixrgb("Halo × Outside", (-450, -250), "MULTIPLY")
    halo_add = mixrgb("Add Halo", (-250, 100), "ADD")

    arc_move = nearest(node("CompositorNodeTranslate", "Arc Glow Lift (Y px)", (-900, -800)))
    arc_move.inputs["Y"].default_value = LENS["arc_lift_px"]
    # Three stacked blurs ≈ a hotspot with a long soft tail, without clipping the core.
    arc_b = [blur(f"Arc Glow {name}", (-700, -800 - 150 * i), px)
             for i, (name, px) in enumerate(zip(("Near", "Mid", "Far"), LENS["arc_glow_px"]))]
    arc_near = mixrgb("Arc Glow Near Amount", (-550, -750), "MULTIPLY", 1.0)
    mix_in(arc_near, "B").default_value = (LENS["arc_glow_amounts"][0],) * 3 + (1.0,)
    arc_m1 = mixrgb("Arc Glow Mid Amount", (-500, -900), "ADD", LENS["arc_glow_amounts"][1])
    arc_far_tint = mixrgb("Arc Glow Far Tint", (-550, -1050), "MULTIPLY", 1.0)
    mix_in(arc_far_tint, "B").default_value = LENS["arc_glow_far_tint"]
    arc_blur = mixrgb("Arc Glow Far Amount", (-350, -950), "ADD", LENS["arc_glow_amounts"][2])
    arc_add = mixrgb("Add Arc Glow", (-50, 0), "ADD")
    arc_cover = blur("Arc Occluder Edge", (-900, -1100), LENS["arc_cover_px"])
    arc_kill = math("Arc Glow Inside Kill", (-750, -1100), "MULTIPLY", clamp=True)
    arc_kill.inputs[1].default_value = LENS["arc_glow_inside_kill"]
    arc_outside = math("Arc Glow Outside Mask", (-600, -1100), "SUBTRACT")
    arc_outside.inputs[0].default_value = 1.0

    # Crescent: the object's silhouette, lifted and shrunk, minus the silhouette itself — the classic
    # eclipse lens. Works for any object because it is built from the object's own coverage.
    cres_move = nearest(node("CompositorNodeTransform", "Crescent Offset (Y = lift px, Scale)", (-900, -1300)))
    cres_move.inputs["Y"].default_value = LENS["crescent_lift_px"]
    cres_move.inputs["Scale"].default_value = LENS["crescent_scale"]
    cres_hole = math("Crescent = Shifted × (1 − Object)", (-700, -1300), "SUBTRACT", clamp=True)
    cres_soft = blur("Crescent Softness", (-550, -1300), LENS["crescent_soft_px"])
    cres_col = mixrgb("Crescent Colour", (-400, -1300), "MULTIPLY", 1.0)
    mix_in(cres_col, "B").default_value = LENS["crescent_color"]
    cres_glow = blur("Crescent Glow Spread", (-400, -1450), LENS["crescent_glow_px"])
    cres_glow_col = mixrgb("Crescent Glow Colour", (-250, -1450), "MULTIPLY", 1.0)
    mix_in(cres_glow_col, "B").default_value = LENS["crescent_glow_color"]
    cres_sum = mixrgb("Crescent Glow Amount", (-150, -1300), "ADD", LENS["crescent_glow_amount"])
    cres_add = mixrgb("Add Crescent (Fac = amount)", (0, -150), "ADD", LENS["crescent_amount"])

    if LEGACY_COMP:
        bloom = node("CompositorNodeGlare", "Bloom", (150, 0), glare_type="FOG_GLOW", quality="HIGH",
                     threshold=LENS["glow_threshold"], mix=LENS["glow_mix"], size=LENS["glow_size"])
        lens = node("CompositorNodeLensdist", "Chromatic Dispersion", (350, 0), use_fit=True)
    else:
        # Same conversion Blender uses when it opens a 4.4 file: mix -> strength, size 9 -> 1.0.
        bloom = node("CompositorNodeGlare", "Bloom", (150, 0))
        bi = bloom.inputs
        bi["Type"].default_value = "Fog Glow"
        bi["Quality"].default_value = "High"
        bi["Threshold"].default_value = LENS["glow_threshold"]
        bi["Strength"].default_value = 1.0 - min(max(-LENS["glow_mix"], 0.0), 1.0)
        bi["Size"].default_value = 2.0 ** (LENS["glow_size"] - 9)
        lens = node("CompositorNodeLensdist", "Chromatic Dispersion", (350, 0))
        lens.inputs["Fit"].default_value = True
    lens.inputs["Dispersion"].default_value = LENS["dispersion"]
    grain_img = node("CompositorNodeImage", "Grain Texture", (350, -300), image=film_grain_image())
    grain = mixrgb("Film Grain (Fac = amount)", (550, 0), "OVERLAY", LENS["grain"])
    tint = mixrgb("Shadow Tint (colour = lift)", (750, 0), "ADD")
    mix_in(tint, "B").default_value = LENS["shadow_tint"]

    sgrain = mixrgb("Shadow Grain (Fac = amount)", (900, 0), "LINEAR_LIGHT", LENS["shadow_grain"])
    if LEGACY_COMP:
        comp = t.nodes.new("CompositorNodeComposite")
    else:
        comp = t.nodes.new("NodeGroupOutput")
    comp.location = (1100, 0)
    view = t.nodes.new("CompositorNodeViewer"); view.location = (1000, -200)

    L = t.links.new
    A = lambda n: mix_in(n, "A")  # noqa: E731
    B = lambda n: mix_in(n, "B")  # noqa: E731
    L(rl.outputs["Image"], soften.inputs["Image"])
    L(rl.outputs["Alpha"], cover.inputs["Image"])
    L(out(cover), kill.inputs[0])
    L(out(kill), outside.inputs[1])
    L(rl.outputs["Alpha"], arc_cover.inputs["Image"])
    L(out(arc_cover), arc_kill.inputs[0])
    L(out(arc_kill), arc_outside.inputs[1])
    L(rl.outputs["halo"], halo_tight.inputs["Image"])
    L(rl.outputs["halo"], halo_wide.inputs["Image"])
    L(out(halo_tight), A(wide_mix))
    L(out(halo_wide), B(wide_mix))
    L(out(wide_mix), A(halo_masked))
    L(out(outside), B(halo_masked))
    L(out(soften), A(halo_add))
    L(out(halo_masked), B(halo_add))
    L(rl.outputs["arc_glow"], arc_move.inputs["Image"])
    for b in arc_b:
        L(out(arc_move), b.inputs["Image"])
    L(out(arc_b[0]), A(arc_near))
    L(out(arc_near), A(arc_m1))
    L(out(arc_b[1]), B(arc_m1))
    L(out(arc_m1), A(arc_blur))
    L(out(arc_b[2]), A(arc_far_tint))
    L(out(arc_far_tint), B(arc_blur))
    L(out(halo_add), A(arc_add))
    arc_masked = mixrgb("Arc Glow × Outside", (-200, -700), "MULTIPLY")
    L(out(arc_blur), A(arc_masked))
    L(out(arc_outside), B(arc_masked))
    L(out(arc_masked), B(arc_add))
    L(rl.outputs["Alpha"], cres_move.inputs["Image"])
    L(out(cres_move), cres_hole.inputs[0])
    L(rl.outputs["Alpha"], cres_hole.inputs[1])
    L(out(cres_hole), cres_soft.inputs["Image"])
    L(out(cres_soft), A(cres_col))
    L(out(cres_soft), cres_glow.inputs["Image"])
    L(out(cres_glow), A(cres_glow_col))
    L(out(cres_col), A(cres_sum))
    L(out(cres_glow_col), B(cres_sum))
    L(out(arc_add), A(cres_add))
    L(out(cres_sum), B(cres_add))
    L(out(cres_add), bloom.inputs["Image"])
    L(bloom.outputs["Image"], lens.inputs["Image"])
    L(out(lens), A(grain))
    L(grain_img.outputs["Image"], B(grain))
    L(out(grain), A(tint))
    L(out(tint), A(sgrain))
    L(grain_img.outputs["Image"], B(sgrain))
    L(out(sgrain), comp.inputs["Image"])
    L(out(sgrain), view.inputs["Image"])
    for n in nodes + [soften]:
        n.parent = frame


def build_scene(subject="sphere"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "Eclipse"

    if subject == "suzanne":
        bpy.ops.mesh.primitive_monkey_add(size=1.9, location=(0, 0, -0.03))
        bpy.ops.object.modifier_add(type="SUBSURF")
        bpy.context.active_object.modifiers[-1].levels = 2
        bpy.context.active_object.modifiers[-1].render_levels = 2
    elif subject == "torus":
        bpy.ops.mesh.primitive_torus_add(major_radius=0.75, minor_radius=0.3, location=(0, 0, -0.03),
                                         rotation=(math.radians(70), 0, 0))
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.02, segments=128, ring_count=64, location=(0, 0, -0.03))
    bpy.ops.object.shade_smooth()
    obj = bpy.context.active_object
    obj.name = "Eclipse Subject"
    obj.data.materials.append(build_material())

    bpy.ops.object.camera_add(location=(0, -10, 0), rotation=(math.radians(90), 0, 0))
    cam = bpy.context.active_object
    cam.data.sensor_fit = "VERTICAL"
    cam.data.sensor_height = 36
    cam.data.lens = 36 * 10 / 3.85  # sphere spans ~80% of frame width
    scene.camera = cam

    world = bpy.data.worlds.new("Black")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
    scene.world = world

    scene.render.engine = "CYCLES"
    enable_gpu(scene)
    scene.cycles.samples = 32
    scene.cycles.use_denoising = False
    scene.render.resolution_x, scene.render.resolution_y = RES
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "Standard"
    scene.render.film_transparent = True  # Alpha = object coverage, used to mask the halo
    scene.render.image_settings.color_mode = "RGB"
    for name in ("halo", "arc_glow"):
        aov = scene.view_layers[0].aovs.add(); aov.name = name; aov.type = "COLOR"
    build_compositor(scene)

    # Open the saved file looking through the camera in rendered mode with the compositor on.
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.shading.type = "RENDERED"
                    space.shading.use_compositor = "ALWAYS"
                    space.region_3d.view_perspective = "CAMERA"
    return scene


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    tag = argv[argv.index("--tag") + 1] if "--tag" in argv else "wip"
    subject = argv[argv.index("--subject") + 1] if "--subject" in argv else "sphere"
    scene = build_scene(subject)
    scene.render.filepath = str(EXP["renders"] / f"{NAME}_{tag}.png")
    bpy.ops.render.render(write_still=True)
    blend = f"{NAME}.blend" if subject == "sphere" else f"{NAME}_{subject}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(EXP["output"] / blend))
    print("ECLIPSE OK")
