"""Library materials: cd_diffraction and tinted_plastic, one control node each.

    tools/blender.sh library/materials/build_materials.py     # rewrites the two .blend files here

Experiments import the builders:  sys.path.insert(0, str(LIBRARY / "materials"))
                                  from build_materials import disc_group, case_group, DEFAULTS, IMPERFECTIONS

cd_diffraction: a diffraction grating as a real BSDF. Each spectral band is an anisotropic
Glossy lobe whose normal is tilted about the groove tangent by alpha = 1/2 asin(m lambda / d),
so every light diffracts. Orders m = +-1, +-2; 8 bands 400-700 nm.
  - The tracks circle the OBJECT ORIGIN in its XY plane: put the origin at the disc centre.
  - It only shows colour if its mirror direction sees dark with small lights beside it; in a
    white room it reads white. See knowledge/decisions/wonder-minidisc.md for the studio.
tinted_plastic: transmissive polycarbonate whose colour comes from volume absorption, set from
a target colour at a reference thickness (scene in metres). Link its Volume output too.
"""
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from nodes import auto_layout, group, material_from_group, math as m_  # noqa: E402

HERE = Path(__file__).resolve().parent
TEXTURES = HERE.parent / "textures" / "imperfections"
IMPERFECTIONS = {
    "scratches": TEXTURES / "scratches005_mask.jpg",
    "fingerprints": TEXTURES / "fingerprints002_mask.jpg",
    "dust": TEXTURES / "surface_imperfections015_mask.jpg",
}
# Final wonder-minidisc values: the library defaults.
DEFAULTS = {
    "spectrum": 1.0, "saturation": 1.0, "pitch_um": 1.6, "spread": 0.08, "aniso": 0.3,
    "mirror": 0.35, "mirror_tint": (1.0, 0.72, 0.82, 1.0), "clear_hub_mm": 4.2, "order2": 0.15,
    "case_colour": (0.30, 0.85, 0.78, 1.0), "colour_depth_mm": 3.0, "clarity": 1.0, "frost": 0.02,
    "scratches": 0.08, "fingerprints": 0.08, "dust": 0.2, "shadow_light": 0.9, "imperf_scale": 6.0,
}

BANDS = [400 + i * 300 / 7 for i in range(8)]  # nm
ORDERS = (1, 2)  # diffraction orders; order 2 strength is the "Second Order" input


def _zucconi6(lam):
    """Alan Zucconi's spectral_zucconi6: wavelength (nm) -> linear-ish RGB."""
    x = min(max((lam - 400) / 300, 0), 1)
    c1, x1, y1 = (3.54585104, 2.93225262, 2.41593945), (0.69549072, 0.49228336, 0.27699880), (0.02312639, 0.15225084, 0.52607955)
    c2, x2, y2 = (3.90307140, 3.21182957, 3.96587128), (0.11748627, 0.86755042, 0.66077860), (0.84897130, 0.88445281, 0.73949448)
    def bump(c, x0, y0):
        return max(1 - (c * (x - x0)) ** 2 - y0, 0)
    return [bump(c1[i], x1[i], y1[i]) + bump(c2[i], x2[i], y2[i]) for i in range(3)]


def band_colours():
    """Band RGBs scaled so the bands of one order sum to white."""
    cols = [_zucconi6(l) for l in BANDS]
    tot = [sum(c[i] for c in cols) for i in range(3)]
    return [tuple(c[i] / tot[i] for i in range(3)) + (1.0,) for c in cols]


def _glossy(nt):
    for idname in ("ShaderNodeBsdfAnisotropic", "ShaderNodeBsdfGlossy"):  # 4.4 name, then 5.x
        try:
            n = nt.nodes.new(idname)
            n.distribution = "GGX"
            return n
        except RuntimeError:
            continue
    raise RuntimeError("no Glossy BSDF node")


def _mix_rgb(nt, blend, fac, a, b):
    n = nt.nodes.new("ShaderNodeMix")
    n.data_type, n.blend_type, n.clamp_factor = "RGBA", blend, False
    for sock, v in ((n.inputs[0], fac), (n.inputs[6], a), (n.inputs[7], b)):
        if hasattr(v, "bl_rna"):
            nt.links.new(v, sock)
        else:
            sock.default_value = v
    return n.outputs[2]


