"""Hard-surface kit for cyber-deck-v2: CAD-style parts as a plan outline lofted through a designed section.

A part = plan outline (corner points + a fillet radius per corner, mm) x section (a polyline in (inset, z)
with a fillet radius per corner, mm). Each section station becomes one offset copy of the outline; rings are
joined with quads and capped with flat n-gons. This is Fusion's "sketch, extrude, fillet" in code: the section
carries the foot chamfer, the wall, the slope and the top fillet, so steps read as moulded, not extruded
(RESEARCH.md; v1 used vertical walls and a 0.5 mm chamfer).

Faces in stations marked "wear" (the convex top fillet) get the FACE attribute "wear" = 1, which the polymer
shader reads for edge wear. Profiled cutters carry the host's rim fillet, so pockets need no Bevel modifier
(a Bevel after booleans clamps every edge of the mesh: RESEARCH.md).

Units: mm in, metres out (MM).
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

MM = 0.001
SOLVER = "MANIFOLD"          # MANIFOLD is fast; EXACT (use_self) is the fallback when a result looks wrong
LOG = []                     # (name, polys, note) of every cut, printed by the build


# ------------------------------------------------------------------ 2D helpers

def _area(pts):
    return sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
               for i in range(len(pts))) / 2


def _fillet(pts, radii, seg, closed=True):
    """Round each corner of a polyline with its radius, always seg+1 points per corner (rings stay
    compatible). Returns (points, flags): flag True for points inside an arc (smooth), False at a sharp
    corner or a polyline end. Radii are clamped to what the neighbouring edges allow."""
    n = len(pts)
    out, flags = [], []
    idx = range(n) if closed else range(1, n - 1)
    if not closed:
        out.append(Vector(pts[0])); flags.append(False)
    for i in idx:
        c = Vector(pts[i]); pa = Vector(pts[i - 1]); pb = Vector(pts[(i + 1) % n])
        a = pa - c; b = pb - c
        la, lb = a.length, b.length
        a.normalize(); b.normalize()
        ang = math.acos(max(-1.0, min(1.0, a.dot(b))))
        th = ang / 2
        r = radii[i]
        if r <= 1e-6 or th > math.radians(89.7) or th < 1e-3:
            out.extend(c.copy() for _ in range(seg + 1))
            flags.extend([False] * (seg + 1))
            continue
        t = r / math.tan(th)
        lim = 0.5 * min(la, lb) if closed else 0.98 * min(la if i == 1 else la / 2, lb if i == n - 2 else lb / 2)
        if t > lim:
            t = lim
            r = t * math.tan(th)
        A = c + a * t
        ctr = c + (a + b).normalized() * (r / math.sin(th))
        va = A - ctr
        vb = (c + b * t) - ctr
        sweep = math.atan2(va.x * vb.y - va.y * vb.x, va.dot(vb))
        for k in range(seg + 1):
            q = sweep * k / seg
            cq, sq = math.cos(q), math.sin(q)
            out.append(ctr + Vector((va.x * cq - va.y * sq, va.x * sq + va.y * cq)))
            flags.append(True)
    if not closed:
        out.append(Vector(pts[-1])); flags.append(False)
    return out, flags


def _offset_sharp(pts, d):
    """Miter offset of a CCW polygon, inward by d (negative = outward). Exact for straight edges.
    Returns points and a convex flag per corner."""
    n = len(pts)
    out, convex = [], []
    for i in range(n):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        t0 = (p1 - p0).normalized(); t1 = (p2 - p1).normalized()
        n0 = Vector((-t0.y, t0.x)); n1 = Vector((-t1.y, t1.x))
        out.append(p1 + d * (n0 + n1) / max(0.05, 1 + n0.dot(n1)))
        convex.append(t0.x * t1.y - t0.y * t1.x > 0)
    return out, convex


class Outline:
    """Plan outline: corner points (mm) and a fillet radius per corner (mm), CCW after construction."""

    def __init__(self, pts, radii, seg=10):
        if not isinstance(radii, (list, tuple)):
            radii = [radii] * len(pts)
        pts = [tuple(p) for p in pts]
        radii = list(radii)
        if _area(pts) < 0:
            pts.reverse(); radii.reverse()
        self.pts, self.radii, self.seg = pts, radii, seg

    def ring(self, d):
        """The outline offset inward by d mm, corners re-filleted with r - d (convex) or r + d (concave)."""
        off, convex = _offset_sharp(self.pts, d)
        rr = [max(r - d, 0.02) if cv else max(r + d, 0.02) for r, cv in zip(self.radii, convex)]
        rr = [0.0 if r0 <= 0 else r1 for r0, r1 in zip(self.radii, rr)]
        pts, flags = _fillet(off, rr, self.seg)
        return pts, flags

    @classmethod
    def auto(cls, pts, r_convex, r_concave, seg=10, sharp=(), sweep=40.0, sweep_turn=60.0):
        """Radius by corner type: r_convex on outer corners, r_concave on inner ones, 0 at indices in sharp.
        Shallow corners (turning less than sweep_turn degrees) get up to `sweep` mm, as much as the edges
        allow: a fixed small radius on a shallow bend makes a short arc that reads as a crease (review v03)."""
        o = cls(pts, 0.0, seg)
        _, convex = _offset_sharp(o.pts, 0.0)
        n = len(o.pts)
        radii = []
        for i, cv in enumerate(convex):
            r = r_convex if cv else r_concave
            p0, p1, p2 = Vector(o.pts[i - 1]), Vector(o.pts[i]), Vector(o.pts[(i + 1) % n])
            a, b = p0 - p1, p2 - p1
            turn = 180.0 - math.degrees(a.angle(b))
            if sweep and turn < sweep_turn:
                th = a.angle(b) / 2
                r = max(r, min(sweep, 0.45 * min(a.length, b.length) * math.tan(th)))
            radii.append(r)
        o.radii = radii
        flip = _area([tuple(p) for p in pts]) < 0
        for i in sharp:
            o.radii[(len(pts) - 1 - i) if flip else i] = 0.0
        return o

    def inset(self, d):
        """A new Outline offset inward by d mm (negative = outward), radii adjusted the same way."""
        off, convex = _offset_sharp(self.pts, d)
        rr = [0.0 if r <= 0 else (max(r - d, 0.05) if cv else max(r + d, 0.05)) for r, cv in zip(self.radii, convex)]
        return Outline([tuple(p) for p in off], rr, self.seg)

    def min_convex_radius(self):
        _, convex = _offset_sharp(self.pts, 0.0)
        rs = [r for r, cv in zip(self.radii, convex) if cv]
        return min(rs) if rs else 1e9


def circle(cx, cy, r, n=48):
    """A circle as an Outline (a regular polygon with its corners filleted to the circle)."""
    k = max(6, n // 6)
    R = r / math.cos(math.pi / k)
    pts = [(cx + R * math.cos(2 * math.pi * i / k), cy + R * math.sin(2 * math.pi * i / k)) for i in range(k)]
    return Outline(pts, [r * 0.999] * k, seg=max(2, n // k))


def rrect(cx, cy, w, h, r, rot_deg=0.0, seg=10):
    ca, sa = math.cos(math.radians(rot_deg)), math.sin(math.radians(rot_deg))
    pts = [(cx + x * ca - y * sa, cy + x * sa + y * ca)
           for x, y in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
    return Outline(pts, r, seg)


def toothed(cx, cy, r_root, r_tip, n, tip=0.4, root=0.4):
    """Trapezoid-tooth outline (gear, knurl): sharp corners."""
    pts = []
    p = 2 * math.pi / n
    fl = (1 - tip - root) / 2
    for k in range(n):
        a0 = p * k
        for f, r in ((0, r_root), (root, r_root), (root + fl, r_tip), (root + fl + tip, r_tip)):
            pts.append((cx + r * math.cos(a0 + f * p), cy + r * math.sin(a0 + f * p)))
    return Outline(pts, 0.0, seg=1)


# ------------------------------------------------------------------ sections
# A section is a list of stations (inset_mm, z_mm, flag) from the bottom-outer point to the top-inner
# point. flag: "crisp" (a sharp crease, marked sharp), "smooth" (inside a fillet), "wear" (inside the
# convex top fillet: edge wear goes here).

def section(pts, radii, seg=6, wear_from=None):
    """Polyline section with a fillet per corner. pts [(inset, z)] bottom-outer -> top-inner.
    wear_from: index of the corner whose fillet carries edge wear (default: the last corner)."""
    out, _ = _fillet([Vector(p) for p in pts], radii, seg, closed=False)
    wear_i = (len(pts) - 2) if wear_from is None else wear_from
    st = []
    # rebuild flags per corner block: [start] + (seg+1) per interior corner + [end]
    st.append((out[0].x, out[0].y, "crisp"))
    k = 1
    for ci in range(1, len(pts) - 1):
        r = radii[ci]
        block = out[k:k + seg + 1]
        k += seg + 1
        if r <= 1e-6:
            st.append((block[0].x, block[0].y, "crisp"))
            continue
        for j, p in enumerate(block):
            # wear only on the crest: the middle stations of the convex top fillet (review v01-v06: wear on the
            # whole fillet read as a chalky 15-25 px band; the reference has specks on the crest only)
            crest = 0.3 * seg <= j <= 0.7 * seg
            st.append((p.x, p.y, "wear" if (ci == wear_i and crest) else "smooth"))
    st.append((out[-1].x, out[-1].y, "crisp"))
    # drop repeated stations
    res = [st[0]]
    for s in st[1:]:
        if abs(s[0] - res[-1][0]) + abs(s[1] - res[-1][1]) > 1e-5:
            res.append(s)
    return res


def sec_slab(h, top_r=2.0, foot=0.6, draft=1.0, seg=6):
    """Vertical (drafted) wall, filleted top (the wear edge), small chamfer at the foot."""
    dw = math.tan(math.radians(draft)) * h
    if foot > 0:
        pts, rad = [(foot, 0.0), (0.0, foot), (dw, h), (dw + top_r * 3 + 1.0, h)], [0, 0, top_r, 0]
    else:
        pts, rad = [(0.0, 0.0), (dw, h), (dw + top_r * 3 + 1.0, h)], [0, top_r, 0]
    return _trim_top(section(pts, rad, seg))


def sec_step(h, wall_h, slope_deg=55.0, top_r=2.5, crease_r=0.8, foot=0.0, seg=6, under=None):
    """A moulded step: vertical wall to wall_h, then a slope (slope_deg from horizontal) up to h,
    a filleted crease between wall and slope, and a filleted top edge (the wear edge).
    under=(inset, z): an undercut. The part stands on a stem inset by `inset` up to z, so its lip
    overhangs and the camera sees a dark shadow line under it (reference: the S-step over the battery)."""
    run = (h - wall_h) / math.tan(math.radians(slope_deg))
    pts = [(0.0, 0.0), (0.0, wall_h), (run, h), (run + top_r * 3 + 1.0, h)]
    rad = [0, crease_r, top_r, 0]
    if under:
        ui, uz = under
        pts = [(ui, 0.0), (ui, uz), (0.0, uz)] + pts[1:]
        rad = [0, 0, 0.3] + rad[1:]
    elif foot > 0:
        pts = [(foot, 0.0), (0.0, foot)] + pts[1:]
        rad = [0, 0] + rad[1:]
    return _trim_top(section(pts, rad, seg))


def _trim_top(s):
    """The last station of the polyline is a helper far inside the top; the top cap is the ring at the
    fillet end, so drop the helper."""
    return s[:-1]


def sec_cutter(depth, top_z, rim_r=1.0, floor_r=0.5, over=4.0, seg=5, wall_deg=90.0):
    """Section for a pocket cutter. Stations are insets of the pocket's floor outline (negative = outside).
    Leaves on the host a pocket `depth` below top_z whose wall rises at wall_deg from horizontal (90 =
    vertical, 55 = a moulded sloped wall), with a filleted floor and a filleted rim. The rim arc stops
    3 degrees short of flat and then rises straight up, so nothing is coplanar with the host top.
    Geometry in (u, z) with u = outset: wall line u = (z - zf) / tan(wall)."""
    zf = top_z - depth
    al = math.radians(wall_deg)
    ta = math.tan(al) if wall_deg < 89.99 else 1e12
    nx, nz = math.sin(al), -math.cos(al)          # wall normal pointing into the host
    st = []
    if floor_r > 0:                               # cutter edge rounded: centre inside the cutter
        cz = zf + floor_r
        qz = cz + floor_r * nz
        qu = (qz - zf) / ta
        cu = qu - floor_r * nx
        for j in range(seg + 1):
            th = math.radians(-90 + (wall_deg) * j / seg)
            u, z = cu + floor_r * math.cos(th), cz + floor_r * math.sin(th)
            st.append((-u, z, "smooth"))
        st[0] = (st[0][0], st[0][1], "crisp")
    else:
        st.append((0.0, zf, "crisp"))
    if rim_r > 0:                                 # host rim rounded: centre inside the host
        cz = top_z - rim_r
        pz = cz - rim_r * nz
        pu = (pz - zf) / ta
        cu = pu + rim_r * nx
        a0 = 90.0 + wall_deg
        for j in range(seg + 1):
            th = math.radians(a0 - (a0 - 93.0) * j / seg)
            u, z = cu + rim_r * math.cos(th), cz + rim_r * math.sin(th)
            st.append((-u, z, "wear" if 0.3 * seg <= j <= 0.7 * seg else "smooth"))
        st.append((st[-1][0], top_z + over, "crisp"))
    else:
        st.append((-(depth / ta), top_z, "crisp"))
        st.append((-(depth / ta), top_z + over, "crisp"))
    return st


# ------------------------------------------------------------------ loft

def loft(name, outline, sec, z0=0.0, mat=None, coll=None, cap_bottom=True, cap_top=True):
    """Build a solid from an Outline and a section. Returns the object (mesh in metres, origin at 0)."""
    rings = []
    for d, z, fl in sec:
        pts, pflags = outline.ring(d)
        rings.append((pts, z, fl, pflags))
    n = len(rings[0][0])
    bm = bmesh.new()
    V = [[bm.verts.new((p.x * MM, p.y * MM, (z0 + z) * MM)) for p in pts] for pts, z, fl, pf in rings]
    wear_layer = bm.faces.layers.int.new("wear")
    for k in range(len(rings) - 1):
        wear = rings[k][2] == "wear" and rings[k + 1][2] == "wear"
        for i in range(n):
            j = (i + 1) % n
            vs = (V[k][i], V[k][j], V[k + 1][j], V[k + 1][i])
            if len(set(vs)) < 4:
                continue
            try:
                f = bm.faces.new(vs)
            except ValueError:
                continue
            f[wear_layer] = 1 if wear else 0
            f.smooth = True
    if cap_top:
        f = bm.faces.new(V[-1]); f.smooth = False
    if cap_bottom:
        f = bm.faces.new(list(reversed(V[0]))); f.smooth = False
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005 * MM)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # hard creases (crisp stations, sharp plan corners) are sharp edges; caps are flat
    for e in bm.edges:
        if len(e.link_faces) != 2:
            continue
        if e.calc_face_angle(0.0) > math.radians(40):
            e.smooth = False
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    return ob


def check_outline(name, outline, sec):
    """Warn when the largest inset in the section exceeds the smallest convex plan radius (self-crossing)."""
    dmax = max(d for d, z, f in sec)
    r = outline.min_convex_radius()
    if dmax > r + 1e-6:
        print(f"[out] WARN {name}: section inset {dmax:.2f} mm > smallest convex radius {r:.2f} mm")


# ------------------------------------------------------------------ transforms

def orient(ob, loc_mm, axis=(0, 0, 1), spin_deg=0.0):
    """Place an object built along +Z at loc_mm, its Z axis turned to `axis`, spun about it first."""
    ax = Vector(axis).normalized()
    rot = Vector((0, 0, 1)).rotation_difference(ax).to_matrix().to_4x4()
    spin = Matrix.Rotation(math.radians(spin_deg), 4, "Z")
    ob.matrix_world = Matrix.Translation(Vector(loc_mm) * MM) @ rot @ spin
    return ob


def bake(ob):
    ob.data.transform(ob.matrix_world)
    ob.matrix_world = Matrix.Identity(4)
    return ob


def rod(name, p0, p1, sec_fn, outline, mat=None, spin_deg=0.0, twist_deg=0.0):
    """A lathe-like part along p0 -> p1 (mm): outline in the part's cross-section plane, section along the axis.
    twist_deg turns the outline along the length (a diagonal knurl)."""
    p0, p1 = Vector(p0), Vector(p1)
    length = (p1 - p0).length
    ob = loft(name, outline, sec_fn(length), mat=mat)
    if twist_deg:
        L = length * MM
        for v in ob.data.vertices:
            q = math.radians(twist_deg) * v.co.z / L
            c, s_ = math.cos(q), math.sin(q)
            v.co.x, v.co.y = v.co.x * c - v.co.y * s_, v.co.x * s_ + v.co.y * c
    orient(ob, p0, p1 - p0, spin_deg)
    return bake(ob)


def sec_rod(r_end=0.5, r_start=None, seg=4):
    """Section for a rod of length L: small fillets at both ends (a closed profile needs both)."""
    rs = r_end if r_start is None else r_start

    def f(L):
        pts = [(0.6 * rs if rs > 0 else 0.0, 0.0), (0.0, rs if rs > 0 else 0.0), (0.0, L - r_end), (r_end, L), (r_end * 4 + 1, L)]
        s = []
        if rs > 0:
            s += [(rs, 0.0, "crisp")]
            for j in range(1, seg + 1):
                q = math.radians(-90 + 90 * j / seg)
                s.append((rs - rs * math.cos(q), rs + rs * math.sin(q), "smooth"))
        else:
            s.append((0.0, 0.0, "crisp"))
        s.append((0.0, L - r_end, "smooth"))
        for j in range(1, seg + 1):
            q = math.radians(90 * j / seg)
            s.append((r_end - r_end * math.cos(q), L - r_end + r_end * math.sin(q), "wear" if 0.3 * seg <= j <= 0.7 * seg else "smooth"))
        return s
    return f


# ------------------------------------------------------------------ booleans

def cut(host, cutters, solver=None, name=None):
    """Subtract each cutter (its own object, in one collection operand), apply, and check the result.
    Cutter materials transfer to the new faces (a cutter without one gives the host material)."""
    if not cutters:
        return host
    solver = solver or SOLVER
    col = bpy.data.collections.new((name or host.name) + "_cut")
    bpy.context.scene.collection.children.link(col)
    host_mat = host.data.materials[0] if host.data.materials else None
    for c in cutters:
        if host_mat is not None and not c.data.materials:
            c.data.materials.append(host_mat)
        for uc in list(c.users_collection):
            uc.objects.unlink(c)
        col.objects.link(c)
    before = len(host.data.polygons)
    backup = host.data.copy()
    for attempt in (solver, "EXACT"):
        m = host.modifiers.new("cut", "BOOLEAN")
        m.operation, m.operand_type, m.collection = "DIFFERENCE", "COLLECTION", col
        m.solver = attempt
        if attempt == "EXACT":
            m.use_self = True
        m.material_mode = "TRANSFER"
        with bpy.context.temp_override(object=host, active_object=host, selected_objects=[host]):
            bpy.ops.object.modifier_apply(modifier=m.name)
        n = len(host.data.polygons)
        if n > 0 and n != before:
            break
        LOG.append((host.name, n, f"{attempt} gave {n} polys (was {before}); retrying"))
        host.data = backup.copy()
    LOG.append((host.name, len(host.data.polygons), f"cut x{len(cutters)} {attempt}"))
    for c in list(col.objects):
        bpy.data.objects.remove(c)
    bpy.data.collections.remove(col)
    # drop empty slots the boolean may leave
    me = host.data
    if any(s is None for s in me.materials):
        used = [s for s in me.materials]
        keep = [i for i, s in enumerate(used) if s is not None]
        remap = {old: new for new, old in enumerate(keep)}
        idx = [0] * len(me.polygons)
        me.polygons.foreach_get("material_index", idx)
        mats = [used[i] for i in keep]
        me.materials.clear()
        for mt in mats:
            me.materials.append(mt)
        me.polygons.foreach_set("material_index", [remap.get(i, 0) for i in idx])
    return host


def z_levels(ob):
    return sorted({round(v.co.z / MM, 2) for v in ob.data.vertices})


# ------------------------------------------------------------------ cord

def helix_cord(name, path_mm, coil_r_mm, wire_r_mm, turns, coll=None, pts_per_turn=28, ramp_mm=8.0, wobble=0.0):
    """A coiled cord: a helix round a polyline path (mm 3D points), radius ramped to 0 over ramp_mm at both
    ends so the straight leads join the same tube. Parallel-transport frame, so the coil does not twist."""
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
    _, t0 = at(0)
    nrm = t0.cross(Vector((0, 0, 1)))
    if nrm.length < 1e-4:
        nrm = t0.cross(Vector((0, 1, 0)))
    nrm.normalize()
    for i in range(n + 1):
        s = total * i / n
        c, tan = at(s)
        nrm = (nrm - tan * nrm.dot(tan)).normalized()
        bn = tan.cross(nrm).normalized()
        a = 2 * math.pi * turns * i / n
        e = max(0.0, min(1.0, min(s, total - s) / max(ramp_mm, 1e-6)))
        rr = coil_r_mm * (e * e * (3 - 2 * e)) * (1.0 + wobble * math.sin(a * 0.37 + 1.3))
        p = c + nrm * (rr * math.cos(a)) + bn * (rr * math.sin(a))
        sp.points[i].co = (p.x * MM, p.y * MM, p.z * MM, 1.0)
    ob = bpy.data.objects.new(name, cu)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob
