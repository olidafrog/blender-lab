"""Build wonder_logos.blend: each SVG as a flat curve plus a live Extrude modifier.

    tools/blender.sh library/models/wonder-logos/build_logos.py [--set key=value ...]

Each logo is one curve object. A geometry-nodes modifier fills it with n-gon caps
and extrudes it. Depth and Curve Resolution stay editable in the modifier panel.
Straight SVG segments get vector handles, so they evaluate to one edge with no
extra vertices. Apply the modifier when you want a mesh to bevel.
"""
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent

P = {
    "depth": 0.1,         # extrude depth in metres (10 px at the scale below)
    "resolution": 6,      # vertices per curved segment
    "px_per_m": 100.0,    # SVG units per metre; both logos share it so sizes match
    "straight_tol": 1e-3, # handle-to-chord distance (m) under which a segment counts as straight
}

LOGOS = {
    "wonder_logomark": HERE / "logomark" / "logomark-Light.svg",
    "wonder_logotype": HERE / "logotype" / "logotype-Light.svg",
}


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    for i, a in enumerate(argv):
        if a == "--set":
            k, v = argv[i + 1].split("=", 1)
            P[k] = type(P[k])(v)


def import_svg(path):
    """Import an SVG and return its curve objects."""
    before = set(bpy.data.objects)
    bpy.ops.import_curve.svg(filepath=str(path))
    return [o for o in bpy.data.objects if o not in before and o.type == "CURVE"]


def is_straight(a, b, tol):
    """True when both handles of segment a->b lie on the chord."""
    chord = b.co - a.co
    L = chord.length
    if L < 1e-9:
        return True
    d = chord / L
    for h, origin in ((a.handle_right, a.co), (b.handle_left, b.co)):
        v = h - origin
        if (v - d * v.dot(d)).length > tol:
            return False
    return True


def rebuild_spline(cu, sp, tol):
    """Rewrite a spline without the duplicate closing point and with vector handles on straights."""
    pts = [(p.co.copy(), p.handle_left.copy(), p.handle_right.copy()) for p in sp.bezier_points]
    if len(pts) > 2 and (pts[-1][0] - pts[0][0]).length < 1e-6:
        pts[0] = (pts[0][0], pts[-1][1], pts[0][2])
        pts.pop()
    cu.splines.remove(sp)
    new = cu.splines.new("BEZIER")
    new.bezier_points.add(len(pts) - 1)
    new.use_cyclic_u = True
    for bp, (co, hl, hr) in zip(new.bezier_points, pts):
        bp.handle_left_type = bp.handle_right_type = "FREE"
        bp.co, bp.handle_left, bp.handle_right = co, hl, hr
    n = len(new.bezier_points)
    straight = 0
    for i in range(n):
        a, b = new.bezier_points[i], new.bezier_points[(i + 1) % n]
        if is_straight(a, b, tol):
            a.handle_right_type = "VECTOR"
            b.handle_left_type = "VECTOR"
            straight += 1
    return n, straight


def extrude_group():
    ng = bpy.data.node_groups.new("Extrude Logo", "GeometryNodeTree")
    iface = ng.interface
    iface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    s = iface.new_socket("Depth", in_out="INPUT", socket_type="NodeSocketFloat")
    s.default_value, s.min_value, s.max_value, s.subtype = P["depth"], 0.0, 10.0, "DISTANCE"
    s = iface.new_socket("Curve Resolution", in_out="INPUT", socket_type="NodeSocketInt")
    s.default_value, s.min_value, s.max_value = P["resolution"], 1, 64
    s.description = "Vertices per curved segment. Straight edges always stay one edge"
    iface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")

    N = ng.nodes
    gi = N.new("NodeGroupInput")
    go = N.new("NodeGroupOutput")
    res = N.new("GeometryNodeSetSplineResolution")
    fill = N.new("GeometryNodeFillCurve")
    if "Mode" in fill.inputs:  # 5.x: menu socket
        fill.inputs["Mode"].default_value = "N-gons"
    else:                      # 4.x: node property
        fill.mode = "NGONS"
    ext = N.new("GeometryNodeExtrudeMesh")
    ext.mode = "FACES"
    ext.inputs["Offset"].default_value = (0, 0, 1)
    ext.inputs["Individual"].default_value = False
    # Extrude Mesh moves the cap up and leaves the bottom open; add a flipped copy as the base.
    flip = N.new("GeometryNodeFlipFaces")
    join = N.new("GeometryNodeJoinGeometry")
    merge = N.new("GeometryNodeMergeByDistance")

    L = ng.links
    L.new(gi.outputs["Geometry"], res.inputs["Geometry"])
    L.new(gi.outputs["Curve Resolution"], res.inputs["Resolution"])
    L.new(res.outputs["Geometry"], fill.inputs["Curve"])
    L.new(fill.outputs["Mesh"], ext.inputs["Mesh"])
    L.new(gi.outputs["Depth"], ext.inputs["Offset Scale"])
    L.new(fill.outputs["Mesh"], flip.inputs["Mesh"])
    L.new(ext.outputs["Mesh"], join.inputs["Geometry"])
    L.new(flip.outputs["Mesh"], join.inputs["Geometry"])
    L.new(join.outputs["Geometry"], merge.inputs["Geometry"])
    L.new(merge.outputs["Geometry"], go.inputs["Geometry"])
    for i, n in enumerate((gi, res, fill, ext, join, merge, go)):
        n.location = (i * 220, 0)
    flip.location = (3 * 220, -200)
    return ng


