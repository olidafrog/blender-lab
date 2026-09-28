"""Eclipse glow v2, rise video: the logomark rises out of the horizon like a moonrise, through a
shimmering mirage. Same material and Post as the still (build.py); this adds the horizon, the
animation and the atmosphere. The still's .blend (output/eclipse_logo.blend) is untouched.

    tools/blender.sh experiments/eclipse-glow/scripts/build_rise.py --out v01 --frame 150
        [--scale 0.5] [--samples N] [--set key=value ...] [--save]
    tools/blender.sh experiments/eclipse-glow/scripts/build_rise.py --out v01 --anim [--from 1 --to 288]

--frame N renders one still frame (PNG + raw EXR for the compositor preview).
--anim renders the frame sequence to renders/eclipse_rise_<out>/ (no EXRs); make_video.sh
encodes it with the score.
"""
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as B  # noqa: E402
from comp import use_saved_render  # noqa: E402
from nodes import how_to_tweak  # noqa: E402

NAME = B.NAME = "eclipse_rise"
REF_H = B.REF_H

B.P.update({
    "res_x": 1920, "res_y": 1080,
    "samples": 16,
    "fps": 24,
    "frames": 288,           # 12 s
    "rise_start": 12,        # frame the top first breaks the horizon
    "rise_end": 288,         # frame the logo comes to rest; the ease-out leaves a slow drift before it
    "logo_height": 0.5,      # rested logo height, fraction of frame height
    "rest_gap": 0.07,        # rested gap from horizon to the logo's base, fraction of frame height
    "ground": (3, 2, 2),     # sRGB 0-255, the ground below the horizon
    # Atmosphere (Post inputs)
    "horizon": 26.0,         # % of frame height, from the bottom
    "shimmer": 8.0,          # px at REF_H: heat-haze wobble at the horizon
    "mirage": 1.0,           # strength of the upside-down mirror below the horizon
    "flatten": 0.35,         # vertical squash of the logo near the horizon
    "extinction": 0.8,       # dim + redden near the horizon
    "sky_glow": 0.2,         # warm sky along the horizon
    # Fixed shapes of the atmosphere (fractions of frame height)
    "shimmer_height": 0.035,  # shimmer fades out over this height above the horizon
    "flatten_height": 0.10,
    "extinction_height": 0.22,
    "extinction_tint": (255, 120, 70),  # sRGB, the colour light fades to at the horizon
    "mirage_reach": 0.035,   # only what is within this height of the horizon is mirrored
    "mirage_squash": 3.0,    # mirror is this much shorter than the real thing
    "mirage_shimmer": 2.5,   # the mirror shimmers this much more than the sky
    "sky_glow_height": 0.10,     # the warm sky fades out over this height
    "horizon_line": 0.5,         # thin line at the horizon, relative to the sky glow
    "horizon_line_height": 0.004,
    "ground_glow_depth": 0.015,  # glow reaches this far into the ground
    "sky_glow_color": (255, 105, 45),
    "shimmer_speed": 5.0,    # noise evolution per second
    "shimmer_rise": 0.12,    # frame heights per second the haze layers drift up (hot air rises)
})
P = B.P

def extra():
    """Atmosphere inputs on the Post node. Built after --set is parsed, so overrides reach them."""
    return [
    ("Horizon", "NodeSocketFloat", P["horizon"], 5.0, 60.0),       # % of frame height from the bottom
    ("Shimmer", "NodeSocketFloat", P["shimmer"], 0.0, 30.0),       # px: heat-haze wobble at the horizon
    ("Mirage", "NodeSocketFloat", P["mirage"], 0.0, 1.5),          # upside-down mirror below the horizon
    ("Flatten", "NodeSocketFloat", P["flatten"], 0.0, 1.0),        # squash near the horizon
    ("Extinction", "NodeSocketFloat", P["extinction"], 0.0, 1.0),  # dim and redden near the horizon
    ("Sky Glow", "NodeSocketFloat", P["sky_glow"], 0.0, 2.0),      # warm band along the horizon
    ]


