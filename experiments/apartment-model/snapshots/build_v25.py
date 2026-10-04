"""apartment-model: Flat 233, Manhattan Building, Bow Quarter — the shell, built from measured values.

Run from the repo root:
  tools/blender.sh experiments/apartment-model/scripts/build.py --out v01 --views 2,3 --samples 128 --scale 0.5
  ... --views all          every camera fitted to a reference photo (assets/cams/<n>.json)
  ... --set key=value      override any value in P
  ... --save               also save output/apartment-model.blend
  ... --preflight          no render: the correctness sheet (clay, mirror, albedo 0, each light alone)
  ... --scale 2 --finish   photographic output stage (round three): render 2x, keep it as <out>_<view>_2x.png, and
                           write <out>_<view>.png at the photo size through tools/photo_finish.py (Lanczos, unsharp, JPEG)

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
import mat_kit  # noqa: E402
sys.path.insert(0, str(HERE / "furniture"))
import sofa  # noqa: E402

EXP = experiment_paths(__file__)

P = {
    # ---- render
    "res_x": 2048, "res_y": 1536,          # the photos' size; --scale picks the fraction
    "exposure": 2.5,                       # film exposure, stops
    "view": "AgX",                         # AgX | Khronos PBR Neutral | Standard
    "look": "None",
    "wb_temp": 13000.0, "wb_tint": 10.0,    # warm like the phone: paint R/B 1.24 in photo 2 (round two)
    "clay": False,
    "finish": (1.0, 80, 85),       # --finish: unsharp radius px, percent, JPEG quality (photo 2 edge ratio 1.36; this 1.41)
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
    "beam_w": 0.25, "beam_y": -0.03, "beam_z": 3.72,          # central downstand beam
    "girder_x0": 0.9, "girder_z": 3.68,                       # cross girder over the mezzanine front
    "haunch": 0.10,                                            # splayed pilaster head under the girder
    "pilaster_x": (0.77, 1.29), "pilaster_proud": (0.1075, 0.0525),  # RC frame columns on the side walls (W, E)
    "under_mezz_y": (-2.755, 2.825),                           # side wall faces under the mezzanine
    "cove_z": 3.69, "cove_in": (0.05, 0.05),                   # side walls curve into the room to the ceiling (W, E; scan + advisor)
    "corner_brick_w": 0.20,  # brick returns on the side walls next to the window wall
    # ---- windows (brick openings; frame plane further out)
    "win_cy": (-1.625, 1.425),    # opening centres (y)
    "win_w": 1.5963,                # opening width at the room face (splayed reveal; 1.70 drew a false arris in photo 2)
    "win_w_frame": 1.45,          # opening width at the glazing plane (scan)
    "reveal_shift": 0.09,         # room-face opening shifted toward the central pier (photos 2 + 5: asymmetric splay)
    "win_sill": 1.11,
    "win_spring": 3.5,           # segmental head: photo 2 rise ~0.18 of the span (v03)
    "win_rise": 0.3,             # arch rise above the spring
    "frame_x": -4.60,             # glazing plane
    "frame_w": 0.04,              # outer frame member width (v12: photo steel ~3 px in row 2)
    "frame_d": 0.06,
    "bar_w": 0.02,                # glazing bars
    "win_cols": 4,
    "win_transoms": (2.42, 3.12), # heavy transom, transom at the spring
    "win_lower_bar": 1.80,        # bar across the lower lights
    "track_z": 3.95,              # curtain track under the ceiling
    "sash_top": 3.12,             # opening sashes run from the sill to the spring transom
    "sash_deg": ((0.0, 0.0), (0.0, 0.0)),   # (left, right) half per window, degrees open into the room; closed (user: only the factory windows matter)
    # ---- brick piers proud of the window wall
    "pier_proud": 0.145, "pier_top": 1.585, "pier_cap": 0.10,
    "piers": ((-2.875, -2.42), (-0.85, 0.50), (2.13, 2.75)),
    # ---- mezzanine
    "mezz_x": 1.29, "mezz_t": 0.15,
    "soffit_z": 1.93, "mezz_floor_z": 2.08,
    "fascia_h": 0.07,
    "iwin": ((0.64, 2.30), (-2.40, -0.68)),   # internal windows (y ranges)
    "iwin_z": (2.64, 3.66),         # sill raised from the scan 2.52 by the photo 3/6 overlays (v02)
    "iwin_set": 0.01,               # frame set back from the room face of the mezzanine front
    "iwin_frame": 0.04,
    "col_y": 0.0025, "col_w": 0.115, "col_d": 0.07,   # column width across, depth along the room
    # ---- under the mezzanine (scan)
    "kitchen_back_x": 3.50, "dining_back_x": 4.34, "split_y": 0.10,
    "door_y": (0.12, 0.78), "door_h": 1.93,          # east jamb 0.78 from photo 6 back-projection (v12)
    "counter_h": 0.90, "counter_d": 0.60,
    "island": (1.35, 1.95, -1.35, 0.10),       # x0 x1 y0 y1
    "bookcase": (4.02, 4.34, 0.96, 2.72),
    "bookcase_base": 0.88,                       # cupboard base height under the open bays
    "radiator": (-2.15, -1.12, 0.3, 0.94),     # west wall: x0 x1 z0 z1 (column radiator)
    "panel_heater": (1.75, 2.35, 0.18, 0.62),   # dining east wall: x0 x1 z0 z1
    "shelf_z": (1.26, 1.62), "shelf_x": (1.39, 3.50),
    # ---- rest of the flat (1:60 plan, 72 px/m at 110 dpi, pinned to the scan)
    "plan_kx": 0.98, "plan_ky": 0.995,
    "upper_ceil_z": 4.08,
    # ---- looks
    "paint": (0.80, 0.79, 0.76, 1.0),
    "oak": (0.33, 0.19, 0.10, 1.0),           # kitchen shelves
    # ---- brick (round two; levels from scripts/mat_measure.py: brick/paint luma 0.21-0.25 in photos 2, 5)
    "brick": (0.08, 0.05, 0.07, 1.0), "brick_dark": (0.042, 0.031, 0.04, 1.0),        # plum-maroon (v14-v16 reviews; photo 2 hue)
    "brick_pale": (0.15, 0.115, 0.125, 1.0), "mortar": (0.10, 0.085, 0.085, 1.0),   # pale = the grey-violet bloom; mortar a touch lighter
    "brick_var": 1.0, "brick_dust": 0.5, "mortar_depth": 0.3,
    # brick scan (Poly Haven factory_brick, CC0, 1.5 m tile, 16 courses): scaled to 1.36 m so a course is 85 mm
    "brick_tex_dir": EXP["root"].parents[1] / "library/textures/brick/factory_brick",
    "brick_tex_size": 1.36, "brick_tex_z0": 0.0,
    "brick_joint_t": 0.635,       # height below which the scan is joint (its 20th percentile)
    # ---- herringbone floor (rectified photos 2, 3, 8: spine along the room; photo 2 read 700 x 140, photo 8 and two reviews ~20 % smaller: 600 x 120, the common size)
    # rustic oak scan (Poly Haven oak_wood_planks, CC0, 1.2 m; v16 review: the clean veneer read as fresh-cut):
    # scaled 1.6x so a 140 mm plank fits inside one of its ~90 mm source planks; centres of the clean ones (V)
    "oak_tex": EXP["root"].parents[1] / "library/textures/wood/oak_wood_planks/oak_wood_planks_diff_2k.jpg",
    "oak_rough_tex": EXP["root"].parents[1] / "library/textures/wood/oak_wood_planks/oak_wood_planks_rough_2k.jpg",
    "oak_tex_size": 1.64,       # 1.37x: a 120 mm plank fits inside one ~92 mm source plank
    "oak_tex_strips": tuple(round(1 - r / 2048, 4) for r in (710, 871, 1040, 1210, 1648, 1818)),
    "oak_tint": (1.0, 1.0, 1.0, 1.0), "oak_bright": 1.25, "oak_sat": 0.45, "oak_grain": 2.0,
    "oak_var": 0.6, "oak_seams": 0.9, "oak_rough": 0.3, "oak_aniso": 0.3, "oak_spec": 0.4,
    "plank_ratio": 5, "plank_w": 0.12, "plank_bevel": 0.001, "ring_sp": 0.014,
    "plank_x0": 0.0, "plank_y0": -0.09,       # pattern origin: puts a tip line at y 0.80 (rectified photo 2)
    "steel_white": (0.72, 0.71, 0.66, 1.0),
    "steel_black": (0.025, 0.025, 0.025, 1.0),
    "grey": (0.45, 0.45, 0.45, 1.0),
    "units": (0.70, 0.69, 0.65, 1.0),
    "bookcase_col": (0.045, 0.05, 0.055, 1.0),
    # ---- furniture blocks
    "furniture": True,
    # ---- furniture: sofa (Swyft Model 03 three-seater + ottoman, Pumice; sizes from Swyft, placement from the scan)
    "sofa": True,
    "sofa_x_end": -0.87,          # outer face of the room-end arm (scan: arm end, seat seams at -1.79 and -2.49)
    "sofa_y_front": -1.70,        # seat fronts (scan section); the back is 0.92 behind, ~0.25 off the wall
    "sofa_d": 0.92, "sofa_seat_w": 0.70, "sofa_arm_w": 0.22,
    "sofa_arm_h": 0.56, "sofa_arm_setback": 0.12,       # arm top (Swyft, scan 0.56); seats proud of the arms (scan)
    "sofa_seat_h": 0.45, "sofa_back_h": 0.71, "sofa_back_t": 0.23,
    "sofa_seat_edge": 0.39,       # front seam height; the dome rises to sofa_seat_h (Swyft drawing: 0.39 / 0.45)
    "sofa_back_t_top": 0.21,      # back block thickness at its top: near upright (v22 at 0.115 leaned back ~15 deg; the drawing's ~0.11 line is the crown of a rounded top)
    "sofa_back_crown": 0.03,      # the top of the back bows up this much in the middle (drawing: ~0.03)
    "sofa_foot_h": 0.04, "sofa_foot_d": 0.07, "sofa_foot_inset": 0.065,   # Swyft drawing: 7 x 4 cm pucks, 3 cm in
    "sofa_r": 0.055,              # edge roll of the blocks: under this even light the roll band is what reads as a cushion (advisor after v24)
    "sofa_flange": 0.008, "sofa_flange_t": 0.004,       # self-fabric flange on every seam
    "sofa_ear": 0.012,            # flange runs carry past the corners into small ears
    "sofa_flange_lift": 1.0,      # flange colour x the fabric colour
    "sofa_gap": 0.003,            # half the gap between modules
    "sofa_puff_side": 0.022, "sofa_puff_front": 0.03,   # seat fronts bulge so the gaps between seats open into a V (v23 review)
    "sofa_puff_back": 0.035, "sofa_puff_shape": 2.0,  # pillow, not plateau (advisor, v21)
    "sofa_puff_ottoman": 0.025,   # the ottoman sides bow out (drawing: 1.8-3.5 cm)
    "sofa_sag": 0.01, "sofa_sag_at": 0.30,      # sat in: dip depth, and how far behind the seat front
    "sofa_roll": 0.035, "sofa_back_roll": 0.04, "sofa_tuck": 0.04,  # seat tops overhang their fronts, which lean under (advisor after v21)
    "sofa_wobble": 0.008, "sofa_wobble_len": 0.35,   # low-frequency deformation so the seams bow
    "sofa_back_wobble": 0.3,      # x the wobble on the back blocks (v24: full wobble dented their tops)
    "sofa_ripple": 0.003, "sofa_ripple_len": 0.07,      # vertical compression folds low on the back fronts (photo 2; v24 review)
    "sofa_mesh_step": 0.03,
    "sofa_ottoman_xy": (-3.03, -1.33), "sofa_ottoman_w": 0.70,   # in front of the window-end seat: corners fitted in photos 1, 2 (11 px rms)
    "sofa_colour": (0.425, 0.432, 0.455, 1.0), # linear; midway between v22 and v23: photo 1 wants warmer, photo 2 cooler (trade-off, a designer control)
    "sofa_tex_dir": EXP["root"].parents[1] / "library/textures/fabric/rough_linen",
    "sofa_tex_size": 0.40, "sofa_tex_contrast": 0.0,   # rough_linen (270.7 mm tile) at 1.5x; its tone off from v23 (the Pumice weave replaces it)
    "sofa_slub": 0.45, "sofa_slub_len": 0.02, "sofa_slub_w": 0.0045, "sofa_fleck": 0.1,   # short, at least a pixel wide (v20-v22: 3 cm streaks read as brushed felt)
    "sofa_weave_img": EXP["root"] / "assets/mat/pumice_weave.png",   # high-passed seamless patch of Swyft's Pumice close-up
    "sofa_weave": 2.0, "sofa_weave_tile": 0.11,       # its weave period is ~5 px: 512 px = ~11 cm at a ~1.1 mm thread
    "sofa_weave_relief": 0.3, "sofa_rough": 0.85, "sofa_sheen": 0.5, "sofa_sheen_rough": 0.7,
    "sofa_puckers": 0.4, "sofa_pucker_w": 0.05,
    "feet_colour": (0.05, 0.03, 0.02, 1.0),     # dark stained beech
}

HOW_TO_TWEAK = """\
apartment-model — how to tweak

