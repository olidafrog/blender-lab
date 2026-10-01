"""Architecture kit, Blender part: a facade traced in reference pixels, built at true scale.

From experiments/aztechno-building (Freddy Mamani's Crucero del Sur). The model is a straight-on photo with
a level shift-lens camera: one px-per-metre value maps the traced spec (arch_shapes.py) to metres on the
facade plane (y = 0, +y away from the camera), and the camera is computed so that plane lands on the
reference's pixels.

    sys.path.insert(0, "<repo>/library/models/arch-kit")
    import arch_kit as K
    K.configure(P, axis=727.0, ground=882.0)   # P: ppm, cam_d, cam_h, cam_x, res_x, res_y, and the
                                               # material defaults read by paint_group / glass_group
    K.slab("Band", [outline_px, *holes_px], d0, d1, mat, bev)    # filled curve with holes -> mesh
    x, z = K.at_depth(u, v, y)                 # a point y m behind the facade that lands on pixel (u, v)
    K.camera_from_spec(scene)

Material groups (one control node each, via tools/nodes.py): paint_group() reads red, paint_rough,
paint_var, grime, chalk, base_dirt, sky_glossy; glass_group() reads glass_tint, glass_refl, glass_rough,
glass_see, glass_wobble, glass_spread. Glass objects carry pane_x0, pane_z0, pane_pu, pane_pv.
"""
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from arch_shapes import circle, offset, rect, simple_polygon  # noqa: E402,F401
from nodes import auto_layout, group  # noqa: E402

CFG = {}


def configure(params, axis, ground):
    """params is the experiment's P dict (read live, so --set overrides apply); axis and ground in px."""
    global CFG
    CFG = params
    CFG["axis"], CFG["ground"] = axis, ground


def X(u):
    return (u - CFG["axis"]) / CFG["ppm"]


def Z(v):
    return (CFG["ground"] - v) / CFG["ppm"]


def at_depth(u, v, y):
    """World (x, z) of a point at depth y (m behind the facade plane, + away from the camera) that lands
    on reference pixel (u, v): for parts set back from the facade (roof tanks, far wings)."""
    k = (CFG["cam_d"] + y) / CFG["cam_d"]
    u_axis = CFG["axis"] + CFG["cam_x"] * CFG["ppm"]
    v_h = CFG["ground"] - CFG["cam_h"] * CFG["ppm"]
    return CFG["cam_x"] + (u - u_axis) / CFG["ppm"] * k, CFG["cam_h"] + (v_h - v) / CFG["ppm"] * k