def _add(nt, a, b):
    n = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(a, n.inputs[0]); nt.links.new(b, n.inputs[1])
    return n.outputs[0]


def _vt(nt, vec, kind, frm, to):
    n = nt.nodes.new("ShaderNodeVectorTransform")
    n.vector_type, n.convert_from, n.convert_to = kind, frm, to
    nt.links.new(vec, n.inputs[0])
    return n.outputs[0]


def disc_group(P, name="Disc"):
    ng, gi, go = group(name, [
        ("Spectrum", "NodeSocketFloat", P["spectrum"], 0.0, 3.0),          # strength of the rainbow lobes
        ("Saturation", "NodeSocketFloat", P["saturation"], 0.0, 1.0),      # 1 = CD, ~0.35 = pastel foil
        ("Track Pitch um", "NodeSocketFloat", P["pitch_um"], 0.8, 4.0),    # smaller = colours fan wider
        ("Spread", "NodeSocketFloat", P["spread"], 0.01, 0.5),             # lobe roughness; higher = softer, pastel
        ("Streak", "NodeSocketFloat", P["aniso"], -1.0, 1.0),              # anisotropy along the tracks
        ("Mirror", "NodeSocketFloat", P["mirror"], 0.0, 1.0),              # plain mirror between the colours
        ("Mirror Tint", "NodeSocketColor", P["mirror_tint"], None, None),  # colour of the reflective layer; tints every order (pink = recordable MD)
        ("Clear Hub mm", "NodeSocketFloat", P["clear_hub_mm"], 0.0, 20.0), # clear polycarbonate radius round the hub
        ("Second Order", "NodeSocketFloat", P["order2"], 0.0, 1.0),        # outer colour bands; they also pick up the table
    ], [("Shader", "NodeSocketShader")])
    nt = ng
    N = nt.nodes
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sep.inputs[0])
    flat = N.new("ShaderNodeCombineXYZ")
    nt.links.new(sep.outputs[0], flat.inputs[0]); nt.links.new(sep.outputs[1], flat.inputs[1])
    nrm = N.new("ShaderNodeVectorMath"); nrm.operation = "NORMALIZE"
    nt.links.new(flat.outputs[0], nrm.inputs[0])
    tan = N.new("ShaderNodeVectorMath"); tan.operation = "CROSS_PRODUCT"
    tan.inputs[0].default_value = (0, 0, 1)
    nt.links.new(nrm.outputs[0], tan.inputs[1])
    T_obj = tan.outputs[0]
    T_world = _vt(nt, T_obj, "VECTOR", "OBJECT", "WORLD")
    geo = N.new("ShaderNodeNewGeometry")
    N_obj = _vt(nt, geo.outputs["Normal"], "NORMAL", "WORLD", "OBJECT")

    grey = (1 / 8, 1 / 8, 1 / 8, 1.0)
    stack = None
    for order in ORDERS:
        weight = 1.0 if order == 1 else gi.outputs["Second Order"]
        for lam, col in zip(BANDS, band_colours()):
            # alpha = 0.5 * asin(m * lambda / d); lambda in nm, d in um
            ratio = m_(nt, "DIVIDE", order * lam / 1000.0, gi.outputs["Track Pitch um"])
            alive = m_(nt, "LESS_THAN", ratio, 0.999)               # evanescent orders vanish
            alpha = m_(nt, "MULTIPLY", m_(nt, "ARCSINE", m_(nt, "MINIMUM", ratio, 0.999)), 0.5)
            c = _mix_rgb(nt, "MIX", gi.outputs["Saturation"], grey, col)
            amp = m_(nt, "MULTIPLY", m_(nt, "MULTIPLY", gi.outputs["Spectrum"], weight), alive)
            c = _mix_rgb(nt, "MULTIPLY", 1.0, c, _gray_socket(nt, amp))
            c = _mix_rgb(nt, "MULTIPLY", 1.0, c, gi.outputs["Mirror Tint"])
            for sign in (1, -1):
                ang = m_(nt, "MULTIPLY", alpha, sign)
                rot = N.new("ShaderNodeVectorRotate"); rot.rotation_type = "AXIS_ANGLE"
                nt.links.new(N_obj, rot.inputs["Vector"])
                nt.links.new(T_obj, rot.inputs["Axis"])
                nt.links.new(ang, rot.inputs["Angle"])
                g = _glossy(nt)
                nt.links.new(c, g.inputs["Color"])
                nt.links.new(gi.outputs["Spread"], g.inputs["Roughness"])
                nt.links.new(gi.outputs["Streak"], g.inputs["Anisotropy"])
                nt.links.new(T_world, g.inputs["Tangent"])
                nt.links.new(_vt(nt, rot.outputs[0], "NORMAL", "OBJECT", "WORLD"), g.inputs["Normal"])
                stack = g.outputs[0] if stack is None else _add(nt, stack, g.outputs[0])

    base = _glossy(nt)  # order 0: the plain mirror
    nt.links.new(_mix_rgb(nt, "MULTIPLY", 1.0, gi.outputs["Mirror Tint"], _gray_socket(nt, gi.outputs["Mirror"])), base.inputs["Color"])
    base.inputs["Roughness"].default_value = 0.04
    nt.links.new(gi.outputs["Streak"], base.inputs["Anisotropy"])
    nt.links.new(T_world, base.inputs["Tangent"])
    stack = _add(nt, stack, base.outputs[0])

    # 1.2 mm polycarbonate over the data layer
    coat = _glossy(nt); coat.inputs["Color"].default_value = (1, 1, 1, 1); coat.inputs["Roughness"].default_value = 0.015
    fr = N.new("ShaderNodeFresnel"); fr.inputs["IOR"].default_value = 1.58
    mix = N.new("ShaderNodeMixShader")
    nt.links.new(fr.outputs[0], mix.inputs[0]); nt.links.new(stack, mix.inputs[1]); nt.links.new(coat.outputs[0], mix.inputs[2])

    # clear hub zone: plain polycarbonate
    glass = N.new("ShaderNodeBsdfGlass"); glass.inputs["IOR"].default_value = 1.58
    glass.inputs["Roughness"].default_value = 0.02; glass.inputs["Color"].default_value = (1, 1, 1, 1)
    rlen = N.new("ShaderNodeVectorMath"); rlen.operation = "LENGTH"; nt.links.new(flat.outputs[0], rlen.inputs[0])
    in_hub = m_(nt, "LESS_THAN", rlen.outputs["Value"], m_(nt, "MULTIPLY", gi.outputs["Clear Hub mm"], 0.001))
    hubmix = N.new("ShaderNodeMixShader")
    nt.links.new(in_hub, hubmix.inputs[0]); nt.links.new(mix.outputs[0], hubmix.inputs[1]); nt.links.new(glass.outputs[0], hubmix.inputs[2])
    nt.links.new(hubmix.outputs[0], go.inputs["Shader"])
    auto_layout(nt)
    return ng


