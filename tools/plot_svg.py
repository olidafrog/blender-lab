"""Curves in a Blender scene → SVG strokes for a pen plotter. Runs inside Blender (bpy, numpy).

    import plot_svg
    stats = plot_svg.export(objects, camera, "out.svg", page=(210, 148), margin=15, pen=0.5)
    plot_svg.export_scene(folder)      # one SVG per collection named "Plot <name>"
    plot_svg.raster("out.svg", "out.png", width=2400)       # needs Inkscape
    plot_svg.sheet(["a.svg", "b.svg"], "sheet.svg")         # side by side, for review only

What it reads: the evaluated curves of each object (Geometry Nodes output included) as strokes, its
evaluated point cloud as dots, and its evaluated mesh as an occluder: with hidden=1 the parts of a
stroke behind a mesh are cut away (hidden=2 keeps them on their own layer "0 - hidden"), and with
outline=1 each mesh also gives its silhouette as strokes. The mesh itself is never drawn. What it writes: millimetres, stroke only, one top-level Inkscape
layer per pen ("1 - lines", "2 - dots"), strokes ordered to cut pen-up travel. A dot is one spiral
stroke, because a plotter cannot fill.

A final .blend carries this file as the text block "plot_svg.py", so "Export SVG" runs without the repo.
"""
import colorsys
import math
import shutil
import subprocess
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

DEFAULTS = {
    "page": (210.0, 148.0),   # mm, A5 landscape
    "margin": 15.0,           # mm
    "pen": 0.5,               # mm, the stroke width shown in previews
    "dot": 1.8,               # mm, dot diameter; 0: no dots
    "min_gap": 0.05,          # mm: a stroke running this close beside an earlier one is cut there; 0: off
    "gap_angle": 10.0,        # degrees: min_gap only cuts a line that runs within this angle of the earlier one.
                              # 10 removes doubled lines; about 25 with min_gap near the pen width also thins
                              # the places where many lines converge into a blot
    "gap_run": 2.5,           # mm: a too-close run shorter than this is a crossing, and is kept
    "gap_remnant": 0.0,       # mm: a piece shorter than this left between two such cuts is removed with them
    "weave": 0.0,             # mm: where two lines cross at different depths, the far one is broken by a gap this
                              # wide, as in a knot diagram. For see-through plots; 0: off
    "join": 0.0,              # mm: two stroke ends closer than this, running the same way, become one stroke
    "end_dots": True,         # a dot on each end the cut leaves
    "simplify": 0.01,         # mm, tolerance for dropping points on straight runs
    "min_length": 0.3,        # mm, shorter strokes are dropped
    "min_loop": 8.0,          # mm, closed loops shorter than this are dropped (a speck at the top of a peak)
    "cusp_dots": True,        # a dot where a line folds back on itself (a smooth 3D curve seen end-on)
    "hidden": 0,              # 0: draw every line. 1: cut the parts behind a mesh. 2: put them on layer "0 - hidden"
    "outline": False,         # also draw the silhouette of each mesh
    "clip": False,            # cut strokes at the margins instead of letting them leave the page
    "hide_step": 0.25,        # mm between visibility samples along a stroke
    "hide_bias": 0.004,       # free curves only: how far in front of the curve its ray starts, as a share of the mesh's size
    "graze": 0.0,             # with hidden on: also cut a line where its surface is nearly edge-on (|normal . view|
                              # under this, 0..1). Thins the crowd of lines at the rim of a ball; 0: off
    "min_outline": 0.0,       # mm: outline pieces shorter than this are dropped (specks where a surface twists edge-on)
    "min_visible": 0.8,       # mm: visible runs shorter than this are dropped, hidden gaps shorter are bridged
    "ink": "#262626",
}
INKSCAPE = shutil.which("inkscape") or "/Applications/Inkscape.app/Contents/MacOS/inkscape"


def read_geometry(obj, depsgraph):
    """World-space strokes [(N×3 array, cyclic)], dots (M×3) and mesh (verts, normals, triangles) or None
    of one evaluated object."""
    geo = obj.evaluated_get(depsgraph).evaluated_geometry()  # keep alive while reading
    mw = np.array(obj.matrix_world)
    strokes, dots = [], np.zeros((0, 3))

    def world(attr, n):
        co = np.empty(n * 3, np.float32)
        attr.data.foreach_get("vector", co)
        return co.reshape(-1, 3).astype(np.float64) @ mw[:3, :3].T + mw[:3, 3]

    c = geo.curves
    if c is not None and len(c.curves):
        pts = world(c.attributes["position"], len(c.points))
        off = np.empty(len(c.curves) + 1, np.int32)
        c.curve_offset_data.foreach_get("value", off)
        cyc = np.zeros(len(c.curves), bool)
        if "cyclic" in c.attributes:
            c.attributes["cyclic"].data.foreach_get("value", cyc)
        strokes = [(pts[off[i]:off[i + 1]], bool(cyc[i])) for i in range(len(c.curves)) if off[i + 1] - off[i] > 1]
    pc = geo.pointcloud
    if pc is not None and len(pc.points):
        dots = world(pc.attributes["position"], len(pc.points))
    mesh = None
    m = geo.mesh
    if m is not None and len(m.polygons):
        nv = len(m.vertices)
        co = np.empty(nv * 3, np.float32)
        m.vertices.foreach_get("co", co)
        verts = co.reshape(-1, 3).astype(np.float64) @ mw[:3, :3].T + mw[:3, 3]
        nr = np.empty(nv * 3, np.float32)
        m.vertex_normals.foreach_get("vector", nr)
        normals = nr.reshape(-1, 3).astype(np.float64) @ np.linalg.inv(mw[:3, :3])
        normals /= np.maximum(np.linalg.norm(normals, axis=1), 1e-12)[:, None]
        loops = np.empty(len(m.loops), np.int32)
        m.loops.foreach_get("vertex_index", loops)
        start = np.empty(len(m.polygons), np.int32)
        total = np.empty(len(m.polygons), np.int32)
        m.polygons.foreach_get("loop_start", start)
        m.polygons.foreach_get("loop_total", total)
        tris = [np.stack([loops[start], loops[start + k], loops[start + k + 1]], 1)[total > k + 1]
                for k in range(1, int(total.max()) - 1)]       # fan
        tris = np.vstack(tris)
        # Weld vertices that share a position (the seam of a closed surface, a pole), so the outline and
        # the neighbour test run across the seam.
        scale = max(float(np.ptp(verts, axis=0).max()), 1e-9) * 1e-6
        _, first_of, inverse = np.unique(np.round(verts / scale).astype(np.int64), axis=0, return_index=True, return_inverse=True)
        inverse = inverse.reshape(-1)
        summed = np.zeros((len(first_of), 3))
        np.add.at(summed, inverse, normals)
        ln = np.linalg.norm(summed, axis=1)
        normals = np.where(ln[:, None] > 1e-9, summed / np.maximum(ln, 1e-12)[:, None], normals[first_of])
        verts, tris = verts[first_of], inverse[tris]
        tris = tris[(tris[:, 0] != tris[:, 1]) & (tris[:, 1] != tris[:, 2]) & (tris[:, 0] != tris[:, 2])]
        mesh = (verts, normals, tris)
    return strokes, dots, mesh


def to_page(pts, scene, cam, page, margin):
    """Project world points through the camera into page millimetres (y down)."""
    r = scene.render
    proj = np.array(cam.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(), x=r.resolution_x, y=r.resolution_y,
                                           scale_x=r.pixel_aspect_x, scale_y=r.pixel_aspect_y))
    m = proj @ np.array(cam.matrix_world.inverted())
    pts = np.asarray(pts, np.float64).reshape(-1, 3)
    h = pts @ m[:, :3].T + m[:, 3]
    uv = h[:, :2] / h[:, 3:4] * 0.5 + 0.5
    aspect = scene.render.resolution_x / scene.render.resolution_y
    w, h = page[0] - 2 * margin, page[1] - 2 * margin
    fw = min(w, h * aspect)                       # the camera frame, fitted inside the margins
    fh = fw / aspect
    x = (page[0] - fw) / 2 + uv[:, 0] * fw
    y = (page[1] - fh) / 2 + (1 - uv[:, 1]) * fh
    return np.stack([x, y], 1)


class _View:
    """Which way the camera is from a point."""

    def __init__(self, cam):
        mw = cam.matrix_world
        self.origin = np.array(mw.translation)
        self.toward = np.array(mw.to_3x3() @ Vector((0, 0, 1)))
        self.toward /= np.linalg.norm(self.toward)
        self.ortho = cam.data.type == "ORTHO"

    def depth(self, pts):
        """Distance from the camera (from its plane, for an orthographic camera)."""
        if self.ortho:
            return (self.origin - pts) @ self.toward
        return np.linalg.norm(self.origin - pts, axis=1)

    def rays(self, pts):
        """Unit directions to the camera and the distance to it (inf for an orthographic camera)."""
        if self.ortho:
            return np.broadcast_to(self.toward, pts.shape), np.full(len(pts), 1e30)
        d = self.origin - pts
        far = np.linalg.norm(d, axis=1)
        return d / far[:, None], far


class _Occluder:
    """The meshes of a plot as one BVH, with the tests a stroke sample needs."""

    def __init__(self, meshes, o):
        verts = np.vstack([m[0] for m in meshes])
        off, faces = 0, []
        for v, _, t in meshes:
            faces.append(t + off)
            off += len(v)
        tris = np.vstack(faces)
        self.size = float(np.linalg.norm(verts.max(0) - verts.min(0)))
        self.bias = o["hide_bias"] * self.size
        self.bvh = BVHTree.FromPolygons(verts.tolist(), tris.tolist(), all_triangles=True)
        p = verts[tris]
        self.edge = np.linalg.norm(p - np.roll(p, 1, axis=1), axis=2).max(1)      # longest edge of each triangle
        self.corners = [frozenset(t) for t in tris.tolist()]


def _visible(occ, pts, view, graze=0.0, reach=0.0):
    """True where nothing lies between the point and the camera.

    A point on the surface (an isoline, an outline) is tested from the camera's side: it is seen when
    the first triangle the ray meets is the point's own or one that shares a corner with it. Depth
    along the ray is useless where the surface is edge-on; the mesh's own connections are not, and
    another sheet of a self-crossing surface is never a neighbour. reach > 0 (outlines, which sit
    where the mesh is edge-on) also accepts a first hit within `reach` triangle edges of the point.
    A point off the surface (a free curve) is tested with a ray from just in front of it.
    graze > 0 also hides a point on a surface seen nearly edge-on."""
    d, far = view.rays(pts)
    cast, near = occ.bvh.ray_cast, occ.bvh.find_nearest
    span = occ.size * 4
    vis = np.ones(len(pts), bool)
    for k in range(len(pts)):
        p, dk = pts[k], d[k]
        loc, normal, own, _ = near(tuple(p), occ.size * 1e-3)
        if own is None:
            vis[k] = cast(tuple(p + dk * occ.bias), tuple(dk), far[k] - occ.bias)[0] is None
            continue
        if graze > 0 and abs(normal.x * dk[0] + normal.y * dk[1] + normal.z * dk[2]) < graze:
            vis[k] = False
            continue
        back = min(far[k], span)
        hit, _, first, _ = cast(tuple(p + dk * back), tuple(-dk), back)
        if hit is not None and first != own and not (occ.corners[first] & occ.corners[own]):
            gap = ((hit.x - p[0]) ** 2 + (hit.y - p[1]) ** 2 + (hit.z - p[2]) ** 2) ** 0.5
            vis[k] = gap < max(reach, 0.1) * occ.edge[own]
    return vis


def _densify(q, page, step):
    """Points along polyline q so that no two neighbours are more than `step` mm apart on the page."""
    n = np.maximum(np.ceil(np.linalg.norm(np.diff(page, axis=0), axis=1) / step).astype(int), 1)
    seg = np.repeat(np.arange(len(n)), n)
    frac = (np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n)) / np.repeat(n, n)
    return np.vstack([q[seg] + (q[seg + 1] - q[seg]) * frac[:, None], q[-1:]])


def _split_hidden(p, cyc, project, occ, view, o, kind="line"):
    """One world-space stroke → (visible runs, hidden runs), each [(points, cyclic)]."""
    q = np.vstack([p, p[:1]]) if cyc else p
    d = _densify(q, project(q), o["hide_step"])
    graze, reach = (0.0, 2.5) if kind == "outline" else (o["graze"], 0.0)
    vis = _visible(occ, d, view, graze, reach)
    if vis.all():
        return [(p, cyc)], []
    if not vis.any():
        return [], [(p, cyc)]
    short = max(int(round(o["min_visible"] / o["hide_step"])), 1)

    def runs():
        out, i = [], 0
        while i < len(vis):
            j = i
            while j + 1 < len(vis) and vis[j + 1] == vis[i]:
                j += 1
            out.append([i, j])
            i = j + 1
        return out

    for want in (False, True):       # bridge short hidden gaps, then drop short visible runs
        rs = runs()
        for k, (a, b) in enumerate(rs):
            inner = 0 < k < len(rs) - 1 or (cyc and len(rs) > 2)
            if vis[a] == want and b - a + 1 < short and (inner or want):
                vis[a:b + 1] = not want
    if vis.all():
        return [(p, cyc)], []
    if not vis.any():
        return [], [(p, cyc)]
    rs = runs()

    def edge(k):                     # the point between samples k and k+1 where visibility flips
        lo, hi = d[k], d[k + 1]
        first = vis[k]
        for _ in range(5):
            mid = (lo + hi) / 2
            if _visible(occ, mid[None], view, graze, reach)[0] == first:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    cuts = {b: edge(b) for a, b in rs[:-1]}
    pieces = []
    for a, b in rs:
        pts = [d[a:b + 1]]
        if a - 1 in cuts:
            pts.insert(0, cuts[a - 1][None])
        if b in cuts:
            pts.append(cuts[b][None])
        pieces.append((bool(vis[a]), np.vstack(pts)))
    if cyc and len(pieces) > 1 and pieces[0][0] == pieces[-1][0]:     # the run that wraps round the start
        pieces[0] = (pieces[0][0], np.vstack([pieces[-1][1], pieces[0][1][1:]]))
        pieces.pop()
    return [(x, False) for v, x in pieces if v], [(x, False) for v, x in pieces if not v]


def _silhouette(verts, normals, tris, view):
    """Outline of a smooth mesh: the zero set of (normal · view) across each triangle, chained into
    polylines. Returns [(points, normals at the points, cyclic)]."""
    d, _ = view.rays(verts)
    P = verts[tris]
    face = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
    N = normals[tris]                                         # corner normals, flipped to the face's side:
    N = N * np.where(np.einsum("tcj,tj->tc", N, face) < 0, -1.0, 1.0)[:, :, None]   # a Mobius band has no global side
    G = np.einsum("tcj,tcj->tc", N, d[tris])
    G = np.where(np.abs(G) < 1e-9, 1e-9, G)
    side = G > 0
    n_pos = side.sum(1)
    mixed = (n_pos == 1) | (n_pos == 2)
    T, S, G, N, P = tris[mixed], side[mixed], G[mixed], N[mixed], P[mixed]
    if not len(T):
        return []
    lone = np.argmax(S == (n_pos[mixed] == 1)[:, None], axis=1)
    rows = np.arange(len(T))

    def cross(ci, cj):
        gi, gj = G[rows, ci], G[rows, cj]
        t = (gi / (gi - gj))[:, None]
        i, j = T[rows, ci], T[rows, cj]
        n = N[rows, ci] + (N[rows, cj] - N[rows, ci]) * t
        return P[rows, ci] + (P[rows, cj] - P[rows, ci]) * t, n / np.maximum(np.linalg.norm(n, axis=1), 1e-12)[:, None], \
            np.minimum(i, j).astype(np.int64) * len(verts) + np.maximum(i, j)

    a, b, c = lone, (lone + 1) % 3, (lone + 2) % 3
    (p0, n0, k0), (p1, n1, k1) = cross(a, b), cross(a, c)
    ends = {}
    for s, (ka, kb) in enumerate(zip(k0.tolist(), k1.tolist())):
        ends.setdefault(ka, []).append(s)
        ends.setdefault(kb, []).append(s)
    k0, k1 = k0.tolist(), k1.tolist()
    used = np.zeros(len(T), bool)
    chains = []

    def walk(s, key):
        """Follow segments from segment s, leaving through `key`."""
        pts = []
        while True:
            nxt = [x for x in ends[key] if not used[x]]
            if len(ends[key]) != 2 or not nxt:
                return pts, False
            s = nxt[0]
            used[s] = True
            key, other = (k1[s], 1) if k0[s] == key else (k0[s], 0)
            pts.append((p1[s], n1[s]) if other else (p0[s], n0[s]))
            if key == start_key:
                return pts, True

    for s in range(len(T)):
        if used[s]:
            continue
        used[s] = True
        start_key = k0[s]
        fwd, closed = walk(s, k1[s])
        pts = [(p0[s], n0[s]), (p1[s], n1[s])] + fwd
        if not closed:
            start_key = None
            back, _ = walk(s, k0[s])
            pts = back[::-1] + pts
        else:
            pts = pts[:-1]
        chains.append((np.array([x for x, _ in pts]), np.array([x for _, x in pts]), closed))
    return chains


def _weave(strokes, gap):
    """Knot-diagram breaks: where two strokes cross on the page at different depths, cut a gap in the
    far one. strokes: [(page points, cyclic, kind, depth per point)]. Returns [(points, cyclic, kind)]."""
    cell = 2.0
    Q, grid = [], {}
    for si, (p, cyc, kind, dep) in enumerate(strokes):
        keep = _simplify_mask(p, 0.02)
        q, d = p[keep], dep[keep]
        if cyc:
            q, d = np.vstack([q, q[:1]]), np.append(d, d[0])
        cum = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(q, axis=0), axis=1))])
        Q.append((q, d, cum))
        lo = np.floor(np.minimum(q[:-1], q[1:]) / cell).astype(int)
        hi = np.floor(np.maximum(q[:-1], q[1:]) / cell).astype(int)
        for j in range(len(q) - 1):
            for cx in range(lo[j, 0], hi[j, 0] + 1):
                for cy in range(lo[j, 1], hi[j, 1] + 1):
                    grid.setdefault((cx, cy), []).append((si, j))
    cuts = {}
    done = set()
    for items in grid.values():
        for x in range(len(items)):
            sa, ja = items[x]
            qa, da, ca = Q[sa]
            a0, a1 = qa[ja], qa[ja + 1]
            r = a1 - a0
            for y in range(x + 1, len(items)):
                sb, jb = items[y]
                if sa == sb and abs(ja - jb) < 2:
                    continue
                key = (sa, ja, sb, jb)
                if key in done:
                    continue
                done.add(key)
                qb, db, cb = Q[sb]
                b0 = qb[jb]
                e = qb[jb + 1] - b0
                den = r[0] * e[1] - r[1] * e[0]
                if abs(den) < 1e-12:
                    continue
                w = b0 - a0
                t = (w[0] * e[1] - w[1] * e[0]) / den
                u = (w[0] * r[1] - w[1] * r[0]) / den
                if not (0 <= t < 1 and 0 <= u < 1):
                    continue
                za, zb = da[ja] + (da[ja + 1] - da[ja]) * t, db[jb] + (db[jb + 1] - db[jb]) * u
                if abs(za - zb) < 1e-6:
                    continue
                sin = abs(den) / (np.linalg.norm(r) * np.linalg.norm(e))
                half = min(gap / 2 / max(sin, 0.25), 2 * gap)
                if za > zb:
                    cuts.setdefault(sa, []).append((ca[ja] + (ca[ja + 1] - ca[ja]) * t, half))
                else:
                    cuts.setdefault(sb, []).append((cb[jb] + (cb[jb + 1] - cb[jb]) * u, half))
    out = []
    for si, (p, cyc, kind, _) in enumerate(strokes):
        q, _, cum = Q[si]
        if si not in cuts:
            out.append((q[:-1] if cyc else q, cyc, kind))
            continue
        spans, pos = [], 0.0
        for s0, s1 in sorted((c - h, c + h) for c, h in cuts[si]):
            if s0 > pos:
                spans.append((pos, s0))
            pos = max(pos, s1)
        if pos < cum[-1]:
            spans.append((pos, cum[-1]))
        for s0, s1 in spans:
            i0, i1 = np.searchsorted(cum, s0, "right"), np.searchsorted(cum, s1, "left")
            ends = [q[k - 1] + (q[k] - q[k - 1]) * ((v - cum[k - 1]) / max(cum[k] - cum[k - 1], 1e-12))
                    for v, k in ((s0, min(max(i0, 1), len(q) - 1)), (s1, min(max(i1, 1), len(q) - 1)))]
            pts = np.vstack([ends[0][None], q[i0:i1], ends[1][None]])
            if len(pts) > 1:
                out.append((pts, False, kind))
    return out


def _clip(p, cyc, lo, hi):
    """Cut a page-space stroke at the rectangle lo..hi. Returns the parts inside."""
    q = np.vstack([p, p[:1]]) if cyc else p
    inside = ((q >= lo) & (q <= hi)).all(1)
    if inside.all():
        return [(p, cyc)]
    out, cur = [], []
    for a, b in zip(q[:-1], q[1:]):
        d = b - a
        t0, t1 = 0.0, 1.0
        for k in range(2):           # Liang-Barsky
            if abs(d[k]) < 1e-12:
                if a[k] < lo[k] or a[k] > hi[k]:
                    t0, t1 = 1.0, 0.0
            else:
                ta, tb = (lo[k] - a[k]) / d[k], (hi[k] - a[k]) / d[k]
                t0, t1 = max(t0, min(ta, tb)), min(t1, max(ta, tb))
        if t0 > t1:
            if len(cur) > 1:
                out.append(np.array(cur))
            cur = []
            continue
        if t0 > 0 or not cur:
            if len(cur) > 1:
                out.append(np.array(cur))
            cur = [a + d * t0]
        cur.append(a + d * t1)
        if t1 < 1:
            out.append(np.array(cur))
            cur = []
    if len(cur) > 1:
        out.append(np.array(cur))
    return [(x, False) for x in out]


def _length(p):
    return float(np.linalg.norm(np.diff(p, axis=0), axis=1).sum()) if len(p) > 1 else 0.0


def _simplify(p, tol):
    """Ramer–Douglas–Peucker, iterative."""
    return p[_simplify_mask(p, tol)]


def _simplify_mask(p, tol):
    if tol <= 0 or len(p) < 3:
        return np.ones(len(p), bool)
    keep = np.zeros(len(p), bool)
    keep[[0, -1]] = True
    stack = [(0, len(p) - 1)]
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        d = p[b] - p[a]
        n = np.linalg.norm(d)
        seg = p[a + 1:b] - p[a]
        dist = np.abs(seg[:, 0] * d[1] - seg[:, 1] * d[0]) / n if n > 1e-12 else np.linalg.norm(seg, axis=1)
        i = int(dist.argmax())
        if dist[i] > tol:
            keep[a + 1 + i] = True
            stack += [(a, a + 1 + i), (a + 1 + i, b)]
    return keep


def _cusps(p, cyc, reach=1.0, angle=110.0):
    """Points where the stroke reverses within `reach` mm each side: the tips of projection folds."""
    if len(p) < 5:
        return []
    seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    found = []
    for i in range(1, len(p) - 1):
        a = min(int(np.searchsorted(s, s[i] - reach)), i - 1)
        b = max(min(int(np.searchsorted(s, s[i] + reach)), len(p) - 1), i + 1)
        u, v = p[i] - p[a], p[b] - p[i]
        nu, nv = np.linalg.norm(u), np.linalg.norm(v)
        if nu < 1e-6 or nv < 1e-6:
            continue
        turn = math.degrees(math.acos(max(-1.0, min(1.0, float(u @ v) / (nu * nv)))))
        if turn > angle:
            found.append((turn, i))
    tips, last = [], None          # one tip per fold: the sharpest point of each run
    for turn, i in found:
        if last is not None and s[i] - s[last[1]] < 2 * reach:
            if turn > last[0]:
                last = (turn, i)
                tips[-1] = p[i]
        else:
            last = (turn, i)
            tips.append(p[i])
    return tips


def _dedupe(strokes, tol, min_run=2.5, cos=0.985, remnant=0.0):
    """Cut away the parts of a stroke that run along an earlier stroke (same place, same direction).
    Two meridians that project onto one line would otherwise be inked twice."""
    step = 2.5                                      # degrees per direction bucket
    n_b = int(180 / step)
    reach = int(math.ceil(math.degrees(math.acos(min(cos, 1.0))) / step))
    near = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    grid = {}                                       # cell -> set of direction buckets inked there
    out = []
    for p, cyc in strokes:
        q = np.vstack([p, p[:1]]) if cyc else p
        seg = np.diff(q, axis=0)
        ln = np.linalg.norm(seg, axis=1)
        ang = np.degrees(np.arctan2(seg[:, 1], seg[:, 0])) % 180.0
        bucket = (ang / step).astype(int) % n_b
        bucket = np.append(bucket, bucket[-1:])
        cells = np.floor(q / tol).astype(int).tolist()
        dup = np.zeros(len(q), bool)
        if grid:
            for i, (cx, cy) in enumerate(cells):
                b = int(bucket[i])
                want = {(b + k) % n_b for k in range(-reach, reach + 1)}
                for dx, dy in near:
                    have = grid.get((cx + dx, cy + dy))
                    if have and not want.isdisjoint(have):
                        dup[i] = True
                        break
        # Register this stroke, sampled every tol/2, after testing it (a stroke never hides itself).
        for a, c, l, bk in zip(q[:-1], q[1:], ln, bucket):
            n = max(2, int(l / (tol / 2)) + 1)
            pts = np.floor((a + (c - a) * np.linspace(0, 1, n)[:, None]) / tol).astype(int).tolist()
            for cell in pts:
                grid.setdefault((cell[0], cell[1]), set()).add(int(bk))
        if not dup.any():
            out.append((p, cyc))
            continue
        # Keep duplicate runs shorter than min_run: those are crossings, not overlaps.
        runs, i = [], 0
        while i < len(q):
            j = i
            while j + 1 < len(q) and dup[j + 1] == dup[i]:
                j += 1
            runs.append((i, j, bool(dup[i])))
            i = j + 1
        for a, b, d in runs:
            if d and _length(q[a:b + 1]) < min_run:
                dup[a:b + 1] = False
        if not dup.any():
            out.append((p, cyc))
            continue
        # A short piece left between two cuts, or between a cut and the stroke's end, is a remnant: cut it too.
        i = 0
        while i < len(q):
            j = i
            while j + 1 < len(q) and dup[j + 1] == dup[i]:
                j += 1
            if not dup[i] and _length(q[i:j + 1]) < remnant:
                dup[i:j + 1] = True
            i = j + 1
        i = 0
        while i < len(q):
            if dup[i]:
                i += 1
                continue
            j = i
            while j + 1 < len(q) and not dup[j + 1]:
                j += 1
            if j > i:
                out.append((q[i:j + 1], False))
            i = j + 1
    return out


def _back(p, end, reach=0.4):
    """The point about `reach` mm in from an end: a stroke's direction there, ignoring a tiny hook at the tip."""
    step = 1 if end == 0 else -1
    k = end + step
    while 0 <= (k + step if step > 0 else k + step + len(p)) < len(p) and np.linalg.norm(p[k] - p[end]) < reach:
        k += step
    return p[k]


