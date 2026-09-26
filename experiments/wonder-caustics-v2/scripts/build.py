"""Wonder logo as dispersive perspex on black — build + render.

Run:  blender -b -P scripts/build.py -- --out renders/v01.png --samples 256 --scale 0.5
Everything tunable is in P (params). Blender 5.2 API — sockets addressed by name
except Math/Mix/MixShader (see notes in wonder-logo-exploration/docs).
"""
import bpy, bmesh, math, sys, os, argparse
from mathutils import Euler, Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.path.join(ROOT, "assets", "logo.svg")

# ---------------------------------------------------------------- params
P_STRIPES = 3
P = dict(
    logo_w=2.0,            # metres across
    depth=0.42,            # slab thickness
    bevel=0.15, bevel_segs=16,
    # geometry: clean bevel only (no remesh); the face crown lives in the shader (crown_bump)
    remesh_mode=None, remesh_voxel=0.012, subsurf=0, presmooth=0, quad_faces=30000,
    wave_strength=0.0, wave_scale=1.05, wave_stretch=(1.0, 1.0, 2.6), wave_tilt=15.0, wave_rim=0.0,
    crown_bump=0.85, crown_detail=1.0, ripple=0.0002, ripple_scale=30.0, ripple2=0.00005, ripple2_scale=90.0, gloss_inside=0.0, panel_vignette=0.35, panel_holes=[(0.539,0.296,0.12)], bevel_back=0, crown_face=(0.55, 0.97),
    # material
    ior=1.49, spread=0.45, rough=0.015,
    haze=0.1, prints=0.6, dust=1.0, dust_size=0.4, dust_scale=600, dust_density=0.005, scratch=0.15, scratch_bump=0.05, scratch_width=0.008, coat=0.2, coat_rough=0.06,
    absorb=(0.97, 0.985, 1.0), absorb_density=0.16,
    tilt=(8.0, -4.0, -14.0),  # object rotation deg (x,y,z) for a dynamic pose
    cam_lens=85.0, cam_dist=5.9, cam_fstop=2.8, focus_offset=0.2, cam_h=0.0, cam_dx=0.0, cam_dz=0.0,
    floor=False, floor_z=-1.9,
    lights=[  # name, loc, target, size(x,y), power, spread_deg, kelvin
        ("Key_soft",   (-2.9, -1.1, 2.6), (0, 0, 0), (1.2, 3.6), 150, 80, 9500),
        ("Rim_soft",   ( 3.1,  1.5, 1.4), (0, 0, 0), (0.8, 3.0), 100, 80, 2700),
        ("Glint_warm", ( 3.2,  1.6, 1.6), (0, 0, 0), (0.20, 5.0), 900, 35, 2700),
        ("Kick_L",     (-1.3,  4.5, -0.4), (0, 0, 0), (0.15, 3.0), 60, 60, 9500, True),  # behind, ~15° off axis: grazing hairline rims
        ("Kick_R",     ( 1.6,  4.5, -0.9), (0, 0, 0), (0.15, 3.0), 60, 60, 2700, True),
    ],
    panels=[  # name, loc, target, size(w,h), strength, colours, stripes, mode  (camera-hidden emitters)
        ("Grad_back",  (0.0, 8.25, 0.2), (0, 0, 0.2), (9.5, 9.5), 2.0, [(1.0,0.30,0.04),(1.0,1.0,1.0),(0.55,0.85,0.95),(0.03,0.32,1.0)], P_STRIPES, "refract"),
        ("Grad_front", (-1.5, -4.5, 3.5), (0, 0, 0), (5.0, 2.5), 0.12, [(0.1,0.3,1.0),(1.0,1.0,1.0),(1.0,0.45,0.1)], 3, "reflect"),
        ("Card_L",     (-2.7, -5.0, 1.8), (0, 0, 0), (3.0, 3.0), 0.6, [(0,0,0),(0.12,0.12,0.12),(1,1,1)], 0, "reflect"),   # mirror direction of the front faces
        ("Card_R",     ( 2.5, -1.4, 1.2), (0, 0, 0), (3.2, 2.2), 0.25, [(0,0,0),(0.15,0.15,0.15),(1,1,1)], 0, "reflect"),
        ("Spark_1",    (-0.8, -4.0, 3.2), (0, 0, 0), (0.08, 0.08), 40.0, [(1,1,1),(1,1,1)], 0, "reflect"),   # small bright things for the body to reflect
        ("Spark_2",    ( 2.2, -3.5, 2.4), (0, 0, 0), (0.06, 0.06), 40.0, [(1,0.9,0.8),(1,0.9,0.8)], 0, "reflect"),
        ("Spark_3",    (-2.6, -3.0, -1.2), (0, 0, 0), (0.06, 0.06), 30.0, [(0.85,0.9,1),(0.85,0.9,1)], 0, "reflect"),
        ("Strip_cam",  (-1.5, -5.5, 2.5), (0, 0, 0), (0.30, 4.0), 9000.0, [(0.0,0.0,0.0),(0.5,0.5,0.5),(1,1,1)], 0, "reflect"),  # graded strip beside camera
    ],
    stripe_duty=0.4, stripe_soft=0.1, rail=9.0, rail_width=0.03, band_warp=0.1, panel_noise=0.07, lobes=6, band_angle=22.0, band_tint_mix=0.15,
    spectrum=[(1.0,0.02,0.0),(1.0,0.40,0.0),(1.0,0.90,0.05),(0.05,0.95,0.15),(0.0,0.75,1.0),(0.02,0.15,1.0),(0.55,0.05,1.0)],
    exposure=-0.5, look="AgX - Punchy", light_diffuse=0.12,
    comp=dict(glow=0.18, glow_thr=1.2, glow_size=0.4, veil=0.03, streaks=0.025, streak_thr=3.0, chroma=0.010,
              vignette=0.15, vig_size=(0.86, 0.86), vig_blur=0.16,
              lift=(1.003, 1.003, 1.008), scurve=0.035, sat=1.4, grain=0.035),
)

# ---------------------------------------------------------------- helpers
def deselect():
    for o in bpy.context.view_layer.objects: o.select_set(False)

def activate(ob):
    deselect(); ob.select_set(True); bpy.context.view_layer.objects.active = ob

def wipe():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def centre_curve_data(d):
    xs, ys = [], []
    for sp in d.splines:
        for bp in sp.bezier_points:
            for v in (bp.co, bp.handle_left, bp.handle_right): xs.append(v.x); ys.append(v.y)
        for pt in sp.points: xs.append(pt.co.x); ys.append(pt.co.y)
    cx, cy = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
    for sp in d.splines:
        for bp in sp.bezier_points:
            for v in (bp.co, bp.handle_left, bp.handle_right): v.x -= cx; v.y -= cy
        for pt in sp.points: pt.co.x -= cx; pt.co.y -= cy
    return max(xs)-min(xs), max(ys)-min(ys)

def import_logo():
    before = {o.name for o in bpy.data.objects}
    bpy.ops.import_curve.svg(filepath=SVG)
    new = [o for o in bpy.data.objects if o.name not in before]
    deselect()
    for o in new: o.select_set(True)
    bpy.context.view_layer.objects.active = new[0]
    bpy.ops.object.join()
    logo = bpy.context.active_object
    for c in list(logo.users_collection): c.objects.unlink(logo)
    bpy.context.scene.collection.objects.link(logo)
    for c in list(bpy.data.collections):
        if not c.objects: bpy.data.collections.remove(c)
    d = logo.data
    d.resolution_u = 24; d.dimensions = '2D'; d.fill_mode = 'BOTH'
    for sp in d.splines: sp.resolution_u = P.get("curve_res", 24)
    print("SPLINES", [(sp.type, len(sp.bezier_points), len(sp.points), sp.resolution_u) for sp in d.splines])
    w, h = centre_curve_data(d)
    logo.location = (0, 0, 0)
    return logo, P["logo_w"] / w

def curve_to_prism(cur, depth, sf):
    # extrude in native units (never scale a curve), convert, then scale the mesh
    cur.data.extrude = (depth/2)/sf
    cur.data.bevel_depth = 0; cur.data.offset = 0
    activate(cur); bpy.ops.object.convert(target='MESH')
    ob = bpy.context.active_object; ob.name = "Logo"
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data); bm.free()
    ob.scale = (sf, sf, sf)
    ob.rotation_euler = Euler((math.radians(90), 0, 0))
    activate(ob); bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    # remove the curve's material slots
    ob.data.materials.clear()
    return ob

def bevel(ob, width, segs):
    b = ob.modifiers.new("Bevel", 'BEVEL')
    b.width = width; b.segments = segs; b.limit_method = 'ANGLE'
    b.angle_limit = math.radians(30); b.miter_outer = 'MITER_ARC'; b.use_clamp_overlap = P.get('bevel_clamp', True)
    b.harden_normals = True
    activate(ob); bpy.ops.object.modifier_apply(modifier=b.name)
    bpy.ops.object.shade_smooth()
    if P.get("flat_caps", True):
        # the big front/back n-gons triangulate into slivers; smooth-interpolated normals across
        # them band visibly in refraction. Keep caps flat; the bevel ring stays smooth.
        n = 0
        for f in ob.data.polygons:
            if abs(f.normal.y) > 0.995: f.use_smooth = False; n += 1
        print("flat caps:", n)
    else:
        try: bpy.ops.object.shade_auto_smooth(angle=math.radians(40))
        except Exception as e: print("auto smooth:", e)

def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

# ---------------------------------------------------------------- materials
def _noise(nt, vec, scale, detail=2.0, rough=0.5, loc=(0,0), mapping=None):
    """Noise texture on object coords; optional mapping=(rot_deg_xyz, scale_xyz) for stretched families."""
    src = vec
    if mapping:
        rot, scl = mapping
        mp = nt.nodes.new("ShaderNodeMapping"); mp.location = (loc[0]-200, loc[1])
        mp.inputs["Rotation"].default_value = tuple(math.radians(r) for r in rot)
        mp.inputs["Scale"].default_value = scl
        nt.links.new(vec, mp.inputs["Vector"]); src = mp.outputs[0]
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.location = loc
    nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = detail
    nz.inputs["Roughness"].default_value = rough
    nt.links.new(src, nz.inputs["Vector"])
    return nz.outputs["Fac"]

def _window(nt, val, lo, hi, loc=(0,0), invert=False):
    """ColorRamp window lo..hi -> 0..1 (or 1..0)."""
    rp = nt.nodes.new("ShaderNodeValToRGB"); rp.location = loc
    rp.color_ramp.elements[0].position = lo; rp.color_ramp.elements[1].position = hi
    if invert:
        rp.color_ramp.elements[0].color = (1,1,1,1); rp.color_ramp.elements[1].color = (0,0,0,1)
    nt.links.new(val, rp.inputs[0]); return rp.outputs["Color"]

def _math(nt, op, a, b=None, loc=(0,0)):
    m = nt.nodes.new("ShaderNodeMath"); m.operation = op; m.location = loc
    if hasattr(a, "bl_rna"): nt.links.new(a, m.inputs[0])
    else: m.inputs[0].default_value = a
    if b is not None:
        if hasattr(b, "bl_rna"): nt.links.new(b, m.inputs[1])
        else: m.inputs[1].default_value = b
    return m.outputs[0]

def _bump(nt, height, strength, distance, prev=None, loc=(0,0)):
    bp = nt.nodes.new("ShaderNodeBump"); bp.location = loc
    bp.inputs["Strength"].default_value = strength; bp.inputs["Distance"].default_value = distance
    nt.links.new(height, bp.inputs["Height"])
    if prev is not None: nt.links.new(prev, bp.inputs["Normal"])
    return bp.outputs["Normal"]

