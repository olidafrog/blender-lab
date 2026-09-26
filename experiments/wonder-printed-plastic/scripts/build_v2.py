"""Wonder logo reverse-printed inside a frosted acrylic slab (A5) — build + render. V2.

V2 applies leads from the Photoshop build of the same refs (knowledge/decisions/wonder-printed-plastic.md):
measured screen angles, a crisp FRONT plate for small type, ink density mottle, a 1-2 px fluoro rim,
and mostly light specks. build.py is the v29 original, kept for comparison.

Physical model (second-surface print):
  camera -> frosted front face (rough dielectric + micro-grain/weave bump + milky diffuse lobe)
         -> clear acrylic body (thickness = gap between diffuser and ink => blur radius)
         -> ink layer on the back face (artwork PNG, riso/toner ink grain) -> white flood backer.

Run:  blender -b -P scripts/build.py -- --out renders/v01.png --samples 256 --scale 0.5 [--save file.blend] [--set key=value]
Artwork: content/artwork.png (A5 148x210, transparent = no ink). Swap it in the ARTWORK image node.
"""
import bpy, bmesh, math, sys, os, argparse
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

P = dict(
    artwork=os.path.join(ROOT, "content", "artwork.png"),
    slab=(0.148, 0.015, 0.210),      # A5, 12 mm thick (x, thickness, height) metres
    edge_bevel=0.0005, edge_segs=6,
    slab_rot=(0.0, 0.0, 36.0),       # deg
    print_inset=0.013,              # ink plane distance from back face (m)
    # frosted front
    diffusion=0.08, halo=0.15, halo_spread=0.5, milk=0.13, coat=0.35, coat_rough=0.4, surf_speckle=0.5, ior=1.49, tint=(0.93, 0.955, 0.985),
    grain=0.5, grain_scale=2.5, weave=0.0, weave_pitch_mm=0.5, weave_angle=-40.0, rough_mottle=1.2,
    edge_rough=0.45,
    # ink
    ink_density=0.72, ink_grain=0.03, pinholes=0.3, edge_erosion=0.7, edge_scatter=1.0, toner_patch=0.06, ink_grain_scale=1.0, ragged=2.6, speckle=0.5, backer=(0.80, 0.82, 0.85), backer_mottle=0.02,
    artwork_front='', density_mottle=0.14, fluoro_rim=0.5, speck_light=0.92, front_density=0.95,
    fluoro=1.2, soft_copy=0.6, soft_radius_mm=1.8, pre_blur=0.7, pre_blur_mm=2.5, core_soften_mm=0.5, soft_offset=(0.0, 0.0),
    screen=0.4, screen_dip=0.12, toner_tone=0.1, screen_pitch_mm=0.34, screen_angle_k=63.4, screen_angle_c=-26.6, screen_jitter=0.25, tracking_dots=1.0,
    # stage
    bg=(0.11, 0.11, 0.11), world=0.15,
    cam_lens=90.0, cam_dist=0.72, cam_h=0.2, cam_target=(0.0, 0.0, 0.103), fstop=16.0,
    lights=[  # name, loc, target, size, power W, kelvin
        ("Key",    (-0.35, -0.65, 0.75), (0, 0, 0.1), (1.4, 1.4), 44.0, 6500),
        ("Graze",  (-0.50, -0.05, 0.40), (0, 0, 0.14), (0.12, 0.9), 45.0, 6500),
        ("Satin",  ( 0.70, -0.38, 0.42), (0, 0, 0.1), (0.25, 1.4), 0.6, 6800),   # placed by sheen_point (mirror of camera)
        ("Top",    ( 0.05,  0.10, 0.70), (0, 0, 0.1), (0.5, 0.3), 18.0, 6500),
        ("Rim",    ( 0.30,  0.45, 0.20), (0.07, 0, 0.1), (0.1, 0.6), 45.0, 6500),
        ("Bounce", (-0.15, -0.55, 0.02), (0, 0, 0.06), (0.6, 0.15), 14.0, 6500),
        ("Rim_L",  (-0.40,  0.30, 0.30), (-0.07, 0, 0.12), (0.08, 0.6), 35.0, 6500),
    ],
    flag=((-0.28, 0.14, 0.165), (0.7, 0.32)),
    glossy_only=("Satin", "Rim", "Rim_L"), sheen_point=(-0.1, 0.4), sheen_rot=80.0, sheen_dist=0.75,
    res=(1600, 2000), exposure=-0.75, look="AgX - High Contrast",
    comp=dict(denoise_mix=0.5, grain=0.08, vignette=0.12),
)

# ---------------------------------------------------------------- helpers
def wipe():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def look_at(ob, target):
    ob.rotation_euler = (Vector(target) - ob.location).to_track_quat('-Z', 'Y').to_euler()

def link(nt, a, b): nt.links.new(a, b)

def N(nt, t, loc=(0, 0), **inputs):
    n = nt.nodes.new(t); n.location = loc
    for k, v in inputs.items():
        if hasattr(v, "bl_rna"): nt.links.new(v, n.inputs[k])
        else: n.inputs[k].default_value = v
    return n

def math_(nt, op, a, b=None, loc=(0, 0), clamp=False):
    m = nt.nodes.new("ShaderNodeMath"); m.operation = op; m.location = loc; m.use_clamp = clamp
    for i, v in enumerate((a, b)):
        if v is None: continue
        if hasattr(v, "bl_rna"): nt.links.new(v, m.inputs[i])
        else: m.inputs[i].default_value = v
    return m.outputs[0]

def sock(ng, name, kind, default=None, lo=None, hi=None, out=False, desc=""):
    s = ng.interface.new_socket(name, in_out='OUTPUT' if out else 'INPUT', socket_type=kind)
    if default is not None: s.default_value = default
    if lo is not None: s.min_value = lo
    if hi is not None: s.max_value = hi
    if desc: s.description = desc
    return s

def mix_col(nt, fac, a, b, blend='MIX', loc=(0, 0)):
    m = nt.nodes.new("ShaderNodeMix"); m.data_type = 'RGBA'; m.blend_type = blend; m.location = loc
    for i, v in ((0, fac), (6, a), (7, b)):
        if hasattr(v, "bl_rna"): nt.links.new(v, m.inputs[i])
        else: m.inputs[i].default_value = v
    return m.outputs[2]