def _frame_h():
    return P["res_y"] * B.parse_args()["scale"]


def _coords(H):
    """(x, y, d): x across the width in frame heights, y up in frame heights, d = y − horizon."""
    N, L, I, m = H.N, H.L, H.I, H.math
    ic = N.new("CompositorNodeImageCoordinates"); L(I["Image"], ic.inputs["Image"])
    sep = N.new("ShaderNodeSeparateXYZ"); L(ic.outputs["Normalized"], sep.inputs[0])
    x = m("MULTIPLY", sep.outputs["X"], P["res_x"] / P["res_y"])
    y = sep.outputs["Y"]
    d = m("SUBTRACT", y, m("MULTIPLY", I["Horizon"], 0.01), label="Height Above Horizon")
    return x, y, d


def pre(H, S):
    """The ground hides everything below the horizon, before any glow is made from it."""
    m, mix = H.math, H.mix
    _, _, d = _coords(H)
    fh = _frame_h()
    sky = m("ADD", m("MULTIPLY", d, fh), 0.5)  # 1 px anti-aliased edge
    sky = m("MINIMUM", m("MAXIMUM", sky, 0.0), 1.0, label="Sky Mask")
    out = dict(S)
    out["Image"] = mix("MIX", B.srgb(*P["ground"]), S["Image"], sky, "Ground")
    for k in ("Coverage Pass", "Halo Pass", "Arc Glow Pass", "Height Pass"):
        out[k] = mix("MULTIPLY", S[k], sky, 1.0, f"{k} × Sky") if k in ("Halo Pass", "Arc Glow Pass") \
            else m("MULTIPLY", S[k], sky)
    H.sky = sky
    return out


def stage(H, col):
    """Atmosphere, after the glows and before bloom: shimmer, flattening, the mirage mirror,
    extinction and the horizon glow. All keyed to d, the height above the horizon."""
    N, L, I, m, mix = H.N, H.L, H.I, H.math, H.mix
    fh = _frame_h()
    x, y, d = _coords(H)
    up = m("MAXIMUM", d, 0.0)
    down = m("MAXIMUM", m("MULTIPLY", d, -1.0), 0.0)

    def fade(v, height):  # exp(−v / height)
        return m("EXPONENT", m("MULTIPLY", v, -1.0 / height))

    # Heat shimmer: 4D noise stretched along x, so the air moves in horizontal layers.
    t = N.new("CompositorNodeSceneTime")
    w = m("MULTIPLY", t.outputs["Seconds"], P["shimmer_speed"])

    drift = m("MULTIPLY", t.outputs["Seconds"], -P["shimmer_rise"])

    def noise(seed, sx, sy):
        v = N.new("ShaderNodeCombineXYZ")
        L(m("MULTIPLY", x, sx), v.inputs["X"]); L(m("MULTIPLY", m("ADD", y, drift), sy), v.inputs["Y"])
        n = N.new("ShaderNodeTexNoise"); n.noise_dimensions = "4D"; n.label = "Shimmer Noise"
        n.inputs["Scale"].default_value = 1.0
        n.inputs["Detail"].default_value = 0.5  # smooth: fine octaves read as video tearing
        L(v.outputs[0], n.inputs["Vector"]); L(m("ADD", w, seed), n.inputs["W"])
        # Fac sits mostly in 0.35–0.65; stretch that to about ±1.
        return m("MINIMUM", m("MAXIMUM", m("MULTIPLY", m("SUBTRACT", n.outputs["Fac"], 0.5), 6.0), -1.0), 1.0)

    amp = m("MULTIPLY", I["Shimmer"], fh / REF_H)  # px at this frame
    # Strong at the horizon, fading up the sky; full strength through the mirror.
    reach = m("MAXIMUM", fade(up, P["shimmer_height"]), m("MULTIPLY", m("SUBTRACT", 1.0, H.sky), P["mirage_shimmer"]))
    amp = m("MULTIPLY", amp, reach, label="Shimmer Strength")
    dx = m("MULTIPLY", noise(0.0, 3.0, 50.0), amp)  # layers ~20 px tall
    dy = m("MULTIPLY", noise(17.0, 2.0, 30.0), m("MULTIPLY", amp, 0.35))
    # Flattening: near the horizon, sample from higher up, squashing the bottom of the logo.
    flat = m("MULTIPLY", m("MULTIPLY", up, fade(up, P["flatten_height"])), I["Flatten"])
    # Mirror below the horizon, squashed: y' = horizon + depth × squash.
    mirror = m("MULTIPLY", down, 1.0 + P["mirage_squash"])
    # Displace samples at (pixel − offset), so "sample higher" is a negative offset.
    dy = m("ADD", dy, m("MULTIPLY", m("ADD", flat, mirror), -fh), label="Vertical Offset (px)")
    vec = N.new("ShaderNodeCombineXYZ"); L(dx, vec.inputs["X"]); L(dy, vec.inputs["Y"])
    disp = N.new("CompositorNodeDisplace"); disp.label = "Mirage Displace"
    disp.inputs["Extension X"].default_value = "Extend"
    disp.inputs["Extension Y"].default_value = "Extend"
    L(col, disp.inputs["Image"]); L(vec.outputs[0], disp.inputs["Displacement"])
    moved = disp.outputs["Image"]

    # Below the horizon: the ground plus a fading mirror; above: the shimmered sky.
    # A real inferior mirage only mirrors what is close to the horizon: fade by the height of the
    # reflected point, so the mirror dies away once the logo's base clears the ground.
    ref = m("MULTIPLY", fade(mirror, P["mirage_reach"]), I["Mirage"], label="Mirror Strength")
    ground = mix("ADD", col, moved, ref, "Add Mirror")
    out = mix("MIX", ground, moved, H.sky, "Sky / Ground")

    # Extinction: light near the horizon (both sides) is dimmer and redder.
    near = m("MULTIPLY", fade(m("ABSOLUTE", d), P["extinction_height"]), I["Extinction"])
    tint = mix("MIX", (1, 1, 1, 1), B.srgb(*P["extinction_tint"]), near, "Extinction Tint")
    out = mix("MULTIPLY", out, tint, 1.0, "Extinction")
    # Horizon glow: a broad warm sky that fades upward, a thin dim line, and a quick falloff
    # into the ground (a hard neon stripe read as a grid line, not air).
    wide = m("MULTIPLY", fade(up, P["sky_glow_height"]), H.sky)
    line = m("MULTIPLY", fade(m("ABSOLUTE", d), P["horizon_line_height"]), P["horizon_line"])
    under = m("MULTIPLY", fade(down, P["ground_glow_depth"]), m("SUBTRACT", 1.0, H.sky))
    band = m("ADD", m("ADD", wide, line), m("MULTIPLY", under, 0.5))
    band = m("MULTIPLY", band, I["Sky Glow"], label="Horizon Glow Amount")
    out = mix("ADD", out, B.srgb(*P["sky_glow_color"]), band, "Horizon Glow")
    return out


def animate(scene, logo):
    """Keyframe the rise on Logo › Location Y. Edit it in the Timeline or Graph Editor."""
    cam = scene.camera
    bpy.context.view_layer.update()
    bb = [logo.matrix_world @ __import__("mathutils").Vector(c) for c in logo.bound_box]
    lo, hi = min(v.y for v in bb), max(v.y for v in bb)
    h_world = hi - lo
    # Camera: rested logo height = logo_height of the frame.
    frame_h_world = h_world / P["logo_height"]
    frame_w_world = frame_h_world * P["res_x"] / P["res_y"]
    cam.data.lens = 36 * cam.location.z / frame_w_world
    horizon_y = (P["horizon"] / 100 - 0.5) * frame_h_world
    y0 = logo.location.y
    rest = horizon_y + P["rest_gap"] * frame_h_world - lo + y0
    start = horizon_y - 0.02 * frame_h_world - hi + y0  # just below the horizon
    below = start - 0.05 * frame_h_world
    for f, v in ((1, below), (P["rise_start"], start), (P["rise_end"], rest)):
        logo.location.y = v
        logo.keyframe_insert("location", index=1, frame=f)
    fc = next(c for c in logo.animation_data.action.layers[0].strips[0].channelbags[0].fcurves) \
        if hasattr(logo.animation_data.action, "layers") else logo.animation_data.action.fcurves[0]
    k = fc.keyframe_points
    k[0].interpolation = "LINEAR"
    k[1].interpolation, k[1].easing = "SINE", "EASE_OUT"  # moving from the first frame, settling slowly
    scene.frame_start, scene.frame_end = 1, P["frames"]
    scene.render.fps = P["fps"]


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    val = lambda k, d: type(d)(argv[argv.index(k) + 1]) if k in argv else d  # noqa: E731
    a = B.parse_args()
    orig_post = B.post
    B.post = lambda fh: orig_post(fh, extra=extra(), pre=pre, stage=stage)
    scene, raw = B.build(a)
    scene.name = "Eclipse Rise"
    logo = bpy.data.objects["Logo"]
    animate(scene, logo)
    scene.render.use_motion_blur = False

    if "--anim" in argv:
        tree = scene.compositing_node_group
        tree.nodes.remove(tree.nodes["Raw EXR"])  # no 60 MB EXR per frame
        seq = B.EXP["renders"] / f"{NAME}_{a['out']}"
        seq.mkdir(exist_ok=True)
        scene.frame_start, scene.frame_end = val("--from", 1), val("--to", P["frames"])
        scene.render.filepath = str(seq) + "/"
        scene.render.image_settings.file_format = "PNG"
        scene.render.use_overwrite = "--overwrite" in argv
        bpy.ops.render.render(animation=True)
        print(f"[out] WROTE {seq}")
    else:
        scene.frame_set(val("--frame", 150))
        png = B.EXP["renders"] / f"{NAME}_{a['out']}.png"
        scene.render.filepath = str(png)
        bpy.ops.render.render(write_still=True)
        print(f"[out] WROTE {png}")
        if a["save"]:
            use_saved_render(scene, raw, B.EXP["output"])
            how_to_tweak(HOW)
            blend = B.EXP["output"] / f"{NAME}.blend"
            bpy.ops.wm.save_as_mainfile(filepath=str(blend))
            bpy.ops.file.make_paths_relative()
            bpy.ops.wm.save_mainfile()
            Path(str(blend) + "1").unlink(missing_ok=True)
            print(f"[out] WROTE {blend}")
    print("ECLIPSE RISE OK")


HOW = B.HOW.replace("ECLIPSE LOGO — how to tweak", "ECLIPSE RISE — how to tweak (video)") + """
RISE (this file only)
  Motion: Logo › Location Y is keyframed (Timeline / Graph Editor). Frame 12 = top breaks the
  horizon, frame 288 = at rest (sine ease-out, so it drifts slowly for the last seconds). Move or retime those keys.
  Atmosphere: Post node, bottom six inputs.
    Horizon      % of frame height from the bottom (the ground hides the logo below it)
    Shimmer      heat-haze wobble at the horizon (px); it moves with the timeline
    Mirage       the upside-down mirror just below the horizon
    Flatten      squash near the horizon, like a low moon
    Extinction   dimmer and redder near the horizon
    Sky Glow     warm band along the horizon
  The Compositing tab previews one saved frame; scrub the timeline to see the shimmer move.
  Before rendering the animation: Source › Use Saved Render off. Output is a PNG sequence;
  the score is music/eclipse_rise_score.wav (see make_video.sh).
"""

if __name__ == "__main__":
    main()