def _join(strokes, tol):
    """Join open strokes whose ends meet within tol and run the same way (the cuts leave such pairs)."""
    open_ = [p for p, c in strokes if not c]
    closed = [(p, c) for p, c in strokes if c]
    merged = True
    while merged:
        merged = False
        grid = {}
        for k, p in enumerate(open_):
            for end in (0, -1):
                grid.setdefault(tuple(np.floor(p[end] / tol).astype(int)), []).append((k, end))
        gone = set()
        for k, p in enumerate(open_):
            if k in gone:
                continue
            for end in (0, -1):
                cx, cy = np.floor(p[end] / tol).astype(int)
                best = None
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        for j, e in grid.get((cx + dx, cy + dy), ()):
                            if j == k or j in gone:
                                continue
                            q = open_[j]
                            gap = float(np.linalg.norm(q[e] - p[end]))
                            if gap > tol:
                                continue
                            out_p = p[end] - _back(p, end)             # leaving p
                            in_q = _back(q, e) - q[e]                    # entering q
                            n = np.linalg.norm(out_p) * np.linalg.norm(in_q)
                            if n > 1e-12 and float(out_p @ in_q) / n > 0.8 and (best is None or gap < best[0]):
                                best = (gap, j, e)
                if best:
                    _, j, e = best
                    a = p if end == -1 else p[::-1]
                    b = open_[j] if e == 0 else open_[j][::-1]
                    open_[k] = np.vstack([a, b])
                    gone.add(j)
                    merged = True
                    break
        open_ = [p for k, p in enumerate(open_) if k not in gone]
    return closed + [(p, False) for p in open_]


def _order(strokes, start=(0.0, 0.0)):
    """Greedy nearest neighbour. Open strokes may reverse; closed ones start at their nearest point."""
    todo = list(strokes)
    pos = np.array(start, float)
    out = []
    while todo:
        best = None
        for k, (p, cyc) in enumerate(todo):
            if cyc:
                d = np.linalg.norm(p - pos, axis=1)
                i = int(d.argmin())
                cand = (d[i], k, i)
            else:
                d0, d1 = np.linalg.norm(p[0] - pos), np.linalg.norm(p[-1] - pos)
                cand = (min(d0, d1), k, 0 if d0 <= d1 else -1)
            if best is None or cand[0] < best[0]:
                best = cand
        _, k, i = best
        p, cyc = todo.pop(k)
        if cyc:
            p = np.roll(p, -i, axis=0)
        elif i == -1:
            p = p[::-1]
        out.append((p, cyc))
        pos = p[0] if cyc else p[-1]
    return out


def _spiral(c, diameter, pen):
    """One stroke that fills a dot: a spiral out from the centre, closed by a full circle."""
    r = max(diameter / 2 - pen / 2, pen * 0.1)    # the pen's own width reaches the rim
    turns = max(r / (pen * 0.8), 0.0)
    n = int(turns * 16)
    a = np.linspace(0, turns * math.tau, n + 1)[:-1] if n else np.zeros(0)
    rad = r * a / (turns * math.tau) if n else np.zeros(0)
    a2 = turns * math.tau + np.linspace(0, math.tau, 17)
    ang = np.concatenate([a, a2])
    rad = np.concatenate([rad, np.full(17, r)])
    return c + np.stack([rad * np.cos(ang), rad * np.sin(ang)], 1)


def _travel(strokes, start=(0.0, 0.0)):
    pos, up = np.array(start, float), 0.0
    for p, cyc in strokes:
        up += float(np.linalg.norm(p[0] - pos))
        pos = p[0] if cyc else p[-1]
    return up


def _path(p, cyc):
    d = "M" + " L".join(f"{x:.3f},{y:.3f}" for x, y in p)
    return f'<path d="{d}{" Z" if cyc else ""}"/>'


def export(objects, camera, path, scene=None, debug=None, **opts):
    """Write one SVG. Returns the plot's stats. debug=<path> also writes the plot-check drawing."""
    o = {**DEFAULTS, **opts}
    scene = scene or bpy.context.scene
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    def project(p):
        return to_page(p, scene, camera, o["page"], o["margin"])

    world, dots3, meshes = [], [], []      # world: (points, cyclic, kind)
    for ob in objects:
        strokes, pts, mesh = read_geometry(ob, dg)
        world += [(p, cyc, "line") for p, cyc in strokes]
        if len(pts) and o["dot"] > 0:
            dots3.append(pts)
        if mesh is not None:
            meshes.append(mesh)
    hidden = []
    view = _View(camera)
    if meshes and (o["hidden"] or o["outline"]):
        if o["outline"]:
            for verts, normals, tris in meshes:
                world += [(p, cyc, "outline") for p, n, cyc in _silhouette(verts, normals, tris, view) if len(p) > 2]
        if o["hidden"]:
            occ = _Occluder(meshes, o)
            seen = []
            for p, cyc, kind in world:
                vis, hid = _split_hidden(p, cyc, project, occ, view, o, kind)
                seen += [(q, c, kind) for q, c in vis]
                hidden += hid
            world = [(q, c, kind) for q, c, kind in seen
                     if kind != "outline" or _length(project(q)) >= o["min_outline"]]
            dots3 = [d[_visible(occ, d, view)] for d in dots3]
    if o["weave"] > 0:
        lines = _weave([(project(p), cyc, kind, view.depth(p)) for p, cyc, kind in world], o["weave"])
    else:
        lines = [(project(p), cyc, kind) for p, cyc, kind in world]
    hidden = [(project(p), cyc) for p, cyc in hidden] if o["hidden"] == 2 else []
    dots = [d for pts in dots3 if len(pts) for d in project(pts)]
    if o["clip"]:
        lo, hi = np.full(2, o["margin"] * 0.5), np.array(o["page"]) - o["margin"] * 0.5
        lines = [(x, c, kind) for p, cyc, kind in lines for x, c in _clip(p, cyc, lo, hi)]
        hidden = [x for p, cyc in hidden for x in _clip(p, cyc, lo, hi)]
        dots = [d for d in dots if (d >= lo).all() and (d <= hi).all()]
    n_in, closed_in = len(lines), sum(c for _, c, _ in lines)
    marks = []
    # Outlines, then longest first, so a duplicate or a crowded part is cut from the lesser stroke.
    lines.sort(key=lambda s: (s[2] != "outline", -_length(s[0])))
    lines = [(p, cyc) for p, cyc, _ in lines]
    if o["min_gap"] > 0:
        n_open = sum(not c for _, c in lines)
        ends_before = {tuple(np.round(e, 3)) for p, c in lines if not c for e in (p[0], p[-1])}
        lines = _dedupe(lines, o["min_gap"], o["gap_run"], math.cos(math.radians(o["gap_angle"])), o["gap_remnant"])
        if o["end_dots"] and o["dot"] > 0:
            for p, c in lines:
                if not c and _length(p) >= o["min_length"]:
                    marks += [e for e in (p[0], p[-1]) if tuple(np.round(e, 3)) not in ends_before]
    if o["join"] > 0:
        lines = _join(lines, o["join"])
    lines = [(_simplify(p, o["simplify"]), cyc) for p, cyc in lines]
    lines = [(p, cyc) for p, cyc in lines
             if _length(p) >= o["min_length"] and not (cyc and _length(np.vstack([p, p[:1]])) < o["min_loop"])]
    if o["cusp_dots"] and o["dot"] > 0:
        for p, cyc in lines:
            marks += _cusps(p, cyc)
    dots = marks + dots   # ends and fold tips first: they win when two dots would touch
    lines = _order(lines)
    hidden = _order([(q, c) for q, c in ((_simplify(p, o["simplify"]), c) for p, c in hidden) if _length(q) >= o["min_length"]])
    if dots:  # drop dots that touch or sit on top of each other
        uniq = []
        for d in dots:
            if all(np.linalg.norm(d - u) > o["dot"] * 1.5 for u in uniq):
                uniq.append(d)
        dots = uniq
    end = (lines[-1][0][0] if lines[-1][1] else lines[-1][0][-1]) if lines else (0, 0)
    spirals = _order([(_spiral(d, o["dot"], o["pen"]), False) for d in dots], start=end)

    allp = np.vstack([p for p, _ in lines + spirals]) if lines or spirals else np.zeros((1, 2))
    w, h = o["page"]
    stats = {
        "strokes_in": n_in, "closed_in": closed_in, "hidden": len(hidden), "strokes": len(lines), "closed": sum(c for _, c in lines), "dots": len(spirals),
        "points": int(sum(len(p) for p, _ in lines)),
        "draw_mm": round(sum(_length(np.vstack([p, p[:1]]) if c else p) for p, c in lines + spirals)),
        "travel_mm": round(_travel(lines) + _travel(spirals, start=end)),
        "off_page": int(((allp < 0).any(1) | (allp[:, 0] > w) | (allp[:, 1] > h)).sum()),
        "bounds_mm": [round(float(v), 1) for v in (*allp.min(0), *allp.max(0))],
    }
    style = f'fill="none" stroke="{o["ink"]}" stroke-width="{o["pen"]}" stroke-linecap="round" stroke-linejoin="round"'
    svg = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
        f'width="{w:g}mm" height="{h:g}mm" viewBox="0 0 {w:g} {h:g}">',
        *([f'<g inkscape:groupmode="layer" inkscape:label="0 - hidden" id="hidden" '
           + style.replace(o["ink"], "#b4b4b4").replace(f'stroke-width="{o["pen"]}"', f'stroke-width="{o["pen"] * 0.6:g}"') + ">",
           *[_path(p, c) for p, c in hidden], "</g>"] if hidden else []),
        f'<g inkscape:groupmode="layer" inkscape:label="1 - lines" id="lines" {style}>',
        *[_path(p, c) for p, c in lines], "</g>",
        f'<g inkscape:groupmode="layer" inkscape:label="2 - dots" id="dots" {style}>',
        *[_path(p, c) for p, c in spirals], "</g>", "</svg>",
    ]
    Path(path).write_text("\n".join(svg), encoding="utf-8")
    if debug:
        _debug(lines, spirals, o, debug)
    return stats


def _debug(lines, spirals, o, path):
    """The plot check: each stroke in its own hue in plot order, pen-up moves in red, starts ringed."""
    w, h = o["page"]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}mm" height="{h:g}mm" viewBox="0 0 {w:g} {h:g}">',
           f'<rect width="{w:g}" height="{h:g}" fill="white"/><g fill="none" stroke-linecap="round">']
    pos = np.zeros(2)
    seq = lines + spirals
    for i, (p, cyc) in enumerate(seq):
        r, g, b = colorsys.hsv_to_rgb(0.75 * i / max(len(seq) - 1, 1), 0.9, 0.75)
        col = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
        out.append(f'<path d="M{pos[0]:.2f},{pos[1]:.2f} L{p[0][0]:.2f},{p[0][1]:.2f}" stroke="#ff2020" stroke-width="0.08"/>')
        out.append(_path(p, cyc).replace("<path", f'<path stroke="{col}" stroke-width="{o["pen"] * 0.6:.2f}"'))
        if i < len(lines):
            out.append(f'<circle cx="{p[0][0]:.2f}" cy="{p[0][1]:.2f}" r="0.5" stroke="{"#00a040" if cyc else "#000"}" stroke-width="0.12"/>')
        pos = p[0] if cyc else p[-1]
    out.append("</g></svg>")
    Path(path).write_text("\n".join(out), encoding="utf-8")