# ---------------------------------------------------------------- node groups (the tweakable controls)
def group_frosted():
    """Frosted acrylic face. Inputs are the look's main dials."""
    ng = bpy.data.node_groups.new("Frosted Acrylic", 'ShaderNodeTree')
    sock(ng, "Diffusion", 'NodeSocketFloat', P["diffusion"], 0, 1, desc="Surface roughness: how blurred the print looks through the plastic")
    sock(ng, "Halo", 'NodeSocketFloat', P["halo"], 0, 1, desc="Share of light in the wide-angle lobe: soft glow around the sharp core")
    sock(ng, "Halo Spread", 'NodeSocketFloat', P["halo_spread"], 0, 1, desc="Roughness of the wide lobe")
    sock(ng, "Satin Coat", 'NodeSocketFloat', P["coat"], 0, 1, desc="Thin satin top-coat: a defined soft highlight")
    sock(ng, "Coat Roughness", 'NodeSocketFloat', P["coat_rough"], 0, 1)
    sock(ng, "Milk", 'NodeSocketFloat', P["milk"], 0, 1, desc="Share of light fully scattered: lifts blacks, flattens contrast")
    sock(ng, "Tint", 'NodeSocketColor', (*P["tint"], 1))
    sock(ng, "IOR", 'NodeSocketFloat', P["ior"], 1, 2)
    sock(ng, "Surface Grain", 'NodeSocketFloat', P["grain"], 0, 2, desc="Fine sandblast grain on top")
    sock(ng, "Grain Scale", 'NodeSocketFloat', P["grain_scale"], 0.1, 10)
    sock(ng, "Weave", 'NodeSocketFloat', P["weave"], 0, 2, desc="Fine embossed diagonal line texture")
    sock(ng, "Weave Pitch mm", 'NodeSocketFloat', P["weave_pitch_mm"], 0.05, 3)
    sock(ng, "Weave Angle", 'NodeSocketFloat', P["weave_angle"], -90, 90)
    sock(ng, "Roughness Mottle", 'NodeSocketFloat', P["rough_mottle"], 0, 1, desc="Uneven frosting across the face")
    sock(ng, "Surface Speckle", 'NodeSocketFloat', P["surf_speckle"], 0, 1, desc="Crisp dust/toner specks sitting on top of the plastic")
    sock(ng, "BSDF", 'NodeSocketShader', out=True)
    nt = ng; gi = N(nt, "NodeGroupInput", (-1400, 0)); go = N(nt, "NodeGroupOutput", (1100, 0))
    tc = N(nt, "ShaderNodeTexCoord", (-1400, 400))
    obj = tc.outputs["Object"]  # metres; slab front lies in local XZ
    # sandblast grain: two octaves of fine noise, feature ~0.25 mm at scale 1
    gs = math_(nt, 'DIVIDE', 3500.0, gi.outputs["Grain Scale"], (-1200, 500))
    n1 = N(nt, "ShaderNodeTexNoise", (-1000, 500), Vector=obj, Scale=gs, Detail=3.0, Roughness=0.7)
    wn = N(nt, "ShaderNodeTexWhiteNoise", (-1000, 300), Vector=math_vec_scale(nt, obj, gs, 2.2, (-1200, 300)))
    wn.noise_dimensions = '3D'
    grain_h = math_(nt, 'ADD', math_(nt, 'MULTIPLY', n1.outputs["Fac"], 1.0, (-800, 500)),
                    math_(nt, 'MULTIPLY', wn.outputs["Value"], 0.0, (-800, 350)), (-600, 450))
    grain_h = math_(nt, 'MULTIPLY', grain_h, gi.outputs["Surface Grain"], (-400, 450))
    # weave: diagonal sine ridges in the face plane, pitch in mm, broken up by noise
    sep = N(nt, "ShaderNodeSeparateXYZ", (-1200, 100), Vector=obj)
    ang = math_(nt, 'RADIANS', gi.outputs["Weave Angle"], None, (-1200, -100))
    u = math_(nt, 'ADD', math_(nt, 'MULTIPLY', sep.outputs["X"], math_(nt, 'COSINE', ang, None, (-1050, -100)), (-900, 100)),
              math_(nt, 'MULTIPLY', sep.outputs["Z"], math_(nt, 'SINE', ang, None, (-1050, -200)), (-900, -50)), (-750, 50))
    pitch = math_(nt, 'MULTIPLY', gi.outputs["Weave Pitch mm"], 0.001, (-900, -250))
    wobble = N(nt, "ShaderNodeTexNoise", (-900, -400), Vector=obj, Scale=300.0, Detail=2.0)
    u = math_(nt, 'ADD', u, math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', wobble.outputs["Fac"], 0.5, (-750, -400)), 0.0004, (-600, -400)), (-600, 50))
    ph = math_(nt, 'MULTIPLY', math_(nt, 'DIVIDE', u, pitch, (-450, 50)), 2 * math.pi, (-300, 50))
    ridge = math_(nt, 'MULTIPLY', math_(nt, 'ADD', math_(nt, 'SINE', ph, None, (-150, 50)), 1.0, (0, 50)), 0.5, (150, 50))
    wv_mask = N(nt, "ShaderNodeTexNoise", (-150, -200), Vector=obj, Scale=40.0, Detail=1.0)
    ridge = math_(nt, 'MULTIPLY', ridge, math_(nt, 'ADD', wv_mask.outputs["Fac"], 0.25, (0, -200)), (300, 50))
    weave_h = math_(nt, 'MULTIPLY', ridge, gi.outputs["Weave"], (450, 50))
    height = math_(nt, 'ADD', grain_h, weave_h, (600, 250))
    bump = N(nt, "ShaderNodeBump", (700, 250), Height=height, Strength=1.0, Distance=0.00001)
    # roughness mottle
    mot = N(nt, "ShaderNodeTexNoise", (-400, -600), Vector=obj, Scale=500.0, Detail=4.0)
    mfac = math_(nt, 'ADD', 1.0, math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', mot.outputs["Fac"], 0.5, (-250, -600)),
                                       math_(nt, 'MULTIPLY', gi.outputs["Roughness Mottle"], 1.2, (-250, -750)), (-100, -650)), (50, -650))
    rough = math_(nt, 'MULTIPLY', gi.outputs["Diffusion"], mfac, (200, -600), clamp=True)
    # albedo grain: +-4% speckle on the tint so grain covers blank areas too
    tg = math_(nt, 'ADD', 0.96, math_(nt, 'MULTIPLY', wn.outputs["Value"], math_(nt, 'MULTIPLY', gi.outputs["Surface Grain"], 0.12, (100, 700)), (250, 700)), (400, 700))
    tint = mix_col(nt, 1.0, gi.outputs["Tint"], tg, 'MULTIPLY', (550, 700))
    blot = N(nt, "ShaderNodeTexNoise", (400, 900), Vector=obj, Scale=9.0, Detail=4.0, Roughness=0.6)
    bl = math_(nt, 'ADD', 0.85, math_(nt, 'MULTIPLY', blot.outputs["Fac"], 0.3, (550, 900)), (700, 900))
    tint = mix_col(nt, 1.0, tint, bl, 'MULTIPLY', (700, 750))
    def lobe(r, y):
        pb = N(nt, "ShaderNodeBsdfPrincipled", (500, y))
        link(nt, tint, pb.inputs["Base Color"]); link(nt, r, pb.inputs["Roughness"])
        link(nt, gi.outputs["IOR"], pb.inputs["IOR"]); pb.inputs["Transmission Weight"].default_value = 1.0
        link(nt, bump.outputs["Normal"], pb.inputs["Normal"])
        link(nt, gi.outputs["Satin Coat"], pb.inputs["Coat Weight"]); link(nt, math_(nt, 'MULTIPLY', gi.outputs["Coat Roughness"], mfac, (350, -350), clamp=True), pb.inputs["Coat Roughness"])
        link(nt, bump.outputs["Normal"], pb.inputs["Coat Normal"]); return pb
    core = lobe(rough, -200)
    # wide lobe is refraction-only: forward scatter through the frosting, no broad reflective veil
    wide = N(nt, "ShaderNodeBsdfRefraction", (500, -900)); wide.distribution = 'GGX'
    link(nt, tint, wide.inputs["Color"]); link(nt, gi.outputs["IOR"], wide.inputs["IOR"])
    link(nt, math_(nt, 'MULTIPLY', gi.outputs["Halo Spread"], mfac, (200, -900), clamp=True), wide.inputs["Roughness"])
    link(nt, bump.outputs["Normal"], wide.inputs["Normal"])
    lm = N(nt, "ShaderNodeMixShader", (700, -500)); link(nt, gi.outputs["Halo"], lm.inputs[0])
    link(nt, core.outputs[0], lm.inputs[1]); link(nt, wide.outputs[0], lm.inputs[2])
    class _P: outputs = [lm.outputs[0]]
    pb = _P
    tl = N(nt, "ShaderNodeBsdfTranslucent", (500, -500)); link(nt, tint, tl.inputs["Color"])
    link(nt, bump.outputs["Normal"], tl.inputs["Normal"])
    mx = N(nt, "ShaderNodeMixShader", (750, -200)); link(nt, gi.outputs["Milk"], mx.inputs[0])
    link(nt, pb.outputs[0], mx.inputs[1]); link(nt, tl.outputs[0], mx.inputs[2])
    # specks: sparse voronoi dots (~0.1-0.2 mm), mix of dark toner and pale dust
    vo = N(nt, "ShaderNodeTexVoronoi", (500, -1200), Vector=obj, Scale=700.0); vo.voronoi_dimensions = '3D'
    sp = N(nt, "ShaderNodeSeparateColor", (650, -1300)); link(nt, vo.outputs["Color"], sp.inputs[0])
    sthr = math_(nt, 'ADD', 0.06, math_(nt, 'MULTIPLY', sp.outputs["Blue"], 0.16, (500, -1500)), (550, -1500))
    clus = N(nt, "ShaderNodeTexNoise", (400, -1650), Vector=obj, Scale=12.0, Detail=3.0)
    cm = math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', clus.outputs["Fac"], 0.35, (550, -1650)), 5.0, (650, -1650), clamp=True)
    dotm = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', math_(nt, 'LESS_THAN', vo.outputs["Distance"], sthr, (650, -1150)), cm, (700, -1250)),
                 math_(nt, 'GREATER_THAN', sp.outputs["Red"], 0.75, (800, -1300)), (800, -1150))
    dotm = math_(nt, 'MULTIPLY', dotm, math_(nt, 'MULTIPLY', gi.outputs["Surface Speckle"], 0.7, (950, -1050)), (950, -1150))
    spc = mix_col(nt, math_(nt, 'GREATER_THAN', sp.outputs["Green"], 0.55, (800, -1450)), (0.18, 0.18, 0.2, 1), (0.35, 0.35, 0.37, 1), "MIX", (950, -1400))
    df = N(nt, "ShaderNodeBsdfTransparent", (1000, -1300)); link(nt, spc, df.inputs["Color"])
    mxs = N(nt, "ShaderNodeMixShader", (1000, -300)); link(nt, dotm, mxs.inputs[0])
    link(nt, mx.outputs[0], mxs.inputs[1]); link(nt, df.outputs[0], mxs.inputs[2])
    link(nt, mxs.outputs[0], go.inputs["BSDF"])
    return ng

