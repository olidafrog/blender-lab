"""roman-model: a low-poly Roman legionnaire, built from nothing, rendered and saved.

Run from the repo root:
  tools/blender.sh experiments/roman-model/scripts/build.py --out v01 --samples 128 --scale 1
  ... --set key=value      override any value in P
  ... --mask               also a Workbench silhouette (renders/<out>_mask.png) for scripts/silhouette.py
  ... --sheet              also a debug sheet: front, side, back and hero views, colour per part
  ... --save               also save output/roman-model.blend

How it is built (see RESEARCH.md):
- Every length is in head units H. Joints come from IK: feet and hands are placed in P,
  hips, knees, shoulders and elbows follow.
- Body parts are closed lofts of superellipse rings along the posed bones, then
  Subdivision 1 and Decimate (Collapse) to a triangle target: the irregular facets.
- Armour and props are low-poly parts built face by face, flat shaded, no decimate.
- Character space: faces -Y, left is +X, up is +Z. The whole figure turns by P["turn"].
"""
import argparse
import ast
import math
import random
import sys
import zlib
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Euler, Matrix, Quaternion, Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from common import enable_gpu, experiment_paths  # noqa: E402
from nodes import auto_layout, group, how_to_tweak, use
from nodes import math as nmath  # noqa: E402
from comp import LEGACY, compositor, post_group, use_saved_render  # noqa: E402

EXP = experiment_paths(__file__)

# Every value a designer might tune lives here. Override with --set key=value.
# Lengths in head units (H); angles in degrees.
P = {
    # --- scale and stance
    "H": 0.30,                  # metres per head unit
    "turn": 28.0,               # whole figure turns toward the viewer's right
    "hip_h": 2.26,              # hip-joint height before the feet are planted
    "hip_half": 0.44,           # hip joints either side of centre
    "pelvis_tilt": 4.0,         # hip hike on the sword side (+)
    "chest_twist": -8.0,        # chest turns back toward the camera
    "chest_lean": 4.0,          # forward lean of the chest
    "chest_tilt": -3.0,         # shoulders tilt against the hips
    "foot_r": (-1.25, -0.15),   # right foot ankle (x, y) in character space, H
    "foot_l": (0.12, -0.95),     # left foot ankle
    "foot_yaw_r": -38.0,        # toes out
    "foot_yaw_l": 14.0,
    "knee_out": 0.6,           # knees point out along x as well as forward
    "thigh_len": 1.10,
    "shin_len": 1.12,
    "ankle_h": 0.30,
    # --- torso (half widths / depths at named heights above the hip joint)
    "waist_z": 0.46, "waist_w": 0.64, "waist_d": 0.48,
    "hip_w": 0.80, "hip_d": 0.52,
    "chest_z": 1.44, "chest_w": 1.10, "chest_d": 0.62,
    "pec": 0.10, "lat": 0.08, "jitter": 0.025, "seed": 0,                # pec bulge on the front
    "shoulder_z": 1.44, "shoulder_half": 1.18,
    "neck_z": 2.04, "neck_r": 0.28,
    "torso_tris": 520,
    # --- arms
    "upper_len": 0.95, "fore_len": 0.88,
    "arm_r": (0.30, 0.34, 0.40, 0.28, 0.36, 0.23),  # cap, deltoid, bicep, elbow, forearm, wrist
    "hand_r": (-1.80, -0.45, 2.28),           # right fist (sword) target, character space
    "hand_l": (1.42, -0.70, 2.12),            # left fist (shield) target
    "elbow_pole_r": (1.0, 0.3, 0.0),         # elbow points back and out
    "elbow_pole_l": (0.6, 0.6, -0.3),
    "limb_tris": 150,
    "fist": (0.58, 0.52, 0.48),               # width, depth, length
    # --- legs
    "leg_r": (0.30, 0.37, 0.40, 0.32, 0.24, 0.18),  # hip, upper thigh, lower thigh, knee, calf, ankle
    # --- head and helmet
    "head_tilt": (12.0, 0.0, 12.0),
    "head_lift": 0.56,           # nod, roll, turn (toward the viewer's right +)
    "helmet_w": 0.52, "helmet_d": 0.58, "helmet_scale": 1.0, "face_flat": 0.84,
    "helmet_thick": 0.07,
    "eye_slot": 52.0,                         # half-angle of the eye slot
    "nose_half": 9.0,                         # half-angle of the nose guard / mouth gap
    "crest_h": 0.46, "crest_w": 0.20, "crest_back": 1.45,
    # --- armour and props
    "pad_r": 0.56, "pad_tilt": 22.0, "pad_drop": 0.22, "pad_out": 0.16, "pad_flat": 0.80,
    "belt_h": 0.28, "belt_out": 0.13,
    "skirt_hem": -0.55, "skirt_flare": 1.95, "skirt_pleats": 14, "pleat_depth": 0.05,
    "strap_w": 0.34,
    "bracer_len": (0.30, 0.90),               # along the forearm, as a fraction
    "boot_top": 0.84, "boot_r": 0.27, "foot_len": 0.95, "foot_w": 0.26,
    "sword_blade": 1.75, "sword_pitch": 32.0, "sword_yaw": 35.0,
    "shield_h": 3.0, "shield_w": 1.60, "shield_yaw": -15.0, "shield_roll": -12.0, "shield_off": (-0.20, 0.0, -0.18),
    # --- look
    "look": "clay",             # clay (the reference) or legion (colour)
    "clay_color": (0.66, 0.46, 0.17, 1.0),
    "clay_rough": 0.7,
    "facet_vary": 0.06, "grain": 0.08,
    # --- camera and light
    "res": 1500,
    "cam_focal": 50.0,
    "cam_dist": 2.96,            # metres from the figure's centre line
    "cam_height": 1.05,
    "cam_target": 0.835,
    "cam_shift_x": 0.0,
    "key_power": 330.0,
    "key_size": 1.2,
    "key_pos": (-3.2, -3.4, 4.6),
    "world_color": (1.0, 0.80, 0.56),
    "world_strength": 0.3,
    "cyc_color": (0.92, 0.70, 0.42, 1.0),
    "cyc_glow": 0.80,
    "cyc_albedo": 0.22,
    "cyc_bounce": False,
    "view": "Standard",
    "exposure": 0.15,
    "glow": 0.0, "glow_size": 0.5, "glow_threshold": 1.0, "chroma": 0.0,
}

