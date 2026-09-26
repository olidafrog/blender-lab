"""Threshold Orbit — orbital diagram whose ink lines bleed together where they cross.

Lines render into AOVs, not colour. The compositor blurs the "ink" AOV and thresholds it, so
wherever lines meet the summed blur crosses the threshold sooner and the joint fills in like
Photoshop's Threshold on a blurred drawing. Labels and dotted guides go to a "crisp" AOV that
skips the bleed so they stay legible.

    tools/blender.sh experiments/threshold-orbit/scripts/threshold_orbit.py [--still N] [--out NAME]

--still N renders frame N to renders/<out>.png. Default renders the loop to
renders/<out>_frames/ and encodes renders/<out>.mp4. The .blend goes to output/.
"""
import math
import shutil
import subprocess
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from common import enable_gpu, experiment_paths  # noqa: E402

EXP = experiment_paths(__file__)

NAME = "threshold_orbit"

# --- Tunables (px values are at RES) -------------------------------------------------------
RES = 1080
FPS = 30
LOOP_FRAMES = 300            # 10 s seamless loop
ORTHO = 2.5                  # world units across the frame; the globe is 2 units wide
ELEVATION = 14               # camera tilt in degrees; flattens latitudes and inner orbits

LINE_PX = 3.6                # every bleeding line
GRID_INK = 0.9               # grid ink strength vs rings (1.0); lower = thinner grid
MARKER_PX = 9                # marker size
BLEED_PX = 13                # blur radius before the threshold: bigger = fatter joins
THRESHOLD = 0.26             # lower = thicker lines and bigger joins
SOFTNESS = 0.015             # threshold edge width, keeps edges anti-aliased
FAINT = 0.22                 # opacity of the back half of the globe

PAPER = (0.925, 0.918, 0.890)  # sRGB
INK = (0.10, 0.10, 0.10)
FONT = "/System/Library/Fonts/SFNSMono.ttf"

N_MERIDIANS = 6
LATITUDES = (-60, -30, 0, 30, 60)
GLOBE_SPIN = math.radians(360 / (2 * N_MERIDIANS))  # one meridian gap per loop = seamless

# Orbit rings spin in the picture plane. tilt = degrees about screen Y (narrows the ellipse),
# roll = starting angle. spin must be +-0.5 turns per loop: with markers also moving 0.5 turns
# along the ring, the half-turn maps the ellipse and markers back onto themselves.
RINGS = [
    dict(tilt=38, roll=20, radius=1.0, spin=0.5, shape="tri",
         markers=[(0.05, "HIGGS BOSON\nDISCOVERY"), (0.38, "COLLIDER\nPHYSICS"),
                  (0.70, "THE\nSEARCH")]),
    dict(tilt=55, roll=-30, radius=1.0, spin=-0.5, shape="dot",
         markers=[(0.18, "PARTICLE\nDREAMS"), (0.52, "THE\nEXPERIMENT"),
                  (0.84, "QUANTUM\nCHROMODYNAMICS")]),
]
INNER_ORBITS = [(0.62, 1), (0.28, 2)]  # radius, planet turns per loop
LABEL_OFFSET_PX = 46

# --- Helpers ---------------------------------------------------------------------------------
PX = ORTHO / RES


def lin(c):
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


def circle_pts(r=1.0, n=256):
    return [Vector((r * math.cos(t), r * math.sin(t), 0)) for t in
            (2 * math.pi * i / n for i in range(n))]


def link(ob, parent=None):
    bpy.context.scene.collection.objects.link(ob)
    if parent:
        ob.parent = parent
    return ob


def poly_curve(name, pts, width_px, mat, cyclic=True, parent=None):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = width_px * PX / 2
    cu.bevel_resolution = 2
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for p, co in zip(sp.points, pts):
        p.co = (*co, 1)
    sp.use_cyclic_u = cyclic
    cu.materials.append(mat)
    return link(bpy.data.objects.new(name, cu), parent)


def flat_mesh(name, polys, mat, parent=None):
    """polys: list of 2D point lists, built in the XY plane."""
    bm = bmesh.new()
    for poly in polys:
        bm.faces.new([bm.verts.new((x, y, 0)) for x, y in poly])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    return link(bpy.data.objects.new(name, me), parent)


def disc(cx, cy, r, n=20):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n))
            for i in range(n)]


def triangle(r):
    return [(r * math.cos(a), r * math.sin(a)) for a in (0, 2.0944, 4.1888)]


def text(body, size_px, mat, parent, x, y, align_x="CENTER", align_y="CENTER"):
    cu = bpy.data.curves.new("txt", "FONT")
    cu.body = body
    cu.font = bpy.data.fonts.load(FONT, check_existing=True)
    cu.size = size_px * PX
    cu.align_x, cu.align_y = align_x, align_y
    cu.space_line = 0.95
    cu.materials.append(mat)
    ob = link(bpy.data.objects.new("txt_" + body.split("\n")[0], cu), parent)
    ob.location = (x, y, -8)
    return ob


# --- Scene -----------------------------------------------------------------------------------
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
    scene = bpy.context.scene
    enable_gpu(scene)  # Cycles only; Eevee picks the GPU itself, kept for consistency
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 16
    scene.render.resolution_x = scene.render.resolution_y = RES
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, LOOP_FRAMES
    scene.view_settings.view_transform = "Standard"
    scene.world = bpy.data.worlds.new("world")
    return scene


def aov_material(name, mode, view_layer):
    """mode: 'ink' (always bleeds), 'globe' (front bleeds, back faint) or 'crisp'."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0, 0, 0, 1)
    nt.links.new(em.outputs[0], out.inputs["Surface"])

    def aov(aov_name, value):
        n = nt.nodes.new("ShaderNodeOutputAOV")
        n.aov_name = aov_name
        if isinstance(value, float):
            n.inputs["Value"].default_value = value
        else:
            nt.links.new(value, n.inputs["Value"])

    if mode == "globe":
        # Front = surface point faces the camera: dot(position, incoming) > 0.
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        dot = nt.nodes.new("ShaderNodeVectorMath")
        dot.operation = "DOT_PRODUCT"
        nt.links.new(geo.outputs["Position"], dot.inputs[0])
        nt.links.new(geo.outputs["Incoming"], dot.inputs[1])
        front = nt.nodes.new("ShaderNodeMapRange")
        front.inputs[1].default_value, front.inputs[2].default_value = -0.01, 0.01
        nt.links.new(dot.outputs["Value"], front.inputs[0])
        back = nt.nodes.new("ShaderNodeMath")
        back.operation = "SUBTRACT"
        back.inputs[0].default_value = 1.0
        nt.links.new(front.outputs[0], back.inputs[1])
        ink = nt.nodes.new("ShaderNodeMath")
        ink.operation = "MULTIPLY"
        ink.inputs[1].default_value = GRID_INK
        nt.links.new(front.outputs[0], ink.inputs[0])
        aov("ink", ink.outputs[0])
        aov("faint", back.outputs[0])
    else:
        aov(mode, 1.0)
    return mat


def build(scene):
    vl = scene.view_layers[0]
    for n in ("ink", "faint", "crisp"):
        aov = vl.aovs.add()  # before building the compositor, or the sockets are missing
        aov.name, aov.type = n, "VALUE"  # default COLOR reads the node's (black) Color input
    m_ink = aov_material("ink", "ink", vl)
    m_globe = aov_material("globe", "globe", vl)
    m_crisp = aov_material("crisp", "crisp", vl)

    # Camera
    cam = bpy.data.objects.new("camera", bpy.data.cameras.new("camera"))
    link(cam)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = ORTHO
    cam.data.clip_start, cam.data.clip_end = 0.1, 100
    el = math.radians(ELEVATION)
    cam.location = (0, -20 * math.cos(el), 20 * math.sin(el))
    cam.rotation_euler = (math.pi / 2 - el, 0, 0)
    scene.camera = cam
    bpy.context.view_layer.update()
    cam_inv = cam.matrix_world.inverted()

    def to_screen(p):
        v = cam_inv @ p
        return v.x, v.y

    last = LOOP_FRAMES + 1  # key the loop end one frame past the last render frame

    # Globe: meridians + latitudes, spinning by one meridian gap per loop
    globe = link(bpy.data.objects.new("globe", None))
    globe.rotation_euler = (0, 0, 0)
    globe.keyframe_insert("rotation_euler", index=2, frame=1)
    globe.rotation_euler.z = GLOBE_SPIN
    globe.keyframe_insert("rotation_euler", index=2, frame=last)
    for i in range(N_MERIDIANS):
        rot = Matrix.Rotation(math.pi * i / N_MERIDIANS, 3, "Z") @ Matrix.Rotation(
            math.pi / 2, 3, "X")
        poly_curve(f"meridian_{i}", [rot @ p for p in circle_pts()], LINE_PX, m_globe,
                   parent=globe)
    for lat in LATITUDES:
        a = math.radians(lat)
        pts = [p + Vector((0, 0, math.sin(a))) for p in circle_pts(math.cos(a))]
        poly_curve(f"lat_{lat}", pts, LINE_PX, m_globe, parent=globe)

    # Silhouette and ticks live in camera space so they stay round and upright
    poly_curve("silhouette", circle_pts(1.0), LINE_PX, m_ink, parent=cam).location.z = -20
    for ang in range(0, 360, 90):
        d = Vector((math.cos(math.radians(ang)), math.sin(math.radians(ang)), 0))
        t = poly_curve(f"tick_{ang}", [d * 0.97, d * 1.07], LINE_PX, m_ink, cyclic=False,
                       parent=cam)
        t.location.z = -20

    # Inner system: sun, crosshair, two flat orbits with planets
    sun = poly_curve("sun", circle_pts(0.06, 64), LINE_PX, m_ink, parent=cam)
    sun.location.z = -12
    for a, b in (((-0.16, 0), (-0.1, 0)), ((0.1, 0), (0.16, 0)),
                 ((0, 0.1), (0, 0.18)), ((0, -0.1), (0, -0.18))):
        c = poly_curve("cross", [Vector((*a, 0)), Vector((*b, 0))], LINE_PX, m_ink,
                       cyclic=False, parent=cam)
        c.location.z = -12
    poles = flat_mesh("poles", [disc(0, 0.18, MARKER_PX * 0.55 * PX),
                                disc(0, -0.18, MARKER_PX * 0.55 * PX)], m_ink, parent=cam)
    poles.location.z = -12

    planets = []
    for r, turns in INNER_ORBITS:
        poly_curve(f"orbit_{r}", circle_pts(r), LINE_PX, m_ink)
        ob = flat_mesh(f"planet_{r}", [disc(0, 0, MARKER_PX * 0.6 * PX)], m_ink, parent=cam)
        planets.append((ob, r, turns))

    # Orbit rings with markers and labels
    rings = []
    for i, cfg in enumerate(RINGS):
        roll = math.radians(cfg["roll"])
        spin = link(bpy.data.objects.new(f"ring_spin_{i}", None), cam)
        spin.location.z = -20
        spin.rotation_euler.z = roll
        spin.keyframe_insert("rotation_euler", index=2, frame=1)
        spin.rotation_euler.z = roll + 2 * math.pi * cfg["spin"]
        spin.keyframe_insert("rotation_euler", index=2, frame=last)
        tilt = Matrix.Rotation(math.radians(cfg["tilt"]), 3, "Y")
        ring = poly_curve(f"ring_{i}", circle_pts(cfg["radius"]), LINE_PX, m_ink, parent=spin)
        ring.rotation_euler = tilt.to_euler()
        for phase, label in cfg["markers"]:
            shape = triangle(MARKER_PX * PX) if cfg["shape"] == "tri" else disc(
                0, 0, MARKER_PX * 0.6 * PX)
            mk = flat_mesh(f"marker_{label.split()[0]}", [shape], m_ink, parent=cam)
            lb = text(label, 18, m_crisp, cam, 0, 0)
            rings.append((mk, lb, cfg, tilt, phase))

    # Per-frame keys for everything that is computed in screen space
    for f in range(1, last + 1):
        t = (f - 1) / LOOP_FRAMES
        for ob, r, turns in planets:
            a = 2 * math.pi * (turns * t + r)
            x, y = to_screen(Vector((r * math.cos(a), r * math.sin(a), 0)))
            ob.location = (x, y, -10)
            ob.keyframe_insert("location", frame=f)
        for mk, lb, cfg, tilt, phase in rings:
            spin = Matrix.Rotation(math.radians(cfg["roll"]) + 2 * math.pi * cfg["spin"] * t, 3,
                                   "Z")
            a = 2 * math.pi * (phase + t * cfg["spin"])

            def ring_pt(a):
                return spin @ tilt @ Vector((cfg["radius"] * math.cos(a),
                                             cfg["radius"] * math.sin(a), 0))
            x, y = ring_pt(a).xy  # already in camera space
            x2, y2 = ring_pt(a + 0.01 * math.copysign(1, cfg["spin"])).xy
            mk.location = (x, y, -10)
            mk.rotation_euler = (0, 0, math.atan2(y2 - y, x2 - x))
            mk.keyframe_insert("location", frame=f)
            mk.keyframe_insert("rotation_euler", frame=f)
            d = Vector((x, y)).normalized() if (x or y) else Vector((1, 0))
            off = LABEL_OFFSET_PX * PX
            edge = ORTHO / 2 - 90 * PX
            lb.location = (max(-edge, min(edge, x + d.x * off)), y + d.y * off * 0.7, -8)
            lb.keyframe_insert("location", frame=f)

    # Dotted guides (crisp): diagonals and the equator line
    dots = []
    for ang in (45, 135, 225, 315, 0, 180):
        d = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
        for k in range(8, 48):
            s = k / 48 * (1.0 if ang % 90 else 0.95)
            dots.append(disc(d[0] * s, d[1] * s, 1.6 * PX, 8))
    flat_mesh("dotted", dots, m_crisp, parent=cam).location.z = -9

    # Frame furniture
    h = ORTHO / 2 - 40 * PX
    text("THRESHOLD ORBIT", 16, m_crisp, cam, -h, h, "LEFT", "TOP")
    text("II IIIII", 16, m_crisp, cam, h, h, "RIGHT", "TOP")
    text("TO-260926", 16, m_crisp, cam, h, -h, "RIGHT", "BOTTOM")
    bars = [(-h, -h, 60, 8), (-h + 60 * PX, -h + 8 * PX, 60, 8), (-h + 180 * PX, -h, 60, 8),
            (-h + 240 * PX, -h + 8 * PX, 60, 3)]
    flat_mesh("bars", [[(x, y), (x + w * PX, y), (x + w * PX, y + hh * PX), (x, y + hh * PX)]
                       for x, y, w, hh in bars], m_crisp, parent=cam).location.z = -8


# --- Compositor: blur -> threshold on ink, crisp and faint laid on top -----------------------
def compositor(scene):
    ng = bpy.data.node_groups.new(NAME, "CompositorNodeTree")
    scene.compositing_node_group = ng
    ng.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    N, L = ng.nodes, ng.links
    rl = N.new("CompositorNodeRLayers")

    blur = N.new("CompositorNodeBlur")
    blur.label = "Bleed"
    blur.inputs["Size"].default_value = (BLEED_PX, BLEED_PX)
    blur.inputs["Type"].default_value = "Gaussian"
    L.new(rl.outputs["ink"], blur.inputs["Image"])

    thr = N.new("ShaderNodeMapRange")
    thr.label = "Threshold"
    thr.inputs[1].default_value = THRESHOLD - SOFTNESS
    thr.inputs[2].default_value = THRESHOLD + SOFTNESS
    L.new(blur.outputs[0], thr.inputs[0])

    faint = N.new("ShaderNodeMath")
    faint.operation = "MULTIPLY"
    faint.inputs[1].default_value = FAINT
    L.new(rl.outputs["faint"], faint.inputs[0])

    def maximum(a, b):
        n = N.new("ShaderNodeMath")
        n.operation = "MAXIMUM"
        L.new(a, n.inputs[0])
        L.new(b, n.inputs[1])
        return n.outputs[0]

    cover = maximum(maximum(thr.outputs[0], rl.outputs["crisp"]), faint.outputs[0])

    mix = N.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs[6].default_value = (*lin(PAPER), 1)
    mix.inputs[7].default_value = (*lin(INK), 1)
    L.new(cover, mix.inputs[0])
    out = N.new("NodeGroupOutput")
    L.new(mix.outputs[2], out.inputs[0])


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    still = int(argv[argv.index("--still") + 1]) if "--still" in argv else None
    tag = argv[argv.index("--out") + 1] if "--out" in argv else "wip"

    scene = reset()
    build(scene)
    compositor(scene)
    bpy.ops.wm.save_as_mainfile(filepath=str(EXP["output"] / f"{NAME}.blend"))

    if still is not None:
        scene.frame_set(still)
        scene.render.filepath = str(EXP["renders"] / f"{tag}.png")
        bpy.ops.render.render(write_still=True)
        return

    frames = EXP["renders"] / f"{tag}_frames"
    shutil.rmtree(frames, ignore_errors=True)
    scene.render.filepath = str(frames / "frame_")
    bpy.ops.render.render(animation=True)
    ffmpeg = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
    mp4 = EXP["renders"] / f"{tag}.mp4"
    subprocess.run([ffmpeg, "-v", "error", "-y", "-framerate", str(FPS), "-i",
                    str(frames / "frame_%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "16", str(mp4)], check=True)
    print(f"Saved {mp4}")


main()
