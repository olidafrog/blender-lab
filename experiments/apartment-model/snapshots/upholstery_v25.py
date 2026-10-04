"""Upholstery kit: puffed, round-edged fabric boxes with flanged seams, in metres.

A block is an axis-aligned box. Its surface is a lattice packed toward the edges, pushed onto a rounded box
(edge radius r), then each face is puffed out along its normal by a cushion profile that is 0 at the seams.
The seams are where the flat faces met: the 45 degree line of each rounded edge. A thin self-fabric flange
stands out of every seam (Swyft Model 03: a ~1 cm flange, not piping).
"""
import math

import bpy
import numpy as np

AX = {"x": 0, "y": 1, "z": 2}


def _samples(a, b, r, k, step):
    """1D lattice from a to b: k samples across each rounded band (width r), about `step` apart inside."""
    n = max(2, int(math.ceil((b - a - 2 * r) / step)))
    band = r * (1 - np.cos(np.linspace(0, math.pi / 2, k + 1)))          # dense toward the arris
    inner = np.linspace(a + r, b - r, n + 1)
    return np.unique(np.round(np.concatenate([a + band, inner, b - band[::-1]]), 7))


def block(name, lo, hi, r=0.03, puff=None, step=0.03, k=4, shape=4.0, collection=None, mat=None,
          subsurf=1, sag=None, span=None, field=None):
    """lo, hi: opposite corners (x, y, z). puff: {"+z": m, "-y": m, ...} outward bulge at the face centre.
    shape: the cushion profile exponent (higher = flatter middle, steeper fall at the seams).
    sag: {"+z": (m, centre_u, centre_v, width)} a soft dip (a seat sat in), in face-local 0-1 coords.
    span: {"+z": {"y": (a, b)}} puff a face only over part of one axis (a seat top in front of its back block).
    field: f(points) -> points, a whole-block deformation (slump, roll, wobble) applied last; give the
    block's flange the same field so it stays on its seams."""
    lo, hi = np.array(lo, float), np.array(hi, float)
    puff = puff or {}
    ax = [_samples(lo[i], hi[i], min(r, (hi[i] - lo[i]) / 2 - 1e-4), k, step) for i in range(3)]
    verts, faces, index = [], [], {}

    def vid(p):
        key = tuple(np.round(p, 6))
        if key not in index:
            index[key] = len(verts)
            verts.append(p)
        return index[key]

    for d in range(3):                                      # the two faces normal to axis d
        u, v = [i for i in range(3) if i != d]
        for side, val in ((0, lo[d]), (1, hi[d])):
            ids = np.empty((len(ax[u]), len(ax[v])), int)
            for a, pu in enumerate(ax[u]):
                for b, pv in enumerate(ax[v]):
                    p = np.zeros(3); p[d], p[u], p[v] = val, pu, pv
                    ids[a, b] = vid(p)
            for a in range(len(ax[u]) - 1):
                for b in range(len(ax[v]) - 1):
                    q = [ids[a, b], ids[a + 1, b], ids[a + 1, b + 1], ids[a, b + 1]]
                    # outward winding: flip on the low side, and for the odd axis order
                    flip = (side == 0) ^ (d == 1)
                    faces.append(q[::-1] if flip else q)
    P0 = np.array(verts)
    # round the edges: clamp into the inner box, push out to radius r
    rr = np.minimum(r, (hi - lo) / 2 - 1e-4)
    c = np.clip(P0, lo + rr, hi - rr)
    dvec = P0 - c
    nrm = np.linalg.norm(dvec / rr, axis=1, keepdims=True)
    nrm[nrm == 0] = 1
    P1 = c + dvec / nrm
    # puff each face: weight from the flat-box face coordinates (0 at the seam lines)
    out = P1.copy()
    for key, amt in puff.items():
        d = AX[key[1]]
        side = hi[d] if key[0] == "+" else lo[d]
        on = np.isclose(P0[:, d], side)
        u, v = [i for i in range(3) if i != d]
        rng_ = {u: (lo[u], hi[u]), v: (lo[v], hi[v])}
        for a_, (s0, s1) in ((span or {}).get(key, {})).items():
            rng_[AX[a_]] = (s0, s1)
        tu = np.clip((P0[:, u] - rng_[u][0]) / (rng_[u][1] - rng_[u][0]), 0, 1)
        tv = np.clip((P0[:, v] - rng_[v][0]) / (rng_[v][1] - rng_[v][0]), 0, 1)
        w = (1 - np.abs(2 * tu - 1) ** shape) * (1 - np.abs(2 * tv - 1) ** shape)
        disp = amt * w
        if sag and key in sag:
            m, cu, cv, wd = sag[key]
            disp = disp - m * np.exp(-((tu - cu) ** 2 + (tv - cv) ** 2) / (2 * wd ** 2)) * w
        # the faces' rounded margins belong to two faces; puff them by the dominant face only
        dom = np.abs(dvec[:, d]) >= np.max(np.abs(dvec), axis=1) - 1e-9
        sel = on | (dom & (np.abs(dvec[:, d]) > 0) & (np.sign(dvec[:, d]) == (1 if key[0] == "+" else -1)))
        out[sel, d] += (1 if key[0] == "+" else -1) * disp[sel]
    if field is not None:
        out = field(out)
    # seam data for the shader: distance (m) to the nearest seam on the flat box, and position along it
    seam_d = np.full(len(P0), 1e3); seam_s = np.zeros(len(P0))
    for d in range(3):
        for side in (lo[d], hi[d]):
            on = np.isclose(P0[:, d], side)
            for a in [i for i in range(3) if i != d]:
                b = 3 - d - a
                dist = np.minimum(P0[:, a] - lo[a], hi[a] - P0[:, a])
                take = on & (dist < seam_d)
                seam_d[take] = dist[take]
                seam_s[take] = P0[take, b] + 7.3 * a + 3.1 * d     # offset per seam so ripples do not line up
    me = bpy.data.meshes.new(name)
    me.from_pydata(out.tolist(), [], faces)
    me.validate()
    for key, val in (("seam_d", seam_d), ("seam_s", seam_s)):
        at = me.attributes.new(key, "FLOAT", "POINT")
        at.data.foreach_set("value", val.astype(np.float32))
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    if mat is not None:
        me.materials.append(mat)
    if subsurf:
        m = ob.modifiers.new("Subdivision", "SUBSURF")
        m.levels, m.render_levels = subsurf, subsurf
    if collection is not None:
        collection.objects.link(ob)
    return ob


def seam_paths(lo, hi, r, axis="z", n_arc=6, ear=0.0):
    """The 12 seams of a block, as (points, outward directions): a perimeter loop on each of the two faces
    normal to `axis`, and a straight run on each edge between them (box-cushion construction).
    ear: the runs carry on this far past each corner, where the stitched flanges cross into a small tab."""
    lo, hi = np.array(lo, float), np.array(hi, float)
    rr = np.minimum(r, (hi - lo) / 2 - 1e-4)
    d = AX[axis]
    u, v = [i for i in range(3) if i != d]
    s2 = 1 / math.sqrt(2)
    paths = []
    for sd in (-1, 1):
        pts, dirs = [], []
        for cu, cv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):       # arc around each corner, in order
            mid = math.atan2(cv, cu)
            for t in np.linspace(mid - math.pi / 4, mid + math.pi / 4, n_arc):
                corner = np.zeros(3); corner[d], corner[u], corner[v] = sd, cu, cv
                c = np.clip((lo + hi) / 2 + corner * 1e3, lo + rr, hi - rr)
                dirv = np.zeros(3); dirv[u], dirv[v], dirv[d] = math.cos(t) * s2, math.sin(t) * s2, sd * s2
                pts.append(c + rr * dirv); dirs.append(dirv)
        pts.append(pts[0]); dirs.append(dirs[0])
        paths.append((np.array(pts), np.array(dirs)))
    for cu, cv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):            # the runs along axis d
        h = np.zeros(3); h[u], h[v] = cu * s2, cv * s2
        pts, dirs = [], []
        c = np.clip((lo + hi) / 2 + h * 1e3, lo + rr, hi - rr)
        for t in np.linspace(lo[d] - ear, hi[d] + ear, 10):
            q = c.copy(); q[d] = t
            pts.append(q + rr * h); dirs.append(h)
        paths.append((np.array(pts), np.array(dirs)))
    return paths