def export_scene(folder=None, prefix="", scene=None, debug=False, **opts):
    """One SVG per collection named "Plot <name>": its camera frames the page, its other objects are drawn.
    Scene custom properties plot_page_w, plot_page_h and plot_<any key of DEFAULTS> (plot_pen, plot_hidden,
    plot_outline ...) override the defaults; the same properties on a "Plot" collection override the scene for that plot. Returns {name: stats}."""
    scene = scene or bpy.context.scene
    folder = Path(folder or bpy.path.abspath("//") or ".")
    o = dict(opts)
    if "plot_page_w" in scene and "page" not in o:
        o["page"] = (float(scene["plot_page_w"]), float(scene["plot_page_h"]))
    def cast(k, v):
        return bool(v) if isinstance(DEFAULTS.get(k), bool) else int(v) if k == "hidden" else float(v)

    for k in DEFAULTS:
        if f"plot_{k}" in scene and k not in o and k != "page":
            o[k] = cast(k, scene[f"plot_{k}"])
    results = {}
    for col in bpy.data.collections:
        if not col.name.startswith("Plot "):
            continue
        cams = [ob for ob in col.all_objects if ob.type == "CAMERA"]
        if not cams:
            print(f"[out] {col.name}: no camera in the collection, skipped")
            continue
        name = col.name[5:].strip().lower().replace(" ", "-")
        path = folder / f"{prefix}{name}.svg"
        dbg = path.with_name(path.stem + "_check.svg") if debug else None
        own = {k[5:]: cast(k[5:], col[k]) for k in col.keys() if k.startswith("plot_")}  # a plot's own overrides
        results[name] = export([ob for ob in col.all_objects if ob.type != "CAMERA"], cams[0], path,
                               scene=scene, debug=dbg, **{**o, **own})
        results[name]["path"] = str(path)
        print(f"[out] {path.name}: {results[name]}")
    return results


def sheet(svgs, path, gap=0.0, paper="#efefef"):
    """Several plot SVGs side by side on one canvas. For review rasters, not for plotting."""
    import re
    parts, x, hmax = [], 0.0, 0.0
    for s in svgs:
        text = Path(s).read_text(encoding="utf-8")
        w, h = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', text).groups())
        body = text[text.index(">", text.index("<svg")) + 1:text.rindex("</svg>")]
        parts.append(f'<g transform="translate({x:g},0)">{body}</g>')
        x += w + gap
        hmax = max(hmax, h)
    x -= gap
    Path(path).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
        f'width="{x:g}mm" height="{hmax:g}mm" viewBox="0 0 {x:g} {hmax:g}">'
        f'<rect width="{x:g}" height="{hmax:g}" fill="{paper}"/>' + "".join(parts) + "</svg>", encoding="utf-8")


def contact(svgs, path, cols=6, labels=None, gap=4.0, paper="#efefef", title=None):
    """A grid of plot SVGs with a label under each. For review rasters, not for plotting."""
    import re
    cells = []
    for s in svgs:
        text = Path(s).read_text(encoding="utf-8")
        w, h = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', text).groups())
        cells.append((w, h, text[text.index(">", text.index("<svg")) + 1:text.rindex("</svg>")]))
    cw, ch = max(c[0] for c in cells), max(c[1] for c in cells)
    rows = -(-len(cells) // cols)
    top = 16.0 if title else 0.0
    W, H = cols * (cw + gap) + gap, top + rows * (ch + gap + 10) + gap
    parts = [f'<rect width="{W:g}" height="{H:g}" fill="{paper}"/>']
    if title:
        parts.append(f'<text x="{gap:g}" y="11" font-family="Helvetica, Arial, sans-serif" font-size="8" fill="#262626">{title}</text>')
    for k, (w, h, body) in enumerate(cells):
        x, y = gap + (k % cols) * (cw + gap), top + gap + (k // cols) * (ch + gap + 10)
        parts.append(f'<rect x="{x:g}" y="{y:g}" width="{cw:g}" height="{ch:g}" fill="#f7f7f5"/>')
        parts.append(f'<g transform="translate({x + (cw - w) / 2:g},{y + (ch - h) / 2:g})">{body}</g>')
        if labels:
            parts.append(f'<text x="{x:g}" y="{y + ch + 7:g}" font-family="Helvetica, Arial, sans-serif" '
                         f'font-size="5.5" fill="#262626">{labels[k]}</text>')
    Path(path).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
        f'width="{W:g}mm" height="{H:g}mm" viewBox="0 0 {W:g} {H:g}">' + "".join(parts) + "</svg>", encoding="utf-8")
    return W, H


def raster(svg, png, width=2400, paper="#efefef"):
    """SVG → PNG with Inkscape."""
    r = subprocess.run([INKSCAPE, str(svg), "--export-type=png", f"--export-filename={png}",
                        f"--export-width={width}", f"--export-background={paper}", "--export-background-opacity=1"],
                       capture_output=True, text=True)
    if not Path(png).exists():
        raise RuntimeError(f"Inkscape did not write {png}: {r.stderr[-400:]}")
    return png