HOW_TO_TWEAK = """\
roman-model — how to tweak

Each material is one node. Select a part, open the Shader Editor and change the inputs
on its group node (Colour, Gloss, Metal).

- Facets: each body part has a Decimate modifier. Lower Ratio = bigger facets.
- Key light: select "Key", change Power and Size in Object Data.
- Post: open the Compositing tab and change the inputs on the "Post" node.

Built by experiments/roman-model/scripts/build.py. Changes made here are lost on rebuild;
copy good values back into P. Pose, proportions and parts live in P (head units).
"""

PARTS = []   # (object, category) for the size table and the debug sheet


# ------------------------------------------------------------------ helpers

def h(v):
    """Head units → metres, for numbers and tuples."""
    if isinstance(v, (tuple, list)):
        return Vector([x * P["H"] for x in v])
    return v * P["H"]


def rot(x=0.0, y=0.0, z=0.0):
    return Euler((math.radians(x), math.radians(y), math.radians(z)), "XYZ").to_matrix()


def frame_from(axis, front):
    """Rotation whose local -Z runs along `axis` and local -Y leans toward `front`."""
    zc = -axis.normalized()
    yc = -(front - front.project(zc))
    if yc.length < 1e-6:
        yc = Vector((0, 1, 0)) - Vector((0, 1, 0)).project(zc)
    yc.normalize()
    xc = yc.cross(zc)
    m = Matrix((xc, yc, zc)).transposed()
    return m


def superellipse(rx, ry, a, p=2.4):
    """Point on a superellipse. a = 0 is local +X (left), 90° is the front (local -Y)."""
    c, s = math.cos(a), math.sin(a)
    x = rx * math.copysign(abs(c) ** (2 / p), c)
    y = -ry * math.copysign(abs(s) ** (2 / p), s)
    return x, y


def ring(origin, R, rx, ry, n=12, p=2.4, z=0.0, bump=None):
    """A ring of n points in the local XY plane of frame R, z along local Z (metres)."""
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        x, y = superellipse(rx, ry, a, p)
        if bump:
            f = bump(a)
            x, y = x * f, y * f
        pts.append(origin + R @ Vector((x, y, z)))
    return pts


def new_object(name, bm, cat, smooth=False):
    me = bpy.data.meshes.new(name)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = smooth
    bm.to_mesh(me)
    bm.free()
    rng = random.Random(zlib.crc32(name.encode()) + 7)
    me.attributes.new("facet", "FLOAT", "FACE").data.foreach_set("value", [rng.random() for _ in me.polygons])
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(MATS[cat])
    PARTS.append((ob, cat))
    return ob


def loft(name, rings, cat, caps=True, low=False):
    """Closed tube through rings of equal size; triangle-fan caps.
    low=True: jitter every vertex a little and triangulate, so a coarse loft reads as
    hand-placed irregular facets (no subdivision, no decimate)."""
    bm = bmesh.new()
    vs = [[bm.verts.new(p) for p in r] for r in rings]
    n = len(rings[0])
    for a, b in zip(vs, vs[1:]):
        for j in range(n):
            bm.faces.new((a[j], a[(j + 1) % n], b[(j + 1) % n], b[j]))
    if caps:
        for r, flip in ((vs[0], True), (vs[-1], False)):
            c = bm.verts.new(sum((v.co for v in r), Vector()) / n)
            for j in range(n):
                tri = (c, r[j], r[(j + 1) % n])
                bm.faces.new(tri[::-1] if flip else tri)
    if low:
        jitter(bm, name)
    return new_object(name, bm, cat)


def jitter(bm, name):
    rng = random.Random(zlib.crc32(name.encode()) + P["seed"])
    j = h(P["jitter"])
    for v in bm.verts:
        v.co += Vector((rng.uniform(-j, j), rng.uniform(-j, j), rng.uniform(-j, j)))
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")


def facet(ob, tris):
    """Subdivision 1 then Decimate (Collapse) to about `tris` triangles."""
    sub = ob.modifiers.new("Smooth", "SUBSURF")
    sub.levels = sub.render_levels = 1
    src = sum(len(p.vertices) - 2 for p in ob.data.polygons) * 4
    dec = ob.modifiers.new("Decimate", "DECIMATE")
    dec.decimate_type = "COLLAPSE"
    dec.use_collapse_triangulate = True
    dec.ratio = min(1.0, tris / max(1, src))
    return ob


def solid(ob, thick, offset=-1.0):
    m = ob.modifiers.new("Thickness", "SOLIDIFY")
    m.thickness = h(thick)
    m.offset = offset
    m.use_even_offset = True
    return ob


def grid_surface(name, rows, cat, keep=lambda i, j: True, cyclic=True, pole=None, low=False, close=False):
    """Quad surface through rows of points; faces where keep(row, col) is False are left out."""
    bm = bmesh.new()
    vs = [[bm.verts.new(p) for p in r] for r in rows]
    n = len(rows[0])
    for i in range(len(rows) - 1):
        for j in range(n if cyclic else n - 1):
            if keep(i, j):
                bm.faces.new((vs[i][j], vs[i][(j + 1) % n], vs[i + 1][(j + 1) % n], vs[i + 1][j]))
    if pole is not None:
        c = bm.verts.new(pole)
        for j in range(n):
            bm.faces.new((c, vs[0][(j + 1) % n], vs[0][j]))
    if close:
        bm.faces.new(vs[-1])
    if low:
        jitter(bm, name)
    return new_object(name, bm, cat)


