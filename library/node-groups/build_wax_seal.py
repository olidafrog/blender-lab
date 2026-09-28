"""Library wax seal: the "Wax Seal" geometry-nodes group. A live heightfield seal (rim bead,
stamped field, emblem relief) whose emblem is any curve, text or mesh object on its Emblem input,
auto-fitted to Emblem Size. From experiments/wax-seal (knowledge/decisions/wax-seal.md).

    tools/blender.sh library/node-groups/build_wax_seal.py    # rewrites wax_seal.blend here

Experiments import the builder:
    sys.path.insert(0, str(LIBRARY / "node-groups"))
    from build_wax_seal import DEFAULTS, seal_group, gn_input

    ob = bpy.data.objects.new("Seal", bpy.data.meshes.new("Seal")); scene.collection.objects.link(ob)
    mod = ob.modifiers.new("Wax Seal", "NODES"); mod.node_group = seal_group(wax_material, {"relief": 0.6})
    gn_input(mod, "Emblem", emblem_object)

Scale: metres in the scene, inputs in mm. Needs Blender 5.x. The seal sits on z = 0, closed
underneath for random-walk SSS; keep SSS scale well under Field Height.
"""
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from nodes import auto_layout, group  # noqa: E402

HERE = Path(__file__).resolve().parent

# Final wax-seal values (lengths in mm).
DEFAULTS = {
    "seal_radius": 16.4,        # outer radius before wobble
    "oval": 1.03,               # >1 widens left-right
    "stamp_radius": 13.0,       # the stamp's circle; the rim is the wax squeezed outside it
    "field_height": 1.4,        # stamped field above the paper
    "dish": 0.08,               # field sinks this much toward the centre
    "rim_height": 2.4,          # rim bead crest
    "rim_peak": 0.3,            # 0..1 across the rim: where the crest sits (low = crest near the stamp)
    "rim_blend": 0.5,           # fillet between field and rim
    "wobble": 0.06,             # outline irregularity (fraction of radius)
    "wobble_scale": 1.6,        # lumps around the outline
    "bulge": 0.05,              # extra lobe of wax (fraction of radius)
    "bulge_angle": -35.0,       # degrees, 0 = right, -90 = bottom
    "bulge_width": 50.0,        # degrees
    "rim_lumps": 0.08,          # crest height noise (fraction)
    "pool": 0.6,                # wax pooled in the bulge: a taller, wrinkled lump (0 off)
    "flow": 0.03,               # low undulation over the whole seal
    "seed": 3.0,
    "detail": 0.045,            # grid spacing; smaller = finer relief, slower
    "emblem_size": 17.0,        # longest side
    "emblem_rotation": 0.0,     # degrees
    "emblem_x": 0.0, "emblem_y": 0.0,
    "relief": 0.45,             # height of the raised emblem (negative = pressed in)
    "bevel": 0.15,              # width of the edge rounding
    "bevel_shape": 0.7,        # 0 chamfer … 1 round
    "soften": 2,                # blur passes over the relief (mesh emblems rely on this)
}


def gn_input(mod, name, value):
    """Set a geometry-nodes modifier input by its interface name (5.2: RNA properties)."""
    ident = next(i.identifier for i in mod.node_group.interface.items_tree
                 if getattr(i, "in_out", None) == "INPUT" and i.name == name)
    props = getattr(mod, "properties", None)
    if props is not None:
        getattr(props.inputs, ident).value = value
    else:
        mod[ident] = value


# --- small node helpers -------------------------------------------------------------------------

class G:
    """Terse field maths inside one node tree."""

    def __init__(self, ng):
        self.ng, self.N, self.L = ng, ng.nodes, ng.links.new

    def _wire(self, node, vals, offset=0):
        for i, v in enumerate(vals):
            if v is None:
                continue
            s = node.inputs[i + offset]
            if hasattr(v, "is_linked"):
                self.L(v, s)
            else:
                s.default_value = v

    def m(self, op, a, b=None, c=None, clamp=False):
        n = self.N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        self._wire(n, (a, b, c))
        return n.outputs[0]

    def vm(self, op, a, b=None, scale=None):
        n = self.N.new("ShaderNodeVectorMath"); n.operation = op
        self._wire(n, (a, b))
        if scale is not None:
            self._wire(n, (scale,), offset=3)
        return n.outputs[1] if op in ("LENGTH", "DOT_PRODUCT", "DISTANCE") else n.outputs[0]

    def xyz(self, x=0.0, y=0.0, z=0.0):
        n = self.N.new("ShaderNodeCombineXYZ"); self._wire(n, (x, y, z))
        return n.outputs[0]

    def sep(self, v):
        n = self.N.new("ShaderNodeSeparateXYZ"); self.L(v, n.inputs[0])
        return n.outputs

    def mix(self, a, b, f):
        return self.m("ADD", a, self.m("MULTIPLY", self.m("SUBTRACT", b, a), f))

    def clamp01(self, a):
        return self.m("MULTIPLY", a, 1.0, clamp=True)

    def noise(self, vec, scale, w=None, detail=2.0, dims="3D"):
        n = self.N.new("ShaderNodeTexNoise"); n.noise_dimensions = dims
        self.L(vec, n.inputs["Vector"])
        self._wire(n, (scale,), offset=2)
        n.inputs["Detail"].default_value = detail
        if w is not None:
            self._wire(n, (w,), offset=1)
        return n.outputs["Fac"]


# --- geometry: the seal ------------------------------------------------------------------------