def flange(name, paths, width=0.01, thick=0.003, wave=0.0015, seed=0, collection=None, mat=None, field=None):
    """A self-fabric flange on each seam: a strip standing out of the seam along the outward direction,
    `width` proud of the fabric, with a slow random wave like stitched cloth."""
    rng = np.random.default_rng(seed)
    verts, faces = [], []
    for pts, dirs in paths:
        seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        s = np.concatenate([[0], np.cumsum(seg)])
        ph = rng.random(3) * 6.28
        wob = wave * (np.sin(s * 37 + ph[0]) * 0.6 + np.sin(s * 91 + ph[1]) * 0.4)
        n0 = len(verts)
        for p, dv, w in zip(pts, dirs, wob):
            verts.append(p - dv * 0.004)                 # root, just inside the rounded fabric
            verts.append(p + dv * (width + w))
        if field is not None:
            verts[n0:] = list(field(np.array(verts[n0:])))
        for i in range(len(pts) - 1):
            a = n0 + 2 * i
            faces.append((a, a + 2, a + 3, a + 1))
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.validate()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    m = ob.modifiers.new("Thickness", "SOLIDIFY")
    m.thickness, m.offset = thick, 0.0
    m.use_rim_only = False
    b = ob.modifiers.new("Round", "BEVEL")               # a rounded section catches a highlight line
    b.width, b.segments, b.limit_method = thick * 0.45, 2, "NONE"
    m = ob.modifiers.new("Subdivision", "SUBSURF")
    m.levels = m.render_levels = 1
    if mat is not None:
        me.materials.append(mat)
    if collection is not None:
        collection.objects.link(ob)
    return ob


def slump_field(lo, hi, seed=0, wobble=0.0, wavelength=0.3, dips=(), roll=None, tuck=0.0, ripple=None):
    """A deformation for one block, zero at the floor and growing with height.
    wobble: low-frequency vector noise (m) so seams bow. dips: [(cx, cy, sx, sy, depth)] where it is sat in:
    the top sinks, seams included. roll: (front_y, depth_m, amount_m) the front of a seat rolls forward at the top.
    tuck: the foot of that front draws back this far, so the face leans under the seat's overhang.
    ripple: (front_y, depth_m, amplitude_m, wavelength_m) vertical compression folds on a +y face, strongest
    low in the middle of the face (a back block leaned on)."""
    lo, hi = np.array(lo, float), np.array(hi, float)
    rng = np.random.default_rng(seed)
    waves = [(rng.normal(size=3), rng.random() * 6.283, rng.normal(size=3)) for _ in range(4)]

    def f(p):
        p = np.array(p, float)
        h = np.clip((p[:, 2] - lo[2]) / (hi[2] - lo[2]), 0, 1)
        out = p.copy()
        if wobble:
            for k_, ph, dirv in waves:
                k_ = k_ / np.linalg.norm(k_) * 6.283 / wavelength
                out += (wobble / 2) * np.sin(p @ k_ + ph)[:, None] * (dirv / np.linalg.norm(dirv)) * h[:, None]
        for cx, cy, sx, sy, depth in dips:
            g = np.exp(-((p[:, 0] - cx) ** 2 / (2 * sx ** 2) + (p[:, 1] - cy) ** 2 / (2 * sy ** 2)))
            out[:, 2] -= depth * g * h ** 2
        if roll is not None:
            fy, dd, amt = roll
            tx = np.clip((p[:, 0] - lo[0]) / (hi[0] - lo[0]), 0, 1)
            near = np.clip((p[:, 1] - (fy - dd)) / dd, 0, 1)
            out[:, 1] += amt * h ** 3 * near * (1 - np.abs(2 * tx - 1) ** 2)
            out[:, 1] -= tuck * (1 - h) ** 1.5 * near
        if ripple is not None:
            fy, dd, amp, wl_ = ripple
            tx = np.clip((p[:, 0] - lo[0]) / (hi[0] - lo[0]), 0, 1)
            near = np.clip((p[:, 1] - (fy - dd)) / dd, 0, 1)
            ph = 6.283 * p[:, 0] / wl_ + 1.7 * np.sin(6.283 * p[:, 0] / (wl_ * 3.3) + seed)
            env = np.sin(np.pi * tx) * np.clip(1.2 - h, 0, 1)
            out[:, 1] += amp * np.sin(ph) * env * near
        return out
    return f


def rake_field(y0, z0, z1, t0, t1):
    """Taper a block along +y with height: thickness t0 at z0 (its base) to t1 at z1 (its top), measured from y0.
    A Model 03 back block is a wedge (Swyft plan drawing: ~21 cm at the seat, ~11 cm at the top)."""
    def f(p):
        p = np.array(p, float)
        h = np.clip((p[:, 2] - z0) / (z1 - z0), 0, 1)
        k = (t0 + (t1 - t0) * h) / t0
        p[:, 1] = y0 + (p[:, 1] - y0) * k
        return p
    return f


def chain(*fs):
    """Compose deformation fields, first to last; None entries are skipped."""
    fs = [f for f in fs if f is not None]
    def f(p):
        for g in fs:
            p = g(p)
        return p
    return f
