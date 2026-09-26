"""Wonder logo as a pop-art / Lichtenstein print — build + render.

Flat emission cel shading, screen-space halftone on the front faces, three-tone
blue extrusion banded by N.L to the key light, Grease Pencil Line Art ink strokes.
The logo stands in front of an orange wall; a hard point light casts its shadow
onto the wall, and the wall shader fills whatever is in shadow with halftone
dots. Move the Key Light or the camera and everything follows.

Run:
  blender -b -P scripts/build.py -- --out renders/p01.png --samples 64 --scale 0.5
  blender -b -P scripts/build.py -- --set dot_freq=90 --set orbit="(10,0,-9)"
"""
import bpy, bmesh, math, sys, os, argparse
from mathutils import Euler, Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.path.join(ROOT, "assets", "logo.svg")
TAU = math.pi * 2


def hexc(h):
    """'#RRGGBB' -> linear RGBA (so Standard view transform prints the exact hex)."""
    h = h.lstrip("#")
    srgb = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    return (*lin, 1.0)


# ---------------------------------------------------------------- params
P = dict(
    # --- palette (hex, as printed). All of these are also live inputs on the
    # material group nodes, so they can be changed in Blender without a rebuild.
    bg="#FF5837",          # lit wall
    face="#E9DC1E",        # W front faces, solid
    full_col="#1E4FD8",    # sides facing away from the light, or in the W's own shadow
    mid_line="#1E4FD8",    # mid-tone sides: hatch lines ...
    mid_base="#55BAF1",    # ... over this
    highlight="#55BAF1",   # sides facing the light
    shadow_base="#FF5837", # wall in shadow, under the dots
    shadow_dot="#0A0A08",  # halftone dots in the shadow
    ink="#0A0A08",         # outline

    # --- geometry / pose
    logo_w=2.0,
    depth=0.52,            # extrusion thickness
    bevel=0.0, bevel_segs=2,
    # camera orbit around the logo, deg. Same convention the old logo tilt used:
    # X shows the top faces, Z swings the left faces into view.
    orbit=(9.0, 0.0, 11.0),

    # --- wall + key light
    gap=0.7,                       # logo back face -> wall
    sun_from=(-0.3, -1.0, 0.25),   # direction toward the key light: -X left, -Y toward viewer, +Z up.
                                   # X/Z vs Y sets shadow length: shadow shifts (gap+depth) * X/Y, Z/Y
    light_dist=14.0,               # far away -> near-parallel shadow; bring it closer to grow the shadow
    light_power=20000.0,           # only needs to clear the shadow threshold
    wall_size=200.0,

    # --- patterns: screen space, 1.0 = frame width, so they print at a constant
    # size and never stretch whatever the camera does
    dot_density=64.0,      # dots across the frame
    dot_size=0.8,          # 0 = none, 1 = dots touch, 1.42 = solid
    dot_angle=45.0,
    dot_soft=0.03,         # edge softness, share of a cell
    line_density=120.0,    # lines across the frame
    line_width=0.45,       # share of each stripe that is ink
    line_angle=45.0,
    line_soft=0.04,

    # --- side bands (full / lines / highlight), N·L against the light across the logo plane
    band_lit=0.7, band_dark=-0.1,
    front_thresh=0.70,     # |object-space Y normal| above this counts as a front face

    # --- outline
    outline="lineart",     # 'lineart' (live in viewport) | 'freestyle' | 'hull' | 'none'
    stroke=0.016,          # line art radius, world units: one even weight for outline + creases
    line_px=12.0,          # freestyle thickness at full res
    crease_angle=35.0,
    hull_thick=0.012,      # inverted-hull fallback

    # --- camera
    ortho=2.75, cam_dist=8.0, cam_dx=0.0, cam_dz=0.0,

    res=(2048, 2048),
    grain=0.0,
)


# ---------------------------------------------------------------- helpers
def deselect():
    for o in bpy.context.view_layer.objects:
        o.select_set(False)


def activate(ob):
    deselect(); ob.select_set(True); bpy.context.view_layer.objects.active = ob


def centre_curve_data(d):
    xs, ys = [], []
    for sp in d.splines:
        for bp in sp.bezier_points:
            for v in (bp.co, bp.handle_left, bp.handle_right):
                xs.append(v.x); ys.append(v.y)
        for pt in sp.points:
            xs.append(pt.co.x); ys.append(pt.co.y)
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    for sp in d.splines:
        for bp in sp.bezier_points:
            for v in (bp.co, bp.handle_left, bp.handle_right):
                v.x -= cx; v.y -= cy
        for pt in sp.points:
            pt.co.x -= cx; pt.co.y -= cy
    return max(xs) - min(xs), max(ys) - min(ys)


def import_logo():
    before = {o.name for o in bpy.data.objects}
    bpy.ops.import_curve.svg(filepath=SVG)
    new = [o for o in bpy.data.objects if o.name not in before]
    deselect()
    for o in new:
        o.select_set(True)
    bpy.context.view_layer.objects.active = new[0]
    bpy.ops.object.join()
    logo = bpy.context.active_object
    for c in list(logo.users_collection):
        c.objects.unlink(logo)
    bpy.context.scene.collection.objects.link(logo)
    for c in list(bpy.data.collections):
        if not c.objects:
            bpy.data.collections.remove(c)
    d = logo.data
    d.resolution_u = 24; d.dimensions = '2D'; d.fill_mode = 'BOTH'
    for sp in d.splines:
        sp.resolution_u = 24
    w, h = centre_curve_data(d)
    logo.location = (0, 0, 0)
    return logo, P["logo_w"] / w


def curve_to_prism(cur, depth, sf):
    cur.data.extrude = (depth / 2) / sf
    cur.data.bevel_depth = 0; cur.data.offset = 0
    activate(cur); bpy.ops.object.convert(target='MESH')
    ob = bpy.context.active_object; ob.name = "Logo"
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data); bm.free()
    ob.scale = (sf, sf, sf)
    ob.rotation_euler = Euler((math.radians(90), 0, 0))   # face the camera: thickness along object Y
    activate(ob); bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    ob.data.materials.clear()
    bpy.ops.object.shade_flat()      # hard facets — cel bands must not interpolate
    return ob


def sun_dir():
    """Unit vector toward the sun (world space)."""
    return Vector(P["sun_from"]).normalized()


def look_at(ob, target):
    ob.rotation_euler = (Vector(target) - ob.location).to_track_quat('-Z', 'Y').to_euler()


# ---------------------------------------------------------------- node helpers
def _math(nt, op, a, b=None, c=None, loc=(0, 0), clamp=False):
    m = nt.nodes.new("ShaderNodeMath"); m.operation = op; m.location = loc
    m.use_clamp = clamp
    for i, v in enumerate((a, b, c)):
        if v is None:
            continue
        if hasattr(v, "bl_rna"):
            nt.links.new(v, m.inputs[i])
        else:
            m.inputs[i].default_value = v
    return m.outputs[0]


# ---------------------------------------------------------------- node groups
# Every tunable lives on a group node's inputs, so in Blender you select the
# object, open the Shader Editor and tweak the one node the material holds.

def _link(nt, a, sock):
    if hasattr(a, "bl_rna"):
        nt.links.new(a, sock)
    else:
        sock.default_value = a


def _vmath(nt, op, a, b=None):
    n = nt.nodes.new("ShaderNodeVectorMath"); n.operation = op
    _link(nt, a, n.inputs[0])
    if b is not None:
        _link(nt, b, n.inputs[1])
    return n.outputs["Value"] if op in ('DOT_PRODUCT', 'LENGTH', 'DISTANCE') else n.outputs["Vector"]


def _group(name, ins, outs):
    """ins = [(name, socket_type, default, min, max)], outs = [(name, socket_type)]."""
    ng = bpy.data.node_groups.new(name, 'ShaderNodeTree')
    for n, kind, default, lo, hi in ins:
        s = ng.interface.new_socket(n, in_out='INPUT', socket_type=kind)
        if default is not None:
            s.default_value = default
        if lo is not None:
            s.min_value, s.max_value = lo, hi
    for n, kind in outs:
        ng.interface.new_socket(n, in_out='OUTPUT', socket_type=kind)
    return ng, ng.nodes.new("NodeGroupInput"), ng.nodes.new("NodeGroupOutput")


def _use(nt, ng, label=None):
    g = nt.nodes.new("ShaderNodeGroup"); g.node_tree = ng
    if label:
        g.label = label
    return g


def _drive(sock, expr, variables, index=-1):
    """Scripted driver; variables = {name: (id, data_path)}. Simple expressions
    only, so it runs without enabling Python auto-exec."""
    fc = sock.driver_add("default_value", index) if index >= 0 else sock.driver_add("default_value")
    d = fc.driver; d.type = 'SCRIPTED'
    for name, (idb, path) in variables.items():
        v = d.variables.new(); v.name = name; v.type = 'SINGLE_PROP'
        v.targets[0].id_type = 'OBJECT'; v.targets[0].id = idb; v.targets[0].data_path = path
    d.expression = expr
    return d


def _value(nt, expr, variables):
    n = nt.nodes.new("ShaderNodeValue")
    _drive(n.outputs[0], expr, variables)
    return n.outputs[0]


def auto_layout(nt):
    """Column per dependency depth, so the group internals are readable."""
    depth = {}
    def d(n):
        if n.name in depth:
            return depth[n.name]
        depth[n.name] = 0
        ins = [l.from_node for l in nt.links if l.to_node == n]
        depth[n.name] = 1 + max((d(m) for m in ins), default=-1)
        return depth[n.name]
    cols = {}
    for n in nt.nodes:
        cols.setdefault(d(n), []).append(n)
    for c, ns in cols.items():
        for i, n in enumerate(ns):
            n.location = (c * 220, -i * 200)


def grp_screen_uv(cam):
    """Camera-space position -> screen coords where 1.0 = the frame width.

    Works for ortho and perspective, and in the viewport's camera view too,
    so patterns print at a constant size wherever the camera goes.
    """
    ng, gi, go = _group("Pop Screen UV", [], [("UV", 'NodeSocketVector')])
    nt = ng
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Camera"], sep.inputs[0])
    ortho = _value(nt, "t == 1", {"t": (cam, "data.type")})          # 1 = ORTHO
    scale = _value(nt, "s", {"s": (cam, "data.ortho_scale")})
    k = _value(nt, "2 * tan(a / 2)", {"a": (cam, "data.angle")})
    persp = _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', sep.outputs["Z"], -1.0), k)
    den = _math(nt, 'MULTIPLY_ADD', _math(nt, 'SUBTRACT', scale, persp), ortho, persp)
    cmb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(_math(nt, 'DIVIDE', sep.outputs["X"], den), cmb.inputs[0])
    nt.links.new(_math(nt, 'DIVIDE', sep.outputs["Y"], den), cmb.inputs[1])
    nt.links.new(cmb.outputs[0], go.inputs["UV"])
    auto_layout(nt)
    return ng


def _rotated_cells(nt, uv_ng, density, angle):
    """Rotate screen uv by angle (deg) and scale to cells -> (u, v)."""
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(_use(nt, uv_ng).outputs["UV"], sep.inputs[0])
    rad = _math(nt, 'RADIANS', angle)
    c, s = _math(nt, 'COSINE', rad), _math(nt, 'SINE', rad)
    u, v = sep.outputs["X"], sep.outputs["Y"]
    ur = _math(nt, 'MULTIPLY_ADD', u, c, _math(nt, 'MULTIPLY', v, s))
    vr = _math(nt, 'SUBTRACT', _math(nt, 'MULTIPLY', v, c), _math(nt, 'MULTIPLY', u, s))
    return _math(nt, 'MULTIPLY', ur, density), _math(nt, 'MULTIPLY', vr, density)


def _edge(nt, radius, dist, soft):
    """1 inside radius, 0 outside, with a soft band of +-soft."""
    sf = _math(nt, 'MAXIMUM', soft, 1e-4)
    top = _math(nt, 'SUBTRACT', _math(nt, 'ADD', radius, sf), dist)
    return _math(nt, 'DIVIDE', top, _math(nt, 'MULTIPLY', sf, 2.0), clamp=True)


def _pattern_colour(nt, gi, go, mask, base, ink):
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    nt.links.new(mask, mx.inputs[0]); nt.links.new(gi.outputs[base], mx.inputs[6])
    nt.links.new(gi.outputs[ink], mx.inputs[7])
    nt.links.new(mx.outputs[2], go.inputs["Color"]); nt.links.new(mask, go.inputs["Mask"])


def grp_halftone(uv_ng):
    ng, gi, go = _group("Pop Halftone Dots", [
        ("Base Color", 'NodeSocketColor', hexc(P["shadow_base"]), None, None),
        ("Dot Color", 'NodeSocketColor', hexc(P["shadow_dot"]), None, None),
        ("Density", 'NodeSocketFloat', P["dot_density"], 1.0, 500.0),   # dots across the frame
        ("Size", 'NodeSocketFloat', P["dot_size"], 0.0, 1.42),          # 1 = dots touch, 1.42 = solid
        ("Angle", 'NodeSocketFloat', P["dot_angle"], -180.0, 180.0),    # degrees
        ("Softness", 'NodeSocketFloat', P["dot_soft"], 0.0, 0.5),
    ], [("Color", 'NodeSocketColor'), ("Mask", 'NodeSocketFloat')])
    nt = ng
    cu, cv = _rotated_cells(nt, uv_ng, gi.outputs["Density"], gi.outputs["Angle"])
    dx = _math(nt, 'SUBTRACT', _math(nt, 'FRACT', cu), 0.5)
    dy = _math(nt, 'SUBTRACT', _math(nt, 'FRACT', cv), 0.5)
    r = _math(nt, 'SQRT', _math(nt, 'MULTIPLY_ADD', dx, dx, _math(nt, 'MULTIPLY', dy, dy)))
    mask = _edge(nt, _math(nt, 'MULTIPLY', gi.outputs["Size"], 0.5), r, gi.outputs["Softness"])
    _pattern_colour(nt, gi, go, mask, "Base Color", "Dot Color")
    auto_layout(nt)
    return ng


def grp_hatch(uv_ng):
    ng, gi, go = _group("Pop Hatch Lines", [
        ("Base Color", 'NodeSocketColor', hexc(P["mid_base"]), None, None),
        ("Line Color", 'NodeSocketColor', hexc(P["mid_line"]), None, None),
        ("Density", 'NodeSocketFloat', P["line_density"], 1.0, 500.0),  # lines across the frame
        ("Width", 'NodeSocketFloat', P["line_width"], 0.0, 1.0),        # share of each stripe that is ink
        ("Angle", 'NodeSocketFloat', P["line_angle"], -180.0, 180.0),   # degrees
        ("Softness", 'NodeSocketFloat', P["line_soft"], 0.0, 0.5),
    ], [("Color", 'NodeSocketColor'), ("Mask", 'NodeSocketFloat')])
    nt = ng
    # lines run along the rotated u axis, so Angle is the lines' own direction (45 = /)
    _, cv = _rotated_cells(nt, uv_ng, gi.outputs["Density"], gi.outputs["Angle"])
    d = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', cv), 0.5))
    mask = _edge(nt, _math(nt, 'MULTIPLY', gi.outputs["Width"], 0.5), d, gi.outputs["Softness"])
    _pattern_colour(nt, gi, go, mask, "Base Color", "Line Color")
    auto_layout(nt)
    return ng


def grp_light_dir(light):
    """Unit vector from the shaded object toward the Key Light, driven live from
    the light's world position, so moving the light re-bands the extrusion."""
    ng, gi, go = _group("Pop Light Direction", [], [("Direction", 'NodeSocketVector')])
    nt = ng
    cmb = nt.nodes.new("ShaderNodeCombineXYZ")
    for i, axis in enumerate("XYZ"):
        v = nt.nodes.new("ShaderNodeValue")
        fc = v.outputs[0].driver_add("default_value"); d = fc.driver; d.type = 'AVERAGE'
        var = d.variables.new(); var.type = 'TRANSFORMS'
        t = var.targets[0]; t.id = light; t.transform_type = 'LOC_' + axis; t.transform_space = 'WORLD_SPACE'
        nt.links.new(v.outputs[0], cmb.inputs[i])
    # measured from the object's origin, not each pixel, so every flat face gets
    # one clean band instead of splitting partway along
    info = nt.nodes.new("ShaderNodeObjectInfo")
    nt.links.new(_vmath(nt, 'NORMALIZE', _vmath(nt, 'SUBTRACT', cmb.outputs[0], info.outputs["Location"])),
                 go.inputs["Direction"])
    auto_layout(nt)
    return ng


def grp_logo(hatch_ng, light_ng):
    """Front faces solid. Sides in three tones like a comic print: full colour
    away from the light, hatch lines for the mid tone, highlight toward it.
    Anything the Key Light can't reach (the W shadowing itself) drops to full."""
    ng, gi, go = _group("Pop Logo Shader", [
        ("Face Color", 'NodeSocketColor', hexc(P["face"]), None, None),
        ("Full Color", 'NodeSocketColor', hexc(P["full_col"]), None, None),
        ("Mid Line Color", 'NodeSocketColor', hexc(P["mid_line"]), None, None),
        ("Mid Base Color", 'NodeSocketColor', hexc(P["mid_base"]), None, None),
        ("Highlight Color", 'NodeSocketColor', hexc(P["highlight"]), None, None),
        ("Line Density", 'NodeSocketFloat', P["line_density"], 1.0, 500.0),
        ("Line Width", 'NodeSocketFloat', P["line_width"], 0.0, 1.0),
        ("Line Angle", 'NodeSocketFloat', P["line_angle"], -180.0, 180.0),
        ("Line Softness", 'NodeSocketFloat', P["line_soft"], 0.0, 0.5),
        ("Band Highlight", 'NodeSocketFloat', P["band_lit"], -1.0, 1.0),  # N·L above -> highlight
        ("Band Full", 'NodeSocketFloat', P["band_dark"], -1.0, 1.0),      # N·L below -> full colour
        ("Self Shadow", 'NodeSocketFloat', 1.0, 0.0, 1.0),                # 1 = W's own cast shadow -> full
        ("Shadow Threshold", 'NodeSocketFloat', 0.02, 0.0, 1.0),
        ("Front Threshold", 'NodeSocketFloat', P["front_thresh"], 0.0, 1.0),
    ], [("Shader", 'NodeSocketShader')])
    nt = ng
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    to_obj = nt.nodes.new("ShaderNodeVectorTransform")
    to_obj.vector_type = 'NORMAL'; to_obj.convert_from = 'WORLD'; to_obj.convert_to = 'OBJECT'
    nt.links.new(geo.outputs["Normal"], to_obj.inputs[0])
    n_obj = to_obj.outputs[0]
    # the prism's thickness runs along object Y, so |ny| picks the front/back caps
    ny = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(n_obj, ny.inputs[0])
    front = _math(nt, 'GREATER_THAN', _math(nt, 'ABSOLUTE', ny.outputs["Y"]), gi.outputs["Front Threshold"])

    # N·L using the light's direction across the logo plane only, so even a
    # near-frontal light gives clear bands
    l_obj = nt.nodes.new("ShaderNodeVectorTransform")
    l_obj.vector_type = 'VECTOR'; l_obj.convert_from = 'WORLD'; l_obj.convert_to = 'OBJECT'
    nt.links.new(_use(nt, light_ng).outputs["Direction"], l_obj.inputs[0])
    l_flat = _vmath(nt, 'NORMALIZE', _vmath(nt, 'MULTIPLY', l_obj.outputs[0], (1.0, 0.0, 1.0)))
    ndl = _vmath(nt, 'DOT_PRODUCT', _vmath(nt, 'NORMALIZE', n_obj), l_flat)
    hi = _math(nt, 'GREATER_THAN', ndl, gi.outputs["Band Highlight"])
    full = _math(nt, 'LESS_THAN', ndl, gi.outputs["Band Full"])

    # real light reaching this pixel (toon mask); shadowed -> full colour
    df = nt.nodes.new("ShaderNodeBsdfDiffuse"); df.inputs["Color"].default_value = (1, 1, 1, 1)
    s2r = nt.nodes.new("ShaderNodeShaderToRGB"); nt.links.new(df.outputs[0], s2r.inputs[0])
    bw = nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(s2r.outputs["Color"], bw.inputs[0])
    dark = _math(nt, 'MULTIPLY', _math(nt, 'LESS_THAN', bw.outputs[0], gi.outputs["Shadow Threshold"]),
                 gi.outputs["Self Shadow"])
    full = _math(nt, 'MAXIMUM', full, dark)

    h = _use(nt, hatch_ng)
    for a, b in (("Mid Base Color", "Base Color"), ("Mid Line Color", "Line Color"), ("Line Density", "Density"),
                 ("Line Width", "Width"), ("Line Angle", "Angle"), ("Line Softness", "Softness")):
        nt.links.new(gi.outputs[a], h.inputs[b])

    def mix(fac, a, b):
        m = nt.nodes.new("ShaderNodeMix"); m.data_type = 'RGBA'
        nt.links.new(fac, m.inputs[0]); nt.links.new(a, m.inputs[6]); nt.links.new(b, m.inputs[7])
        return m.outputs[2]
    side = mix(hi, h.outputs["Color"], gi.outputs["Highlight Color"])
    side = mix(full, side, gi.outputs["Full Color"])
    col = mix(front, side, gi.outputs["Face Color"])
    em = nt.nodes.new("ShaderNodeEmission"); nt.links.new(col, em.inputs["Color"])
    nt.links.new(em.outputs[0], go.inputs["Shader"])
    auto_layout(nt)
    return ng


def grp_wall(dots_ng):
    ng, gi, go = _group("Pop Wall Shader", [
        ("Wall Color", 'NodeSocketColor', hexc(P["bg"]), None, None),
        ("Shadow Color", 'NodeSocketColor', hexc(P["shadow_base"]), None, None),
        ("Shadow Dot Color", 'NodeSocketColor', hexc(P["shadow_dot"]), None, None),
        ("Dot Density", 'NodeSocketFloat', P["dot_density"], 1.0, 500.0),
        ("Dot Size", 'NodeSocketFloat', P["dot_size"], 0.0, 1.42),
        ("Dot Angle", 'NodeSocketFloat', P["dot_angle"], -180.0, 180.0),
        ("Dot Softness", 'NodeSocketFloat', P["dot_soft"], 0.0, 0.5),
        ("Shadow Threshold", 'NodeSocketFloat', 0.02, 0.0, 1.0),   # any light at all = lit
    ], [("Shader", 'NodeSocketShader')])
    nt = ng
    # toon shadow mask: is this bit of wall receiving the Key Light? The shadow
    # itself is cast by the W geometry; this only decides how to paint it
    df = nt.nodes.new("ShaderNodeBsdfDiffuse"); df.inputs["Color"].default_value = (1, 1, 1, 1)
    s2r = nt.nodes.new("ShaderNodeShaderToRGB"); nt.links.new(df.outputs[0], s2r.inputs[0])
    bw = nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(s2r.outputs["Color"], bw.inputs[0])
    lit = _math(nt, 'GREATER_THAN', bw.outputs[0], gi.outputs["Shadow Threshold"])
    h = _use(nt, dots_ng)
    for a, b in (("Shadow Color", "Base Color"), ("Shadow Dot Color", "Dot Color"), ("Dot Density", "Density"),
                 ("Dot Size", "Size"), ("Dot Angle", "Angle"), ("Dot Softness", "Softness")):
        nt.links.new(gi.outputs[a], h.inputs[b])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    nt.links.new(lit, mx.inputs[0]); nt.links.new(h.outputs["Color"], mx.inputs[6])
    nt.links.new(gi.outputs["Wall Color"], mx.inputs[7])
    em = nt.nodes.new("ShaderNodeEmission"); nt.links.new(mx.outputs[2], em.inputs["Color"])
    nt.links.new(em.outputs[0], go.inputs["Shader"])
    auto_layout(nt)
    return ng


def mat_from_group(name, ng):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    g = _use(nt, ng); g.location = (0, 0); g.width = 240
    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (340, 0)
    nt.links.new(g.outputs["Shader"], out.inputs["Surface"])
    return m


def mat_flat(name, hexcol, backfacing_only=False):

    m = bpy.data.materials.new(name); m.use_nodes = True
    m.cycles.emission_sampling = 'NONE'
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (400, 0)
    em = nt.nodes.new("ShaderNodeEmission"); em.location = (200, 0)
    em.inputs["Color"].default_value = hexc(hexcol); em.inputs["Strength"].default_value = 1.0
    if backfacing_only:
        # inverted-hull outline: only the flipped back faces paint, fronts stay invisible
        tr = nt.nodes.new("ShaderNodeBsdfTransparent"); tr.location = (200, -180)
        geo = nt.nodes.new("ShaderNodeNewGeometry"); geo.location = (0, 120)
        mixs = nt.nodes.new("ShaderNodeMixShader"); mixs.location = (380, 100)
        nt.links.new(geo.outputs["Backfacing"], mixs.inputs[0])
        nt.links.new(tr.outputs[0], mixs.inputs[1])
        nt.links.new(em.outputs[0], mixs.inputs[2])
        nt.links.new(mixs.outputs[0], out.inputs["Surface"])
        m.use_backface_culling = False
    else:
        nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


# ---------------------------------------------------------------- scene
def build(args):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    # EEVEE: Shader to RGB turns the sun's shadow into a mask the wall shader can
    # read (Cycles can't), and the viewport shows the final look in real time
    sc.render.engine = 'BLENDER_EEVEE'
    ee = sc.eevee
    ee.taa_render_samples = args.samples
    ee.taa_samples = 16
    ee.use_raytracing = False
    ee.use_shadows = True
    ee.shadow_resolution_scale = 1.0
    ee.shadow_pool_size = '1024'      # room for fine shadow-map tiles -> clean shadow edge
    sc.render.filter_size = 1.2
    sc.render.resolution_x, sc.render.resolution_y = P["res"]
    sc.render.resolution_percentage = int(args.scale * 100)
    sc.render.film_transparent = False
    sc.view_settings.view_transform = 'Standard'   # flat print colours, no tone map
    sc.view_settings.look = 'None'
    sc.view_settings.exposure = 0.0

    # orange behind everything, but no ambient light: the shadow mask must see the key light only
    w = bpy.data.worlds.new("Pop"); w.use_nodes = True; sc.world = w
    wt = w.node_tree; bgn = wt.nodes["Background"]
    bgn.inputs["Color"].default_value = hexc(P["bg"]); bgn.inputs["Strength"].default_value = 1.0
    lp = wt.nodes.new("ShaderNodeLightPath")
    mix = wt.nodes.new("ShaderNodeMixShader")
    blk = wt.nodes.new("ShaderNodeBackground"); blk.inputs["Strength"].default_value = 0.0
    wt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    wt.links.new(blk.outputs[0], mix.inputs[1]); wt.links.new(bgn.outputs[0], mix.inputs[2])
    wt.links.new(mix.outputs[0], wt.nodes["World Output"].inputs["Surface"])

    # camera: orthographic keeps the extrusion parallel, like a printed illustration
    cd = bpy.data.cameras.new("Cam"); cd.type = 'ORTHO'; cd.ortho_scale = P["ortho"]
    cd.clip_end = 1000.0
    cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cam.location = (P["cam_dx"], -P["cam_dist"], P["cam_dz"])
    look_at(cam, (P["cam_dx"], 0, P["cam_dz"]))
    # orbit: the inverse of tilting the logo, so the old tilt values give the old view
    orbit = Euler([math.radians(a) for a in P["orbit"]]).to_matrix().to_4x4()
    bpy.context.view_layer.update()
    cam.matrix_world = orbit.inverted() @ cam.matrix_world

    # one hard point light: casts the W's shadow onto the wall and sets which blue
    # each side face gets. Grab it and move it (G) to move the shadow.
    ld = bpy.data.lights.new("Key Light", 'POINT')
    ld.energy = P["light_power"]
    ld.shadow_soft_size = 0.0                               # point source -> razor shadow edge
    ld.use_soft_falloff = False
    ld.use_shadow_jitter = False
    ld.shadow_filter_radius = 0.0                           # no PCF blur on the shadow edge
    ld.shadow_maximum_resolution = 0.0001
    key = bpy.data.objects.new("Key Light", ld); sc.collection.objects.link(key)
    key.location = sun_dir() * P["light_dist"]

    uv_ng = grp_screen_uv(cam)
    logo_ng = grp_logo(grp_hatch(uv_ng), grp_light_dir(key))
    wall_ng = grp_wall(grp_halftone(uv_ng))

    cur, sf = import_logo()
    logo = curve_to_prism(cur, P["depth"], sf)
    if P["bevel"]:
        b = logo.modifiers.new("Bevel", 'BEVEL')
        b.width = P["bevel"]; b.segments = P["bevel_segs"]; b.limit_method = 'ANGLE'
        b.angle_limit = math.radians(30); b.harden_normals = False
        activate(logo); bpy.ops.object.modifier_apply(modifier=b.name)
        bpy.ops.object.shade_flat()
    logo.data.materials.append(mat_from_group("PopLogo", logo_ng))
    print("LOGO dims", tuple(round(v, 3) for v in logo.dimensions), "faces", len(logo.data.polygons))

    ink_coll = bpy.data.collections.new("Ink"); sc.collection.children.link(ink_coll)

    # wall behind the logo catches the shadow
    bpy.ops.mesh.primitive_plane_add(size=P["wall_size"])
    wall = bpy.context.active_object; wall.name = "Wall"
    wall.rotation_euler = (math.radians(90), 0, 0)          # normal faces -Y, toward the viewer
    wall.location = (0, P["depth"] / 2 + P["gap"], 0)
    wall.data.materials.append(mat_from_group("PopWall", wall_ng))
    for c in list(wall.users_collection):
        c.objects.unlink(wall)
    ink_coll.objects.link(wall)                              # never outlined

    # inverted-hull outline (alternative to freestyle; also shows in the viewport)
    if P["outline"] == "hull":
        hl = logo.copy(); hl.data = logo.data.copy(); hl.name = "Hull"
        sc.collection.objects.link(hl)
        hl.data.materials.clear(); hl.data.materials.append(mat_flat("HullInk", P["ink"], backfacing_only=True))
        so = hl.modifiers.new("Solidify", 'SOLIDIFY')
        so.thickness = P["hull_thick"]; so.offset = 1.0; so.use_flip_normals = True
        so.use_rim = False

    if P["outline"] == "freestyle":
        freestyle(sc, logo)
    elif P["outline"] == "lineart":
        lineart(sc, logo, cam)
    compositor(sc)
    sc.frame_set(1)          # evaluate the drivers
    return sc


def viewport_to_camera():
    """Open the saved file looking through the camera in Rendered shading."""
    for scr in bpy.data.screens:
        for area in scr.areas:
            if area.type != 'VIEW_3D':
                continue
            for sp in area.spaces:
                if sp.type == 'VIEW_3D':
                    sp.shading.type = 'RENDERED'
                    sp.region_3d.view_perspective = 'CAMERA'
                    sp.overlay.show_overlays = False


def lineart(sc, logo, cam):
    """Grease Pencil Line Art: live ink strokes, visible in the viewport and the
    render. One modifier for silhouette and creases, so the lines chain into
    each other at an even weight with no mismatched joins."""
    gp = bpy.data.grease_pencils.new("Ink Lines")
    ob = bpy.data.objects.new("Ink Lines", gp); sc.collection.objects.link(ob)
    ink = bpy.data.materials.new("Ink Stroke"); bpy.data.materials.create_gpencil_data(ink)
    ink.grease_pencil.color = hexc(P["ink"]); ink.grease_pencil.show_fill = False
    gp.materials.append(ink)
    layer = gp.layers.new("Ink"); layer.frames.new(sc.frame_current)
    layer.use_lights = False          # flat ink: the Key Light must not grey the strokes
    m = ob.modifiers.new("Ink", 'LINEART')
    m.source_type = 'OBJECT'; m.source_object = logo
    m.target_layer = "Ink"; m.target_material = ink
    m.use_contour = True; m.use_crease = True
    m.use_intersection = False; m.use_material = False; m.use_edge_mark = False; m.use_loose = False
    m.crease_threshold = math.radians(180 - P["crease_angle"])
    m.radius = P["stroke"]
    m.use_crease_on_smooth = True
    return ob


def freestyle(sc, logo):
    sc.render.use_freestyle = True
    vl = sc.view_layers[0]
    vl.use_freestyle = True
    fs = vl.freestyle_settings
    fs.mode = 'EDITOR'
    fs.crease_angle = math.radians(P["crease_angle"])
    fs.use_culling = True
    while fs.linesets:
        fs.linesets.remove(fs.linesets[0])
    ls = fs.linesets.new("Ink")
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = True
    ls.select_edge_mark = False
    ls.select_contour = True
    ls.select_material_boundary = False
    ls.select_by_collection = True
    ink = bpy.data.collections.get("Ink")
    if ink:
        ls.collection = ink
        ls.collection_negation = 'EXCLUSIVE'   # never outline the wall
    st = ls.linestyle
    st.color = hexc(P["ink"])[:3]
    st.thickness = P["line_px"]   # Blender scales this by resolution_percentage itself
    st.thickness_position = 'CENTER'
    st.caps = 'ROUND'
    st.use_chaining = True
    print("FREESTYLE thickness", st.thickness)


def compositor(sc):
    if not P.get("grain"):
        sc.render.use_compositing = False
        return
    ng = bpy.data.node_groups.new("Comp", "CompositorNodeTree")
    sc.compositing_node_group = ng
    rl = ng.nodes.new("CompositorNodeRLayers"); rl.location = (0, 0)
    ic = ng.nodes.new("CompositorNodeImageCoordinates"); ic.location = (200, -200)
    ng.links.new(rl.outputs["Image"], ic.inputs["Image"])
    wn = ng.nodes.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = '2D'; wn.location = (380, -200)
    ng.links.new(ic.outputs["Pixel"], wn.inputs["Vector"])
    sub = ng.nodes.new("ShaderNodeMath"); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = 0.5
    sub.location = (540, -200)
    ng.links.new(wn.outputs["Value"], sub.inputs[0])
    mul = ng.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = P["grain"]
    mul.location = (700, -200)
    ng.links.new(sub.outputs[0], mul.inputs[0])
    add = ng.nodes.new("ShaderNodeMix"); add.data_type = 'RGBA'; add.blend_type = 'ADD'
    add.inputs[0].default_value = 1.0; add.location = (880, 0)
    ng.links.new(rl.outputs["Image"], add.inputs[6]); ng.links.new(mul.outputs[0], add.inputs[7])
    ng.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    outn = ng.nodes.new("NodeGroupOutput"); outn.location = (1100, 0)
    ng.links.new(add.outputs[2], outn.inputs["Image"])
    sc.render.use_compositing = True


# ---------------------------------------------------------------- main
if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "renders", "test.png"))
    ap.add_argument("--samples", type=int, default=64)
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--save", default="")
    ap.add_argument("--norender", action="store_true")
    ap.add_argument("--set", action="append", default=[])
    args = ap.parse_args(argv)
    for kv in args.set:
        k, v = kv.split("=", 1)
        P[k] = v if (v.startswith("#") or k == "outline") else eval(v)
    sc = build(args)
    if args.save:
        viewport_to_camera()
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(args.save))
    if not args.norender:
        sc.render.filepath = os.path.abspath(args.out)
        sc.render.image_settings.file_format = 'PNG'
        sc.render.image_settings.color_depth = '8'
        bpy.ops.render.render(write_still=True)
        print("WROTE", sc.render.filepath)
