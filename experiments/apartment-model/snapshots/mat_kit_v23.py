"""Brick and herringbone floor as one-node designer materials, from scanned CC0 textures in library/textures.

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
    """Old factory brick from a whole-wall CC0 scan (Poly Haven factory_brick) at true scale, regraded.

    v13-v16: a procedural per-brick grid read as tile three rounds running; the advisor's test showed a scan
    reads as masonry at once, because its arris wear, bloom and mortar net are correlated with the joints.
    The scan gives structure only: its height map splits face from joint, and each is coloured from the
    measured values here (one gain on the whole scan turns the grey mortar violet). Wall-scale soot and dust
    noises on top break the repeat of the 1.36 m tile.
    """
    ng, gi, go = group("Brick", [
        ("Brick", "NodeSocketColor", P["brick"], None, None),             # mean brick face (linear)
        ("Brick Dark", "NodeSocketColor", P["brick_dark"], None, None),   # soot and burnt bricks
        ("Brick Pale", "NodeSocketColor", P["brick_pale"], None, None),   # the dusty grey-violet bloom
        ("Mortar", "NodeSocketColor", P["mortar"], None, None),
        ("Variation", "NodeSocketFloat", P["brick_var"], 0.0, 2.0),       # brick-to-brick contrast from the scan
        ("Dust", "NodeSocketFloat", P["brick_dust"], 0.0, 1.0),           # bloom and soot over bricks and joints
        ("Relief", "NodeSocketFloat", P["mortar_depth"], 0.0, 1.0),       # depth of joints and pitting
        ("Roughness", "NodeSocketFloat", 0.88, 0.0, 1.0),
    ], [("Shader", "NodeSocketShader")])
    nt = ng
    tc, sep = _xyz(nt)
    T = P["brick_tex_size"]
    u = math(nt, "ADD", sep.outputs["Y"], sep.outputs["X"])
    v = math(nt, "ADD", sep.outputs["Z"], P["brick_tex_z0"])
    uv = _vec(nt, math(nt, "DIVIDE", u, T), math(nt, "DIVIDE", v, T), 0.0)

    def img(path, data):
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(str(path), check_existing=True)
        if data:
            t.image.colorspace_settings.name = "Non-Color"
        t.interpolation = "Cubic"
        nt.links.new(uv, t.inputs["Vector"])
        return t
    D = P["brick_tex_dir"]
    col = img(D / "factory_brick_diff_2k.jpg", False)
    disp = img(D / "factory_brick_disp_2k.png", True)
    rgh = img(D / "factory_brick_rough_2k.jpg", True)
    lum = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(col.outputs["Color"], lum.inputs[0])
    joint = math(nt, "SUBTRACT", 1.0, step(nt, disp.outputs["Color"], P["brick_joint_t"], 0.04))   # 1 in the joints
    # faces: the scan's own brick-to-brick and in-brick tone around its mean (0.167), on the measured colour
    rel = math(nt, "SUBTRACT", math(nt, "DIVIDE", lum.outputs["Val"], 0.167), 1.0)
    tone = math(nt, "MULTIPLY", rel, gi.outputs["Variation"])
    face = _mix(nt, math(nt, "MULTIPLY", tone, -1.5, clamp=True), gi.outputs["Brick"], gi.outputs["Brick Dark"])
    face = _mix(nt, math(nt, "MULTIPLY", tone, 1.0, clamp=True), face, gi.outputs["Brick Pale"])
    # joints: the scan's mortar tone (mean 0.204) on the measured mortar colour
    mrel = math(nt, "DIVIDE", lum.outputs["Val"], 0.204)
    mort = nt.nodes.new("ShaderNodeMix")
    mort.data_type, mort.blend_type = "RGBA", "MULTIPLY"
    mort.inputs["Factor"].default_value = 1.0
    nt.links.new(gi.outputs["Mortar"], mort.inputs[6]); nt.links.new(_vec(nt, mrel, mrel, mrel), mort.inputs[7])
    col_out = _mix(nt, joint, face, mort.outputs[2])
    # wall-scale soot and dust across bricks and joints alike
    stain = _noise(nt, tc.outputs["Object"], 0.9, 3.0, 0.5)
    col_out = _mix(nt, math(nt, "MULTIPLY", math(nt, "MULTIPLY", math(nt, "SUBTRACT", stain.outputs["Fac"], 0.45), 1.2, clamp=True), gi.outputs["Dust"]),
                   col_out, gi.outputs["Brick Dark"])
    dust = _noise(nt, tc.outputs["Object"], 3.0, 5.0, 0.65)
    col_out = _mix(nt, math(nt, "MULTIPLY", math(nt, "MULTIPLY", math(nt, "SUBTRACT", dust.outputs["Fac"], 0.5), 1.6, clamp=True), gi.outputs["Dust"]),
                   col_out, gi.outputs["Brick Pale"])
    bump = nt.nodes.new("ShaderNodeBump")
    nt.links.new(math(nt, "MULTIPLY", gi.outputs["Relief"], 0.01), bump.inputs["Distance"])
    nt.links.new(disp.outputs["Color"], bump.inputs["Height"])
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(col_out, b.inputs["Base Color"])
    nt.links.new(math(nt, "MULTIPLY", gi.outputs["Roughness"], math(nt, "ADD", 0.8, math(nt, "MULTIPLY", rgh.outputs["Color"], 0.25))), b.inputs["Roughness"])
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
    strips = P.get("oak_tex_strips")
    if strips:
        # the scan is itself a floor of narrow planks with grain along U: each plank samples one source plank,
        # chosen at random, centred across it, so no source seam crosses a plank
        k = math(nt, "FLOOR", math(nt, "MULTIPLY", g1, len(strips) - 1e-3))
        cv = 0.0
        for idx, c in enumerate(strips):
            term = math(nt, "MULTIPLY", math(nt, "COMPARE", k, float(idx), 0.5), c)
            cv = term if idx == 0 else math(nt, "ADD", cv, term)
        tu = math(nt, "ADD", math(nt, "DIVIDE", a, S), g3)
        tv = math(nt, "ADD", cv, math(nt, "DIVIDE", math(nt, "SUBTRACT", b, w / 2), S))
    else:
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



def fabric_group(P):
    """Sofa_Fabric: Swyft "Linen" Pumice from a scanned linen (library/textures/fabric/rough_linen), box-projected
    in Object coordinates (the sofa is built in world metres). The scan is blue: its luminance is kept, normalised
    to its mean (0.40), shaped by Contrast, and multiplied onto Colour. Puckers: ripples running out of each seam,
    from the seam_d / seam_s attributes the upholstery kit writes on every block."""
    ng, gi, go = group("Sofa_Fabric", [
        ("Colour", "NodeSocketColor", P["sofa_colour"], None, None),
        ("Contrast", "NodeSocketFloat", P["sofa_tex_contrast"], 0.0, 3.0),
        ("Weave", "NodeSocketFloat", P["sofa_weave"], 0.0, 4.0),                   # gain on the Pumice weave detail
        ("Weave Tile", "NodeSocketFloat", P["sofa_weave_tile"], 0.02, 0.5),        # metres per weave tile
        ("Weave Size", "NodeSocketFloat", P["sofa_tex_size"], 0.05, 1.0),       # metres per texture tile
        ("Weave Relief", "NodeSocketFloat", P["sofa_weave_relief"], 0.0, 1.0),
        ("Roughness", "NodeSocketFloat", P["sofa_rough"], 0.0, 1.0),
        ("Sheen", "NodeSocketFloat", P["sofa_sheen"], 0.0, 1.0),
        ("Sheen Roughness", "NodeSocketFloat", P["sofa_sheen_rough"], 0.0, 1.0),
        ("Slub", "NodeSocketFloat", P["sofa_slub"], 0.0, 1.0),                     # streaky yarn tone
        ("Slub Length", "NodeSocketFloat", P["sofa_slub_len"], 0.005, 0.2),        # metres along the weft
        ("Slub Width", "NodeSocketFloat", P["sofa_slub_w"], 0.001, 0.05),          # metres across it
        ("Fleck", "NodeSocketFloat", P["sofa_fleck"], 0.0, 1.0),                   # heathered yarn: tone per 3 mm cell
        ("Puckers", "NodeSocketFloat", P["sofa_puckers"], 0.0, 1.0),
        ("Pucker Width", "NodeSocketFloat", P["sofa_pucker_w"], 0.005, 0.2),   # metres from the seam
    ], [("Shader", "NodeSocketShader")])
    nt = ng
    tc = nt.nodes.new("ShaderNodeTexCoord")
    vec = nt.nodes.new("ShaderNodeVectorMath"); vec.operation = "DIVIDE"
    nt.links.new(tc.outputs["Object"], vec.inputs[0])
    nt.links.new(_vec(nt, gi.outputs["Weave Size"], gi.outputs["Weave Size"], gi.outputs["Weave Size"]), vec.inputs[1])

    def tex(name, colour=True):
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(str(P["sofa_tex_dir"] / f"rough_linen_{name}_2k.jpg"), check_existing=True)
        if not colour:
            t.image.colorspace_settings.name = "Non-Color"
        t.projection, t.projection_blend = "BOX", 0.25
        t.interpolation = "Cubic"
        nt.links.new(vec.outputs[0], t.inputs["Vector"])
        return t
    diff, rough, disp = tex("diff"), tex("rough", False), tex("disp", False)
    lum = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(diff.outputs["Color"], lum.inputs[0])
    tone = math(nt, "POWER", math(nt, "DIVIDE", lum.outputs[0], 0.40), gi.outputs["Contrast"])
    # the real fabric: a high-passed, seamless patch of Swyft's Pumice close-up (assets/mat/pumice_weave.png,
    # mean 0.5); its weave and heather multiply the tone, Weave = gain on its contrast
    wv = nt.nodes.new("ShaderNodeVectorMath"); wv.operation = "DIVIDE"
    nt.links.new(tc.outputs["Object"], wv.inputs[0])
    nt.links.new(_vec(nt, gi.outputs["Weave Tile"], gi.outputs["Weave Tile"], gi.outputs["Weave Tile"]), wv.inputs[1])
    wt = nt.nodes.new("ShaderNodeTexImage")
    wt.image = bpy.data.images.load(str(P["sofa_weave_img"]), check_existing=True)
    wt.image.colorspace_settings.name = "Non-Color"
    wt.projection, wt.projection_blend, wt.interpolation = "BOX", 0.25, "Cubic"
    nt.links.new(wv.outputs[0], wt.inputs["Vector"])
    wlum = nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(wt.outputs["Color"], wlum.inputs[0])
    weave = math(nt, "MULTIPLY", math(nt, "SUBTRACT", wlum.outputs[0], 0.5), gi.outputs["Weave"])
    tone = math(nt, "MULTIPLY", tone, math(nt, "ADD", 1.0, math(nt, "MULTIPLY", weave, 2.0)))
    # slubs: thick and thin yarn as streaks along the weft, horizontal on the sides, along x on the tops
    # (photos 1-3 at 1:1: centimetre streaks are what reads at room distance; the 0.7 mm weave is sub-pixel)
    inv_l = math(nt, "DIVIDE", 1.0, gi.outputs["Slub Length"])
    inv_w = math(nt, "DIVIDE", 1.0, gi.outputs["Slub Width"])
    streaks = []
    for thin_axis in (2, 1):
        sc = [inv_l, inv_l, inv_l]; sc[thin_axis] = inv_w
        v = nt.nodes.new("ShaderNodeVectorMath"); v.operation = "MULTIPLY"
        nt.links.new(tc.outputs["Object"], v.inputs[0]); nt.links.new(_vec(nt, *sc), v.inputs[1])
        streaks.append(_noise(nt, v.outputs[0], 1.0, detail=3.0, rough=0.6).outputs["Fac"])
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    nz = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Normal"], nz.inputs[0])
    up = math(nt, "ABSOLUTE", nz.outputs["Z"])
    slub = math(nt, "ADD", math(nt, "MULTIPLY", streaks[0], math(nt, "SUBTRACT", 1.0, up)), math(nt, "MULTIPLY", streaks[1], up))
    tone = math(nt, "MULTIPLY", tone, math(nt, "ADD", 1.0, math(nt, "MULTIPLY", math(nt, "SUBTRACT", slub, 0.5),
                                                                   math(nt, "MULTIPLY", gi.outputs["Slub"], 2.0))))
    snap = nt.nodes.new("ShaderNodeVectorMath"); snap.operation = "SNAP"
    nt.links.new(tc.outputs["Object"], snap.inputs[0]); snap.inputs[1].default_value = (0.003, 0.003, 0.003)
    fl = _white(nt, snap.outputs[0]).outputs["Value"]
    tone = math(nt, "MULTIPLY", tone, math(nt, "ADD", 1.0, math(nt, "MULTIPLY", math(nt, "SUBTRACT", fl, 0.5),
                                                                   math(nt, "MULTIPLY", gi.outputs["Fleck"], 2.0))))
    base = nt.nodes.new("ShaderNodeMix"); base.data_type = "RGBA"; base.blend_type = "MULTIPLY"
    base.inputs["Factor"].default_value = 1.0
    nt.links.new(gi.outputs["Colour"], base.inputs["A"])
    nt.links.new(_vec(nt, tone, tone, tone), base.inputs["B"])
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(base.outputs["Result"], b.inputs["Base Color"])
    # roughness: the scan's own variation around the Roughness input
    nt.links.new(math(nt, "ADD", gi.outputs["Roughness"], math(nt, "MULTIPLY", math(nt, "SUBTRACT", rough.outputs["Color"], 0.5), 0.3)),
                 b.inputs["Roughness"])
    b.inputs["Specular IOR Level"].default_value = 0.3
    nt.links.new(gi.outputs["Sheen"], b.inputs["Sheen Weight"])
    nt.links.new(gi.outputs["Sheen Roughness"], b.inputs["Sheen Roughness"])
    nt.links.new(base.outputs["Result"], b.inputs["Sheen Tint"])
    # weave relief (fine) then seam puckers (coarse)
    bw = nt.nodes.new("ShaderNodeBump")
    bw.inputs["Distance"].default_value = 0.0006
    nt.links.new(gi.outputs["Weave Relief"], bw.inputs["Strength"])
    nt.links.new(wlum.outputs[0], bw.inputs["Height"])
    sd = nt.nodes.new("ShaderNodeAttribute"); sd.attribute_name = "seam_d"
    ss = nt.nodes.new("ShaderNodeAttribute"); ss.attribute_name = "seam_s"
    fall = math(nt, "POWER", math(nt, "SUBTRACT", 1.0, math(nt, "DIVIDE", sd.outputs["Fac"], gi.outputs["Pucker Width"]), clamp=True), 2.0)
    n1 = _noise(nt, _vec(nt, math(nt, "MULTIPLY", ss.outputs["Fac"], 6.0), 0.0, 0.0), 1.0, detail=2.0, dims="3D")
    ph = math(nt, "MULTIPLY", math(nt, "ADD", ss.outputs["Fac"], math(nt, "MULTIPLY", n1.outputs["Fac"], 0.08)), 6.283 / 0.045)
    rip = math(nt, "MULTIPLY", math(nt, "SINE", ph), math(nt, "MULTIPLY", n1.outputs["Fac"], 2.0))
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Distance"].default_value = 0.003
    nt.links.new(gi.outputs["Puckers"], bp.inputs["Strength"])
    nt.links.new(math(nt, "MULTIPLY", rip, fall), bp.inputs["Height"])
    nt.links.new(bw.outputs["Normal"], bp.inputs["Normal"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    nt.links.new(b.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng
