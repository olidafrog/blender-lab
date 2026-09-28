"""Eclipse glow v2: the Wonder logomark in the eclipse look, as a designer hand-off .blend.

    tools/blender.sh experiments/eclipse-glow/scripts/build.py [--out NAME] [--scale 0.5]
        [--samples N] [--set key=value ...] [--save]

Reuses the v1 shader and lens (eclipse_glow.py), consolidated into:
  - material "Eclipse Glow": one group node, colour ramps inside it.
  - compositor: one "Post" group node, previewed live from the saved render EXR.
  - world: an opaque background colour. The halo mask comes from a `coverage` AOV,
    so the render no longer needs a transparent film.
5.x only (compositor group sockets). v1 (eclipse_glow.py) still runs on 4.4.
"""
import ast
import math
import sys
from pathlib import Path
from types import SimpleNamespace

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import LIBRARY, enable_gpu, experiment_paths  # noqa: E402
from comp import compositor, post_group, use_saved_render  # noqa: E402
from nodes import auto_layout, group, how_to_tweak, use  # noqa: E402
from eclipse_glow import (BODY_STOPS, COORDS, LENS, RIM_BOTTOM_STOPS, RIM_SIDE_STOPS,  # noqa: E402
                          SHADE, build_coords_group, build_shade_group, srgb)

EXP = experiment_paths(__file__)
NAME = "eclipse_logo"
REF_H = 1248  # v1 lens sizes are pixels at this frame height; everything below scales from it

P = {
    "res_x": 1200, "res_y": 1500,
    "samples": 32,
    # Logo geometry: the library logomark curve, inflated so its normals sweep the colour bands.
    "puff": 0.09,            # m, half the thickness (the final GLB is 0.18 m thick)
    "roundness": 0.06,       # m, edge radius (final GLB: 0.03; 0.06 catches more rim light); = puff for a full dome
    "detail": 0.005,         # m, voxel size of the inflated mesh
    "tilt_x": 0.0,           # degrees; tips the logo so the faces catch the gradient
    "tilt_y": 0.0,
    "frame_fill": 0.62,      # logo width as a fraction of frame width
    "background": (6, 5, 4),  # sRGB 0-255, the world colour
    # Material (one node)
    "brightness": SHADE["Brightness"],
    "gradient_offset": COORDS["Gradient Offset"],
    "gradient_angle": COORDS["Gradient Angle"],
    "shape_gradient": 0.7,
    "rim": SHADE["Rim Strength"],
    "arc": SHADE["Arc Strength"],
    "halo_light": SHADE["Halo Strength"],
    "arc_light": SHADE["Arc Glow Strength"],
    # Post (one node)
    "cap_start": 0.8,                  # shape_v where a shape's top cap begins (crescent mask)
    "crescent_glow_px": 12,            # v1: 28; thinner arc on the logo
    "crescent_glow_amount": 0.6,       # v1: 1.1
    "glow_key": (0.25, 0.7),           # luminance range that feeds the self-glow (below = none)
    "glow_tint": (255, 110, 50),       # sRGB, multiplies the glowing colours towards orange
    "glow_px": (30, 90),               # v1 px at REF_H: near and far blur
    "glow_far": 0.7,
    "glow_amount": 2.0,
    "halo": 1.0,
    "halo_reach": 1.0,
    "arc_glow": 1.0,
    "crescent": LENS["crescent_amount"],
    "crescent_lift": 100.0 * LENS["crescent_lift_px"] / REF_H,  # % of frame height
    "bloom": 1.0 - min(max(-LENS["glow_mix"], 0.0), 1.0),
    "dispersion": LENS["dispersion"],
    "grain": LENS["grain"],
}


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    a = {"out": "wip", "scale": 1.0, "samples": None, "save": "--save" in argv}
    for i, k in enumerate(argv):
        if k == "--set":
            key, v = argv[i + 1].split("=", 1)
            P[key] = ast.literal_eval(v) if isinstance(P[key], tuple) else type(P[key])(v)
        elif k in ("--out", "--scale", "--samples"):
            a[k[2:]] = argv[i + 1]
    a["scale"] = float(a["scale"])
    a["samples"] = int(a["samples"]) if a["samples"] else P["samples"]
    return a


# --- Logo ----------------------------------------------------------------------------------------

