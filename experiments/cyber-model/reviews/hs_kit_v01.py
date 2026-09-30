"""Hard-surface part builders for cyber-model. Lengths in the API are millimetres; meshes are metres.

Import from build.py:  from hs_kit import *
Everything here builds real geometry from numbers, so a part can be moved or resized from P.
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

MM = 0.001


def mm(v):
    return v * MM


# ---------------------------------------------------------------- 2D outlines

def rounded_outline(pts, radius, seg=5):
    """Round every corner of a closed polygon (mm points). radius: one number or a list per point."""
    n = len(pts)
    rs = radius if isinstance(radius, (list, tuple)) else [radius] * n
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        r = rs[i]
        if r <= 1e-6:
            out.append(tuple(p1))
            continue
        a, b = (p0 - p1), (p2 - p1)
        la, lb = a.length, b.length
        a.normalize()
        b.normalize()
        ang = math.acos(max(-1.0, min(1.0, a.dot(b))))
        if ang < 1e-3 or abs(ang - math.pi) < 1e-3:
            out.append(tuple(p1))
            continue
        t = min(r / math.tan(ang / 2), la * 0.5, lb * 0.5)
        rr = t * math.tan(ang / 2)
        c = p1 + (a + b).normalized() * (rr / math.sin(ang / 2))
        s = p1 + a * t
        e = p1 + b * t
        a0 = math.atan2(s.y - c.y, s.x - c.x)
        a1 = math.atan2(e.y - c.y, e.x - c.x)
        d = a1 - a0
        while d > math.pi:
            d -= 2 * math.pi
        while d < -math.pi:
            d += 2 * math.pi
        for k in range(seg + 1):
            q = a0 + d * k / seg
            out.append((c.x + rr * math.cos(q), c.y + rr * math.sin(q)))
    return out


def rect_outline(cx, cy, w, h, r=0.0, rot=0.0, seg=5):
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    if r:
        pts = rounded_outline(pts, r, seg)
    c, s = math.cos(rot), math.sin(rot)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]


def circle_outline(cx, cy, r, n=48):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def offset_outline(pts, d):
    """Inset (d < 0) or outset (d > 0) a convex-ish polygon by moving each edge; fine for plates."""
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n)) / 2
    sgn = 1 if area > 0 else -1
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        e0, e1 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n0 = Vector((e0.y, -e0.x)) * sgn
        n1 = Vector((e1.y, -e1.x)) * sgn
        bis = n0 + n1
        k = 1.0 + n0.dot(n1)
        out.append(tuple(p1 + bis * (d / k if k > 1e-4 else d)))
    return out


# ---------------------------------------------------------------- solids

def _to_obj(name, bm, coll):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def extrude_outline(name, outline_mm, z0_mm, h_mm, coll=None, holes=None):
    """A prism from a closed 2D outline (mm), floor at z0, height h. Flat n-gon caps."""
    bm = bmesh.new()
    vs = [bm.verts.new((x * MM, y * MM, z0_mm * MM)) for x, y in outline_mm]
    f = bm.faces.new(vs)
    if f.normal.z < 0:
        f.normal_flip()
    res = bmesh.ops.extrude_face_region(bm, geom=[f])
    top = [e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=(0, 0, h_mm * MM))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _to_obj(name, bm, coll)


def cylinder(name, r_mm, length_mm, centre_mm=(0, 0, 0), axis="Z", segs=48, coll=None, r2_mm=None, cap=True):
    """Cylinder or cone frustum along an axis (X, Y or Z), centred on centre_mm."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=segs,
                          radius1=r_mm * MM, radius2=(r2_mm if r2_mm is not None else r_mm) * MM,
                          depth=length_mm * MM)
    if axis == "X":
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "Y"))
    elif axis == "Y":
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(-math.pi / 2, 3, "X"))
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(centre_mm) * MM)
    return _to_obj(name, bm, coll)


def box(name, size_mm, centre_mm, coll=None, rot_z=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size_mm[0] * MM
        v.co.y *= size_mm[1] * MM
        v.co.z *= size_mm[2] * MM
    if rot_z:
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(rot_z, 3, "Z"))
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(centre_mm) * MM)
    return _to_obj(name, bm, coll)