def mat_dispersive():
    """RGB-split refraction + Fresnel glossy, with a procedural imperfection stack:
    crown (shader bump standing in for face displacement), greasy haze, fingerprints,
    dust specks, surface-conforming micro-scratches, and a soft coat lobe."""
    m = bpy.data.materials.new("PerspexDispersive"); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (1400, 0)
    ior, sp = P["ior"], P["spread"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-1800, 0)
    obj = tc.outputs["Object"]
    normal = None            # running bumped normal
    rough_terms = []         # roughness contributions for refraction+glossy (MAX-combined)
    gloss_terms = []         # extra contributions for the glossy lobe only

    # --- crown: broad low-frequency bump on the front/back faces (replaces mesh displacement)
    if P.get("crown_bump", 0):
        st = P["wave_stretch"]
        h = _noise(nt, obj, 1.0/P["wave_scale"], detail=P.get("crown_detail", 1.0), rough=0.4, loc=(-1300, 700),
                   mapping=((0, P.get("wave_tilt", 0.0), 0), (1/st[0], 1/st[1], 1/st[2])))
        geo = nt.nodes.new("ShaderNodeNewGeometry"); geo.location = (-1600, 400)
        vt = nt.nodes.new("ShaderNodeVectorTransform"); vt.location = (-1400, 400)
        vt.vector_type = 'NORMAL'; vt.convert_from = 'WORLD'; vt.convert_to = 'OBJECT'
        nt.links.new(geo.outputs["Normal"], vt.inputs[0])
        sep = nt.nodes.new("ShaderNodeSeparateXYZ"); sep.location = (-1200, 400)
        nt.links.new(vt.outputs[0], sep.inputs[0])
        ny = _math(nt, 'ABSOLUTE', sep.outputs["Y"], loc=(-1050, 400))
        wr = nt.nodes.new("ShaderNodeMapRange"); wr.location = (-900, 400); wr.interpolation_type = 'SMOOTHSTEP'
        lo, hi = P.get("crown_face", (0.55, 0.97))
        wr.inputs["From Min"].default_value = lo; wr.inputs["From Max"].default_value = hi
        wr.inputs["To Min"].default_value = P.get("wave_rim", 0.0); wr.inputs["To Max"].default_value = 1.0
        nt.links.new(ny, wr.inputs["Value"])
        hw = _math(nt, 'MULTIPLY', h, wr.outputs["Result"], loc=(-700, 600))
        normal = _bump(nt, hw, 1.0, P["crown_bump"], None, loc=(-500, 600))
        crown_normal = normal

    # --- ripple: fine low-amplitude surface undulation (real cast perspex is never optically flat)
    if P.get("ripple", 0):
        rp = _noise(nt, obj, P.get("ripple_scale", 12.0), 1.5, 0.5, loc=(-1300, 850))
        normal = _bump(nt, rp, 1.0, P["ripple"], normal, loc=(-500, 850))
    if P.get("ripple2", 0):
        rp2 = _noise(nt, obj, P.get("ripple2_scale", 90.0), 1.0, 0.5, loc=(-1300, 950))
        normal = _bump(nt, rp2, 1.0, P["ripple2"], normal, loc=(-500, 950))

    # --- greasy haze: broad roughness variation on the reflection only
    if P.get("haze", 0):
        h = _noise(nt, obj, 2.2, 4, 0.5, loc=(-1300, 200))
        w = _window(nt, h, 0.62, 0.72, loc=(-1100, 200))
        gloss_terms.append(_math(nt, 'MULTIPLY', w, P["haze"], loc=(-900, 200)))

    # --- fingerprints: fine ridge loops inside a few soft patches. Reflection-only: they haze the
    #     highlight but must not bend the refraction (that reads as engraved lines).
    gloss_normal_extra = None
    if P.get("prints", 0):
        ridges = _window(nt, _noise(nt, obj, 42, 2, 0.35, loc=(-1300, -50)), 0.485, 0.515, loc=(-1100, -50))
        patch = _window(nt, _noise(nt, obj, 2.8, 2, 0.5, loc=(-1300, -250)), 0.58, 0.74, loc=(-1100, -250))
        pr = _math(nt, 'MULTIPLY', ridges, patch, loc=(-900, -150))
        gloss_terms.append(_math(nt, 'MULTIPLY', pr, 0.06 * P["prints"], loc=(-700, -150)))
        prints_h = pr

    # --- dust specks: sparse occluding motes. Voronoi F1 cells ~1.7 mm; ~0.1% of cells picked at
    #     random by White Noise (no clumping); each mote darkens transmission and roughens the coat.
    dust_h = None
    if P.get("dust", 0):
        v1 = nt.nodes.new("ShaderNodeTexVoronoi"); v1.location = (-1300, -450); v1.feature = 'F1'
        v1.inputs["Scale"].default_value = P.get("dust_scale", 600); v1.inputs["Randomness"].default_value = 1.0
        nt.links.new(obj, v1.inputs["Vector"])
        specks = _window(nt, v1.outputs["Distance"], 0.0, P.get("dust_size", 0.4), loc=(-1100, -450), invert=True)
        wn = nt.nodes.new("ShaderNodeTexWhiteNoise"); wn.location = (-1100, -650); wn.noise_dimensions = '3D'
        nt.links.new(v1.outputs["Position"], wn.inputs["Vector"])
        pick = _math(nt, 'GREATER_THAN', wn.outputs["Value"], 1.0 - P.get("dust_density", 0.001), loc=(-950, -650))
        dust_h = _math(nt, 'MULTIPLY', specks, pick, loc=(-900, -550))
        rough_terms.append(_math(nt, 'MULTIPLY', dust_h, 0.5 * P["dust"], loc=(-700, -550)))

    # --- micro-scratches: Voronoi cell edges = straight hairline segments in random directions,
    #     thinned by a sparse noise mask so they read as isolated scratches, not a mesh.
    if P.get("scratch", 0):
        fams = []
        for k, (scale, mask_scale, w) in enumerate([(4.5, 2.4, 0.0), (7.5, 3.1, 5.7)]):
            vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.location = (-1300, -900 - k*220)
            vo.feature = 'DISTANCE_TO_EDGE'; vo.voronoi_dimensions = '4D'
            vo.inputs["Scale"].default_value = scale; vo.inputs["Randomness"].default_value = 1.0; vo.inputs["W"].default_value = w
            nt.links.new(obj, vo.inputs["Vector"])
            edge = _window(nt, vo.outputs["Distance"], 0.0, P.get("scratch_width", 0.007), loc=(-1100, -900 - k*220), invert=True)
            mk = nt.nodes.new("ShaderNodeTexNoise"); mk.location = (-1300, -1100 - k*220); mk.noise_dimensions = '4D'
            mk.inputs["Scale"].default_value = mask_scale; mk.inputs["Detail"].default_value = 1.0; mk.inputs["W"].default_value = w + 3.1
            nt.links.new(obj, mk.inputs["Vector"])
            sparse = _window(nt, mk.outputs["Fac"], 0.63, 0.68, loc=(-1100, -1100 - k*220))
            fams.append(_math(nt, 'MULTIPLY', edge, sparse, loc=(-850, -1000 - k*220)))
        sc = _math(nt, 'MAXIMUM', fams[0], fams[1], loc=(-700, -1000))
        rough_terms.append(_math(nt, 'MULTIPLY', sc, P["scratch"], loc=(-550, -1000)))
        normal = _bump(nt, sc, P["scratch_bump"], 0.0008, normal, loc=(-400, -1000))

    # --- combine roughness: MAX of terms over a base floor, clamped
    def combine(terms, base, loc):
        cur = None
        for t in terms:
            cur = t if cur is None else _math(nt, 'MAXIMUM', cur, t, loc=loc)
        if cur is None: return None
        cur = _math(nt, 'MAXIMUM', cur, base, loc=(loc[0]+150, loc[1]))
        return _math(nt, 'MINIMUM', cur, 0.4, loc=(loc[0]+300, loc[1]))
    rough_refr = combine(rough_terms, P["rough"], (-300, -300))
    rough_gloss = combine(rough_terms + gloss_terms, P["rough"], (-300, 100))

    def set_rough(node, src):
        node.inputs["Roughness"].default_value = P["rough"]
        if src is not None: nt.links.new(src, node.inputs["Roughness"])
    def set_normal(node, src):
        if src is not None: nt.links.new(src, node.inputs["Normal"])

    # wavelength lobes: colours sum to white; IOR runs low (red) -> high (violet) across the spread
    if P.get("lobes", 3) == 6:
        k = 1/3   # each channel appears in 3 lobes -> sums to 1
        lobes = [((k,0,0,1), -0.5), ((k,k,0,1), -0.3), ((0,k,0,1), -0.1), ((0,k,k,1), 0.1), ((0,0,k,1), 0.3), ((k,0,k,1), 0.5)]
    else:
        lobes = [((1,0,0,1), -0.5), ((0,1,0,1), 0.0), ((0,0,1,1), 0.5)]
    refr = []
    for i, (col, d) in enumerate(lobes):
        r = nt.nodes.new("ShaderNodeBsdfRefraction"); r.location = (200, 300 - i*150)
        r.inputs["Color"].default_value = col; r.inputs["IOR"].default_value = ior + d * sp
        set_rough(r, rough_refr); set_normal(r, normal); refr.append(r)
    acc = refr[0].outputs[0]
    for i, r in enumerate(refr[1:]):
        ad = nt.nodes.new("ShaderNodeAddShader"); ad.location = (450, 200 - i*120)
        nt.links.new(acc, ad.inputs[0]); nt.links.new(r.outputs[0], ad.inputs[1]); acc = ad.outputs[0]
    a2 = type("O", (), {})(); a2.outputs = [acc]
    gl = nt.nodes.new("ShaderNodeBsdfGlossy"); gl.location = (450, -300)
    gnormal = normal
    if P.get("prints", 0): gnormal = _bump(nt, prints_h, 0.03 * P["prints"], 0.0012, normal, loc=(200, -450))
    set_rough(gl, rough_gloss); set_normal(gl, gnormal)
    fr = nt.nodes.new("ShaderNodeFresnel"); fr.location = (450, 350); fr.inputs["IOR"].default_value = ior
    set_normal(fr, normal)
    mix = nt.nodes.new("ShaderNodeMixShader"); mix.location = (700, 0)
    fr_out = fr.outputs[0]
    gi = P.get("gloss_inside", 1.0)
    if gi < 1.0:
        # after the ray has entered the glass, damp the glossy lobe: lamps reflected off the inner
        # surface otherwise appear as detached bright chips floating inside the body
        lp0 = nt.nodes.new("ShaderNodeLightPath"); lp0.location = (450, 600)
        inside = _math(nt, 'MINIMUM', lp0.outputs["Transmission Depth"], 1.0, loc=(600, 600))
        damp = _math(nt, 'MULTIPLY', inside, 1.0 - gi, loc=(600, 500))
        keep = _math(nt, 'SUBTRACT', 1.0, damp, loc=(600, 420))
        fr_out = _math(nt, 'MULTIPLY', fr.outputs[0], keep, loc=(600, 350))
    nt.links.new(fr_out, mix.inputs[0]); nt.links.new(a2.outputs[0], mix.inputs[1]); nt.links.new(gl.outputs[0], mix.inputs[2])
    main = mix.outputs[0]
    if dust_h is not None:
        dd = nt.nodes.new("ShaderNodeBsdfDiffuse"); dd.location = (700, -500)
        dd.inputs["Color"].default_value = (0.0, 0.0, 0.0, 1)   # pure occluder: dirt dulls, never adds
        dm = nt.nodes.new("ShaderNodeMixShader"); dm.location = (850, -150)
        dfac = _math(nt, 'MULTIPLY', dust_h, 0.9 * P["dust"], loc=(700, -650))
        nt.links.new(dfac, dm.inputs[0]); nt.links.new(main, dm.inputs[1]); nt.links.new(dd.outputs[0], dm.inputs[2])
        main = dm.outputs[0]
    # --- coat: broad soft specular over the defects (follows the crown, not the dirt)
    if P.get("coat", 0):
        cg = nt.nodes.new("ShaderNodeBsdfGlossy"); cg.location = (700, -300)
        cg.inputs["Roughness"].default_value = P.get("coat_rough", 0.11)
        if P.get("crown_bump", 0): nt.links.new(crown_normal, cg.inputs["Normal"])
        lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.location = (700, 300); lw.inputs["Blend"].default_value = 0.5
        if P.get("crown_bump", 0): nt.links.new(crown_normal, lw.inputs["Normal"])
        cw = _math(nt, 'MULTIPLY', lw.outputs["Fresnel"], P["coat"], loc=(850, 300))
        cm = nt.nodes.new("ShaderNodeMixShader"); cm.location = (950, 0)
        nt.links.new(cw, cm.inputs[0]); nt.links.new(main, cm.inputs[1]); nt.links.new(cg.outputs[0], cm.inputs[2])
        main = cm.outputs[0]
    # cheap plain glass after a few transmission bounces to cut noise
    glass = nt.nodes.new("ShaderNodeBsdfGlass"); glass.location = (950, -300)
    glass.inputs["IOR"].default_value = ior; glass.inputs["Roughness"].default_value = P["rough"]
    lp = nt.nodes.new("ShaderNodeLightPath"); lp.location = (950, 500)
    gt = _math(nt, 'GREATER_THAN', lp.outputs["Transmission Depth"], 8.5, loc=(1100, 400))
    mix2 = nt.nodes.new("ShaderNodeMixShader"); mix2.location = (1200, 0)
    nt.links.new(gt, mix2.inputs[0]); nt.links.new(main, mix2.inputs[1]); nt.links.new(glass.outputs[0], mix2.inputs[2])
    nt.links.new(mix2.outputs[0], out.inputs["Surface"])
    va = nt.nodes.new("ShaderNodeVolumeAbsorption"); va.location = (1200, -250)
    va.inputs["Color"].default_value = (*P["absorb"], 1); va.inputs["Density"].default_value = P["absorb_density"]
    nt.links.new(va.outputs[0], out.inputs["Volume"])
    return m

