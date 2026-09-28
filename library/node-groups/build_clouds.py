"""Library cloud system: lobe-tier seed points, the "Cloud Shape" geometry-nodes group and the
"Cloud Material" / "Neon" shader groups. From experiments/clouds (knowledge/decisions/clouds.md).

    tools/blender.sh library/node-groups/build_clouds.py     # rewrites cloud_shape.blend here and
                                                             # ../materials/cloud_material.blend

Experiments import the builders:
    sys.path.insert(0, str(LIBRARY / "node-groups"))
    from build_clouds import DEFAULTS, seed_points, shape_group, cloud_material_group, volume_material, neon_group

    p = {**DEFAULTS, "seed": 11, "albedo": (1.0, 0.66, 0.72, 1.0)}
    mat = volume_material("Cloud", cloud_material_group(p))
    me = seed_points(p); me.materials.append(mat)
    ob = bpy.data.objects.new("Cloud", me); scene.collection.objects.link(ob)
    ob.modifiers.new("Cloud Shape", "NODES").node_group = shape_group(mat, p)

Scale: metres. Needs Blender 5.1+ (grid nodes). Render with Cycles, volume_bounces 64–128.
A Sun of ~15 W/m² over a sky of strength ~2; Khronos PBR Neutral keeps coloured clouds.
"""
import random
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from nodes import auto_layout, group, use  # noqa: E402

HERE = Path(__file__).resolve().parent

# Final clouds values (pink_rod preset shape, white cloud): the library defaults.
DEFAULTS = {
    # seed tiers
    "form": "puff",            # puff | cumulus (row of big lobes) | tower | plume
    "seed": 7,
    "size": 3.0,               # cloud width, m
    "aspect": (1.0, 0.8, 0.7), # x, y, z stretch of the main body
    "tiers": (14, 70, 500, 2500, 9000),               # lobes per tier, big → tiny puffs
    "tier_radius": (0.26, 0.1, 0.042, 0.018, 0.009),  # lobe radius, fraction of size
    "up_bias": 0.1,            # 0 = puffs all round, 1 = only on top
    # Cloud Shape node
    "voxel": 0.007,            # m
    "smooth": 0,
    "billow_scale": 9.0,
    "billow": 0.0,
    "edge": 0.04,
    "base_cut": -9,            # flat base height, fraction of size/2; -9 = off
    "base_soft": 0.4,          # m
    # Cloud Material node
    "albedo": (1.0, 1.0, 1.0, 1.0),
    "density": 100.0,          # per m; keep 1/density well under a lobe
    "darkness": 0.0,
    "droplet": 12.0,           # Mie µm
    "forward": 1.0,
    # Neon node
    "neon_color": (1.0, 0.35, 0.45, 1.0),
    "neon_strength": 800.0,
}


def _sphere_dir(rng, up_bias):
    while True:
        d = Vector((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1)))
        if d.length < 1e-6:
            continue
        d.normalize()
        if rng.random() < (1 - up_bias) + up_bias * max(0.0, d.z) * 1.5:
            return d


def _body(rng, form, n, r, asp, size):
    """Tier-0 lobe centres for each cloud form, in metres."""
    h = size / 2
    pts = []
    for i in range(n):
        if form == "tower":
            t = i / max(1, n - 1)                                  # stacked turrets, widening up
            z = (-0.8 + 1.9 * t) * h * asp[2]
            spread = h * (0.45 + 0.35 * t)
            pts.append(Vector((rng.gauss(0, spread * 0.5) * asp[0], rng.gauss(0, spread * 0.4) * asp[1], z)))
        elif form == "plume":
            t = rng.random()
            z = (-1.0 + 2.0 * t) * h * asp[2]
            spread = h * (0.15 + 0.55 * t)
            pts.append(Vector((rng.gauss(0, spread * 0.45), rng.gauss(0, spread * 0.45), z)))
        else:                                                      # puff, cumulus: a row of big lobes
            t = (i + 0.5) / n * 2 - 1 + rng.uniform(-0.5, 0.5) / n  # spread evenly along x
            pts.append(Vector((t * (h - r) * asp[0], rng.gauss(0, 0.25) * (h - r) * asp[1],
                               rng.gauss(0, 0.3) * (h - r) * asp[2])))
    return pts