def gear(name, teeth, r_out_mm, r_root_mm, thick_mm, z0_mm=0.0, centre=(0, 0), coll=None, tooth_frac=0.5):
    """Spur gear prism: trapezoid teeth. Axis Z."""
    pts = []
    for i in range(teeth):
        a = 2 * math.pi * i / teeth
        step = 2 * math.pi / teeth
        w = step * tooth_frac
        for ang, r in ((a - w * 0.5, r_root_mm), (a - w * 0.3, r_out_mm), (a + w * 0.3, r_out_mm), (a + w * 0.5, r_root_mm)):
            pts.append((centre[0] + r * math.cos(ang), centre[1] + r * math.sin(ang)))
    return extrude_outline(name, pts, z0_mm, thick_mm, coll)


def knurled_cylinder(name, r_mm, length_mm, ridges, ridge_depth_mm, centre_mm, axis="Z", coll=None):
    """Cylinder with straight ridges; the profile is a gear outline extruded along the axis."""
    pts = []
    for i in range(ridges):
        a = 2 * math.pi * i / ridges
        step = 2 * math.pi / ridges
        for ang, r in ((a - step * 0.28, r_mm - ridge_depth_mm), (a - step * 0.16, r_mm),
                       (a + step * 0.16, r_mm), (a + step * 0.28, r_mm - ridge_depth_mm)):
            pts.append((r * math.cos(ang), r * math.sin(ang)))
    ob = extrude_outline(name, pts, -length_mm / 2, length_mm, coll)
    if axis == "X":
        ob.rotation_euler = (0, math.pi / 2, 0)
    elif axis == "Y":
        ob.rotation_euler = (-math.pi / 2, 0, 0)
    ob.location = Vector(centre_mm) * MM
    return ob


def tube(name, p0_mm, p1_mm, r0_mm, r1_mm=None, segs=48, coll=None, cap=True):
    """Cylinder or cone frustum between two 3D points (mm). r0 at p0, r1 at p1."""
    p0, p1 = Vector(p0_mm), Vector(p1_mm)
    d = p1 - p0
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=segs, radius1=r0_mm * MM,
                          radius2=(r1_mm if r1_mm is not None else r0_mm) * MM, depth=d.length * MM)
    rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    bmesh.ops.transform(bm, verts=bm.verts, matrix=rot, space=Matrix.Identity(4))
    bmesh.ops.translate(bm, verts=bm.verts, vec=((p0 + p1) / 2) * MM)
    return _to_obj(name, bm, coll)


def bake_transform(ob):
    me = ob.data
    me.transform(ob.matrix_basis)
    ob.matrix_basis = Matrix.Identity(4)


# ---------------------------------------------------------------- edges and normals

def _ctx(ob):
    return bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob],
                                     selected_editable_objects=[ob])


def weight_edges(ob, top=1.0, vert=0.35, min_deg=35.0):
    """Write bevel weights by edge class, so plates get a soft shoulder on the top rim, a small break on
    vertical corners and no bevel on the foot (the reference shows a black crease there).

    Top rim = a top face meeting a wall, convex. Pocket floors (concave), bottom edges and the short arc
    edges of rounded corners (under min_deg between faces) get 0. Run it after the booleans.
    Advisor (Opus) point: one angle-limited width on every edge makes plates read as soft bricks.
    """
    import bmesh
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    lay = bm.edges.layers.float.get("bevel_weight_edge") or bm.edges.layers.float.new("bevel_weight_edge")
    for e in bm.edges:
        w = 0.0
        if len(e.link_faces) == 2:
            n1, n2 = e.link_faces[0].normal, e.link_faces[1].normal
            up1, up2 = abs(n1.z) > 0.9, abs(n2.z) > 0.9
            if up1 != up2 and e.is_convex:
                w = top if (n1.z if up1 else n2.z) > 0 else 0.0
            elif not up1 and not up2 and e.is_convex and n1.angle(n2) > math.radians(min_deg):
                w = vert
        e[lay] = w
    bm.to_mesh(me)
    bm.free()


