"""opal-essence: a milky opalescent resin plate over dark hardware, lit from behind by a
gradient. Build the whole scene from nothing, render, save.

Run from the repo root:
  tools/blender.sh experiments/opal-essence/scripts/build.py --out v01 --samples 256 --scale 0.5
  ... --set key=value      override any value in P
  ... --save               also save output/opal-essence.blend

Layout: the plate lies flat in XY, face up (+Z). The camera looks down from above, like a
flat-lay product shot. Hardware sits under the plate at several depths, so near parts read
sharp and far parts blur through the frosted resin. A gradient emission plane at the bottom
is the "gel backlight"; the camera cannot see it directly, only through the resin.
"""
import argparse
import ast
import math
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Euler, Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from common import LIBRARY, enable_gpu, experiment_paths  # noqa: E402
from nodes import auto_layout, group, how_to_tweak, material_from_group, math as m_  # noqa: E402
from comp import compositor, post_group, use_saved_render  # noqa: E402

EXP = experiment_paths(__file__)


def srgb(hexstr, a=1.0):
    """'#rrggbb' → linear RGBA."""
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    h = hexstr.lstrip("#")
    return tuple(lin(int(h[i:i + 2], 16)) for i in (0, 2, 4)) + (a,)


# Every value a designer might tune lives here. Override with --set key=value.
P = {
    "res_x": 1600,
    "res_y": 2000,
    # Camera
    "lens": 100.0,
    "cam_dist": 1.62,
    "cam_tilt": 14.0,           # degrees off straight-down, for a little parallax
    "fstop": 5.6,
    # Plate (metres)
    "plate_w": 0.40,
    "plate_h": 0.50,
    "plate_t": 0.014,
    "edge_round": 0.0045,
    # Opal resin look
    "milk": 0.60,               # 0 clear → 1 opaque milk
    "opal_blue": 0.35,          # how much more blue scatters than red (opalescence)
    "frost": 0.50,              # blur of what is behind (transmission roughness)
    "gloss": 0.92,              # wet top coat, 1 = mirror
    "warm": (1.0, 1.0, 1.0, 1.0),   # tint of light through thick resin; white = none
    "density": 260.0,
    "absorb": 0.05,             # how strongly Warm tints, as a fraction of the scatter density
    "wave": 0.25,               # slow undulation in the wet coat (highlights only)
    "wave_scale": 6.0,
    "wave_stretch": 0.35,        # <1 stretches the ripples along the plate's height           # scatter per metre at milk 1
    # Gradient backlight (the colour stops)
    "stops": [
        (0.00, srgb("#0b5a66")),   # deep teal: lights the milk from behind on the left too
        (0.38, srgb("#2f9a90")),   # teal, wrapping the parts cluster
        (0.60, srgb("#f0d6a8")),   # cream
        (0.84, srgb("#ffa321")),   # orange (late, so a wide cream band clears the parts)
        (1.00, srgb("#ff4f7a")),   # hot pink
    ],
    "back_strength": 6.0,
    "back_angle": 0.0,           # degrees; 0 = left → right
    "back_depth": 0.50,
    "softbox_power": 40.0,          # plate → backlight distance (m)
    # Lights
    "key_power": 6.0,
    "key_width": 0.008,
    "key_offsets": [0.0],          # thin + bright: same highlight, less spill into the milk
    "key_x": 0.15,               # strip's mirror highlight lands at ~0.55 × this across the plate           # glossy strip, mirror point, for the long highlight
    "fill_power": 5.0,
    "fill_colour": (0.82, 0.92, 1.0),   # cool: the milk scatters it back as the opal blue skin           # big soft top light, shows the milky front (blue)
    "rake_power": 25.0,
    "env_sheen": 0.35,           # overhead softbox seen only in reflections (coat sheen)
    "env_card_x": 0.05,          # where the card sits in the plate's reflection (-0.14 … 0.14 spans it)
    "env_card_w": 0.35,
    "env_card_soft": 0.12,
    "env_side": 1.5,             # low side card: rims of screws, rivets, type
    "env_colour": (0.85, 0.92, 1.0, 1.0),   # cool, for the blue-white skin in reflections
    "parts_key": 60.0,            # front light on the hardware under the plate (skips the plate)
    "parts_rim": 15.0,           # teal and orange rims on the hardware, from the sides
    # Hardware
    "hw_gloss": 0.75,
    "hw_under_colour": srgb("#0a3a40"),
    "parts_rim_warm": (0.55, 0.85, 1.0),   # was orange: it gave the parts red-brown halos
    # Type (editable Text objects in the .blend)
    "font_mono": "/System/Library/Fonts/SFNSMono.ttf",   # trial fonts lack &, ·, — and /
    "type_top": "WONDER MATERIALS & OPTICS",
    "type_spec": "OPAL ESSENCE\nSPECIMEN 01 / RESIN, OPALESCENT\n14 MM CAST — LOT 0927-26",
    "type_small": "DO NOT POLISH · HANDLE AT EDGES",
    "type_height": 0.00035,      # relief of the raised type (m)
    "warp": 0.0,                 # plate undulation amplitude (m); 0 = flat, as cast sheet
    "warp_voxel": 0.0008,        # remesh voxel size for the warped plate (m)
    # Post
    "glow": 0.25,
    "glow_size": 0.5,
    "glow_threshold": 1.2,
    "chroma": 0.003,
    "saturation": 1.0,
    "grain": 0.06,
    "view": "Khronos PBR Neutral",   # keeps the saturated orange/pink; AgX turns them peach
    "look": "None",
}