def mat_gradient(name, strength, cols, stripes=0):
    m = bpy.data.materials.new("Grad_"+name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = strength
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Location"].default_value = (0.5, 0.5, 0)
    ang = 90.0 if name.startswith("Strip") else P.get("band_angle", 90.0)
    mp.inputs["Rotation"].default_value = (0, 0, math.radians(ang))
    gr = nt.nodes.new("ShaderNodeTexGradient"); gr.gradient_type = 'LINEAR'
    if name.startswith("Strip"):
        # radial falloff along the strip so its reflection has no square ends
        gr.gradient_type = 'SPHERICAL'; mp.inputs["Location"].default_value = (0, 0, 0)
        mp.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
    if stripes and P.get("band_warp", 0):
        # bend the band boundaries so refracted band edges never form straight terraces
        wn = nt.nodes.new("ShaderNodeTexNoise"); wn.inputs["Scale"].default_value = 1.6; wn.inputs["Detail"].default_value = 2
        nt.links.new(tc.outputs["Object"], wn.inputs["Vector"])
        vm = nt.nodes.new("ShaderNodeVectorMath"); vm.operation = 'MULTIPLY_ADD'
        vm.inputs[1].default_value = (P["band_warp"],) * 3
        sub = nt.nodes.new("ShaderNodeVectorMath"); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = (0.5, 0.5, 0.5)
        nt.links.new(wn.outputs["Color"], sub.inputs[0])
        nt.links.new(sub.outputs[0], vm.inputs[0]); nt.links.new(mp.outputs[0], vm.inputs[2])
        warped = vm.outputs[0]
    else:
        warped = mp.outputs[0]
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*cols[0], 1); ramp.color_ramp.elements[1].color = (*cols[-1], 1)
    for i, c in enumerate(cols[1:-1], 1):
        e = ramp.color_ramp.elements.new(i/(len(cols)-1)); e.color = (*c, 1)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(warped, gr.inputs[0])
    if stripes and P.get("panel_debug"):
        # emission = (x+0.5, y+0.5, 0) in panel-local coords so a render tells us which panel region a pixel sees
        sxyz = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sxyz.inputs[0])
        ax = nt.nodes.new("ShaderNodeMath"); ax.operation = 'ADD'; ax.inputs[1].default_value = 0.5; nt.links.new(sxyz.outputs["X"], ax.inputs[0])
        ay = nt.nodes.new("ShaderNodeMath"); ay.operation = 'ADD'; ay.inputs[1].default_value = 0.5; nt.links.new(sxyz.outputs["Y"], ay.inputs[0])
        cmb = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(ax.outputs[0], cmb.inputs[0]); nt.links.new(ay.outputs[0], cmb.inputs[1])
        nt.links.new(cmb.outputs[0], em.inputs["Color"]); em.inputs["Strength"].default_value = 1.0
        nt.links.new(em.outputs[0], out.inputs["Surface"]); return m
    hole_mask = None
    for (hu, hv, hr) in (P.get("panel_holes", []) if stripes else []):
        # soft dark disc: kills the panel region a corner prism images into the black
        hm = nt.nodes.new("ShaderNodeMapping"); hm.inputs["Location"].default_value = (0.5 - hu, 0.5 - hv, 0)
        nt.links.new(tc.outputs["Object"], hm.inputs["Vector"])
        hg = nt.nodes.new("ShaderNodeTexGradient"); hg.gradient_type = 'SPHERICAL'; nt.links.new(hm.outputs[0], hg.inputs[0])
        hmr = nt.nodes.new("ShaderNodeMapRange"); hmr.interpolation_type = 'SMOOTHSTEP'
        hmr.inputs["From Min"].default_value = 1.0 - hr; hmr.inputs["From Max"].default_value = 1.0 - hr * 0.4
        hmr.inputs["To Min"].default_value = 1.0; hmr.inputs["To Max"].default_value = 0.0
        nt.links.new(hg.outputs["Fac"], hmr.inputs["Value"])
        if hole_mask is None: hole_mask = hmr.outputs["Result"]
        else:
            mm = nt.nodes.new("ShaderNodeMath"); mm.operation = 'MULTIPLY'
            nt.links.new(hole_mask, mm.inputs[0]); nt.links.new(hmr.outputs["Result"], mm.inputs[1]); hole_mask = mm.outputs[0]
    nt.links.new(gr.outputs["Fac"], ramp.inputs[0])
    lum = None
    if stripes and P.get("panel_vignette", 0):
        # dim the panel toward its edges so corner prisms don't throw hard-ended bright lozenges
        sg = nt.nodes.new("ShaderNodeTexGradient"); sg.gradient_type = 'SPHERICAL'
        nt.links.new(tc.outputs["Object"], sg.inputs[0])
        vr = nt.nodes.new("ShaderNodeMapRange"); vr.inputs["From Min"].default_value = 0.25; vr.inputs["From Max"].default_value = 1.0
        vr.inputs["To Min"].default_value = 1.0 - P["panel_vignette"]; vr.inputs["To Max"].default_value = 1.0
        nt.links.new(sg.outputs["Fac"], vr.inputs["Value"]); lum = vr.outputs["Result"]
    if hole_mask is not None:
        if lum is None: lum = hole_mask
        else:
            hmul = nt.nodes.new("ShaderNodeMath"); hmul.operation = 'MULTIPLY'
            nt.links.new(lum, hmul.inputs[0]); nt.links.new(hole_mask, hmul.inputs[1]); lum = hmul.outputs[0]
    if stripes and P.get("panel_noise", 0):
        # gentle luminance texture so refracted fields have internal falloff instead of flat poster fills
        ln = nt.nodes.new("ShaderNodeTexNoise"); ln.inputs["Scale"].default_value = 0.9; ln.inputs["Detail"].default_value = 3
        nt.links.new(tc.outputs["Object"], ln.inputs["Vector"])
        lr = nt.nodes.new("ShaderNodeMapRange"); lr.inputs["To Min"].default_value = 1 - P["panel_noise"]; lr.inputs["To Max"].default_value = 1 + P["panel_noise"]
        nt.links.new(ln.outputs["Fac"], lr.inputs["Value"])
        if lum is not None:
            lmul = nt.nodes.new("ShaderNodeMath"); lmul.operation = 'MULTIPLY'
            nt.links.new(lum, lmul.inputs[0]); nt.links.new(lr.outputs["Result"], lmul.inputs[1]); lum = lmul.outputs[0]
        else:
            lum = lr.outputs["Result"]
    if stripes:
        # each band is a full spectral ramp across its own width: t = fract(fac*n)/duty, masked to the band
        mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = stripes
        fr = nt.nodes.new("ShaderNodeMath"); fr.operation = 'FRACT'
        nt.links.new(gr.outputs["Fac"], mul.inputs[0]); nt.links.new(mul.outputs[0], fr.inputs[0])
        mask = nt.nodes.new("ShaderNodeMapRange"); mask.interpolation_type = 'SMOOTHSTEP'
        mask.inputs["From Min"].default_value = P["stripe_duty"] - P["stripe_soft"]
        mask.inputs["From Max"].default_value = P["stripe_duty"] + P["stripe_soft"]
        mask.inputs["To Min"].default_value = 1.0; mask.inputs["To Max"].default_value = 0.0
        nt.links.new(fr.outputs[0], mask.inputs["Value"])
        tdiv = nt.nodes.new("ShaderNodeMath"); tdiv.operation = 'DIVIDE'; tdiv.inputs[1].default_value = P["stripe_duty"]
        nt.links.new(fr.outputs[0], tdiv.inputs[0])
        spec = nt.nodes.new("ShaderNodeValToRGB")
        cr = spec.color_ramp; cr.interpolation = P.get('spec_interp', 'B_SPLINE')
        stops = P["spectrum"]
        cr.elements[0].position = 0.0; cr.elements[0].color = (*stops[0], 1)
        cr.elements[1].position = 1.0; cr.elements[1].color = (*stops[-1], 1)
        for i, c in enumerate(stops[1:-1], 1):
            e = cr.elements.new(i/(len(stops)-1)); e.color = (*c, 1)
        nt.links.new(tdiv.outputs[0], spec.inputs[0])
        spec_out = spec.outputs["Color"]
        if P.get("rail", 0):
            # hot white rail down the centre of each band: bevels map it to a thin bright line with a dark channel beside it
            dv = nt.nodes.new("ShaderNodeMath"); dv.operation = 'SUBTRACT'; dv.inputs[1].default_value = 0.5
            nt.links.new(tdiv.outputs[0], dv.inputs[0])
            sq = nt.nodes.new("ShaderNodeMath"); sq.operation = 'MULTIPLY'
            nt.links.new(dv.outputs[0], sq.inputs[0]); nt.links.new(dv.outputs[0], sq.inputs[1])
            ex = nt.nodes.new("ShaderNodeMath"); ex.operation = 'MULTIPLY'; ex.inputs[1].default_value = -1.0 / (2 * P["rail_width"] ** 2)
            nt.links.new(sq.outputs[0], ex.inputs[0])
            ga = nt.nodes.new("ShaderNodeMath"); ga.operation = 'EXPONENT'
            nt.links.new(ex.outputs[0], ga.inputs[0])
            gm = nt.nodes.new("ShaderNodeMath"); gm.operation = 'MULTIPLY'; gm.inputs[1].default_value = P["rail"]
            nt.links.new(ga.outputs[0], gm.inputs[0])
            radd = nt.nodes.new("ShaderNodeMix"); radd.data_type = 'RGBA'; radd.blend_type = 'ADD'; radd.inputs[0].default_value = 1.0
            nt.links.new(spec_out, radd.inputs[6]); nt.links.new(gm.outputs[0], radd.inputs[7])
            spec_out = radd.outputs[2]
        # multiply by the panel's broad tint ramp (warm bottom / cool top) so bands still differ from each other
        tint = nt.nodes.new("ShaderNodeMix"); tint.data_type = 'RGBA'; tint.blend_type = 'MIX'
        tint.inputs[0].default_value = P.get("band_tint_mix", 0.35)
        nt.links.new(spec_out, tint.inputs[6]); nt.links.new(ramp.outputs["Color"], tint.inputs[7])
        mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = 'RGBA'; mixc.blend_type = 'MULTIPLY'
        mixc.inputs[0].default_value = 1.0
        nt.links.new(tint.outputs[2], mixc.inputs[6]); nt.links.new(mask.outputs["Result"], mixc.inputs[7])
        if lum is not None:
            lm = nt.nodes.new("ShaderNodeMix"); lm.data_type = 'RGBA'; lm.blend_type = 'MULTIPLY'; lm.inputs[0].default_value = 1.0
            nt.links.new(mixc.outputs[2], lm.inputs[6]); nt.links.new(lum, lm.inputs[7])
            nt.links.new(lm.outputs[2], em.inputs["Color"])
        else:
            nt.links.new(mixc.outputs[2], em.inputs["Color"])
    else:
        nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m