def shade_group():
    """Material + smooth shading, edges sharper than 40 degrees kept crisp.
    The library's geometry-nodes mesh carries its own empty material slot, so the curve's
    material never reaches the render; Set Material assigns it here."""
    ng, gi, go = group("Shade Logo", [("Geometry", "NodeSocketGeometry", None, None, None),
                                      ("Material", "NodeSocketMaterial", None, None, None)],
                       [("Geometry", "NodeSocketGeometry")], kind="GeometryNodeTree")
    faces = ng.nodes.new("GeometryNodeSetShadeSmooth"); faces.domain = "FACE"
    edges = ng.nodes.new("GeometryNodeSetShadeSmooth"); edges.domain = "EDGE"
    ang = ng.nodes.new("GeometryNodeInputMeshEdgeAngle")
    cmp = ng.nodes.new("FunctionNodeCompare"); cmp.operation = "LESS_THAN"
    cmp.inputs["B"].default_value = math.radians(40)
    L = ng.links.new
    L(gi.outputs["Geometry"], faces.inputs["Geometry"])
    L(faces.outputs["Geometry"], edges.inputs["Geometry"])
    L(ang.outputs["Unsigned Angle"], cmp.inputs["A"])
    L(cmp.outputs["Result"], edges.inputs["Shade Smooth"])
    mat = ng.nodes.new("GeometryNodeSetMaterial")
    L(edges.outputs["Geometry"], mat.inputs["Geometry"])
    L(gi.outputs["Material"], mat.inputs["Material"])
    L(mat.outputs["Geometry"], go.inputs["Geometry"])
    auto_layout(ng)
    return ng


def gn_input(mod, name, value):
    """Set a geometry-nodes modifier input by its interface name (5.2: RNA properties)."""
    ident = next(i.identifier for i in mod.node_group.interface.items_tree
                 if getattr(i, "in_out", None) == "INPUT" and i.name == name)
    props = getattr(mod, "properties", None)
    if props is not None:  # 5.2+: mod.properties.inputs.<identifier>.value
        getattr(props.inputs, ident).value = value
    else:
        mod[ident] = value


def inflate_group():
    """Logo curve → closed slab → dense voxel mesh → each point lifted by a round profile of its
    distance to the outline. The result is a pillow: no flat faces, so camera-space normals sweep
    the whole gradient across every stroke, as they do on the v1 sphere."""
    ng, gi, go = group("Inflate Logo", [
        ("Curve", "NodeSocketGeometry", None, None, None),
        ("Puff", "NodeSocketFloat", P["puff"], 0.01, 0.3),              # m, half the thickness
        ("Roundness", "NodeSocketFloat", P["roundness"], 0.005, 0.3),   # m, edge radius (capped at Puff)
        ("Detail", "NodeSocketFloat", P["detail"], 0.002, 0.03),        # m, voxel size (smaller = finer, slower)
    ], [("Geometry", "NodeSocketGeometry")], kind="GeometryNodeTree")
    N, L, I = ng.nodes, ng.links.new, gi.outputs

    def m(op, a, b=None):
        n = N.new("ShaderNodeMath"); n.operation = op
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            L(v, n.inputs[i]) if hasattr(v, "is_linked") else setattr(n.inputs[i], "default_value", v)
        return n.outputs[0]

    # Closed slab, 2 × Puff thick, centred on z = 0.
    fill = N.new("GeometryNodeFillCurve"); L(I["Curve"], fill.inputs["Curve"])
    ext = N.new("GeometryNodeExtrudeMesh"); ext.mode = "FACES"
    ext.inputs["Offset"].default_value = (0, 0, 1)
    L(fill.outputs["Mesh"], ext.inputs["Mesh"]); L(m("MULTIPLY", I["Puff"], 2.0), ext.inputs["Offset Scale"])
    flip = N.new("GeometryNodeFlipFaces"); L(fill.outputs["Mesh"], flip.inputs["Mesh"])
    join = N.new("GeometryNodeJoinGeometry")
    L(ext.outputs["Mesh"], join.inputs[0]); L(flip.outputs["Mesh"], join.inputs[0])
    move = N.new("GeometryNodeTransform"); L(join.outputs[0], move.inputs["Geometry"])
    off = N.new("ShaderNodeCombineXYZ"); L(m("MULTIPLY", I["Puff"], -1.0), off.inputs["Z"])
    L(off.outputs[0], move.inputs["Translation"])
    # Dense, even mesh from the slab's distance field.
    sdf = N.new("GeometryNodeMeshToSDFGrid"); L(move.outputs[0], sdf.inputs["Mesh"])
    L(I["Detail"], sdf.inputs["Voxel Size"])
    dense = N.new("GeometryNodeGridToMesh"); L(sdf.outputs[0], dense.inputs["Grid"])
    dense.inputs["Threshold"].default_value = 0.0  # SDF surface; the 0.1 default is for density grids
    # Distance of each point (flattened to z = 0) to the outline.
    outline = N.new("GeometryNodeCurveToMesh"); L(I["Curve"], outline.inputs["Curve"])
    prox = N.new("GeometryNodeProximity"); prox.target_element = "EDGES"
    L(outline.outputs["Mesh"], prox.inputs["Geometry"])
    pos = N.new("GeometryNodeInputPosition")
    sep = N.new("ShaderNodeSeparateXYZ"); L(pos.outputs[0], sep.inputs[0])
    flat = N.new("ShaderNodeCombineXYZ"); L(sep.outputs["X"], flat.inputs["X"]); L(sep.outputs["Y"], flat.inputs["Y"])
    L(flat.outputs[0], prox.inputs["Sample Position"])
    # Profile = straight wall up to (Puff − R), then a quarter-round of radius R:
    # |z| = min(|z|, Puff − R) + sqrt(R² − (R − min(d, R))²). R = Puff gives a full dome.
    R = m("MINIMUM", I["Roundness"], I["Puff"])
    t = m("SUBTRACT", R, m("MINIMUM", prox.outputs["Distance"], R))
    arc = m("SQRT", m("MAXIMUM", m("SUBTRACT", m("MULTIPLY", R, R), m("MULTIPLY", t, t)), 0.0))
    wall = m("MINIMUM", m("ABSOLUTE", sep.outputs["Z"]), m("SUBTRACT", I["Puff"], R))
    z = m("MULTIPLY", m("ADD", wall, arc), m("SIGN", sep.outputs["Z"]))
    new_pos = N.new("ShaderNodeCombineXYZ")
    L(sep.outputs["X"], new_pos.inputs["X"]); L(sep.outputs["Y"], new_pos.inputs["Y"]); L(z, new_pos.inputs["Z"])
    setp = N.new("GeometryNodeSetPosition"); L(dense.outputs["Mesh"], setp.inputs["Geometry"])
    L(new_pos.outputs[0], setp.inputs["Position"])
    # shape_v: 0 at the bottom of each separate shape, 1 at its top. The material blends it with
    # the normal-based gradient so broad faces still run the full sunset (Shape Gradient).
    isl = N.new("GeometryNodeInputMeshIsland")
    mm = N.new("GeometryNodeFieldMinAndMax"); mm.domain = "POINT"
    L(sep.outputs["Y"], mm.inputs["Value"]); L(isl.outputs["Island Index"], mm.inputs["Group ID"])
    rng = N.new("ShaderNodeMapRange")
    L(sep.outputs["Y"], rng.inputs["Value"]); L(mm.outputs["Min"], rng.inputs["From Min"])
    L(mm.outputs["Max"], rng.inputs["From Max"])
    store = N.new("GeometryNodeStoreNamedAttribute"); store.data_type = "FLOAT"; store.domain = "POINT"
    store.inputs["Name"].default_value = "shape_v"
    L(setp.outputs[0], store.inputs["Geometry"]); L(rng.outputs["Result"], store.inputs["Value"])
    L(store.outputs[0], go.inputs["Geometry"])
    auto_layout(ng)
    return ng


def add_logo(scene):
    """The library logomark curve. Its Extrude/Bevel modifiers are swapped for Inflate on this copy;
    the library file is untouched."""
    with bpy.data.libraries.load(str(LIBRARY / "models/wonder-logos/wonder_logos.blend")) as (_, dst):
        dst.objects = ["wonder_logomark"]
    obj = dst.objects[0]
    scene.collection.objects.link(obj)
    obj.name = "Logo"
    obj.location = (0, 0, 0)
    for mod in list(obj.modifiers):
        obj.modifiers.remove(mod)
    inf = obj.modifiers.new("Inflate", "NODES"); inf.node_group = inflate_group()
    sm = obj.modifiers.new("Shade", "NODES"); sm.node_group = shade_group()
    obj.rotation_euler = (math.radians(P["tilt_x"]), math.radians(P["tilt_y"]), 0)
    return obj


# --- Material: one node --------------------------------------------------------------------------

