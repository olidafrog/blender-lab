"""plotter-blend: the Geometry Nodes groups. Each returns a T whose .ng is the node group.

  isolines()        contour lines of any float field on any mesh (marching triangles per level)
  bump_field()      latitude + a peak + a trough on a sphere
  contour_sphere()  the designer-facing sphere
  funnel()          catenoid wireframe: meridians x parallels, dots at the crossings
"""
import math

import bpy

GEO = "NodeSocketGeometry"
F, I, V, B = "NodeSocketFloat", "NodeSocketInt", "NodeSocketVector", "NodeSocketBool"


class T:
    """A geometry node tree with short builders. Operands are sockets (linked) or values (set)."""

    def __init__(self, name):
        self.ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
        self.gi = self.ng.nodes.new("NodeGroupInput")
        self.go = self.ng.nodes.new("NodeGroupOutput")
        self.ids = {}

    def inp(self, name, st, default=None, lo=None, hi=None, tip=None, subtype=None):
        it = self.ng.interface.new_socket(name, in_out="INPUT", socket_type=st)
        if subtype:
            it.subtype = subtype
        if default is not None:
            it.default_value = default
        if lo is not None:
            it.min_value, it.max_value = lo, hi
        if tip:
            it.description = tip
        self.ids[name] = it.identifier
        return self.gi.outputs[name]

    def out(self, name, st=GEO):
        self.ng.interface.new_socket(name, in_out="OUTPUT", socket_type=st)
        return self.go.inputs[name]

    def link(self, a, b):
        self.ng.links.new(a, b)

    def put(self, sock, v):
        if hasattr(v, "is_output"):
            self.ng.links.new(v, sock)
        elif hasattr(v, "outputs"):
            self.ng.links.new(first(v.outputs), sock)
        else:
            sock.default_value = v

    def n(self, typ, **kw):
        """Node. kw: a node property, or an input by socket name (__ for a space)."""
        nd = self.ng.nodes.new(typ)
        for k, v in kw.items():           # properties first: they change which sockets are live
            if k in nd.bl_rna.properties:
                setattr(nd, k, v)
        for k, v in kw.items():
            if k not in nd.bl_rna.properties:
                name = k.replace("__", " ")
                self.put(next(s for s in nd.inputs if s.name == name and s.enabled), v)
        return nd

    def m(self, op, a, b=None, c=None):
        nd = self.ng.nodes.new("ShaderNodeMath")
        nd.operation = op
        for i, v in enumerate((a, b, c)):
            if v is not None:
                self.put(nd.inputs[i], v)
        return nd.outputs[0]

    def vm(self, op, a, b=None, scale=None):
        nd = self.ng.nodes.new("ShaderNodeVectorMath")
        nd.operation = op
        for i, v in enumerate((a, b)):
            if v is not None:
                self.put(nd.inputs[i], v)
        if scale is not None:
            self.put(nd.inputs["Scale"], scale)
        return first(nd.outputs)

    def comb(self, x, y, z):
        nd = self.ng.nodes.new("ShaderNodeCombineXYZ")
        for k, v in zip("XYZ", (x, y, z)):
            self.put(nd.inputs[k], v)
        return nd.outputs[0]

    def rot(self, vec, axis, angle):
        nd = self.ng.nodes.new("ShaderNodeVectorRotate")
        nd.rotation_type = axis  # X_AXIS, Y_AXIS, Z_AXIS
        self.put(nd.inputs["Vector"], vec)
        self.put(nd.inputs["Angle"], angle)
        return nd.outputs[0]

    def use(self, tree, **kw):
        g = self.ng.nodes.new("GeometryNodeGroup")
        g.node_tree = tree.ng
        g.label = tree.ng.name
        for k, v in kw.items():
            self.put(g.inputs[k.replace("__", " ")], v)
        return g

    def at(self, value, index, vector=False):
        """Evaluate a vertex field at another vertex."""
        nd = self.n("GeometryNodeFieldAtIndex", domain="POINT",
                    data_type="FLOAT_VECTOR" if vector else "FLOAT", Value=value, Index=index)
        return first(nd.outputs)

    def layout(self):
        from nodes import auto_layout
        auto_layout(self.ng)
        return self


def first(sockets):
    return next(s for s in sockets if s.enabled)


def set_input(mod, tree, name, value):
    """5.2: modifier inputs live at mod.properties.inputs.<identifier>.value."""
    getattr(mod.properties.inputs, tree.ids[name]).value = value