def seal_group(material, p=None):
    """The Wax Seal GN group. p overrides DEFAULTS (lengths in mm)."""
    P = {**DEFAULTS, **(p or {})}
    ins = [
        ("Emblem", "NodeSocketObject", None, None, None),
        ("Emblem Size", "NodeSocketFloat", P["emblem_size"], 1.0, 34.0),
        ("Emblem Rotation", "NodeSocketFloat", P["emblem_rotation"], -180.0, 180.0),
        ("Emblem X", "NodeSocketFloat", P["emblem_x"], -10.0, 10.0),
        ("Emblem Y", "NodeSocketFloat", P["emblem_y"], -10.0, 10.0),
        ("Relief", "NodeSocketFloat", P["relief"], -1.5, 1.5),
        ("Bevel", "NodeSocketFloat", P["bevel"], 0.02, 2.0),
        ("Bevel Shape", "NodeSocketFloat", P["bevel_shape"], 0.0, 1.0),
        ("Soften", "NodeSocketInt", P["soften"], 0, 20),
        ("Seal Radius", "NodeSocketFloat", P["seal_radius"], 5.0, 40.0),
        ("Oval", "NodeSocketFloat", P["oval"], 0.8, 1.3),
        ("Stamp Radius", "NodeSocketFloat", P["stamp_radius"], 3.0, 35.0),
        ("Field Height", "NodeSocketFloat", P["field_height"], 0.3, 4.0),
        ("Dish", "NodeSocketFloat", P["dish"], -0.5, 0.5),
        ("Rim Height", "NodeSocketFloat", P["rim_height"], 0.3, 5.0),
        ("Rim Peak", "NodeSocketFloat", P["rim_peak"], 0.1, 0.9),
        ("Rim Blend", "NodeSocketFloat", P["rim_blend"], 0.01, 2.0),
        ("Wobble", "NodeSocketFloat", P["wobble"], 0.0, 0.3),
        ("Wobble Scale", "NodeSocketFloat", P["wobble_scale"], 0.2, 6.0),
        ("Bulge", "NodeSocketFloat", P["bulge"], 0.0, 0.4),
        ("Bulge Angle", "NodeSocketFloat", P["bulge_angle"], -180.0, 180.0),
        ("Bulge Width", "NodeSocketFloat", P["bulge_width"], 10.0, 120.0),
        ("Rim Lumps", "NodeSocketFloat", P["rim_lumps"], 0.0, 0.5),
        ("Pool", "NodeSocketFloat", P["pool"], 0.0, 1.0),
        ("Flow", "NodeSocketFloat", P["flow"], 0.0, 0.3),
        ("Seed", "NodeSocketFloat", P["seed"], 0.0, 100.0),
        ("Detail", "NodeSocketFloat", P["detail"], 0.02, 0.3),
    ]
    ng, gi, go = group("Wax Seal", ins, [("Geometry", "NodeSocketGeometry")], kind="GeometryNodeTree")
    g = G(ng); N, L, I = g.N, g.L, gi.outputs
    mm = lambda s: g.m("MULTIPLY", I[s], 0.001)  # noqa: E731
    R0, Rs, D = mm("Seal Radius"), mm("Stamp Radius"), mm("Detail")

    # Grid covering the seal; the heightfield is set on its points.
    size = g.m("MULTIPLY", R0, 2.9)
    verts = g.m("ADD", g.m("DIVIDE", size, D), 1.0)
    grid = N.new("GeometryNodeMeshGrid")
    for k, v in (("Size X", size), ("Size Y", size), ("Vertices X", verts), ("Vertices Y", verts)):
        L(v, grid.inputs[k])

    pos = N.new("GeometryNodeInputPosition").outputs[0]
    px, py, _ = g.sep(pos)
    flat = g.xyz(px, py, 0.0)
    rs = g.vm("LENGTH", flat)
    dirn = g.vm("NORMALIZE", flat)
    dx, dy, _ = g.sep(dirn)

    # Outer outline radius at this angle: wobble noise around the circle, oval, one bulge lobe.
    n_out = g.noise(g.vm("SCALE", dirn, scale=I["Wobble Scale"]), 1.0, w=I["Seed"], detail=1.0, dims="4D")
    R = g.m("MULTIPLY", R0, g.m("ADD", 1.0, g.m("MULTIPLY", g.m("SUBTRACT", n_out, 0.5), g.m("MULTIPLY", I["Wobble"], 2.0))))
    R = g.m("MULTIPLY", R, g.m("ADD", 1.0, g.m("MULTIPLY", g.m("SUBTRACT", I["Oval"], 1.0), g.m("MULTIPLY", dx, dx))))
    ba = g.m("RADIANS", I["Bulge Angle"])
    bdir = g.xyz(g.m("COSINE", ba), g.m("SINE", ba), 0.0)
    cosw = g.m("COSINE", g.m("RADIANS", I["Bulge Width"]))
    lobe = g.clamp01(g.m("DIVIDE", g.m("SUBTRACT", g.vm("DOT_PRODUCT", dirn, bdir), cosw), g.m("SUBTRACT", 1.0, cosw)))
    lobe = g.m("MULTIPLY", lobe, g.m("MULTIPLY", lobe, g.m("SUBTRACT", 3.0, g.m("MULTIPLY", lobe, 2.0))))  # smoothstep
    R = g.m("ADD", R, g.m("MULTIPLY", g.m("MULTIPLY", R0, I["Bulge"]), lobe))

    # u: 0 at the stamp edge, 1 at the outer outline.
    u = g.m("DIVIDE", g.m("SUBTRACT", rs, Rs), g.m("MAXIMUM", g.m("SUBTRACT", R, Rs), 0.0005))

    # Rim bead: an elliptical arc peaking at Rim Peak, zero at both ends (vertical tangent at the paper).
    d = g.m("SUBTRACT", u, I["Rim Peak"])
    outer_side = g.m("GREATER_THAN", d, 0.0)
    half = g.mix(I["Rim Peak"], g.m("SUBTRACT", 1.0, I["Rim Peak"]), outer_side)
    t = g.m("DIVIDE", d, half)
    arc = g.m("SQRT", g.m("MAXIMUM", g.m("SUBTRACT", 1.0, g.m("MULTIPLY", t, t)), 0.0))
    n_lump = g.noise(g.vm("SCALE", flat, scale=120.0), 1.0, w=g.m("ADD", I["Seed"], 7.0), detail=0.5, dims="4D")
    crest = g.m("MULTIPLY", mm("Rim Height"),
                g.m("ADD", 1.0, g.m("MULTIPLY", g.m("SUBTRACT", n_lump, 0.5), g.m("MULTIPLY", I["Rim Lumps"], 2.0))))
    # Pool: in the bulge the crest rises, and folds (sharp creases of a warped noise) wrinkle it.
    pool = g.m("MULTIPLY", I["Pool"], lobe)
    crest = g.m("MULTIPLY", crest, g.m("ADD", 1.0, g.m("MULTIPLY", pool, 0.3)))
    n_fold = g.noise(g.vm("SCALE", flat, scale=140.0), 1.0, w=g.m("ADD", I["Seed"], 21.0), detail=0.3, dims="4D")
    fold = g.m("SUBTRACT", 1.0, g.clamp01(g.m("DIVIDE", g.m("ABSOLUTE", g.m("SUBTRACT", n_fold, 0.5)), 0.035)))
    rim = g.m("MULTIPLY", crest, arc)
    rim = g.m("SUBTRACT", rim, g.m("MULTIPLY", g.m("MULTIPLY", fold, pool), g.m("MULTIPLY", arc, 0.00012)))

    # Stamped field: flat, slightly dished, falls away just outside the stamp (hidden under the rim).
    fw = 0.0004
    fmask = g.clamp01(g.m("DIVIDE", g.m("SUBTRACT", g.m("ADD", Rs, fw), rs), fw))
    q = g.m("DIVIDE", rs, Rs)
    field = g.m("MULTIPLY", g.m("SUBTRACT", mm("Field Height"), g.m("MULTIPLY", mm("Dish"), g.m("SUBTRACT", 1.0, g.m("MULTIPLY", q, q)))), fmask)

    # Emblem relief, 0..1, from any curve or mesh object.
    relief01 = emblem_field(g, I, flat, px, py)
    inside_stamp = g.clamp01(g.m("DIVIDE", g.m("SUBTRACT", Rs, rs), 0.0005))
    blur = N.new("GeometryNodeBlurAttribute"); blur.data_type = "FLOAT"
    L(relief01, blur.inputs["Value"]); L(I["Soften"], blur.inputs["Iterations"])
    relief01 = g.m("MULTIPLY", blur.outputs[0], inside_stamp)
    field = g.m("ADD", field, g.m("MULTIPLY", relief01, mm("Relief")))

    # Smooth max of field and rim; the fillet fades out toward the outer edge so the paper line stays clean.
    k = g.m("MAXIMUM", g.m("MULTIPLY", mm("Rim Blend"), g.clamp01(g.m("MULTIPLY", g.m("SUBTRACT", 1.0, u), 3.0))), 1e-6)
    hh = g.m("DIVIDE", g.m("MAXIMUM", g.m("SUBTRACT", k, g.m("ABSOLUTE", g.m("SUBTRACT", field, rim))), 0.0), k)
    z = g.m("ADD", g.m("MAXIMUM", field, rim), g.m("MULTIPLY", g.m("MULTIPLY", hh, hh), g.m("MULTIPLY", k, 0.25)))
    # Low undulation of the whole blob.
    n_flow = g.noise(g.vm("SCALE", flat, scale=60.0), 1.0, w=g.m("ADD", I["Seed"], 13.0), detail=2.0, dims="4D")
    z = g.m("ADD", z, g.m("MULTIPLY", g.m("MULTIPLY", g.m("SUBTRACT", n_flow, 0.5), mm("Flow")), g.clamp01(g.m("MULTIPLY", z, 2000.0))))
    # Outside the outline: just under the paper.
    outside = g.m("GREATER_THAN", u, 1.0)
    z = g.mix(z, -0.0001, outside)

    setp = N.new("GeometryNodeSetPosition"); L(grid.outputs["Mesh"], setp.inputs["Geometry"])
    L(g.xyz(px, py, z), setp.inputs["Position"])

    # Attributes for the material.
    geo = setp.outputs[0]
    for name, val in (("rim", g.clamp01(g.m("MULTIPLY", u, 4.0))), ("relief", relief01)):
        st = N.new("GeometryNodeStoreNamedAttribute"); st.data_type = "FLOAT"; st.domain = "POINT"
        st.inputs["Name"].default_value = name
        L(geo, st.inputs["Geometry"]); L(val, st.inputs["Value"])
        geo = st.outputs[0]

    # A flat bottom closes the solid for random-walk SSS; the open square edge sits far under the paper.
    bot = N.new("GeometryNodeMeshGrid"); L(size, bot.inputs["Size X"]); L(size, bot.inputs["Size Y"])
    bot.inputs["Vertices X"].default_value = bot.inputs["Vertices Y"].default_value = 2
    tb = N.new("GeometryNodeTransform"); L(bot.outputs["Mesh"], tb.inputs["Geometry"])
    tb.inputs["Translation"].default_value = (0, 0, -0.0006)
    flip = N.new("GeometryNodeFlipFaces"); L(tb.outputs[0], flip.inputs["Mesh"])
    join = N.new("GeometryNodeJoinGeometry"); L(geo, join.inputs[0]); L(flip.outputs[0], join.inputs[0])
    smooth = N.new("GeometryNodeSetShadeSmooth"); L(join.outputs[0], smooth.inputs["Mesh"])
    setm = N.new("GeometryNodeSetMaterial"); L(smooth.outputs[0], setm.inputs["Geometry"])
    setm.inputs["Material"].default_value = material
    L(setm.outputs[0], go.inputs["Geometry"])
    # Modifier panel sections.
    sections = {
        "Emblem": ["Emblem", "Emblem Size", "Emblem Rotation", "Emblem X", "Emblem Y",
                   "Relief", "Bevel", "Bevel Shape", "Soften"],
        "Seal": ["Seal Radius", "Oval", "Stamp Radius", "Field Height", "Dish",
                 "Rim Height", "Rim Peak", "Rim Blend"],
        "Outline": ["Wobble", "Wobble Scale", "Bulge", "Bulge Angle", "Bulge Width",
                    "Rim Lumps", "Pool", "Flow", "Seed"],
        "Quality": ["Detail"],
    }
    items = {i.name: i for i in ng.interface.items_tree if getattr(i, "in_out", None) == "INPUT"}
    for title, names in sections.items():
        panel = ng.interface.new_panel(title, default_closed=title in ("Outline", "Quality"))
        for k, n in enumerate(names):
            ng.interface.move_to_parent(items[n], panel, k)
    auto_layout(ng)
    return ng