def hard_edges(ob, width_mm=0.5, segments=2, angle_deg=28, smooth_deg=30, weighted=False, edge_material=-1):
    """Bevel, then keep flat faces flat.

    Research (agent A, 5.2 test): Bevel with Harden Normals, then Smooth by Angle, leaves big faces
    exactly flat (normal error 0.000). Weighted Normal measured worse and is not used.
    weighted=True bevels by the edge weights from weight_edges(); otherwise by angle.
    edge_material: slot index for the generated bevel faces (a separate 'worn edge' material).
    The stack stays live: baking and re-smoothing raises the error (see RESEARCH.md).
    """
    for p in ob.data.polygons:
        p.use_smooth = True
    bv = ob.modifiers.new("Bevel", "BEVEL")
    bv.width = width_mm * MM
    bv.segments = segments
    bv.limit_method = "WEIGHT" if weighted else "ANGLE"
    bv.angle_limit = math.radians(angle_deg)
    bv.miter_outer = "MITER_SHARP"
    bv.use_clamp_overlap = True
    bv.harden_normals = True
    bv.material = edge_material
    with _ctx(ob):
        bpy.ops.object.shade_auto_smooth(angle=math.radians(smooth_deg))
    return ob


def ring_cutter(name, outline_mm, inset_mm, width_mm, z0_mm, z1_mm):
    """A closed groove: the band between two inset copies of an outline. Overshoot z1 above the surface."""
    outer = extrude_outline(name, offset_outline(outline_mm, -inset_mm), z0_mm, z1_mm - z0_mm)
    inner = extrude_outline(name + "_in", offset_outline(outline_mm, -(inset_mm + width_mm)), z0_mm - 1, z1_mm - z0_mm + 2)
    m = outer.modifiers.new("d", "BOOLEAN")
    m.operation, m.operand_type, m.object, m.solver = "DIFFERENCE", "OBJECT", inner, "EXACT"
    with _ctx(outer):
        bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(inner, do_unlink=True)
    outer.data.materials.clear()
    return outer


def join(objs, name):
    """Join objects into the first one (used to merge cutters so one Exact boolean does the job)."""
    base = objs[0]
    with bpy.context.temp_override(object=base, active_object=base, selected_objects=list(objs),
                                   selected_editable_objects=list(objs)):
        bpy.ops.object.join()
    base.name = name
    return base


def cut(target, cutters, solver="EXACT"):
    """One boolean difference with all cutters joined first. Cutters must overshoot the surface."""
    cutters = [c for c in cutters if c is not None]
    if not cutters:
        return target
    cutter = join(cutters, "cutter") if len(cutters) > 1 else cutters[0]
    m = target.modifiers.new("Cut", "BOOLEAN")
    m.operation, m.operand_type, m.object, m.solver = "DIFFERENCE", "OBJECT", cutter, solver
    with _ctx(target):
        bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    target.data.materials.clear()   # the boolean adds an empty slot 0; a later append would land in slot 1
    return target


# ---------------------------------------------------------------- cord

def helix_cord(name, path_mm, coil_r_mm, wire_r_mm, turns, coll=None, pts_per_turn=28, ramp_mm=8.0, wobble=0.0):
    """A coiled cord: a helix wrapped around a polyline path (mm 3D points). Returns a curve object.
    The coil radius ramps smoothly from 0 over ramp_mm at both ends, so straight leads join the tube."""
    path = [Vector(p) for p in path_mm]
    seglen = [(path[i + 1] - path[i]).length for i in range(len(path) - 1)]
    total = sum(seglen)
    n = int(turns * pts_per_turn)

    def at(s):
        s = max(0.0, min(total, s))
        acc = 0.0
        for i, L in enumerate(seglen):
            if s <= acc + L or i == len(seglen) - 1:
                t = (s - acc) / L if L else 0.0
                return path[i].lerp(path[i + 1], min(1.0, t)), (path[i + 1] - path[i]).normalized()
            acc += L

    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = wire_r_mm * MM
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(n)
    up = Vector((0, 0, 1))
    for i in range(n + 1):
        s = total * i / n
        c, tan = at(s)
        nrm = tan.cross(up)
        if nrm.length < 1e-4:
            nrm = tan.cross(Vector((0, 1, 0)))
        nrm.normalize()
        bn = tan.cross(nrm).normalized()
        a = 2 * math.pi * turns * i / n
        e = min(s, total - s) / max(ramp_mm, 1e-6)
        e = max(0.0, min(1.0, e))
        rr = coil_r_mm * (e * e * (3 - 2 * e)) * (1.0 + wobble * math.sin(a * 0.37 + 1.3))
        p = c + nrm * (rr * math.cos(a)) + bn * (rr * math.sin(a))
        sp.points[i].co = (p.x * MM, p.y * MM, p.z * MM, 1.0)
    ob = bpy.data.objects.new(name, cu)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob
