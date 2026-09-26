"""Compositor graph for wonder-caustics. Shared by build.py (full render) and
comp.py (instant re-grade off a saved EXR, with live backdrop preview)."""
import bpy

# Everything the comp stage can be tuned by. build.py merges these into P.
COMP_P = dict(
    # --- highlight extraction (what gets to glow at all)
    bloom_threshold=0.60,   # linear luminance above which pixels bloom
    bloom_smooth=0.45,      # soft knee on that threshold (0 = hard cut)
    bloom_clamp=False, bloom_max=20.0,
    # --- stage 1: soft halo
    bloom_type='Fog Glow',  # 'Fog Glow' (big soft halo) | 'Bloom' (tighter) | 'Ghosts' | 'Simple Star'
    bloom_size=0.90,        # 0..1 — radius as a fraction of the image
    bloom_strength=0.80,
    bloom_sat=1.25,         # >1 pushes the halo colour, reads as spectral
    bloom_tint=(1.0, 0.96, 1.0, 1.0),
    # --- stage 2: anamorphic streaks / flare
    streak_on=True,
    streak_strength=0.40,
    streak_size=1.00,
    streak_count=2,          # 2 = anamorphic bar, 4+ = star
    streak_angle=0.0,       # degrees
    streak_fade=0.95,       # higher = longer streak
    streak_colmod=0.45,     # rainbow separation along each streak
    streak_iters=5,
    streak_sat=1.0,
    streak_tint=(1.0, 1.0, 1.0, 1.0),
    # --- lens
    chroma=0.012,           # lens-distortion dispersion (edge fringing)
    distort=0.0,
    # --- debug view: '' | 'glare' | 'highlights' | 'bloom' | 'streaks'
    comp_preview='',
)


def _set(node, name, value):
    try:
        node.inputs[name].default_value = value
    except Exception as e:
        print(f"  ! {node.bl_idname}.{name}: {e}")


def _glare(ng, P, kind, x, y):
    g = ng.nodes.new("CompositorNodeGlare"); g.location = (x, y)
    _set(g, "Quality", 'High')
    _set(g, "Threshold", P["bloom_threshold"])
    _set(g, "Smoothness", P["bloom_smooth"])
    _set(g, "Clamp", P["bloom_clamp"])
    _set(g, "Maximum", P["bloom_max"])
    if kind == 'bloom':
        g.label = "Bloom"
        _set(g, "Type", P["bloom_type"])
        _set(g, "Size", P["bloom_size"])
        _set(g, "Strength", P["bloom_strength"])
        _set(g, "Saturation", P["bloom_sat"])
        _set(g, "Tint", tuple(P["bloom_tint"]))
    else:
        g.label = "Streaks"
        _set(g, "Type", 'Streaks')
        _set(g, "Size", P["streak_size"])
        _set(g, "Strength", P["streak_strength"])
        _set(g, "Saturation", P["streak_sat"])
        _set(g, "Tint", tuple(P["streak_tint"]))
        _set(g, "Streaks", P["streak_count"])
        _set(g, "Streaks Angle", __import__("math").radians(P["streak_angle"]))
        _set(g, "Iterations", P["streak_iters"])
        _set(g, "Fade", P["streak_fade"])
        _set(g, "Color Modulation", P["streak_colmod"])
    return g


def build_comp(ng, P, src_node, src_socket="Image"):
    """Wire highlights -> bloom -> streaks -> lens onto `ng`, ending in a group
    output AND a Viewer (the Viewer is what draws the backdrop in the GUI)."""
    src = src_node.outputs[src_socket]

    bloom = _glare(ng, P, 'bloom', 320, 0)
    ng.links.new(src, bloom.inputs["Image"])
    chain = bloom.outputs["Image"]

    streak = None
    if P["streak_on"]:
        streak = _glare(ng, P, 'streak', 620, 0)
        ng.links.new(chain, streak.inputs["Image"])
        chain = streak.outputs["Image"]

    ld = ng.nodes.new("CompositorNodeLensdist"); ld.location = (920, 0); ld.label = "Lens"
    _set(ld, "Type", 'Radial')
    _set(ld, "Dispersion", P["chroma"])
    _set(ld, "Distortion", P["distort"])
    _set(ld, "Fit", True)
    ng.links.new(chain, ld.inputs["Image"])
    final = ld.outputs["Image"]

    # debug taps — see the glow on its own, or what the threshold is catching
    pv = P.get("comp_preview", "")
    if pv == "highlights":  final = bloom.outputs["Highlights"]
    elif pv == "bloom":     final = bloom.outputs["Glare"]
    elif pv == "glare":     final = (streak or bloom).outputs["Glare"]
    elif pv == "streaks" and streak: final = streak.outputs["Glare"]

    if not ng.interface.items_tree:
        ng.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    out = ng.nodes.new("NodeGroupOutput"); out.location = (1220, 0)
    ng.links.new(final, out.inputs["Image"])

    vw = ng.nodes.new("CompositorNodeViewer"); vw.location = (1220, -260)
    ng.links.new(final, vw.inputs["Image"])
    return ng
