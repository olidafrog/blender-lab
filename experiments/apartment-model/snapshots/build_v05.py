"""apartment-model: Flat 233, Manhattan Building, Bow Quarter — the shell, built from measured values.

Run from the repo root:
  tools/blender.sh experiments/apartment-model/scripts/build.py --out v01 --views 2,3 --samples 128 --scale 0.5
  ... --views all          every camera fitted to a reference photo (assets/cams/<n>.json)
  ... --set key=value      override any value in P
  ... --save               also save output/apartment-model.blend
  ... --preflight          no render: the correctness sheet (clay, mirror, albedo 0, each light alone)

Frame: the aligned LiDAR scan (metres). x runs along the room from the window wall (x = -4.40) to the
back of the flat; y across, west (-) to east (+); z up, floor 0. Windows face 142 deg (SE).
Every dimension comes from the scan (plane fits) where it reached, else from the 1:60 plan.
"""
import argparse
import ast
import json
import math
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))
sys.path.insert(0, str(HERE))
from common import enable_gpu, experiment_paths  # noqa: E402
from nodes import auto_layout, group, how_to_tweak, material_from_group  # noqa: E402
from comp import LEGACY, compositor, post_group, use_saved_render  # noqa: E402
from preflight import sheet  # noqa: E402
import shell_kit as K  # noqa: E402

EXP = experiment_paths(__file__)

P = {
    # ---- render
    "res_x": 2048, "res_y": 1536,          # the photos' size; --scale picks the fraction
    "exposure": 2.5,                       # film exposure, stops
    "view": "AgX",                         # AgX | Khronos PBR Neutral | Standard
    "look": "None",
    "wb_temp": 6500.0, "wb_tint": 10.0,
    "clay": False,
    # ---- sky (bright overcast, CIE-like: zenith 3x horizon)
    "sky_strength": 9.8,         # zenith radiance; horizontal irradiance = 7/9 pi x this (~24 W/m2)
    "sky_camera": 0.3,           # what the camera sees directly through the glass, x the lighting sky
    "sky_colour": (0.86, 0.90, 1.0, 1.0),
    "ground_colour": (0.18, 0.17, 0.15, 1.0),
    "portals": True,
    # ---- main room planes (scan)
    "win_x": -4.40,          # window wall inner face (brick)
    "win_t": 0.45,           # window wall thickness (outer face not measured)
    "west_y": -2.875, "east_y": 2.75,
    "side_t": 0.28,          # party walls (plan)
    "ceil_z": 4.08,
    "slab_t": 0.30,          # floor and roof slab thickness (not visible)
    # ---- ceiling structure
    "beam_w": 0.25, "beam_y": -0.03, "beam_z": 3.73,          # central downstand beam
    "girder_x0": 0.90, "girder_z": 3.68,                       # cross girder over the mezzanine front
    "haunch": 0.12,                                            # splayed pilaster head under the girder
    "pilaster_x": (0.85, 1.29), "pilaster_proud": (0.20, 0.12),  # RC frame columns on the side walls (W, E)
    "under_mezz_y": (-2.755, 2.825),                           # side wall faces under the mezzanine
    "edge_beam_z": 3.72, "edge_beam_proud": 0.05,              # beams along the side walls
    "corner_brick_w": 0.20,  # brick returns on the side walls next to the window wall
    # ---- windows (brick openings; frame plane further out)
    "win_cy": (-1.625, 1.425),    # opening centres (y)
    "win_w": 1.55,                # opening width at the brick face
    "win_sill": 1.11,
    "win_spring": 3.50,           # segmental head: photo 2 rise ~0.18 of the span (v03)
    "win_rise": 0.30,             # arch rise above the spring
    "frame_x": -4.60,             # glazing plane
    "frame_w": 0.06,              # outer frame member width
    "frame_d": 0.06,
    "bar_w": 0.03,                # glazing bars
    "win_cols": 4,
    "win_transoms": (2.42, 3.12), # heavy transom, transom at the spring
    "win_lower_bar": 1.80,        # bar across the lower lights
    "track_z": 3.95,              # curtain track under the ceiling
    "sash_top": 3.12,             # opening sashes run from the sill to the spring transom
    "sash_deg": ((0.0, 70.0), (20.0, 60.0)),   # (left, right) half per window, degrees open into the room
    # ---- brick piers proud of the window wall
    "pier_proud": 0.15, "pier_top": 1.52, "pier_cap": 0.10,
    "piers": ((-2.875, -2.42), (-0.85, 0.50), (2.13, 2.75)),
    # ---- mezzanine
    "mezz_x": 1.29, "mezz_t": 0.15,
    "soffit_z": 1.93, "mezz_floor_z": 2.08,
    "fascia_h": 0.07,
    "iwin": ((0.64, 2.30), (-2.40, -0.68)),   # internal windows (y ranges)
    "iwin_z": (2.64, 3.66),         # sill raised from the scan 2.52 by the photo 3/6 overlays (v02)
    "iwin_set": 0.01,               # frame set back from the room face of the mezzanine front
    "iwin_frame": 0.04,
    "col_y": -0.02, "col_w": 0.13,
    # ---- under the mezzanine (scan)
    "kitchen_back_x": 3.50, "dining_back_x": 4.34, "split_y": 0.10,
    "door_y": (0.12, 0.90), "door_h": 1.93,
    "counter_h": 0.90, "counter_d": 0.60,
    "island": (1.35, 1.95, -1.35, 0.10),       # x0 x1 y0 y1
    "bookcase": (4.02, 4.34, 0.96, 2.72),
    "radiator": (-2.15, -1.12, 0.30, 0.98),     # west wall: x0 x1 z0 z1 (column radiator)
    "panel_heater": (1.75, 2.35, 0.18, 0.62),   # dining east wall: x0 x1 z0 z1
    "shelf_z": (1.26, 1.62), "shelf_x": (1.39, 3.50),
    # ---- rest of the flat (1:60 plan, 72 px/m at 110 dpi, pinned to the scan)
    "plan_kx": 0.98, "plan_ky": 0.995,
    "upper_ceil_z": 4.08,
    # ---- looks
    "paint": (0.80, 0.79, 0.76, 1.0),
    "brick": (0.20, 0.075, 0.05, 1.0), "brick_dark": (0.11, 0.045, 0.035, 1.0), "mortar": (0.38, 0.34, 0.29, 1.0),
    "oak": (0.33, 0.19, 0.10, 1.0),
    "steel_white": (0.72, 0.71, 0.66, 1.0),
    "steel_black": (0.025, 0.025, 0.025, 1.0),
    "grey": (0.45, 0.45, 0.45, 1.0),
    "units": (0.70, 0.69, 0.65, 1.0),
    "bookcase_col": (0.045, 0.05, 0.055, 1.0),
    # ---- furniture blocks
    "furniture": True,
}

