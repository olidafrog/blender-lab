"""wax-seal: a sealing-wax seal with a raised, swappable emblem. Builds the scene, renders, saves.

Run from the repo root:
  tools/blender.sh experiments/wax-seal/scripts/build.py --out v01 --samples 256 --scale 1
  ... --set key=value      override any value in P
  ... --save               also save output/wax-seal.blend

The seal is one live geometry-nodes heightfield ("Wax Seal" modifier on the Seal object):
rim bead + stamped field + emblem relief. The emblem is any curve or mesh object on the
modifier's Emblem input, auto-fitted to Emblem Size.
"""
import argparse
import ast
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from common import LIBRARY, enable_gpu, experiment_paths  # noqa: E402
from nodes import auto_layout, group, how_to_tweak, material_from_group  # noqa: E402
from comp import compositor, post_group, use_saved_render  # noqa: E402

EXP = experiment_paths(__file__)

# Every value a designer might tune lives here. Override with --set key=value.
# Lengths in mm unless named otherwise.
P = {
    "res_x": 1212, "res_y": 1442,       # the reference crop's size, so compare.py lines up
    # --- seal shape (GN inputs) ---
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
    # --- emblem (GN inputs) ---
    "emblem": "wonder",         # wonder (library curve) | text (a Text curve) | monkey (a mesh) — swap tests
    "emblem_size": 17.0,        # longest side
    "emblem_rotation": 0.0,     # degrees
    "emblem_x": 0.0, "emblem_y": 0.0,
    "relief": 0.45,             # height of the raised emblem (negative = pressed in)
    "bevel": 0.15,              # width of the edge rounding
    "bevel_shape": 0.7,        # 0 chamfer … 1 round
    "soften": 2,                # blur passes over the relief (mesh emblems rely on this)
    # --- wax material ---
    "wax_color": (0.71, 0.63, 0.77, 1.0),
    "roughness": 0.6,          # stamped field
    "rim_roughness": 0.65,       # rim sets matte before pressing
    "scatter_mm": 0.04,         # SSS scale; keep well under the 1.4 mm field or the colour leaks out the bottom
    "sheen": 0.35,               # satin layer on top (Coat weight)
    "sheen_roughness": 0.22,
    "micro_bump": 0.15,
    "flow_lines": 0.5,
    # --- scene ---
    "paper_color": (0.80, 0.76, 0.73, 1.0),
    "key_power": 5.0,
    "key_size": 0.12,          # small: the reference shadow edge is ~10 px           # m
    "key_azimuth": 40.0,        # degrees from +x (screen right) toward screen top
    "key_elevation": 36.0,
    "key_distance": 0.5,        # m
    "world_strength": 0.14,
    "world_color": (1.0, 0.88, 0.78, 1.0),   # warm bounce from the card: warms the shadow core
    "cam_tilt": 16.0,           # degrees off straight down
    "lens": 100.0,
    "frame_mm": 37.5,           # frame width at the seal
    "view": "Khronos PBR Neutral",
    "exposure": -0.55,
    "glow": 0.0,
    "clay": False,              # debug: grey diffuse override
    "mirror": False,            # debug: mirror override (bad normals, domes)
}

HOW_TO_TWEAK = """\
wax-seal — how to tweak

SEAL SHAPE AND EMBLEM
Select "Seal", open the Modifier panel ("Wax Seal"). Every input is live.
- Emblem: pick any object. Curves (an imported SVG) get a true bevel; meshes are
  projected from above (their top face heights) and softened by Soften.
  The object's own location/rotation/scale are ignored: it is auto-fitted.
- Emblem Size (mm, longest side), Emblem Rotation, Emblem X/Y.
- Relief (mm, negative = pressed in), Bevel (mm edge width), Bevel Shape (0 chamfer,
  1 round), Soften (blur passes).
- Rim: Rim Height, Rim Peak, Rim Blend, Stamp Radius. Outline: Wobble, Bulge, Seed.
- Detail (mm): mesh spacing. Lower for tiny emblem detail (slower).
To swap the emblem: File > Import > SVG (or any mesh), then pick it in Emblem.
Hide the source object from render.

WAX
Select Seal, Shader Editor, the "Wax" node: Colour, Roughness (field), Rim Roughness,
Scatter (mm, how far light travels inside), Micro Bump, Flow Lines.

LIGHT
"Key" area light: Power, Size. Rotate "Key Rig" empty about Z to move the light around.

POST
Compositing tab: the "Post" node updates live on the saved render.

Built by experiments/wax-seal/scripts/build.py. Changes here are lost on rebuild;
copy good values back into P.
"""


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

def seal_group():
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
    setm.inputs["Material"].default_value = bpy.data.materials["Wax"]
    L(setm.outputs[0], go.inputs["Geometry"])
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


# --- materials ---------------------------------------------------------------------------------

def wax_group():
    ng, gi, go = group("Wax", [
        ("Colour", "NodeSocketColor", P["wax_color"], None, None),
        ("Roughness", "NodeSocketFloat", P["roughness"], 0.0, 1.0),
        ("Rim Roughness", "NodeSocketFloat", P["rim_roughness"], 0.0, 1.0),
        ("Scatter", "NodeSocketFloat", P["scatter_mm"], 0.0, 10.0),        # mm
        ("Sheen", "NodeSocketFloat", P["sheen"], 0.0, 1.0),                 # satin layer
        ("Sheen Roughness", "NodeSocketFloat", P["sheen_roughness"], 0.0, 1.0),
        ("Micro Bump", "NodeSocketFloat", P["micro_bump"], 0.0, 2.0),
        ("Flow Lines", "NodeSocketFloat", P["flow_lines"], 0.0, 2.0),
    ], [("Shader", "NodeSocketShader")])
    g = G(ng); N, L, I = g.N, g.L, gi.outputs

    def attr(name):
        a = N.new("ShaderNodeAttribute"); a.attribute_name = name
        return a.outputs["Fac"]
    rim = attr("rim")
    co = N.new("ShaderNodeTexCoord").outputs["Object"]

    bsdf = N.new("ShaderNodeBsdfPrincipled")
    bsdf.subsurface_method = "RANDOM_WALK"
    L(I["Colour"], bsdf.inputs["Base Color"])
    bsdf.inputs["Subsurface Weight"].default_value = 1.0
    bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.7, 0.95)
    L(g.m("MULTIPLY", I["Scatter"], 0.001), bsdf.inputs["Subsurface Scale"])
    bsdf.inputs["IOR"].default_value = 1.5
    L(g.mix(I["Roughness"], I["Rim Roughness"], rim), bsdf.inputs["Roughness"])
    L(I["Sheen"], bsdf.inputs["Coat Weight"]); L(I["Sheen Roughness"], bsdf.inputs["Coat Roughness"])
    bsdf.inputs["Coat IOR"].default_value = 1.45

    # Micro surface: fine noise everywhere. Flow lines: hairline contours of a warped noise (curved,
    # meandering, like wax that flowed under the stamp), in patches, on the field only.
    micro = g.m("MULTIPLY", g.noise(co, 2500.0, detail=4.0), I["Micro Bump"])
    warp = N.new("ShaderNodeTexNoise"); L(co, warp.inputs["Vector"]); warp.inputs["Scale"].default_value = 40.0
    wv = g.vm("ADD", co, g.vm("SCALE", warp.outputs["Color"], scale=0.003))
    contour = g.m("ABSOLUTE", g.m("SUBTRACT", g.noise(wv, 150.0, detail=0.6), 0.5))
    line = g.m("SUBTRACT", 1.0, g.clamp01(g.m("DIVIDE", contour, 0.008)))
    sparse = g.clamp01(g.m("MULTIPLY", g.m("SUBTRACT", g.noise(co, 45.0, detail=2.0), 0.48), 5.0))
    flow = g.m("MULTIPLY", g.m("MULTIPLY", line, sparse), g.m("MULTIPLY", g.m("MULTIPLY", I["Flow Lines"], 2.5), g.m("SUBTRACT", 1.0, g.m("MAXIMUM", rim, attr("relief")))))
    bump = N.new("ShaderNodeBump")
    bump.inputs["Distance"].default_value = 0.00003
    L(g.m("ADD", micro, flow), bump.inputs["Height"])
    L(bump.outputs["Normal"], bsdf.inputs["Normal"]); L(bump.outputs["Normal"], bsdf.inputs["Coat Normal"])
    L(bsdf.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def paper_group():
    ng, gi, go = group("Paper", [
        ("Colour", "NodeSocketColor", P["paper_color"], None, None),
        ("Roughness", "NodeSocketFloat", 0.85, 0.0, 1.0),
    ], [("Shader", "NodeSocketShader")])
    g = G(ng); N, L, I = g.N, g.L, gi.outputs
    bsdf = N.new("ShaderNodeBsdfPrincipled")
    L(I["Colour"], bsdf.inputs["Base Color"]); L(I["Roughness"], bsdf.inputs["Roughness"])
    co = N.new("ShaderNodeTexCoord").outputs["Object"]
    bump = N.new("ShaderNodeBump"); bump.inputs["Distance"].default_value = 0.00002
    L(g.noise(co, 900.0, detail=6.0), bump.inputs["Height"])
    L(bump.outputs["Normal"], bsdf.inputs["Normal"])
    L(bsdf.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


# --- scene -------------------------------------------------------------------------------------

def gn_input(mod, name, value):
    """Set a geometry-nodes modifier input by its interface name (5.2: RNA properties)."""
    ident = next(i.identifier for i in mod.node_group.interface.items_tree
                 if getattr(i, "in_out", None) == "INPUT" and i.name == name)
    props = getattr(mod, "properties", None)
    if props is not None:
        getattr(props.inputs, ident).value = value
    else:
        mod[ident] = value


def load_emblem(scene):
    """The Wonder logomark curve from the library, modifiers stripped. Hidden from render:
    the seal's modifier reads its shape."""
    with bpy.data.libraries.load(str(LIBRARY / "models/wonder-logos/wonder_logos.blend")) as (_, dst):
        dst.objects = ["wonder_logomark"]
    obj = dst.objects[0]
    scene.collection.objects.link(obj)
    obj.name = "Emblem_Wonder"
    for mod in list(obj.modifiers):
        obj.modifiers.remove(mod)
    obj.data.extrude = obj.data.bevel_depth = 0.0
    obj.location = (0.06, 0, 0)
    obj.hide_render = True
    return obj


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="wip", help="render name, saved to renders/<out>.png")
    ap.add_argument("--samples", type=int, default=256)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--norender", action="store_true")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    a = ap.parse_args(argv)
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in P:
            sys.exit(f"unknown P key: {k}")
        P[k] = ast.literal_eval(v)
    return a


def post():
    ng, gi, go = post_group("Post", [
        ("Glow", "NodeSocketFloat", P["glow"], 0.0, 2.0),
    ])
    glare = ng.nodes.new("CompositorNodeGlare")
    glare.inputs["Type"].default_value = "Fog Glow"
    glare.inputs["Size"].default_value = 0.5
    ng.links.new(gi.outputs["Image"], glare.inputs["Image"])
    ng.links.new(gi.outputs["Glow"], glare.inputs["Strength"])
    ng.links.new(glare.outputs["Image"], go.inputs["Image"])
    auto_layout(ng)
    return ng


def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    enable_gpu(scene)
    scene.unit_settings.length_unit = "MILLIMETERS"

    material_from_group("Wax", wax_group())

    # Paper
    bpy.ops.mesh.primitive_plane_add(size=0.5)
    paper = bpy.context.active_object
    paper.name = "Paper"
    paper.data.materials.append(material_from_group("Paper", paper_group()))

    # Seal: an empty mesh carrying the geometry-nodes seal.
    emblem = load_emblem(scene)
    if P["emblem"] == "text":
        td = bpy.data.curves.new("Emblem_Text", "FONT"); td.body = "W&Co"; td.align_x = "CENTER"
        emblem = bpy.data.objects.new("Emblem_Text", td); scene.collection.objects.link(emblem)
        emblem.hide_render = True
    elif P["emblem"] == "monkey":
        bpy.ops.mesh.primitive_monkey_add(location=(0.1, 0, 0))
        emblem = bpy.context.active_object; emblem.hide_render = True
    mesh = bpy.data.meshes.new("Seal")
    seal = bpy.data.objects.new("Seal", mesh)
    scene.collection.objects.link(seal)
    mod = seal.modifiers.new("Wax Seal", "NODES")
    mod.node_group = seal_group()
    gn_input(mod, "Emblem", emblem)
    seal.data.materials.append(bpy.data.materials["Wax"])

    # Key light on a rig: rotate the rig about Z to move the light around the seal.
    rig = bpy.data.objects.new("Key Rig", None)
    scene.collection.objects.link(rig)
    rig.rotation_euler = (0, 0, math.radians(P["key_azimuth"]))
    kd = bpy.data.lights.new("Key", "AREA")
    kd.energy, kd.size = P["key_power"], P["key_size"]
    key = bpy.data.objects.new("Key", kd)
    scene.collection.objects.link(key)
    key.parent = rig
    el = math.radians(P["key_elevation"])
    key.location = (P["key_distance"] * math.cos(el), 0, P["key_distance"] * math.sin(el))
    key.rotation_euler = (0, math.radians(90) - el, 0)  # face the origin: local -Z toward the seal

    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = P["world_color"]
    bg.inputs["Strength"].default_value = P["world_strength"]
    scene.world = world

    # Camera: near top-down, tilted toward screen bottom; frame width set at the seal.
    tilt = math.radians(P["cam_tilt"])
    dist = P["frame_mm"] * 0.001 * P["lens"] / 36.0
    cd = bpy.data.cameras.new("Camera")
    cd.lens, cd.sensor_width, cd.sensor_fit = P["lens"], 36.0, "HORIZONTAL"
    cd.clip_start = 0.01
    cam = bpy.data.objects.new("Camera", cd)
    scene.collection.objects.link(cam)
    cam.location = (0, -dist * math.sin(tilt), dist * math.cos(tilt) + 0.0015)
    cam.rotation_euler = (tilt, 0, 0)
    scene.camera = cam

    scene.render.resolution_x, scene.render.resolution_y = P["res_x"], P["res_y"]
    scene.view_settings.view_transform = P["view"]
    scene.view_settings.exposure = P["exposure"]
    scene.cycles.use_denoising = True
    scene.cycles.sample_clamp_indirect = 5.0
    if P["clay"] or P["mirror"]:
        ov = bpy.data.materials.new("Override")
        ov.use_nodes = True
        b = ov.node_tree.nodes["Principled BSDF"]
        if P["mirror"]:
            b.inputs["Metallic"].default_value, b.inputs["Roughness"].default_value = 1.0, 0.02
        scene.view_layers[0].material_override = ov
    how_to_tweak(HOW_TO_TWEAK)
    return scene


if __name__ == "__main__":
    args = parse_args()
    scene = build_scene()
    raw = EXP["renders"] / f"{args.out}_raw.exr"
    compositor(scene, post(), raw_exr=raw)
    scene.cycles.samples = args.samples
    scene.render.resolution_percentage = round(args.scale * 100)
    if not args.norender:
        scene.render.filepath = str(EXP["renders"] / f"{args.out}.png")
        bpy.ops.render.render(write_still=True)
    if args.save:
        if not args.norender:
            use_saved_render(scene, raw, EXP["output"])
        blend = EXP["output"] / f"{EXP['name']}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        blend.with_suffix(".blend1").unlink(missing_ok=True)
    print("BUILD OK")