def isolines():
    """Contours of Value on Mesh, one closed spline per loop, with a `level` attribute.

    Per level (For Each zone): keep the triangles the level crosses and split them apart. In each,
    slide the two same-side corners along their edges to the crossing; the edge between them is now
    the contour segment. Merge by Distance joins the segments into loops."""
    t = T("Isolines")
    mesh = t.inp("Mesh", GEO)
    value = t.inp("Value", F, tip="The field to contour. Plug in any float field")
    spacing = t.inp("Spacing", F, 0.15, 0.001, 10.0, "Field distance between neighbouring lines")
    offset = t.inp("Offset", F, 0.0, -10.0, 10.0, "Slides every line through the field")
    keep_pts = t.inp("Keep", B, True, tip="Field on the finished lines: where false, the line is cut away")
    out = t.out("Curves")

    tri = t.n("GeometryNodeTriangulate", Mesh=mesh)
    held = t.n("GeometryNodeStoreNamedAttribute", data_type="FLOAT", domain="POINT",
               Geometry=tri, Name="_f", Value=value)
    stat = t.n("GeometryNodeAttributeStatistic", data_type="FLOAT", domain="POINT",
               Geometry=held, Attribute=value)
    k0 = t.m("CEIL", t.m("DIVIDE", t.m("SUBTRACT", stat.outputs["Min"], offset), spacing))
    k1 = t.m("FLOOR", t.m("DIVIDE", t.m("SUBTRACT", stat.outputs["Max"], offset), spacing))
    count = t.m("MAXIMUM", t.m("ADD", t.m("SUBTRACT", k1, k0), 1.0), 0.0)
    levels = t.n("GeometryNodePoints", Count=count)

    zi = t.ng.nodes.new("GeometryNodeForeachGeometryElementInput")
    zo = t.ng.nodes.new("GeometryNodeForeachGeometryElementOutput")
    zi.pair_with_output(zo)
    zo.domain = "POINT"
    t.link(levels.outputs[0], zi.inputs["Geometry"])
    level = t.m("ADD", t.m("MULTIPLY", t.m("ADD", k0, zi.outputs["Index"]), spacing), offset)

    f = t.n("GeometryNodeInputNamedAttribute", data_type="FLOAT", Name="_f").outputs[0]
    pos = t.n("GeometryNodeInputPosition").outputs[0]
    index = t.n("GeometryNodeInputIndex").outputs[0]

    def corners(face):
        """Side (1 above the level), value and position of the three corners of a face."""
        out = []
        for k in range(3):
            c = t.n("GeometryNodeCornersOfFace", Face__Index=face, Sort__Index=k).outputs["Corner Index"]
            v = t.n("GeometryNodeVertexOfCorner", Corner__Index=c).outputs[0]
            fk = t.at(f, v)
            out.append((t.m("GREATER_THAN", fk, level), fk, t.at(pos, v, vector=True)))
        return out

    def above(cs):
        return t.m("ADD", t.m("ADD", cs[0][0], cs[1][0]), cs[2][0])

    n_face = above(corners(index))
    crossed = t.m("MULTIPLY", t.m("GREATER_THAN", n_face, 0.5), t.m("LESS_THAN", n_face, 2.5))
    keep = t.n("GeometryNodeSeparateGeometry", domain="FACE", Geometry=held, Selection=crossed)
    split = t.n("GeometryNodeSplitEdges", Mesh=keep.outputs["Selection"])

    # After the split every vertex has one face. The odd corner is alone on its side of the level.
    corner = t.n("GeometryNodeCornersOfVertex", Vertex__Index=index, Sort__Index=0).outputs["Corner Index"]
    face = t.n("GeometryNodeFaceOfCorner", Corner__Index=corner).outputs["Face Index"]
    cs = corners(face)
    lone_side = t.m("COMPARE", above(cs), 1.0, 0.5)  # 1: the odd corner is the one above

    def is_odd(side):
        return t.m("SUBTRACT", 1.0, t.m("ABSOLUTE", t.m("SUBTRACT", side, lone_side)))

    w = [is_odd(c[0]) for c in cs]
    f_odd = t.m("ADD", t.m("ADD", t.m("MULTIPLY", w[0], cs[0][1]), t.m("MULTIPLY", w[1], cs[1][1])),
                t.m("MULTIPLY", w[2], cs[2][1]))
    p_odd = t.vm("ADD", t.vm("ADD", t.vm("SCALE", cs[0][2], scale=w[0]), t.vm("SCALE", cs[1][2], scale=w[1])),
                 t.vm("SCALE", cs[2][2], scale=w[2]))
    odd = is_odd(t.m("GREATER_THAN", f, level))
    along = t.m("DIVIDE", t.m("SUBTRACT", level, f), t.m("SUBTRACT", f_odd, f))
    # Never land on a corner: a level through a vertex would join four segments there.
    along = t.m("MINIMUM", t.m("MAXIMUM", along, 1e-3), 1.0 - 1e-3)
    mix = t.n("ShaderNodeMix", data_type="VECTOR", Factor=along, A=pos, B=p_odd)
    slid = t.n("GeometryNodeSetPosition", Geometry=split, Selection=t.m("SUBTRACT", 1.0, odd),
               Position=first(mix.outputs))

    ev = t.n("GeometryNodeInputMeshEdgeVertices")
    spoke = t.m("MAXIMUM", t.at(odd, ev.outputs["Vertex Index 1"]), t.at(odd, ev.outputs["Vertex Index 2"]))
    seg = t.n("GeometryNodeDeleteGeometry", domain="EDGE", mode="ALL", Geometry=slid, Selection=spoke)
    merged = t.n("GeometryNodeMergeByDistance", Geometry=seg, Distance=2e-6)
    # Cut on the mesh: deleting curve points does not split a spline.
    cut = t.n("GeometryNodeSeparateGeometry", domain="POINT", Geometry=merged, Selection=keep_pts)
    curve = t.n("GeometryNodeMeshToCurve", Mesh=cut.outputs["Selection"])
    tagged = t.n("GeometryNodeStoreNamedAttribute", data_type="FLOAT", domain="CURVE",
                 Geometry=curve, Name="level", Value=level)
    t.link(tagged.outputs[0], zo.inputs["Generation_0"])
    t.link(zo.outputs["Generation_0"], out)
    return t.layout()


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