def mat_floor():
    m = bpy.data.materials.new("Floor"); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.006, 0.006, 0.007, 1)
    b.inputs["Roughness"].default_value = 0.22
    b.inputs["Specular IOR Level"].default_value = 0.5
    return m

# ---------------------------------------------------------------- scene
def build(args):
    wipe()
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    cy = sc.cycles
    cp = bpy.context.preferences.addons['cycles'].preferences
    cp.compute_device_type = 'METAL'; cp.get_devices()
    for d in cp.devices: d.use = (d.type == 'METAL')
    cy.device = 'GPU'
    cy.samples = args.samples; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.005
    cy.use_denoising = True; cy.denoiser = 'OPENIMAGEDENOISE'; cy.denoising_prefilter = 'ACCURATE'
    cy.denoising_use_gpu = True
    cy.max_bounces = 40; cy.transmission_bounces = 32; cy.glossy_bounces = 8; cy.transparent_max_bounces = 16
    cy.caustics_reflective = True; cy.caustics_refractive = True; cy.blur_glossy = 0.35
    cy.sample_clamp_direct = 0; cy.sample_clamp_indirect = 4
    cy.use_light_tree = True
    sc.render.resolution_x, sc.render.resolution_y = P.get("res", (2400, 2400))
    sc.render.resolution_percentage = int(args.scale*100)
    sc.render.film_transparent = False
    if P.get("border"):
        x0, y0, x1, y1 = P["border"]; sc.render.use_border = True; sc.render.use_crop_to_border = True
        sc.render.border_min_x, sc.render.border_min_y, sc.render.border_max_x, sc.render.border_max_y = x0, y0, x1, y1
    vs = sc.view_settings
    try: vs.view_transform = P.get("view", 'AgX'); vs.look = P["look"]
    except Exception as e: print("view:", e)
    vs.exposure = P["exposure"]

    # world: black
    w = bpy.data.worlds.new("Black"); w.use_nodes = True; sc.world = w
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0, 0, 0, 1)

    # logo
    cur, sf = import_logo()
    logo = curve_to_prism(cur, P["depth"], sf)
    bevel(logo, P["bevel"], P["bevel_segs"])
    rm = P.get("remesh_mode", 'VOXEL')
    if rm == 'VOXEL' and P["remesh_voxel"]:
        logo.data.remesh_mode = 'VOXEL'; logo.data.remesh_voxel_size = P["remesh_voxel"]
        logo.data.remesh_voxel_adaptivity = 0.0
        activate(logo); bpy.ops.object.voxel_remesh()
    elif rm == 'QUAD':
        activate(logo)
        bpy.ops.object.quadriflow_remesh(target_faces=P.get("quad_faces", 30000), use_mesh_symmetry=False,
                                         use_preserve_sharp=False, use_preserve_boundary=False, smooth_normals=True, seed=1)
        print("QUADRIFLOW faces", len(logo.data.polygons))
    if P.get("subsurf", 0):
        ss = logo.modifiers.new("Subd", 'SUBSURF'); ss.levels = P["subsurf"]; ss.subdivision_type = 'CATMULL_CLARK'
        activate(logo); bpy.ops.object.modifier_apply(modifier=ss.name)
    if P.get("presmooth", 0):
        ps = logo.modifiers.new("PreSmooth", 'SMOOTH'); ps.factor = 0.5; ps.iterations = P["presmooth"]
        activate(logo); bpy.ops.object.modifier_apply(modifier=ps.name)
    if P["wave_strength"]:
        tex = bpy.data.textures.new("Wave", 'CLOUDS'); tex.noise_scale = P["wave_scale"]; tex.noise_depth = 1
        tex.noise_basis = P.get("wave_basis", 'IMPROVED_PERLIN'); tex.noise_type = 'SOFT_NOISE'
        # weight front/back faces only (|normal.y| high) so the rim/silhouette stays crisp while faces crown
        vg = logo.vertex_groups.new(name="Faces")
        for v in logo.data.vertices:
            rw = P.get("wave_rim", 0.22)
            w = min(1.0, rw + abs(v.normal.y) * (1.0 - rw))   # rims/caps get ~22% so they carry some hue
            if w > 0: vg.add([v.index], w, 'REPLACE')
        d = logo.modifiers.new("Wave", 'DISPLACE'); d.texture = tex; d.strength = P["wave_strength"]; d.mid_level = 0.5
        d.direction = P.get('wave_dir', 'NORMAL'); d.vertex_group = "Faces"
        emp = bpy.data.objects.new("WaveSpace", None); bpy.context.scene.collection.objects.link(emp)
        emp.scale = P["wave_stretch"]; emp.rotation_euler = (0, math.radians(P.get("wave_tilt", 0.0)), 0)   # >1 along Z stretches noise along the bar length -> ribbons not islands
        d.texture_coords = 'OBJECT'; d.texture_coords_object = emp
        activate(logo); bpy.ops.object.modifier_apply(modifier=d.name)
        sm = logo.modifiers.new("Smooth", 'SMOOTH'); sm.factor = 0.8; sm.iterations = P.get("smooth_iters", 6)
        bpy.ops.object.modifier_apply(modifier=sm.name)
        bpy.ops.object.shade_smooth()
    logo.data.materials.append(mat_dispersive())
    logo.rotation_euler = Euler([math.radians(a) for a in P["tilt"]])
    logo.cycles.is_caustics_caster = True
    print("LOGO dims", tuple(round(v, 3) for v in logo.dimensions), "verts", len(logo.data.vertices))

    if P["floor"]:
        bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, P["floor_z"]))
        fl = bpy.context.active_object; fl.name = "Floor"
        fl.data.materials.append(mat_floor())
        fl.cycles.is_caustics_receiver = True

    # lights
    for li in P["lights"]:
        name, loc, tgt, size, power, spread, kelvin = li[:7]; through = li[7] if len(li) > 7 else False
        ld = bpy.data.lights.new(name, 'AREA'); ld.shape = 'RECTANGLE'
        ld.size, ld.size_y = size; ld.energy = power; ld.spread = math.radians(spread)
        ld.use_temperature = True; ld.temperature = kelvin; ld.diffuse_factor = P["light_diffuse"]
        ld.cycles.is_caustics_light = True
        lo = bpy.data.objects.new(name, ld); sc.collection.objects.link(lo)
        lo.location = loc; look_at(lo, tgt)
        lo.visible_transmission = through   # False: lamp never images through the glass (kills internal ghost reflections)
        # (kickers stay glossy-visible: the rim hairline is an internal-reflection path)

    for pan in P.get("panels", []):
        name, loc, tgt, size, strength, cols, stripes = pan[:7]; mode = pan[7] if len(pan) > 7 else "both"
        bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
        pl = bpy.context.active_object; pl.name = name; pl.scale = (size[0], size[1], 1)
        look_at(pl, tgt); pl.rotation_euler.rotate_axis('Z', 0)
        # plane normal is +Z; look_at points -Z at target, so flip to face the target
        pl.rotation_euler = (Vector(tgt) - pl.location).to_track_quat('Z', 'Y').to_euler()
        pl.data.materials.append(mat_gradient(name, strength, cols, stripes))
        pl.visible_camera = False; pl.visible_shadow = False; pl.visible_diffuse = False
        if mode == "reflect": pl.visible_transmission = False   # seen in reflections only, never through the glass
        if mode == "refract": pl.visible_glossy = False
    # camera
    cd = bpy.data.cameras.new("Cam"); cd.lens = P["cam_lens"]; cd.sensor_width = 36
    cd.dof.use_dof = True; cd.dof.aperture_fstop = P["cam_fstop"]
    cd.dof.focus_distance = P["cam_dist"] - P.get("focus_offset", 0.0)   # focus on the front face, let the rear soften
    cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cam.location = (0.3 + P.get("cam_dx", 0.0), -P["cam_dist"], P["cam_h"]); look_at(cam, (P.get("cam_dx", 0.0), 0, P.get("cam_dz", 0.0)))

    compositor(sc)
    return sc