def seed_points(p=None):
    """Lobe centres as mesh vertices with a `radius` attribute, from p (DEFAULTS keys)."""
    p = {**DEFAULTS, **(p or {})}
    rng = random.Random(p["seed"])
    size, asp = p["size"], p["aspect"]
    radii = [f * size for f in p["tier_radius"]]
    centres, rads = [], []
    for c in _body(rng, p["form"], p["tiers"][0], radii[0], asp, size):
        s = 1.0 + (0.35 * (c.z / (size / 2)) if p["form"] == "tower" else 0.0)
        centres.append(c)
        rads.append(radii[0] * rng.uniform(0.7, 1.25) * s)
    # Each finer tier sits on the exposed skin of everything so far, so it covers the
    # whole surface (lobes on lobes on lobes), not just the previous tier.
    C = np.array([tuple(c) for c in centres])
    R = np.array(rads)
    for tier in range(1, len(p["tiers"])):
        want, tries = p["tiers"][tier], 0
        added = 0
        cdf = np.cumsum(R ** 2)                # pick parents by surface area
        while added < want and tries < want * 40:
            tries += 1
            i = min(int(np.searchsorted(cdf, rng.random() * cdf[-1])), len(cdf) - 1)
            r = radii[tier] * rng.uniform(0.6, 1.4)
            d = _sphere_dir(rng, p["up_bias"])
            pt = np.array(C[i]) + np.array(d) * R[i] * rng.uniform(0.85, 1.0)
            gap = np.linalg.norm(C - pt, axis=1) - R
            gap[i] = 0.0
            if gap.min() < -0.25 * r:          # buried inside another lobe
                continue
            C = np.vstack([C, pt])
            R = np.append(R, r)
            added += 1
    centres = [Vector(c) for c in C]
    rads = list(R)
    me = bpy.data.meshes.new("Cloud")
    me.from_pydata([tuple(c) for c in centres], [], [])
    a = me.attributes.new("radius", "FLOAT", "POINT")
    a.data.foreach_set("value", rads)
    print(f"[out] seed points {len(centres)}")
    return me


# ---------------------------------------------------------------- Cloud Shape (GN)