def main():
    parse_args()
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)

    ng = extrude_group()
    col = bpy.context.scene.collection
    x = 0.0
    for name, path in LOGOS.items():
        parts = import_svg(path)
        # Join every path of this logo into one curve object.
        bpy.ops.object.select_all(action="DESELECT")
        for o in parts:
            o.select_set(True)
        bpy.context.view_layer.objects.active = parts[0]
        bpy.ops.object.join()
        obj = bpy.context.view_layer.objects.active
        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        col.objects.link(obj)

        cu = obj.data
        obj.name = cu.name = name
        cu.materials.clear()
        cu.dimensions = "3D"       # 2D curves refuse transform_apply; set back to 2D below
        cu.extrude = cu.bevel_depth = 0.0
        cu.resolution_u = P["resolution"]

        # Bake the importer's scale into the points, then rescale to px_per_m.
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        svg_w = float(path.read_text().split('width="', 1)[1].split('"', 1)[0])
        xs = [p.co.x for sp in cu.splines for p in sp.bezier_points]
        k = (svg_w / P["px_per_m"]) / (max(xs) - min(xs)) if name == "wonder_logotype" else None
        if k is None:  # logomark path spans 124 of its 128 px; measure against the viewBox
            k = (126.003 - 2.003) / P["px_per_m"] / (max(xs) - min(xs))
        obj.scale = (k, k, k)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        # Centre the outline on the object origin.
        pts = [p.co for sp in cu.splines for p in sp.bezier_points]
        cx = (min(p.x for p in pts) + max(p.x for p in pts)) / 2
        cy = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
        for sp in cu.splines:
            for p in sp.bezier_points:
                p.co.x -= cx; p.co.y -= cy
                p.handle_left.x -= cx; p.handle_left.y -= cy
                p.handle_right.x -= cx; p.handle_right.y -= cy

        total = straight = 0
        for sp in list(cu.splines):
            n, s = rebuild_spline(cu, sp, P["straight_tol"])
            total += n; straight += s
        cu.dimensions = "2D"
        cu.fill_mode = "NONE"      # the modifier does the filling

        mod = obj.modifiers.new("Extrude", "NODES")
        mod.node_group = ng

        w = max(p.co.x for sp in cu.splines for p in sp.bezier_points) * 2
        obj.location = (x + w / 2, 0, 0)
        x += w + 0.5
        print(f"[out] {name}: {len(cu.splines)} splines, {total} points, {straight} straight segments")

    for m in list(bpy.data.materials):
        if m.users == 0:
            bpy.data.materials.remove(m)

    # Report the evaluated mesh so we can check it is closed and minimal.
    import bmesh
    dg = bpy.context.evaluated_depsgraph_get()
    for name in LOGOS:
        ev = bpy.data.objects[name].evaluated_get(dg)
        bm = bmesh.new()
        bm.from_mesh(ev.to_mesh())
        nm = sum(1 for e in bm.edges if not (e.is_manifold and e.is_contiguous))
        tris = sum(1 for f in bm.faces if len(f.verts) == 3)
        dims = [max(v.co[i] for v in bm.verts) - min(v.co[i] for v in bm.verts) for i in range(3)]
        bm.normal_update()
        up = sum(1 for f in bm.faces if f.normal.z > 0.99 and f.calc_center_median().z > 1e-4)
        print(f"[out] {name}: {len(bm.verts)} verts, {len(bm.faces)} faces ({tris} tris), "
              f"{nm} non-manifold edges, {up} top caps facing up, size {dims[0]:.3f} x {dims[1]:.3f} x {dims[2]:.3f} m")
        bm.free()

    out = HERE / "wonder_logos.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out))
    print(f"[out] WROTE {out}")


main()
