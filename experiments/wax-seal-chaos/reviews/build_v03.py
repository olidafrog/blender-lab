"""wax-seal-chaos: the seal sculpted as one SDF volume (the reroll after the Mantaflow press failed),
matte-wax Sheen BRDF, sun + bounce card. Chaos seed 2761081326 (see BRIEF.md).

Run from the repo root:
  tools/blender.sh experiments/wax-seal-chaos/scripts/build.py --out v01 --samples 256 --scale 1
  ... --set key=value      override any value in P
  ... --save               also save output/wax-seal-chaos.blend
"""
import argparse
import ast
import math
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "library" / "node-groups"))
from common import LIBRARY, enable_gpu, experiment_paths  # noqa: E402
from nodes import auto_layout, group, how_to_tweak, material_from_group  # noqa: E402
from comp import compositor, post_group, use_saved_render  # noqa: E402
from build_wax_seal import G, emblem_field, gn_input  # noqa: E402

EXP = experiment_paths(__file__)

# Lengths in mm unless named otherwise.
P = {
    "res_x": 1212, "res_y": 1442,
    # --- sculpt (GN inputs; mm) ---
    "emblem_size": 17.0,
    "emblem_rotation": 0.0,
    "emblem_x": 0.0, "emblem_y": 0.0,
    "relief": 0.5,
    "bevel": 0.15,              # width of the emblem edge rounding
    "bevel_shape": 0.7,         # 0 chamfer … 1 round
    "soften": 2,
    "seal_radius": 16.2,
    "pour_height": 1.2,         # wax outside the die before the bead
    "pour_round": 1.2,          # rounded edge where the pour meets the paper
    "die_radius": 13.0,
    "die_height": 1.4,          # stamped field height
    "bead_radius": 1.9,         # squeezed-out bead (tube radius)
    "bead_height": 0.9,         # bead centre height
    "bead_gap": 0.4,            # bead centre offset outward from the die edge + radius
    "lumps": 0.15,
    "wobble": 0.09,
    "pool": 0.8,
    "pool_angle": -35.0,
    "fillet": 6,
    "smooth": 2,
    "relax": 6,                 # mesh position blur: removes voxel terraces
    "sculpt_seed": 3.0,
    "voxel": 0.06,
    "debug_stage": "",         # pour | bead_only | pour_bead | die: mesh that SDF stage instead
    # --- matte wax ---
    "wax_color": (0.66, 0.60, 0.73, 1.0),
    "roughness": 0.45,
    "roughness_var": 0.5,       # patchy roughness: low patches glint
    "diffuse_roughness": 0.8,   # Oren-Nayar: chalky, flatter falloff
    "sheen": 0.35,
    "sheen_roughness": 0.45,
    "sheen_tint": (0.95, 0.93, 1.0, 1.0),
    "scatter_mm": 0.07,
    "scatter_rgb": (1.0, 0.5, 1.2),
    "micro_bump": 0.4,
    "flow_lines": 0.5,
    # --- scene ---
    "paper_color": (0.80, 0.76, 0.73, 1.0),
    "sun_strength": 3.0,
    "sun_angle": 3.0,           # degrees; penumbra ≈ 0.05 × height
    "sun_azimuth": 40.0,        # degrees from screen right toward screen top
    "sun_elevation": 32.0,
    "bounce": 0.3,              # white card on the shadow side (0 = off); diffuse reflectance
    "bounce_size": 0.25,        # m
    "world_strength": 0.02,
    "cam_tilt": 16.0,
    "lens": 100.0,
    "frame_mm": 37.5,
    "view": "Khronos PBR Neutral",
    "exposure": 0.75,
    "glow": 0.0,
    "clay": False,
}

HOW_TO_TWEAK = """\
wax-seal-chaos — how to tweak

SEAL (live, one volume)
Select "Seal", Modifier panel, "Wax Sculpt". The seal is sculpted as a signed-distance volume:
pour ∪ bead − die − paper, then fillet and smooth; the emblem is raised on the die face.
- Emblem: any curve, text or mesh object (auto-fitted; its own transform is ignored).
  Emblem Size (mm, longest side), Rotation, X/Y, Relief (mm, negative = pressed in),
  Bevel (mm), Bevel Shape (0 chamfer, 1 round), Soften.
- Seal: Seal Radius, Pour Height, Pour Round (edge at the paper), Die Radius, Die Height.
- Bead: the squeezed-out rim. Radius, Height, Gap, Lumps, Wobble, Pool (a pooled blob) and
  Pool Angle.
- Finish: Fillet (rounds inside corners), Smooth, Seed, Voxel (mm; 0.15 to preview, 0.06 final).

WAX
Select Seal, Shader Editor, "Matte Wax" node: Colour, Roughness, Diffuse Roughness (chalky
falloff), Sheen and Sheen Roughness (velvet glow at grazing angles), Scatter (mm; 0.05-0.1),
Micro Bump, Flow Lines.

LIGHT
"Sun": Strength, Angle (bigger = softer shadow edge). Rotate "Sun Rig" about Z to move it.
"Bounce": a white card on the shadow side, hidden from the camera; move or scale it to lift
the shadow side.

Built by experiments/wax-seal-chaos/scripts/build.py; changes here are lost on rebuild.
"""


def sculpt_group(material):
    """The whole seal as one signed-distance volume: pour slab ∪ squeezed bead − die − floor, then
    fillet + smooth, then meshed; the emblem is raised on the die face. Live: every input re-sculpts."""
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
        ("Seal Radius", "NodeSocketFloat", P["seal_radius"], 8.0, 30.0),
        ("Pour Height", "NodeSocketFloat", P["pour_height"], 0.5, 4.0),
        ("Pour Round", "NodeSocketFloat", P["pour_round"], 0.2, 3.0),
        ("Die Radius", "NodeSocketFloat", P["die_radius"], 3.0, 25.0),
        ("Die Height", "NodeSocketFloat", P["die_height"], 0.3, 4.0),
        ("Bead Radius", "NodeSocketFloat", P["bead_radius"], 0.3, 4.0),
        ("Bead Height", "NodeSocketFloat", P["bead_height"], 0.0, 4.0),
        ("Bead Gap", "NodeSocketFloat", P["bead_gap"], -2.0, 3.0),
        ("Lumps", "NodeSocketFloat", P["lumps"], 0.0, 0.8),
        ("Wobble", "NodeSocketFloat", P["wobble"], 0.0, 0.3),
        ("Pool", "NodeSocketFloat", P["pool"], 0.0, 1.0),
        ("Pool Angle", "NodeSocketFloat", P["pool_angle"], -180.0, 180.0),
        ("Fillet", "NodeSocketInt", P["fillet"], 0, 20),
        ("Smooth", "NodeSocketInt", P["smooth"], 0, 10),
        ("Relax", "NodeSocketInt", P["relax"], 0, 30),
        ("Seed", "NodeSocketFloat", P["sculpt_seed"], 0.0, 1000.0),
        ("Voxel", "NodeSocketFloat", P["voxel"], 0.03, 0.4),
    ]
    ng, gi, go = group("Wax Sculpt", ins, [("Geometry", "NodeSocketGeometry")], kind="GeometryNodeTree")
    g = G(ng); N, L, I = g.N, g.L, gi.outputs
    mm = lambda k: g.m("MULTIPLY", I[k], 0.001)  # noqa: E731
    vox = mm("Voxel")

    band = g.m("CEIL", g.m("DIVIDE", 0.0008, vox))  # ~0.8 mm of band whatever the voxel

    def to_sdf(geo):
        n = N.new("GeometryNodeMeshToSDFGrid"); L(geo, n.inputs["Mesh"]); L(vox, n.inputs["Voxel Size"])
        L(band, n.inputs["Band Width"])
        return n.outputs[0]

    def sdf_op(op, a, b):
        n = N.new("GeometryNodeSDFGridBoolean"); n.operation = op
        if op == "DIFFERENCE":
            L(a, n.inputs[0]); L(b, n.inputs[1])
        else:  # union / intersect read only the multi-input Grid 2, like Mesh Boolean
            L(a, n.inputs[1]); L(b, n.inputs[1])
        return n.outputs[0]

    def offset(grid, dist):
        n = N.new("GeometryNodeSDFGridOffset"); L(grid, n.inputs["Grid"]); L(dist, n.inputs["Distance"])
        return n.outputs[0]

    def angular_noise(pos, scale, w_add):
        d = g.vm("NORMALIZE", g.xyz(*g.sep(pos)[:2], 0.0))
        return g.noise(g.vm("SCALE", d, scale=scale), 1.0, w=g.m("ADD", I["Seed"], w_add), detail=1.0, dims="4D"), d

    pool_dir = lambda: g.xyz(g.m("COSINE", g.m("RADIANS", I["Pool Angle"])), g.m("SINE", g.m("RADIANS", I["Pool Angle"])), 0.0)  # noqa: E731

    def lobe(d):  # 0..1 around the pool angle
        c = g.clamp01(g.m("DIVIDE", g.m("SUBTRACT", g.vm("DOT_PRODUCT", d, pool_dir()), 0.6), 0.4))
        return g.m("MULTIPLY", c, c)

    # 1. Pour: a wobbly outline slab, grown by Pour Round (rounded edge), floor cut later.
    circ = N.new("GeometryNodeCurvePrimitiveCircle"); circ.mode = "RADIUS"
    circ.inputs["Resolution"].default_value = 256
    L(g.m("SUBTRACT", mm("Seal Radius"), mm("Pour Round")), circ.inputs["Radius"])
    cpos = N.new("GeometryNodeInputPosition").outputs[0]
    n_out, d_out = angular_noise(cpos, 1.6, 0.0)
    k = g.m("ADD", 1.0, g.m("MULTIPLY", g.m("SUBTRACT", n_out, 0.5), g.m("MULTIPLY", I["Wobble"], 2.0)))
    k = g.m("ADD", k, g.m("MULTIPLY", g.m("MULTIPLY", I["Pool"], 0.1), lobe(d_out)))
    wob = N.new("GeometryNodeSetPosition"); L(circ.outputs["Curve"], wob.inputs["Geometry"])
    L(g.vm("SCALE", cpos, scale=k), wob.inputs["Position"])
    fill = N.new("GeometryNodeFillCurve"); L(wob.outputs[0], fill.inputs["Curve"])
    fill.inputs["Mode"].default_value = "N-gons"
    slab_h = g.m("MAXIMUM", g.m("SUBTRACT", mm("Pour Height"), mm("Pour Round")), 0.0001)
    ext = N.new("GeometryNodeExtrudeMesh"); ext.mode = "FACES"
    L(fill.outputs["Mesh"], ext.inputs["Mesh"]); ext.inputs["Offset"].default_value = (0, 0, 1)
    L(slab_h, ext.inputs["Offset Scale"])
    flip = N.new("GeometryNodeFlipFaces"); L(fill.outputs["Mesh"], flip.inputs["Mesh"])
    join = N.new("GeometryNodeJoinGeometry"); L(ext.outputs["Mesh"], join.inputs[0]); L(flip.outputs["Mesh"], join.inputs[0])
    merge = N.new("GeometryNodeMergeByDistance"); L(join.outputs[0], merge.inputs["Geometry"])
    wax = offset(to_sdf(merge.outputs[0]), mm("Pour Round"))
    stages = {"pour": wax}

    # 2. Bead: squeezed wax as a tube around the die, lumpy, with a pooled blob. A tube mesh (not
    #    point spheres): point SDFs carry a ~3-voxel band and shred under fillet/smooth.
    bc = N.new("GeometryNodeCurvePrimitiveCircle"); bc.mode = "RADIUS"
    bc.inputs["Resolution"].default_value = 720
    L(g.m("ADD", mm("Die Radius"), g.m("ADD", mm("Bead Radius"), mm("Bead Gap"))), bc.inputs["Radius"])
    ppos = N.new("GeometryNodeInputPosition").outputs[0]
    n_b, d_b = angular_noise(ppos, 1.6, 0.0)       # same noise as the outline: the bead follows it
    n_l, _ = angular_noise(ppos, 4.0, 11.0)
    kb = g.m("ADD", 1.0, g.m("MULTIPLY", g.m("SUBTRACT", n_b, 0.5), g.m("MULTIPLY", I["Wobble"], 1.2)))
    thick = g.m("ADD", 1.0, g.m("ADD",
            g.m("MULTIPLY", g.m("SUBTRACT", n_l, 0.5), g.m("MULTIPLY", I["Lumps"], 2.0)),
            g.m("MULTIPLY", I["Pool"], lobe(d_b))))
    bx, by, _ = g.sep(g.vm("SCALE", ppos, scale=kb))
    bpos = N.new("GeometryNodeSetPosition"); L(bc.outputs["Curve"], bpos.inputs["Geometry"])
    L(g.xyz(bx, by, mm("Bead Height")), bpos.inputs["Position"])
    setr = N.new("GeometryNodeSetCurveRadius"); L(bpos.outputs[0], setr.inputs["Curve"]); L(thick, setr.inputs["Radius"])
    prof = N.new("GeometryNodeCurvePrimitiveCircle"); prof.mode = "RADIUS"
    prof.inputs["Resolution"].default_value = 24; L(mm("Bead Radius"), prof.inputs["Radius"])
    tube = N.new("GeometryNodeCurveToMesh"); L(setr.outputs[0], tube.inputs["Curve"])
    L(prof.outputs["Curve"], tube.inputs["Profile Curve"])
    tube.inputs["Fill Caps"].default_value = True
    stages["bead_only"] = to_sdf(tube.outputs["Mesh"])
    wax = sdf_op("UNION", wax, stages["bead_only"])
    stages["pour_bead"] = wax

    # 3. Die and floor cut away.
    die = N.new("GeometryNodeMeshCylinder"); die.inputs["Vertices"].default_value = 256
    L(mm("Die Radius"), die.inputs["Radius"]); die.inputs["Depth"].default_value = 0.02
    td = N.new("GeometryNodeTransform"); L(die.outputs["Mesh"], td.inputs["Geometry"])
    L(g.xyz(0.0, 0.0, g.m("ADD", mm("Die Height"), 0.01)), td.inputs["Translation"])
    wax = sdf_op("DIFFERENCE", wax, to_sdf(td.outputs[0]))
    stages["die"] = wax
    fl = N.new("GeometryNodeMeshCube"); fl.inputs["Size"].default_value = (0.2, 0.2, 0.02)
    tf = N.new("GeometryNodeTransform"); L(fl.outputs["Mesh"], tf.inputs["Geometry"])
    tf.inputs["Translation"].default_value = (0, 0, -0.01)
    wax = sdf_op("DIFFERENCE", wax, to_sdf(tf.outputs[0]))

    # 5. Fillet concave corners (field to bead, emblem foot), smooth, mesh.
    wax = stages.get(P["debug_stage"], wax)
    fil = N.new("GeometryNodeSDFGridFillet"); L(wax, fil.inputs["Grid"]); L(I["Fillet"], fil.inputs["Iterations"])
    mean = N.new("GeometryNodeSDFGridMean"); L(fil.outputs[0], mean.inputs["Grid"]); L(I["Smooth"], mean.inputs["Iterations"])
    mean.inputs["Width"].default_value = 1
    mesh = N.new("GeometryNodeGridToMesh"); L(mean.outputs[0], mesh.inputs["Grid"])
    mesh.inputs["Threshold"].default_value = 0.0

    # 4. Emblem: raise the die face by the library emblem field (true round bevel; OpenVDB offsets
    #    chamfer convex corners into octagons, so the relief is not done in the SDF).
    pos = N.new("GeometryNodeInputPosition").outputs[0]
    px, py, pz = g.sep(pos)
    flat = g.xyz(px, py, 0.0)
    rs = g.vm("LENGTH", flat)
    nz = g.sep(N.new("GeometryNodeInputNormal").outputs[0])[2]
    face = g.m("MULTIPLY", g.m("LESS_THAN", rs, g.m("SUBTRACT", mm("Die Radius"), 0.0003)),
               g.m("MULTIPLY", g.m("GREATER_THAN", nz, 0.7),
                   g.m("LESS_THAN", g.m("ABSOLUTE", g.m("SUBTRACT", pz, mm("Die Height"))), 0.0002)))
    relief01 = emblem_field(g, I, flat, px, py)
    blur = N.new("GeometryNodeBlurAttribute"); blur.data_type = "FLOAT"
    L(relief01, blur.inputs["Value"]); L(I["Soften"], blur.inputs["Iterations"])
    relief01 = g.m("MULTIPLY", blur.outputs[0], face)
    # Voxel terraces: blur the meshed positions (Blender Artists fix for Volume to Mesh lumps).
    pblur = N.new("GeometryNodeBlurAttribute"); pblur.data_type = "FLOAT_VECTOR"
    L(N.new("GeometryNodeInputPosition").outputs[0], pblur.inputs["Value"]); L(I["Relax"], pblur.inputs["Iterations"])
    relax = N.new("GeometryNodeSetPosition"); L(mesh.outputs["Mesh"], relax.inputs["Geometry"])
    L(pblur.outputs[0], relax.inputs["Position"])
    setp = N.new("GeometryNodeSetPosition"); L(relax.outputs[0], setp.inputs["Geometry"])
    L(g.m("GREATER_THAN", face, 0.5), setp.inputs["Selection"])
    L(g.xyz(px, py, g.m("ADD", pz, g.m("MULTIPLY", relief01, mm("Relief")))), setp.inputs["Position"])

    # Attributes for the material.
    geo = setp.outputs[0]
    rim = g.clamp01(g.m("DIVIDE", g.m("SUBTRACT", rs, mm("Die Radius")), 0.001))
    for name, val in (("rim", rim), ("relief", relief01)):
        st = N.new("GeometryNodeStoreNamedAttribute"); st.data_type = "FLOAT"; st.domain = "POINT"
        st.inputs["Name"].default_value = name
        L(geo, st.inputs["Geometry"]); L(val, st.inputs["Value"])
        geo = st.outputs[0]
    smooth = N.new("GeometryNodeSetShadeSmooth"); L(geo, smooth.inputs["Mesh"])
    setm = N.new("GeometryNodeSetMaterial"); L(smooth.outputs[0], setm.inputs["Geometry"])
    setm.inputs["Material"].default_value = material
    L(setm.outputs[0], go.inputs["Geometry"])
    sections = {
        "Emblem": ["Emblem", "Emblem Size", "Emblem Rotation", "Emblem X", "Emblem Y", "Relief", "Bevel", "Bevel Shape", "Soften"],
        "Seal": ["Seal Radius", "Pour Height", "Pour Round", "Die Radius", "Die Height"],
        "Bead": ["Bead Radius", "Bead Height", "Bead Gap", "Lumps", "Wobble", "Pool", "Pool Angle"],
        "Finish": ["Fillet", "Smooth", "Relax", "Seed", "Voxel"],
    }
    items = {i.name: i for i in ng.interface.items_tree if getattr(i, "in_out", None) == "INPUT"}
    for title, names in sections.items():
        panel = ng.interface.new_panel(title, default_closed=title == "Finish")
        for j, n in enumerate(names):
            ng.interface.move_to_parent(items[n], panel, j)
    auto_layout(ng)
    return ng


def wax_group():
    ng, gi, go = group("Matte Wax", [
        ("Colour", "NodeSocketColor", P["wax_color"], None, None),
        ("Roughness", "NodeSocketFloat", P["roughness"], 0.0, 1.0),
        ("Roughness Variation", "NodeSocketFloat", P["roughness_var"], 0.0, 1.0),
        ("Diffuse Roughness", "NodeSocketFloat", P["diffuse_roughness"], 0.0, 1.0),
        ("Sheen", "NodeSocketFloat", P["sheen"], 0.0, 1.0),
        ("Sheen Roughness", "NodeSocketFloat", P["sheen_roughness"], 0.0, 1.0),
        ("Scatter", "NodeSocketFloat", P["scatter_mm"], 0.0, 1.0),        # mm
        ("Micro Bump", "NodeSocketFloat", P["micro_bump"], 0.0, 2.0),
        ("Flow Lines", "NodeSocketFloat", P["flow_lines"], 0.0, 2.0),
    ], [("Shader", "NodeSocketShader")])
    g = G(ng); N, L, I = g.N, g.L, gi.outputs

    def attr(name):
        a = N.new("ShaderNodeAttribute"); a.attribute_name = name
        return a.outputs["Fac"]
    rim = attr("rim")
    co = N.new("ShaderNodeTexCoord").outputs["Object"]

    b = N.new("ShaderNodeBsdfPrincipled")
    b.subsurface_method = "RANDOM_WALK"
    L(I["Colour"], b.inputs["Base Color"])
    # Roughness varies in patches (0.5–2 mm) around the set value: where it dips the rim catches glints.
    rvar = g.m("MULTIPLY", g.m("SUBTRACT", g.noise(co, 900.0, detail=2.0), 0.5), I["Roughness Variation"])
    L(g.clamp01(g.m("ADD", I["Roughness"], rvar)), b.inputs["Roughness"])
    L(I["Diffuse Roughness"], b.inputs["Diffuse Roughness"])
    L(I["Sheen"], b.inputs["Sheen Weight"]); L(I["Sheen Roughness"], b.inputs["Sheen Roughness"])
    b.inputs["Sheen Tint"].default_value = P["sheen_tint"]
    b.inputs["Subsurface Weight"].default_value = 1.0
    b.inputs["Subsurface Radius"].default_value = P["scatter_rgb"]
    L(g.m("MULTIPLY", I["Scatter"], 0.001), b.inputs["Subsurface Scale"])
    b.inputs["IOR"].default_value = 1.5

    micro = g.m("MULTIPLY", g.noise(co, 2500.0, detail=4.0), I["Micro Bump"])
    warp = N.new("ShaderNodeTexNoise"); L(co, warp.inputs["Vector"]); warp.inputs["Scale"].default_value = 40.0
    wv = g.vm("ADD", co, g.vm("SCALE", warp.outputs["Color"], scale=0.003))
    contour = g.m("ABSOLUTE", g.m("SUBTRACT", g.noise(wv, 150.0, detail=0.6), 0.5))
    line = g.m("SUBTRACT", 1.0, g.clamp01(g.m("DIVIDE", contour, 0.008)))
    sparse = g.clamp01(g.m("MULTIPLY", g.m("SUBTRACT", g.noise(co, 45.0, detail=2.0), 0.48), 5.0))
    flow = g.m("MULTIPLY", g.m("MULTIPLY", line, sparse),
               g.m("MULTIPLY", g.m("MULTIPLY", I["Flow Lines"], 2.5), g.m("SUBTRACT", 1.0, g.m("MAXIMUM", rim, attr("relief")))))
    bump = N.new("ShaderNodeBump"); bump.inputs["Distance"].default_value = 0.00003
    L(g.m("SUBTRACT", micro, flow), bump.inputs["Height"])  # flow lines cut in, not raised
    L(bump.outputs["Normal"], b.inputs["Normal"])
    L(b.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def paper_group():
    ng, gi, go = group("Paper", [
        ("Colour", "NodeSocketColor", P["paper_color"], None, None),
        ("Roughness", "NodeSocketFloat", 0.85, 0.0, 1.0),
    ], [("Shader", "NodeSocketShader")])
    g = G(ng); N, L, I = g.N, g.L, gi.outputs
    b = N.new("ShaderNodeBsdfPrincipled")
    L(I["Colour"], b.inputs["Base Color"]); L(I["Roughness"], b.inputs["Roughness"])
    co = N.new("ShaderNodeTexCoord").outputs["Object"]
    bump = N.new("ShaderNodeBump"); bump.inputs["Distance"].default_value = 0.00002
    L(g.noise(co, 900.0, detail=6.0), bump.inputs["Height"])
    L(bump.outputs["Normal"], b.inputs["Normal"])
    L(b.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def load_emblem(scene):
    with bpy.data.libraries.load(str(LIBRARY / "models/wonder-logos/wonder_logos.blend")) as (_, dst):
        dst.objects = ["wonder_logomark"]
    obj = dst.objects[0]
    scene.collection.objects.link(obj)
    obj.name = "Emblem_Wonder"
    for mod in list(obj.modifiers):
        obj.modifiers.remove(mod)
    obj.data.extrude = obj.data.bevel_depth = 0.0
    obj.data.resolution_u = 24  # the library curve is low-poly; the SDF shows facets
    for sp in obj.data.splines:  # geometry nodes read the per-spline resolution
        sp.resolution_u = 24
    obj.location = (0.06, 0, 0)
    obj.hide_render = True
    return obj


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="wip")
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
    ng, gi, go = post_group("Post", [("Glow", "NodeSocketFloat", P["glow"], 0.0, 2.0)])
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

    wax = material_from_group("Wax", wax_group())
    bpy.ops.mesh.primitive_plane_add(size=0.5)
    paper = bpy.context.active_object
    paper.name = "Paper"
    paper.data.materials.append(material_from_group("Paper", paper_group()))

    seal = bpy.data.objects.new("Seal", bpy.data.meshes.new("Seal"))
    scene.collection.objects.link(seal)
    seal.data.materials.append(wax)
    seal.location.z = 0.00003  # just off the paper (coplanar faces render black)
    mod = seal.modifiers.new("Wax Sculpt", "NODES")
    mod.node_group = sculpt_group(wax)
    gn_input(mod, "Emblem", load_emblem(scene))

    # Sun on a rig; bounce card on the shadow side, hidden from the camera.
    rig = bpy.data.objects.new("Sun Rig", None); scene.collection.objects.link(rig)
    rig.rotation_euler = (0, 0, math.radians(P["sun_azimuth"]))
    sd = bpy.data.lights.new("Sun", "SUN")
    sd.energy, sd.angle = P["sun_strength"], math.radians(P["sun_angle"])
    sun = bpy.data.objects.new("Sun", sd); scene.collection.objects.link(sun)
    sun.parent = rig
    sun.rotation_euler = (0, math.radians(90 - P["sun_elevation"]), 0)  # -Z toward the origin from +x
    if P["bounce"] > 0:
        bpy.ops.mesh.primitive_plane_add(size=P["bounce_size"])
        card = bpy.context.active_object
        card.name = "Bounce"
        a = math.radians(P["sun_azimuth"] + 180)
        card.location = (0.12 * math.cos(a), 0.12 * math.sin(a), 0.06)
        card.rotation_euler = (math.radians(90), 0, a + math.radians(90))
        card.visible_camera = False
        cm = bpy.data.materials.new("Bounce Card"); cm.use_nodes = True
        cb = cm.node_tree.nodes["Principled BSDF"]
        cb.inputs["Base Color"].default_value = (P["bounce"],) * 3 + (1,)
        cb.inputs["Roughness"].default_value = 1.0
        card.data.materials.append(cm)

    world = bpy.data.worlds.new("World"); world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (1.0, 0.95, 0.9, 1)
    bg.inputs["Strength"].default_value = P["world_strength"]
    scene.world = world

    tilt = math.radians(P["cam_tilt"])
    dist = P["frame_mm"] * 0.001 * P["lens"] / 36.0
    cd = bpy.data.cameras.new("Camera")
    cd.lens, cd.sensor_width, cd.sensor_fit, cd.clip_start = P["lens"], 36.0, "HORIZONTAL", 0.01
    cam = bpy.data.objects.new("Camera", cd); scene.collection.objects.link(cam)
    cam.location = (0, -dist * math.sin(tilt), dist * math.cos(tilt) + 0.0015)
    cam.rotation_euler = (tilt, 0, 0)
    scene.camera = cam

    scene.render.resolution_x, scene.render.resolution_y = P["res_x"], P["res_y"]
    scene.view_settings.view_transform = P["view"]
    scene.view_settings.exposure = P["exposure"]
    scene.cycles.use_denoising = True
    scene.cycles.sample_clamp_indirect = 5.0
    if P["clay"]:
        ov = bpy.data.materials.new("Override"); ov.use_nodes = True
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
