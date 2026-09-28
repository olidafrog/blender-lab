"""Eclipse glow v3, sunrise video: the rise (build_rise.py) reworked as a sunrise over hot water.
Same logo, material, motion and Post; a new atmosphere stage (see RESEARCH.md, "Sunrise video"):
the logo meets its inverted mirage image at a vanishing line above the sea horizon, the meeting
point is a blown-out, blooming, grainy highlight, a gap opens as it lifts off, and the heat haze
blurs as well as shimmers. build_rise.py and its renders are untouched.

    tools/blender.sh experiments/eclipse-glow/scripts/build_sunrise.py --out v01 --frame 150
        [--scale 0.5] [--samples N] [--set key=value ...] [--save]
    tools/blender.sh experiments/eclipse-glow/scripts/build_sunrise.py --out v01 --anim [--from 1 --to 288]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as B  # noqa: E402
import build_rise as R  # noqa: E402

R.NAME = B.NAME = "eclipse_sunrise"
REF_H = B.REF_H

B.P.update({
    "shimmer": 12.0,          # v07 rise: 8
    "extinction": 0.45,       # was 0.8: the contact must be the brightest point, not the dimmest
    "flatten": 0.2,
    "shimmer_height": 0.11,   # shimmer fades over this height (v07: 0.035)
    "mirage_reach": 0.12,     # mirror fades by the reflected point's height (v07: 0.035); longer, so the gap shows
    "mirror_hold": 0.05,          # coverage within this height of the line keeps the mirror alive
    "mirror_feather": 0.8,        # mirror falls off over this × the band depth
    "mirror_tint": (255, 238, 220),
    "mirror_presence_px": (8, 90),
    "mirror_presence_gain": 3.0,
    # New atmosphere (Post inputs)
    "haze": 1.0,              # heat-haze blur near the ground
    "contact": 1.0,           # the blown-out highlight where the logo meets its mirage
    "band": 3.0,              # % of frame height: miraged sky between the vanishing line and the sea
    "stem": 0.65,             # vertical stretch at the vanishing line (the "Etruscan vase" stem)
    # Fixed shapes (fractions of frame height, px at REF_H)
    "stem_height": 0.012,
    "haze_px": 12.0,
    "haze_height": 0.13,
    "haze_veil_px": 40,
    "haze_veil": 0.3,
    "band_glow": 2.0,         # band brightness, × sky glow colour
    "band_fade": 0.02,        # band brightness falls off over this depth
    "contact_width": 0.02,    # the highlight lives within this height of the line
    "contact_key": (0.25, 0.6),   # luminance range that turns into highlight
    "contact_gain": 1.5,      # whole contact zone (v03: 5, which blew out the full bar bases)
    "core_px": (70, 8),       # sideways blur that finds the middle of each contact
    "core_key": (0.45, 0.8),
    "core_gain": 6.0,
    "core_bloom_px": 30,
    "core_bloom": 3.0,
    "core_far_px": 230,
    "core_far": 6.0,
    "core_streak_px": (900, 12),
    "core_streak": 8.0,
    "contact_bloom_px": (50, 200),
    "contact_bloom": (2.0, 1.5),
    "contact_spread_px": (300, 45),  # wide, flat bloom along the line (x, y)
    "contact_spread": 6.0,
    "contact_tint": (255, 200, 150),     # sRGB: hot, near white
    "contact_bloom_tint": (255, 165, 95),
    "contact_grain": 1.4,
})
P = B.P
_rise_extra = R.extra


def extra():
    return _rise_extra() + [
        ("Haze", "NodeSocketFloat", P["haze"], 0.0, 3.0),         # heat-haze blur near the ground
        ("Contact", "NodeSocketFloat", P["contact"], 0.0, 3.0),   # blown-out highlight at the meeting point
        ("Band", "NodeSocketFloat", P["band"], 0.0, 6.0),         # % of frame height: bright strip below the line
        ("Stem", "NodeSocketFloat", P["stem"], 0.0, 0.9),         # stretch at the line
    ]


def stage(H, col):
    """Sunrise atmosphere, after the glows and before bloom. d = height above the vanishing line
    (the Horizon control); the sea horizon is Band % below it."""
    N, L, I, m, mix = H.N, H.L, H.I, H.math, H.mix
    fh = R._frame_h()
    x, y, d = R._coords(H)
    up = m("MAXIMUM", d, 0.0)
    down = m("MAXIMUM", m("MULTIPLY", d, -1.0), 0.0)
    ad = m("ABSOLUTE", d)

    def fade(v, height):  # exp(−v / height)
        return m("EXPONENT", m("MULTIPLY", v, -1.0 / height))

    t = N.new("CompositorNodeSceneTime")
    w = m("MULTIPLY", t.outputs["Seconds"], P["shimmer_speed"])
    drift = m("MULTIPLY", t.outputs["Seconds"], -P["shimmer_rise"])

    def noise(seed, sx, sy):
        v = N.new("ShaderNodeCombineXYZ")
        L(m("MULTIPLY", x, sx), v.inputs["X"]); L(m("MULTIPLY", m("ADD", y, drift), sy), v.inputs["Y"])
        n = N.new("ShaderNodeTexNoise"); n.noise_dimensions = "4D"; n.label = "Shimmer Noise"
        n.inputs["Scale"].default_value = 1.0
        n.inputs["Detail"].default_value = 0.5
        L(v.outputs[0], n.inputs["Vector"]); L(m("ADD", w, seed), n.inputs["W"])
        return m("MINIMUM", m("MAXIMUM", m("MULTIPLY", m("SUBTRACT", n.outputs["Fac"], 0.5), 6.0), -1.0), 1.0)

    # Shimmer, as v07 but reaching higher.
    amp = m("MULTIPLY", I["Shimmer"], fh / REF_H)
    reach = m("MAXIMUM", fade(up, P["shimmer_height"]), m("MULTIPLY", m("SUBTRACT", 1.0, H.sky), P["mirage_shimmer"]))
    amp = m("MULTIPLY", amp, reach, label="Shimmer Strength")
    dx = m("MULTIPLY", noise(0.0, 3.0, 50.0), amp)
    dy = m("MULTIPLY", noise(17.0, 2.0, 30.0), m("MULTIPLY", amp, 0.35))

    # Where to sample, as a height above the line: up there, the squashed mirror height below it.
    mirror = m("MULTIPLY", down, P["mirage_squash"], label="Reflected Height")
    # Never sample the occlusion edge itself: the stem would magnify its 1 px seam into a dark stripe.
    h = m("MAXIMUM", m("ADD", up, mirror), 2.0 / fh)
    # Stem: vertical magnification grows without bound at the vanishing line, so sample closer to it.
    h = m("MULTIPLY", h, m("SUBTRACT", 1.0, m("MULTIPLY", fade(h, P["stem_height"]), I["Stem"])), label="Stem Stretch")
    flat = m("MULTIPLY", m("MULTIPLY", up, fade(up, P["flatten_height"])), I["Flatten"])
    delta = m("ADD", m("SUBTRACT", h, d), flat)  # sample at y + delta
    dy = m("ADD", dy, m("MULTIPLY", delta, -fh), label="Vertical Offset (px)")
    vec = N.new("ShaderNodeCombineXYZ"); L(dx, vec.inputs["X"]); L(dy, vec.inputs["Y"])
    disp = N.new("CompositorNodeDisplace"); disp.label = "Mirage Displace"
    disp.inputs["Extension X"].default_value = "Extend"
    disp.inputs["Extension Y"].default_value = "Extend"
    # The warm sky goes in before the haze, so the air at the line shimmers too and the mirage
    # below the line reflects it (miraged sky is bright).
    sky_amt = m("MULTIPLY", m("MULTIPLY", fade(up, P["sky_glow_height"]), H.sky), I["Sky Glow"], label="Sky Glow Amount")
    col = mix("ADD", col, B.srgb(*P["sky_glow_color"]), sky_amt, "Sky Glow")
    L(col, disp.inputs["Image"]); L(vec.outputs[0], disp.inputs["Displacement"])
    moved = disp.outputs["Image"]

    # Heat haze blurs as well as moves: mix in a blurred copy, fully in the mirage, fading up the sky.
    hz = m("MAXIMUM", fade(up, P["haze_height"]), m("SUBTRACT", 1.0, H.sky))
    hz = m("MINIMUM", m("MULTIPLY", hz, I["Haze"]), 1.0, label="Haze Amount")
    moved = mix("MIX", moved, H.blur(moved, P["haze_px"], "Haze Blur", I["Haze"]), hz, "Heat Haze")
    # Contrast loss: a wide veil of the local average, strongest at the line.
    moved = mix("MIX", moved, H.blur(moved, P["haze_veil_px"], "Haze Veil"), m("MULTIPLY", hz, P["haze_veil"]), "Haze Veil")

    # Below the line: the bright miraged-sky band, with the inverted image in it, then the dark sea.
    band_d = m("MULTIPLY", I["Band"], 0.01)
    in_band = m("MINIMUM", m("MAXIMUM", m("ADD", m("MULTIPLY", m("SUBTRACT", band_d, down), fh), 0.5), 0.0), 1.0)
    in_band = m("MULTIPLY", in_band, m("SUBTRACT", 1.0, H.sky), label="Mirage Band")
    ref = m("MULTIPLY", fade(mirror, P["mirage_reach"]), I["Mirage"])
    # Feathered, not cut at the band's edge: full strength near the line, a Gaussian falloff by the band's depth.
    feather = m("DIVIDE", down, m("MULTIPLY", band_d, P["mirror_feather"]))
    ref = m("MULTIPLY", ref, m("EXPONENT", m("MULTIPLY", m("POWER", feather, 2.0), -1.0)))
    # Only a logo still near the line has a mirage: coverage within ~30 px above the line, spread
    # down over the mirror. Once the base lifts ~80 px the column has nothing left to mirror.
    low = m("MULTIPLY", H.cov, fade(up, P["mirror_hold"]))
    pb = N.new("CompositorNodeBlur"); pb.label = "Mirror Presence"
    pb.inputs["Type"].default_value = "Gaussian"
    pb.inputs["Size"].default_value = tuple(v * fh / REF_H for v in P["mirror_presence_px"])
    L(low, pb.inputs["Image"])
    ref = m("MULTIPLY", ref, m("MULTIPLY", pb.outputs[0], P["mirror_presence_gain"], clamp=True), label="Mirror Strength")
    band_lum = m("MULTIPLY", m("MULTIPLY", in_band, fade(down, P["band_fade"])), P["band_glow"])
    band_lum = m("MULTIPLY", band_lum, I["Sky Glow"], label="Band Glow")
    ground = mix("ADD", col, B.srgb(*P["sky_glow_color"]), band_lum, "Add Band")
    warm = mix("MULTIPLY", moved, B.srgb(*P["mirror_tint"]), 1.0, "Mirror Tint")  # it shows sunlit air, not blue body
    ground = mix("ADD", ground, warm, ref, "Add Mirror")
    out = mix("MIX", ground, moved, H.sky, "Sky / Ground")

    near = m("MULTIPLY", fade(ad, P["extinction_height"]), I["Extinction"])
    tint = mix("MIX", (1, 1, 1, 1), B.srgb(*P["extinction_tint"]), near, "Extinction Tint")
    out = mix("MULTIPLY", out, tint, 1.0, "Extinction")
    below_band = m("MAXIMUM", m("SUBTRACT", down, band_d), 0.0)
    under = m("MULTIPLY", m("MULTIPLY", fade(below_band, P["ground_glow_depth"]), m("SUBTRACT", 1.0, H.sky)),
              m("SUBTRACT", 1.0, in_band))
    band = m("MULTIPLY", m("MULTIPLY", under, 0.5), I["Sky Glow"], label="Ground Glow Amount")
    out = mix("ADD", out, B.srgb(*P["sky_glow_color"]), band, "Horizon Glow")

    # Contact highlight: bright light near the line (the logo, its stem and mirror) pushed past white,
    # then bloomed locally. Values over 1 also feed the Fog Glow after this stage.
    lum = N.new("CompositorNodeRGBToBW"); L(out, lum.inputs["Image"])
    k0, k1 = P["contact_key"]
    key = m("MULTIPLY", m("SUBTRACT", lum.outputs[0], k0), 1.0 / (k1 - k0), clamp=True)
    key = m("MULTIPLY", key, fade(ad, P["contact_width"]), label="Contact Key")
    hot = mix("MULTIPLY", mix("MULTIPLY", out, key), B.srgb(*P["contact_tint"]), 1.0, "Contact Source")
    (n_px, f_px), (n_a, f_a) = P["contact_bloom_px"], P["contact_bloom"]
    glow = mix("ADD", mix("MULTIPLY", H.blur(hot, n_px, "Contact Bloom Near"), (n_a,) * 3 + (1.0,)),
               H.blur(hot, f_px, "Contact Bloom Far"), f_a)
    # One sun, not one slab per bar: a wide, flat bloom that fills the gaps along the line.
    wide_b = N.new("CompositorNodeBlur"); wide_b.label = "Contact Spread"
    wide_b.inputs["Type"].default_value = "Gaussian"
    wide_b.inputs["Size"].default_value = tuple(v * fh / REF_H for v in P["contact_spread_px"])
    L(hot, wide_b.inputs["Image"])
    glow = mix("MULTIPLY", glow, B.srgb(*P["contact_bloom_tint"]), 1.0, "Contact Bloom Tint")
    glow = mix("ADD", glow, wide_b.outputs[0], P["contact_spread"], "Add Contact Spread")  # hot, untinted
    # Core: the key blurred sideways peaks at the middle of each bright run along the line, so a
    # threshold on it leaves an oval hot spot per contact point, not the whole width of a bar base.
    kb = N.new("CompositorNodeBlur"); kb.label = "Core Finder"
    kb.inputs["Type"].default_value = "Gaussian"
    kb.inputs["Size"].default_value = tuple(v * fh / REF_H for v in P["core_px"])
    L(key, kb.inputs["Image"])
    c0, c1 = P["core_key"]
    core = m("MULTIPLY", m("SUBTRACT", kb.outputs[0], c0), 1.0 / (c1 - c0), clamp=True, label="Contact Core")
    hot_core = mix("MULTIPLY", hot, core, 1.0, "Core Source")
    core_glow = H.blur(hot_core, P["core_bloom_px"], "Core Bloom")
    lit = mix("ADD", mix("MULTIPLY", hot, (P["contact_gain"],) * 3 + (1.0,)), glow, 1.0, "Contact Light")
    lit = mix("ADD", lit, hot_core, P["core_gain"], "Add Core")
    lit = mix("ADD", lit, core_glow, P["core_bloom"], "Add Core Bloom")
    # A sun blooms far past its disc: a wide warm bloom and a long streak along the water, both off the core.
    far = mix("MULTIPLY", H.blur(hot_core, P["core_far_px"], "Core Far Bloom"), B.srgb(*P["contact_bloom_tint"]), 1.0,
              "Core Far Tint")
    lit = mix("ADD", lit, far, P["core_far"], "Add Core Far Bloom")
    st = N.new("CompositorNodeBlur"); st.label = "Core Streak"
    st.inputs["Type"].default_value = "Gaussian"
    st.inputs["Size"].default_value = tuple(v * fh / REF_H for v in P["core_streak_px"])
    L(hot_core, st.inputs["Image"])
    lit = mix("ADD", lit, st.outputs[0], P["core_streak"], "Add Core Streak")
    out = mix("ADD", out, lit, I["Contact"], "Add Contact")

    # Grainier where it is hot: animated per-pixel noise, as a ± brightness jitter under the key.
    ic = N.new("CompositorNodeImageCoordinates"); L(I["Image"], ic.inputs["Image"])
    gv = N.new("ShaderNodeCombineXYZ")
    sp = N.new("ShaderNodeSeparateXYZ"); L(ic.outputs["Pixel"], sp.inputs[0])
    L(sp.outputs["X"], gv.inputs["X"]); L(sp.outputs["Y"], gv.inputs["Y"])
    L(t.outputs["Frame"], gv.inputs["Z"])
    wn = N.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = "3D"; L(gv.outputs[0], wn.inputs["Vector"])
    hotness = m("MULTIPLY", m("MINIMUM", key, 1.0), fade(ad, P["contact_width"] * 1.5))
    jit = m("MULTIPLY", m("SUBTRACT", wn.outputs["Value"], 0.5), m("MULTIPLY", hotness, P["contact_grain"]))
    out = mix("MULTIPLY", out, m("ADD", 1.0, jit, label="Contact Grain"), 1.0, "Hot Grain")
    return out


def pre(H, S):
    out = _rise_pre(H, S)
    H.cov = out["Coverage Pass"]  # logo coverage, hidden below the line
    return out


_rise_pre = R.pre
R.extra, R.stage, R.pre = extra, stage, pre
R.HOW = R.HOW.replace("ECLIPSE RISE", "ECLIPSE SUNRISE") + """
SUNRISE (this file)
    Haze      heat-haze blur near the ground (on top of the shimmer)
    Contact   the blown-out highlight where the logo meets its mirage
    Band      % of frame height: the bright miraged-sky strip between the line and the dark sea
    Stem      vertical stretch at the line, where the logo and its inverted image join
  Horizon is now the vanishing line: the logo appears from it, its mirage hangs below it.
"""

if __name__ == "__main__":
    R.main()