HOW_TO_TWEAK = """\
apartment-model — how to tweak

The scene is built from measured values in build.py (P). Collections: Shell (walls, slabs,
beams), Windows, Mezzanine, Kitchen, Flat (grey boxes for the other rooms), Furniture (blocks),
Outside (sky ground, portals).

- Each material is one node: select an object, open the Shader Editor, change the group inputs.
- Daylight: World > Sky node group (Strength). Exposure: Render > Color Management.
- Cameras: one per reference photo, named Cam_<n>. Set one active to compare with the photo.

Built by experiments/apartment-model/scripts/build.py. Changes made here are lost on rebuild;
copy good values back into P.
"""


# --------------------------------------------------------------------------- materials

def simple_group(name, colour, rough, metal=0.0):
    ng, gi, go = group(name, [
        ("Colour", "NodeSocketColor", colour, None, None),
        ("Roughness", "NodeSocketFloat", rough, 0.0, 1.0),
    ], [("Shader", "NodeSocketShader")])
    b = ng.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Metallic"].default_value = metal
    ng.links.new(gi.outputs["Colour"], b.inputs["Base Color"])
    ng.links.new(gi.outputs["Roughness"], b.inputs["Roughness"])
    ng.links.new(b.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def brick_group():
    """Brick on walls in plane x: the pattern runs in (y, z)."""
    ng, gi, go = group("Brick", [
        ("Brick", "NodeSocketColor", P["brick"], None, None),
        ("Brick Dark", "NodeSocketColor", P["brick_dark"], None, None),
        ("Mortar", "NodeSocketColor", P["mortar"], None, None),
        ("Roughness", "NodeSocketFloat", 0.85, 0.0, 1.0),
    ], [("Shader", "NodeSocketShader")])
    n = ng.nodes
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    comb = n.new("ShaderNodeCombineXYZ")
    ng.links.new(tc.outputs["Object"], sep.inputs[0])
    # use y+x as the running direction so side faces of piers still get courses
    add = n.new("ShaderNodeMath"); add.operation = "ADD"
    ng.links.new(sep.outputs["Y"], add.inputs[0]); ng.links.new(sep.outputs["X"], add.inputs[1])
    ng.links.new(add.outputs[0], comb.inputs["X"])
    ng.links.new(sep.outputs["Z"], comb.inputs["Y"])
    bt = n.new("ShaderNodeTexBrick")
    bt.inputs["Scale"].default_value = 1.0
    bt.inputs["Brick Width"].default_value = 0.225
    bt.inputs["Row Height"].default_value = 0.076
    bt.inputs["Mortar Size"].default_value = 0.010
    bt.offset = 0.5
    ng.links.new(comb.outputs[0], bt.inputs["Vector"])
    ng.links.new(gi.outputs["Brick"], bt.inputs["Color1"])
    ng.links.new(gi.outputs["Brick Dark"], bt.inputs["Color2"])
    ng.links.new(gi.outputs["Mortar"], bt.inputs["Mortar"])
    b = n.new("ShaderNodeBsdfPrincipled")
    ng.links.new(bt.outputs["Color"], b.inputs["Base Color"])
    ng.links.new(gi.outputs["Roughness"], b.inputs["Roughness"])
    bump = n.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.4
    bump.inputs["Distance"].default_value = 0.004
    inv = n.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    ng.links.new(bt.outputs["Fac"], inv.inputs[1])
    ng.links.new(inv.outputs[0], bump.inputs["Height"])
    ng.links.new(bump.outputs[0], b.inputs["Normal"])
    ng.links.new(b.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def glass_group():
    """Thin window glass: transparent plus a Fresnel reflection (tested: 3 % below an open hole, same noise)."""
    ng, gi, go = group("Glass", [("IOR", "NodeSocketFloat", 1.45, 1.0, 2.0)], [("Shader", "NodeSocketShader")])
    n = ng.nodes
    tr = n.new("ShaderNodeBsdfTransparent")
    gl = n.new("ShaderNodeBsdfGlossy"); gl.inputs["Roughness"].default_value = 0.0
    fr = n.new("ShaderNodeFresnel")
    ng.links.new(gi.outputs["IOR"], fr.inputs["IOR"])
    mix = n.new("ShaderNodeMixShader")
    ng.links.new(fr.outputs[0], mix.inputs[0])
    ng.links.new(tr.outputs[0], mix.inputs[1]); ng.links.new(gl.outputs[0], mix.inputs[2])
    ng.links.new(mix.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def make_materials():
    M = {}
    for key, col, r in (("paint", P["paint"], 0.9), ("oak", P["oak"], 0.45), ("steel_white", P["steel_white"], 0.4),
                        ("steel_black", P["steel_black"], 0.35), ("grey", P["grey"], 0.8), ("units", P["units"], 0.5),
                        ("bookcase", P["bookcase_col"], 0.6), ("ground", P["ground_colour"], 1.0)):
        M[key] = material_from_group(key.title(), simple_group(key.title(), col, r))
    M["brick"] = material_from_group("Brick", brick_group())
    M["glass"] = material_from_group("Glass", glass_group())
    M["worktop"] = material_from_group("Worktop", simple_group("Worktop", (0.82, 0.82, 0.8, 1), 0.25))
    return M


# --------------------------------------------------------------------------- plan mapping

def PX(py):
    """Plan pixel row (110 dpi render of EX-01) to scene x."""
    return P["win_x"] + (py - 180) / 72 * P["plan_kx"]


def PY(px):
    """Plan pixel column to scene y (second floor; the third floor sits 500 px to the right)."""
    return P["west_y"] + (px - 500) / 72 * P["plan_ky"]


# --------------------------------------------------------------------------- the shell

def build_shell(M):
    wx, W, E, C = P["win_x"], P["west_y"], P["east_y"], P["ceil_z"]
    st, back = P["side_t"], PX(980)
    ext = back + P["side_t"]
    # floor and roof slabs over the whole flat
    K.box("Floor", wx - P["win_t"], ext, W - st, E + st, -P["slab_t"], 0, M["oak"])
    K.box("Roof", wx - P["win_t"], ext, W - st, E + st, C, C + P["slab_t"], M["paint"])
    # party walls (west, east) and the back wall
    K.box("Wall_W", wx, ext, W - st, W, 0, C, M["paint"])
    K.box("Wall_E", wx, ext, E, E + st, 0, C, M["paint"])
    K.box("Wall_Back", back, ext, W, E, 0, C, M["paint"])
    # brick returns: a thin brick skin on the side walls next to the window wall
    cb = P["corner_brick_w"]
    K.box("Brick_Return_W", wx, wx + cb, W, W + 0.004, 0, C, M["brick"])
    K.box("Brick_Return_E", wx, wx + cb, E - 0.004, E, 0, C, M["brick"])

    # window wall: brick, two segmental-arched openings
    holes = [K.arch_loop(cy, P["win_w"] / 2, P["win_sill"], P["win_spring"], P["win_rise"]) for cy in P["win_cy"]]
    K.wall("Window_Wall", K.rect(W - st, 0, E + st, C), holes, wx - P["win_t"], wx, "x", M["brick"])
    # brick piers proud of the wall, with a sloped cap
    for i, (y0, y1) in enumerate(P["piers"]):
        x1 = wx + P["pier_proud"]
        K.box(f"Pier_{i}", wx, x1, y0, y1, 0, P["pier_top"] - P["pier_cap"], M["brick"])
        K.prism(f"Pier_Cap_{i}", [(wx, P["pier_top"] - P["pier_cap"]), (x1, P["pier_top"] - P["pier_cap"]),
                                  (wx, P["pier_top"])], y0, y1, "y", M["brick"])
    # window sills (brick, flat) are the bottom of the opening; add a timber/stone board
    for i, cy in enumerate(P["win_cy"]):
        hw = P["win_w"] / 2
        K.box(f"Sill_{i}", P["frame_x"], wx + 0.02, cy - hw, cy + hw, P["win_sill"] - 0.04, P["win_sill"], M["paint"])

    # ceiling structure
    gx = P["girder_x0"]
    K.box("Beam_Central", wx, gx, P["beam_y"] - P["beam_w"] / 2, P["beam_y"] + P["beam_w"] / 2, P["beam_z"], C, M["paint"])
    K.box("Girder", gx, P["mezz_x"] + P["mezz_t"], W, E, P["girder_z"], C, M["paint"])
    h = P["haunch"]
    px0, px1 = P["pilaster_x"]
    for k, (side, y) in enumerate((("W", W), ("E", E))):
        s = 1 if side == "W" else -1
        face = y + s * P["pilaster_proud"][k]
        # RC frame column on the side wall, floor to girder, with a splayed head under the girder
        K.box(f"Pilaster_{side}", px0, px1, y, face, 0, P["girder_z"], M["paint"])
        loop = [(face, P["girder_z"]), (face + s * h, P["girder_z"]), (face, P["girder_z"] - h)]
        K.prism(f"Pilaster_Head_{side}", loop if s > 0 else loop[::-1], gx, px1, "x", M["paint"])
        y0, y1 = sorted((y, y + s * P["edge_beam_proud"]))
        K.box(f"Edge_Beam_{side}", wx + cb, px0, y0, y1, P["edge_beam_z"], C, M["paint"])
    # curtain tracks
    for i, cy in enumerate(P["win_cy"]):
        hw = P["win_w"] / 2 + 0.15
        K.box(f"Track_{i}", wx, wx + 0.06, cy - hw, cy + hw, P["track_z"] - 0.05, P["track_z"], M["steel_black"], "Windows")
    # column radiator on the west wall: vertical tubes on headers
    x0, x1, z0, z1 = P["radiator"]
    parts = [K.box("Rad_Head_T", x0, x1, W + 0.03, W + 0.09, z1 - 0.04, z1, M["paint"], "Shell"),
             K.box("Rad_Head_B", x0, x1, W + 0.03, W + 0.09, z0, z0 + 0.04, M["paint"], "Shell")]
    n = int((x1 - x0) / 0.065)
    for k in range(n):
        x = x0 + 0.01 + k * (x1 - x0 - 0.02) / max(n - 1, 1)
        parts.append(K.box(f"Rad_Col_{k}", x - 0.022, x + 0.022, W + 0.02, W + 0.10, z0, z1, M["paint"], "Shell"))
    K.join(parts, "Radiator_W")


def build_window(M, i, cy):
    """Steel factory window in the opening: outer frame on the arch, 4 columns, two transoms, a lower bar."""
    hw, sill, spring, rise = P["win_w"] / 2, P["win_sill"], P["win_spring"], P["win_rise"]
    fx, fd, fw, bw = P["frame_x"], P["frame_d"], P["frame_w"], P["bar_w"]
    a0, a1 = fx - fd / 2, fx + fd / 2
    mat = M["steel_white"]
    parts = []
    outer = K.arch_loop(cy, hw, sill, spring, rise)
    icu, ihw, isill, ispring, irise = K.inset_arch(cy, hw, sill, spring, rise, fw)
    inner = K.arch_loop(icu, ihw, isill, ispring, irise)
    parts.append(K.wall(f"Frame_{i}", outer, [inner], a0, a1, "x", mat, "Windows"))
    u0, u1 = cy - ihw, cy + ihw
    for k in range(1, P["win_cols"]):
        u = u0 + (u1 - u0) * k / P["win_cols"]
        top = K.arch_top(icu, ihw, ispring, irise, u)
        parts.append(K.bar_v(f"Mullion_{i}_{k}", u, bw, isill, top, a0 + 0.01, a1 - 0.01, "x", mat, "Windows"))
    for k, z in enumerate(P["win_transoms"]):
        w = bw * (2.2 if k == 0 else 1.4)
        parts.append(K.bar_h(f"Transom_{i}_{k}", z, w, u0, u1, a0, a1, "x", mat, "Windows"))
    K.join(parts, f"Window_{i}")
    # fixed glass: the top light above the sash transom
    st = P["sash_top"]
    cv, R, _ = K.seg_arch(icu, ihw, ispring, irise)
    top_loop = [(u1, st), (u1, ispring)] + K.arch_loop(icu, ihw, isill, ispring, irise)[3:-1] + [(u0, ispring), (u0, st)]
    K.wall(f"Glass_Top_{i}", top_loop, [], fx - 0.003, fx + 0.003, "x", M["glass"], "Windows")
    # two opening sashes (the lower part, each two columns wide), hinged on the jambs, open into the room
    for side, (h0, h1) in (("L", (u0, (u0 + u1) / 2)), ("R", ((u0 + u1) / 2, u1))):
        sp = []
        sw = 0.045
        sp.append(K.wall(f"Sash_{i}{side}_F", K.rect(h0, isill, h1, st), [K.rect(h0 + sw, isill + sw, h1 - sw, st - sw)],
                         a0 + 0.012, a1 - 0.012, "x", mat, "Windows"))
        sp.append(K.bar_v(f"Sash_{i}{side}_M", (h0 + h1) / 2, bw, isill, st, a0 + 0.015, a1 - 0.015, "x", mat, "Windows"))
        for k, z in enumerate((P["win_lower_bar"], P["win_transoms"][0])):
            sp.append(K.bar_h(f"Sash_{i}{side}_B{k}", z, bw * (1.8 if k else 1.0), h0, h1, a0 + 0.015, a1 - 0.015, "x", mat, "Windows"))
        sp.append(K.wall(f"Sash_{i}{side}_G", K.rect(h0 + sw, isill + sw, h1 - sw, st - sw), [], fx - 0.003, fx + 0.003, "x",
                         M["glass"], "Windows"))
        ob = K.join(sp, f"Sash_{i}{side}")
        hinge_u = h0 if side == "L" else h1
        from mathutils import Matrix, Vector
        hinge = Vector((a1, hinge_u, 0.0))
        ob.data.transform(Matrix.Translation(-hinge))
        ob.location = hinge
        ang = math.radians(P["sash_deg"][i][0 if side == "L" else 1])
        ob.rotation_euler = (0, 0, -ang if side == "L" else ang)   # free edge swings toward +x


def build_mezzanine(M):
    W, E, C = P["west_y"], P["east_y"], P["ceil_z"]
    mx, mt = P["mezz_x"], P["mezz_t"]
    back = PX(980)
    z0, z1 = P["iwin_z"]
    holes = [K.rect(a, z0, b, z1) for a, b in P["iwin"]]
    K.wall("Mezz_Front", K.rect(W, P["soffit_z"], E, P["girder_z"]), holes, mx, mx + mt, "x", M["paint"], "Mezzanine")
    K.box("Mezz_Floor", mx + 0.01, back, W, E, P["soffit_z"], P["mezz_floor_z"], M["paint"], "Mezzanine")
    K.box("Fascia", mx - 0.02, mx + 0.005, W, E, P["soffit_z"] - 0.0, P["soffit_z"] + P["fascia_h"], M["paint"], "Mezzanine")
    K.box("Column", mx - P["col_w"] / 2 + 0.02, mx + P["col_w"] / 2 + 0.02, P["col_y"] - P["col_w"] / 2,
          P["col_y"] + P["col_w"] / 2, 0, P["soffit_z"], M["paint"], "Mezzanine")
    # internal steel windows: 3 columns x 2 rows, casement column on the outer side
    f = P["iwin_frame"]
    for i, (a, b) in enumerate(P["iwin"]):
        parts = [K.wall(f"IFrame_{i}", K.rect(a, z0, b, z1), [K.rect(a + f, z0 + f, b - f, z1 - f)],
                        mx + P["iwin_set"], mx + P["iwin_set"] + 0.04, "x", M["steel_black"], "Mezzanine")]
        casement_left = (i == 1)                         # the west window has its casement on the left (photo 3)
        for k in (1, 2):
            u = a + (b - a) * k / 3
            w = f * (1.4 if (k == 1) == casement_left else 0.8)
            parts.append(K.bar_v(f"IMull_{i}_{k}", u, w, z0, z1, mx + P["iwin_set"] + 0.005, mx + P["iwin_set"] + 0.035, "x", M["steel_black"], "Mezzanine"))
        parts.append(K.bar_h(f"ITran_{i}", (z0 + z1) / 2, f * 0.8, a, b, mx + P["iwin_set"] + 0.005, mx + P["iwin_set"] + 0.035, "x", M["steel_black"], "Mezzanine"))
        K.join(parts, f"Internal_Window_{i}")
        g = mx + P["iwin_set"] + 0.02
        K.wall(f"IGlass_{i}", K.rect(a, z0, b, z1), [], g - 0.002, g + 0.002, "x", M["glass"], "Mezzanine")


def build_under_mezz(M):
    W, E, sz = P["west_y"], P["east_y"], P["soffit_z"]
    kx, dx, sy = P["kitchen_back_x"], P["dining_back_x"], P["split_y"]
    t = 0.12
    uw, ue = P["under_mezz_y"]
    K.box("Lining_W", P["pilaster_x"][1], kx, W, uw, 0, sz, M["paint"], "Mezzanine")
    W = uw
    K.box("Kitchen_Back", kx, kx + t, W, sy, 0, sz, M["paint"], "Mezzanine")
    K.box("Return_Wall", kx + 0.01, dx + t, sy - t, sy, 0, sz, M["paint"], "Mezzanine")
    d0, d1 = P["door_y"]
    K.wall("Dining_Back", K.rect(sy, 0, E, sz), [K.rect(d0, 0, d1, P["door_h"] - 0.0)], dx, dx + t, "x", M["paint"], "Mezzanine")
    # kitchen: run along the west wall, run along the back wall, island
    ch, cd = P["counter_h"], P["counter_d"]
    runs = [("Run_West", P["mezz_x"] + 0.05, kx, W, W + cd), ("Run_Back", kx - cd, kx, W + cd, sy)]
    x0, x1, y0, y1 = P["island"]
    runs.append(("Island", x0, x1, y0, y1))
    for name, a, b, c, d in runs:
        K.box(name, a, b, c, d, 0.1, ch - 0.03, M["units"], "Kitchen")
        K.box(name + "_Plinth", a + 0.05, b - 0.05 if name != "Run_West" else b, c + 0.05, d - 0.05, 0, 0.1, M["grey"], "Kitchen")
        K.box(name + "_Top", a - 0.01, b, c, d + 0.01, ch - 0.03, ch, M["worktop"], "Kitchen")
    # open shelves on the west wall (photo 1)
    for z in P["shelf_z"]:
        K.box(f"Shelf_{z}", *P["shelf_x"], W, W + 0.25, z, z + 0.035, M["oak"], "Kitchen")
    hx0, hx1, hz0, hz1 = P["panel_heater"]
    K.box("Panel_Heater", hx0, hx1, P["under_mezz_y"][1] - 0.07, P["under_mezz_y"][1] - 0.02, hz0, hz1, M["paint"], "Mezzanine")
    # dining bookcase (built in, wavy top in reality: block for now)
    b0, b1, c0, c1 = P["bookcase"]
    K.box("Bookcase", b0, b1, c0, c1, 0, sz, M["bookcase"], "Mezzanine")


def build_flat(M):
    """The rooms the scan did not reach: grey boxes from the plan."""
    g, sz, mz, C = M["grey"], P["soffit_z"], P["mezz_floor_z"], P["upper_ceil_z"]
    t = 0.12
    # second floor: shower room, stores, hallway, stair
    K.box("Shower_Wall_E", PX(773), PX(980), PY(615), PY(630), 0, sz, g, "Flat")
    K.box("Store_Wall_S", PX(925), PX(937), P["west_y"], PY(615), 0, sz, g, "Flat")
    K.box("Store2_Walls", PX(773), PX(838), PY(697), PY(710), 0, sz, g, "Flat")
    K.box("Hall_Wall_N", PX(825), PX(838), PY(770), P["east_y"], 0, sz, g, "Flat")
    # stair: a stepped block rising east along the north side of the hallway
    n = 12
    x0, x1 = PX(845), PX(905)
    for k in range(n):
        y0 = PY(822) + (PY(907) - PY(822)) * k / n
        K.box(f"Stair_{k}", x0, x1, y0, PY(907), 0, mz * (k + 1) / n, g, "Flat")
    # third floor (plan x - 500): bedrooms and upper hallway walls, from the upper floor level
    def UY(px):
        return PY(px - 500)
    K.box("Up_Wall_Bed1_E", P["mezz_x"] + P["mezz_t"], PX(980), UY(1208), UY(1218), mz, C, g, "Flat")
    K.box("Up_Wall_Bed2_S", PX(835), PX(845), UY(1280), P["east_y"], mz, C, g, "Flat")
    K.box("Up_Wardrobe", PX(928), PX(980), P["west_y"], UY(1208), mz, mz + 2.0, g, "Flat")
    K.box("Up_Stair_Void_Rail", PX(915), PX(920), UY(1335), P["east_y"], mz, mz + 0.9, g, "Flat")


def build_furniture(M):
    """Rough blocks from the scan's top view, so the photos' occlusion reads. Not judged."""
    g = M["grey"]
    # footprints and tops from connected components of the scan's up-facing faces (z 0.12-1.3)
    for name, x0, x1, y0, y1, z1 in (
        ("Sofa_Seat", -3.30, -0.95, -2.75, -1.90, 0.42), ("Sofa_Back", -3.30, -0.95, -2.75, -2.50, 0.70),
        ("Sofa_Arm", -1.15, -0.95, -2.75, -1.90, 0.58), ("Pouf", -4.00, -3.20, -0.45, 0.50, 0.45),
        ("Coffee_Table", -2.40, -1.10, -1.45, -0.95, 0.48), ("Rug", -4.0, -0.6, -1.90, -0.20, 0.03),
        ("Chair_1", -0.75, 0.15, -1.45, -0.45, 0.50), ("Chair_1_Back", -0.10, 0.15, -1.45, -0.65, 0.81),
        ("Chair_2", -0.75, 0.05, -0.20, 0.55, 0.50), ("Chair_2_Back", -0.20, 0.05, -0.15, 0.50, 0.83),
        ("Footstool", -1.30, -0.80, -0.15, 0.45, 0.46), ("Desk", -1.90, -0.15, 2.25, 2.70, 0.90),
        ("Stool", -3.75, -3.20, 1.25, 1.80, 0.47), ("Speaker_Unit", -3.70, -3.40, 1.85, 2.50, 0.59),
        ("Bookshelf", 0.60, 1.20, -2.85, -2.45, 1.75), ("Media_Unit", 0.60, 1.20, 2.10, 2.70, 0.40),
        ("Trolley", 0.70, 1.20, -1.30, -0.05, 0.80), ("Dining_Table", 1.9, 3.3, 1.35, 2.25, 0.75),
    ):
        K.box(name, x0, x1, y0, y1, 0.0 if name != "Rug" else 0.0, z1, g, "Furniture")


# --------------------------------------------------------------------------- light, world, cameras

def sky_world():
    """Bright overcast: a uniform sky brighter at the zenith, a dark ground below the horizon."""
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    ng, gi, go = group("Sky", [
        ("Strength", "NodeSocketFloat", P["sky_strength"], 0.0, 20.0),
        ("Sky Colour", "NodeSocketColor", P["sky_colour"], None, None),
        ("Ground Colour", "NodeSocketColor", P["ground_colour"], None, None),
        ("Camera View", "NodeSocketFloat", P["sky_camera"], 0.0, 1.0),
    ], [("Shader", "NodeSocketShader")], kind="ShaderNodeTree")
    n = ng.nodes
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    ng.links.new(tc.outputs["Generated"], sep.inputs[0])
    # CIE overcast: L ~ (1 + 2 sin(elevation)) / 3; z of the direction is sin(elevation)
    lum = n.new("ShaderNodeMath"); lum.operation = "MULTIPLY_ADD"
    ng.links.new(sep.outputs["Z"], lum.inputs[0]); lum.inputs[1].default_value = 2 / 3; lum.inputs[2].default_value = 1 / 3
    gt = n.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.0
    ng.links.new(sep.outputs["Z"], gt.inputs[0])
    mixc = n.new("ShaderNodeMix"); mixc.data_type = "RGBA"
    ng.links.new(gt.outputs[0], mixc.inputs["Factor"])
    ng.links.new(gi.outputs["Ground Colour"], mixc.inputs["A"])
    ng.links.new(gi.outputs["Sky Colour"], mixc.inputs["B"])
    gl = n.new("ShaderNodeMath"); gl.operation = "MAXIMUM"; gl.inputs[1].default_value = 0.33
    ng.links.new(lum.outputs[0], gl.inputs[0])
    s = n.new("ShaderNodeMath"); s.operation = "MULTIPLY"
    ng.links.new(gl.outputs[0], s.inputs[0]); ng.links.new(gi.outputs["Strength"], s.inputs[1])
    # camera rays (seen through the windows) get "Camera View" x the light; lighting keeps the full sky
    lp = n.new("ShaderNodeLightPath")
    cam = n.new("ShaderNodeMix"); cam.data_type = "FLOAT"
    ng.links.new(lp.outputs["Is Camera Ray"], cam.inputs["Factor"])
    cam.inputs["A"].default_value = 1.0
    ng.links.new(gi.outputs["Camera View"], cam.inputs["B"])
    s2 = n.new("ShaderNodeMath"); s2.operation = "MULTIPLY"
    ng.links.new(s.outputs[0], s2.inputs[0]); ng.links.new(cam.outputs["Result"], s2.inputs[1])
    s = s2
    bg = n.new("ShaderNodeBackground")
    ng.links.new(mixc.outputs["Result"], bg.inputs["Color"])
    ng.links.new(s.outputs[0], bg.inputs["Strength"])
    ng.links.new(bg.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    gn = nt.nodes.new("ShaderNodeGroup"); gn.node_tree = ng
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(gn.outputs[0], out.inputs["Surface"])
    return world


def portals():
    for i, cy in enumerate(P["win_cy"]):
        h = P["win_spring"] + P["win_rise"] - P["win_sill"]
        ld = bpy.data.lights.new(f"Portal_{i}", "AREA")
        ld.shape = "RECTANGLE"
        ld.size, ld.size_y = h, P["win_w"] * 1.1
        ok = False
        for owner in (getattr(ld, "cycles", None), ld):
            if owner is not None and hasattr(owner, "is_portal"):
                owner.is_portal = True
                ok = True
        ob = bpy.data.objects.new(f"Portal_{i}", ld)
        K.link(ob, "Outside")
        ob.location = (P["win_x"] - P["win_t"] - 0.02, cy, P["win_sill"] + h / 2)
        ob.rotation_euler = (0, math.radians(-90), 0)      # area lights emit along local -Z: here +x, into the room
        ob["purpose"] = "portal: guides sky sampling through the window opening"
        print(f"[out] portal {i}: is_portal set = {ok}")


def outside(M):
    """Ground in front of the building (the flat is about 8 m up) and the building opposite (photo 4)."""
    K.box("Ground", -80, P["win_x"] - 1.0, -60, 60, -8.6, -8.5, M["ground"], "Outside")
    K.box("Opposite", -45, -32, -30, 25, -8.5, 6.0, M["grey"], "Outside")


def cameras(scene):
    cams = {}
    for path in sorted((EXP["root"] / "assets/cams").glob("*.json")):
        d = json.load(open(path))
        f = d.get("refined") or d.get("fit")
        if not f:
            continue
        n = path.stem
        cd = bpy.data.cameras.new(f"Cam_{n}")
        cd.sensor_fit = "HORIZONTAL"
        cd.sensor_width = f.get("sensor_w", 34.62)
        cd.lens = f["lens"]
        cd.clip_start = 0.05
        ob = bpy.data.objects.new(f"Cam_{n}", cd)
        K.link(ob, "Cameras")
        ob.location = f["loc"]
        ob.rotation_euler = [math.radians(a) for a in f["rot_deg"]]
        cams[n] = ob
    return cams


# --------------------------------------------------------------------------- run

def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="wip")
    ap.add_argument("--views", default="2")
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
        try:
            P[k] = ast.literal_eval(v)
        except (ValueError, SyntaxError):
            P[k] = v
    return a


def post():
    ng, gi, go = post_group("Post", [("Exposure", "NodeSocketFloat", 0.0, -3.0, 3.0)])
    ex = ng.nodes.new("CompositorNodeExposure")
    ng.links.new(gi.outputs["Image"], ex.inputs["Image"])
    ng.links.new(gi.outputs["Exposure"], ex.inputs["Exposure"])
    ng.links.new(ex.outputs["Image"], go.inputs["Image"])
    auto_layout(ng)
    return ng


def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    enable_gpu(scene)
    M = make_materials()
    build_shell(M)
    for i, cy in enumerate(P["win_cy"]):
        build_window(M, i, cy)
    build_mezzanine(M)
    build_under_mezz(M)
    build_flat(M)
    if P["furniture"]:
        build_furniture(M)
    outside(M)
    scene.world = sky_world()
    if P["portals"]:
        portals()
    cams = cameras(scene)
    nf = sum(len(o.data.polygons) for o in scene.objects if o.type == "MESH")
    print(f"[out] objects {len(scene.objects)}, faces {nf}, cameras {sorted(cams)}")
    scene.render.resolution_x, scene.render.resolution_y = P["res_x"], P["res_y"]
    cy = scene.cycles
    cy.use_denoising = True
    cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces, cy.transmission_bounces = 16, 12, 4, 8
    cy.transparent_max_bounces = 16
    cy.sample_clamp_indirect = 0.0            # physical sky units: a clamp of 10 removed 7 % of the light
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.02
    cy.denoising_prefilter = "ACCURATE"
    cy.film_exposure = 2 ** P["exposure"]
    vs = scene.view_settings
    vs.view_transform = P["view"]
    vs.look = P["look"] if P["look"] != "None" else "None"
    vs.use_white_balance = (P["wb_temp"], P["wb_tint"]) != (6500.0, 10.0)
    vs.white_balance_temperature, vs.white_balance_tint = P["wb_temp"], P["wb_tint"]
    if P["clay"]:
        clay = bpy.data.materials.new("Clay")
        clay.use_nodes = True
        scene.view_layers[0].material_override = clay
    how_to_tweak(HOW_TO_TWEAK)
    return scene, cams


if __name__ == "__main__":
    args = parse_args()
    scene, cams = build_scene()
    raw = EXP["renders"] / f"{args.out}_raw.exr"
    compositor(scene, post(), raw_exr=raw)
    scene.cycles.samples = args.samples
    scene.render.resolution_percentage = round(args.scale * 100)
    views = sorted(cams, key=int) if args.views == "all" else args.views.split(",")
    scene.camera = cams[views[0]]
    if args.preflight:
        sheet(scene, EXP["reviews"] / f"preflight_{args.out}.png", tiles_dir=EXP["renders"] / f"preflight_{args.out}")
        args.norender, args.save = True, False
    if not args.norender:
        for v in views:
            scene.camera = cams[v]
            scene.render.filepath = str(EXP["renders"] / f"{args.out}_{v}.png")
            bpy.ops.render.render(write_still=True)
        # crisp object-id pass (Workbench, flat random colours) for the edge overlay on the photos
        scene.render.engine = "BLENDER_WORKBENCH"
        sh = scene.display.shading
        sh.light, sh.color_type = "FLAT", "RANDOM"
        scene.view_settings.view_transform = "Standard"
        hidden = [o for o in scene.objects if o.name.startswith("Portal")]
        for o in hidden:
            o.hide_render = True
        for v in views:
            scene.camera = cams[v]
            scene.render.filepath = str(EXP["renders"] / f"{args.out}_{v}_ids.png")
            bpy.ops.render.render(write_still=True)
        scene.render.engine = "CYCLES"
        scene.view_settings.view_transform = P["view"]
        for o in hidden:
            o.hide_render = False
    if args.save:
        blend = EXP["output"] / f"{EXP['name']}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        blend.with_suffix(".blend1").unlink(missing_ok=True)
    print("BUILD OK")
