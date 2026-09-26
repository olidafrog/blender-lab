"""Wonder logo as dispersive perspex on black — build + render.

Run:  blender -b -P scripts/build.py -- --out renders/v01.png --samples 256 --scale 0.5
Everything tunable is in P (params). Blender 5.2 API — sockets addressed by name
except Math/Mix/MixShader (see notes in wonder-logo-exploration/docs).
"""
import bpy, bmesh, math, sys, os, argparse
from mathutils import Euler, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comp_nodes import COMP_P, build_comp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.path.join(ROOT, "assets", "logo.svg")

# ---------------------------------------------------------------- params
P_STRIPES = 3
P = dict(
    logo_w=2.0,            # metres across
    depth=0.42,            # slab thickness
    bevel=0.15, bevel_segs=16,
    remesh_voxel=0.012, wave_strength=0.36, wave_scale=1.05,   # pillow/wave on faces so refraction smears into bands
    ior=1.49, spread=0.30, scratch=0.10, scratch_bump=0.025,  # RGB IOR spread (exaggerated for style)
    rough=0.0,
    absorb=(0.97, 0.985, 1.0), absorb_density=0.30,
    tilt=(8.0, -4.0, -14.0),  # object rotation deg (x,y,z) for a dynamic pose
    cam_lens=85.0, cam_dist=5.9, cam_fstop=4.0, cam_h=0.0, cam_dx=0.0, cam_dz=0.0,
    floor=False, floor_z=-1.9,
    lights=[  # name, loc, target, size(x,y), power, spread_deg, kelvin
        ("Key_strip",  (-3.0, -1.2, 2.8), (0, 0, 0), (0.20, 6.0), 1400, 45, 9500),
        ("Rim_warm",   ( 3.2,  1.6, 1.6), (0, 0, 0), (0.16, 5.0), 900, 35, 2700),
    ],
    panels=[  # name, loc, target, size(w,h), strength, colours bottom->top, camera-hidden gradient emitters
        ("Grad_back",  (0.0, 5.5, 0.2), (0, 0, 0.2), (7.0, 7.0), 1.25, [(1.0,0.30,0.04),(1.0,1.0,1.0),(0.25,0.70,0.30),(0.03,0.32,1.0)], P_STRIPES),
        ("Grad_front", (-1.5, -4.5, 3.5), (0, 0, 0), (5.0, 2.5), 0.3, [(0.1,0.3,1.0),(1.0,1.0,1.0),(1.0,0.45,0.1)], 3),
    ],
    stripe_duty=0.55, stripe_soft=0.08, band_angle=18.0, band_tint_mix=0.15,
    spectrum=[(1.0,0.02,0.0),(1.0,0.40,0.0),(1.0,0.90,0.05),(0.05,0.95,0.15),(0.0,0.75,1.0),(0.02,0.15,1.0),(0.55,0.05,1.0)], wave_stretch=(1.0, 1.0, 2.6), wave_tilt=15.0,
    exposure=-0.6, look="AgX - Punchy", light_diffuse=0.12,
)
P.update(COMP_P)   # compositor params live in scripts/comp_nodes.py

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
    b.angle_limit = math.radians(30); b.miter_outer = 'MITER_ARC'; b.use_clamp_overlap = True
    b.harden_normals = True
    activate(ob); bpy.ops.object.modifier_apply(modifier=b.name)
    bpy.ops.object.shade_smooth()
    try: bpy.ops.object.shade_auto_smooth(angle=math.radians(40))
    except Exception as e: print("auto smooth:", e)

def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