HOW_TO_TWEAK = """\
opal-essence — how to tweak

Each material is one node. Select the object, open the Shader Editor, and change
the inputs on its group node. Hover an input for its range.

GRADIENT (the colour stops)
- Select "Backlight" in the Outliner (it sits under the plate, hidden from the camera).
  Its node has Stop 1–5 Colour and Position. Positions run 0 (plate's left edge) → 1 (right).
  Keep them in order. Angle turns the gradient (degrees). Strength = how bright it glows
  through the resin (6 is the reviewed exposure; above ~8 the orange and pink clip).

RESIN — "Opal Resin" node (Plate, Strip)
- Milk: 0 clear → 1 dense milk.     Frost: blur of the parts behind (0.5 = milky diffuser).
- Opal Blue: blue scatter / warm transmission (real opalescence). Above ~0.5 it pulls the
  gradient warm: teal goes olive, parts go brown.
- Gloss: the wet top coat.  Wave: slow ripple in that coat.
- Warm: tint of light passing through thick resin. White = none; cream/amber = warmer core.
- Raised type and wet blobs use "Opal Resin Type": the same node with Frost 0, so they read
  as clear moulded relief. Change it there too if you change the look.

HARDWARE
- "Anodised" (clamps), "Anodised Teal" (parts under the plate), "Metal" (screws),
  "Pearl" (rivets): Colour and Gloss.

TYPE — live Text objects
- "Type Top", "Type Spec", "Type Small": Tab in the viewport to edit the words.
  Font: Object Data > Font (SF Mono; trial fonts lack & · — /). "Logotype Raised" is the
  Wonder mesh from library/.

LIGHTS
- Key 1: thin strip, reflection-only, reaches rivets and the top strip only (light linking).
- Fill: cool, from below the camera — lifts the milk. Above ~8 W it greys the plate.
- Rake: low from the camera side — the glints on the raised type.
- Softbox: reflection-only accents on the type and hardware.
- Parts Key / Parts Rim Cool / Parts Rim Warm: light only the parts under the plate and
  pass through it (shadow linking), so the parts show form.
- World: black, except two soft cards seen only in reflections (chrome, coat).

POST — Compositing tab
- The backdrop shows the saved render. The "Post" node's inputs update it at once:
  Glow, Glow Size, Glow Threshold, Chroma (edge fringing), Saturation, Grain.
- After a new render (F12), set "Source" to Off to use it.

REBUILD
- experiments/opal-essence/scripts/build.py. Changes made here are lost on rebuild; copy
  good values back into P, or use --set key=value.
- Experimental: --set warp=0.0015 remeshes the plate and adds a 1.5 mm undulation (type and
  hardware ride it). Off in the final: with nothing bright to mirror it adds little yet.
"""


# --- Materials: one node each ---------------------------------------------------------------

def mix_rgb(ng, fac, a, b):
    mx = ng.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    mx.clamp_factor = True
    for sock, v in ((mx.inputs[0], fac), (mx.inputs[6], a), (mx.inputs[7], b)):
        if hasattr(v, "bl_rna"):
            ng.links.new(v, sock)
        else:
            sock.default_value = v
    return mx.outputs[2]


def opal_group():
    """Milky opalescent resin: frosted transmission under a wet coat, with a volume inside that
    scatters blue more than red (Rayleigh-like), so the skin looks blue and thick paths glow warm."""
    ng, gi, go = group("Opal Resin", [
        ("Milk", "NodeSocketFloat", P["milk"], 0.0, 1.0),
        ("Opal Blue", "NodeSocketFloat", P["opal_blue"], 0.0, 1.0),
        ("Frost", "NodeSocketFloat", P["frost"], 0.0, 1.0),
        ("Gloss", "NodeSocketFloat", P["gloss"], 0.0, 1.0),
        ("Warm", "NodeSocketColor", P["warm"], None, None),
        ("Wave", "NodeSocketFloat", P["wave"], 0.0, 1.0),
    ], [("Shader", "NodeSocketShader"), ("Volume", "NodeSocketShader")])
    L = ng.links.new
    bsdf = ng.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (1, 1, 1, 1)
    bsdf.inputs["Transmission Weight"].default_value = 1.0
    bsdf.inputs["IOR"].default_value = 1.49
    # The frosted base must not reflect: at its roughness every light smears across the whole
    # plate as a milky veil. All reflection comes from the sharp coat above it.
    bsdf.inputs["Specular IOR Level"].default_value = 0.0
    bsdf.inputs["Coat Weight"].default_value = 1.0
    bsdf.inputs["Coat IOR"].default_value = 1.49
    L(m_(ng, "MULTIPLY", gi.outputs["Frost"], 0.6), bsdf.inputs["Roughness"])
    L(m_(ng, "MULTIPLY", m_(ng, "SUBTRACT", 1.0, gi.outputs["Gloss"]), 0.25), bsdf.inputs["Coat Roughness"])
    # A slow wave in the coat only: breaks the highlights up like cast resin, keeps the
    # transmission clean.
    wn = ng.nodes.new("ShaderNodeTexNoise")
    wn.inputs["Scale"].default_value = P["wave_scale"]
    wn.inputs["Detail"].default_value = 1.0
    wn.inputs["Roughness"].default_value = 0.4
    tco = ng.nodes.new("ShaderNodeTexCoord")
    stretch = ng.nodes.new("ShaderNodeVectorMath")        # long flowing highlights, not blobs
    stretch.operation = "MULTIPLY"
    stretch.inputs[1].default_value = (1.0, P["wave_stretch"], 1.0)
    L(tco.outputs["Object"], stretch.inputs[0])
    L(stretch.outputs[0], wn.inputs["Vector"])
    bump = ng.nodes.new("ShaderNodeBump")
    L(gi.outputs["Wave"], bump.inputs["Strength"])
    bump.inputs["Distance"].default_value = 0.002
    L(wn.outputs["Fac"], bump.inputs["Height"])
    L(bump.outputs[0], bsdf.inputs["Coat Normal"])
    L(bsdf.outputs[0], go.inputs["Shader"])

    # Scatter per channel, Rayleigh ratio R:G:B = 1:2.3:5.7 at Opal Blue 1. Times Milk·Density.
    dens = m_(ng, "MULTIPLY", gi.outputs["Milk"], P["density"])
    ob = gi.outputs["Opal Blue"]
    r = m_(ng, "MULTIPLY", m_(ng, "SUBTRACT", 1.0, m_(ng, "MULTIPLY", ob, 0.83)), dens)
    g = m_(ng, "MULTIPLY", m_(ng, "SUBTRACT", 1.0, m_(ng, "MULTIPLY", ob, 0.6)), dens)
    comb = ng.nodes.new("ShaderNodeCombineXYZ")
    L(r, comb.inputs[0]); L(g, comb.inputs[1]); L(dens, comb.inputs[2])
    # Absorption: a little, of the complement of Warm, so long paths turn warm.
    inv = ng.nodes.new("ShaderNodeInvert")
    L(gi.outputs["Warm"], inv.inputs["Color"])
    absorb = ng.nodes.new("ShaderNodeVectorMath")
    absorb.operation = "SCALE"
    L(inv.outputs[0], absorb.inputs[0])
    L(m_(ng, "MULTIPLY", dens, P["absorb"]), absorb.inputs["Scale"])
    vol = ng.nodes.new("ShaderNodeVolumeCoefficients")
    L(comb.outputs[0], vol.inputs["Scatter Coefficients"])
    L(absorb.outputs[0], vol.inputs["Absorption Coefficients"])
    vol.inputs["Anisotropy"].default_value = 0.35
    L(vol.outputs[0], go.inputs["Volume"])
    auto_layout(ng)
    return ng


