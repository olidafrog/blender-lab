"""wax-seal-chaos: pour and press the seal with Mantaflow, save the pressed liquid mesh.

    tools/blender.sh experiments/wax-seal-chaos/scripts/sim.py [--set key=value ...]

Scene at SCALE× real size (Mantaflow has no real-world size; a 34 mm blob flows like water).
Writes assets/seal_sim_<seed>_r<res>.blend holding one mesh "SealSim" at real size (metres),
floor at z = 0, die face at gap_mm. build.py loads it.
"""
import argparse
import ast
import math
import random
import sys
from pathlib import Path

import bpy

EXP = Path(__file__).resolve().parents[1]

P = {
    "seed": 2761081326,
    "tag": "",               # suffix for the output file (variants)
    "export_frame": 0,       # >0: skip the bake, export this frame from an existing cache
    "scale": 20.0,           # scene units per real unit
    "res": 200,              # resolution_max
    "volume_mm3": 1900.0,    # wax in the finished seal
    "overfill": 1.0,
    "domain_h_mm": 16.0,     # the pour must fit under the lid         # pour this much more to cover the solver's volume loss
    "lumps": 5,
    "flat": (0.35, 0.55),    # lump height / width range              # overlapping ellipsoids in the pour
    "spread_mm": 2.0,        # how far the lumps scatter from the centre
    "viscosity": 1.0,
    "gravity": 9.81,
    "fractions": True,
    "cfl": 4.0,
    "die_subframes": 3,         # slump: low = wax setting as it cools, the squeeze piles up instead of running        # High Viscosity Solver strength
    "time_scale": 0.5,
    "die_radius_mm": 13.0,
    "gap_mm": 1.4,           # die face above the paper when pressed
    "f_press_start": 18, "f_pressed": 42, "f_end": 50,
    "mesh_scale": 2,         # mesh upres
    "mesh_radius": 1.8,      # mesh_particle_radius
    "smooth": 2,             # mesh_smoothen_pos
}


def parse():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", action="append", default=[])
    for kv in ap.parse_args(argv).set:
        k, v = kv.split("=", 1)
        if k not in P:
            sys.exit(f"unknown P key: {k}")
        P[k] = ast.literal_eval(v)


def ellipsoid(name, loc, radii):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = radii
    bpy.ops.object.transform_apply(scale=True)
    return ob


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    S = P["scale"] * 0.001  # mm → scene units
    rng = random.Random(P["seed"])

    # Domain: a tight box on the floor (its bottom wall is the paper).
    W, H = 50 * S, P["domain_h_mm"] * S
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, H / 2))
    dom = bpy.context.active_object
    dom.name = "Domain"
    dom.scale = (W / 2, W / 2, H / 2)
    bpy.ops.object.transform_apply(scale=True)
    m = dom.modifiers.new("Fluid", "FLUID"); m.fluid_type = "DOMAIN"
    d = m.domain_settings
    sc.use_gravity = True
    sc.gravity = (0, 0, -P["gravity"])
    d.domain_type = "LIQUID"
    d.resolution_max = P["res"]
    d.use_viscosity, d.viscosity_value = True, P["viscosity"]
    d.use_fractions = P["fractions"]
    d.cfl_condition = P["cfl"]
    d.timesteps_max = 16
    d.time_scale = P["time_scale"]
    d.use_mesh = True
    d.mesh_scale = P["mesh_scale"]
    d.mesh_particle_radius = P["mesh_radius"]
    d.mesh_smoothen_pos = P["smooth"]
    d.cache_type = "ALL"
    cache = EXP / "renders" / f"fluid_cache_{P['seed']}_r{P['res']}{P['tag']}"
    d.cache_directory = str(cache)
    d.cache_frame_start, d.cache_frame_end = 1, P["f_end"]
    sc.frame_start, sc.frame_end = 1, P["f_end"]

    # Pour: overlapping ellipsoids, seeded, total volume ≈ volume_mm3, resting on the floor.
    lumps = []
    each = P["volume_mm3"] / P["lumps"]
    for i in range(P["lumps"]):
        a = rng.uniform(0, math.tau); rr = rng.uniform(0, P["spread_mm"])
        flat = rng.uniform(*P["flat"])                     # height / width
        r = (each * 3 / (4 * math.pi * flat)) ** (1 / 3)  # equal-volume radius in mm
        rx, ry = r * rng.uniform(0.85, 1.2), r * rng.uniform(0.85, 1.2)
        rz = r * flat
        lumps.append(ellipsoid(f"Lump{i}", (rr * math.cos(a) * S, rr * math.sin(a) * S, (rz + 0.2) * S),
                               (rx * S, ry * S, rz * S)))
    bpy.ops.object.select_all(action="DESELECT")
    for ob in lumps:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = lumps[0]
    bpy.ops.object.join()
    wax = bpy.context.active_object
    wax.name = "Pour"
    # Overlapping shells confuse the flow's inside test (most of the pour went missing):
    # voxel-remesh them into one closed surface first.
    rm = wax.modifiers.new("Union", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = 0.3 * S
    bpy.ops.object.modifier_apply(modifier="Union")
    import bmesh
    bm = bmesh.new(); bm.from_mesh(wax.data)
    vol = bm.calc_volume() / S ** 3
    bm.free()
    k = (P["volume_mm3"] * P["overfill"] / vol) ** (1 / 3)  # lumps overlap: scale the union to the target
    wax.data.transform(__import__("mathutils").Matrix.Diagonal((k, k, k, 1)))
    for v in wax.data.vertices:
        v.co.z = max(v.co.z, 0.2 * S)
    print(f"[out] pour union {vol:.0f} mm3, scaled ×{k:.2f} to {P['volume_mm3'] * P['overfill']:.0f}")
    f = wax.modifiers.new("Fluid", "FLUID"); f.fluid_type = "FLOW"
    fs = f.flow_settings
    fs.flow_type, fs.flow_behavior = "LIQUID", "GEOMETRY"
    fs.surface_distance = 0.0
    wax.hide_render = True

    # Die: a cylinder that descends to gap_mm and holds.
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=P["die_radius_mm"] * S, depth=6 * S)
    die = bpy.context.active_object
    die.name = "Die"
    e = die.modifiers.new("Fluid", "FLUID"); e.fluid_type = "EFFECTOR"
    es = e.effector_settings
    es.effector_type = "COLLISION"
    es.surface_distance = 0.0
    es.subframes = P["die_subframes"]
    z_up, z_down = (P["domain_h_mm"] - 1 + 3) * S, (P["gap_mm"] + 3) * S
    for fr, z in ((1, z_up), (P["f_press_start"], z_up), (P["f_pressed"], z_down), (P["f_end"], z_down)):
        die.location = (0, 0, z)
        die.keyframe_insert("location", frame=fr)
    act = die.animation_data.action
    try:
        fcs = act.fcurves
    except AttributeError:  # 5.x layered actions
        fcs = act.layers[0].strips[0].channelbag(act.slots[0]).fcurves
    for fc in fcs:
        for kp in fc.keyframe_points:
            kp.interpolation = "SINE"
    return sc, dom


def bake_and_export(sc, dom):
    if P["export_frame"] <= 0:
        with bpy.context.temp_override(scene=sc, active_object=dom, object=dom, selected_objects=[dom]):
            bpy.ops.fluid.free_all()
            bpy.ops.fluid.bake_all()
    sc.frame_set(P["export_frame"] or P["f_end"])
    dg = bpy.context.evaluated_depsgraph_get()
    ev = dom.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev)
    me.transform(dom.matrix_world)  # the liquid mesh is in domain-local space
    s = 1.0 / P["scale"]
    xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    print(f"[out] liquid bbox centre offset (scene units): {cx:.4f}, {cy:.4f}")
    for v in me.vertices:
        v.co.x -= cx; v.co.y -= cy
        v.co = v.co * s
    me.name = "SealSim"
    import bmesh
    bm = bmesh.new(); bm.from_mesh(me)
    print(f"[out] volume {bm.calc_volume() * 1e9:.0f} mm3 (poured {P['volume_mm3']:.0f})")
    bm.free()
    print(f"[out] sim mesh: {len(me.vertices)} verts, {len(me.polygons)} faces")
    out = EXP / "assets" / f"seal_sim_{P['seed']}_r{P['res']}{P['tag']}{'_f%d' % P['export_frame'] if P['export_frame'] else ''}.blend"
    out.parent.mkdir(exist_ok=True)
    me.use_fake_user = True
    bpy.data.libraries.write(str(out), {me}, fake_user=True)
    print(f"[out] wrote {out}")


if __name__ == "__main__":
    parse()
    sc, dom = build()
    bake_and_export(sc, dom)
    print("SIM OK")
