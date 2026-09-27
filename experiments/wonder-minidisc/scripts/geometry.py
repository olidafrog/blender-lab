"""Meshes for the disc, hub and case, built from outline.py polygons.

All sizes in P are millimetres or logo units (1 unit = P["mm_per_unit"] mm);
meshes come out in metres. The disc object's origin is the groove centre, so
the disc shader's object coordinates are radial about the tracks.
"""
import hashlib
import json
import math
from pathlib import Path

import bmesh
import bpy
import numpy as np

import outline

MM = 0.001


def cached_outlines(P, cache_dir):
    """Every 2D outline the build needs, cached on the parameters that shape them."""
    keys = ("case_offset", "case_close", "side_wall", "well_gap", "well_rib")
    tag = hashlib.md5(json.dumps({k: P[k] for k in keys} | {"v": 3}).encode()).hexdigest()[:10]
    f = Path(cache_dir) / f"outlines_{tag}.npz"
    if f.exists():
        z = np.load(f, allow_pickle=True)
        return {k: list(z[k]) for k in z.files}
    parts = outline.logomark_parts()
    u = 1.0 / P["mm_per_unit"]  # mm -> units
    out = {"parts": parts}
    out["outer"] = outline.offset(parts, P["case_offset"], close=P["case_close"])
    out["hollow"] = outline.offset(out["outer"], -P["side_wall"] * u)
    out["well_in"], out["well_out"] = [], []
    for p in parts:
        out["well_in"] += outline.offset([p], P["well_gap"])
        out["well_out"] += outline.offset([p], P["well_gap"] + P["well_rib"] * u)
    f.parent.mkdir(parents=True, exist_ok=True)
    arr = {k: np.array(v, dtype=object) for k, v in out.items()}
    np.savez(f, **arr)
    print(f"[out] outlines cached to {f.name}: " + ", ".join(f"{k} {len(v)}" for k, v in out.items()))
    return out


def prism(name, rings, z0, z1, scale, bevel=0.0, segments=3, centre=(0.0, 0.0)):
    """Extrude closed 2D rings (units) from z0 to z1 (metres). Optional bevel (metres) on the cap edges."""
    bm = bmesh.new()
    for r in rings:
        pts = [((x - centre[0]) * scale, (y - centre[1]) * scale) for x, y in np.asarray(r, float)]
        bot = [bm.verts.new((x, y, z0)) for x, y in pts]
        top = [bm.verts.new((x, y, z1)) for x, y in pts]
        bm.faces.new(top)
        bm.faces.new(bot[::-1])
        n = len(pts)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bm.normal_update()
    if bevel > 0:
        cap_edges = [e for e in bm.edges if len(e.link_faces) == 2 and
                     any(abs(f.normal.z) > 0.99 for f in e.link_faces) and
                     any(abs(f.normal.z) < 0.5 for f in e.link_faces)]
        bmesh.ops.bevel(bm, geom=cap_edges, offset=bevel, segments=segments, profile=0.5,
                        affect="EDGES", clamp_overlap=True)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def cylinder(name, x, y, r, z0, z1, scale, centre=(0.0, 0.0), n=48):
    ring = [(x + r * math.cos(t), y + r * math.sin(t)) for t in np.linspace(0, 2 * math.pi, n, endpoint=False)]
    return prism(name, [ring], z0, z1, scale, centre=centre)


def boolean(target, cutter, op):
    """Apply an exact boolean and delete the cutter."""
    m = target.modifiers.new("b", "BOOLEAN")
    m.operation, m.solver, m.object = op, "EXACT", cutter
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(target.evaluated_get(dg))
    target.modifiers.remove(m)
    old = target.data
    target.data = me
    bpy.data.meshes.remove(old)
    bpy.data.objects.remove(cutter)


def shade(ob, angle=35):
    """Smooth walls and bevels, flat caps, sharp edges above `angle`."""
    me = ob.data
    if hasattr(me, "set_sharp_from_angle"):
        me.set_sharp_from_angle(angle=math.radians(angle))  # also sets every face smooth, so do it first
    for f in me.polygons:
        # flat caps: a smooth n-gon interpolates its tilted rim normals across the face and renders as a dome
        f.use_smooth = abs(f.normal.z) < 0.999


def build_case(P, O):
    s = P["mm_per_unit"] * MM
    H, t = P["case_h"] * MM, P["plate"] * MM
    eps = 0.02 * MM
    zin0, zin1 = -H / 2 + t, H / 2 - t
    case = prism("Case", O["outer"], -H / 2, H / 2, s, bevel=P["edge_round"] * MM)
    boolean(case, prism("hollow", O["hollow"], zin0, zin1, s, bevel=P["inner_round"] * MM), "DIFFERENCE")
    # Ring ribs round each well: one hangs from the top shell, one stands on the bottom shell,
    # with the parting gap between. Full-height walls read as a solid slab with holes cut in it.
    rib = P["rib_h"] * MM
    ribs = []
    for k, (z0, z1) in enumerate(((zin0 - eps, zin0 + rib), (zin1 - rib, zin1 + eps))):
        r = prism(f"ribs{k}", O["well_out"], z0, z1, s)
        boolean(r, prism(f"wells{k}", O["well_in"], z0 - eps, z1 + eps, s), "DIFFERENCE")
        ribs.append(r)
    boolean(ribs[0], ribs[1], "UNION")
    walls = ribs[0]
    for i, (x, y) in enumerate(P["bosses"]):  # screw posts stay full height
        c = cylinder(f"boss{i}", x, y, P["boss_r"], zin0 - eps, zin1 + eps, s)
        boolean(walls, c, "UNION")
    boolean(case, walls, "UNION")
    for i, (x, y) in enumerate(P["bosses"]):  # screw holes from underneath
        boolean(case, cylinder(f"hole{i}", x, y, P["boss_hole_r"], -H, zin1 - 0.6 * MM, s), "DIFFERENCE")
    shade(case)
    return case


def build_disc(P, O):
    s = P["mm_per_unit"] * MM
    dt = P["disc_t"] * MM
    c = P["groove_centre"]
    parts = O["parts"]
    if P.get("round_disc"):  # debug: a real 64 mm disc, to check the shader against a CD
        r = 32.0 / P["mm_per_unit"]
        parts = [np.array([(c[0] + r * math.cos(t), c[1] + r * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 256, endpoint=False)])]
    disc = prism("Disc", parts, -dt / 2, dt / 2, s, bevel=0.12 * MM, segments=2, centre=c)
    shade(disc)
    hub = cylinder("Hub", c[0], c[1], P["hub_r"], dt / 2 - 0.05 * MM, dt / 2 + P["hub_t"] * MM, s, centre=c, n=96)
    shade(hub)
    hub.parent = disc
    disc.location = (c[0] * s, c[1] * s, 0)
    return disc, hub