# ---------------------------------------------------------------- materials
def mat_dispersive():
    m = bpy.data.materials.new("PerspexDispersive"); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (900, 0)
    ior, sp = P["ior"], P["spread"]
    rough_out, bump_out = None, None
    if P.get("scratch"):
        tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-1200, 0)
        fams = []
        for k, (rot, scale) in enumerate([(58, 9.0), (-72, 13.0)]):
            mp = nt.nodes.new("ShaderNodeMapping"); mp.location = (-1000, -k*300)
            mp.inputs["Rotation"].default_value = (math.radians(rot), math.radians(rot*0.4), math.radians(rot*1.7))
            mp.inputs["Scale"].default_value = (1, 1, 240)
            nz = nt.nodes.new("ShaderNodeTexNoise"); nz.location = (-800, -k*300)
            nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 3; nz.inputs["Roughness"].default_value = 0.55
            rp = nt.nodes.new("ShaderNodeValToRGB"); rp.location = (-600, -k*300)
            rp.color_ramp.elements[0].position = 0.655; rp.color_ramp.elements[1].position = 0.69
            nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs[0], nz.inputs["Vector"])
            nt.links.new(nz.outputs["Fac"], rp.inputs[0]); fams.append(rp)
        mx = nt.nodes.new("ShaderNodeMath"); mx.operation = 'MAXIMUM'; mx.location = (-350, 0)
        nt.links.new(fams[0].outputs["Color"], mx.inputs[0]); nt.links.new(fams[1].outputs["Color"], mx.inputs[1])
        rg = nt.nodes.new("ShaderNodeMath"); rg.operation = 'MULTIPLY'; rg.location = (-200, 0)
        rg.inputs[1].default_value = P["scratch"]
        nt.links.new(mx.outputs[0], rg.inputs[0]); rough_out = rg.outputs[0]
        bp = nt.nodes.new("ShaderNodeBump"); bp.location = (-200, -250)
        bp.inputs["Strength"].default_value = P["scratch_bump"]; bp.inputs["Distance"].default_value = 0.02
        nt.links.new(mx.outputs[0], bp.inputs["Height"]); bump_out = bp.outputs["Normal"]
    refr = []
    for i, (col, d) in enumerate([((1,0,0,1), -sp/2), ((0,1,0,1), 0.0), ((0,0,1,1), sp/2)]):
        r = nt.nodes.new("ShaderNodeBsdfRefraction"); r.location = (0, 200 - i*180)
        r.inputs["Color"].default_value = col
        r.inputs["IOR"].default_value = ior + d
        r.inputs["Roughness"].default_value = P["rough"]
        if rough_out: nt.links.new(rough_out, r.inputs["Roughness"])
        if bump_out: nt.links.new(bump_out, r.inputs["Normal"])
        refr.append(r)
    a1 = nt.nodes.new("ShaderNodeAddShader"); a1.location = (250, 150)
    a2 = nt.nodes.new("ShaderNodeAddShader"); a2.location = (250, -50)
    nt.links.new(refr[0].outputs[0], a1.inputs[0]); nt.links.new(refr[1].outputs[0], a1.inputs[1])
    nt.links.new(a1.outputs[0], a2.inputs[0]); nt.links.new(refr[2].outputs[0], a2.inputs[1])
    # reflection lobe, Fresnel weighted
    gl = nt.nodes.new("ShaderNodeBsdfGlossy"); gl.location = (250, -300)
    gl.inputs["Roughness"].default_value = P["rough"]
    if rough_out: nt.links.new(rough_out, gl.inputs["Roughness"])
    if bump_out: nt.links.new(bump_out, gl.inputs["Normal"])
    fr = nt.nodes.new("ShaderNodeFresnel"); fr.location = (250, 350)
    fr.inputs["IOR"].default_value = ior
    mix = nt.nodes.new("ShaderNodeMixShader"); mix.location = (500, 0)
    nt.links.new(fr.outputs[0], mix.inputs[0])
    nt.links.new(a2.outputs[0], mix.inputs[1])   # fac 0 -> refraction
    nt.links.new(gl.outputs[0], mix.inputs[2])   # fac 1 -> reflection
    # cheap plain glass after a few transmission bounces to cut noise
    glass = nt.nodes.new("ShaderNodeBsdfGlass"); glass.location = (500, -300)
    glass.inputs["IOR"].default_value = ior; glass.inputs["Roughness"].default_value = P["rough"]
    lp = nt.nodes.new("ShaderNodeLightPath"); lp.location = (500, 400)
    gt = nt.nodes.new("ShaderNodeMath"); gt.operation = 'GREATER_THAN'; gt.location = (650, 300)
    gt.inputs[1].default_value = 8.5
    nt.links.new(lp.outputs["Transmission Depth"], gt.inputs[0])
    mix2 = nt.nodes.new("ShaderNodeMixShader"); mix2.location = (750, 0)
    nt.links.new(gt.outputs[0], mix2.inputs[0])
    nt.links.new(mix.outputs[0], mix2.inputs[1]); nt.links.new(glass.outputs[0], mix2.inputs[2])
    nt.links.new(mix2.outputs[0], out.inputs["Surface"])
    # subtle path-length tint
    va = nt.nodes.new("ShaderNodeVolumeAbsorption"); va.location = (750, -250)
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
    mp.inputs["Rotation"].default_value = (0, 0, math.radians(P.get("band_angle", 90.0)))
    gr = nt.nodes.new("ShaderNodeTexGradient"); gr.gradient_type = 'LINEAR'
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*cols[0], 1); ramp.color_ramp.elements[1].color = (*cols[-1], 1)
    for i, c in enumerate(cols[1:-1], 1):
        e = ramp.color_ramp.elements.new(i/(len(cols)-1)); e.color = (*c, 1)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs[0], gr.inputs[0])
    nt.links.new(gr.outputs["Fac"], ramp.inputs[0])
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
        cr = spec.color_ramp; cr.interpolation = 'EASE'
        stops = P["spectrum"]
        cr.elements[0].position = 0.0; cr.elements[0].color = (*stops[0], 1)
        cr.elements[1].position = 1.0; cr.elements[1].color = (*stops[-1], 1)
        for i, c in enumerate(stops[1:-1], 1):
            e = cr.elements.new(i/(len(stops)-1)); e.color = (*c, 1)
        nt.links.new(tdiv.outputs[0], spec.inputs[0])
        # multiply by the panel's broad tint ramp (warm bottom / cool top) so bands still differ from each other
        tint = nt.nodes.new("ShaderNodeMix"); tint.data_type = 'RGBA'; tint.blend_type = 'MIX'
        tint.inputs[0].default_value = P.get("band_tint_mix", 0.35)
        nt.links.new(spec.outputs["Color"], tint.inputs[6]); nt.links.new(ramp.outputs["Color"], tint.inputs[7])
        mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = 'RGBA'; mixc.blend_type = 'MULTIPLY'
        mixc.inputs[0].default_value = 1.0
        nt.links.new(tint.outputs[2], mixc.inputs[6]); nt.links.new(mask.outputs["Result"], mixc.inputs[7])
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
    cy.max_bounces = 32; cy.transmission_bounces = 24; cy.glossy_bounces = 8; cy.transparent_max_bounces = 16
    cy.caustics_reflective = True; cy.caustics_refractive = True; cy.blur_glossy = 0.35
    cy.sample_clamp_direct = 0; cy.sample_clamp_indirect = 4
    cy.use_light_tree = True
    sc.render.resolution_x, sc.render.resolution_y = P.get("res", (2400, 2400))
    sc.render.resolution_percentage = int(args.scale*100)
    sc.render.film_transparent = False
    vs = sc.view_settings
    try: vs.view_transform = 'AgX'; vs.look = P["look"]
    except Exception as e: print("view:", e)
    vs.exposure = P["exposure"]

    # world: black
    w = bpy.data.worlds.new("Black"); w.use_nodes = True; sc.world = w
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0, 0, 0, 1)

    # logo
    cur, sf = import_logo()
    logo = curve_to_prism(cur, P["depth"], sf)
    bevel(logo, P["bevel"], P["bevel_segs"])
    if P["remesh_voxel"]:
        logo.data.remesh_mode = 'VOXEL'; logo.data.remesh_voxel_size = P["remesh_voxel"]
        logo.data.remesh_voxel_adaptivity = 0.0
        activate(logo); bpy.ops.object.voxel_remesh()
    if P["wave_strength"]:
        tex = bpy.data.textures.new("Wave", 'CLOUDS'); tex.noise_scale = P["wave_scale"]; tex.noise_depth = 1
        # weight front/back faces only (|normal.y| high) so the rim/silhouette stays crisp while faces crown
        vg = logo.vertex_groups.new(name="Faces")
        for v in logo.data.vertices:
            w = min(1.0, 0.22 + abs(v.normal.y) * 0.78)   # rims/caps get ~22% so they carry some hue
            if w > 0: vg.add([v.index], w, 'REPLACE')
        d = logo.modifiers.new("Wave", 'DISPLACE'); d.texture = tex; d.strength = P["wave_strength"]; d.mid_level = 0.5
        d.direction = P.get('wave_dir', 'NORMAL'); d.vertex_group = "Faces"
        emp = bpy.data.objects.new("WaveSpace", None); bpy.context.scene.collection.objects.link(emp)
        emp.scale = P["wave_stretch"]; emp.rotation_euler = (0, math.radians(P.get("wave_tilt", 0.0)), 0)   # >1 along Z stretches noise along the bar length -> ribbons not islands
        d.texture_coords = 'OBJECT'; d.texture_coords_object = emp
        activate(logo); bpy.ops.object.modifier_apply(modifier=d.name)
        sm = logo.modifiers.new("Smooth", 'SMOOTH'); sm.factor = 0.8; sm.iterations = 6
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
    for name, loc, tgt, size, power, spread, kelvin in P["lights"]:
        ld = bpy.data.lights.new(name, 'AREA'); ld.shape = 'RECTANGLE'
        ld.size, ld.size_y = size; ld.energy = power; ld.spread = math.radians(spread)
        ld.use_temperature = True; ld.temperature = kelvin; ld.diffuse_factor = P["light_diffuse"]
        ld.cycles.is_caustics_light = True
        lo = bpy.data.objects.new(name, ld); sc.collection.objects.link(lo)
        lo.location = loc; look_at(lo, tgt)

    for name, loc, tgt, size, strength, cols, stripes in P.get("panels", []):
        bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
        pl = bpy.context.active_object; pl.name = name; pl.scale = (size[0], size[1], 1)
        look_at(pl, tgt); pl.rotation_euler.rotate_axis('Z', 0)
        # plane normal is +Z; look_at points -Z at target, so flip to face the target
        pl.rotation_euler = (Vector(tgt) - pl.location).to_track_quat('Z', 'Y').to_euler()
        pl.data.materials.append(mat_gradient(name, strength, cols, stripes))
        pl.visible_camera = False; pl.visible_shadow = False; pl.visible_diffuse = False
    # camera
    cd = bpy.data.cameras.new("Cam"); cd.lens = P["cam_lens"]; cd.sensor_width = 36
    cd.dof.use_dof = True; cd.dof.aperture_fstop = P["cam_fstop"]; cd.dof.focus_object = logo
    cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cam.location = (0.3 + P.get("cam_dx", 0.0), -P["cam_dist"], P["cam_h"]); look_at(cam, (P.get("cam_dx", 0.0), 0, P.get("cam_dz", 0.0)))

    compositor(sc)
    return sc