Flat 233, Manhattan Building. The shell is built from measured values (LiDAR scan plane fits,
the 1:60 plan, and a joint fit against the user's photos). Units are metres; the scene frame is
the scan: x runs from the window wall (x = -4.40) into the flat, y runs west (-) to east (+),
z is up from the living-room floor. The windows face 142 deg (SE).

Collections
- Shell: floor, roof, walls, brick window wall with splayed reveals, piers, beams, cove, pilasters.
- Windows: the factory windows (closed; secondary glazing is not modelled), curtain tracks.
- Mezzanine: mezzanine front, internal steel windows, soffit, column, under-mezzanine walls, bookcase.
- Kitchen: counter runs, island, open shelves (blocks).
- Flat: grey boxes for rooms the scan did not reach (shower room, stores, hallway, upper floor).
  The stair is a placeholder; it is 10 steps in two flights (to be modelled from photos).
- Furniture: rough grey blocks from the scan, for occlusion only.
- Cameras: Cam_<n> matches the user's photo <n>.jpeg (set one active and compare).
- Outside: ground and the building opposite; Portals help the sky light through the windows.

Materials: each is one group node. Select an object, open the Shader Editor, change the inputs:
Paint, Oak (shelves), Steel_White, Steel_Black, Units, Worktop, Bookcase, Grey (Colour, Roughness);
Brick (Brick, Brick Dark, Brick Pale, Mortar, Variation, Dust, Relief, Roughness): a scanned brick wall
(library/textures/brick/factory_brick) at true scale; its faces take Brick (darker toward Brick Dark, paler
toward Brick Pale by the scan's own tone x Variation), its joints take Mortar. Dust = soot and grey bloom over
the wall, Relief = joint and pitting depth.
Oak_Floor (Tint, Brightness, Saturation, Grain, Variation, Seams, Roughness, Anisotropy): 600 x 120
herringbone, spine along the room, each plank cut from a scanned rustic oak (library/textures/wood/
oak_wood_planks). Grain = figure contrast, Variation = plank-to-plank tone, Anisotropy = how far window
reflections streak along each plank. Plank size and pattern position are in P (plank_w, plank_ratio, plank_y0).
Glass (IOR).
White balance: Color Management > White Balance (13000 K warms the image like the phone photos).
Daylight: World > Sky node (Strength, Sky Colour, Ground Colour, Camera View = how bright the
sky looks through the glass). Exposure: Render > Film > Exposure, or the Post node.
Post: Compositing tab, the "Post" node (Exposure); it previews the saved render. After a new
render (F12), set "Source" to Off to use it.

Built by experiments/apartment-model/scripts/build.py (every dimension is a value in P there).
Changes made here are lost on rebuild; copy good values back into P (/sync-tweaks).
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
    M["brick"] = material_from_group("Brick", mat_kit.brick_group(P))
    M["floor"] = material_from_group("Oak_Floor", mat_kit.herringbone_group(P))
    M["glass"] = material_from_group("Glass", glass_group())
    M["sofa"] = material_from_group("Sofa_Fabric", mat_kit.fabric_group(P))
    # the flanges: the same fabric, a touch paler (photos 1-3: the lip reads as a pale line where it catches light)
    M["sofa_flange"] = material_from_group("Sofa_Flange", M["sofa"].node_tree.nodes[0].node_tree)
    fg = next(n for n in M["sofa_flange"].node_tree.nodes if n.type == "GROUP")
    fg.inputs["Colour"].default_value = tuple(min(1.0, c * P["sofa_flange_lift"]) for c in P["sofa_colour"][:3]) + (1.0,)
    M["feet"] = material_from_group("Sofa_Feet", simple_group("Sofa_Feet", P["feet_colour"], 0.5))
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
    K.box("Floor", wx - P["win_t"], ext, W - st, E + st, -P["slab_t"], 0, M["floor"])
    K.box("Roof", wx - P["win_t"], ext, W - st, E + st, C, C + P["slab_t"], M["paint"])
    # party walls (west, east) and the back wall
    K.box("Wall_W", wx, ext, W - st, W, 0, C, M["paint"])
    K.box("Wall_E", wx, ext, E, E + st, 0, C, M["paint"])
    K.box("Wall_Back", back, ext, W, E, 0, C, M["paint"])
    # brick returns: a thin brick skin on the side walls next to the window wall
    cb = P["corner_brick_w"]
    K.box("Brick_Return_W", wx, wx + cb, W, W + 0.004, 0, C, M["brick"])
    K.box("Brick_Return_E", wx, wx + cb, E - 0.004, E, 0, C, M["brick"])

    # window wall: brick, two segmental-arched openings with splayed reveals (wide at the room face)
    fx = P["frame_x"]
    pier_c = sum(P["win_cy"]) / len(P["win_cy"])
    room = [K.arch_loop(cy + math.copysign(P["reveal_shift"], pier_c - cy), P["win_w"] / 2, P["win_sill"], P["win_spring"],
                        P["win_rise"]) for cy in P["win_cy"]]
    glaz = [K.arch_loop(cy, P["win_w_frame"] / 2, P["win_sill"], P["win_spring"], win_rise_frame()) for cy in P["win_cy"]]
    K.wall("Window_Wall_Outer", K.rect(W - st, 0, E + st, C), glaz, wx - P["win_t"], fx, "x", M["brick"])
    K.wall("Window_Wall_Inner", K.rect(W - st, 0, E + st, C), room, fx, wx, "x", M["brick"])
    for i in range(len(room)):
        K.loft_ring(f"Reveal_{i}", glaz[i], room[i], fx, wx, "x", M["brick"])
    # brick piers proud of the wall, with a sloped cap
    for i, (y0, y1) in enumerate(P["piers"]):
        x1 = wx + P["pier_proud"]
        K.box(f"Pier_{i}", wx, x1, y0, y1, 0, P["pier_top"] - P["pier_cap"], M["brick"])
        K.prism(f"Pier_Cap_{i}", [(wx, P["pier_top"] - P["pier_cap"]), (x1, P["pier_top"] - P["pier_cap"]),
                                  (wx, P["pier_top"])], y0, y1, "y", M["brick"])
    # window sills (brick, flat) are the bottom of the opening; add a timber/stone board
    for i, cy in enumerate(P["win_cy"]):
        hw = P["win_w_frame"] / 2
        K.box(f"Sill_{i}", P["frame_x"], wx + 0.02, cy - hw, cy + hw, P["win_sill"] - 0.04, P["win_sill"] + 0.002, M["paint"])

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
        # cove: the wall leans in from cove_z and meets the ceiling cove_in inside the wall plane
        z0, d = P["cove_z"], P["cove_in"][k]
        prof = [(y, z0)] + [(y + s * d * (1 - math.cos(t)), z0 + (C - z0) * math.sin(t))
                            for t in [math.pi / 2 * i / 8 for i in range(1, 9)]] + [(y, C)]
        K.prism(f"Cove_{side}", prof if s > 0 else prof[::-1], wx, px0, "x", M["paint"])
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


def win_rise_frame():
    """Rise of the glazing-plane arch: same crown as the room-face arch, same spring."""
    return P["win_rise"]


def build_window(M, i, cy):
    """Steel factory window in the opening: outer frame on the arch, 4 columns, two transoms, a lower bar."""
    hw, sill, spring, rise = P["win_w_frame"] / 2, P["win_sill"], P["win_spring"], win_rise_frame()
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
    K.box("Column", mx - P["col_d"] / 2 + 0.02, mx + P["col_d"] / 2 + 0.02, P["col_y"] - P["col_w"] / 2,
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
    K.wall("Dining_Back", K.rect(sy - t + 0.01, 0, E, sz), [K.rect(d0, 0, d1, P["door_h"] - 0.0)], dx, dx + t, "x", M["paint"], "Mezzanine")
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
    # dining bookcase: cupboard base, three open bays with scalloped (wavy) sides and heads, shelves
    b0, b1, c0, c1 = P["bookcase"]
    base = P["bookcase_base"]
    bm = M["bookcase"]
    parts = [K.box("BC_Base", b0 - 0.02, b1, c0, c1, 0, base, bm, "Mezzanine"),
             K.box("BC_Back", b1 - 0.03, b1, c0, c1, base, sz, bm, "Mezzanine")]
    nb, fw = 3, 0.07                                     # bays, face-frame stile width
    bw = (c1 - c0 - (nb + 1) * fw) / nb
    holes = []
    for k in range(nb):
        u0 = c0 + fw + k * (bw + fw); u1 = u0 + bw
        z0, z1 = base + 0.04, sz - 0.08
        amp, pitch = 0.025, 0.16
        nz = max(int((z1 - z0) / pitch * 8), 8)
        right = [(u1 - amp * (0.5 - 0.5 * math.cos(2 * math.pi * (z0 + (z1 - z0) * i / nz - z0) / pitch)), z0 + (z1 - z0) * i / nz)
                 for i in range(nz + 1)]
        nu = max(int((u1 - u0) / pitch * 8), 8)
        top = [(u1 - (u1 - u0) * i / nu, z1 - amp * (0.5 - 0.5 * math.cos(2 * math.pi * (u1 - u0) * i / nu / pitch)))
               for i in range(1, nu)]
        left = [(u0 + amp * (0.5 - 0.5 * math.cos(2 * math.pi * (z1 - (z1 - z0) * i / nz - z0) / pitch)), z1 - (z1 - z0) * i / nz)
                for i in range(nz + 1)]
        holes.append([(u0, z0)] + right[:0] + [(u1, z0)] + right[1:] + top + left[:-1])
        for zs in (base + 0.38, base + 0.72):
            parts.append(K.box(f"BC_Shelf_{k}_{zs:.2f}", b0 + 0.02, b1 - 0.03, u0, u1, zs, zs + 0.025, bm, "Mezzanine"))
    parts.append(K.wall("BC_Face", K.rect(c0, base, c1, sz), holes, b0 - 0.02, b0 + 0.02, "x", bm, "Mezzanine"))
    K.join(parts, "Bookcase")


def build_flat(M):
    """The rooms the scan did not reach: grey boxes from the plan."""
    g, sz, mz, C = M["grey"], P["soffit_z"], P["mezz_floor_z"], P["upper_ceil_z"]
    t = 0.12
    # second floor: shower room, stores, hallway, stair
    K.box("Shower_Wall_E", PX(773), PX(980), PY(615), PY(630), 0, sz, g, "Flat")
    K.box("Store_Wall_S", PX(925), PX(937), P["west_y"], PY(615), 0, sz, g, "Flat")
    K.box("Store2_Walls", PX(773), PX(838), PY(697), PY(710), 0, sz, g, "Flat")
    K.box("Hall_Wall_N", PX(825), PX(838), max(PY(770), P["door_y"][1]), P["east_y"], 0, sz, g, "Flat")
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
        ("Coffee_Table", -2.40, -1.10, -1.45, -0.95, 0.48), ("Rug", -4.0, -0.6, -1.90, -0.20, 0.03),
        ("Chair_1", -0.75, 0.15, -1.45, -0.45, 0.50), ("Chair_1_Back", -0.10, 0.15, -1.45, -0.65, 0.81),
        ("Chair_2", -0.75, 0.05, -0.20, 0.55, 0.50), ("Chair_2_Back", -0.20, 0.05, -0.15, 0.50, 0.83),
        ("Footstool", -1.30, -0.80, -0.15, 0.45, 0.46), ("Desk", -1.90, -0.15, 2.25, 2.70, 0.90),
        ("Stool", -3.75, -3.20, 1.25, 1.80, 0.47), ("Speaker_Unit", -3.70, -3.40, 1.85, 2.50, 0.59),
        ("Bookshelf", -0.95, 0.30, -2.85, -2.45, 1.80), ("Media_Unit", 0.60, 1.20, 2.10, 2.70, 0.40),
        ("Trolley", 0.70, 1.20, -1.30, -0.05, 0.80), ("Dining_Table", 1.9, 3.3, 1.35, 2.25, 0.75),
    ):
        K.box(name, x0, x1, y0, y1, 0.0 if name != "Rug" else 0.0, z1, g, "Furniture")
    if P["sofa"]:            # replaces the scan's Sofa_* blocks and the Pouf (the ottoman, moved in the photos)
        sofa.build(P, M["sofa"], M["feet"], K.coll("Furniture"), M["sofa_flange"])


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
        f = d.get("joint") or d.get("refined") or d.get("fit")
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
    ap.add_argument("--finish", action="store_true")
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
    K.COLL.clear()                        # collections from an earlier build in this session are gone
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
            out = EXP["renders"] / f"{args.out}_{v}.png"
            scene.render.filepath = str(out.with_name(f"{args.out}_{v}_2x.png") if args.finish else out)
            bpy.ops.render.render(write_still=True)
            if args.finish:                    # the phone's processing: a sharpened JPEG at the photo's size
                import subprocess
                subprocess.run(["python3", str(HERE.parents[2] / "tools/photo_finish.py"), scene.render.filepath, str(out),
                                str(P["res_x"]), str(P["res_y"]), *[str(x) for x in P["finish"]]], check=True)
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
        # studio-shaded pass: folds inside one object (a girder's front arris) change shade
        sh.light, sh.color_type = "STUDIO", "SINGLE"
        sh.single_color = (0.8, 0.8, 0.8)
        for v in views:
            scene.camera = cams[v]
            scene.render.filepath = str(EXP["renders"] / f"{args.out}_{v}_shade.png")
            bpy.ops.render.render(write_still=True)
        scene.render.engine = "CYCLES"
        scene.view_settings.view_transform = P["view"]
        for o in hidden:
            o.hide_render = False
    if args.save:
        scene.camera = cams[views[-1]]
        if not args.norender:
            use_saved_render(scene, raw, EXP["output"])   # Compositing tab previews the final raw EXR
        blend = EXP["output"] / f"{EXP['name']}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        blend.with_suffix(".blend1").unlink(missing_ok=True)
    print("BUILD OK")
