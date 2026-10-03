"""Procedural brick and herringbone floor as one-node designer materials (shader math, no image textures).

Both work in Object coordinates, which equal world metres for every shell object (built at the origin).
brick_group(P):      walls in plane x (the window wall); u = y + x runs along a course on any face that turns.
herringbone_group(P): floor in plane z; the herringbone spine runs along x (rectified photos 2 and 3).
"""
import bpy

from nodes import auto_layout, group, math, step


def _vec(nt, x, y, z=0.0):
    c = nt.nodes.new("ShaderNodeCombineXYZ")
    for i, v in enumerate((x, y, z)):
        if hasattr(v, "bl_rna"):
            nt.links.new(v, c.inputs[i])
        else:
            c.inputs[i].default_value = v
    return c.outputs[0]


def _noise(nt, vec, scale, detail=4.0, rough=0.55, dims="3D"):
    t = nt.nodes.new("ShaderNodeTexNoise")
    t.noise_dimensions = dims
    t.inputs["Scale"].default_value = scale
    t.inputs["Detail"].default_value = detail
    t.inputs["Roughness"].default_value = rough
    nt.links.new(vec, t.inputs["Vector"])
    return t


def _white(nt, vec):
    t = nt.nodes.new("ShaderNodeTexWhiteNoise")
    t.noise_dimensions = "3D"
    nt.links.new(vec, t.inputs["Vector"])
    return t


def _mix(nt, fac, a, b):
    m = nt.nodes.new("ShaderNodeMix")
    m.data_type = "RGBA"
    for sock, v in ((m.inputs["Factor"], fac), (m.inputs[6], a), (m.inputs[7], b)):
        if hasattr(v, "bl_rna"):
            nt.links.new(v, sock)
        else:
            sock.default_value = v
    return m.outputs[2]


def _xyz(nt):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    return tc, sep


def _edge_dist(nt, f, length):
    """Distance (m) from a 0-1 coordinate f to the nearer end of a unit `length` m long."""
    return math(nt, "MULTIPLY", math(nt, "MINIMUM", f, math(nt, "SUBTRACT", 1.0, f)), length)


def brick_group(P):
    """Old factory brick: burnt, common and pale buff bricks with a wide tone spread; flush mortar near the brick tone."""
    ng, gi, go = group("Brick", [
        ("Brick", "NodeSocketColor", P["brick"], None, None),             # the common brick face (linear)
        ("Brick Dark", "NodeSocketColor", P["brick_dark"], None, None),   # burnt / sooted bricks
        ("Brick Pale", "NodeSocketColor", P["brick_pale"], None, None),   # the odd pale, greyer brick
        ("Mortar", "NodeSocketColor", P["mortar"], None, None),
        ("Variation", "NodeSocketFloat", P["brick_var"], 0.0, 1.0),       # brick-to-brick tone spread
        ("Wear", "NodeSocketFloat", P["brick_wear"], 0.0, 1.0),           # pitted faces, rounded arrises
        ("Mortar Depth", "NodeSocketFloat", P["mortar_depth"], 0.0, 2.0), # relief: 1 = joints 2 mm behind the face
        ("Roughness", "NodeSocketFloat", 0.88, 0.0, 1.0),
    ], [("Shader", "NodeSocketShader")])
    nt = ng
    tc, sep = _xyz(nt)
    C, St = P["brick_course"], P["brick_len"]                     # course height, stretcher pitch (with joint)
    j = P["mortar_w"] / 2
    # a hand-laid wall is not a grid: warp both axes a few mm with low-frequency noise
    warp = _noise(nt, tc.outputs["Object"], 2.5, 2.0, 0.5)
    wsep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(warp.outputs["Color"], wsep.inputs[0])
    u = math(nt, "ADD", math(nt, "ADD", sep.outputs["Y"], sep.outputs["X"]), math(nt, "MULTIPLY", math(nt, "SUBTRACT", wsep.outputs[0], 0.5), 0.012))
    v = math(nt, "ADD", sep.outputs["Z"], math(nt, "MULTIPLY", math(nt, "SUBTRACT", wsep.outputs[1], 0.5), 0.006))
    vr = math(nt, "DIVIDE", v, C)
    row = math(nt, "FLOOR", vr)
    fv = math(nt, "SUBTRACT", vr, row)
    # English garden wall bond: a header course every N courses, stretchers between (lap of half a brick)
    N = P["brick_header_every"]
    if N > 0:
        hc = math(nt, "LESS_THAN", math(nt, "FLOORED_MODULO", row, N), 0.5)
    else:
        hc = 0.0
    unit = math(nt, "SUBTRACT", St, math(nt, "MULTIPLY", hc, St / 2)) if N > 0 else St
    off = math(nt, "ADD", math(nt, "MULTIPLY", math(nt, "FLOORED_MODULO", row, 2), St / 2),
               math(nt, "MULTIPLY", hc, St / 4) if N > 0 else 0.0)
    ur = math(nt, "DIVIDE", math(nt, "ADD", u, off), unit)
    col = math(nt, "FLOOR", ur)
    fu = math(nt, "SUBTRACT", ur, col)
    d = math(nt, "MINIMUM", _edge_dist(nt, fu, unit), _edge_dist(nt, fv, C))
    # per-brick random values
    rid = _white(nt, _vec(nt, col, row, 3.7))
    r1 = rid.outputs["Value"]
    sep2 = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(rid.outputs["Color"], sep2.inputs[0])
    r2, r3 = sep2.outputs[1], sep2.outputs[2]
    # face colour (advisor: the tone spread between bricks is the pattern, not the joints): a categorical pick
    # per brick (burnt / common / pale buff), a continuous spread inside each class, and a gradient along the brick
    burnt = math(nt, "LESS_THAN", r1, P["brick_burnt_share"])
    pale = math(nt, "GREATER_THAN", r1, 1.0 - P["brick_pale_share"])
    spread = math(nt, "MULTIPLY", math(nt, "SUBTRACT", r2, 0.3), gi.outputs["Variation"])
    face = _mix(nt, math(nt, "MAXIMUM", spread, 0.0), gi.outputs["Brick"], gi.outputs["Brick Dark"])
    face = _mix(nt, math(nt, "MULTIPLY", burnt, math(nt, "MULTIPLY_ADD", r3, 0.4, 0.6)), face, gi.outputs["Brick Dark"])
    face = _mix(nt, math(nt, "MULTIPLY", pale, math(nt, "MULTIPLY_ADD", r3, 0.5, 0.5)), face, gi.outputs["Brick Pale"])
    grad = math(nt, "MULTIPLY", math(nt, "MULTIPLY", math(nt, "SUBTRACT", fu, 0.5), math(nt, "SUBTRACT", r3, 0.5)), 1.2)
    face = _mix(nt, math(nt, "ABSOLUTE", grad), face, gi.outputs["Brick Dark"])
    # mottling inside a brick, broad soot staining and dust smeared across several bricks
    mott = _noise(nt, _vec(nt, math(nt, "ADD", u, math(nt, "MULTIPLY", r3, 50)), v, 0.0), 18.0, 5.0, 0.6)
    face = _mix(nt, math(nt, "MULTIPLY", math(nt, "SUBTRACT", mott.outputs["Fac"], 0.35), 0.5, clamp=True),
                face, gi.outputs["Brick Dark"])
    stain = _noise(nt, tc.outputs["Object"], 0.9, 3.0, 0.5)
    face = _mix(nt, math(nt, "MULTIPLY", math(nt, "SUBTRACT", stain.outputs["Fac"], 0.45), 0.6, clamp=True),
                face, gi.outputs["Brick Dark"])
    dust = _noise(nt, tc.outputs["Object"], 3.0, 4.0, 0.6)
    dfac = math(nt, "MULTIPLY", math(nt, "SUBTRACT", dust.outputs["Fac"], 0.52), 2.0 * P["brick_dust"], clamp=True)
    face = _mix(nt, dfac, face, gi.outputs["Brick Pale"])
    # mortar near the brick's own tone, soft-edged, and missing in stretches (smeared, flush, dirty)
    pit = _noise(nt, tc.outputs["Object"], 60.0, 6.0, 0.7)
    rag = math(nt, "MULTIPLY", math(nt, "SUBTRACT", pit.outputs["Fac"], 0.5), math(nt, "MULTIPLY", gi.outputs["Wear"], 0.008))
    dj = math(nt, "ADD", math(nt, "SUBTRACT", d, j), rag)
    brick_mask = step(nt, dj, 0.0, 0.004)                          # 0 in the joint, 1 on the face
    vis = step(nt, _noise(nt, tc.outputs["Object"], 9.0, 3.0, 0.6).outputs["Fac"], 0.42, 0.25)
    col_out = _mix(nt, math(nt, "MULTIPLY", math(nt, "SUBTRACT", 1.0, brick_mask), vis), face, gi.outputs["Mortar"])
    # height in mm (brick research agent: Bump Distance 0.001 with height in mm). Mortar Depth 1 = joints 2 mm
    # back; the default is faint (advisor: the wall is backlit, no relief reads in the photos)
    arris = step(nt, dj, 0.002, 0.004)
    face_mm = math(nt, "MULTIPLY", math(nt, "SUBTRACT", r2, 0.5), 1.0)
    wave = _noise(nt, _vec(nt, u, v, math(nt, "MULTIPLY", r1, 20.0)), 22.0, 2.0, 0.5)
    face_mm = math(nt, "ADD", face_mm, math(nt, "MULTIPLY", math(nt, "SUBTRACT", wave.outputs["Fac"], 0.5), 0.9))
    face_mm = math(nt, "SUBTRACT", face_mm, math(nt, "MULTIPLY", math(nt, "MULTIPLY", pit.outputs["Fac"], gi.outputs["Wear"]), 0.6))
    height = math(nt, "ADD", math(nt, "MULTIPLY", arris, 2.0), math(nt, "MULTIPLY", arris, face_mm))
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Distance"].default_value = 0.001
    nt.links.new(math(nt, "MULTIPLY", height, gi.outputs["Mortar Depth"]), bump.inputs["Height"])
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(col_out, b.inputs["Base Color"])
    nt.links.new(math(nt, "ADD", gi.outputs["Roughness"], math(nt, "MULTIPLY", r3, 0.06)), b.inputs["Roughness"])
    nt.links.new(bump.outputs[0], b.inputs["Normal"])
    nt.links.new(b.outputs[0], go.inputs["Shader"])
    auto_layout(nt)
    return ng


def herringbone_group(P):
    """Herringbone oak: n x 1 planks (length = n widths), spine along x, per-plank tone and grain, bevelled seams.

    Cell (i, j) of a w-grid in plank axes p, q (45 deg to the room): c = (i - j) mod 2n; c < n is a plank along p
    with origin cell (i - c, j), else a plank along q with origin cell (i, j - (2n - c) + 1). Checked to tile.
    """
    ng, gi, go = group("Oak_Floor", [
        ("Tint", "NodeSocketColor", P["oak_tint"], None, None),           # multiplies the scanned oak (linear)
        ("Brightness", "NodeSocketFloat", P["oak_bright"], 0.0, 3.0),
        ("Saturation", "NodeSocketFloat", P["oak_sat"], 0.0, 2.0),        # 1 = the veneer's own colour
        ("Grain", "NodeSocketFloat", P["oak_grain"], 0.0, 2.0),           # contrast of the wood figure
        ("Variation", "NodeSocketFloat", P["oak_var"], 0.0, 1.0),         # plank-to-plank tone spread
        ("Seams", "NodeSocketFloat", P["oak_seams"], 0.0, 1.0),           # darkness and depth of the bevelled joints
        ("Roughness", "NodeSocketFloat", P["oak_rough"], 0.0, 1.0),
        ("Anisotropy", "NodeSocketFloat", P["oak_aniso"], 0.0, 1.0),      # window reflections streak along each plank
    ], [("Shader", "NodeSocketShader")])
    nt = ng
    tc, sep = _xyz(nt)
    n, w = P["plank_ratio"], P["plank_w"]
    L = n * w
    r2 = 2 ** -0.5
    x = math(nt, "SUBTRACT", sep.outputs["X"], P["plank_x0"])
    y = math(nt, "SUBTRACT", sep.outputs["Y"], P["plank_y0"])
    # plank axes: p + q runs along x, so the spine (the staircase direction) is along the room
    p = math(nt, "DIVIDE", math(nt, "MULTIPLY", math(nt, "SUBTRACT", x, y), r2), w)
    q = math(nt, "DIVIDE", math(nt, "MULTIPLY", math(nt, "ADD", x, y), r2), w)
    i = math(nt, "FLOOR", p)
    jj = math(nt, "FLOOR", q)
    c = math(nt, "FLOORED_MODULO", math(nt, "SUBTRACT", i, jj), 2 * n)
    is_v = math(nt, "GREATER_THAN", c, n - 0.5)                   # 1 = plank along q
    rr = math(nt, "SUBTRACT", 2 * n, c)
    # origin cell of the plank
    oi = math(nt, "SUBTRACT", i, math(nt, "MULTIPLY", math(nt, "SUBTRACT", 1.0, is_v), c))
    oj = math(nt, "SUBTRACT", jj, math(nt, "MULTIPLY", is_v, math(nt, "SUBTRACT", rr, 1.0)))
    # plank-local coordinates in metres: a along the plank (0..L), b across (0..w)
    a_h = math(nt, "MULTIPLY", math(nt, "SUBTRACT", p, oi), w)
    b_h = math(nt, "MULTIPLY", math(nt, "SUBTRACT", q, oj), w)
    a = _mix_f(nt, is_v, a_h, b_h)
    b = _mix_f(nt, is_v, b_h, a_h)
    rid = _white(nt, _vec(nt, oi, oj, is_v))
    rv = rid.outputs["Value"]
    rsep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(rid.outputs["Color"], rsep.inputs[0])
    g1, g2 = rsep.outputs[1], rsep.outputs[2]
    rsep2 = nt.nodes.new("ShaderNodeSeparateColor")
    rid2 = _white(nt, _vec(nt, oi, oj, math(nt, "ADD", is_v, 7.3)))
    nt.links.new(rid2.outputs["Color"], rsep2.inputs[0])
    g3, g4, g5 = rsep2.outputs[0], rsep2.outputs[1], rsep2.outputs[2]
    # grain: a scanned flat-sawn oak veneer (Poly Haven oak_veneer_01, CC0, 1.83 m square, grain along its V),
    # sampled in each plank's own coordinates with a random offset and end-for-end flip (v14: the procedural ring
    # model read as zebrano twice). Plank length a runs along the veneer's grain.
    S = P["oak_tex_size"]
    a = math(nt, "ADD", math(nt, "MULTIPLY", math(nt, "GREATER_THAN", g4, 0.5), math(nt, "SUBTRACT", L, math(nt, "MULTIPLY", a, 2.0))), a)
    tu = math(nt, "ADD", math(nt, "DIVIDE", b, S), g1)
    tv = math(nt, "ADD", math(nt, "DIVIDE", a, S), g3)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(P["oak_tex"]), check_existing=True)
    tex.interpolation, tex.extension = "Cubic", "REPEAT"
    nt.links.new(_vec(nt, tu, tv, 0.0), tex.inputs["Vector"])
    rtex = nt.nodes.new("ShaderNodeTexImage")
    rtex.image = bpy.data.images.load(str(P["oak_rough_tex"]), check_existing=True)
    rtex.image.colorspace_settings.name = "Non-Color"
    nt.links.new(_vec(nt, tu, tv, 0.0), rtex.inputs["Vector"])
    hsv = nt.nodes.new("ShaderNodeHueSaturation")
    nt.links.new(tex.outputs["Color"], hsv.inputs["Color"])
    nt.links.new(gi.outputs["Saturation"], hsv.inputs["Saturation"])
    # grain contrast around the veneer's mean tone, then per-plank value spread and a gentle gradient along it
    mean = (0.23, 0.23, 0.23, 1.0)
    colr = _mix(nt, gi.outputs["Grain"], mean, hsv.outputs["Color"])
    grad = math(nt, "MULTIPLY", math(nt, "SUBTRACT", math(nt, "DIVIDE", a, L), 0.5), math(nt, "SUBTRACT", g5, 0.5))
    val = math(nt, "MULTIPLY", gi.outputs["Brightness"],
               math(nt, "ADD", 1.0, math(nt, "ADD", math(nt, "MULTIPLY", math(nt, "SUBTRACT", rv, 0.5), gi.outputs["Variation"]),
                                         math(nt, "MULTIPLY", grad, 0.3))))
    tint = nt.nodes.new("ShaderNodeMix")
    tint.data_type, tint.blend_type = "RGBA", "MULTIPLY"
    tint.inputs["Factor"].default_value = 1.0
    nt.links.new(colr, tint.inputs[6]); nt.links.new(gi.outputs["Tint"], tint.inputs[7])
    colr = nt.nodes.new("ShaderNodeMix")
    colr.data_type, colr.blend_type = "RGBA", "MULTIPLY"
    colr.inputs["Factor"].default_value = 1.0
    nt.links.new(tint.outputs[2], colr.inputs[6]); nt.links.new(_vec(nt, val, val, val), colr.inputs[7])
    colr = colr.outputs[2]
    fig = math(nt, "MULTIPLY", math(nt, "SUBTRACT", 0.5, rtex.outputs["Color"]), 0.3)   # veneer pores: rougher, a touch lower
    # bevelled seams: ~1.5 mm micro-bevel on every plank edge
    d = math(nt, "MINIMUM", _edge_dist(nt, math(nt, "DIVIDE", a, L), L), _edge_dist(nt, math(nt, "DIVIDE", b, w), w))
    seam = math(nt, "SUBTRACT", 1.0, step(nt, d, P["plank_bevel"], P["plank_bevel"]))
    colr = _mix(nt, math(nt, "MULTIPLY", seam, gi.outputs["Seams"]), colr, (0.01, 0.006, 0.004, 1.0))
    height = math(nt, "SUBTRACT", math(nt, "MULTIPLY", fig, 0.05), seam)
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Distance"].default_value = 0.0015
    nt.links.new(gi.outputs["Seams"], bump.inputs["Strength"])
    nt.links.new(height, bump.inputs["Height"])
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(colr, bsdf.inputs["Base Color"])
    # satin sheen: per-plank roughness spread, and anisotropy along the plank so window reflections streak
    # along the grain (advisor; photo 4). Tangent: planks along p run (1, -1, 0), along q (1, 1, 0)
    rough = math(nt, "ADD", gi.outputs["Roughness"], math(nt, "MULTIPLY", math(nt, "SUBTRACT", g2, 0.5), 0.16))
    nt.links.new(math(nt, "SUBTRACT", rough, fig), bsdf.inputs["Roughness"])
    nt.links.new(gi.outputs["Anisotropy"], bsdf.inputs["Anisotropic"])
    bsdf.inputs["Specular IOR Level"].default_value = P["oak_spec"]          # v13 review: the sheen read as milky haze
    nt.links.new(_vec(nt, r2, math(nt, "SUBTRACT", math(nt, "MULTIPLY", is_v, 2 * r2), r2), 0.0), bsdf.inputs["Tangent"])
    nt.links.new(bump.outputs[0], bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs[0], go.inputs["Shader"])
    auto_layout(nt)
    return ng


def _mix_f(nt, fac, a, b):
    m = nt.nodes.new("ShaderNodeMix")
    m.data_type = "FLOAT"
    for sock, v in ((m.inputs["Factor"], fac), (m.inputs[2], a), (m.inputs[3], b)):
        if hasattr(v, "bl_rna"):
            nt.links.new(v, sock)
        else:
            sock.default_value = v
    return m.outputs[0]