def box(name, M, size, cat, bevel=0.0):
    """Box of `size` (x, y, z in metres) under 4×4 matrix M, with an optional 1-segment bevel."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel:
        bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:], offset=bevel, segments=1,
                        affect="EDGES", clamp_overlap=True)
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    return new_object(name, bm, cat)


def two_bone(root, target, l1, l2, pole):
    """Two-bone IK: returns the middle joint (knee or elbow)."""
    d = target - root
    dist = min(d.length, (l1 + l2) * 0.999)
    u = d.normalized()
    cos_a = (l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist)
    a = math.acos(max(-1.0, min(1.0, cos_a)))
    v = pole - pole.project(u)
    v.normalize()
    return root + (u * math.cos(a) + v * math.sin(a)) * l1


# ------------------------------------------------------------------ materials

MATS = {}


def surface_group():
    ng, gi, go = group("Surface", [
        ("Colour", "NodeSocketColor", (0.8, 0.8, 0.8, 1.0), None, None),
        ("Gloss", "NodeSocketFloat", 0.3, 0.0, 1.0),     # 0 matte, 1 mirror
        ("Metal", "NodeSocketFloat", 0.0, 0.0, 1.0),
        ("Glow", "NodeSocketFloat", 0.0, 0.0, 2.0),      # self-light in its own colour
        ("Facet Vary", "NodeSocketFloat", 0.0, 0.0, 0.3),  # per-facet tone shift
        ("Grain", "NodeSocketFloat", 0.0, 0.0, 0.3),       # fine surface grain
    ], [("Shader", "NodeSocketShader")])
    bsdf = ng.nodes.new("ShaderNodeBsdfPrincipled")
    # tone = colour × (1 + vary·(facet − ½)·2 + grain·(noise − ½)·2)
    attr = ng.nodes.new("ShaderNodeAttribute")
    attr.attribute_type, attr.attribute_name = "GEOMETRY", "facet"
    tc = ng.nodes.new("ShaderNodeTexCoord")
    noise = ng.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 60.0
    noise.inputs["Detail"].default_value = 3.0
    ng.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    f1 = nmath(ng, "MULTIPLY", nmath(ng, "SUBTRACT", attr.outputs["Fac"], 0.5), 2.0)
    f1 = nmath(ng, "MULTIPLY", f1, gi.outputs["Facet Vary"])
    f2 = nmath(ng, "MULTIPLY", nmath(ng, "SUBTRACT", noise.outputs["Fac"], 0.5), 2.0)
    f2 = nmath(ng, "MULTIPLY", f2, gi.outputs["Grain"])
    fac = nmath(ng, "ADD", nmath(ng, "ADD", f1, f2), 1.0)
    scale = ng.nodes.new("ShaderNodeVectorMath")
    scale.operation = "SCALE"
    ng.links.new(gi.outputs["Colour"], scale.inputs[0])
    ng.links.new(fac, scale.inputs["Scale"])
    inv = ng.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    ng.links.new(gi.outputs["Gloss"], inv.inputs[1])
    ng.links.new(scale.outputs["Vector"], bsdf.inputs["Base Color"])
    ng.links.new(gi.outputs["Metal"], bsdf.inputs["Metallic"])
    ng.links.new(gi.outputs["Colour"], bsdf.inputs["Emission Color"])
    ng.links.new(gi.outputs["Glow"], bsdf.inputs["Emission Strength"])
    ng.links.new(inv.outputs[0], bsdf.inputs["Roughness"])
    bsdf.inputs["Specular IOR Level"].default_value = 0.3
    ng.links.new(bsdf.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


# name: (colour sRGB hex, gloss, metal) for the legion look
LEGION = {
    "skin": ("#D69E78", 0.35, 0.0),
    "cloth": ("#A02C24", 0.15, 0.0),
    "crest": ("#B8281F", 0.1, 0.0),
    "steel": ("#A4A8AA", 0.55, 0.7),
    "brass": ("#C9A04E", 0.55, 0.7),
    "leather": ("#5A3A24", 0.3, 0.0),
    "shield": ("#A8302A", 0.35, 0.0),
    "trim": ("#E2B243", 0.4, 0.0),
    "grip": ("#DCCCA4", 0.4, 0.0),
    "inner": ("#1A1410", 0.1, 0.0),
}


def hex_lin(hx):
    c = [int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c) + (1.0,)


def make_materials():
    ng = surface_group()
    for cat, (hx, gloss, metal) in LEGION.items():
        m = bpy.data.materials.new(cat.capitalize())
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        g = use(nt, ng)
        g.width = 260
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        out.location = (360, 0)
        nt.links.new(g.outputs["Shader"], out.inputs["Surface"])
        if P["look"] == "clay":
            col, gloss, metal = P["clay_color"], 1 - P["clay_rough"], 0.0
            if cat == "inner":
                col = tuple(c * 0.25 for c in P["clay_color"][:3]) + (1.0,)
        else:
            col = hex_lin(hx)
        g.inputs["Colour"].default_value = col
        g.inputs["Gloss"].default_value = gloss
        g.inputs["Metal"].default_value = metal
        if P["look"] != "clay":
            g.inputs["Facet Vary"].default_value = P["facet_vary"]
            g.inputs["Grain"].default_value = P["grain"] if cat in ("cloth", "leather", "crest", "shield") else P["grain"] * 0.4
        MATS[cat] = m


# ------------------------------------------------------------------ skeleton

def skeleton():
    """Joint positions (metres, world) and frames. Character space turned by P['turn']."""
    Rr = rot(z=P["turn"])
    S = {"Rr": Rr}
    hip = Vector((0, 0, h(P["hip_h"])))
    Rp = Rr @ rot(y=P["pelvis_tilt"])
    Rc = Rp @ rot(x=-P["chest_lean"], y=P["chest_tilt"], z=P["chest_twist"])
    S.update(pelvis=hip, Rp=Rp, Rc=Rc)

    def spine(z):
        """Origin and frame of the torso at height z (metres) above the hip joint."""
        t = max(0.0, min(1.0, z / h(P["shoulder_z"])))
        R = Quaternion(Rp.to_quaternion()).slerp(Rc.to_quaternion(), t).to_matrix()
        return hip + R @ Vector((0, 0, z)), R
    S["spine"] = spine

    # legs: IK from hip joints to planted ankles
    for side, sx in (("r", -1), ("l", 1)):
        hj = hip + Rp @ Vector((sx * h(P["hip_half"]), 0, 0))
        fx, fy = P[f"foot_{side}"]
        ankle = Rr @ Vector((h(fx), h(fy), 0)) + Vector((0, 0, h(P["ankle_h"])))
        pole = Rr @ Vector((sx * P["knee_out"] * (1.0 if side == "r" else 0.4), -1.0, 0))
        knee = two_bone(hj, ankle, h(P["thigh_len"]), h(P["shin_len"]), pole)
        S[f"hip_{side}"], S[f"knee_{side}"], S[f"ankle_{side}"] = hj, knee, ankle
        S[f"Rfoot_{side}"] = Rr @ rot(z=P[f"foot_yaw_{side}"])

    # arms: IK from shoulders to fist targets
    o, R = spine(h(P["shoulder_z"]))
    for side, sx in (("r", -1), ("l", 1)):
        sh = o + R @ Vector((sx * h(P["shoulder_half"]), 0, 0))
        tgt = Rr @ h(P[f"hand_{side}"])
        pole = Rr @ Vector(P[f"elbow_pole_{side}"])
        elbow = two_bone(sh, tgt, h(P["upper_len"]), h(P["fore_len"]), pole)
        S[f"sh_{side}"], S[f"elbow_{side}"], S[f"wrist_{side}"] = sh, elbow, tgt
        S[f"pole_{side}"] = pole
    no, nR = spine(h(P["neck_z"]))
    S["neck"], S["Rn"] = no, nR
    S["Rh"] = Rc @ rot(*P["head_tilt"])
    S["head"] = no + S["Rh"] @ Vector((0, h(0.10), h(P["head_lift"])))
    return S


# ------------------------------------------------------------------ body

def torso_shape(z):
    """Half width, half depth and pec strength at height z (head units above the hip joint)."""
    keys = [  # z, w, d
        (-0.40, 0.46, 0.34),
        (0.00, P["hip_w"], P["hip_d"]),
        (P["waist_z"], P["waist_w"], P["waist_d"]),
        (0.95, 0.80, 0.52),
        (1.22, P["chest_w"] * 0.96, P["chest_d"]),
        (P["chest_z"], P["chest_w"], P["chest_d"]),
        (1.64, P["chest_w"] * 0.98, P["chest_d"] * 0.88),
        (1.78, P["chest_w"] * 0.84, P["chest_d"] * 0.74),
        (1.92, 0.56, 0.42),
        (P["neck_z"], P["neck_r"] * 1.15, P["neck_r"]),
    ]
    for (z0, w0, d0), (z1, w1, d1) in zip(keys, keys[1:]):
        if z <= z1:
            t = max(0.0, (z - z0) / (z1 - z0))
            t = t * t * (3 - 2 * t)
            return w0 + (w1 - w0) * t, d0 + (d1 - d0) * t
    return keys[-1][1], keys[-1][2]


def torso_point(S, z, a, out=0.0):
    """Point on the built torso at height z (H) and ring angle a, pushed out by `out` (H) along
    its normal. Ray-cast from outside toward the spine, so straps and belts sit on the facets."""
    o, R = S["spine"](h(z))
    d = R @ Vector((math.cos(a), -math.sin(a), 0))
    hit, nrm, _, _ = S["torso_bvh"].ray_cast(o + d * h(3.0), -d)
    if hit is None:
        w, dd = torso_shape(z)
        x, y = superellipse(w, dd, a, 2.6)
        return o + R @ Vector((h(x), h(y), 0)) + d * h(out)
    return hit + nrm * h(out)


def pec_bump(z):
    k = P["pec"] * math.exp(-((z - 1.30) / 0.22) ** 2)

    def f(a):
        # two bumps either side of the front (front = 90°)
        return 1 + k * (math.exp(-((a - math.radians(62)) / 0.35) ** 2) +
                        math.exp(-((a - math.radians(118)) / 0.35) ** 2))
    return f


def torso_ring(S, z):
    """12 points round the torso at height z (H above the hip joint), angle 0 = left, 90° = front.
    Planes, not a tube: a pec shelf, a sternum crease, lat flare and a flatter back."""
    w, d = torso_shape(z)
    pec = P["pec"] * max(0.0, 1 - abs(z - 1.40) / 0.22)          # pecs push the front out
    lat = P["lat"] * max(0.0, 1 - abs(z - 1.15) / 0.35)           # lats flare the sides
    o, R = S["spine"](h(z))
    pts = []
    for k in range(12):
        a = math.radians(30 * k)
        c, sn = math.cos(a), math.sin(a)
        x = w * math.copysign(abs(c) ** 0.8, c)
        y = -(d if sn > 0 else d * 0.9) * math.copysign(abs(sn) ** 0.8, sn)
        if sn > 0.4:
            y -= pec * (0.6 if k == 3 else 1.0)       # k=3 is dead front: the sternum crease
        if abs(c) > 0.8:
            x += math.copysign(lat, c)
        pts.append(o + R @ h((x, y, 0)))
    return pts


def build_body(S):
    zs = [-0.40, 0.0, P["waist_z"], 0.80, 1.14, 1.24, 1.40, 1.60, 1.78, 1.92, P["neck_z"]]
    torso = loft("Torso", [torso_ring(S, z) for z in zs], "skin", low=True)
    bm = bmesh.new()
    bm.from_mesh(torso.data)
    S["torso_bvh"] = BVHTree.FromBMesh(bm)
    bm.free()

    # neck into the head
    no, Rn = S["neck"], S["Rn"]
    rings = [ring(no, Rn, h(P["neck_r"] * 1.1), h(P["neck_r"]), n=10, z=h(z)) for z in (-0.1, 0.25, 0.5)]
    loft("Neck", rings, "skin", low=True)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=7, radius=1.0)
    bmesh.ops.scale(bm, vec=h((0.36, 0.40, 0.46)), verts=bm.verts)
    bmesh.ops.transform(bm, matrix=Matrix.Translation(S["head"]) @ S["Rh"].to_4x4(), verts=bm.verts)
    new_object("Head", bm, "inner")

    ar = P["arm_r"]
    for side in ("r", "l"):
        sh, el, wr = S[f"sh_{side}"], S[f"elbow_{side}"], S[f"wrist_{side}"]
        pole = S[f"pole_{side}"]
        Ru = frame_from(el - sh, -pole)
        Rf = frame_from(wr - el, -pole)
        Re = Quaternion(Ru.to_quaternion()).slerp(Rf.to_quaternion(), 0.5).to_matrix()
        L1, L2 = (el - sh).length, (wr - el).length
        # cap, deltoid, bicep, elbow, forearm swell, wrist
        rings = [
            ring(sh, Ru, h(ar[0]), h(ar[0]), n=8, z=h(0.12)),
            ring(sh, Ru, h(ar[1]), h(ar[1] * 0.95), n=8, z=-L1 * 0.18),
            ring(sh, Ru, h(ar[2] * 0.92), h(ar[2] * 1.08), n=8, z=-L1 * 0.50),
            ring(el, Re, h(ar[3]), h(ar[3]), n=8),
            ring(el, Rf, h(ar[4]), h(ar[4] * 0.88), n=8, z=-L2 * 0.30),
            ring(el, Rf, h(ar[5]), h(ar[5] * 0.85), n=8, z=-L2 * 1.0),
        ]
        loft(f"Arm.{side}", rings, "skin", low=True)
        S[f"Ru_{side}"], S[f"Rf_{side}"] = Ru, Rf
        # fist: bevelled box beyond the wrist, knuckles forward
        fw, fd, fl = P["fist"]
        M = Matrix.Translation(wr + Rf @ Vector((0, 0, -h(fl * 0.45)))) @ Rf.to_4x4()
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:], offset=0.14, segments=1, affect="EDGES")
        bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) < 1e-4
                                             and abs(e.verts[0].co.z) > 0.4], cuts=1)
        bmesh.ops.scale(bm, vec=h((fw, fd, fl)), verts=bm.verts)
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
        jitter(bm, f"Fist.{side}")
        new_object(f"Fist.{side}", bm, "skin")
        thumb = Matrix.Translation(wr + Rf @ h((0, -fd * 0.45, -fl * 0.25))) @ (Rf @ rot(x=25)).to_4x4()
        box(f"Thumb.{side}", thumb, h((fw * 0.35, 0.16, 0.26)), "skin", bevel=h(0.03))
        S[f"fist_{side}"] = wr + Rf @ Vector((0, 0, -h(fl * 0.45)))

    lr = P["leg_r"]
    for side in ("r", "l"):
        hj, kn, an = S[f"hip_{side}"], S[f"knee_{side}"], S[f"ankle_{side}"]
        front = S["Rr"] @ Vector((0, -1, 0))
        Rt = frame_from(kn - hj, front)
        Rs = frame_from(an - kn, front)
        Rk = Quaternion(Rt.to_quaternion()).slerp(Rs.to_quaternion(), 0.5).to_matrix()
        L1, L2 = (kn - hj).length, (an - kn).length
        # hip, upper thigh, lower thigh, knee, calf, ankle
        rings = [
            ring(hj, Rt, h(lr[0]), h(lr[0]), n=8, z=h(0.2)),
            ring(hj, Rt, h(lr[1]), h(lr[1] * 1.05), n=8, z=-L1 * 0.3),
            ring(hj, Rt, h(lr[2]), h(lr[2]), n=8, z=-L1 * 0.75),
            ring(kn, Rk, h(lr[3] * 1.05), h(lr[3]), n=8),
            ring(kn, Rs, h(lr[4]), h(lr[4] * 1.1), n=8, z=-L2 * 0.35),
            ring(kn, Rs, h(lr[5]), h(lr[5]), n=8, z=-L2),
        ]
        loft(f"Leg.{side}", rings, "skin", low=True)
        S[f"Rt_{side}"], S[f"Rs_{side}"] = Rt, Rs


# ------------------------------------------------------------------ armour and props

def build_helmet(S):
    """Corinthian helm: bell dome, flat face plate with a T cut, thick cheek guards, crest on a holder."""
    c, R = S["head"], S["Rh"]
    w, d, k = P["helmet_w"], P["helmet_d"], P["helmet_scale"]
    e, nz = P["eye_slot"], P["nose_half"]
    # column angles from the front (0) round both sides, in degrees
    cols = [-165, -140, -112, -84, -e, -24, -nz, nz, 24, e, 84, 112, 140, 165, 180]
    # rows: height above the head centre (H), radius scale; the brow row is index 4, eye bottom 5
    rows_def = [(0.57, 0.32), (0.50, 0.64), (0.39, 0.87), (0.25, 0.99), (0.10, 1.03),
                (-0.06, 1.03), (-0.30, 1.00), (-0.55, 0.94)]
    last = len(rows_def) - 1
    rows = []
    for zi, (z, sc) in enumerate(rows_def):
        r = []
        for a in cols:
            ar = math.radians(a)
            x = math.sin(ar) * w * sc
            y = -math.cos(ar) * d * sc
            if zi >= 3 and abs(a) < 45:
                y = max(y, -d * P["face_flat"])          # flat face plate from the brow down
            if zi == last and abs(a) > 100:
                x, y = x * 1.10, y * 1.12                 # neck guard flares out
            if zi == last and abs(a) < 40:
                x *= 0.80                                 # cheek guards close in toward the jaw
            if zi >= 4 and abs(a) < 30:
                y -= 0.05 * (zi - 3)                      # ... and jut forward
            r.append(c + R @ (Vector((x, y, z)) * P["H"] * k))
        rows.append(r)
    eye_cols = {i for i in range(len(cols) - 1) if abs(cols[i]) <= e + 0.1 and abs(cols[i + 1]) <= e + 0.1}
    nose_col = cols.index(-nz)

    def keep(i, j):
        if i == 4 and j in eye_cols and j != nose_col:
            return False  # eye slot either side of the nose bar
        if i >= 5 and j == nose_col:
            return False  # vertical cut between the cheek guards
        return True
    ob = grid_surface("Helmet", rows, "steel", keep=keep, pole=c + R @ (Vector((0, 0, 0.60)) * P["H"] * k), low=True)
    solid(ob, P["helmet_thick"], offset=1.0)
    # nose guard: a wedge hanging from the brow into the T
    nb = c + R @ (Vector((0, -d * P["face_flat"] - 0.05, 0.02)) * P["H"] * k)
    box("Nose", Matrix.Translation(nb) @ (R @ rot(x=-8)).to_4x4(), h((0.10 * k, 0.09, 0.30 * k)), "steel", bevel=h(0.015))

    # crest holder: a block on the crown
    top = c + R @ (Vector((0, 0.02, 0.61)) * P["H"] * k)
    box("CrestHolder", Matrix.Translation(top) @ R.to_4x4(), h((0.16, 0.34, 0.14)), "brass", bevel=h(0.02))
    # crest: a long crescent between two arcs (local +Y is the back). It starts over the brow,
    # stays high over the crown and sweeps back past the dome, its tail dropping behind the head.
    bm = bmesh.new()
    n = 12
    half = h(P["crest_w"]) / 2
    ch, cb = P["crest_h"], P["crest_back"]

    def bez(a, b, c2, t):
        return a * (1 - t) ** 2 + b * 2 * t * (1 - t) + c2 * t * t
    O0, O1, O2 = Vector((-0.24, 0.62 + ch)), Vector((0.45, 0.88 + ch)), Vector((cb, 0.52))
    I0, I1, I2 = Vector((-0.12, 0.60)), Vector((0.45, 0.76)), Vector((cb - 0.22, 0.40))
    base, tip = [], []
    for i in range(n):
        t = i / (n - 1)
        o, q = bez(O0, O1, O2, t), bez(I0, I1, I2, t)
        o = o + (o - q).normalized() * (0.012 if i % 2 else -0.008)   # set points along the top
        base.append(Vector((0, q.x, q.y)) * k)
        tip.append(Vector((0, o.x, o.y)) * k)
    M = Matrix.Translation(c) @ R.to_4x4()
    sides = []
    for sx in (-1, 1):
        sides.append(([bm.verts.new(M @ (h(v) + Vector((sx * half, 0, 0)))) for v in base],
                      [bm.verts.new(M @ (h(v) + Vector((sx * half * 0.55, 0, 0)))) for v in tip]))
    (bl, tl), (br, tr) = sides
    for i in range(n - 1):
        bm.faces.new((bl[i], bl[i + 1], tl[i + 1], tl[i]))
        bm.faces.new((br[i], tr[i], tr[i + 1], br[i + 1]))
        bm.faces.new((tl[i], tl[i + 1], tr[i + 1], tr[i]))
        bm.faces.new((bl[i], br[i], br[i + 1], bl[i + 1]))
    for i in (0, n - 1):
        bm.faces.new((bl[i], tl[i], tr[i], br[i]))
    new_object("Crest", bm, "crest")


def build_armour(S):
    Rc = S["Rc"]
    # shoulder pads: one rounded cap each, pointing out and a little up
    for side, sx in (("r", -1), ("l", 1)):
        sh = S[f"sh_{side}"]
        axis = Rc @ Vector((sx * math.cos(math.radians(P["pad_tilt"])), 0, math.sin(math.radians(P["pad_tilt"]))))
        Rpad = frame_from(-axis, Rc @ Vector((0, -1, 0)))  # local +Z = axis
        # one rounded cap on the deltoid; the last row flares out a little as a rim
        r = h(P["pad_r"])
        cen = sh + axis * h(P["pad_out"]) - Rc @ Vector((0, 0, h(P["pad_drop"])))
        nlon = 10
        rows = []
        for th, grow in ((32, 1.0), (58, 1.0), (82, 1.08)):
            th = math.radians(th)
            rows.append([cen + Rpad @ Vector((r * grow * math.sin(th) * math.cos(2 * math.pi * j / nlon),
                                               r * grow * math.sin(th) * math.sin(2 * math.pi * j / nlon),
                                               r * math.cos(th) * P["pad_flat"])) for j in range(nlon)])
        grid_surface(f"Pad.{side}", rows, "steel", pole=cen + Rpad @ Vector((0, 0, r * P["pad_flat"])), close=True)

    # belt: a band just outside the waist
    zc, bh, out = P["waist_z"], P["belt_h"], P["belt_out"]
    n = 16
    rings = [[torso_point(S, z, 2 * math.pi * k / n + math.pi / 16, out) for k in range(n)]
             for z in (zc - bh / 2, zc + bh / 2)]
    loft("Belt", rings, "leather")

    # strap (baldric): over the right shoulder, across the chest, to the belt at the front-left
    bm = bmesh.new()
    m = 7
    path = []
    for i in range(m):
        t = i / (m - 1)
        z = 1.84 - t * (1.84 - P["waist_z"] - 0.05)
        a = math.radians(140 - t * 95)
        path.append((torso_point(S, z, a, 0.04), S["spine"](h(z))[0]))
    edge = []
    for i, (c0, axis_pt) in enumerate(path):
        tan = path[min(i + 1, m - 1)][0] - path[max(i - 1, 0)][0]
        nrm = c0 - axis_pt
        wv = nrm.cross(tan).normalized() * h(P["strap_w"] / 2)
        edge.append((bm.verts.new(c0 + wv), bm.verts.new(c0 - wv)))
    for (a0, b0), (a1, b1) in zip(edge, edge[1:]):
        bm.faces.new((a0, a1, b1, b0))
    solid(new_object("Strap", bm, "leather"), 0.09, offset=1.0)

    # skirt: flat plates hung round the hips under the belt, alternately stepped in and out
    Rp, hip = S["Rp"], S["pelvis"]
    top_z, hem = P["waist_z"] - P["belt_h"] / 2 + 0.04, P["skirt_hem"]
    wt, dt = torso_shape(top_z)
    wh, dh = torso_shape(0.0)
    npl = P["skirt_pleats"]
    bm = bmesh.new()
    for j in range(npl):
        step = P["pleat_depth"] if j % 2 else 0.0
        a0, a1 = 2 * math.pi * (j - 0.55) / npl, 2 * math.pi * (j + 0.55) / npl
        drop = hem + 0.04 * ((j * 7) % 3 - 1)
        quad = []
        for a, z, w, d, fl in ((a0, top_z, wt, dt, 1.0), (a1, top_z, wt, dt, 1.0),
                               (a1, drop, wh, dh, P["skirt_flare"]), (a0, drop, wh, dh, P["skirt_flare"])):
            x, y = superellipse((w + 0.06 + step) * fl, (d + 0.06 + step) * fl, a, 2.2)
            quad.append(bm.verts.new(hip + Rp @ h((x, y, z))))
        bm.faces.new(quad)
    solid(new_object("Skirt", bm, "cloth"), 0.05, offset=1.0)

    # bracers on both forearms
    for side in ("r", "l"):
        el, wr, Rf = S[f"elbow_{side}"], S[f"wrist_{side}"], S[f"Rf_{side}"]
        L = (wr - el).length
        f0, f1 = P["bracer_len"]
        ar = P["arm_r"]
        rings = [ring(el, Rf, h(ar[4] * 1.10), h(ar[4] * 1.04), n=8, p=2.2, z=-L * f0),
                 ring(el, Rf, h(ar[5] * 1.25), h(ar[5] * 1.16), n=8, p=2.2, z=-L * f1)]
        loft(f"Bracer.{side}", rings, "leather")

    # boots: a shaft up the shin with a cuff, and a foot block
    for side in ("r", "l"):
        an, kn, Rs, Rf = S[f"ankle_{side}"], S[f"knee_{side}"], S[f"Rs_{side}"], S[f"Rfoot_{side}"]
        top = P["boot_top"]
        shin = (kn - an)
        t_top = (h(top) - an.z) / max(1e-4, shin.z)
        ctop = an + shin * t_top
        br = P["boot_r"]
        # one tapered shaft, then a turned cuff that flares past it
        rings = [ring(an, Rs, h(br * 0.98), h(br * 1.08), n=10, z=h(0.1)),
                 ring(an + (ctop - an) * 0.45, Rs, h(br * 1.02), h(br * 1.12), n=10),
                 ring(ctop, Rs, h(br * 1.06), h(br * 1.10), n=10)]
        loft(f"Boot.{side}", rings, "leather")
        cuff = [ring(ctop, Rs, h(br * 1.28), h(br * 1.32), n=10, z=h(z)) for z in (-0.08, 0.10)]
        loft(f"Cuff.{side}", cuff, "leather")
        # foot: flat-soled hexagon rings along the foot's forward axis
        fl, fw = P["foot_len"], P["foot_w"]
        base = Vector((an.x, an.y, 0.0))
        prof = [(-0.32, 0.92, 0.50), (0.0, 1.0, 0.62), (0.35, 1.06, 0.46), (0.62, 1.06, 0.34), (fl - 0.30, 0.82, 0.22)]
        rings = []
        for sf, wscale, ht in prof:
            o = base + Rf @ h((0, -sf, 0))
            w = fw * wscale
            hexa = [(-w, 0), (w, 0), (w, 0.55 * ht), (0.6 * w, ht), (-0.6 * w, ht), (-w, 0.55 * ht)]
            rings.append([o + Rf @ h((x, 0, zz)) for x, zz in hexa])
        loft(f"Foot.{side}", rings, "leather")


def build_props(S):
    # gladius in the right fist: grip through the fist, blade forward and down
    fist = S["fist_r"]
    pch, yw = math.radians(P["sword_pitch"]), math.radians(P["sword_yaw"])
    blade_dir = S["Rr"] @ Vector((math.cos(pch) * math.cos(yw), -math.cos(pch) * math.sin(yw), -math.sin(pch)))
    Rsw = frame_from(blade_dir, Vector((0, -1, 0)))    # local -Z = blade direction, flat toward the camera
    M = Matrix.Translation(fist) @ Rsw.to_4x4()
    box("Grip", M @ Matrix.Translation(h((0, 0, 0.05))), h((0.12, 0.12, 0.62)), "grip", bevel=h(0.02))
    box("Pommel", M @ Matrix.Translation(h((0, 0, 0.40))), h((0.2, 0.2, 0.14)), "brass", bevel=h(0.04))
    box("Guard", M @ Matrix.Translation(h((0, 0, -0.30))), h((0.64, 0.18, 0.13)), "brass", bevel=h(0.03))
    L, W, T = h(P["sword_blade"]), h(0.34), h(0.09)
    bm = bmesh.new()
    prof = [(0.0, 1.0), (0.55, 0.92), (0.82, 0.75), (1.0, 0.0)]  # length fraction, width fraction
    rings = []
    for t, wf in prof:
        z = -h(0.36) - L * t
        pts = [(W / 2 * wf, 0), (0, -T / 2 * max(wf, 0.2)), (-W / 2 * wf, 0), (0, T / 2 * max(wf, 0.2))]
        rings.append([bm.verts.new(M @ Vector((x, y, z))) for x, y in pts])
    for a, b in zip(rings, rings[1:]):
        for j in range(4):
            bm.faces.new((a[j], a[(j + 1) % 4], b[(j + 1) % 4], b[j]))
    bm.faces.new(rings[0][::-1])
    new_object("Blade", bm, "steel")

    # shield on the left forearm, upright, face turned out and toward the camera
    el, wr = S["elbow_l"], S["wrist_l"]
    mid = el + (wr - el) * 0.55
    Rsh = S["Rr"] @ rot(z=P["shield_yaw"]) @ rot(y=P["shield_roll"])
    c = mid + Rsh @ h(P["shield_off"])
    hh, hw = P["shield_h"], P["shield_w"]
    outline = [(-0.5, 0.42), (0.5, 0.50), (0.5, -0.12), (0.30, -0.36), (0.0, -0.50), (-0.30, -0.36), (-0.5, -0.12)]
    curve = 0.12

    def pt(u, v, depth):
        x, z = u * hw, v * hh
        y = -depth + curve * (2 * u) ** 2
        return c + Rsh @ h((x, y, z))
    bm = bmesh.new()
    ring_out = [bm.verts.new(pt(u, v, 0.0)) for u, v in outline]
    ring_back = [bm.verts.new(pt(u, v, -0.10)) for u, v in outline]
    inner = [(u * 0.84, v * 0.86 - 0.01) for u, v in outline]
    ring_in = [bm.verts.new(pt(u, v, 0.0)) for u, v in inner]
    ring_face = [bm.verts.new(pt(u, v, -0.035)) for u, v in inner]
    n = len(outline)
    for j in range(n):
        k = (j + 1) % n
        for quad in ((ring_out[j], ring_out[k], ring_back[k], ring_back[j]),     # outer edge
                     (ring_in[j], ring_in[k], ring_out[k], ring_out[j]),         # rim top
                     (ring_face[j], ring_face[k], ring_in[k], ring_in[j])):      # rim inner wall
            bm.faces.new(quad).material_index = 1                              # the rim is brass
    bm.faces.new(ring_face[::-1])
    bm.faces.new(ring_back)
    new_object("Shield", bm, "shield").data.materials.append(MATS["brass"])

    # painted emblem: four wings round the boss, raised a hair off the face
    bm = bmesh.new()
    wing = [(0.07, 0.10), (0.34, 0.33), (0.37, 0.25), (0.30, 0.23), (0.33, 0.16), (0.24, 0.14), (0.10, 0.04)]
    for su, sv, k2 in ((1, 1, 1.0), (-1, 1, 1.0), (1, -1, 0.8), (-1, -1, 0.8)):
        poly = [(su * u * k2, sv * v * k2) for u, v in wing]
        if su * sv < 0:
            poly = poly[::-1]
        fr = [bm.verts.new(pt(u, v, -0.02)) for u, v in poly]
        bk = [bm.verts.new(pt(u, v, -0.04)) for u, v in poly]
        bm.faces.new(fr)
        bm.faces.new(bk[::-1])
        for j in range(len(poly)):
            k2j = (j + 1) % len(poly)
            bm.faces.new((fr[j], bk[j], bk[k2j], fr[k2j]))
    new_object("Emblem", bm, "trim")
    boss = Matrix.Translation(pt(0.0, 0.02, 0.03)) @ Rsh.to_4x4()
    box("Boss", boss, h((0.34, 0.12, 0.40)), "brass", bevel=h(0.05))


# ------------------------------------------------------------------ scene

def cyc(scene):
    """Seamless floor-to-wall sweep behind the figure."""
    bm = bmesh.new()
    rows = []
    r, back = 1.6, 3.5
    profile = [(-6.0, 0.0)] + [(back - r + r * math.sin(t), r - r * math.cos(t))
                              for t in np.linspace(0, math.pi / 2, 8)] + [(back, 7.0)]
    for x in (-8.0, 8.0):
        rows.append([bm.verts.new((x, y, z)) for y, z in profile])
    for j in range(len(profile) - 1):
        bm.faces.new((rows[0][j], rows[1][j], rows[1][j + 1], rows[0][j + 1]))
    me = bpy.data.meshes.new("Cyc")
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("Cyc", me)
    scene.collection.objects.link(ob)
    ng = bpy.data.node_groups["Surface"]
    m = bpy.data.materials.new("Backdrop")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    g = use(nt, ng)
    # same emitted colour, less reflected key: floor and wall come out even
    k = P["cyc_albedo"]
    g.inputs["Colour"].default_value = tuple(c * k for c in P["cyc_color"][:3]) + (1.0,)
    g.inputs["Gloss"].default_value = 0.05
    g.inputs["Glow"].default_value = P["cyc_glow"] / k
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(g.outputs["Shader"], out.inputs["Surface"])
    ob.data.materials.append(m)
    ob.rotation_euler.z = math.radians(P["turn"] * 0.3)
    ob.visible_diffuse = P["cyc_bounce"]   # off: its glow lights the camera view only, not the figure
    return ob


def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    enable_gpu(scene)
    make_materials()

    S = skeleton()
    build_body(S)
    build_helmet(S)
    build_armour(S)
    build_props(S)

    # plant the figure: lowest point of any part at the floor, plus a hair
    dg = bpy.context.evaluated_depsgraph_get()
    zmin = min(min((ob.evaluated_get(dg).matrix_world @ v.co).z for v in ob.evaluated_get(dg).to_mesh().vertices)
               for ob, _ in PARTS)
    for ob, _ in PARTS:
        ob.location.z -= zmin - 3e-5
    root = bpy.data.objects.new("Legionnaire", None)
    scene.collection.objects.link(root)
    for ob, _ in PARTS:
        ob.parent = root

    cyc(scene)

    bpy.ops.object.light_add(type="AREA", location=P["key_pos"])
    key = bpy.context.active_object
    key.name = "Key"
    key.data.energy = P["key_power"]
    key.data.size = P["key_size"]
    tgt = Vector((0, 0, h(2.6)))
    key.rotation_euler = (tgt - key.location).to_track_quat("-Z", "Y").to_euler()

    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*P["world_color"], 1.0)
    bg.inputs["Strength"].default_value = P["world_strength"]
    scene.world = world

    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = P["cam_focal"]
    cam_data.shift_x = P["cam_shift_x"]
    cam = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (0, -P["cam_dist"], P["cam_height"])
    cam.rotation_euler = (Vector((0, 0, P["cam_target"])) - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam

    scene.render.resolution_x = scene.render.resolution_y = P["res"]
    scene.view_settings.view_transform = P["view"]
    scene.view_settings.exposure = P["exposure"]
    how_to_tweak(HOW_TO_TWEAK)
    return scene


def size_table():
    """Each part's evaluated size in head units, for checking proportions blind."""
    dg = bpy.context.evaluated_depsgraph_get()
    tris = 0
    print("[out] part            w      d      h    zmin  zmax  tris")
    for ob, _ in PARTS:
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        co = np.array([(ev.matrix_world @ v.co)[:] for v in me.vertices]) / P["H"]
        t = sum(len(p.vertices) - 2 for p in me.polygons)
        tris += t
        mn, mx = co.min(0), co.max(0)
        d = mx - mn
        print(f"[out] {ob.name:13s} {d[0]:5.2f}  {d[1]:5.2f}  {d[2]:5.2f}  {mn[2]:5.2f} {mx[2]:5.2f} {t:5d}")
        ev.to_mesh_clear()
    print(f"[out] total triangles {tris}")