def math_vec_scale(nt, vec, s, extra, loc):
    m = nt.nodes.new("ShaderNodeVectorMath"); m.operation = 'SCALE'; m.location = loc
    link(nt, vec, m.inputs[0])
    sc = math_(nt, 'MULTIPLY', s, extra, (loc[0]-150, loc[1]-80))
    link(nt, sc, m.inputs["Scale"])
    return m.outputs[0]

def group_ink_misprint():
    """Distorts artwork UVs: ragged ink edges + registration offset."""
    ng = bpy.data.node_groups.new("Ink Misprint UV", 'ShaderNodeTree')
    sock(ng, "Vector", 'NodeSocketVector')
    sock(ng, "Ragged Edges", 'NodeSocketFloat', P["ragged"], 0, 3, desc="Wobbly, bled ink edges")
    sock(ng, "Offset X mm", 'NodeSocketFloat', 0.0, -5, 5, desc="Registration shift")
    sock(ng, "Offset Y mm", 'NodeSocketFloat', 0.0, -5, 5)
    sock(ng, "Vector", 'NodeSocketVector', out=True)
    nt = ng; gi = N(nt, "NodeGroupInput", (-800, 0)); go = N(nt, "NodeGroupOutput", (600, 0))
    nz = N(nt, "ShaderNodeTexNoise", (-500, -150), Vector=gi.outputs["Vector"], Scale=140.0, Detail=4.0, Roughness=0.65)
    nz.noise_dimensions = '2D'
    cen = N(nt, "ShaderNodeVectorMath", (-250, -150)); cen.operation = 'SUBTRACT'
    link(nt, nz.outputs["Color"], cen.inputs[0]); cen.inputs[1].default_value = (0.5, 0.5, 0.5)
    amt = math_(nt, 'MULTIPLY', gi.outputs["Ragged Edges"], 0.0012, (-250, -350))
    sc = N(nt, "ShaderNodeVectorMath", (0, -150)); sc.operation = 'SCALE'
    link(nt, cen.outputs[0], sc.inputs[0]); link(nt, amt, sc.inputs["Scale"])
    off = N(nt, "ShaderNodeCombineXYZ", (0, 150))
    link(nt, math_(nt, 'DIVIDE', gi.outputs["Offset X mm"], 148.0, (-250, 250)), off.inputs["X"])
    link(nt, math_(nt, 'DIVIDE', gi.outputs["Offset Y mm"], 210.0, (-250, 100)), off.inputs["Y"])
    a1 = N(nt, "ShaderNodeVectorMath", (250, 0)); a1.operation = 'ADD'
    link(nt, gi.outputs["Vector"], a1.inputs[0]); link(nt, sc.outputs[0], a1.inputs[1])
    a2 = N(nt, "ShaderNodeVectorMath", (420, 0)); a2.operation = 'ADD'
    link(nt, a1.outputs[0], a2.inputs[0]); link(nt, off.outputs[0], a2.inputs[1])
    link(nt, a2.outputs[0], go.inputs["Vector"])
    return ng

def group_soft_copy(img):
    """Blurred copy of the artwork (16 jittered taps on two rings) — the digital pre-blur layer
    the reference designers put under the crisp print. Reads the same ARTWORK image."""
    ng = bpy.data.node_groups.new("Soft Copy (blur)", 'ShaderNodeTree')
    sock(ng, "Vector", 'NodeSocketVector')
    sock(ng, "Radius mm", 'NodeSocketFloat', P["soft_radius_mm"], 0, 20, desc="Blur radius of the soft copy")
    sock(ng, "Offset X mm", 'NodeSocketFloat', P["soft_offset"][0], -10, 10, desc="Shift of the soft copy: reads as depth / shadow")
    sock(ng, "Offset Y mm", 'NodeSocketFloat', P["soft_offset"][1], -10, 10)
    sock(ng, "Color", 'NodeSocketColor', out=True); sock(ng, "Alpha", 'NodeSocketFloat', out=True)
    nt = ng; gi = N(nt, "NodeGroupInput", (-1200, 0)); go = N(nt, "NodeGroupOutput", (1600, 0))
    wn = N(nt, "ShaderNodeTexWhiteNoise", (-1000, 300)); wn.noise_dimensions = '2D'
    sv = N(nt, "ShaderNodeVectorMath", (-1100, 300)); sv.operation = 'SCALE'; link(nt, gi.outputs["Vector"], sv.inputs[0]); sv.inputs["Scale"].default_value = 4000.0
    link(nt, sv.outputs[0], wn.inputs["Vector"])
    jit = math_(nt, 'MULTIPLY', wn.outputs["Value"], 2 * math.pi, (-850, 300))
    rx = math_(nt, 'DIVIDE', gi.outputs["Radius mm"], 148.0, (-850, 100)); ry = math_(nt, 'DIVIDE', gi.outputs["Radius mm"], 210.0, (-850, -50))
    oc = N(nt, "ShaderNodeCombineXYZ", (-850, -250))
    link(nt, math_(nt, 'DIVIDE', gi.outputs["Offset X mm"], -148.0, (-1000, -250)), oc.inputs["X"])
    link(nt, math_(nt, 'DIVIDE', gi.outputs["Offset Y mm"], -210.0, (-1000, -400)), oc.inputs["Y"])
    bu = N(nt, "ShaderNodeVectorMath", (-700, -250)); bu.operation = 'ADD'; link(nt, gi.outputs["Vector"], bu.inputs[0]); link(nt, oc.outputs[0], bu.inputs[1])
    base_uv = bu.outputs[0]
    acc_c = None; acc_a = None; n = 0; y = 600
    for ring, rr in ((0, 0.33), (1, 0.66), (0, 1.0)):
        for k in range(8):
            a = math_(nt, 'ADD', jit, (k + 0.5 * ring) * math.pi / 4, (-650, y))
            ox = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', math_(nt, 'COSINE', a, None, (-500, y)), rx, (-350, y)), rr, (-200, y))
            oy = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', math_(nt, 'SINE', a, None, (-500, y - 60)), ry, (-350, y - 60)), rr, (-200, y - 60))
            cv = N(nt, "ShaderNodeCombineXYZ", (-50, y)); link(nt, ox, cv.inputs["X"]); link(nt, oy, cv.inputs["Y"])
            ad = N(nt, "ShaderNodeVectorMath", (100, y)); ad.operation = 'ADD'; link(nt, base_uv, ad.inputs[0]); link(nt, cv.outputs[0], ad.inputs[1])
            it = N(nt, "ShaderNodeTexImage", (250, y)); it.image = img; it.extension = 'CLIP'; it.interpolation = 'Linear'
            link(nt, ad.outputs[0], it.inputs["Vector"])
            pc = N(nt, "ShaderNodeVectorMath", (500, y)); pc.operation = 'SCALE'; link(nt, it.outputs["Color"], pc.inputs[0]); link(nt, it.outputs["Alpha"], pc.inputs["Scale"])
            if acc_c is None: acc_c, acc_a = pc.outputs[0], it.outputs["Alpha"]
            else:
                va = N(nt, "ShaderNodeVectorMath", (700, y)); va.operation = 'ADD'; link(nt, acc_c, va.inputs[0]); link(nt, pc.outputs[0], va.inputs[1]); acc_c = va.outputs[0]
                acc_a = math_(nt, 'ADD', acc_a, it.outputs["Alpha"], (700, y - 80))
            n += 1; y -= 180
    alpha = math_(nt, 'DIVIDE', acc_a, float(n), (1000, 0))
    den = math_(nt, 'MAXIMUM', acc_a, 1e-4, (1000, -150))
    col = N(nt, "ShaderNodeVectorMath", (1200, 100)); col.operation = 'DIVIDE'
    link(nt, acc_c, col.inputs[0]); cmb = N(nt, "ShaderNodeCombineXYZ", (1100, -150))
    for c in "XYZ": link(nt, den, cmb.inputs[c])
    link(nt, cmb.outputs[0], col.inputs[1])
    link(nt, col.outputs[0], go.inputs["Color"]); link(nt, alpha, go.inputs["Alpha"])
    return ng

