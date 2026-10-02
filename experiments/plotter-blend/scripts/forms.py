"""plotter-blend: the Geometry Nodes groups. Each returns a T whose .ng is the node group.

  (T, isolines and set_input now live in library/node-groups/plot_kit.py)
  bump_field()      latitude + a peak + a trough on a sphere
  contour_sphere()  the designer-facing sphere
  funnel()          catenoid wireframe: meridians x parallels, dots at the crossings
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "library" / "node-groups"))
from plot_kit import B, F, GEO, I, V, T, first, isolines, set_input  # noqa: E402,F401


def bump_field():
    """f(p) = p.a + A exp(-(1 - p.c1)/s^2) - balance A exp(-(1 - p.c2)/s^2), p on the unit sphere."""
    t = T("Bump Field")
    axis = t.inp("Axis", V, (0, 0, 1))
    c1 = t.inp("Peak", V, (1, 0, 0))
    c2 = t.inp("Trough", V, (-1, 0, 0))
    amp = t.inp("Strength", F, 1.0)
    size = t.inp("Size", F, 0.45)
    balance = t.inp("Balance", F, 1.0)
    out = t.out("Value", F)
    p = t.vm("NORMALIZE", t.n("GeometryNodeInputPosition").outputs[0])
    s2 = t.m("MAXIMUM", t.m("MULTIPLY", size, size), 1e-4)

    def bump(c):
        d = t.m("SUBTRACT", 1.0, t.vm("DOT_PRODUCT", p, c))
        return t.m("MULTIPLY", amp, t.m("EXPONENT", t.m("DIVIDE", t.m("MULTIPLY", d, -1.0), s2)))

    v = t.m("ADD", t.vm("DOT_PRODUCT", p, axis), bump(c1))
    t.link(t.m("SUBTRACT", v, t.m("MULTIPLY", balance, bump(c2))), out)
    return t.layout()


def contour_sphere(p):
    """The sphere. The viewer looks along +Y: X is screen right, Z is screen up, -Y is towards them."""
    t = T("Contour Sphere")
    t.panel_of = {**dict.fromkeys(("Lines", "Phase", "Pole Ring", "Axis Tilt", "Axis Roll"), "Lines"),
                  **dict.fromkeys(("Eye Strength", "Eye Size", "Eye Spread", "Eye Direction", "Eye Balance"), "Eyes"),
                  **dict.fromkeys(("Back Reach", "Ragged Ends", "Dot Spacing", "Dot Dropout", "Seed"), "Ends and dots"),
                  **dict.fromkeys(("Radius", "Detail", "Point Spacing"), "Size and detail")}
    lines = t.inp("Lines", I, p["lines"], 2, 80, "Lines from pole to pole, before the eyes add their rings")
    phase = t.inp("Phase", F, p["phase"], 0.0, 1.0, "Slides the lines through the field. Animate it")
    cap = t.inp("Pole Ring", F, p["pole_ring"], 0.005, 0.5, "Size of the first and last line round the poles; small: a tight ellipse")
    tilt = t.inp("Axis Tilt", F, p["axis_tilt"], -math.pi, math.pi, "Tips the pole towards the viewer", "ANGLE")
    roll = t.inp("Axis Roll", F, p["axis_roll"], -math.pi, math.pi, "Rolls the pole clockwise", "ANGLE")
    strength = t.inp("Eye Strength", F, p["eye_strength"], 0.0, 4.0, "0: plain parallels. Higher: more rings per eye")
    size = t.inp("Eye Size", F, p["eye_size"], 0.05, 1.5, "Angular size of each eye")
    spread = t.inp("Eye Spread", F, p["eye_spread"], 0.0, math.pi, "Angle of each eye off the view axis", "ANGLE")
    direction = t.inp("Eye Direction", F, p["eye_direction"], -math.pi, math.pi,
                      "Turns the pair of eyes around the view axis", "ANGLE")
    balance = t.inp("Eye Balance", F, p["eye_balance"], -1.0, 2.0, "Second eye: 1 a trough, 0 none, -1 a second peak")
    reach = t.inp("Back Reach", F, p["back_reach"], 0.0, 2.0,
                  "How far lines run onto the far side. 0: front only. 2: whole sphere, closed loops")
    ragged = t.inp("Ragged Ends", F, p["ragged_ends"], 0.0, 1.0, "Makes the lines end at uneven depths")
    dot_gap = t.inp("Dot Spacing", F, p["dot_spacing"], 0.02, 10.0, "Distance between dots along a line")
    dot_drop = t.inp("Dot Dropout", F, p["dot_dropout"], 0.0, 1.0, "Share of dots removed at random; 1: no dots")
    seed = t.inp("Seed", I, p["seed"], 0, 9999)
    radius = t.inp("Radius", F, p["radius"], 0.01, 100.0)
    detail = t.inp("Detail", I, p["detail"], 2, 7, "Sphere subdivisions the contours are cut from")
    step = t.inp("Point Spacing", F, p["point_spacing"], 0.002, 1.0, "Distance between points on a line")
    out = t.out("Geometry")

    axis = t.rot(t.rot((0.0, 0.0, 1.0), "X_AXIS", tilt), "Y_AXIS", roll)
    sx = t.m("MULTIPLY", t.m("SINE", spread), t.m("COSINE", direction))
    sz = t.m("MULTIPLY", t.m("SINE", spread), t.m("SINE", direction))
    toward = t.m("MULTIPLY", t.m("COSINE", spread), -1.0)
    peak = t.comb(sx, toward, sz)
    trough = t.comb(t.m("MULTIPLY", sx, -1.0), toward, t.m("MULTIPLY", sz, -1.0))

    field = t.use(bump_field(), Axis=axis, Peak=peak, Trough=trough, Strength=strength, Size=size, Balance=balance)
    ico = t.n("GeometryNodeMeshIcoSphere", Radius=1.0, Subdivisions=detail)
    # Lines run from one pole ring to the other: levels at -(1 - cap) ... +(1 - cap), then on into the eyes.
    top = t.m("SUBTRACT", 1.0, cap)
    spacing = t.m("DIVIDE", t.m("MULTIPLY", top, 2.0), t.m("MAXIMUM", t.m("SUBTRACT", lines, 1.0), 1.0))
    offset = t.m("SUBTRACT", t.m("MULTIPLY", phase, spacing), top)
    # Facing: 1 at the point nearest the viewer, -1 at the far point.
    pos = t.n("GeometryNodeInputPosition").outputs[0]
    facing = t.m("MULTIPLY", t.n("ShaderNodeSeparateXYZ", Vector=t.vm("NORMALIZE", pos)).outputs["Y"], -1.0)
    noise = t.n("ShaderNodeTexNoise", noise_dimensions="4D", Vector=pos, W=seed, Scale=1.5, Detail=0.0)
    wobble = t.m("MULTIPLY", t.m("SUBTRACT", noise.outputs[0], 0.5), t.m("MULTIPLY", ragged, 2.0))
    limit = t.m("MULTIPLY", t.m("ADD", reach, wobble), -1.0)
    whole = t.m("GREATER_THAN", reach, 1.999)
    keep = t.m("MAXIMUM", t.m("GREATER_THAN", facing, limit), whole)
    iso = t.use(isolines(), Mesh=ico, Value=field.outputs["Value"], Spacing=spacing, Offset=offset, Keep=keep)

    on_sphere = t.n("GeometryNodeSetPosition", Geometry=iso,
                    Position=t.vm("SCALE", t.vm("NORMALIZE", pos), scale=radius))
    even = t.n("GeometryNodeResampleCurve", Curve=on_sphere, Length=step)
    even.inputs["Mode"].default_value = "Length"

    dots = t.n("GeometryNodeCurveToPoints", mode="LENGTH", Curve=even, Length=dot_gap)
    rnd = t.n("FunctionNodeRandomValue", data_type="FLOAT", Seed=seed)
    kept = t.n("GeometryNodeDeleteGeometry", domain="POINT", Geometry=dots.outputs["Points"],
               Selection=t.m("LESS_THAN", first(rnd.outputs), dot_drop))
    # A dot on every loose end.
    is_end = t.m("MULTIPLY", t.n("GeometryNodeCurveEndpointSelection", Start__Size=1, End__Size=1).outputs[0],
                 t.m("SUBTRACT", 1.0, t.n("GeometryNodeInputSplineCyclic").outputs[0]))
    marked = t.n("GeometryNodeStoreNamedAttribute", data_type="BOOLEAN", domain="POINT",
                 Geometry=even, Name="_end", Value=is_end)
    ends = t.n("GeometryNodeCurveToPoints", mode="EVALUATED", Curve=marked)
    not_end = t.m("SUBTRACT", 1.0, t.n("GeometryNodeInputNamedAttribute", data_type="BOOLEAN", Name="_end").outputs[0])
    ends = t.n("GeometryNodeDeleteGeometry", domain="POINT", Geometry=ends.outputs["Points"], Selection=not_end)
    kept = t.n("GeometryNodeJoinGeometry", Geometry=kept)
    t.link(ends.outputs[0], kept.inputs[0])
    small = t.n("GeometryNodeSetPointRadius", Points=kept, Radius=t.m("MULTIPLY", radius, 0.012))
    join = t.n("GeometryNodeJoinGeometry")
    t.link(even.outputs[0], join.inputs[0])
    t.link(small.outputs[0], join.inputs[0])
    t.link(join.outputs[0], out)
    return t.layout()


def funnel(p):
    """Flared catenoid r(u) = a cosh(k u^flare), k = acosh(R / a), u = z / H: throat a at z = 0, rim R at z = H."""
    t = T("Funnel")
    n_mer = t.inp("Meridians", I, p["meridians"], 0, 200, "Lines running from rim to throat")
    n_par = t.inp("Parallels", I, p["parallels"], 2, 200, "Rings, including the rim and the throat")
    throat = t.inp("Throat Radius", F, p["throat_radius"], 0.01, 100.0)
    rim = t.inp("Rim Radius", F, p["rim_radius"], 0.02, 100.0)
    height = t.inp("Height", F, p["height"], 0.01, 100.0)
    flare = t.inp("Flare", F, p["flare"], 0.3, 4.0, "1: a true catenoid. Higher: a straighter throat and a later, wider lip")
    bias = t.inp("Ring Bias", F, p["ring_bias"], 0.2, 5.0, "1: even height steps. Higher: rings gather at the throat")
    twist = t.inp("Twist", F, p["twist"], -math.tau, math.tau, "Turns the rim against the throat: a vortex", "ANGLE")
    dots_on = t.inp("Dots", B, p["funnel_dots"], tip="A dot at every crossing")
    res = t.inp("Resolution", I, p["resolution"], 8, 1024, "Points around a ring")
    out = t.out("Geometry")

    ratio = t.m("MAXIMUM", t.m("DIVIDE", rim, throat), 1.0)
    k = t.m("LOGARITHM", t.m("ADD", ratio, t.m("SQRT", t.m("SUBTRACT", t.m("MULTIPLY", ratio, ratio), 1.0))), math.e)

    def radius(u):  # u: 0 at the throat, 1 at the rim
        return t.m("MULTIPLY", throat, t.m("COSH", t.m("MULTIPLY", t.m("POWER", u, flare), k)))

    index = t.n("GeometryNodeInputIndex").outputs[0]

    # One meridian in the XZ plane, then a copy per angle.
    line = t.n("GeometryNodeCurvePrimitiveLine", End=(0.0, 0.0, 1.0))
    line = t.n("GeometryNodeResampleCurve", Curve=line, Count=t.m("MAXIMUM", t.m("DIVIDE", res, 2.0), 8.0))
    u = t.n("GeometryNodeSplineParameter").outputs["Factor"]
    swirl = t.m("MULTIPLY", twist, u)
    r_u = radius(u)
    profile = t.n("GeometryNodeSetPosition", Geometry=line, Position=t.comb(
        t.m("MULTIPLY", r_u, t.m("COSINE", swirl)), t.m("MULTIPLY", r_u, t.m("SINE", swirl)),
        t.m("MULTIPLY", u, height)))
    spokes = t.n("GeometryNodePoints", Count=n_mer)
    turn = t.m("MULTIPLY", t.m("DIVIDE", index, t.m("MAXIMUM", n_mer, 1.0)), math.tau)
    mer = t.n("GeometryNodeInstanceOnPoints", Points=spokes, Instance=profile,
              Rotation=t.n("FunctionNodeEulerToRotation", Euler=t.comb(0.0, 0.0, turn)))
    mer = t.n("GeometryNodeRealizeInstances", Geometry=mer)

    # Rings: k-th at u = (k / (K - 1)) ^ (1 / bias), counted from the rim so bias gathers them below.
    frac = t.m("DIVIDE", index, t.m("MAXIMUM", t.m("SUBTRACT", n_par, 1.0), 1.0))
    u_k = t.m("POWER", frac, bias)
    r_k = radius(u_k)
    rings = t.n("GeometryNodePoints", Count=n_par, Position=t.comb(0.0, 0.0, t.m("MULTIPLY", u_k, height)))
    circle = t.n("GeometryNodeCurvePrimitiveCircle", mode="RADIUS", Resolution=res, Radius=1.0)
    par = t.n("GeometryNodeInstanceOnPoints", Points=rings, Instance=circle, Scale=t.comb(r_k, r_k, 1.0),
              Rotation=t.n("FunctionNodeEulerToRotation", Euler=t.comb(0.0, 0.0, t.m("MULTIPLY", twist, u_k))))
    par = t.n("GeometryNodeRealizeInstances", Geometry=par)

    dots = t.n("GeometryNodeCurveToPoints", mode="COUNT", Curve=par, Count=n_mer)
    dots = t.n("GeometryNodeSetPointRadius", Points=dots.outputs["Points"], Radius=t.m("MULTIPLY", rim, 0.012))
    gate = t.n("GeometryNodeSwitch", input_type="GEOMETRY", Switch=dots_on)
    t.link(dots.outputs[0], next(s for s in gate.inputs if s.name == "True" and s.enabled))
    join = t.n("GeometryNodeJoinGeometry")
    for g in (mer, par, gate):
        t.link(first(g.outputs), join.inputs[0])
    t.link(join.outputs[0], out)
    return t.layout()