def workbench(scene, path, mode):
    """mask: black subject on transparent; sheet: colour per object, studio light."""
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.use_compositing = False
    sh = scene.display.shading
    scene.render.film_transparent = True
    bpy.data.objects["Cyc"].hide_render = True
    if mode == "mask":
        sh.light, sh.color_type, sh.single_color = "FLAT", "SINGLE", (0, 0, 0)
    else:
        sh.light, sh.color_type = "STUDIO", "RANDOM"
        sh.show_object_outline = True
        sh.show_backface_culling = True     # flipped normals show as holes
        scene.render.film_transparent = False
    scene.display.render_aa = "8"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def sheet(scene, out):
    """Front, side, back and hero views side by side in one PNG."""
    H = P["H"]
    views = [("front", (0, -12, 2.8 * H), 0), ("side", (12, 0, 2.8 * H), 0), ("back", (0, 12, 2.8 * H), 0), ("hero", None, 0)]
    cam = scene.camera
    orig = (cam.location.copy(), cam.rotation_euler.copy(), cam.data.type)
    tiles = []
    res = scene.render.resolution_x
    scene.render.resolution_x = scene.render.resolution_y = 700
    scene.render.resolution_percentage = 100
    for name, loc, _ in views:
        if loc:
            cam.data.type, cam.data.ortho_scale = "ORTHO", 6.4 * H
            cam.location = loc
            cam.rotation_euler = (Vector((0, 0, loc[2])) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        else:
            cam.location, cam.rotation_euler, cam.data.type = orig
        p = EXP["renders"] / f"_sheet_{name}.png"
        workbench(scene, p, "sheet")
        img = bpy.data.images.load(str(p))
        a = np.array(img.pixels[:], dtype=np.float32).reshape(700, 700, 4)
        tiles.append(a)
        bpy.data.images.remove(img)
        p.unlink()
    cam.location, cam.rotation_euler, cam.data.type = orig
    scene.render.resolution_x = scene.render.resolution_y = res
    big = np.concatenate(tiles, axis=1)
    im = bpy.data.images.new("sheet", big.shape[1], big.shape[0], alpha=True)
    im.pixels = big.ravel()
    im.filepath_raw = str(EXP["renders"] / f"{out}_sheet.png")
    im.file_format = "PNG"
    im.save()
    print(f"Saved {im.filepath_raw}")


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="wip")
    ap.add_argument("--samples", type=int, default=128)
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--norender", action="store_true")
    ap.add_argument("--mask", action="store_true")
    ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    a = ap.parse_args(argv)
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in P:
            sys.exit(f"unknown P key: {k}")
        P[k] = v if isinstance(P[k], str) else ast.literal_eval(v)
    return a


def post():
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
    size_table()
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
    if args.mask:
        workbench(scene, EXP["renders"] / f"{args.out}_mask.png", "mask")
    if args.sheet:
        sheet(scene, args.out)
    print("BUILD OK")