def emblem_field(g, I, flat, px, py):
    """0..1 relief of the Emblem object at each grid point: inside test and height from a top-down
    raycast, bevel from the distance to the outline. Curves are filled first."""
    N, L = g.N, g.L
    info = N.new("GeometryNodeObjectInfo"); info.transform_space = "ORIGINAL"
    L(I["Emblem"], info.inputs["Object"])
    real = N.new("GeometryNodeRealizeInstances"); L(info.outputs["Geometry"], real.inputs["Geometry"])
    src = real.outputs[0]

    # Fit: centre on the bounding box, scale the longest side to Emblem Size, rotate, offset.
    bb = N.new("GeometryNodeBoundBox"); L(src, bb.inputs["Geometry"])
    bb.inputs["Use Radius"].default_value = False  # curve radius (1 m by default) would pad the box
    centre = g.vm("SCALE", g.vm("ADD", bb.outputs["Min"], bb.outputs["Max"]), scale=0.5)
    ex, ey, _ = g.sep(g.vm("SUBTRACT", bb.outputs["Max"], bb.outputs["Min"]))
    s = g.m("DIVIDE", g.m("MULTIPLY", I["Emblem Size"], 0.001), g.m("MAXIMUM", g.m("MAXIMUM", ex, ey), 1e-6))
    t1 = N.new("GeometryNodeTransform"); L(src, t1.inputs["Geometry"])
    L(g.vm("SCALE", centre, scale=-1.0), t1.inputs["Translation"])
    t2 = N.new("GeometryNodeTransform"); L(t1.outputs[0], t2.inputs["Geometry"])
    L(g.xyz(0.0, 0.0, g.m("RADIANS", I["Emblem Rotation"])), t2.inputs["Rotation"])
    L(g.xyz(s, s, s), t2.inputs["Scale"])
    L(g.xyz(g.m("MULTIPLY", I["Emblem X"], 0.001), g.m("MULTIPLY", I["Emblem Y"], 0.001), 0.0), t2.inputs["Translation"])
    fit = t2.outputs[0]

    # Curves become a flat filled mesh, so curves and meshes share one path.
    ds = N.new("GeometryNodeAttributeDomainSize"); ds.component = "CURVE"; L(fit, ds.inputs["Geometry"])
    is_curve = g.m("GREATER_THAN", ds.outputs["Spline Count"], 0.5)
    fill = N.new("GeometryNodeFillCurve"); L(fit, fill.inputs["Curve"])
    sw_geo = N.new("GeometryNodeSwitch"); sw_geo.input_type = "GEOMETRY"
    L(is_curve, sw_geo.inputs["Switch"]); L(fit, sw_geo.inputs["False"]); L(fill.outputs["Mesh"], sw_geo.inputs["True"])
    mesh = sw_geo.outputs[0]

    # Top-down raycast: inside test, plus the height of a 3D mesh (a flat mesh counts as full height).
    bb2 = N.new("GeometryNodeBoundBox"); L(mesh, bb2.inputs["Geometry"])
    bb2.inputs["Use Radius"].default_value = False
    _, _, zmin = g.sep(bb2.outputs["Min"]); _, _, zmax = g.sep(bb2.outputs["Max"])
    ray = N.new("GeometryNodeRaycast"); L(mesh, ray.inputs["Target Geometry"])
    L(g.xyz(px, py, 1.0), ray.inputs["Source Position"])
    ray.inputs["Ray Direction"].default_value = (0, 0, -1)
    ray.inputs["Ray Length"].default_value = 3.0
    hit = ray.outputs["Is Hit"]
    _, _, hz = g.sep(ray.outputs["Hit Position"])
    zr = g.m("SUBTRACT", zmax, zmin)
    zn = g.clamp01(g.m("DIVIDE", g.m("SUBTRACT", hz, zmin), g.m("MAXIMUM", zr, 1e-9)))
    zn = g.mix(1.0, zn, g.m("GREATER_THAN", zr, 1e-5))

    # Bevel: distance to the open (boundary) edges, i.e. the outline of a flat shape.
    # A closed 3D mesh has none; it keeps its own profile and relies on Soften.
    nb = N.new("GeometryNodeInputMeshEdgeNeighbors")
    dele = N.new("GeometryNodeDeleteGeometry"); dele.domain = "EDGE"
    L(mesh, dele.inputs["Geometry"])
    L(g.m("SUBTRACT", 1.0, g.m("COMPARE", nb.outputs["Face Count"], 1.0, 0.5)), dele.inputs["Selection"])
    prox = N.new("GeometryNodeProximity"); prox.target_element = "EDGES"
    L(dele.outputs[0], prox.inputs["Geometry"]); L(flat, prox.inputs["Sample Position"])
    tt = g.clamp01(g.m("DIVIDE", prox.outputs["Distance"], g.m("MULTIPLY", I["Bevel"], 0.001)))
    tt = g.mix(1.0, tt, prox.outputs["Is Valid"])
    one_minus = g.m("SUBTRACT", 1.0, tt)
    rnd = g.m("SQRT", g.m("MAXIMUM", g.m("SUBTRACT", 1.0, g.m("MULTIPLY", one_minus, one_minus)), 0.0))
    profile = g.mix(tt, rnd, I["Bevel Shape"])
    return g.m("MULTIPLY", g.m("MULTIPLY", profile, zn), hit)


if __name__ == "__main__":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mat = bpy.data.materials.new("Wax Seal Placeholder")
    ng = seal_group(mat)
    out = HERE / "wax_seal.blend"
    bpy.data.libraries.write(str(out), {ng}, path_remap="RELATIVE_ALL", fake_user=True)
    print(f"[out] wrote {out}")