def shape_group(material, p=None):
    """The "Cloud Shape" geometry-nodes group: lobe points → `density` grid with `material`."""
    p = {**DEFAULTS, **(p or {})}
    ng, gi, go = group("Cloud Shape", [
        ("Geometry", "NodeSocketGeometry", None, None, None),
        ("Voxel Size", "NodeSocketFloat", p["voxel"], 0.004, 0.2),
        ("Smooth", "NodeSocketInt", p["smooth"], 0, 8),
        ("Billow Scale", "NodeSocketFloat", p["billow_scale"], 0.5, 60.0),
        ("Billow", "NodeSocketFloat", p["billow"], 0.0, 1.0),
        ("Edge", "NodeSocketFloat", p["edge"], 0.005, 0.5),
        ("Base Height", "NodeSocketFloat", p["base_cut"] * p["size"] / 2, -100.0, 100.0),
        ("Base Softness", "NodeSocketFloat", p["base_soft"], 0.0, 10.0),
    ], [("Geometry", "NodeSocketGeometry")], kind="GeometryNodeTree")
    N, L = ng.nodes, ng.links

    def node(t, **ins):
        x = N.new(t)
        for k, v in ins.items():
            if hasattr(v, "bl_rna"):
                L.new(v, x.inputs[k])
            else:
                x.inputs[k].default_value = v
        return x

    def m(op, a, b=None, c=None):
        x = N.new("ShaderNodeMath")
        x.operation = op
        for i, v in enumerate((a, b, c)):
            if v is None:
                continue
            if hasattr(v, "bl_rna"):
                L.new(v, x.inputs[i])
            else:
                x.inputs[i].default_value = v
        return x.outputs[0]

    rad = N.new("GeometryNodeInputNamedAttribute")
    rad.data_type = "FLOAT"
    rad.inputs["Name"].default_value = "radius"
    pts = node("GeometryNodeMeshToPoints", Mesh=gi.outputs["Geometry"], Radius=rad.outputs[0])
    vol = node("GeometryNodePointsToVolume", Points=pts.outputs[0], Radius=rad.outputs[0],
               **{"Voxel Size": gi.outputs["Voxel Size"]})
    vol.inputs["Resolution Mode"].default_value = "Size"
    raw = node("GeometryNodeGetNamedGrid", Volume=vol.outputs[0], Name="density")
    # room for billows and the soft edge outside the lobes
    dil = node("GeometryNodeGridDilateAndErode", Grid=raw.outputs["Grid"], Steps=8)
    mean = node("GeometryNodeGridMean", Grid=dil.outputs[0], Width=2, Iterations=gi.outputs["Smooth"])
    f2g = N.new("GeometryNodeFieldToGrid")
    f2g.data_type = "FLOAT"
    f2g.grid_items.new("FLOAT", "density")
    L.new(dil.outputs[0], f2g.inputs["Topology"])
    pos = N.new("GeometryNodeInputPosition")
    smp = node("GeometryNodeSampleGrid", Grid=mean.outputs[0], Position=pos.outputs[0])
    # billows: rounded cells (1 - Voronoi F1) at two scales, plus noise to break the cells
    v1 = node("ShaderNodeTexVoronoi", Vector=pos.outputs[0], Scale=gi.outputs["Billow Scale"])
    v2 = node("ShaderNodeTexVoronoi", Vector=pos.outputs[0], Scale=m("MULTIPLY", gi.outputs["Billow Scale"], 2.3))
    nz = node("ShaderNodeTexNoise", Vector=pos.outputs[0], Scale=m("MULTIPLY", gi.outputs["Billow Scale"], 0.4), Detail=3.0)
    b = m("ADD", m("MULTIPLY", m("SUBTRACT", 1.0, v1.outputs["Distance"]), 0.6),
          m("MULTIPLY", m("SUBTRACT", 1.0, v2.outputs["Distance"]), 0.25))
    b = m("ADD", b, m("MULTIPLY", nz.outputs["Fac"], 0.3))
    field = m("MULTIPLY_ADD", m("SUBTRACT", b, 0.72), gi.outputs["Billow"], smp.outputs["Value"])
    mr = N.new("ShaderNodeMapRange")
    L.new(field, mr.inputs["Value"])
    L.new(m("SUBTRACT", 0.5, gi.outputs["Edge"]), mr.inputs["From Min"])
    L.new(m("ADD", 0.5, gi.outputs["Edge"]), mr.inputs["From Max"])
    # smoothstep-ish: square the ramp so the edge fades in softly and the core is solid
    # flat base: fade density out below Base Height over a few voxels (condensation level)
    zsep = node("ShaderNodeSeparateXYZ", Vector=pos.outputs[0])
    bnz = node("ShaderNodeTexNoise", Vector=pos.outputs[0], Scale=2.5, Detail=4.0)
    base = N.new("ShaderNodeMapRange")
    L.new(m("MULTIPLY_ADD", m("SUBTRACT", bnz.outputs["Fac"], 0.5), m("MULTIPLY", gi.outputs["Base Softness"], 1.5),
            zsep.outputs["Z"]), base.inputs["Value"])
    L.new(gi.outputs["Base Height"], base.inputs["From Min"])
    L.new(m("ADD", gi.outputs["Base Height"], gi.outputs["Base Softness"]), base.inputs["From Max"])
    L.new(m("MULTIPLY", m("POWER", mr.outputs[0], 1.5), base.outputs[0]), f2g.inputs["density"])
    store = N.new("GeometryNodeStoreNamedGrid")
    store.data_type = "FLOAT"
    store.inputs["Name"].default_value = "density"   # Cycles only rendered a grid named density
    # Field to Grid leaves a non-zero background: Cycles then fills the whole bounding box
    bg = node("GeometryNodeSetGridBackground", Grid=f2g.outputs["density"])
    L.new(bg.outputs[0], store.inputs["Grid"])
    # the volume made here carries no material: without this Cycles renders default grey smoke
    setm = node("GeometryNodeSetMaterial", Geometry=store.outputs[0])
    setm.inputs["Material"].default_value = material
    L.new(setm.outputs[0], go.inputs["Geometry"])
    auto_layout(ng)
    return ng


# ---------------------------------------------------------------- Cloud Material

def math_node(ng, op, a, b=None, c=None):
    x = ng.nodes.new("ShaderNodeMath")
    x.operation = op
    for i, v in enumerate((a, b, c)):
        if v is None:
            continue
        if hasattr(v, "bl_rna"):
            ng.links.new(v, x.inputs[i])
        else:
            x.inputs[i].default_value = v
    return x.outputs[0]


