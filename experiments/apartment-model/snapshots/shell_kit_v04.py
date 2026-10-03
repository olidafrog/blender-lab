"""Shell kit: walls with openings, boxes, arched frames and glazing bars, in metres.

Scene frame = the aligned scan: x along the room (window wall at x < 0), y across (west < 0), z up, floor 0.
A wall "in plane x" is perpendicular to x: its 2D outline is drawn in (u, v) = (y, z) and extruded along x.
A wall "in plane y" uses (u, v) = (x, z) and is extruded along y.
"""
import math

import bmesh
import bpy
import numpy as np

COLL = {}


def coll(name):
    if name not in COLL:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
        COLL[name] = c
    return COLL[name]


def link(ob, collection):
    coll(collection).objects.link(ob)
    return ob


def _finish(name, me, mat, collection):
    if mat is not None:
        me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = False
    assert len(me.polygons) > 0, f"empty mesh {name}"
    return link(bpy.data.objects.new(name, me), collection)


def box(name, x0, x1, y0, y1, z0, z1, mat, collection="Shell"):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    me = bpy.data.meshes.new(name)
    v = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    f = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    me.from_pydata(v, [], f)
    return _finish(name, me, mat, collection)


def prism(name, loop, a0, a1, plane, mat, collection="Shell"):
    """A convex or concave polygon (u, v) without holes, extruded from a0 to a1 along the plane's axis."""
    return wall(name, loop, [], a0, a1, plane, mat, collection)


def wall(name, outer, holes, a0, a1, plane, mat, collection="Shell"):
    """Filled outline with holes, extruded between a0 and a1 along x (plane="x") or y (plane="y")."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    for lp in [outer, *holes]:
        sp = cu.splines.new("POLY")
        sp.points.add(len(lp) - 1)
        for p, (u, v) in zip(sp.points, lp):
            p.co = (u, v, 0, 1)
        sp.use_cyclic_u = True
    a0, a1 = sorted((a0, a1))
    cu.extrude = (a1 - a0) / 2
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    u, v, w = co[:, 0], co[:, 1], co[:, 2] + (a0 + a1) / 2
    if plane == "x":
        new = np.stack([w, u, v], 1)              # cyclic permutation: orientation kept
    else:
        new = np.stack([u, w, v], 1)              # a swap: flip the faces after
    me.vertices.foreach_set("co", new.ravel())
    if plane == "y":
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
        bm.to_mesh(me); bm.free()
    me.update()
    return _finish(name, me, mat, collection)


def rect(u0, v0, u1, v1):
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


def seg_arch(cu, hw, spring, rise):
    """Segmental arch over the chord (cu - hw, cu + hw) at height `spring`: (centre_v, radius, half-angle)."""
    R = (hw * hw + rise * rise) / (2 * rise)
    cv = spring + rise - R
    return cv, R, math.asin(hw / R)


def arch_loop(cu, hw, sill, spring, rise, n=32):
    """Opening outline: a rectangle from the sill to the spring with a segmental arch on top."""
    cv, R, th = seg_arch(cu, hw, spring, rise)
    # counter-clockwise: along the sill, up the right jamb, over the arch from right to left
    arc = [(cu + R * math.sin(th - 2 * th * i / n), cv + R * math.cos(th - 2 * th * i / n)) for i in range(n + 1)]
    return [(cu - hw, sill), (cu + hw, sill)] + arc


def arch_top(cu, hw, spring, rise, u):
    """Height of the arch at u (for clipping glazing bars)."""
    cv, R, _ = seg_arch(cu, hw, spring, rise)
    return cv + math.sqrt(max(R * R - (u - cu) ** 2, 0.0))


def inset_arch(cu, hw, sill, spring, rise, t):
    """The same opening shrunk by t on every side (the arch keeps its centre, radius - t)."""
    cv, R, _ = seg_arch(cu, hw, spring, rise)
    hw2 = hw - t
    top2 = cv + (R - t)                            # crown lowered by t
    spring2 = cv + math.sqrt((R - t) ** 2 - hw2 ** 2)
    return cu, hw2, sill + t, spring2, top2 - spring2


def bar_v(name, u, w, v0, v1, a0, a1, plane, mat, collection):
    return prism(name, rect(u - w / 2, v0, u + w / 2, v1), a0, a1, plane, mat, collection)


def bar_h(name, v, w, u0, u1, a0, a1, plane, mat, collection):
    return prism(name, rect(u0, v - w / 2, u1, v + w / 2), a0, a1, plane, mat, collection)


def join(objs, name):
    """Join objects into one (fewer objects, one control per material later)."""
    objs = [o for o in objs if o is not None]
    if len(objs) == 1:
        objs[0].name = name
        return objs[0]
    ctx = {"active_object": objs[0], "selected_editable_objects": objs, "object": objs[0]}
    with bpy.context.temp_override(**ctx):
        bpy.ops.object.join()
    objs[0].name = name
    return objs[0]