def backlight_group():
    """Five editable colour stops along a direction across the plate, as emission."""
    ins = []
    for i, (pos, col) in enumerate(P["stops"], 1):
        ins.append((f"Stop {i} Colour", "NodeSocketColor", col, None, None))
        ins.append((f"Stop {i} Position", "NodeSocketFloat", pos, 0.0, 1.0))
    ins += [("Strength", "NodeSocketFloat", P["back_strength"], 0.0, 40.0),
            ("Angle", "NodeSocketFloat", P["back_angle"], -180.0, 180.0)]
    ng, gi, go = group("Backlight", ins, [("Shader", "NodeSocketShader")])
    L = ng.links.new
    # u: 0 at the plate's left edge, 1 at its right, rotated by Angle about the centre.
    tc = ng.nodes.new("ShaderNodeTexCoord")
    sep = ng.nodes.new("ShaderNodeSeparateXYZ")
    L(tc.outputs["Object"], sep.inputs[0])
    a = m_(ng, "RADIANS", gi.outputs["Angle"])
    proj = m_(ng, "ADD", m_(ng, "MULTIPLY", sep.outputs[0], m_(ng, "COSINE", a)),
              m_(ng, "MULTIPLY", sep.outputs[1], m_(ng, "SINE", a)))
    u = m_(ng, "ADD", m_(ng, "DIVIDE", proj, P["plate_w"]), 0.5)
    col = gi.outputs["Stop 1 Colour"]
    for i in range(2, len(P["stops"]) + 1):
        p0, p1 = gi.outputs[f"Stop {i-1} Position"], gi.outputs[f"Stop {i} Position"]
        span = m_(ng, "MAXIMUM", m_(ng, "SUBTRACT", p1, p0), 1e-4)
        f = m_(ng, "DIVIDE", m_(ng, "SUBTRACT", u, p0), span, clamp=True)
        col = mix_rgb(ng, f, col, gi.outputs[f"Stop {i} Colour"])
    em = ng.nodes.new("ShaderNodeEmission")
    L(col, em.inputs["Color"])
    L(gi.outputs["Strength"], em.inputs["Strength"])
    L(em.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def plastic_group(name, colour, gloss, metallic=0.0):
    ng, gi, go = group(name, [
        ("Colour", "NodeSocketColor", colour, None, None),
        ("Gloss", "NodeSocketFloat", gloss, 0.0, 1.0),
    ], [("Shader", "NodeSocketShader")])
    bsdf = ng.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Metallic"].default_value = metallic
    ng.links.new(gi.outputs["Colour"], bsdf.inputs["Base Color"])
    ng.links.new(m_(ng, "SUBTRACT", 1.0, gi.outputs["Gloss"]), bsdf.inputs["Roughness"])
    ng.links.new(bsdf.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def opal_material(ng):
    mat = material_from_group("Opal Resin", ng)
    g = mat.node_tree.nodes["Group"]
    out = mat.node_tree.nodes["Material Output"]
    mat.node_tree.links.new(g.outputs["Volume"], out.inputs["Volume"])
    return mat


# --- Geometry --------------------------------------------------------------------------------

def outline_points(w, h, r=0.02, n_arc=10):
    """Rounded rectangle with two soft bites out of the left edge, counter-clockwise."""
    pts = []

    def arc(cx, cy, rad, a0, a1, n):
        for k in range(n + 1):
            t = math.radians(a0 + (a1 - a0) * k / n)
            pts.append((cx + rad * math.cos(t), cy + rad * math.sin(t)))

    x0, x1, y0, y1 = -w / 2, w / 2, -h / 2, h / 2
    arc(x1 - r, y0 + r, r, -90, 0, n_arc)           # bottom right
    arc(x1 - r, y1 - r, r, 0, 90, n_arc)            # top right
    arc(x0 + r, y1 - r, r, 90, 180, n_arc)          # top left
    # left edge, top → bottom, with two concave bites (arcs curving into the plate)
    for cy, rad in ((0.10, 0.045), (-0.07, 0.06)):
        pts.append((x0, cy + rad * 1.05))
        arc(x0, cy, rad, 90, -90, 2 * n_arc)
        pts[-1] = (x0 + 1e-4, pts[-1][1])
        pts.append((x0, cy - rad * 1.05))
    arc(x0 + r, y0 + r, r, 180, 270, n_arc)         # bottom left
    return pts


def slab(name, pts, thickness, round_r, z, mat):
    """A flat 2D curve outline, filled, extruded and rounded; kept as a curve (clean caps)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    cu.extrude = max(thickness / 2 - round_r, 0.0)
    cu.bevel_depth = round_r
    cu.bevel_resolution = 6
    cu.resolution_u = 12
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for p, (x, y) in zip(sp.points, pts):
        p.co = (x, y, 0, 1)
    sp.use_cyclic_u = True
    ob = bpy.data.objects.new(name, cu)
    ob.location.z = z
    bpy.context.scene.collection.objects.link(ob)
    cu.materials.append(mat)
    return ob


def rounded_rect(w, h, r, n=8):
    pts = []
    for cx, cy, a0 in ((w / 2 - r, -h / 2 + r, -90), (w / 2 - r, h / 2 - r, 0),
                       (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180)):
        for k in range(n + 1):
            t = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return pts


def box(name, size, loc, mat, bevel=0.0015, rot_z=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=(0, 0, math.radians(rot_z)))
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        bv = ob.modifiers.new("Bevel", "BEVEL")
        bv.width, bv.segments, bv.limit_method = bevel, 3, "ANGLE"
        bv.harden_normals = True
    bpy.ops.object.shade_smooth()
    ob.data.materials.append(mat)
    return ob


def cylinder(name, r, depth, loc, mat, verts=48, bevel=0.001, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    if bevel:
        bv = ob.modifiers.new("Bevel", "BEVEL")
        bv.width, bv.segments, bv.limit_method = bevel, 3, "ANGLE"
        bv.harden_normals = True
    bpy.ops.object.shade_smooth()
    ob.data.materials.append(mat)
    return ob


def gear(name, r, depth, teeth, loc, mat):
    """A plain spur gear: disc plus rectangular teeth, joined."""
    parts = [cylinder(name, r, depth, loc, mat, verts=96, bevel=0)]
    tw = 2 * math.pi * r / teeth * 0.45
    for k in range(teeth):
        a = 2 * math.pi * k / teeth
        parts.append(box(f"{name}_t{k}", (r * 0.14, tw, depth),
                         (loc[0] + math.cos(a) * r * 1.05, loc[1] + math.sin(a) * r * 1.05, loc[2]),
                         mat, bevel=0, rot_z=math.degrees(a)))
    bpy.ops.object.select_all(action="DESELECT")
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    ob = parts[0]
    bv = ob.modifiers.new("Bevel", "BEVEL")
    bv.width, bv.segments, bv.limit_method = 0.0008, 2, "ANGLE"
    bv.harden_normals = True
    hole = cylinder(f"{name}_hub", r * 0.28, depth * 1.3, (loc[0], loc[1], loc[2] - depth * 0.2), mat, bevel=0.0006)
    return ob, hole


def dome(name, r, height, loc, mat):
    """Upper half of a squashed sphere, closed flat underneath, resting on z = loc.z."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=r, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0),
                           plane_no=(0, 0, 1), clear_inner=True)
    edges = [e for e in bm.edges if e.is_boundary]
    bmesh.ops.edgeloop_fill(bm, edges=edges)
    for v in bm.verts:
        v.co.z = v.co.z * height / r + 2e-5
    bm.to_mesh(ob.data)
    bm.free()
    bpy.ops.object.shade_smooth()
    ob.data.materials.append(mat)
    return ob


def load_font(path):
    try:
        return bpy.data.fonts.load(path, check_existing=True)
    except Exception:  # Windows or missing font: Blender's built-in
        print(f"[out] font not found, using built-in: {path}")
        return None


def raised_text(name, body, size, loc, rot_z, mat, font, align="LEFT", spacing=1.0, line=1.2):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    if font:
        cu.font = font
    cu.align_x = align
    cu.space_character = spacing
    cu.space_line = line
    cu.extrude = P["type_height"] / 2
    cu.bevel_depth = P["type_height"] * 0.35
    cu.bevel_resolution = 2
    cu.offset = -P["type_height"] * 0.3        # keep strokes from fattening with the bevel
    cu.resolution_u = 6
    cu.materials.append(mat)
    ob = bpy.data.objects.new(name, cu)
    # Sit on the surface with a hair gap: overlapping the plate's volume turns the type dark.
    ob.location = (loc[0], loc[1], loc[2] + cu.extrude + cu.bevel_depth + 2e-5)
    ob.rotation_euler.z = math.radians(rot_z)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def add_logo(name, which, width, loc, height, mat):
    """Library Wonder mesh, scaled to `width`, flattened to `height` of relief."""
    with bpy.data.libraries.load(str(LIBRARY / "models/wonder-logos/wonder_logos.blend")) as (_, dst):
        dst.objects = [f"wonder_{which}.001"]
    ob = dst.objects[0]
    bpy.context.scene.collection.objects.link(ob)
    ob.name = name
    ob.data = ob.data.copy()
    me = ob.data
    xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]; zs = [v.co.z for v in me.vertices]
    cx, cy, zmin = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)
    s = width / (max(xs) - min(xs))
    sz = height / (max(zs) - zmin)
    for v in me.vertices:
        v.co = Vector(((v.co.x - cx) * s, (v.co.y - cy) * s, (v.co.z - zmin) * sz))
    ob.location, ob.rotation_euler, ob.scale = loc, (0, 0, 0), (1, 1, 1)
    me.materials.clear()
    me.materials.append(mat)
    bv = ob.modifiers.new("Bevel", "BEVEL")
    bv.width, bv.segments, bv.limit_method = min(height * 0.45, width * 0.004), 3, "ANGLE"
    bv.harden_normals = True
    return ob


def area(name, size, loc, target, power, shape="RECTANGLE", size_y=None, spread=180.0,
         transmit=False, glossy=True, diffuse=True, colour=(1, 1, 1)):
    bpy.ops.object.light_add(type="AREA", location=loc)
    ob = bpy.context.active_object
    ob.name = name
    li = ob.data
    li.shape = shape
    li.size = size
    if size_y is not None:
        li.size_y = size_y
    li.energy = power
    li.color = colour
    li.spread = math.radians(spread)
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    ob.visible_transmission = transmit
    ob.visible_glossy = glossy
    ob.visible_diffuse = diffuse
    return ob


# --- Scene ----------------------------------------------------------------------------------

def studio_world(world):
    """Black to everything except reflections: the coat and the chrome see a dark studio with
    two soft-edged softbox cards. Gated by Is Glossy Ray, so no light reaches the milk (a lamp
    there would veil it)."""
    nt = world.node_tree
    L = nt.links.new
    bg = nt.nodes["Background"]
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    neg = nt.nodes.new("ShaderNodeVectorMath")
    neg.operation = "SCALE"
    neg.inputs["Scale"].default_value = -1.0
    L(geo.outputs["Incoming"], neg.inputs[0])   # Incoming points back along the ray; flip it
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    L(neg.outputs[0], sep.inputs[0])
    x, y, z = sep.outputs[0], sep.outputs[1], sep.outputs[2]

    def band(v, lo, hi, soft):
        """1 inside [lo, hi], soft edges `soft` wide."""
        a = m_(nt, "DIVIDE", m_(nt, "SUBTRACT", v, lo - soft), soft, clamp=True)
        b = m_(nt, "DIVIDE", m_(nt, "SUBTRACT", hi + soft, v), soft, clamp=True)
        return m_(nt, "MULTIPLY", a, b)

    # Overhead card, straddling the flat plate's mirror direction, so its soft edge crosses the
    # plate as a gentle sheen that the coat ripple bends.
    over = m_(nt, "MULTIPLY", band(x, P["env_card_x"], P["env_card_x"] + P["env_card_w"], P["env_card_soft"]),
                band(z, 0.75, 1.0, 0.1))
    # A low card on the left for the rims of screws, rivets and type.
    side = m_(nt, "MULTIPLY", band(x, -1.0, -0.6, 0.15), band(z, 0.05, 0.45, 0.1))
    val = m_(nt, "ADD", m_(nt, "MULTIPLY", over, P["env_sheen"]), m_(nt, "MULTIPLY", side, P["env_side"]))
    lp = nt.nodes.new("ShaderNodeLightPath")
    L(m_(nt, "MULTIPLY", val, lp.outputs["Is Glossy Ray"]), bg.inputs["Strength"])
    bg.inputs["Color"].default_value = P["env_colour"]


# --- Warp: one analytic field shared by the plate's geometry nodes and everything on it ----
WAVES = ((0.55, 0.62, 0.0, 0.7), (0.45, 0.0, 0.48, 1.9), (0.3, 0.33, 0.29, 4.2))  # weight, λx, λy, phase


def warp_z(x, y):
    """Height of the warp at (x, y), in metres. Mirrors warp_group()."""
    z = 0.0
    for wgt, lx, ly, ph in WAVES:
        kx = 2 * math.pi / lx if lx else 0.0
        ky = 2 * math.pi / ly if ly else 0.0
        z += wgt * math.sin(kx * x + ky * y + ph)
    return P["warp"] * z


def ride_warp(ob, tilt=True):
    """Move an object on the plate up/down with the warp at its origin, and tilt it to the slope."""
    x, y = ob.matrix_world.translation.x, ob.matrix_world.translation.y
    e = 1e-4
    dzdx = (warp_z(x + e, y) - warp_z(x - e, y)) / (2 * e)
    dzdy = (warp_z(x, y + e) - warp_z(x, y - e)) / (2 * e)
    tilt_m = Euler((math.atan(dzdy), -math.atan(dzdx), 0)).to_matrix().to_4x4() if tilt else Matrix()
    loc = ob.matrix_world.translation.copy()
    loc.z += warp_z(x, y)
    rest = ob.matrix_world.copy()
    rest.translation = (0, 0, 0)
    ob.matrix_world = Matrix.Translation(loc) @ tilt_m @ rest