def compositor(sc):
    ng = bpy.data.node_groups.new("Comp", "CompositorNodeTree")
    sc.compositing_node_group = ng
    rl = ng.nodes.new("CompositorNodeRLayers"); rl.location = (0, 0)
    build_comp(ng, P, rl)
    sc.render.use_compositing = True


def gui_setup(sc):
    """Open the saved .blend straight into Compositing with the backdrop on."""
    try:
        bpy.context.window.workspace = bpy.data.workspaces["Compositing"]
    except Exception:
        pass
    for scr in bpy.data.screens:
        for area in scr.areas:
            if area.type == 'NODE_EDITOR':
                for sp in area.spaces:
                    if sp.type == 'NODE_EDITOR':
                        sp.tree_type = 'CompositorNodeTree'
                        sp.show_backdrop = True
                        sp.backdrop_zoom = 0.6


# ---------------------------------------------------------------- main
if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "renders", "test.png"))
    ap.add_argument("--samples", type=int, default=256)
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--save", default="")
    ap.add_argument("--norender", action="store_true")
    ap.add_argument("--exr", action="store_true", help="also write a linear pre-comp EXR for scripts/comp.py")
    ap.add_argument("--set", action="append", default=[], help="key=value overrides for P")
    args = ap.parse_args(argv)
    for kv in args.set:
        k, v = kv.split("=", 1)
        if k == "stripes":
            P["panels"][0] = P["panels"][0][:-1] + (int(v),)
        else:
            P[k] = eval(v)
    sc = build(args)
    if args.save:
        gui_setup(sc)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(args.save))
    if not args.norender:
        sc.render.filepath = os.path.abspath(args.out)
        sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_depth = '16'
        bpy.ops.render.render(write_still=True)
        print("WROTE", sc.render.filepath)
        if args.exr:
            # linear, pre-comp beauty pass -> feed scripts/comp.py for instant re-grades
            exr = os.path.splitext(os.path.abspath(args.out))[0] + ".exr"
            sc.render.use_compositing = False
            sc.render.filepath = exr
            sc.render.image_settings.file_format = 'OPEN_EXR'
            sc.render.image_settings.color_mode = 'RGBA'
            sc.render.image_settings.color_depth = '32'
            bpy.ops.render.render(write_still=True)
            sc.render.use_compositing = True
            print("WROTE", exr)