def _gray_socket(nt, value):
    """A float socket as an RGB socket (all channels equal)."""
    c = nt.nodes.new("ShaderNodeCombineColor")
    for i in range(3):
        nt.links.new(value, c.inputs[i])
    return c.outputs[0]


def _image(nt, path, vec, noncolor=True):
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = bpy.data.images.load(str(path), check_existing=True)
    if noncolor:
        n.image.colorspace_settings.name = "Non-Color"
    n.projection = "BOX"
    n.projection_blend = 0.2
    nt.links.new(vec, n.inputs["Vector"])
    return n.outputs["Color"]


def case_group(P, imperf=None, name="Case Plastic"):
    imperf = imperf or IMPERFECTIONS
    ng, gi, go = group(name, [
        ("Colour", "NodeSocketColor", P["case_colour"], None, None),          # colour seen through one wall
        ("Colour Depth mm", "NodeSocketFloat", P["colour_depth_mm"], 0.1, 20.0),  # wall thickness that shows exactly Colour
        ("Clarity", "NodeSocketFloat", P["clarity"], 0.0, 1.0),               # 1 = clear, 0 = opaque plastic
        ("Frost", "NodeSocketFloat", P["frost"], 0.0, 0.5),                   # surface roughness
        ("Scratches", "NodeSocketFloat", P["scratches"], 0.0, 1.0),
        ("Fingerprints", "NodeSocketFloat", P["fingerprints"], 0.0, 1.0),
        ("Dust", "NodeSocketFloat", P["dust"], 0.0, 1.0),
        ("Shadow Light", "NodeSocketFloat", P["shadow_light"], 0.0, 1.0),     # light let through into the cast shadow
    ], [("Shader", "NodeSocketShader"), ("Volume", "NodeSocketShader")])
    nt = ng
    N = nt.nodes
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (P["imperf_scale"],) * 3
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    v = mp.outputs[0]
    scr = _image(nt, imperf["scratches"], v)
    fin = _image(nt, imperf["fingerprints"], v)
    dst = _image(nt, imperf["dust"], v)
    to_f = lambda s: m_(nt, "ADD", s, 0.0)  # colour -> float via implicit convert
    bsdf = N.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["IOR"].default_value = 1.585
    # Wear must not touch this roughness: it also blurs transmission, which hazes the disc.
    nt.links.new(gi.outputs["Frost"], bsdf.inputs["Roughness"])
    nt.links.new(gi.outputs["Clarity"], bsdf.inputs["Transmission Weight"])
    # opaque end: the colour itself; clear end: white surface, colour from the volume
    nt.links.new(_mix_rgb(nt, "MIX", gi.outputs["Clarity"], gi.outputs["Colour"], (1, 1, 1, 1)), bsdf.inputs["Base Color"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Distance"].default_value = 0.00002
    nt.links.new(m_(nt, "MULTIPLY", to_f(scr), gi.outputs["Scratches"]), bump.inputs["Height"])
    bump.inputs["Strength"].default_value = 0.15
    nt.links.new(bump.outputs[0], bsdf.inputs["Normal"])

    # scratches and fingerprints: a thin rough reflection over the clean plastic, by mask
    wear = m_(nt, "ADD", m_(nt, "MULTIPLY", m_(nt, "MULTIPLY", to_f(scr), gi.outputs["Scratches"]), 0.5),
              m_(nt, "MULTIPLY", m_(nt, "MULTIPLY", to_f(fin), gi.outputs["Fingerprints"]), 0.3))
    haze = _glossy(nt); haze.inputs["Color"].default_value = (1, 1, 1, 1); haze.inputs["Roughness"].default_value = 0.35
    wmix = N.new("ShaderNodeMixShader")
    nt.links.new(m_(nt, "MINIMUM", wear, 1.0), wmix.inputs[0]); nt.links.new(bsdf.outputs[0], wmix.inputs[1]); nt.links.new(haze.outputs[0], wmix.inputs[2])

    # dust occludes: a dark diffuse mixed in by a sparse mask
    # only the map's strongest specks: a sparse sprinkle, not a film
    dmask = m_(nt, "MULTIPLY", m_(nt, "MULTIPLY", m_(nt, "SUBTRACT", to_f(dst), 0.6), 5.0, clamp=True),
               gi.outputs["Dust"], clamp=True)
    dif = N.new("ShaderNodeBsdfDiffuse"); dif.inputs["Color"].default_value = (0.25, 0.24, 0.23, 1)
    dmix = N.new("ShaderNodeMixShader")
    nt.links.new(dmask, dmix.inputs[0]); nt.links.new(wmix.outputs[0], dmix.inputs[1]); nt.links.new(dif.outputs[0], dmix.inputs[2])

    # shadow rays pass straight through; the volume still tints them
    lp = N.new("ShaderNodeLightPath")
    tr = N.new("ShaderNodeBsdfTransparent")
    smix = N.new("ShaderNodeMixShader")
    nt.links.new(m_(nt, "MULTIPLY", m_(nt, "MULTIPLY", lp.outputs["Is Shadow Ray"], gi.outputs["Shadow Light"]), gi.outputs["Clarity"]), smix.inputs[0])
    nt.links.new(dmix.outputs[0], smix.inputs[1]); nt.links.new(tr.outputs[0], smix.inputs[2])
    nt.links.new(smix.outputs[0], go.inputs["Shader"])

    # Beer-Lambert: k = -ln(C); density = max(k)/depth; absorption colour = 1 - k/max(k)
    sc = N.new("ShaderNodeSeparateColor"); nt.links.new(gi.outputs["Colour"], sc.inputs[0])
    k = [m_(nt, "MULTIPLY", m_(nt, "LOGARITHM", m_(nt, "MAXIMUM", sc.outputs[i], 0.001), math.e), -1.0) for i in range(3)]
    kmax = m_(nt, "MAXIMUM", m_(nt, "MAXIMUM", m_(nt, "MAXIMUM", k[0], k[1]), k[2]), 0.0001)
    cc = N.new("ShaderNodeCombineColor")
    for i in range(3):
        nt.links.new(m_(nt, "SUBTRACT", 1.0, m_(nt, "DIVIDE", k[i], kmax)), cc.inputs[i])
    dens = m_(nt, "DIVIDE", kmax, m_(nt, "MULTIPLY", gi.outputs["Colour Depth mm"], 0.001))
    va = N.new("ShaderNodeVolumeAbsorption")
    nt.links.new(cc.outputs[0], va.inputs["Color"])
    nt.links.new(m_(nt, "MULTIPLY", dens, gi.outputs["Clarity"]), va.inputs["Density"])
    nt.links.new(va.outputs[0], go.inputs["Volume"])
    auto_layout(nt)
    return ng


def steel_group(P):
    ng, gi, go = group("Hub Steel", [
        ("Colour", "NodeSocketColor", P["steel_colour"], None, None),
        ("Roughness", "NodeSocketFloat", P["steel_rough"], 0.0, 1.0),
    ], [("Shader", "NodeSocketShader")])
    N = ng.nodes
    b = N.new("ShaderNodeBsdfPrincipled")
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Anisotropic"].default_value = 0.6
    t = N.new("ShaderNodeTangent"); t.direction_type = "RADIAL"; t.axis = "Z"
    ng.links.new(t.outputs[0], b.inputs["Tangent"])
    ng.links.new(gi.outputs["Colour"], b.inputs["Base Color"])
    ng.links.new(gi.outputs["Roughness"], b.inputs["Roughness"])
    ng.links.new(b.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def sweep_group(P):
    ng, gi, go = group("Sweep", [
        ("Colour", "NodeSocketColor", P["sweep_colour"], None, None),
        ("Gloss", "NodeSocketFloat", P["sweep_gloss"], 0.0, 1.0),  # clearcoat strength: the table reflection
    ], [("Shader", "NodeSocketShader")])
    b = ng.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Roughness"].default_value = 0.6
    b.inputs["Coat Roughness"].default_value = P["sweep_coat_rough"]
    ng.links.new(gi.outputs["Colour"], b.inputs["Base Color"])
    ng.links.new(gi.outputs["Gloss"], b.inputs["Coat Weight"])
    ng.links.new(b.outputs[0], go.inputs["Shader"])
    auto_layout(ng)
    return ng


def save_library_material(mat, path):
    """Write a .blend holding just this material (and what it uses), paths relative."""
    bpy.data.libraries.write(str(path), {mat}, path_remap="RELATIVE_ALL", fake_user=True)
    print(f"[out] WROTE {path}")


if __name__ == "__main__":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    disc = material_from_group("cd_diffraction", disc_group(DEFAULTS, "CD Diffraction"))
    save_library_material(disc, HERE / "cd_diffraction.blend")
    case = material_from_group("tinted_plastic", case_group(DEFAULTS, None, "Tinted Plastic"))
    nt = case.node_tree
    g = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeGroup")
    nt.links.new(g.outputs["Volume"], nt.nodes["Material Output"].inputs["Volume"])
    case.cycles.homogeneous_volume = True
    save_library_material(case, HERE / "tinted_plastic.blend")
