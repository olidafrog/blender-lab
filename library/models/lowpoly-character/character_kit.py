"""Low-poly character kit: pose a figure by IK and build faceted parts from code, no hand edits.
From experiments/roman-model (knowledge/gotchas/modelling.md, knowledge/decisions/roman-model.md).

    sys.path.insert(0, str(LIBRARY / "models" / "lowpoly-character"))
    import character_kit as ck

    knee = ck.two_bone(hip, ankle, thigh_len, shin_len, pole)       # IK: place feet/fists, joints follow
    R = ck.frame_from(knee - hip, front)                             # bone frame: local -Z along the bone
    rings = [ck.ring(hip, R, rx, ry, n=8, z=-t) for ...]             # 8-point rings along the bone
    bm = ck.loft_bm(rings)                                           # closed tube, fan caps
    ck.jitter_triangulate(bm, amount=0.0075, key="Leg.r")            # the irregular-facet look
    ob = ck.finish_mesh("Leg.r", bm, material)                       # flat shaded, `facet` attribute

Conventions: metres; a character faces -Y with its left at +X; ring angle 0 is local +X and 90°
is the front (local -Y). Build every part already posed; bone heat weighting fails on
multi-part meshes and a static render needs no rig.

The look: few controlled rings, jitter, triangulate. Do not subdivide and decimate; that gives
round tubes with ring bands. Jitter body parts only; armour and props stay clean prisms.
Each mesh gets a random per-face `facet` float attribute, for a per-facet tone shift in a shader.
"""
import math
import random
import zlib

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector


# ------------------------------------------------------------------ frames and IK

def rot(x=0.0, y=0.0, z=0.0):
    """3×3 rotation from Euler angles in degrees (XYZ)."""
    return Euler((math.radians(x), math.radians(y), math.radians(z)), "XYZ").to_matrix()


def frame_from(axis, front):
    """Rotation whose local -Z runs along `axis` and local -Y leans toward `front`."""
    zc = -axis.normalized()
    yc = -(front - front.project(zc))
    if yc.length < 1e-6:
        yc = Vector((0, 1, 0)) - Vector((0, 1, 0)).project(zc)
    yc.normalize()
    xc = yc.cross(zc)
    return Matrix((xc, yc, zc)).transposed()


def two_bone(root, target, l1, l2, pole):
    """Two-bone IK: the middle joint (knee or elbow). `pole` is the direction it bends toward.
    A pose that keeps missing (an arm gap, a splayed leg) is usually the pole, not the target."""
    d = target - root
    dist = min(d.length, (l1 + l2) * 0.999)
    u = d.normalized()
    cos_a = (l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist)
    a = math.acos(max(-1.0, min(1.0, cos_a)))
    v = pole - pole.project(u)
    v.normalize()
    return root + (u * math.cos(a) + v * math.sin(a)) * l1


# ------------------------------------------------------------------ rings

def superellipse(rx, ry, a, p=2.4):
    """Point on a superellipse. a = 0 is local +X (left), 90° is the front (local -Y)."""
    c, s = math.cos(a), math.sin(a)
    x = rx * math.copysign(abs(c) ** (2 / p), c)
    y = -ry * math.copysign(abs(s) ** (2 / p), s)
    return x, y


def ring(origin, R, rx, ry, n=12, p=2.4, z=0.0, bump=None):
    """n points in the local XY plane of frame R, offset z along local Z (metres).
    bump(a) → scale factor per angle, for a bulge on one side."""
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        x, y = superellipse(rx, ry, a, p)
        if bump:
            f = bump(a)
            x, y = x * f, y * f
        pts.append(origin + R @ Vector((x, y, z)))
    return pts


def torso_ring(origin, R, w, d, pec=0.0, lat=0.0, unit=1.0):
    """12 points round a torso, in planes rather than a tube: `pec` pushes the front out (and
    less at dead front: the sternum crease), `lat` pushes the sides out, the back is 10 % flatter.
    w, d, pec, lat are in `unit`s (for example a head unit in metres)."""
    pts = []
    for k in range(12):
        a = math.radians(30 * k)
        c, sn = math.cos(a), math.sin(a)
        x = w * math.copysign(abs(c) ** 0.8, c)
        y = -(d if sn > 0 else d * 0.9) * math.copysign(abs(sn) ** 0.8, sn)
        if sn > 0.4:
            y -= pec * (0.6 if k == 3 else 1.0)
        if abs(c) > 0.8:
            x += math.copysign(lat, c)
        pts.append(origin + R @ (Vector((x, y, 0)) * unit))
    return pts


# ------------------------------------------------------------------ bmesh builders

def loft_bm(rings, caps=True):
    """Closed tube through rings of equal size, with triangle-fan caps."""
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
    return bm


def grid_bm(rows, keep=lambda i, j: True, cyclic=True, pole=None, close=False):
    """Quad surface through rows of points. keep(row, col) False leaves a hole (an eye slot).
    pole: a point that fans the first row shut (a dome top). close: an n-gon over the last row."""
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
    return bm


def box_bm(M, size, bevel=0.0):
    """Box of `size` (x, y, z metres) under 4×4 matrix M, optional one-segment bevel."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel:
        bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:], offset=bevel, segments=1,
                        affect="EDGES", clamp_overlap=True)
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    return bm


def jitter_triangulate(bm, amount, key, seed=0):
    """Move each vertex up to ±amount (metres), then BEAUTY-triangulate: irregular planar facets.
    `key` (the part name) and `seed` make it repeatable per part."""
    rng = random.Random(zlib.crc32(key.encode()) + seed)
    for v in bm.verts:
        v.co += Vector((rng.uniform(-amount, amount), rng.uniform(-amount, amount), rng.uniform(-amount, amount)))
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    return bm


def finish_mesh(name, bm, material=None, collection=None, smooth=False):
    """bmesh → linked object: merged doubles, outward normals, flat faces, a per-face `facet`
    attribute (0–1, repeatable per name). Frees the bmesh."""
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
    (collection or bpy.context.scene.collection).objects.link(ob)
    if material is not None:
        ob.data.materials.append(material)
    return ob