def warp_group(mat):
    """Geometry nodes: even remesh of the slab (via an SDF grid), then the warp as a Z offset."""
    ng = bpy.data.node_groups.new("Warp Slab", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    n, L = ng.nodes, ng.links.new
    gi, go = n.new("NodeGroupInput"), n.new("NodeGroupOutput")
    sdf = n.new("GeometryNodeMeshToSDFGrid")
    sdf.inputs["Voxel Size"].default_value = P["warp_voxel"]
    g2m = n.new("GeometryNodeGridToMesh")
    g2m.inputs["Threshold"].default_value = 0.0
    L(gi.outputs[0], sdf.inputs["Mesh"])
    L(sdf.outputs[0], g2m.inputs["Grid"])
    pos = n.new("GeometryNodeInputPosition")
    sep = n.new("ShaderNodeSeparateXYZ")
    L(pos.outputs[0], sep.inputs[0])
    total = None
    for wgt, lx, ly, ph in WAVES:
        kx = 2 * math.pi / lx if lx else 0.0
        ky = 2 * math.pi / ly if ly else 0.0
        arg = m_(ng, "ADD", m_(ng, "MULTIPLY", sep.outputs[0], kx), m_(ng, "MULTIPLY", sep.outputs[1], ky))
        term = m_(ng, "MULTIPLY", m_(ng, "SINE", m_(ng, "ADD", arg, ph)), wgt * P["warp"])
        total = term if total is None else m_(ng, "ADD", total, term)
    off = n.new("ShaderNodeCombineXYZ")
    L(total, off.inputs[2])
    setp = n.new("GeometryNodeSetPosition")
    L(g2m.outputs[0], setp.inputs["Geometry"])
    L(off.outputs[0], setp.inputs["Offset"])
    smooth = n.new("GeometryNodeSetShadeSmooth")
    L(setp.outputs[0], smooth.inputs["Geometry"])
    setm = n.new("GeometryNodeSetMaterial")
    setm.inputs["Material"].default_value = mat
    L(smooth.outputs[0], setm.inputs["Geometry"])
    L(setm.outputs[0], go.inputs[0])
    auto_layout(ng)
    return ng


def warp_slab(ob, mat):
    """Curve slab → mesh → Warp Slab modifier. Objects keep their names."""
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.convert(target="MESH")
    mod = ob.modifiers.new("Warp", "NODES")
    mod.node_group = warp_group(mat)


def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    enable_gpu(scene)

    opal_ng = opal_group()
    opal = opal_material(opal_ng)
    # Raised type: the same resin node, surface only. A thin volume just catches front light
    # and turns the type into a flat grey decal.
    # Its own faces are clear (Frost 0): as a separate object a frosted type slab is a second
    # diffuser that greys and re-blurs everything under it.
    type_mat = material_from_group("Opal Resin Type", opal_ng)
    type_mat.node_tree.nodes["Group"].inputs["Frost"].default_value = 0.0
    black = material_from_group("Anodised", plastic_group("Anodised", srgb("#0b0c0e"), P["hw_gloss"]))
    # Parts under the plate: deep teal anodising, so they read navy/teal through the milk, not brown.
    teal_hw = material_from_group("Anodised Teal", plastic_group("Anodised Teal", P["hw_under_colour"], P["hw_gloss"]))
    metal = material_from_group("Metal", plastic_group("Metal", srgb("#c9c3b8"), 0.82, metallic=1.0))
    pearl = material_from_group("Pearl", plastic_group("Pearl", srgb("#f2d7c4"), 0.9, metallic=0.6))
    back_mat = material_from_group("Backlight", backlight_group())

    W, H, T = P["plate_w"], P["plate_h"], P["plate_t"]
    top = T / 2

    # The plate and a thinner folded strip across the top that carries the micro-type.
    plate = slab("Plate", outline_points(W, H), T, P["edge_round"], 0.0, opal)
    strip = slab("Strip", [(x + 0.03, y + H / 2 - 0.035) for x, y in rounded_rect(W * 0.86, 0.05, 0.004)],
                 0.004, 0.0016, top + 0.002 + 2e-5, opal)

    # Hardware under the plate. Depth sets how blurred each part reads.
    under = -T / 2
    x0 = -W / 2
    box("Rail A", (0.30, 0.018, 0.012), (x0 + 0.13, 0.12, under - 0.0068), teal_hw)   # touching: reads sharp
    box("Rail B", (0.26, 0.014, 0.010), (x0 + 0.12, -0.02, under - 0.03), teal_hw)
    box("Rail C", (0.22, 0.020, 0.012), (x0 + 0.10, -0.15, under - 0.0068), teal_hw)  # touching
    box("Column", (0.05, 0.46, 0.02), (x0 + 0.055, 0.0, under - 0.06), teal_hw)
    box("Block A", (0.07, 0.09, 0.03), (x0 + 0.13, 0.19, under - 0.05), teal_hw)
    box("Block B", (0.06, 0.05, 0.04), (x0 + 0.20, -0.09, under - 0.09), teal_hw)
    box("Block C", (0.09, 0.07, 0.03), (x0 + 0.09, -0.21, under - 0.035), teal_hw)
    box("Tab", (0.03, 0.12, 0.006), (x0 + 0.24, 0.05, under - 0.0038), teal_hw)
    gear("Gear A", 0.045, 0.01, 28, (x0 + 0.17, 0.05, under - 0.04), teal_hw)
    gear("Gear B", 0.028, 0.008, 18, (x0 + 0.235, -0.035, under - 0.0048), teal_hw)
    cylinder("Shaft", 0.006, 0.20, (x0 + 0.25, 0.14, under - 0.11), teal_hw, rot=(0, math.radians(90), 0))
    add_logo("Logomark Behind", "logomark", 0.15, (0.07, -0.02, under - 0.16), 0.02, teal_hw)

    # Clamps on the corners and pearl rivets on top, each in a clear wet blob of resin.
    for i, (sx, sy) in enumerate(((-1, 1), (1, 1), (-1, -1), (1, -1))):
        cx, cy = sx * (W / 2 - 0.012), sy * (H / 2 - 0.012)
        box(f"Clamp {i}", (0.036, 0.036, 0.008), (cx, cy, top + 0.004), black, bevel=0.003)
        box(f"Clamp {i} Under", (0.036, 0.036, 0.006), (cx, cy, -T / 2 - 0.003), black, bevel=0.002)
        cylinder(f"Screw {i}", 0.0055, 0.003, (cx, cy, top + 0.0085), metal, bevel=0.0012)
    for i, (x, y) in enumerate(((-0.02, H / 2 - 0.05), (0.12, H / 2 - 0.05), (0.15, 0.02),
                                (0.15, -0.12), (0.07, -H / 2 + 0.035), (0.17, 0.10))):
        z = top + (0.004 if y > H / 2 - 0.07 else 0.0)
        dome(f"Rivet {i}", 0.0042, 0.0028, (x, y, z), pearl)
        dome(f"Rivet {i} Wet", 0.0085, 0.0013, (x, y, z), type_mat)   # clear wet blob

    # Raised type, all live Text objects in the resin material.
    font = load_font(P["font_mono"])
    raised_text("Type Top", P["type_top"], 0.017, (x0 + 0.075, H / 2 - 0.041, top + 0.004 + 2e-5),
                0, type_mat, font, spacing=1.15)
    raised_text("Type Spec", P["type_spec"], 0.0095, (-0.03, -H / 2 + 0.10, top),
                0, type_mat, font, spacing=1.1)
    raised_text("Type Small", P["type_small"], 0.0075, (W / 2 - 0.028, -0.05, top),
                90, type_mat, font, spacing=1.3)
    add_logo("Logotype Raised", "logotype", 0.15, (-0.055, -H / 2 + 0.04, top + 2e-5),
             P["type_height"] * 1.3, type_mat)

    # A big softbox off to the upper left, seen only in reflections. It sits outside the flat
    # plate's mirror angle, so only curved things (type bevels, rivets, edges) pick it up.
    soft = area("Softbox", 0.9, (-1.1, 0.7, 0.9), (0, 0, 0), P["softbox_power"], size_y=0.6,
                diffuse=False, glossy=True)
    soft.visible_volume_scatter = False

    # Gradient backlight: the gel wall behind the plate. Seen only through the resin.
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, -P["back_depth"]))
    back = bpy.context.active_object
    back.name = "Backlight"
    back.scale = (W * 1.6, H * 1.4, 1)
    bpy.ops.object.transform_apply(scale=True)   # object coords in metres, so stops map across the plate
    back.data.materials.append(back_mat)
    back.visible_camera = False
    back.visible_glossy = False

    # Lights: long glossy strip at the mirror point, big soft fill, low rake for the type.
    # A bank of thin strips: each draws one long highlight that the coat ripple bends.
    for i, dx in enumerate(P["key_offsets"]):
        key = area(f"Key {i + 1}", P["key_width"], (P["key_x"] + dx, 0.0, 1.3), (P["key_x"] + dx, 0.0, 0),
                   P["key_power"], size_y=1.2, diffuse=False)
        key.rotation_euler = (0, 0, 0)
        key.visible_volume_scatter = False
    # Fill sits below the camera, outside the flat plate's mirror angle, so the coat never shows
    # its edge; it only lights the milk.
    area("Fill", 0.8, (-0.1, -0.95, 1.2), (0, 0, 0), P["fill_power"], colour=P["fill_colour"])
    # Front light scatters in the milk and veils everything, so these three are reflection-only.
    # The body gets its light from the backlight, plus a little Fill for the blue opal skin.
    # Low from the camera side: a bevel tilted toward the camera mirrors a light ~14° above
    # the plate on that side, so this is what draws the edge glints on the raised type.
    rake = area("Rake", 0.7, (0.0, -0.9, 0.22), (0, 0, 0), P["rake_power"], size_y=0.12, spread=40,
                diffuse=False)
    rake.visible_volume_scatter = False

    area("Parts Key", 0.25, (-0.6, 0.45, 0.02), (-0.08, 0.0, -0.05), P["parts_key"], size_y=0.6,
         diffuse=False)
    area("Parts Rim Cool", 0.3, (-0.45, -0.1, -0.12), (-0.1, 0.0, -0.03), P["parts_rim"], size_y=0.6,
         colour=P["stops"][1][1][:3], diffuse=False)
    area("Parts Rim Warm", 0.3, (0.35, 0.1, -0.1), (-0.05, 0.0, -0.03), P["parts_rim"], size_y=0.6,
         colour=P["parts_rim_warm"], diffuse=False)

    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    studio_world(world)
    scene.world = world

    # Camera, focused on the top face.
    tilt = math.radians(P["cam_tilt"])
    loc = Vector((0, -math.sin(tilt) * P["cam_dist"], math.cos(tilt) * P["cam_dist"]))
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = P["lens"]
    cam_data.sensor_fit = "VERTICAL"
    cam_data.sensor_height = 36
    cam = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam)
    cam.location = loc
    cam.rotation_euler = (Vector((0, 0, 0)) - loc).to_track_quat("-Z", "Y").to_euler()
    focus = bpy.data.objects.new("Focus", None)
    scene.collection.objects.link(focus)
    focus.location = (0, 0, top)
    cam_data.dof.use_dof = True
    cam_data.dof.focus_object = focus
    cam_data.dof.aperture_fstop = P["fstop"]
    scene.camera = cam

    c = scene.cycles
    c.max_bounces, c.transmission_bounces, c.volume_bounces = 32, 24, 12
    c.glossy_bounces, c.diffuse_bounces, c.transparent_max_bounces = 8, 4, 16
    c.caustics_reflective = False
    c.caustics_refractive = True
    c.blur_glossy = 0.2
    c.sample_clamp_indirect = 10.0
    c.use_denoising = True
    scene.render.resolution_x = P["res_x"]
    scene.render.resolution_y = P["res_y"]
    scene.view_settings.view_transform = P["view"]
    try:
        scene.view_settings.look = P["look"]
    except TypeError:
        print(f"[out] look not found: {P['look']}")
    if P["warp"] > 0:
        for name in ("Plate", "Strip"):
            warp_slab(scene.objects[name], opal)
        for o in list(scene.objects):
            if o.name.startswith(("Type ", "Logotype", "Rivet", "Screw")) or (
                    o.name.startswith("Clamp") and not o.name.endswith("Under")):
                ride_warp(o)

    # Accent lights reach only the type and hardware: on the milky plate they would add a veil.
    accents = bpy.data.collections.new("Accent Receivers")
    for o in scene.objects:
        if o.name.startswith(("Type ", "Logotype", "Rivet", "Clamp", "Screw")):
            accents.objects.link(o)
    for name in ("Softbox", "Rake"):
        scene.objects[name].light_linking.receiver_collection = accents
    # The key strips skip the flat plate too: in it they read as one hard glowing bar. They
    # still draw short glints on the rivets, the wet blobs, the type and the top strip's edge.
    key_rx = bpy.data.collections.new("Key Receivers")
    # Not the type: its flat tops mirror a thin strip as a stray vertical line ("Won|er").
    for o in [o for o in accents.objects if not o.name.startswith(("Type ", "Logotype"))] + [scene.objects["Strip"]]:
        key_rx.objects.link(o)
    for o in scene.objects:
        if o.name.startswith("Key "):
            o.light_linking.receiver_collection = key_rx

    # Hardware under the plate gets its own lights. They skip the plate as a shadow blocker
    # (shadow linking), as if the resin were clear to them, so the parts show form and gloss
    # through it instead of reading as flat silhouettes.
    parts = bpy.data.collections.new("Hardware Under")
    clear = bpy.data.collections.new("Hardware Blockers")
    for o in scene.objects:
        top_z = max(((o.matrix_world @ v.co).z for v in o.data.vertices), default=0) if o.type == "MESH" else 0
        if o.type == "MESH" and top_z < -P["plate_t"] / 2 and o.name != "Backlight":
            parts.objects.link(o)
            clear.objects.link(o)
    for name in ("Parts Key", "Parts Rim Cool", "Parts Rim Warm"):
        scene.objects[name].light_linking.receiver_collection = parts
        scene.objects[name].light_linking.blocker_collection = clear
    print("[out] hardware under:", sorted(o.name for o in parts.objects))
    how_to_tweak(HOW_TO_TWEAK)
    return scene