def compositor(sc):
    C = P.get("comp", {})
    try:
        ng = bpy.data.node_groups.new("Comp", "CompositorNodeTree")
        sc.compositing_node_group = ng
        def node(t, x, **kw):
            n = ng.nodes.new(t); n.location = (x, 0)
            for k, v in kw.items():
                for s_ in n.inputs:
                    if s_.name == k:
                        try: s_.default_value = v
                        except Exception as e: print("comp set", t, k, e)
            return n
        x = 0
        rl = node("CompositorNodeRLayers", x); img = rl.outputs["Image"]; x += 300
        if C.get("glow", 0):
            g = node("CompositorNodeGlare", x, Type='Fog Glow', Quality='High', Threshold=C.get("glow_thr", 1.0),
                     Strength=C["glow"], Size=C.get("glow_size", 0.6), Smoothness=0.15); x += 300
            ng.links.new(img, g.inputs["Image"]); img = g.outputs["Image"]
        if C.get("veil", 0):
            g = node("CompositorNodeGlare", x, Type='Fog Glow', Quality='High', Threshold=2.5,
                     Strength=C["veil"], Size=0.95, Smoothness=0.3); x += 300
            ng.links.new(img, g.inputs["Image"]); img = g.outputs["Image"]
        if C.get("streaks", 0):
            g = node("CompositorNodeGlare", x, Type='Streaks', Quality='High', Threshold=C.get("streak_thr", 1.5),
                     Strength=C["streaks"], Streaks=4, Iterations=3, Fade=0.9)
            g.inputs["Streaks Angle"].default_value = math.radians(12); x += 300
            ng.links.new(img, g.inputs["Image"]); img = g.outputs["Image"]
        if C.get("chroma", 0):
            ld = node("CompositorNodeLensdist", x, Dispersion=C["chroma"], Distortion=C.get("distort", 0.0)); x += 300
            ng.links.new(img, ld.inputs["Image"]); img = ld.outputs["Image"]
        if C.get("vignette", 0):
            em = node("CompositorNodeEllipseMask", x, Operation='Add')
            em.inputs["Size"].default_value = C.get("vig_size", (0.86, 0.86))
            bl = node("CompositorNodeBlur", x+150, Type='Fast Gaussian')
            px = int(P.get("res", (2400, 2400))[0] * sc.render.resolution_percentage / 100 * C.get("vig_blur", 0.16))
            bl.inputs["Size"].default_value = (px, px)
            try: bl.inputs["Extend Bounds"].default_value = True
            except Exception: pass
            ng.links.new(em.outputs["Mask"], bl.inputs["Image"])
            mixv = node("ShaderNodeMix", x+300); mixv.data_type = 'RGBA'; mixv.blend_type = 'MULTIPLY'
            mixv.inputs[0].default_value = C["vignette"]
            ng.links.new(img, mixv.inputs[6]); ng.links.new(bl.outputs["Image"], mixv.inputs[7])
            img = mixv.outputs[2]; x += 500
        if C.get("lift"):
            cb = node("CompositorNodeColorBalance", x, Type='Lift/Gamma/Gain'); x += 300
            for s_ in cb.inputs:
                if s_.name == "Lift" and hasattr(s_.default_value, "__len__"): s_.default_value = (*C["lift"], 1.0)
                if s_.name == "Gain" and hasattr(s_.default_value, "__len__") and C.get("gain"): s_.default_value = (*C["gain"], 1.0)
                if s_.name == "Gamma" and hasattr(s_.default_value, "__len__") and C.get("gamma"): s_.default_value = (*C["gamma"], 1.0)
            ng.links.new(img, cb.inputs["Image"]); img = cb.outputs["Image"]
        if C.get("scurve", 0):
            cv = node("CompositorNodeCurveRGB", x); x += 300
            c = cv.mapping.curves[3]; k = C["scurve"]
            c.points.new(0.26, 0.26 - k); c.points.new(0.74, 0.74 + k); cv.mapping.update()
            ng.links.new(img, cv.inputs["Image"]); img = cv.outputs["Image"]
        if C.get("sat", 0):
            hs = node("CompositorNodeHueSat", x, Saturation=C["sat"]); x += 300
            ng.links.new(img, hs.inputs["Image"]); img = hs.outputs["Image"]
        if C.get("grain", 0):
            ic = node("CompositorNodeImageCoordinates", x); ng.links.new(rl.outputs["Image"], ic.inputs["Image"])
            wn = node("ShaderNodeTexWhiteNoise", x+150); wn.noise_dimensions = '2D'
            ng.links.new(ic.outputs["Pixel"], wn.inputs["Vector"])
            # centre the noise on 0 and add: img + (n-0.5)*grain
            sub = node("ShaderNodeMath", x+300); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = 0.5
            ng.links.new(wn.outputs["Value"], sub.inputs[0])
            mul = node("ShaderNodeMath", x+450); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = C["grain"]
            ng.links.new(sub.outputs[0], mul.inputs[0])
            cc = node("ShaderNodeCombineColor", x+550) if False else None
            add = node("ShaderNodeMix", x+600); add.data_type = 'RGBA'; add.blend_type = 'ADD'
            add.inputs[0].default_value = 1.0
            # RGBA sockets are A=inputs[6], B=inputs[7], Result=outputs[2]
            ng.links.new(img, add.inputs[6]); ng.links.new(mul.outputs[0], add.inputs[7])
            img = add.outputs[2]; x += 800
        ng.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
        outn = ng.nodes.new("NodeGroupOutput"); outn.location = (x, 0)
        ng.links.new(img, outn.inputs["Image"])
        sc.render.use_compositing = True
    except Exception as e:
        import traceback; traceback.print_exc()

# ---------------------------------------------------------------- main
if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "renders", "test.png"))
    ap.add_argument("--samples", type=int, default=256)
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--save", default="")
    ap.add_argument("--norender", action="store_true")
    ap.add_argument("--set", action="append", default=[], help="key=value overrides for P")
    args = ap.parse_args(argv)
    for kv in args.set:
        k, v = kv.split("=", 1)
        if k.startswith("comp."):
            P["comp"][k[5:]] = eval(v)
        elif k == "stripes":
            P["panels"][0] = P["panels"][0][:-1] + (int(v),)
        else:
            P[k] = eval(v)
    sc = build(args)
    if args.save:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(args.save))
    if not args.norender:
        sc.render.filepath = os.path.abspath(args.out)
        sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_depth = '16'
        bpy.ops.render.render(write_still=True)
        print("WROTE", sc.render.filepath)