def link(ob, coll=None):
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def coll(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


# ---------------------------------------------------------------- geometry builders

_mesh_cache = []


def slab(name, loops_px, d0, d1, mat, bev=0.01, collection=None):
    """Filled 2D outline (outer + holes, in px) extruded from depth d0 to d1 (m, toward the street),
    round-bevelled, converted to a mesh."""
    bad = [i for i, lp in enumerate(loops_px) if not simple_polygon(lp)]
    assert not bad, f"{name}: self-intersecting loop(s) {bad}"
    bev = max(0.0, min(bev, (d1 - d0) / 2 - 0.002))
    bpx = bev * CFG["ppm"]
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    for i, lp in enumerate(loops_px):
        lp = offset(lp, -bpx if i == 0 else bpx) if bpx > 0.05 else lp
        sp = cu.splines.new("POLY")
        sp.points.add(len(lp) - 1)
        for p, (u, v) in zip(sp.points, lp):
            p.co = (X(u), Z(v), 0, 1)
        sp.use_cyclic_u = True
    cu.extrude = max((d1 - d0) / 2 - bev, 0.0005)
    cu.bevel_depth = bev
    cu.bevel_resolution = 2
    ob = bpy.data.objects.new(name, cu)
    link(ob)
    ob.rotation_euler = (math.pi / 2, 0, 0)
    ob.location = (0, -(d0 + d1) / 2, 0)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    me.transform(ob.matrix_world)
    me.use_auto_texspace = True          # the curve's texture space is stale after the transform
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    assert len(me.polygons) > 0, f"empty slab {name}"
    me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = False
    mo = bpy.data.objects.new(name, me)
    link(mo, collection)
    return mo


def box(name, x0, x1, y0, y1, z0, z1, mat, collection=None):
    me = bpy.data.meshes.new(name)
    v = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    me.from_pydata(v, [], f)
    me.materials.append(mat)
    return link(bpy.data.objects.new(name, me), collection)


def plane_px(name, pts, d, mat, collection=None):
    """Flat polygon (px) at depth d, facing the street."""
    return slab(name, [pts], d - 0.0005, d + 0.0005, mat, bev=0.0, collection=collection)


def scan(pts, axis, value):
    """Intervals of the polygon on the line u=value (axis 0) or v=value (axis 1), even-odd."""
    xs = []
    n = len(pts)
    for i in range(n):
        a, b = pts[i - 1], pts[i]
        if (a[axis] <= value < b[axis]) or (b[axis] <= value < a[axis]):
            t = (value - a[axis]) / (b[axis] - a[axis])
            xs.append(a[1 - axis] + t * (b[1 - axis] - a[1 - axis]))
    xs.sort()
    return list(zip(xs[0::2], xs[1::2]))


def bar_step(lo, hi, pitch):
    """The spacing bars() really uses: the span divided evenly (whole span when there are no bars)."""
    n = int((hi - lo) / pitch + 0.5) if pitch else 1
    return (hi - lo) / max(n, 1)


def bars(pts, pitch, axis, width_px):
    """Mullion bars across a polygon every `pitch` px: vertical bars for axis 0 (u = const)."""
    lo = min(p[axis] for p in pts)
    hi = max(p[axis] for p in pts)
    out = []
    n = int((hi - lo) / pitch + 0.5)
    if n < 2:
        return out
    step = (hi - lo) / n
    for i in range(1, n):
        c = lo + i * step
        for a, b in scan(pts, axis, c):
            if axis == 0:
                out.append(rect(c - width_px / 2, a, c + width_px / 2, b))
            else:
                out.append(rect(a, c - width_px / 2, b, c + width_px / 2))
    return out


# ---------------------------------------------------------------- materials


def tex_image(nt, path, non_color=False):
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = bpy.data.images.load(str(Path(path).resolve()), check_existing=True)
    if non_color:
        n.image.colorspace_settings.name = "Non-Color"
    n.projection = "BOX"
    n.projection_blend = 0.2
    return n


def paint_group():
    """Exterior acrylic paint on cement render: colour, large mottling, crevice grime, plaster bump."""
    ng, gi, go = group("Paint", [
        ("Colour", "NodeSocketColor", CFG["red"], None, None),
        ("Roughness", "NodeSocketFloat", CFG["paint_rough"], 0.0, 1.0),
        ("Variation", "NodeSocketFloat", CFG["paint_var"], 0.0, 1.0),   # sun-faded mottling
        ("Grime", "NodeSocketFloat", CFG["grime"], 0.0, 1.0),           # dirt in corners and under ledges
        ("Waviness", "NodeSocketFloat", 0.5, 0.0, 1.0),                # low-frequency unevenness of cast render
        ("Chalk", "NodeSocketFloat", CFG["chalk"], 0.0, 1.0),            # pale sun-faded blotches (roller patches)
    ], [("Shader", "NodeSocketShader")])
    N = ng.nodes.new
    L = ng.links.new
    tc = N("ShaderNodeTexCoord")
    # large mottling: value +-(variation * 18 %)
    mot = N("ShaderNodeTexNoise")
    mot.inputs["Scale"].default_value = 0.45
    mot.inputs["Detail"].default_value = 4.0
    L(tc.outputs["Object"], mot.inputs["Vector"])
    fine = N("ShaderNodeTexNoise")
    fine.inputs["Scale"].default_value = 9.0
    fine.inputs["Detail"].default_value = 2.0
    L(tc.outputs["Object"], fine.inputs["Vector"])
    mix_n = N("ShaderNodeMix")
    mix_n.data_type = "FLOAT"
    mix_n.inputs[0].default_value = 0.35
    L(mot.outputs["Fac"], mix_n.inputs[2])
    L(fine.outputs["Fac"], mix_n.inputs[3])
    cen = N("ShaderNodeMath")
    cen.operation = "SUBTRACT"
    L(mix_n.outputs[0], cen.inputs[0])
    cen.inputs[1].default_value = 0.5
    amt = N("ShaderNodeMath")
    amt.operation = "MULTIPLY"
    L(cen.outputs[0], amt.inputs[0])
    L(gi.outputs["Variation"], amt.inputs[1])
    gain = N("ShaderNodeMath")
    gain.operation = "MULTIPLY_ADD"
    L(amt.outputs[0], gain.inputs[0])
    gain.inputs[1].default_value = 0.9
    gain.inputs[2].default_value = 1.0
    col = N("ShaderNodeMix")
    col.data_type = "RGBA"
    col.blend_type = "MULTIPLY"
    col.inputs[0].default_value = 1.0
    L(gi.outputs["Colour"], col.inputs[6])
    comb = N("ShaderNodeCombineColor")
    for i in range(3):
        L(gain.outputs[0], comb.inputs[i])
    L(comb.outputs[0], col.inputs[7])
    # grime (advisor): streaks just below ledges (local AO x a vertically stretched noise) plus dust on
    # up-facing tops; freshly painted, so keep it light
    ao = N("ShaderNodeAmbientOcclusion")
    ao.samples = 8
    ao.only_local = True
    ao.inputs["Distance"].default_value = 0.15
    inv = N("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    L(ao.outputs["AO"], inv.inputs[1])
    mp = N("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (6.0, 6.0, 0.5)
    L(tc.outputs["Object"], mp.inputs["Vector"])
    st = N("ShaderNodeTexNoise")
    st.inputs["Scale"].default_value = 3.0
    st.inputs["Detail"].default_value = 3.0
    L(mp.outputs[0], st.inputs["Vector"])
    sm = N("ShaderNodeMath")
    sm.operation = "MULTIPLY"
    L(inv.outputs[0], sm.inputs[0])
    L(st.outputs["Fac"], sm.inputs[1])
    geo = N("ShaderNodeNewGeometry")
    gz = N("ShaderNodeSeparateXYZ")
    L(geo.outputs["Normal"], gz.inputs[0])
    up = N("ShaderNodeMath")
    up.operation = "MAXIMUM"
    L(gz.outputs["Z"], up.inputs[0])
    up.inputs[1].default_value = 0.0
    tot = N("ShaderNodeMath")
    tot.operation = "MULTIPLY_ADD"
    L(sm.outputs[0], tot.inputs[0])
    tot.inputs[1].default_value = 2.0
    L(up.outputs[0], tot.inputs[2])
    gm0 = N("ShaderNodeMath")
    gm0.operation = "MULTIPLY"
    L(tot.outputs[0], gm0.inputs[0])
    L(gi.outputs["Grime"], gm0.inputs[1])
    # splash zone at the foot of walls: 1 at the ground, 0 by 0.8 m, broken by the streak noise
    pz = N("ShaderNodeSeparateXYZ")
    L(tc.outputs["Object"], pz.inputs[0])
    foot = N("ShaderNodeMapRange")
    L(pz.outputs["Z"], foot.inputs["Value"])
    foot.inputs["From Min"].default_value = 0.0
    foot.inputs["From Max"].default_value = 0.8
    foot.inputs["To Min"].default_value = 1.0
    foot.inputs["To Max"].default_value = 0.0
    fz = N("ShaderNodeMath")
    fz.operation = "MULTIPLY"
    L(foot.outputs[0], fz.inputs[0])
    L(st.outputs["Fac"], fz.inputs[1])
    fb = N("ShaderNodeMath")
    fb.operation = "MULTIPLY"
    L(fz.outputs[0], fb.inputs[0])
    fb.inputs[1].default_value = CFG["base_dirt"] * 1.6
    gm = N("ShaderNodeMath")
    gm.operation = "ADD"
    gm.use_clamp = True
    L(gm0.outputs[0], gm.inputs[0])
    L(fb.outputs[0], gm.inputs[1])
    dirt = N("ShaderNodeMix")
    dirt.data_type = "RGBA"
    dirt.blend_type = "MIX"
    L(gm.outputs[0], dirt.inputs[0])
    L(col.outputs[2], dirt.inputs[6])
    dirt.inputs[7].default_value = (0.30, 0.26, 0.21, 1)
    # low-frequency plaster waviness (cast render is never flat); fine grain is invisible at this distance
    bn = N("ShaderNodeTexNoise")
    bn.inputs["Scale"].default_value = 0.6
    bn.inputs["Detail"].default_value = 3.0
    L(tc.outputs["Object"], bn.inputs["Vector"])
    bs = N("ShaderNodeMath")
    bs.operation = "MULTIPLY"
    L(gi.outputs["Waviness"], bs.inputs[0])
    bs.inputs[1].default_value = 0.4
    bump = N("ShaderNodeBump")
    bump.inputs["Distance"].default_value = 0.02
    L(bs.outputs[0], bump.inputs["Strength"])
    L(bn.outputs["Fac"], bump.inputs["Height"])
    # chalky fade: pale, rougher blotches 10-30 cm across (reference red wall at 1:1)
    ck = N("ShaderNodeTexNoise")
    ck.inputs["Scale"].default_value = 3.5
    ck.inputs["Detail"].default_value = 8.0
    ck.inputs["Roughness"].default_value = 0.65
    L(tc.outputs["Object"], ck.inputs["Vector"])
    ckm = N("ShaderNodeMapRange")
    L(ck.outputs["Fac"], ckm.inputs["Value"])
    ckm.inputs["From Min"].default_value = 0.52
    ckm.inputs["From Max"].default_value = 0.72
    ckf = N("ShaderNodeMath")
    ckf.operation = "MULTIPLY"
    L(ckm.outputs[0], ckf.inputs[0])
    L(gi.outputs["Chalk"], ckf.inputs[1])
    pale = N("ShaderNodeMix")                      # the paint's own colour, lifted and greyed
    pale.data_type = "RGBA"
    pale.inputs[0].default_value = 0.35
    L(gi.outputs["Colour"], pale.inputs[6])
    pale.inputs[7].default_value = (0.75, 0.72, 0.68, 1)
    ckc = N("ShaderNodeMix")
    ckc.data_type = "RGBA"
    L(ckf.outputs[0], ckc.inputs[0])
    L(dirt.outputs[2], ckc.inputs[6])
    L(pale.outputs[2], ckc.inputs[7])
    b = N("ShaderNodeBsdfPrincipled")
    L(ckc.outputs[2], b.inputs["Base Color"])
    rv = N("ShaderNodeMath")
    rv.operation = "MULTIPLY_ADD"
    L(amt.outputs[0], rv.inputs[0])
    rv.inputs[1].default_value = 0.8
    L(gi.outputs["Roughness"], rv.inputs[2])
    L(rv.outputs[0], b.inputs["Roughness"])
    b.inputs["Specular IOR Level"].default_value = 0.3 if CFG["sky_glossy"] else 0.5
    L(bump.outputs["Normal"], b.inputs["Normal"])
    L(b.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def glass_group():
    """Reflective tinted curtain-wall glass: a near-black dielectric whose IOR sets the coated
    reflectance (research: 3x less noise than transmission), optional thin-wall see-through for the
    rooms behind, and a small random tilt per pane so neighbouring panes reflect slightly different
    things."""
    ng, gi, go = group("Curtain Glass", [
        ("Tint", "NodeSocketColor", CFG["glass_tint"], None, None),          # body colour seen through the coating
        ("Reflectance", "NodeSocketFloat", CFG["glass_refl"], 0.02, 0.6),    # at normal incidence: 0.04 clear, 0.25 coated
        ("Roughness", "NodeSocketFloat", CFG["glass_rough"], 0.0, 0.3),
        ("See Through", "NodeSocketFloat", CFG["glass_see"], 0.0, 1.0),      # thin-wall transmission to the rooms
        ("Pane Wobble", "NodeSocketFloat", CFG["glass_wobble"], 0.0, 1.0),
    ], [("Shader", "NodeSocketShader")])
    N = ng.nodes.new
    L = ng.links.new
    # pane cell from the opening's own mullion grid (object attributes pane_x0, pane_z0, pane_pu, pane_pv)
    geo0 = N("ShaderNodeNewGeometry")
    sp = N("ShaderNodeSeparateXYZ")
    L(geo0.outputs["Position"], sp.inputs[0])
    cell = N("ShaderNodeCombineXYZ")
    for ax, key in (("X", "x"), ("Z", "z")):
        o = N("ShaderNodeAttribute")
        o.attribute_type = "OBJECT"
        o.attribute_name = f"pane_{key}0"
        pch = N("ShaderNodeAttribute")
        pch.attribute_type = "OBJECT"
        pch.attribute_name = "pane_pu" if key == "x" else "pane_pv"
        sub = N("ShaderNodeMath")
        sub.operation = "SUBTRACT"
        L(sp.outputs[ax], sub.inputs[0])
        L(o.outputs["Fac"], sub.inputs[1])
        dv = N("ShaderNodeMath")
        dv.operation = "DIVIDE"
        L(sub.outputs[0], dv.inputs[0])
        L(pch.outputs["Fac"], dv.inputs[1])
        fl = N("ShaderNodeMath")
        fl.operation = "FLOOR"
        L(dv.outputs[0], fl.inputs[0])
        L(fl.outputs[0], cell.inputs[ax])
    oi = N("ShaderNodeObjectInfo")
    L(oi.outputs["Random"], cell.inputs["Y"])
    wn = N("ShaderNodeTexWhiteNoise")
    wn.noise_dimensions = "3D"
    L(cell.outputs[0], wn.inputs["Vector"])
    sep = N("ShaderNodeSeparateColor")
    L(wn.outputs["Color"], sep.inputs[0])
    tilt = N("ShaderNodeCombineXYZ")
    for i, ax in enumerate(("X", "Z")):
        m = N("ShaderNodeMath")
        m.operation = "MULTIPLY_ADD"
        L(sep.outputs[i], m.inputs[0])
        m.inputs[1].default_value = 0.035           # +-1 degree at Pane Wobble 1
        m.inputs[2].default_value = -0.0175
        sc = N("ShaderNodeMath")
        sc.operation = "MULTIPLY"
        L(m.outputs[0], sc.inputs[0])
        L(gi.outputs["Pane Wobble"], sc.inputs[1])
        L(sc.outputs[0], tilt.inputs[ax])
    # reflectance per pane: 1 -+ spread (reference: most panes dark, a few catch bright sky)
    rv = N("ShaderNodeMath")
    rv.operation = "MULTIPLY_ADD"
    L(sep.outputs[2], rv.inputs[0])
    rv.inputs[1].default_value = 2 * CFG["glass_spread"]
    rv.inputs[2].default_value = 1 - CFG["glass_spread"]
    refl = N("ShaderNodeMath")
    refl.operation = "MULTIPLY"
    L(gi.outputs["Reflectance"], refl.inputs[0])
    L(rv.outputs[0], refl.inputs[1])
    geo = N("ShaderNodeNewGeometry")
    add = N("ShaderNodeVectorMath")
    add.operation = "ADD"
    L(geo.outputs["Normal"], add.inputs[0])
    L(tilt.outputs[0], add.inputs[1])
    nn = N("ShaderNodeVectorMath")
    nn.operation = "NORMALIZE"
    L(add.outputs[0], nn.inputs[0])
    # IOR from reflectance: n = (1 + sqrt R) / (1 - sqrt R)
    sq = N("ShaderNodeMath")
    sq.operation = "SQRT"
    L(refl.outputs[0], sq.inputs[0])
    num = N("ShaderNodeMath")
    num.operation = "ADD"
    num.inputs[0].default_value = 1.0
    L(sq.outputs[0], num.inputs[1])
    den = N("ShaderNodeMath")
    den.operation = "SUBTRACT"
    den.inputs[0].default_value = 1.0
    L(sq.outputs[0], den.inputs[1])
    ior = N("ShaderNodeMath")
    ior.operation = "DIVIDE"
    L(num.outputs[0], ior.inputs[0])
    L(den.outputs[0], ior.inputs[1])
    b = N("ShaderNodeBsdfPrincipled")
    L(gi.outputs["Tint"], b.inputs["Base Color"])
    L(gi.outputs["Roughness"], b.inputs["Roughness"])
    L(ior.outputs[0], b.inputs["IOR"])
    L(gi.outputs["See Through"], b.inputs["Transmission Weight"])
    b.inputs["Thin Wall"].default_value = True
    L(nn.outputs[0], b.inputs["Normal"])
    # shadow rays pass straight through (tinted), so the sun reaches the rooms behind
    tr = N("ShaderNodeBsdfTransparent")
    L(gi.outputs["Tint"], tr.inputs["Color"])
    lp = N("ShaderNodeLightPath")
    sh = N("ShaderNodeMixShader")
    L(lp.outputs["Is Shadow Ray"], sh.inputs[0])
    L(b.outputs[0], sh.inputs[1])
    L(tr.outputs[0], sh.inputs[2])
    L(sh.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def camera_from_spec(scene):
    D, h = CFG["cam_d"], CFG["cam_h"]
    W = CFG["res_x"]
    f_px = CFG["ppm"] * D
    bpy.ops.object.camera_add(location=(CFG["cam_x"], -D, h))
    cam = bpy.context.active_object
    cam.rotation_euler = (math.pi / 2, 0, 0)
    cd = cam.data
    cd.sensor_fit = "HORIZONTAL"
    cd.sensor_width = 36.0
    cd.lens = 36.0 * f_px / W
    u_axis = CFG["axis"] + CFG["cam_x"] * CFG["ppm"]           # where the optical axis meets the facade, in px
    v_h = CFG["ground"] - h * CFG["ppm"]
    cd.shift_x = (W / 2 - u_axis) / W                 # + moves the frame right, the content left
    cd.shift_y = (v_h - CFG["res_y"] / 2) / W
    cd.clip_end = 5000
    scene.camera = cam
    return cam


