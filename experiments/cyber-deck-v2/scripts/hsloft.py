"""Plan x section loft: a closed plan outline swept by a designed cross-section, capped, watertight,
with analytic custom normals (exact fillet shading at low segment counts).

Units: mm in, metres out.
  outline = plan_outline([(x, y, r), ...])          # per-corner radius, r=0 sharp
  sec     = section_slab(h=14, top=('fillet', 4), bottom=('chamfer', .8), draft=3)
  obj     = hs_loft('shell', outline, sec)
Rule: every inset in the section must stay below the smallest CONVEX corner radius
(outward overhangs below the smallest CONCAVE radius) or the offset ring self-intersects.
"""
import math

import bmesh
import bpy
from mathutils import Vector

MM = 0.001


# ------------------------------------------------------------------ plan
def plan_outline(corners, seg_per_90=12):
    """corners: [(x, y, r)] CCW, mm. Returns [(Vector2 p, Vector2 n or None)]: n = exact outward
    normal on arcs/lines (smooth), None at sharp corners (r=0)."""
    n = len(corners)
    out = []
    for i in range(n):
        p0 = Vector(corners[i - 1][:2]); p1 = Vector(corners[i][:2]); p2 = Vector(corners[(i + 1) % n][:2])
        r = corners[i][2]
        a = (p0 - p1).normalized(); b = (p2 - p1).normalized()
        ang = math.acos(max(-1, min(1, a.dot(b))))
        if r <= 1e-6 or ang < 1e-3 or abs(ang - math.pi) < 1e-3:
            out.append((p1, None))
            continue
        t = r / math.tan(ang / 2)
        c = p1 + (a + b).normalized() * (r / math.sin(ang / 2))
        s = p1 + a * t; e = p1 + b * t
        a0 = math.atan2(s.y - c.y, s.x - c.x); a1 = math.atan2(e.y - c.y, e.x - c.x)
        d = a1 - a0
        while d > math.pi: d -= 2 * math.pi
        while d < -math.pi: d += 2 * math.pi
        convex = d > 0  # CCW outline: convex corners turn left
        k = max(2, int(math.ceil(abs(d) / (math.pi / 2) * seg_per_90)))
        for j in range(k + 1):
            q = a0 + d * j / k
            rad = Vector((math.cos(q), math.sin(q)))
            out.append((c + rad * r, rad if convex else -rad))
    return out


def _offset(outline, o):
    """Move each plan vertex outward by o (mm, negative = inset)."""
    n = len(outline)
    pts = []
    for i, (p, nrm) in enumerate(outline):
        if nrm is not None:
            pts.append(p + nrm * o)
            continue
        p0 = outline[i - 1][0]; p2 = outline[(i + 1) % n][0]
        e0 = (p - p0).normalized(); e1 = (p2 - p).normalized()
        n0 = Vector((e0.y, -e0.x)); n1 = Vector((e1.y, -e1.x))
        bis = (n0 + n1).normalized()
        pts.append(p + bis * (o / max(0.2, bis.dot(n0))))
    return pts


# ------------------------------------------------------------------ section
# A section is [(o, z, n)] from the bottom-outer point to the top-inner point.
# o = outset from the plan outline (mm, negative = inset), z = height (mm),
# n = exact 2D normal (no, nz) for a smooth station, None for a crisp edge.

def arc(o_c, z_c, r, a0, a1, segs):
    """Quarter-ish arc in section space centred (o_c, z_c); angles in degrees, 0 = outward."""
    pts = []
    for j in range(segs + 1):
        q = math.radians(a0 + (a1 - a0) * j / segs)
        nn = (math.cos(q), math.sin(q))
        pts.append((o_c + r * nn[0], z_c + r * nn[1], nn))
    return pts


def section_slab(h, top=('fillet', 3.0), bottom=('chamfer', 0.6), draft=0.0, segs=8):
    """Bottom edge -> drafted wall -> top edge. top/bottom: ('fillet', r) | ('chamfer', c) | ('sharp', 0).
    draft in degrees (wall leans in going up)."""
    tdr = math.tan(math.radians(draft))
    wall_n = (math.cos(math.radians(draft)), math.sin(math.radians(draft)))
    sec = []
    kind, b = bottom
    if kind == 'fillet' and b > 0:
        sec += arc(-b, b, b, -90, 0, max(2, segs // 2))
        sec[0] = (sec[0][0], sec[0][1], None)  # base sits on the floor: crisp
    elif kind == 'chamfer' and b > 0:
        sec += [(-b, 0, None), (0, b, None)]
    else:
        sec += [(0, 0, None)]
    kind, t = top
    zt = h - (t if kind != 'sharp' else 0)
    ow = -tdr * zt  # wall top outset
    if kind == 'fillet' and t > 0:
        sec += arc(ow - t, zt, t, math.degrees(math.atan2(wall_n[1], wall_n[0])), 90, segs)
    elif kind == 'chamfer' and t > 0:
        sec += [(ow, zt, None), (ow - t, h, None)]
    else:
        sec += [(ow, h, None)]
    return sec


# ------------------------------------------------------------------ loft
def hs_loft(name, outline, section, coll=None, cap_bottom=True, cap_top=True, custom_normals=True):
    n = len(outline)
    rings = [_offset(outline, o) for (o, z, _) in section]
    bm = bmesh.new()
    V = [[bm.verts.new((p.x * MM, p.y * MM, z * MM)) for p in ring] for ring, (_, z, _) in zip(rings, section)]
    faces = []
    for k in range(len(section) - 1):
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new((V[k][i], V[k][j], V[k + 1][j], V[k + 1][i]))
            faces.append(('side', k, i, f))
    if cap_top:
        faces.append(('top', 0, 0, bm.faces.new(V[-1])))
    if cap_bottom:
        faces.append(('bot', 0, 0, bm.faces.new(list(reversed(V[0])))))
    bm.normal_update()
    # orientation: outline is CCW so side quads face outward already
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    me.shade_smooth()
    if custom_normals == 'flatcap':
        # boolean-safe shading: caps flat, sweep smooth, crisp section stations and sharp plan corners marked sharp
        for (kind, k, i, f), poly in zip(faces, me.polygons):
            if kind in ('top', 'bot'):
                poly.use_smooth = False
        crisp_k = {k for k, st in enumerate(section) if st[2] is None}
        crisp_i = {i for i, (p, nn) in enumerate(outline) if nn is None}
        for ed in me.edges:
            a_, b_ = ed.vertices
            ka, ia = divmod(a_, n); kb, ib = divmod(b_, n)
            if (ka == kb and ka in crisp_k) or (ia == ib and ia in crisp_i):
                ed.use_edge_sharp = True
        bm.free()
        return ob
    if not custom_normals:
        me.set_sharp_from_angle(angle=math.radians(35))
        bm.free()
        return ob

    # analytic per-corner normals
    def plan_n(i, edge_i):
        nrm = outline[i][1]
        if nrm is not None:
            return nrm
        a = outline[edge_i][0]; b = outline[(edge_i + 1) % n][0]
        e = (b - a).normalized()
        return Vector((e.y, -e.x))

    def sec_n(k, seg_k):
        nn = section[k][2]
        if nn is not None:
            return Vector(nn)
        o0, z0, _ = section[seg_k]; o1, z1, _ = section[seg_k + 1]
        t = Vector((o1 - o0, z1 - z0)).normalized()
        return Vector((t.y, -t.x))  # outward/up for a bottom->top, outer->inner walk

    loop_normals = [None] * len(me.loops)
    for (kind, k, i, f), poly in zip(faces, me.polygons):
        for li in poly.loop_indices:
            if kind == 'top':
                loop_normals[li] = (0, 0, 1); continue
            if kind == 'bot':
                loop_normals[li] = (0, 0, -1); continue
            vi = me.loops[li].vertex_index
            kk, ii = divmod(vi, n)
            pn = plan_n(ii, i); sn = sec_n(kk, k)
            v = Vector((pn.x * sn.x, pn.y * sn.x, sn.y)).normalized()
            loop_normals[li] = tuple(v)
    if custom_normals in ('free', 'free_cutter'):
        # 4.5+ "free" storage: a plain FLOAT_VECTOR corner attribute; booleans interpolate it like
        # any attribute. Cutters store it negated: in a DIFFERENCE their faces flip into the host.
        sgn = -1.0 if custom_normals == 'free_cutter' else 1.0
        at = me.attributes.new('custom_normal', 'FLOAT_VECTOR', 'CORNER')
        at.data.foreach_set('vector', [c * sgn for v in loop_normals for c in v])
    else:
        me.normals_split_custom_set(loop_normals)
    bm.free()
    return ob


def circle(cx, cy, r, n=48):
    """Circle plan outline with exact normals."""
    out = []
    for k in range(n):
        q = 2 * math.pi * k / n
        d = Vector((math.cos(q), math.sin(q)))
        out.append((Vector((cx, cy)) + d * r, d))
    return out


def section_cutter(depth, top_z, rim=('fillet', 1.0), floor=('fillet', 0.5), segs=6, over=4.0, draft=0.0):
    """Section for a POCKET cutter whose boolean leaves a designed rim and floor on the host.
    Host top at top_z; pocket floor at top_z - depth. The rim arc stops 2 deg short of horizontal
    and then rises straight up by `over`, so nothing is coplanar with the host top."""
    zf = top_z - depth
    sec = []
    k, f = floor
    if k == 'fillet' and f > 0:
        sec += [(-f, zf, None)] if False else []
        sec += arc(-f, zf + f, f, -90, 0, max(2, segs // 2))
    elif k == 'chamfer' and f > 0:
        sec += [(-f, zf, None), (0, zf + f, None)]
    else:
        sec += [(0, zf, None)]
    # the cutter's bottom cap is the pocket floor; its inner start point is at o=-f
    k, r = rim
    if k == 'fillet' and r > 0:
        # host fillet centred (o=+r, z=top-r); cutter follows it: phi 180 -> 92 deg
        pts = []
        for j in range(segs + 1):
            ph = math.radians(180 - (180 - 92) * j / segs)
            nn = (math.cos(ph), math.sin(ph))
            # cutter normal points out of the cutter = into the host fillet centre direction reversed
            pts.append((r + r * nn[0], top_z - r + r * nn[1], (-nn[0], -nn[1])))
        sec += pts
        sec += [(pts[-1][0], top_z + over, None)]
    elif k == 'chamfer' and r > 0:
        sec += [(0, top_z - r, None), (r + 0.02, top_z + 0.02, None), (r + 0.02, top_z + over, None)]
    else:
        sec += [(0, top_z + over, None)]
    return sec


def hs_ring(name, outline, closed_section, coll=None):
    """Sweep a CLOSED section (list of (o, z)) round a closed plan outline: watertight torus-like
    solid, e.g. a panel-line groove cutter. Flat-shaded (it is only a cutter)."""
    n = len(outline); m = len(closed_section)
    rings = [_offset(outline, o) for (o, z) in closed_section]
    bm = bmesh.new()
    V = [[bm.verts.new((p.x * MM, p.y * MM, z * MM)) for p in ring] for ring, (o, z) in zip(rings, closed_section)]
    for k in range(m):
        kk = (k + 1) % m
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((V[k][i], V[k][j], V[kk][j], V[kk][i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def hs_slab(name, corners, height, top_fillet=3.0, bottom_chamfer=0.6, draft_deg=2.0, segs=8,
            z0=0.0, top_kind='fillet', shading='flatcap', coll=None):
    """Drop-in: a moulded slab from plan corners [(x, y, r_mm)] (CCW, mm). top_kind 'fillet'|'chamfer'|'sharp'.
    shading 'flatcap' is boolean-safe; 'analytic' = exact custom normals (only if no booleans follow)."""
    sec = section_slab(height, top=(top_kind, top_fillet), bottom=('chamfer', bottom_chamfer), draft=draft_deg, segs=segs)
    ob = hs_loft(name, plan_outline(corners), sec, coll=coll,
                 custom_normals={'flatcap': 'flatcap', 'analytic': True}[shading])
    ob.location.z = z0 * MM
    return ob