def post():
    ng, gi, go = post_group("Post", [
        ("Glow", "NodeSocketFloat", P["glow"], 0.0, 2.0),
        ("Glow Size", "NodeSocketFloat", P["glow_size"], 0.0, 1.0),
        ("Glow Threshold", "NodeSocketFloat", P["glow_threshold"], 0.0, 4.0),
        ("Chroma", "NodeSocketFloat", P["chroma"], 0.0, 0.05),
        ("Saturation", "NodeSocketFloat", P["saturation"], 0.0, 2.0),   # 1 = as rendered
        ("Grain", "NodeSocketFloat", P["grain"], 0.0, 0.5),             # film grain
    ])
    glare = ng.nodes.new("CompositorNodeGlare")
    glare.inputs["Type"].default_value = "Fog Glow"
    lens = ng.nodes.new("CompositorNodeLensdist")
    ng.links.new(gi.outputs["Image"], glare.inputs["Image"])
    for src, dst in (("Glow", "Strength"), ("Glow Size", "Size"), ("Glow Threshold", "Threshold")):
        ng.links.new(gi.outputs[src], glare.inputs[dst])
    ng.links.new(glare.outputs["Image"], lens.inputs["Image"])
    ng.links.new(gi.outputs["Chroma"], lens.inputs["Dispersion"])
    # Grade: the milk and the tone map pull the gel colours toward pastel; push them back.
    hs = ng.nodes.new("CompositorNodeHueSat")
    ng.links.new(lens.outputs["Image"], hs.inputs["Image"])
    ng.links.new(gi.outputs["Saturation"], hs.inputs["Saturation"])
    coords = ng.nodes.new("CompositorNodeImageCoordinates")
    ng.links.new(gi.outputs["Image"], coords.inputs["Image"])
    wn = ng.nodes.new("ShaderNodeTexWhiteNoise")
    wn.noise_dimensions = "2D"
    ng.links.new(coords.outputs["Pixel"], wn.inputs["Vector"])
    grain = ng.nodes.new("ShaderNodeMix")
    grain.data_type, grain.blend_type, grain.clamp_factor = "RGBA", "OVERLAY", False
    ng.links.new(gi.outputs["Grain"], grain.inputs[0])
    ng.links.new(hs.outputs["Image"], grain.inputs[6])
    ng.links.new(wn.outputs["Value"], grain.inputs[7])
    ng.links.new(grain.outputs[2], go.inputs["Image"])
    auto_layout(ng)
    return ng


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="wip", help="render name, saved to renders/<out>.png")
    ap.add_argument("--samples", type=int, default=256)
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