def group_ink():
    """Ink laid onto a white flood backer: density, riso/toner grain, stray specks, fluorescent glow."""
    ng = bpy.data.node_groups.new("Ink Layer", 'ShaderNodeTree')
    sock(ng, "Artwork Color", 'NodeSocketColor', (0, 0, 0, 1))
    sock(ng, "Artwork Alpha", 'NodeSocketFloat', 0.0, 0, 1)
    sock(ng, "UV", 'NodeSocketVector')
    sock(ng, "Ink Density", 'NodeSocketFloat', P["ink_density"], 0, 1)
    sock(ng, "Ink Grain", 'NodeSocketFloat', P["ink_grain"], 0, 2, desc="Riso/photocopy voids and mottling inside the ink")
    sock(ng, "Ink Grain Scale", 'NodeSocketFloat', P["ink_grain_scale"], 0.1, 10)
    sock(ng, "Speckle", 'NodeSocketFloat', P["speckle"], 0, 2, desc="Stray toner specks on the backer")
    sock(ng, "Backer", 'NodeSocketColor', (*P["backer"], 1), desc="White flood coat behind the ink")
    sock(ng, "Blur Alpha", 'NodeSocketFloat', 0.0, 0, 1)
    sock(ng, "Pre Blur", 'NodeSocketFloat', P["pre_blur"], 0, 1, desc="Digitally blur the ink shape before printing: soft glyphs, crisp screen lines")
    sock(ng, "Soft Color", 'NodeSocketColor', (0, 0, 0, 1))
    sock(ng, "Soft Alpha", 'NodeSocketFloat', 0.0, 0, 1)
    sock(ng, "Soft Copy", 'NodeSocketFloat', P["soft_copy"], 0, 1, desc="Opacity of the blurred copy under the crisp print (glow / depth)")
    sock(ng, "Fluoro Glow", 'NodeSocketFloat', P["fluoro"], 0, 5, desc="Fluorescent ink: saturated colours emit")
    sock(ng, "Laser Screen", 'NodeSocketFloat', P["screen"], 0, 1, desc="Colour-laser line-screen halftone strength")
    sock(ng, "Screen Pitch mm", 'NodeSocketFloat', P["screen_pitch_mm"], 0.05, 3)
    sock(ng, "Screen Angle Dark", 'NodeSocketFloat', P["screen_angle_k"], -90, 90)
    sock(ng, "Screen Angle Colour", 'NodeSocketFloat', P["screen_angle_c"], -90, 90)
    sock(ng, "Tracking Dots", 'NodeSocketFloat', P["tracking_dots"], 0, 2, desc="Yellow printer tracking-dot grid")
    sock(ng, "Density Mottle", 'NodeSocketFloat', P["density_mottle"], 0, 1, desc="Toner density varies in soft 10-20 mm clouds")
    sock(ng, "Fluoro Rim", 'NodeSocketFloat', P["fluoro_rim"], 0, 10, desc="Bright 1-2 px rim on fluorescent lime/yellow inks")
    sock(ng, "Light Specks", 'NodeSocketFloat', P["speck_light"], 0, 1, desc="Share of specks that are pale (dust) rather than dark toner")
    sock(ng, "Front Color", 'NodeSocketColor', (0, 0, 0, 1))
    sock(ng, "Front Alpha", 'NodeSocketFloat', 0.0, 0, 1)
    sock(ng, "Front Density", 'NodeSocketFloat', P["front_density"], 0, 1, desc="Toner density of the crisp FRONT plate")
    sock(ng, "BSDF", 'NodeSocketShader', out=True)
    nt = ng; gi = N(nt, "NodeGroupInput", (-1400, 0)); go = N(nt, "NodeGroupOutput", (900, 0))
    uv = gi.outputs["UV"]
    gsc = math_(nt, 'MULTIPLY', gi.outputs["Ink Grain Scale"], 2600.0, (-1200, 400))
    fine = N(nt, "ShaderNodeTexNoise", (-1000, 400), Vector=uv, Scale=gsc, Detail=6.0, Roughness=0.75); fine.noise_dimensions = '2D'
    mott = N(nt, "ShaderNodeTexNoise", (-1000, 150), Vector=uv, Scale=60.0, Detail=5.0, Roughness=0.6); mott.noise_dimensions = '2D'
    # voids: high values of fine noise punch out ink
    voids = math_(nt, 'MAP_RANGE' if False else 'SUBTRACT', fine.outputs["Fac"], 0.56, (-800, 400))
    voids = math_(nt, 'MULTIPLY', voids, 5.0, (-650, 400), clamp=True)
    mottle = math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', mott.outputs["Fac"], 0.35, (-800, 150), clamp=True), 1.2, (-650, 150))
    loss = math_(nt, 'ADD', math_(nt, 'MULTIPLY', voids, 0.85, (-500, 400)), math_(nt, 'MULTIPLY', mottle, 0.10, (-500, 150)), (-350, 300))
    loss = math_(nt, 'MULTIPLY', loss, gi.outputs["Ink Grain"], (-200, 300), clamp=True)
    # crisp core OR a scaled-down wide blur: solids stay sharp, a faint screened tail trails outward
    tail = math_(nt, 'MULTIPLY', gi.outputs["Blur Alpha"], gi.outputs["Pre Blur"], (-600, 50))
    shape = math_(nt, 'MAXIMUM', gi.outputs["Artwork Alpha"], tail, (-500, 0))
    cov = math_(nt, 'MULTIPLY', shape, gi.outputs["Ink Density"], (-350, 0))
    # density mottle: soft clouds of heavier/lighter toner, inside the ink only
    dmn = N(nt, "ShaderNodeTexNoise", (-600, -150), Vector=uv, Scale=9.0, Detail=3.0, Roughness=0.5); dmn.noise_dimensions = '2D'
    dmv = math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', dmn.outputs["Fac"], 0.5, (-450, -150)), math_(nt, 'MULTIPLY', gi.outputs["Density Mottle"], 3.0, (-450, -250)), (-350, -150))
    cov = math_(nt, 'MULTIPLY', cov, math_(nt, 'ADD', 1.0, dmv, (-250, -150)), (-200, -50), clamp=True)
    # only a fraction of grain becomes true dropouts; the rest varies toner tone (keeps solids dense)
    cov = math_(nt, 'MULTIPLY', cov, math_(nt, 'SUBTRACT', 1.0, math_(nt, 'MULTIPLY', loss, 0.3, (-200, 250)), (-200, 150)), (0, 0))
    pt = N(nt, "ShaderNodeTexNoise", (-800, 1000), Vector=uv, Scale=30.0, Detail=3.0, Roughness=0.55); pt.noise_dimensions = '2D'
    starve = N(nt, "ShaderNodeMapRange", (-650, 1000)); link(nt, pt.outputs["Fac"], starve.inputs["Value"])
    starve.inputs["From Min"].default_value = 0.58; starve.inputs["From Max"].default_value = 0.72      # 1 in a few starved patches
    patch = math_(nt, 'SUBTRACT', 1.0, math_(nt, 'MULTIPLY', starve.outputs["Result"], P['toner_patch'], (-500, 1000)), (-400, 1000))
    cov = math_(nt, 'MULTIPLY', cov, patch, (-300, 1000))
    ph_ = N(nt, "ShaderNodeTexVoronoi", (-800, 650), Vector=uv, Scale=260.0); ph_.voronoi_dimensions = '2D'
    phs = N(nt, "ShaderNodeSeparateColor", (-650, 750)); link(nt, ph_.outputs["Color"], phs.inputs[0])
    pin = math_(nt, 'MULTIPLY', math_(nt, 'LESS_THAN', ph_.outputs["Distance"], math_(nt, 'ADD', 0.02, math_(nt, 'MULTIPLY', math_(nt, 'POWER', phs.outputs["Blue"], 2.0, (-600, 850)), 0.3, (-500, 850)), (-400, 850)), (-400, 650)),
                math_(nt, 'GREATER_THAN', phs.outputs["Red"], math_(nt, 'SUBTRACT', 0.7, math_(nt, 'MULTIPLY', starve.outputs["Result"], 0.2, (-650, 700)), (-550, 700)), (-500, 750)), (-300, 700))
    clp = N(nt, "ShaderNodeTexNoise", (-600, 350), Vector=uv, Scale=45.0, Detail=2.0); clp.noise_dimensions = '2D'
    clm = math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', clp.outputs["Fac"], 0.5, (-450, 350)), 10.0, (-350, 350), clamp=True)
    pin = math_(nt, 'MULTIPLY', pin, clm, (-300, 350))
    edgeb = math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', 1.0, gi.outputs["Blur Alpha"], (-450, 450)), 3.0, (-350, 450), clamp=True)
    pin = math_(nt, 'MULTIPLY', pin, math_(nt, 'ADD', math_(nt, 'ADD', 0.35, edgeb, (-300, 500)), math_(nt, 'POWER', starve.outputs["Result"], 2.0, (-400, 550)), (-300, 550)), (-250, 650), clamp=True)
    cov = math_(nt, 'MULTIPLY', cov, math_(nt, 'SUBTRACT', 1.0, math_(nt, 'MULTIPLY', pin, P['pinholes'], (-200, 750)), (-100, 700)), (0, 650))
    en = N(nt, "ShaderNodeTexNoise", (-800, 1250), Vector=uv, Scale=38.0, Detail=3.0, Roughness=0.6); en.noise_dimensions = '2D'
    notch = N(nt, "ShaderNodeMapRange", (-650, 1250)); link(nt, en.outputs["Fac"], notch.inputs["Value"])
    notch.inputs["From Min"].default_value = 0.64; notch.inputs["From Max"].default_value = 0.7
    band = math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', 1.0, gi.outputs["Artwork Alpha"], (-650, 1400)), 5.0, (-550, 1400), clamp=True)
    band = math_(nt, 'MAXIMUM', band, math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', 1.0, gi.outputs["Blur Alpha"], (-650, 1500)), 1.5, (-550, 1500), clamp=True), (-450, 1450))
    cov = math_(nt, 'MULTIPLY', cov, math_(nt, 'SUBTRACT', 1.0, math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', notch.outputs["Result"], band, (-400, 1300)), P['edge_erosion'], (-300, 1300)), (-200, 1300)), (-100, 1250))
    # toner scatter along outlines: stray specks just outside, small gaps just inside
    sv = N(nt, "ShaderNodeTexVoronoi", (-800, 1600), Vector=uv, Scale=420.0); sv.voronoi_dimensions = '2D'
    svc = N(nt, "ShaderNodeSeparateColor", (-650, 1700)); link(nt, sv.outputs["Color"], svc.inputs[0])
    sdot = math_(nt, 'MULTIPLY', math_(nt, 'LESS_THAN', sv.outputs["Distance"], math_(nt, 'ADD', 0.12, math_(nt, 'MULTIPLY', svc.outputs["Blue"], 0.12, (-650, 1850)), (-550, 1850)), (-550, 1600)),
                 math_(nt, 'GREATER_THAN', svc.outputs["Red"], 0.08, (-550, 1700)), (-450, 1650))
    cn = N(nt, "ShaderNodeTexNoise", (-800, 2200), Vector=uv, Scale=22.0, Detail=2.0); cn.noise_dimensions = '2D'
    sdot = math_(nt, 'MULTIPLY', sdot, math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', cn.outputs["Fac"], 0.42, (-650, 2200)), 5.0, (-550, 2200), clamp=True), (-450, 2200))
    a_ = gi.outputs["Artwork Alpha"]; b_ = gi.outputs["Blur Alpha"]
    outside = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', b_, 3.0, (-450, 1800), clamp=True), math_(nt, 'SUBTRACT', 1.0, math_(nt, 'MULTIPLY', a_, 2.0, (-450, 1900), clamp=True), (-350, 1900)), (-300, 1800))
    inside = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', a_, 2.0, (-450, 2000), clamp=True), math_(nt, 'SUBTRACT', 1.0, math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', b_, 0.6, (-550, 2100)), 3.0, (-450, 2100), clamp=True), (-350, 2100)), (-300, 2000))
    cov = math_(nt, 'MAXIMUM', cov, math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', sdot, outside, (-200, 1750)), P['edge_scatter'] * 0.8, (-100, 1750)), (0, 1700))
    cov = math_(nt, 'MULTIPLY', cov, math_(nt, 'SUBTRACT', 1.0, math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', sdot, inside, (-200, 2000)), P['edge_scatter'] * 0.6, (-100, 2000)), (0, 2000)), (100, 1900))
    # colour-laser line screen: line width grows with coverage; dark inks and colour inks use different angles
    mm = N(nt, "ShaderNodeSeparateXYZ", (-1000, -700), Vector=uv)
    xmm = math_(nt, 'MULTIPLY', mm.outputs["X"], 148.0, (-850, -650)); ymm = math_(nt, 'MULTIPLY', mm.outputs["Y"], 210.0, (-850, -800))
    hsv = N(nt, "ShaderNodeSeparateColor", (-1000, -950)); hsv.mode = 'HSV'; link(nt, gi.outputs["Artwork Color"], hsv.inputs[0])
    def screen(angle_sock, y):
        a = math_(nt, 'RADIANS', angle_sock, None, (-700, y))
        u = math_(nt, 'ADD', math_(nt, 'MULTIPLY', xmm, math_(nt, 'COSINE', a, None, (-550, y)), (-400, y)),
                  math_(nt, 'MULTIPLY', ymm, math_(nt, 'SINE', a, None, (-550, y - 80)), (-400, y - 80)), (-250, y))
        ph = math_(nt, 'MULTIPLY', math_(nt, 'DIVIDE', u, gi.outputs["Screen Pitch mm"], (-100, y)), 2 * math.pi, (50, y))
        f = math_(nt, 'FRACT', math_(nt, 'DIVIDE', ph, 2 * math.pi, (150, y)), None, (250, y))
        return math_(nt, 'ABSOLUTE', math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', f, 0.5, (350, y)), 2.0, (450, y)), None, (550, y))
    wk = screen(gi.outputs["Screen Angle Dark"], -700); wc = screen(gi.outputs["Screen Angle Colour"], -900)
    wave = N(nt, "ShaderNodeMix", (650, -800)); wave.data_type = 'FLOAT'
    satk = math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', hsv.outputs["Green"], 0.4, (500, -1000)), 4.0, (600, -1000), clamp=True)
    link(nt, satk, wave.inputs[0]); link(nt, wk, wave.inputs[2]); link(nt, wc, wave.inputs[3])
    # line screen: in tints, ink forms lines whose width tracks coverage (thresholded);
    # in solids, toner still leaves thin lighter lines (density dips), so solids stay dark but textured
    jn = N(nt, "ShaderNodeTexNoise", (600, -450), Vector=uv, Scale=70.0, Detail=2.0); jn.noise_dimensions = '2D'
    jit = math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', jn.outputs["Fac"], 0.5, (700, -450)), P['screen_jitter'], (800, -450))
    thr = math_(nt, 'ADD', math_(nt, 'SUBTRACT', math_(nt, 'MULTIPLY', cov, 1.1, (700, -600)), wave.outputs[0], (800, -700)), jit, (850, -650))
    thr = math_(nt, 'MULTIPLY', math_(nt, 'ADD', math_(nt, 'MULTIPLY', thr, 2.5, (950, -700)), 0.5, (1100, -700)), 1.0, (1250, -700), clamp=True)
    # below ~15% coverage the screen fades out: no hairy fringe, no stray lines on bare backer
    lo = N(nt, "ShaderNodeMapRange", (1100, -550)); link(nt, cov, lo.inputs["Value"]); lo.inputs["From Min"].default_value = 0.03; lo.inputs["From Max"].default_value = 0.12
    fr_ = N(nt, "ShaderNodeMix", (1250, -550)); fr_.data_type = 'FLOAT'; link(nt, lo.outputs["Result"], fr_.inputs[0]); link(nt, cov, fr_.inputs[2]); link(nt, thr, fr_.inputs[3])
    thr = fr_.outputs[0]
    solid = math_(nt, 'POWER', cov, 3.0, (1100, -900))                     # 1 in solids, ~0 in tints
    tinted = N(nt, "ShaderNodeMix", (1300, -800)); tinted.data_type = 'FLOAT'
    link(nt, solid, tinted.inputs[0]); link(nt, thr, tinted.inputs[2]); link(nt, cov, tinted.inputs[3])
    gap = math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', wave.outputs[0], 0.6, (1100, -1050)), 2.5, (1250, -1050), clamp=True)
    dip = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', gap, solid, (1400, -1050)), P['screen_dip'], (1550, -1050))
    lined = tinted.outputs[0]
    covs = N(nt, "ShaderNodeMix", (1750, -600)); covs.data_type = 'FLOAT'
    link(nt, gi.outputs["Laser Screen"], covs.inputs[0]); link(nt, cov, covs.inputs[2]); link(nt, lined, covs.inputs[3])
    cov = covs.outputs[0]
    # stray toner specks: sparse voronoi dots anywhere
    vo = N(nt, "ShaderNodeTexVoronoi", (-1000, -250), Vector=uv, Scale=math_(nt, 'MULTIPLY', gi.outputs["Ink Grain Scale"], 420.0, (-1200, -250)))
    vo.voronoi_dimensions = '2D'; vo.feature = 'F1'
    dot = math_(nt, 'LESS_THAN', vo.outputs["Distance"], 0.07, (-800, -250))
    pick = math_(nt, 'GREATER_THAN', vo.outputs["Color"], 0.93, (-800, -400)) if False else None
    sep = N(nt, "ShaderNodeSeparateColor", (-800, -420)); link(nt, vo.outputs["Color"], sep.inputs[0])
    sel = math_(nt, 'GREATER_THAN', sep.outputs["Red"], 0.9, (-650, -420))
    specks = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', dot, sel, (-500, -300)), gi.outputs["Speckle"], (-350, -300), clamp=True)
    specks = math_(nt, 'MULTIPLY', specks, 0.8, (-200, -300))
    # speck colour = darkest ink (use artwork colour where present, else dark grey)
    lighten = math_(nt, 'ADD', math_(nt, 'MULTIPLY', loss, P['toner_tone'], (0, 250)),
                    math_(nt, 'MULTIPLY', dip, gi.outputs["Laser Screen"], (0, 150)), (100, 200), clamp=True)
    ink_tex = mix_col(nt, lighten, gi.outputs["Artwork Color"], gi.outputs["Backer"], 'MIX', (150, 100))
    softw = math_(nt, 'MULTIPLY', gi.outputs["Soft Alpha"], gi.outputs["Soft Copy"], (0, 400))
    bm = N(nt, "ShaderNodeTexNoise", (-300, 700), Vector=uv, Scale=9.0, Detail=5.0, Roughness=0.55); bm.noise_dimensions = '2D'
    mr = N(nt, "ShaderNodeMapRange", (-150, 700)); link(nt, bm.outputs["Fac"], mr.inputs["Value"]); mr.inputs["From Min"].default_value = 0.38; mr.inputs["From Max"].default_value = 0.62
    bmv = math_(nt, 'ADD', 1.0 - P["backer_mottle"], math_(nt, 'MULTIPLY', mr.outputs["Result"], 2 * P["backer_mottle"], (0, 650)), (50, 700))
    bm2 = N(nt, "ShaderNodeTexNoise", (-300, 900), Vector=uv, Scale=2.5, Detail=2.0); bm2.noise_dimensions = '2D'
    mr2 = N(nt, "ShaderNodeMapRange", (-150, 900)); link(nt, bm2.outputs["Fac"], mr2.inputs["Value"]); mr2.inputs["From Min"].default_value = 0.4; mr2.inputs["From Max"].default_value = 0.6
    tintc = mix_col(nt, mr2.outputs["Result"], (0.81, 0.82, 0.84, 1), (0.82, 0.822, 0.818, 1), 'MIX', (0, 850))
    bk = mix_col(nt, 1.0, tintc, bmv, 'MULTIPLY', (100, 700))
    fib = N(nt, "ShaderNodeTexNoise", (-300, 1100), Vector=uv, Scale=150.0, Detail=4.0, Roughness=0.7); fib.noise_dimensions = '2D'
    fv = math_(nt, 'ADD', 0.78, math_(nt, 'MULTIPLY', fib.outputs["Fac"], 0.45, (-150, 1100)), (0, 1100))
    bk = mix_col(nt, 1.0, bk, fv, 'MULTIPLY', (150, 1000))
    base = mix_col(nt, softw, bk, gi.outputs["Soft Color"], 'MIX', (100, 400))
    col = mix_col(nt, cov, base, ink_tex, 'MIX', (200, 0))
    pale = math_(nt, 'LESS_THAN', sep.outputs["Green"], gi.outputs["Light Specks"], (250, -150))
    col = mix_col(nt, math_(nt, 'MULTIPLY', specks, pale, (300, -150)), col, (0.93, 0.93, 0.94, 1), 'MIX', (350, -100))
    col = mix_col(nt, math_(nt, 'MULTIPLY', specks, math_(nt, 'SUBTRACT', 1.0, pale, (300, -250)), (350, -250)), col, (0.06, 0.06, 0.06, 1), 'MIX', (400, -100))
    # FRONT plate: crisp type/linework, no pre-blur or soft copy, multiplied onto the page like toner
    fdip = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', gap, P['screen_dip'] * 2.0, (250, -450)), gi.outputs["Laser Screen"], (300, -450))
    fcov = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', gi.outputs["Front Alpha"], math_(nt, 'SUBTRACT', gi.outputs["Front Density"], fdip, (250, -400)), (300, -500)),
                 math_(nt, 'SUBTRACT', 1.0, math_(nt, 'MULTIPLY', loss, 0.3, (250, -600)), (300, -600)), (400, -550))
    col = mix_col(nt, fcov, col, mix_col(nt, 1.0, col, gi.outputs["Front Color"], 'MULTIPLY', (400, -700)), 'MIX', (450, -550))
    # printer tracking dots: ~1 mm grid, sparse yellow 0.12 mm dots
    tg = N(nt, "ShaderNodeVectorMath", (-600, -1200)); tg.operation = 'MULTIPLY'
    link(nt, uv, tg.inputs[0]); tg.inputs[1].default_value = (148.0 / 1.02, 210.0 / 1.02, 1.0)
    fr = N(nt, "ShaderNodeVectorMath", (-450, -1200)); fr.operation = 'FRACTION'; link(nt, tg.outputs[0], fr.inputs[0])
    fl_ = N(nt, "ShaderNodeVectorMath", (-450, -1350)); fl_.operation = 'FLOOR'; link(nt, tg.outputs[0], fl_.inputs[0])
    cd_ = N(nt, "ShaderNodeVectorMath", (-300, -1200)); cd_.operation = 'DISTANCE'; link(nt, fr.outputs[0], cd_.inputs[0]); cd_.inputs[1].default_value = (0.5, 0.5, 0.0)
    rnd = N(nt, "ShaderNodeTexWhiteNoise", (-300, -1350)); rnd.noise_dimensions = '2D'; link(nt, fl_.outputs[0], rnd.inputs["Vector"])
    tdot = math_(nt, 'MULTIPLY', math_(nt, 'LESS_THAN', cd_.outputs["Value"], 0.2, (-150, -1200)),
                 math_(nt, 'GREATER_THAN', rnd.outputs["Value"], 0.72, (-150, -1350)), (0, -1250))
    tdot = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', tdot, gi.outputs["Tracking Dots"], (150, -1250)), 0.55, (300, -1250), clamp=True)
    shape = math_(nt, 'MAXIMUM', math_(nt, 'MAXIMUM', gi.outputs["Artwork Alpha"], gi.outputs["Blur Alpha"], (200, -1450)), gi.outputs["Front Alpha"], (300, -1400))
    tdot = math_(nt, 'MULTIPLY', tdot, math_(nt, 'SUBTRACT', 1.0, math_(nt, 'MULTIPLY', shape, 3.0, (350, -1400), clamp=True), (400, -1300), clamp=True), (450, -1250))
    col = mix_col(nt, tdot, col, (1.0, 0.85, 0.1, 1), 'MIX', (500, -300))
    bs = N(nt, "ShaderNodeBsdfPrincipled", (600, 0)); link(nt, col, bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.7
    bs.inputs["Specular IOR Level"].default_value = 0.0   # ink sits against acrylic: no air interface, no sheen
    # fluorescence: emission proportional to chroma of the ink
    sepc = N(nt, "ShaderNodeSeparateColor", (200, -350)); link(nt, gi.outputs["Artwork Color"], sepc.inputs[0]); sepc.mode = 'HSV'
    fl = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', sepc.outputs["Green"], cov, (350, -350)), gi.outputs["Fluoro Glow"], (500, -350))
    # fluoro rim: a 1-2 px brighter, yellower edge on lime/yellow inks (measured in ref1: R +10-19)
    a_ = gi.outputs["Artwork Alpha"]
    band = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', a_, math_(nt, 'SUBTRACT', 1.0, a_, (200, -500)), (300, -500)), 4.0, (400, -500), clamp=True)
    hue = math_(nt, 'SUBTRACT', 1.0, math_(nt, 'MULTIPLY', math_(nt, 'ABSOLUTE', math_(nt, 'SUBTRACT', sepc.outputs["Red"], 0.23, (200, -600)), None, (300, -600)), 8.0, (400, -600)), (500, -600), clamp=True)
    rim = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', band, hue, (500, -500)), math_(nt, 'MULTIPLY', sepc.outputs["Green"], gi.outputs["Fluoro Rim"], (500, -700)), (600, -550))
    link(nt, mix_col(nt, math_(nt, 'MULTIPLY', rim, 1.0, (650, -650), clamp=True), gi.outputs["Artwork Color"], (0.9, 1.0, 0.05, 1), 'MIX', (700, -650)), bs.inputs["Emission Color"])
    link(nt, math_(nt, 'ADD', fl, rim, (650, -450)), bs.inputs["Emission Strength"])
    link(nt, bs.outputs[0], go.inputs["BSDF"])
    return ng

# ---------------------------------------------------------------- materials
def mat_front(g):
    m = bpy.data.materials.new("Acrylic_Front_Frosted"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    gn = N(nt, "ShaderNodeGroup", (0, 0)); gn.node_tree = g; gn.label = "FROSTED ACRYLIC — tweak me"; gn.width = 260
    out = N(nt, "ShaderNodeOutputMaterial", (400, 0)); link(nt, gn.outputs[0], out.inputs["Surface"])
    return m

def mat_edges(g):
    m = bpy.data.materials.new("Acrylic_Edges"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    gn = N(nt, "ShaderNodeGroup", (0, 0)); gn.node_tree = g; gn.width = 260
    gn.inputs["Diffusion"].default_value = P["edge_rough"]; gn.inputs["Milk"].default_value = 0.03; gn.inputs["Tint"].default_value = (0.43, 0.45, 0.48, 1)
    gn.inputs["Weave"].default_value = 0.0; gn.inputs["Surface Grain"].default_value = 0.0
    gn.inputs["Satin Coat"].default_value = 0.0; gn.inputs["Surface Speckle"].default_value = 0.0; gn.inputs["Roughness Mottle"].default_value = P["rough_mottle"]
    out = N(nt, "ShaderNodeOutputMaterial", (400, 0)); link(nt, gn.outputs[0], out.inputs["Surface"])
    return m

def mat_print(g_ink, g_uv):
    m = bpy.data.materials.new("Print_Ink"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    tc = N(nt, "ShaderNodeTexCoord", (-900, 0))
    uvg = N(nt, "ShaderNodeGroup", (-650, 0)); uvg.node_tree = g_uv; uvg.width = 220
    link(nt, tc.outputs["UV"], uvg.inputs["Vector"])
    img = bpy.data.images.load(P["artwork"], check_existing=True); img.name = "ARTWORK"
    im = N(nt, "ShaderNodeTexImage", (-350, 0)); im.image = img; im.extension = 'CLIP'; im.interpolation = 'Cubic'
    im.label = "ARTWORK — swap image here"; link(nt, uvg.outputs[0], im.inputs["Vector"])
    ink = N(nt, "ShaderNodeGroup", (0, 0)); ink.node_tree = g_ink; ink.width = 240; ink.label = "INK — tweak me"
    link(nt, im.outputs["Color"], ink.inputs["Artwork Color"]); link(nt, im.outputs["Alpha"], ink.inputs["Artwork Alpha"])
    link(nt, tc.outputs["UV"], ink.inputs["UV"])
    sc_ = N(nt, "ShaderNodeGroup", (-350, -350)); sc_.node_tree = group_soft_copy(img); sc_.width = 220; sc_.label = "SOFT COPY (blur)"
    link(nt, tc.outputs["UV"], sc_.inputs["Vector"])
    link(nt, sc_.outputs["Color"], ink.inputs["Soft Color"]); link(nt, sc_.outputs["Alpha"], ink.inputs["Soft Alpha"])
    sc_.label = "SHADOW COPY (offset blur)"
    pb_ = N(nt, "ShaderNodeGroup", (-350, -700)); pb_.node_tree = sc_.node_tree; pb_.width = 220; pb_.label = "PRE-BLUR (ink shape)"
    pb_.inputs["Radius mm"].default_value = P["pre_blur_mm"]; pb_.inputs["Offset X mm"].default_value = 0; pb_.inputs["Offset Y mm"].default_value = 0
    link(nt, uvg.outputs[0], pb_.inputs["Vector"]); link(nt, pb_.outputs["Alpha"], ink.inputs["Blur Alpha"])
    cs_ = N(nt, "ShaderNodeGroup", (-350, -1050)); cs_.node_tree = sc_.node_tree; cs_.width = 220; cs_.label = "CORE SOFTEN"
    cs_.inputs["Radius mm"].default_value = P["core_soften_mm"]; cs_.inputs["Offset X mm"].default_value = 0; cs_.inputs["Offset Y mm"].default_value = 0
    link(nt, uvg.outputs[0], cs_.inputs["Vector"]); link(nt, cs_.outputs["Alpha"], ink.inputs["Artwork Alpha"])
    if P["artwork_front"]:
        fimg = bpy.data.images.load(P["artwork_front"], check_existing=True); fimg.name = "ARTWORK FRONT"
        fi = N(nt, "ShaderNodeTexImage", (-350, 350)); fi.image = fimg; fi.extension = 'CLIP'; fi.interpolation = 'Cubic'
        fi.label = "FRONT PLATE — crisp type, swap here"; link(nt, uvg.outputs[0], fi.inputs["Vector"])
        link(nt, fi.outputs["Color"], ink.inputs["Front Color"]); link(nt, fi.outputs["Alpha"], ink.inputs["Front Alpha"])
    out = N(nt, "ShaderNodeOutputMaterial", (350, 0)); link(nt, ink.outputs[0], out.inputs["Surface"])
    return m

def mat_backdrop():
    m = bpy.data.materials.new("Backdrop_Grey"); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*P["bg"], 1); b.inputs["Roughness"].default_value = 0.85
    return m

# ---------------------------------------------------------------- geometry
def make_slab(mfront, medge):
    w, t, h = P["slab"]
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * t, v.co.z * h + h / 2))
    me = bpy.data.meshes.new("Slab"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("Slab", me); bpy.context.scene.collection.objects.link(ob)
    me.materials.append(mfront); me.materials.append(medge)
    for p in me.polygons: p.material_index = 0 if p.normal.y < -0.9 else 1
    bv = ob.modifiers.new("Bevel", 'BEVEL'); bv.width = P["edge_bevel"]; bv.segments = P["edge_segs"]
    bv.limit_method = 'ANGLE'; bv.harden_normals = False; bv.profile = 0.5; bv.material = 0
    for p in me.polygons: p.use_smooth = True
    ob.rotation_euler = tuple(math.radians(a) for a in P["slab_rot"])
    ob["print_depth_mm"] = (t - P["print_inset"]) * 1000
    return ob

def make_print(slab, mprint):
    w, t, h = P["slab"]; ins = 0.0
    bpy.ops.mesh.primitive_plane_add(size=1)
    pl = bpy.context.active_object; pl.name = "Print"
    pl.scale = (w - 2 * ins, h - 2 * ins, 1); pl.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    # after rotation normal faces -Y (towards camera side / front face)
    pl.location = (0, t / 2 - P["print_inset"], h / 2)
    pl.data.materials.append(mprint); pl.parent = slab
    rim = bpy.data.materials.new("Print_Rim"); rim.use_nodes = True
    rim.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.45, 0.46, 0.48, 1)
    pl.data.materials.append(rim)
    so = pl.modifiers.new("InkLayer", 'SOLIDIFY'); so.thickness = 0.0004; so.offset = 1.0; so.material_offset_rim = 1
    # driver: slab custom prop print_depth_mm sets distance from the frosted front
    fc = pl.driver_add("location", 1); d = fc.driver; d.type = 'SCRIPTED'
    var = d.variables.new(); var.name = "depth"; var.type = 'SINGLE_PROP'
    var.targets[0].id = slab; var.targets[0].data_path = '["print_depth_mm"]'
    d.expression = f"-{t/2:.6f} + depth/1000"
    return pl

def make_backdrop(mat):
    # cyclorama: floor + curved sweep up to a wall
    prof = []
    R = 0.35; y0 = 0.35
    for i in range(0, 13):
        prof.append((-1.5 + i * (y0 + 1.5) / 12, 0.0))
    for i in range(1, 17):
        a = (i / 16) * math.pi / 2
        prof.append((y0 + R * math.sin(a), R - R * math.cos(a)))
    for i in range(1, 6):
        prof.append((y0 + R, R + i * 0.3))
    bm = bmesh.new(); X = 2.0
    rows = [[bm.verts.new((x, y, z)) for (y, z) in prof] for x in (-X, X)]
    for i in range(len(prof) - 1):
        bm.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
    me = bpy.data.meshes.new("Backdrop"); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new("Backdrop", me); bpy.context.scene.collection.objects.link(ob)
    me.materials.append(mat)
    return ob

# ---------------------------------------------------------------- scene
def build(args):
    wipe()
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; cy = sc.cycles
    cp = bpy.context.preferences.addons['cycles'].preferences
    cp.compute_device_type = 'METAL'; cp.get_devices()
    for d in cp.devices: d.use = (d.type == 'METAL')
    cy.device = 'GPU'; cy.samples = args.samples; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.01
    cy.use_denoising = True; cy.denoiser = 'OPENIMAGEDENOISE'; cy.denoising_prefilter = 'ACCURATE'
    cy.max_bounces = 24; cy.transmission_bounces = 16; cy.glossy_bounces = 6; cy.diffuse_bounces = 4
    cy.caustics_reflective = True; cy.caustics_refractive = True; cy.blur_glossy = 0.0
    cy.sample_clamp_indirect = 10; cy.use_light_tree = True
    sc.render.resolution_x, sc.render.resolution_y = P["res"]; sc.render.resolution_percentage = int(args.scale * 100)
    vs = sc.view_settings; vs.view_transform = 'AgX'
    try: vs.look = P["look"]
    except Exception as e: print("look", e)
    vs.exposure = P["exposure"]
    w = bpy.data.worlds.new("Studio"); w.use_nodes = True; sc.world = w
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (1, 1, 1, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = P["world"]

    gF, gU, gI = group_frosted(), group_ink_misprint(), group_ink()
    slab = make_slab(mat_front(gF), mat_edges(gF))
    make_print(slab, mat_print(gI, gU))
    if P.get('debug_noslab'): slab.hide_render = True
    make_backdrop(mat_backdrop())

    for name, loc, tgt, size, power, k in P["lights"]:
        ld = bpy.data.lights.new(name, 'AREA'); ld.shape = 'RECTANGLE'; ld.size, ld.size_y = size
        ld.energy = 0.0 if name in P.get('mute', ()) else power; ld.use_temperature = True; ld.temperature = k
        lo = bpy.data.objects.new(name, ld); sc.collection.objects.link(lo); lo.location = loc; look_at(lo, tgt)
        if name in P.get("glossy_only", ()): lo.visible_diffuse = False; lo.visible_transmission = False

    if P.get("flag"):
        # negative fill: black card left of the slab, invisible to camera, darkens the side face reflection
        loc, size = P["flag"]
        bpy.ops.mesh.primitive_plane_add(size=1, location=loc); fl = bpy.context.active_object; fl.name = "Flag_Black"
        fl.scale = (size[0], size[1], 1); fl.rotation_euler = (Vector((0, 0, 0.1)) - fl.location).to_track_quat('Z', 'Y').to_euler()
        fm = bpy.data.materials.new("Flag_Black"); fm.use_nodes = True
        fm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.01, 0.01, 0.01, 1)
        fm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
        fl.data.materials.append(fm); fl.visible_camera = False
    cd = bpy.data.cameras.new("Cam"); cd.lens = P["cam_lens"]; cd.sensor_width = 36; cd.sensor_fit = 'AUTO'
    cd.dof.use_dof = True; cd.dof.aperture_fstop = P["fstop"]
    cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cam.location = (0.0, -P["cam_dist"], P["cam_h"]); look_at(cam, P["cam_target"])
    fe = bpy.data.objects.new("Focus", None); sc.collection.objects.link(fe); fe.parent = slab
    fe.location = (0, -P["slab"][1] / 2, P["slab"][2] * 0.52); cd.dof.focus_object = fe
    # satin sweep: put the Satin strip where the camera's mirror ray from sheen_point lands
    sl = sc.objects.get("Satin")
    if sl and P.get("sheen_point"):
        bpy.context.view_layer.update()
        w_, t_, h_ = P["slab"]; u, v = P["sheen_point"]
        pt = slab.matrix_world @ Vector((u * w_, -t_ / 2, h_ / 2 + v * h_))
        n = (slab.matrix_world.to_3x3() @ Vector((0, -1, 0))).normalized()
        vv = (cam.location - pt).normalized(); r = 2 * n.dot(vv) * n - vv
        sl.location = pt + r * P["sheen_dist"]; look_at(sl, pt)
        sl.rotation_euler.rotate_axis('Z', math.radians(P.get('sheen_rot', 0.0)))
    t = bpy.data.texts.new("HOW_TO_TWEAK")
    t.write("""WONDER / PRINTED PLASTIC — controls

SWAP THE ARTWORK
  Image editor > open 'ARTWORK' > Image > Replace (any A5-ratio PNG, transparent = no ink).
  Or edit content/artwork.svg and run content/render_artwork.sh, then Image > Reload.

MATERIAL 'Acrylic_Front_Frosted' > group 'Frosted Acrylic'  (the plastic)
  Diffusion      how blurred the print looks through the plastic
  Halo / Halo Spread   soft glow around everything
  Milk           lifts blacks / flattens contrast
  Satin Coat / Coat Roughness   sheen on top
  Surface Speckle, Roughness Mottle   grain on top of the plastic

MATERIAL 'Print_Ink' > group 'Ink Layer'  (the print)
  Pre Blur       strength of the soft screened tail around shapes
  Soft Copy      unscreened glow under the ink
  Laser Screen / Screen Pitch mm / Screen Angle Dark   the laser line screen
  Ink Density    how dark the ink is (lower = more lifted)
  Tracking Dots, Speckle, Fluoro Glow (fluorescent inks)
  Fluoro Rim     bright yellow edge on lime inks;  Density Mottle   toner clouds;  Light Specks  pale vs dark specks
  Image 'ARTWORK FRONT' (optional)   crisp plate for small type: no pre-blur, no soft copy
  Nodes 'PRE-BLUR' / 'SOFT COPY' / 'CORE SOFTEN' > Radius mm   blur widths
  Group 'Ink Misprint UV' > Ragged Edges, Offset X/Y mm (misregistration)

OBJECT 'Slab' > Custom Properties > print_depth_mm   how deep the print sits (bigger = blurrier)

RENDER TIP: the line screen is fine; render at 200% and downscale for the cleanest result.
""")
    sc.view_layers[0].cycles.denoising_store_passes = True
    compositor(sc)
    return sc

def compositor(sc):
    C = P["comp"]
    ng = bpy.data.node_groups.new("Comp", "CompositorNodeTree"); sc.compositing_node_group = ng
    def node(t, x, y=0):
        n = ng.nodes.new(t); n.location = (x, y); return n
    rl = node("CompositorNodeRLayers", 0); img = rl.outputs["Image"]; x = 300
    # partial denoise: keep some true render grain, lose the sampling speckle
    if "Noisy Image" in rl.outputs and C.get("denoise_mix", 1.0) < 1.0:
        dm = node("ShaderNodeMix", x, 200); dm.data_type = 'RGBA'; dm.inputs[0].default_value = C["denoise_mix"]
        ng.links.new(rl.outputs["Noisy Image"], dm.inputs[6]); ng.links.new(img, dm.inputs[7]); img = dm.outputs[2]; x += 200
    if C.get("vignette"):
        em = node("CompositorNodeEllipseMask", x, -300); em.inputs["Size"].default_value = (0.95, 0.95)
        bl = node("CompositorNodeBlur", x + 150, -300); bl.inputs["Size"].default_value = (300, 300)
        try: bl.inputs["Type"].default_value = 'Fast Gaussian'
        except Exception: pass
        ng.links.new(em.outputs["Mask"], bl.inputs["Image"])
        inv = node("ShaderNodeMix", x + 300, -300); inv.data_type = 'RGBA'; inv.blend_type = 'MIX'
        inv.inputs[0].default_value = 1 - C["vignette"]; inv.inputs[6].default_value = (1, 1, 1, 1)
        ng.links.new(bl.outputs["Image"], inv.inputs[7])
        # fac=1-v: mix(white, mask) -> weight toward mask by (1-v)?? keep simple: lerp mask towards 1
        inv.inputs[0].default_value = C["vignette"]; inv.inputs[6].default_value = (1, 1, 1, 1)
        mixv = node("ShaderNodeMix", x + 450); mixv.data_type = 'RGBA'; mixv.blend_type = 'MULTIPLY'; mixv.inputs[0].default_value = 1.0
        ng.links.new(img, mixv.inputs[6]); ng.links.new(inv.outputs[2], mixv.inputs[7]); img = mixv.outputs[2]; x += 600
    if C.get("grain"):
        ic = node("CompositorNodeImageCoordinates", x, -300); ng.links.new(rl.outputs["Image"], ic.inputs["Image"])
        wn = node("ShaderNodeTexWhiteNoise", x + 150, -300); wn.noise_dimensions = '2D'
        ng.links.new(ic.outputs["Pixel"], wn.inputs["Vector"])
        sub = node("ShaderNodeMath", x + 300, -300); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = 0.5
        ng.links.new(wn.outputs["Value"], sub.inputs[0])
        mul = node("ShaderNodeMath", x + 450, -300); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = C["grain"]
        ng.links.new(sub.outputs[0], mul.inputs[0])
        add = node("ShaderNodeMix", x + 600); add.data_type = 'RGBA'; add.blend_type = 'ADD'; add.inputs[0].default_value = 1.0
        ng.links.new(img, add.inputs[6]); ng.links.new(mul.outputs[0], add.inputs[7]); img = add.outputs[2]; x += 800
    ng.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    o = ng.nodes.new("NodeGroupOutput"); o.location = (x, 0); ng.links.new(img, o.inputs["Image"])
    sc.render.use_compositing = True

# ---------------------------------------------------------------- main
if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "renders", "test.png"))
    ap.add_argument("--samples", type=int, default=256)
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--save", default="")
    ap.add_argument("--norender", action="store_true")
    ap.add_argument("--set", action="append", default=[], help="key=python-literal overrides for P")
    args = ap.parse_args(argv)
    import ast
    for kv in args.set:
        k, v = kv.split("=", 1)
        try: P[k] = ast.literal_eval(v)
        except Exception: P[k] = v
    sc = build(args)
    if args.save:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(args.save))
        bpy.ops.file.make_paths_relative(); bpy.ops.wm.save_mainfile()
    if not args.norender:
        sc.render.filepath = os.path.abspath(args.out); sc.render.image_settings.file_format = 'PNG'
        bpy.ops.render.render(write_still=True)
        print("WROTE", sc.render.filepath)