def cloud_material_group(p=None):
    """The "Cloud Material" volume group: albedo colour, density, darkness, Mie droplet."""
    p = {**DEFAULTS, **(p or {})}
    ng, gi, go = group("Cloud Material", [
        ("Colour", "NodeSocketColor", p["albedo"], None, None),
        ("Density", "NodeSocketFloat", p["density"], 0.0, 200.0),
        ("Darkness", "NodeSocketFloat", p["darkness"], 0.0, 1.0),
        ("Droplet", "NodeSocketFloat", p["droplet"], 5.0, 50.0),
        ("Forward", "NodeSocketFloat", p["forward"], 0.0, 1.0),
    ], [("Volume", "NodeSocketShader")])
    N, L = ng.nodes, ng.links
    att = N.new("ShaderNodeAttribute")
    att.attribute_type, att.attribute_name = "GEOMETRY", "density"
    dens = N.new("ShaderNodeMath")
    dens.operation = "MULTIPLY"
    L.new(att.outputs["Fac"], dens.inputs[0])
    L.new(gi.outputs["Density"], dens.inputs[1])
    mie = N.new("ShaderNodeVolumeScatter")
    mie.phase = "MIE"
    iso = N.new("ShaderNodeVolumeScatter")
    iso.phase = "HENYEY_GREENSTEIN"
    iso.inputs["Anisotropy"].default_value = 0.0
    # Colour is how the lit cloud should look. Many bounces compound the albedo, so invert
    # the multiple-scattering albedo per channel (Christensen & Burley 2015):
    # a = 1 - (4.09712 + 4.20863 C - sqrt(9.59217 + 41.6808 C + 17.7126 C^2))^2
    sep = N.new("ShaderNodeSeparateColor")
    L.new(gi.outputs["Colour"], sep.inputs[0])
    comb = N.new("ShaderNodeCombineColor")
    for ch in range(3):
        c = sep.outputs[ch]
        root = math_node(ng, "SQRT", math_node(ng, "ADD", 9.59217, math_node(ng, "ADD",
               math_node(ng, "MULTIPLY", c, 41.6808),
               math_node(ng, "MULTIPLY", math_node(ng, "MULTIPLY", c, c), 17.7126))))
        t = math_node(ng, "SUBTRACT", math_node(ng, "MULTIPLY_ADD", c, 4.20863, 4.09712), root)
        L.new(math_node(ng, "SUBTRACT", 1.0, math_node(ng, "MULTIPLY", t, t)), comb.inputs[ch])
    for sc in (mie, iso):
        L.new(dens.outputs[0], sc.inputs["Density"])
    L.new(gi.outputs["Droplet"], mie.inputs["Diameter"])
    mix = N.new("ShaderNodeMixShader")
    L.new(gi.outputs["Forward"], mix.inputs[0])
    L.new(iso.outputs[0], mix.inputs[1])
    L.new(mie.outputs[0], mix.inputs[2])
    ab = N.new("ShaderNodeVolumeAbsorption")
    ab.inputs["Color"].default_value = (0.0, 0.0, 0.0, 1.0)
    adens = N.new("ShaderNodeMath")
    adens.operation = "MULTIPLY"
    L.new(dens.outputs[0], adens.inputs[0])
    L.new(gi.outputs["Darkness"], adens.inputs[1])
    L.new(adens.outputs[0], ab.inputs["Density"])
    # Scatter Color alone only changes each channel's free path (the cloud stays white and
    # its shadows go complementary). Albedo needs absorption of 1 - albedo at the same density.
    tint = N.new("ShaderNodeVolumeAbsorption")
    L.new(comb.outputs[0], tint.inputs["Color"])
    L.new(dens.outputs[0], tint.inputs["Density"])
    add = N.new("ShaderNodeAddShader")
    L.new(mix.outputs[0], add.inputs[0])
    L.new(ab.outputs[0], add.inputs[1])
    add2 = N.new("ShaderNodeAddShader")
    L.new(add.outputs[0], add2.inputs[0])
    L.new(tint.outputs[0], add2.inputs[1])
    L.new(add2.outputs[0], go.inputs["Volume"])
    auto_layout(ng)
    return ng


def neon_group(p=None):
    p = {**DEFAULTS, **(p or {})}
    ng, gi, go = group("Neon", [
        ("Colour", "NodeSocketColor", p["neon_color"], None, None),
        ("Strength", "NodeSocketFloat", p["neon_strength"], 0.0, 5000.0),
    ], [("Shader", "NodeSocketShader")])
    em = ng.nodes.new("ShaderNodeEmission")
    ng.links.new(gi.outputs["Colour"], em.inputs["Color"])
    ng.links.new(gi.outputs["Strength"], em.inputs["Strength"])
    ng.links.new(em.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def volume_material(name, ng):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    g = use(nt, ng)
    g.width = 260
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (360, 0)
    nt.links.new(g.outputs["Volume"], out.inputs["Volume"])
    return m


if __name__ == "__main__":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mat = volume_material("cloud_material", cloud_material_group())
    mat.use_fake_user = True
    out = HERE.parent / "materials" / "cloud_material.blend"
    bpy.data.libraries.write(str(out), {mat}, path_remap="RELATIVE_ALL", fake_user=True)
    ng = shape_group(mat)
    ng.name = "cloud_shape"
    out2 = HERE / "cloud_shape.blend"
    bpy.data.libraries.write(str(out2), {ng}, path_remap="RELATIVE_ALL", fake_user=True)
    print(f"[out] wrote {out} and {out2}")