def eclipse_group():
    """One group: the v1 coords + ramps + shade, with the look controls on its face."""
    ng, gi, go = group("Eclipse Glow", [
        ("Brightness", "NodeSocketFloat", P["brightness"], 0.0, 3.0),            # overall emission
        ("Gradient Offset", "NodeSocketFloat", P["gradient_offset"], -0.5, 0.5),  # slide the bands up/down
        ("Gradient Angle", "NodeSocketFloat", P["gradient_angle"], -180.0, 180.0),  # degrees, rotate the sunset
        ("Shape Gradient", "NodeSocketFloat", P["shape_gradient"], 0.0, 1.0),  # 0 = surface angle only, 1 = each shape bottom → top
        ("Rim", "NodeSocketFloat", P["rim"], 0.0, 1.0),                          # spectral edge colour
        ("Arc", "NodeSocketFloat", P["arc"], 0.0, 2.0),                          # bright top arc line
        ("Halo Light", "NodeSocketFloat", P["halo_light"], 0.0, 30.0),           # edge light fed to the halo
        ("Arc Light", "NodeSocketFloat", P["arc_light"], 0.0, 15.0),             # light fed to the arc glow
    ], [("Shader", "NodeSocketShader"), ("Halo", "NodeSocketColor"), ("Arc Glow", "NodeSocketColor")])
    t, L = ng, ng.links.new

    coords = use(t, build_coords_group(), "Coords")
    for k, v in COORDS.items():
        coords.inputs[k].default_value = v
    L(gi.outputs["Gradient Offset"], coords.inputs["Gradient Offset"])
    L(gi.outputs["Gradient Angle"], coords.inputs["Gradient Angle"])

    def ramp(label, stops, fac, alpha=False):
        r = t.nodes.new("ShaderNodeValToRGB"); r.label = label; r.width = 320
        cr = r.color_ramp
        while len(cr.elements) > 1:
            cr.elements.remove(cr.elements[-1])
        for i, s in enumerate(stops):
            e = cr.elements[0] if i == 0 else cr.elements.new(s[0])
            e.position = s[0]
            e.color = srgb(*s[1], s[2] if alpha else 1.0)
        L(fac, r.inputs["Fac"])
        return r

    # Body position: the normal-based Vertical blended with the shape's own bottom → top (shape_v,
    # written by the Inflate modifier; objects without it read 0 there, so keep Shape Gradient at 0).
    attr = t.nodes.new("ShaderNodeAttribute"); attr.attribute_name = "shape_v"
    shifted = t.nodes.new("ShaderNodeMath"); shifted.operation = "ADD"
    L(attr.outputs["Fac"], shifted.inputs[0]); L(gi.outputs["Gradient Offset"], shifted.inputs[1])
    vmix = t.nodes.new("ShaderNodeMix"); vmix.data_type = "FLOAT"; vmix.clamp_result = True
    L(gi.outputs["Shape Gradient"], vmix.inputs[0])
    L(coords.outputs["Vertical"], vmix.inputs[2]); L(shifted.outputs[0], vmix.inputs[3])
    body = ramp("Body Colours (bottom → top)", BODY_STOPS, vmix.outputs[0])
    side = ramp("Rim Sides (centre → edge; alpha = coverage)", RIM_SIDE_STOPS, coords.outputs["Edge"], True)
    bot = ramp("Rim Bottom (centre → edge; alpha = coverage)", RIM_BOTTOM_STOPS, coords.outputs["Edge"], True)

    shade = use(t, build_shade_group(), "Shade")
    for k, v in SHADE.items():
        shade.inputs[k].default_value = v
    L(body.outputs["Color"], shade.inputs["Body Color"])
    L(side.outputs["Color"], shade.inputs["Rim Side Color"])
    L(side.outputs["Alpha"], shade.inputs["Rim Side Alpha"])
    L(bot.outputs["Color"], shade.inputs["Rim Bottom Color"])
    L(bot.outputs["Alpha"], shade.inputs["Rim Bottom Alpha"])
    for k in ("Signed Vertical", "Signed Horizontal", "Edge", "Curved Vertical"):
        L(coords.outputs[k], shade.inputs[k])
    for face, inner in (("Brightness", "Brightness"), ("Rim", "Rim Strength"), ("Halo Light", "Halo Strength")):
        L(gi.outputs[face], shade.inputs[inner])
    # Arcs only on each shape's top cap: an up-facing ledge mid-shape (the logo's steps) would
    # otherwise get its own bright arc line. Weighted by Shape Gradient, so 0 keeps the v1 behaviour.
    cap = t.nodes.new("ShaderNodeMapRange"); cap.label = "Top Cap"
    cap.inputs["From Min"].default_value, cap.inputs["From Max"].default_value = P["cap_start"], 1.0
    L(attr.outputs["Fac"], cap.inputs["Value"])
    gate = t.nodes.new("ShaderNodeMix"); gate.data_type = "FLOAT"; gate.label = "Arc Gate"
    L(gi.outputs["Shape Gradient"], gate.inputs[0]); gate.inputs[2].default_value = 1.0
    L(cap.outputs["Result"], gate.inputs[3])
    for face, inner in (("Arc", "Arc Strength"), ("Arc Light", "Arc Glow Strength")):
        mul = t.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
        L(gi.outputs[face], mul.inputs[0]); L(gate.outputs[0], mul.inputs[1])
        L(mul.outputs[0], shade.inputs[inner])
    for s in ("Shader", "Halo", "Arc Glow"):
        L(shade.outputs[s], go.inputs[s])
    auto_layout(ng, dx=380, dy=260)
    return ng


def build_material():
    m = bpy.data.materials.new("Eclipse Glow")
    m.use_nodes = True
    t = m.node_tree
    t.nodes.clear()
    g = use(t, eclipse_group()); g.width = 260
    out = t.nodes.new("ShaderNodeOutputMaterial"); out.location = (360, 120)
    t.links.new(g.outputs["Shader"], out.inputs["Surface"])
    # AOVs for the compositor: glow sources plus a coverage mask (1 on the object).
    for i, (aov_name, sock) in enumerate((("halo", "Halo"), ("arc_glow", "Arc Glow"), ("coverage", None))):
        aov = t.nodes.new("ShaderNodeOutputAOV"); aov.aov_name = aov_name
        aov.location = (360, -40 - 140 * i)
        if sock:
            t.links.new(g.outputs[sock], aov.inputs["Color"])
        else:
            aov.inputs["Value"].default_value = 1.0
    # height: 0 at the bottom of each shape, 1 at its top (shape_v from Inflate). The compositor uses
    # it to keep the crescent on the top caps and to weight the halo towards the bottoms.
    attr = t.nodes.new("ShaderNodeAttribute"); attr.attribute_name = "shape_v"; attr.location = (0, -520)
    h = t.nodes.new("ShaderNodeOutputAOV"); h.aov_name = "height"; h.location = (360, -520)
    t.links.new(attr.outputs["Fac"], h.inputs["Value"])
    return m


# --- Post: one node ------------------------------------------------------------------------------

def post(frame_h, extra=(), pre=None, stage=None):
    """frame_h: render height in pixels; glow sizes scale with it.
    extra: more designer inputs (group tuples). pre(H, S) → S: rewrites the passes before the glows
    (S maps pass input name → socket). stage(H, col) → col: runs after the glows, before bloom.
    H holds the helpers (N, L, I, math, mix, blur, px). Both unused for the still."""
    ng, gi, go = post_group("Post", [
        ("Coverage Pass", "NodeSocketColor", None, None, None),
        ("Halo Pass", "NodeSocketColor", None, None, None),
        ("Arc Glow Pass", "NodeSocketColor", None, None, None),
        ("Height Pass", "NodeSocketColor", None, None, None),
        ("Halo", "NodeSocketFloat", P["halo"], 0.0, 3.0),                   # glow around the silhouette
        ("Halo Reach", "NodeSocketFloat", P["halo_reach"], 0.25, 3.0),      # 1 = v1 spread
        ("Arc Glow", "NodeSocketFloat", P["arc_glow"], 0.0, 3.0),           # bloom off the top arcs
        ("Crescent", "NodeSocketFloat", P["crescent"], 0.0, 2.0),           # the lifted eclipse outline
        ("Crescent Lift", "NodeSocketFloat", P["crescent_lift"], 0.0, 6.0),  # % of frame height
        ("Bloom", "NodeSocketFloat", P["bloom"], 0.0, 1.0),                 # fog glow on the brightest parts
        ("Dispersion", "NodeSocketFloat", P["dispersion"], 0.0, 0.02),      # chromatic fringe
        ("Grain", "NodeSocketFloat", P["grain"], 0.0, 0.5),                 # film grain
    ] + list(extra))
    t, N, L = ng, ng.nodes, ng.links.new
    I = gi.outputs
    S = {k: I[k] for k in ("Image", "Coverage Pass", "Halo Pass", "Arc Glow Pass", "Height Pass")}

    def sock(v):
        return hasattr(v, "is_linked")

    def math(op, a, b=None, clamp=False, label=None):
        n = N.new("ShaderNodeMath"); n.operation, n.use_clamp = op, clamp
        if label:
            n.label = label
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            L(v, n.inputs[i]) if sock(v) else setattr(n.inputs[i], "default_value", v)
        return n.outputs[0]

    def px(v1_px, reach=None):
        """v1 pixel size at REF_H → pixels at this frame, optionally × a reach control.
        Baked from the render height: Blur ignores a Size linked from Relative To Pixel (5.2),
        but takes one from a Math node."""
        if reach is None:
            n = N.new("ShaderNodeMath"); n.operation = "MULTIPLY"
            n.inputs[0].default_value, n.inputs[1].default_value = v1_px, frame_h / REF_H
            return n.outputs[0]
        return math("MULTIPLY", reach, v1_px * frame_h / REF_H)

    def blur(src, size_px, label, reach=None):
        b = N.new("CompositorNodeBlur"); b.label = label
        b.inputs["Type"].default_value = "Gaussian"
        # Float straight into the vector Size socket. Routed through Combine XYZ, a linked size
        # becomes per-pixel and Blur silently uses 0 (5.2).
        L(px(size_px, reach), b.inputs["Size"])
        L(src, b.inputs["Image"])
        return b.outputs[0]

    def mix(blend, a, b, fac=1.0, label=None):
        n = N.new("ShaderNodeMix"); n.data_type = "RGBA"; n.blend_type = blend; n.clamp_factor = False
        if label:
            n.label = label
        L(fac, n.inputs[0]) if sock(fac) else setattr(n.inputs[0], "default_value", fac)
        for idx, v in ((6, a), (7, b)):
            L(v, n.inputs[idx]) if sock(v) else setattr(n.inputs[idx], "default_value", v)
        return n.outputs[2]

    def outside(px_, kill, label):
        """1 − clamp(blurred coverage × kill): masks glow off the object's face."""
        return math("SUBTRACT", 1.0, math("MULTIPLY", blur(cov, px_, label), kill, clamp=True))

    H = SimpleNamespace(N=N, L=L, I=I, math=math, mix=mix, blur=blur, px=px)
    if pre is not None:
        S = pre(H, S)
    img, cov = S["Image"], S["Coverage Pass"]
    soft = blur(img, LENS["soften_px"], "Soften")

    # Halo: edge light blurred outward (tight + wide), kept off the face.
    halo = S["Halo Pass"]
    spread = mix("ADD", blur(halo, LENS["halo_px"], "Halo Spread", I["Halo Reach"]),
                 blur(halo, LENS["halo_wide_px"], "Halo Wide Spread", I["Halo Reach"]),
                 LENS["halo_wide_amount"])
    halo_out = mix("MULTIPLY", spread, outside(LENS["coverage_px"], LENS["halo_inside_kill"], "Object Coverage"))
    # Self-glow: the body's own bright parts, blurred and added back (see RESEARCH.md). Keyed by
    # brightness so the dark tops give nothing and the pink-orange bases glow widest.
    lum = N.new("CompositorNodeRGBToBW"); L(soft, lum.inputs["Image"])
    key = math("MULTIPLY", math("SUBTRACT", lum.outputs[0], P["glow_key"][0]),
               1.0 / (P["glow_key"][1] - P["glow_key"][0]), clamp=True, label="Glow Key (bright parts)")
    src = mix("MULTIPLY", mix("MULTIPLY", soft, key), srgb(*P["glow_tint"]), 1.0, "Glow Tint")
    src = mix("MULTIPLY", src, cov, 1.0, "Glow Source × Object")
    glow = mix("ADD", blur(src, P["glow_px"][0], "Self Glow Near", I["Halo Reach"]),
               blur(src, P["glow_px"][1], "Self Glow Far", I["Halo Reach"]), P["glow_far"])
    glow = mix("MULTIPLY", glow, outside(LENS["coverage_px"], LENS["halo_inside_kill"], "Glow Edge"), 1.0,
               "Self Glow × Outside")
    halo_out = mix("ADD", halo_out, glow, P["glow_amount"], "Add Self Glow")
    col = mix("ADD", soft, halo_out, I["Halo"], "Add Halo")

    # Arc glow: near + mid + tinted far blur, masked off the face.
    arc = S["Arc Glow Pass"]
    near, mid, far = (blur(arc, p, f"Arc Glow {n}") for n, p in zip(("Near", "Mid", "Far"), LENS["arc_glow_px"]))
    a_n, a_m, a_f = LENS["arc_glow_amounts"]
    arc_sum = mix("ADD", mix("ADD", mix("MULTIPLY", near, (a_n,) * 3 + (1.0,)), mid, a_m),
                  mix("MULTIPLY", far, LENS["arc_glow_far_tint"]), a_f)
    arc_out = mix("MULTIPLY", arc_sum, outside(LENS["arc_cover_px"], LENS["arc_glow_inside_kill"], "Arc Occluder Edge"))
    col = mix("ADD", col, arc_out, I["Arc Glow"], "Add Arc Glow")

    # Crescent: the silhouette lifted and shrunk, minus itself.
    lift = N.new("CompositorNodeTransform"); lift.label = "Crescent Offset"
    lift.inputs["Interpolation"].default_value = "Nearest"
    lift.inputs["Scale"].default_value = LENS["crescent_scale"]
    L(math("MULTIPLY", I["Crescent Lift"], 0.01 * frame_h), lift.inputs["Y"])
    L(cov, lift.inputs["Image"])
    # Same lift applied to the cap mask, so the crescent only forms above each shape's top end.
    cap_lift = N.new("CompositorNodeTransform"); cap_lift.label = "Cap Offset"
    cap_lift.inputs["Interpolation"].default_value = "Nearest"
    cap_lift.inputs["Scale"].default_value = LENS["crescent_scale"]
    L(lift.inputs["Y"].links[0].from_socket, cap_lift.inputs["Y"])
    cap = math("MULTIPLY", math("SUBTRACT", S["Height Pass"], P["cap_start"]), 1.0 / (1.0 - P["cap_start"]),
               clamp=True, label="Top Caps")
    L(cap, cap_lift.inputs["Image"])
    moon = math("SUBTRACT", lift.outputs[0], cov, clamp=True)
    moon = math("MULTIPLY", moon, cap_lift.outputs[0], label="Crescent × Caps")
    hole = blur(moon, LENS["crescent_soft_px"], "Crescent Softness")
    cres = mix("ADD", mix("MULTIPLY", hole, LENS["crescent_color"]),
               mix("MULTIPLY", blur(hole, P["crescent_glow_px"], "Crescent Glow"), LENS["crescent_glow_color"]),
               P["crescent_glow_amount"])
    col = mix("ADD", col, cres, I["Crescent"], "Add Crescent")

    if stage is not None:
        col = stage(H, col)
    bloom = N.new("CompositorNodeGlare"); bloom.label = "Bloom"
    bi = bloom.inputs
    bi["Type"].default_value = "Fog Glow"
    bi["Quality"].default_value = "High"
    bi["Threshold"].default_value = LENS["glow_threshold"]
    bi["Size"].default_value = 2.0 ** (LENS["glow_size"] - 9)
    L(I["Bloom"], bi["Strength"])
    L(col, bi["Image"])
    lens = N.new("CompositorNodeLensdist"); lens.label = "Dispersion"
    lens.inputs["Fit"].default_value = True
    L(I["Dispersion"], lens.inputs["Dispersion"])
    L(bloom.outputs["Image"], lens.inputs["Image"])

    # Film grain: per-pixel noise plus 2 px clumps, resolution-independent (no texture file).
    coords = N.new("CompositorNodeImageCoordinates"); L(I["Image"], coords.inputs["Image"])
    # Reseeded every frame (3D noise, z = frame): frozen grain on a video reads as dirt on the lens.
    frame = N.new("CompositorNodeSceneTime").outputs["Frame"]

    def per_frame(v):
        sep = N.new("ShaderNodeSeparateXYZ"); L(v, sep.inputs[0])
        c = N.new("ShaderNodeCombineXYZ")
        L(sep.outputs["X"], c.inputs["X"]); L(sep.outputs["Y"], c.inputs["Y"]); L(frame, c.inputs["Z"])
        return c.outputs[0]

    fine = N.new("ShaderNodeTexWhiteNoise"); fine.noise_dimensions = "3D"
    L(per_frame(coords.outputs["Pixel"]), fine.inputs["Vector"])
    half = N.new("ShaderNodeVectorMath"); half.operation = "SCALE"; half.inputs["Scale"].default_value = 0.5
    L(coords.outputs["Pixel"], half.inputs[0])
    fl = N.new("ShaderNodeVectorMath"); fl.operation = "FLOOR"; L(half.outputs[0], fl.inputs[0])
    coarse = N.new("ShaderNodeTexWhiteNoise"); coarse.noise_dimensions = "3D"
    L(per_frame(fl.outputs[0]), coarse.inputs["Vector"])
    # v1: 0.5 + 0.18·(0.85·fine + 0.45·coarse)/0.96 with unit-variance noise; uniform noise × 3.46 matches.
    g = math("MULTIPLY_ADD", math("SUBTRACT", fine.outputs["Value"], 0.5), 0.5515)
    g.node.inputs[2].default_value = 0.5
    g = math("ADD", g, math("MULTIPLY", math("SUBTRACT", coarse.outputs["Value"], 0.5), 0.292), clamp=True,
             label="Grain Texture")
    col = mix("OVERLAY", lens.outputs[0], g, I["Grain"], "Film Grain")
    col = mix("ADD", col, LENS["shadow_tint"], 1.0, "Shadow Tint")
    col = mix("LINEAR_LIGHT", col, g, LENS["shadow_grain"], "Shadow Grain")
    L(col, go.inputs["Image"])
    auto_layout(ng, dx=260, dy=180)
    return ng


# --- Scene ---------------------------------------------------------------------------------------

def build(a):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "Eclipse Logo"

    logo = add_logo(scene)
    mat = build_material()
    logo.data.materials.clear()
    logo.data.materials.append(mat)
    gn_input(logo.modifiers["Shade"], "Material", mat)

    cam_data = bpy.data.cameras.new("Camera")
    cam = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (0, 0, 10)
    cam_data.sensor_fit = "HORIZONTAL"
    cam_data.sensor_width = 36
    bpy.context.view_layer.update()  # dimensions include the modifiers only after an update
    frame_w = logo.dimensions.x / P["frame_fill"]
    cam_data.lens = 36 * 10 / frame_w
    scene.camera = cam

    # Opaque world colour. Emission-only material, so the world lights nothing; it is only the backdrop.
    world = bpy.data.worlds.new("Background")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = srgb(*P["background"])
    bg.inputs["Strength"].default_value = 1.0
    scene.world = world

    scene.render.engine = "CYCLES"
    enable_gpu(scene)
    scene.cycles.samples = a["samples"]
    scene.cycles.use_denoising = False
    scene.render.resolution_x, scene.render.resolution_y = P["res_x"], P["res_y"]
    scene.render.resolution_percentage = round(100 * a["scale"])
    scene.view_settings.view_transform = "Standard"
    scene.render.film_transparent = False  # the world colour is the background; coverage comes from an AOV
    scene.render.image_settings.color_mode = "RGB"
    vl = scene.view_layers[0]
    for name, typ in (("halo", "COLOR"), ("arc_glow", "COLOR"), ("coverage", "VALUE"), ("height", "VALUE")):
        aov = vl.aovs.add(); aov.name, aov.type = name, typ

    raw = EXP["renders"] / f"{NAME}_{a['out']}_raw.exr"
    frame_h = P["res_y"] * a["scale"]
    compositor(scene, post(frame_h), raw_exr=raw,
               passes=[("coverage", "Coverage Pass"), ("halo", "Halo Pass"), ("arc_glow", "Arc Glow Pass"),
                       ("height", "Height Pass")])

    # 3D viewport: live material, no compositor (the compositor previews the saved render).
    for scr in bpy.data.screens:
        for area in scr.areas:
            for sp in area.spaces:
                if sp.type == "VIEW_3D":
                    sp.shading.type = "RENDERED"
                    sp.shading.use_compositor = "DISABLED"
                    sp.region_3d.view_perspective = "CAMERA"
    return scene, raw


HOW = """ECLIPSE LOGO — how to tweak

Look (material): select "Logo" → Shader Editor → the one "Eclipse Glow" node.
  Brightness        overall emission
  Gradient Offset   slides the sunset bands up/down the shapes
  Gradient Angle    rotates the bands (degrees)
  Shape Gradient    0 = colour from surface angle only (v1), 1 = each shape runs bottom → top
  Rim               spectral edge colour
  Arc               bright arc line on the top edges
  Halo Light        edge light fed to the halo glow (see Post › Halo)
  Arc Light         light fed to the arc glow (see Post › Arc Glow)
  Colours: Tab into the node; the three Color Ramps hold the body and rim colours.

Background: World tab (or Shader Editor › World) → Background › Color.
  Not transparent: the halo mask comes from the "coverage" AOV, not alpha.

Post (glows, grain): Compositing tab → the one "Post" node. The backdrop shows the saved
render, so every slider updates at once, no re-render.
  Halo, Halo Reach, Arc Glow, Crescent, Crescent Lift (% of height), Bloom, Dispersion, Grain.
  Tab into Post to see every step.

After changing the material, geometry or world: set Source › Use Saved Render off, then F12.
With it on, F12 re-uses the saved render and ignores 3D changes.

Logo shape: Logo › Modifiers › Inflate (Puff = half thickness, Roundness = edge radius, Detail = voxel size).
Rebuild from: experiments/eclipse-glow/scripts/build.py (P dict, --set key=value).
"""


def main():
    a = parse_args()
    scene, raw = build(a)
    png = EXP["renders"] / f"{NAME}_{a['out']}.png"
    scene.render.filepath = str(png)
    bpy.ops.render.render(write_still=True)
    print(f"[out] WROTE {png}")
    if a["save"]:
        use_saved_render(scene, raw, EXP["output"])
        how_to_tweak(HOW)
        blend = EXP["output"] / f"{NAME}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_mainfile()
        Path(str(blend) + "1").unlink(missing_ok=True)
        print(f"[out] WROTE {blend}")
    print("ECLIPSE LOGO OK")


if __name__ == "__main__":
    main()
