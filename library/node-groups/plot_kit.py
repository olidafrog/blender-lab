"""Line-art forms as Geometry Nodes groups: curves for tools/plot_svg.py (pen-plotter SVG strokes).

    sys.path.insert(0, str(LIBRARY / "node-groups")); import plot_kit as pk

  T                 node-tree builder; T.env(...) compiles formula strings ("cos(u)*sinh(v)") to Math nodes
  isolines()        contour lines of any float field on any mesh (marching triangles per level)
  contours()        the same, as "N lines between the field's min and max"
  harmonic()        real spherical harmonic Y(L, M) of a unit vector
  surface()         a parametric surface x,y,z(u,v): parameter lines, edges, contours, dots, occluder mesh
  solid()           any mesh (primitive, implicit volume, object): contour families + occluder mesh
  sphere_field()    contours of a formula on a sphere
  curve_family()    N curves from a formula x,y,z(t, i)

Every form group outputs curves (the strokes), optionally points (dots) and, when "Solid" is on, the
triangulated surface: plot_svg uses that mesh to hide lines behind it and to draw the outline.
Built for plotter-blend and plotter-forms. Blender 5.x (For Each zone).
"""
import ast
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

GEO = "NodeSocketGeometry"
F, I, V, B, OBJ = "NodeSocketFloat", "NodeSocketInt", "NodeSocketVector", "NodeSocketBool", "NodeSocketObject"

MATH1 = {"sin": "SINE", "cos": "COSINE", "tan": "TANGENT", "asin": "ARCSINE", "acos": "ARCCOSINE",
         "atan": "ARCTANGENT", "sinh": "SINH", "cosh": "COSH", "tanh": "TANH", "exp": "EXPONENT",
         "sqrt": "SQRT", "abs": "ABSOLUTE", "floor": "FLOOR", "ceil": "CEIL", "round": "ROUND",
         "frac": "FRACT", "sign": "SIGN"}
MATH2 = {"atan2": "ARCTAN2", "pow": "POWER", "mod": "FLOORED_MODULO", "min": "MINIMUM", "max": "MAXIMUM",
         "gt": "GREATER_THAN", "lt": "LESS_THAN"}
BINOP = {ast.Add: "ADD", ast.Sub: "SUBTRACT", ast.Mult: "MULTIPLY", ast.Div: "DIVIDE", ast.Mod: "FLOORED_MODULO"}
CONST = {"pi": math.pi, "tau": math.tau, "e": math.e}


def first(sockets):
    return next(s for s in sockets if s.enabled)


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


class T:
    """A geometry node tree with short builders. Operands are sockets (linked) or values (set)."""

    def __init__(self, name):
        self.ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
        self.gi = self.ng.nodes.new("NodeGroupInput")
        self.go = self.ng.nodes.new("NodeGroupOutput")
        self.ids = {}
        self.panel_of = {}   # input name -> panel name; set before calling inp()
        self._panels = {}

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
        if name in self.panel_of:
            title = self.panel_of[name]
            if title not in self._panels:
                self._panels[title] = [self.ng.interface.new_panel(title), 0]
            panel = self._panels[title]
            self.ng.interface.move_to_parent(it, panel[0], panel[1])
            panel[1] += 1
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
                sock = next((s for s in nd.inputs if s.name == name and s.enabled), None)
                if sock is None:
                    raise KeyError(f"{typ} has no input '{name}'; it has {[s.name for s in nd.inputs if s.enabled]}")
                self.put(sock, v)
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

    def sep(self, vec):
        nd = self.ng.nodes.new("ShaderNodeSeparateXYZ")
        self.put(nd.inputs[0], vec)
        return nd.outputs[0], nd.outputs[1], nd.outputs[2]

    def rot(self, vec, axis, angle):
        nd = self.ng.nodes.new("ShaderNodeVectorRotate")
        nd.rotation_type = axis  # X_AXIS, Y_AXIS, Z_AXIS
        self.put(nd.inputs["Vector"], vec)
        self.put(nd.inputs["Angle"], angle)
        return nd.outputs[0]

    def use(self, tree, **kw):
        g = self.ng.nodes.new("GeometryNodeGroup")
        g.node_tree = tree if isinstance(tree, bpy.types.NodeTree) else tree.ng
        g.label = g.node_tree.name
        for k, v in kw.items():
            self.put(g.inputs[k.replace("__", " ")], v)
        return g

    def at(self, value, index, vector=False):
        """Evaluate a vertex field at another vertex."""
        nd = self.n("GeometryNodeFieldAtIndex", domain="POINT",
                    data_type="FLOAT_VECTOR" if vector else "FLOAT", Value=value, Index=index)
        return first(nd.outputs)

    def attr(self, name, vector=False):
        return self.n("GeometryNodeInputNamedAttribute", data_type="FLOAT_VECTOR" if vector else "FLOAT",
                      Name=name).outputs[0]

    def store(self, geo, name, value, domain="POINT", data_type="FLOAT"):
        return self.n("GeometryNodeStoreNamedAttribute", data_type=data_type, domain=domain,
                      Geometry=geo, Name=name, Value=value)

    def switch(self, flag, on, off=None):
        """Geometry switch: `on` when flag, else `off` (nothing)."""
        sw = self.n("GeometryNodeSwitch", input_type="GEOMETRY", Switch=flag)
        self.put(next(s for s in sw.inputs if s.name == "True" and s.enabled), on)
        if off is not None:
            self.put(next(s for s in sw.inputs if s.name == "False" and s.enabled), off)
        return sw.outputs[0]

    def join(self, *geos):
        j = self.ng.nodes.new("GeometryNodeJoinGeometry")
        for g in reversed(geos):     # Join Geometry reverses link order
            self.put(j.inputs[0], g) if not hasattr(g, "outputs") else self.link(first(g.outputs), j.inputs[0])
        return j.outputs[0]

    def env(self, **names):
        return Env(self, names)

    def layout(self):
        from nodes import auto_layout
        auto_layout(self.ng)
        return self


class Env:
    """Formula strings → Math nodes. Names are sockets, numbers, or Python callables f(*args) -> socket.

        ex = t.env(u=u, v=v, a=slider)
        x = ex("cos(a)*sinh(v)*sin(u) + sin(a)*cosh(v)*cos(u)")

    Functions: sin cos tan asin acos atan atan2 sinh cosh tanh exp log sqrt abs floor ceil round frac
    sign pow mod min max gt lt clamp(x,a,b) mix(a,b,t) smin(a,b,k) noise(x,y,z[,detail]); constants pi tau e;
    operators + - * / ** %, comparisons < >, and `a if cond else b`."""

    def __init__(self, t, names):
        self.t, self.names, self.cache = t, dict(names), {}

    def __call__(self, src):
        if not isinstance(src, str):
            return src
        return self._ev(ast.parse(src.strip(), mode="eval").body)

    def _ev(self, node):
        key = ast.dump(node)
        if key not in self.cache:
            self.cache[key] = self._build(node)
        return self.cache[key]

    def _build(self, node):
        t, ev = self.t, self._ev
        if isinstance(node, ast.Constant):
            return float(node.value)
        if isinstance(node, ast.Name):
            if node.id in self.names:
                v = self.names[node.id]
                return float(v) if is_num(v) else v
            return CONST[node.id]
        if isinstance(node, ast.UnaryOp):
            v = ev(node.operand)
            if isinstance(node.op, ast.UAdd):
                return v
            return -v if is_num(v) else t.m("MULTIPLY", v, -1.0)
        if isinstance(node, ast.BinOp):
            a, b = ev(node.left), ev(node.right)
            if isinstance(node.op, ast.Pow):
                if is_num(a) and is_num(b):
                    return a ** b
                if is_num(b) and b == int(b) and 1 <= b <= 4:     # safe for a negative base
                    out = a
                    for _ in range(int(b) - 1):
                        out = t.m("MULTIPLY", out, a)
                    return out
                return t.m("POWER", a, b)
            if is_num(a) and is_num(b):
                return {ast.Add: a + b, ast.Sub: a - b, ast.Mult: a * b,
                        ast.Div: a / b if b else 0.0, ast.Mod: a % b if b else 0.0}[type(node.op)]
            return t.m(BINOP[type(node.op)], a, b)
        if isinstance(node, ast.Compare):
            a, b = ev(node.left), ev(node.comparators[0])
            op = "LESS_THAN" if isinstance(node.ops[0], (ast.Lt, ast.LtE)) else "GREATER_THAN"
            return t.m(op, a, b)
        if isinstance(node, ast.IfExp):
            c, a, b = ev(node.test), ev(node.body), ev(node.orelse)
            return first(t.n("ShaderNodeMix", data_type="FLOAT", Factor=c, A=b, B=a).outputs)
        if isinstance(node, ast.Call):
            fn = node.func.id
            args = [ev(a) for a in node.args]
            if fn in self.names and callable(self.names[fn]):
                return self.names[fn](*args)
            if fn in MATH1:
                if is_num(args[0]) and hasattr(math, fn):
                    return getattr(math, fn)(args[0])
                return t.m(MATH1[fn], args[0])
            if fn == "log":
                return t.m("LOGARITHM", args[0], math.e)
            if fn in MATH2:
                out = args[0]
                for a in args[1:]:
                    out = t.m(MATH2[fn], out, a)
                return out
            if fn == "clamp":
                return t.m("MINIMUM", t.m("MAXIMUM", args[0], args[1]), args[2])
            if fn == "smin":      # smooth minimum: rounds the edge where two solids meet
                k = args[2] if len(args) > 2 else 10.0
                e = [t.m("EXPONENT", t.m("MULTIPLY", x, t.m("MULTIPLY", k, -1.0) if not is_num(k) else -k)) for x in args[:2]]
                return t.m("DIVIDE", t.m("LOGARITHM", t.m("ADD", e[0], e[1]), math.e), t.m("MULTIPLY", k, -1.0) if not is_num(k) else -k)
            if fn == "mix":
                return t.m("ADD", args[0], t.m("MULTIPLY", t.m("SUBTRACT", args[1], args[0]), args[2]))
            if fn == "noise":
                nd = t.n("ShaderNodeTexNoise", noise_dimensions="3D", Vector=t.comb(*args[:3]), Scale=1.0,
                         Detail=args[3] if len(args) > 3 else 0.0)
                return nd.outputs[0]
            raise ValueError(f"unknown function {fn}")
        raise ValueError(f"cannot compile {ast.dump(node)}")


def set_input(mod, tree, name, value):
    """5.2: modifier inputs live at mod.properties.inputs.<identifier>.value."""
    ids = tree.ids if hasattr(tree, "ids") else {i.name: i.identifier for i in tree.interface.items_tree
                                                 if getattr(i, "in_out", "") == "INPUT"}
    getattr(mod.properties.inputs, ids[name]).value = value


def _shared(name):
    return bpy.data.node_groups.get(name)


def isolines():
    """Contours of Value on Mesh, one closed spline per loop, with a `level` attribute.

    Per level (For Each zone): keep the triangles the level crosses and split them apart. In each,
    slide the two same-side corners along their edges to the crossing; the edge between them is now
    the contour segment. Merge by Distance joins the segments into loops."""
    if _shared("Isolines"):
        return _shared("Isolines")
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
    return t.layout().ng


def contours():
    """Isolines by count: `Lines` levels spread evenly between the field's min and max on the mesh."""
    if _shared("Contours"):
        return _shared("Contours")
    t = T("Contours")
    mesh = t.inp("Mesh", GEO)
    value = t.inp("Value", F, tip="The field to contour")
    lines = t.inp("Lines", I, 12, 0, 500, "Number of levels between the field's lowest and highest value")
    phase = t.inp("Phase", F, 0.0, 0.0, 1.0, "Slides the levels through the field")
    keep = t.inp("Keep", B, True)
    out = t.out("Curves")
    stat = t.n("GeometryNodeAttributeStatistic", data_type="FLOAT", domain="POINT", Geometry=mesh, Attribute=value)
    lo, hi = stat.outputs["Min"], stat.outputs["Max"]
    spacing = t.m("MAXIMUM", t.m("DIVIDE", t.m("SUBTRACT", hi, lo), t.m("MAXIMUM", lines, 1.0)), 1e-6)
    offset = t.m("ADD", lo, t.m("MULTIPLY", spacing, t.m("ADD", 0.5, t.m("MULTIPLY", t.m("FRACT", phase), 0.999))))
    # The offset is taken out of the field so Isolines' own Offset limits (+-10) never clip it.
    iso = t.use(isolines(), Mesh=mesh, Value=t.m("SUBTRACT", value, offset), Spacing=spacing, Offset=0.0, Keep=keep)
    t.link(t.switch(t.m("GREATER_THAN", lines, 0.5), iso), out)
    return t.layout().ng


def harmonic(max_degree=12):
    """Real spherical harmonic (unnormalised): P_L^|M|(z) * cos(M lon) (sin for M < 0), of a unit vector."""
    if _shared("Spherical Harmonic"):
        return _shared("Spherical Harmonic")
    t = T("Spherical Harmonic")
    L = t.inp("L", I, 3, 0, max_degree, "Degree: total number of nodal lines")
    M = t.inp("M", I, 2, -max_degree, max_degree, "Order: nodal lines through the poles")
    vec = t.inp("Vector", V, (0, 0, 1))
    out = t.out("Value", F)
    x, y, z = t.sep(t.vm("NORMALIZE", vec))
    ex = t.env(x=x, y=y, z=z, L=L, M=M)
    m = ex("min(abs(M), L)")
    ex.names["m"] = m
    prev2, prev = 0.0, ex("pow(max(1 - z*z, 0), m/2)")     # P_m^m up to a constant
    for k in range(1, max_degree + 1):
        e = t.env(z=z, m=m, k=float(k), a=prev, b=prev2, L=L)
        new = e("((2*(m+k) - 1)*z*a - (2*m + k - 1)*b) / k")
        on = e("(m + k) < (L + 0.5)")
        prev2 = first(t.n("ShaderNodeMix", data_type="FLOAT", Factor=on, A=prev2, B=prev).outputs)
        prev = first(t.n("ShaderNodeMix", data_type="FLOAT", Factor=on, A=prev, B=new).outputs)
    ex.names["p"] = prev
    t.link(ex("p * (cos(m*atan2(y, x)) if M > -0.5 else sin(m*atan2(y, x)))"), out)
    return t.layout().ng


# ----------------------------------------------------------------------------------------------------
# Form factories. `params` is a list of dicts: name (slider label), key (formula name), default,
# lo, hi, tip, kind ("f" float, "i" int, "angle" radians shown as degrees).

def _params(t, params, values):
    env = {}
    t.key_names = getattr(t, "key_names", {})      # formula key -> slider label
    for p in params:
        t.key_names[p["key"]] = p["name"]
        kind = p.get("kind", "f")
        d = values.get(p["key"], p["default"])
        env[p["key"]] = t.inp(p["name"], I if kind == "i" else F, int(d) if kind == "i" else float(d),
                              p.get("lo", -100.0), p.get("hi", 100.0), p.get("tip"),
                              "ANGLE" if kind == "angle" else None)
    return env


def _let(ex, let):
    """Named sub-formulas, in order: [("j", "floor(i / fibres)"), ...]."""
    for k, formula in let:
        ex.names[k] = ex(formula)
    return ex


def _grid(t, res_x, res_y):
    """Unit grid with its parameters stored as attributes u, v in 0..1."""
    grid = t.n("GeometryNodeMeshGrid", Size__X=1.0, Size__Y=1.0, Vertices__X=res_x, Vertices__Y=res_y)
    gx, gy, _ = t.sep(t.n("GeometryNodeInputPosition").outputs[0])
    g = t.store(grid, "u", t.m("ADD", gx, 0.5))
    return t.store(g, "v", t.m("ADD", gy, 0.5))


def _uv_env(t, env, u, v, let):
    """Formula names for a parametric surface: u, v in their ranges, u01, v01, the params, the lets."""
    u01, v01 = t.attr("u"), t.attr("v")
    ex = t.env(**env)
    u0, u1, v0, v1 = ex(u[0]), ex(u[1]), ex(v[0]), ex(v[1])
    ex.names.update(u01=u01, v01=v01)
    ex.names["u"] = ex("u0 + u01*(u1 - u0)") if False else t.m("ADD", u0, t.m("MULTIPLY", u01, t.m("SUBTRACT", u1, u0)))
    ex.names["v"] = t.m("ADD", v0, t.m("MULTIPLY", v01, t.m("SUBTRACT", v1, v0)))
    return _let(ex, let)


def _families(t, mesh, ex, families, values, keep=True):
    """Contour families [(label, key, formula, default count)] on a triangulated mesh → list of curve sockets."""
    out = []
    for label, key, formula, count in families:
        n = t.inp(label, I, int(values.get(key, count)), 0, 400, f"Number of lines: contours of {formula}")
        out.append(t.use(contours(), Mesh=mesh, Value=ex(formula), Lines=n, Keep=keep).outputs[0])
    return out


def _finish(t, curves, mesh, values, dots=None):
    solid = t.inp("Solid", B, bool(values.get("solid", True)),
                  tip="On: the surface hides the lines behind it when plotted. Off: see-through")
    parts = list(curves)
    if dots is not None:
        parts.append(dots)
    parts.append(t.switch(solid, mesh))
    t.link(t.join(*parts), t.out("Geometry"))
    return t.layout()


def surface(name, x, y, z, u=(0.0, 1.0), v=(0.0, 1.0), params=(), u_lines=("U Lines", 12), v_lines=("V Lines", 12),
            closed=(False, False), edges=(True, True), families=(), res=(160, 160), values=None, dots=False, let=(),
            pole=False):
    """Parametric surface. u, v ranges may be formulas of the params. u_lines draws curves of constant u.
    closed: the parameter wraps (no edge, lines at half steps). families: extra contour sets by formula
    of x, y, z (the finished position), u, v and the params. let: named sub-formulas. edges: per parameter,
    True (both ends), "lo", "hi" or False. pole: the u-lines are spokes that meet where v is lowest; a
    "Pole Trim" slider ends every 2nd, 4th and 8th spoke early so they do not blot there."""
    values = values or {}
    t = T(name)
    nu = t.inp(u_lines[0], I, int(values.get("u_lines", u_lines[1])), 0, 400)
    nv = t.inp(v_lines[0], I, int(values.get("v_lines", v_lines[1])), 0, 400)
    t.key_names = {"u_lines": u_lines[0], "v_lines": v_lines[0], **{key: label for label, key, _, _ in families}}
    fam_n = {key: t.inp(label, I, int(values.get(key, count)), 0, 400, f"Number of lines: contours of {formula}")
             for label, key, formula, count in families}
    env = _params(t, params, values)
    ex = _uv_env(t, env, u, v, let)
    position = t.comb(ex(x), ex(y), ex(z))
    rx = t.inp("Resolution U", I, int(values.get("res_u", res[0])), 8, 1024, "Mesh points along u: smoothness of the lines")
    ry = t.inp("Resolution V", I, int(values.get("res_v", res[1])), 8, 1024)
    mesh = t.n("GeometryNodeSetPosition", Geometry=_grid(t, rx, ry), Position=position)
    mesh = t.n("GeometryNodeTriangulate", Mesh=mesh)

    u01, v01 = ex.names["u01"], ex.names["v01"]
    keep_spoke = True
    if pole:
        trim = t.inp("Pole Trim", F, float(values.get("pole_trim", 0.3)), 0.0, 0.9,
                     "Ends every 2nd, 4th and 8th spoke before the centre, so the pen does not blot there. 0: off")
        e = t.env(u01=u01, v01=v01, n=nu, trim=trim, shift=0.0 if closed[0] else 0.5)
        e.names["k"] = e("floor(u01 * n + shift)")
        keep_spoke = e("v01 > trim * (1 if mod(k, 2) > 0.5 else (0.5 if mod(k, 4) > 1.5 else (0.25 if mod(k, 8) > 3.5 else 0)))")
    curves = []
    for attr, n, wraps, keep in ((u01, nu, closed[0], keep_spoke), (v01, nv, closed[1], True)):
        inner = t.m("ADD", t.m("MULTIPLY", attr, 1.0 - 2e-4), 1e-4)
        spacing = t.m("DIVIDE", 1.0, t.m("MAXIMUM", n, 1.0))
        iso = t.use(isolines(), Mesh=mesh, Value=inner, Spacing=spacing,
                    Offset=t.m("MULTIPLY", spacing, 0.5) if wraps else 0.0, Keep=keep)
        curves.append(t.switch(t.m("GREATER_THAN", n, 0.5), iso))
    for attr, on in ((u01, edges[0]), (v01, edges[1])):
        if on:
            lo, hi = t.m("LESS_THAN", attr, 5e-5), t.m("GREATER_THAN", attr, 1.0 - 5e-5)
            rim = lo if on == "lo" else hi if on == "hi" else t.m("MAXIMUM", lo, hi)
            curves.append(t.n("GeometryNodeMeshToCurve", Mesh=mesh, Selection=rim).outputs[0])
    px, py, pz = t.sep(t.n("GeometryNodeInputPosition").outputs[0])
    ex2 = t.env(**{**ex.names, "x": px, "y": py, "z": pz})
    for label, key, formula, _ in families:
        curves.append(t.use(contours(), Mesh=mesh, Value=ex2(formula), Lines=fam_n[key]).outputs[0])
    pts = None
    if dots:
        on = t.inp("Dots", B, bool(values.get("dots", True)), tip="A dot at every crossing of the two line sets")
        coarse = t.n("GeometryNodeSetPosition", Geometry=_grid(t, t.m("ADD", nu, 0.0 if closed[0] else 1.0),
                                                               t.m("ADD", nv, 0.0 if closed[1] else 1.0)), Position=position)
        pts = t.switch(on, t.n("GeometryNodeMeshToPoints", Mesh=coarse, Radius=0.01).outputs[0])
    return _finish(t, curves, mesh, values, pts)


def solid(name, mesh_fn, families, params=(), values=None, let=()):
    """Contour families [(label, key, formula of x y z and the params, count)] on any mesh.
    mesh_fn(t, env) -> mesh socket; see param_mesh, implicit_mesh, tube_mesh, object_mesh."""
    values = values or {}
    t = T(name)
    lines = {key: t.inp(label, I, int(values.get(key, count)), 0, 400, f"Number of lines: contours of {formula}")
             for label, key, formula, count in families}
    env = _params(t, params, values)
    mesh = t.n("GeometryNodeTriangulate", Mesh=mesh_fn(t, env)).outputs[0]
    px, py, pz = t.sep(t.n("GeometryNodeInputPosition").outputs[0])
    ex = _let(t.env(**{**env, "x": px, "y": py, "z": pz}), let)
    curves = [t.use(contours(), Mesh=mesh, Value=ex(formula), Lines=lines[key]).outputs[0]
              for _, key, formula, _ in families]
    return _finish(t, curves, mesh, values)


def param_mesh(x, y, z, u=(0.0, 1.0), v=(0.0, 1.0), res=(200, 100), let=()):
    """mesh_fn for solid(): a parametric surface (a torus, say)."""
    def build(t, env):
        ex = _uv_env(t, env, u, v, let)
        return t.n("GeometryNodeSetPosition", Geometry=_grid(t, res[0], res[1]),
                   Position=t.comb(ex(x), ex(y), ex(z))).outputs[0]
    return build


def tube_mesh(x, y, z, radius="0.3", points=400, sides=32, let=()):
    """mesh_fn for solid(): a tube round the closed curve x, y, z(s), s in 0..1."""
    def build(t, env):
        line = t.n("GeometryNodeResampleCurve", Curve=t.n("GeometryNodeCurvePrimitiveLine", End=(1.0, 0.0, 0.0)), Count=points)
        ex = t.env(**env, idx=t.n("GeometryNodeInputIndex").outputs[0])
        ex.names["s"] = ex(f"idx / {points}")
        _let(ex, let)
        path = t.n("GeometryNodeSetPosition", Geometry=line, Position=t.comb(ex(x), ex(y), ex(z)))
        path = t.n("GeometryNodeSetSplineCyclic", Curve=path, Cyclic=True)
        ring = t.n("GeometryNodeCurvePrimitiveCircle", mode="RADIUS", Resolution=sides, Radius=ex(radius))
        return t.n("GeometryNodeCurveToMesh", Curve=path, Profile__Curve=ring).outputs[0]
    return build


def implicit_mesh(formula, bounds=1.2, res=96, let=()):
    """mesh_fn for solid(): the region where formula(x, y, z) > 0, inside a cube of half-size `bounds`."""
    def build(t, env):
        n = t.inp("Resolution", I, res, 16, 256, "Voxels across the form: smoothness, and build time")
        px, py, pz = t.sep(t.n("GeometryNodeInputPosition").outputs[0])
        e = _let(t.env(**{**env, "x": px, "y": py, "z": pz}), let)
        cube = t.n("GeometryNodeVolumeCube", Density=e(formula), Background=-1.0,
                   Min=(-bounds,) * 3, Max=(bounds,) * 3, Resolution__X=n, Resolution__Y=n, Resolution__Z=n)
        return t.n("GeometryNodeVolumeToMesh", Volume=cube, Threshold=0.0, Adaptivity=0.0).outputs[0]
    return build


def object_mesh(default=None, subdivide=2, smooth=4, voxel=0.02):
    """mesh_fn for solid(): any mesh object, picked on the modifier. The mesh is rebuilt from its
    distance field, so a low-poly or untidy source still gives smooth, closed slices."""
    def build(t, env):
        ob = t.inp("Object", OBJ, tip="The mesh to slice")
        info = t.n("GeometryNodeObjectInfo", transform_space="ORIGINAL", Object=ob)
        geo = info.outputs["Geometry"]
        if subdivide:
            geo = t.n("GeometryNodeSubdivisionSurface", Mesh=geo, Level=subdivide).outputs[0]
        if voxel:
            size = t.inp("Voxel Size", F, voxel, 0.004, 0.5, "Detail of the rebuilt mesh: smaller is finer and slower")
            grid = t.n("GeometryNodeMeshToSDFGrid", Mesh=geo, Voxel__Size=size, Band__Width=3)
            grid = t.n("GeometryNodeSDFGridFillet", Grid=grid, Iterations=2)
            geo = t.n("GeometryNodeGridToMesh", Grid=grid, Threshold=0.0, Adaptivity=0.0).outputs[0]
        if smooth:      # relax the facets a low-poly source leaves, so the slices run smooth
            pos = t.n("GeometryNodeBlurAttribute", data_type="FLOAT_VECTOR", Value=t.n("GeometryNodeInputPosition").outputs[0],
                      Iterations=smooth)
            geo = t.n("GeometryNodeSetPosition", Geometry=geo, Position=first(pos.outputs)).outputs[0]
        return geo
    return build


def sphere_field(name, formula, params=(), lines=14, values=None, detail=6, let=(), keep=None, smooth=3, relief=False):
    """Contours of formula(x, y, z, lon, lat, params) on the unit sphere. harmonic(l, m) is available.
    relief: adds a "Relief" slider that pushes the surface in and out by the field (lobes)."""
    values = values or {}
    t = T(name)
    n = t.inp("Lines", I, int(values.get("lines", lines)), 0, 400, "Number of contour levels")
    phase = t.inp("Phase", F, float(values.get("phase", 0.0)), 0.0, 1.0, "Slides the lines through the field. Animate it")
    env = _params(t, params, values)
    det = t.inp("Detail", I, int(values.get("detail", detail)), 2, 7, "Sphere subdivisions the contours are cut from")
    ico = t.n("GeometryNodeMeshIcoSphere", Radius=1.0, Subdivisions=det)
    pos = t.n("GeometryNodeInputPosition").outputs[0]
    unit = t.vm("NORMALIZE", pos)
    x, y, z = t.sep(unit)

    def harm(l, m, tilt=0.0, turn=0.0):
        vec = t.rot(t.rot(unit, "Z_AXIS", turn), "X_AXIS", tilt) if not (tilt == 0.0 and turn == 0.0) else unit
        g = t.use(harmonic(), L=l, M=m, Vector=vec)
        # Scaled to +-1 on this sphere, so two harmonics mix evenly.
        st = t.n("GeometryNodeAttributeStatistic", data_type="FLOAT", domain="POINT", Geometry=ico, Attribute=g.outputs[0])
        return t.m("DIVIDE", g.outputs[0], t.m("MAXIMUM", st.outputs["Max"], 1e-9))

    ex = t.env(**env, x=x, y=y, z=z, harmonic=harm)
    ex.names["lon"] = ex("atan2(y, x)")
    ex.names["lat"] = ex("asin(clamp(z, -1, 1))")
    _let(ex, let)
    field = ex(formula)
    mesh = ico.outputs[0]
    if relief:
        amount = t.inp("Relief", F, float(values.get("relief", 0.3)), -1.0, 1.0,
                       "Pushes the surface out where the field is high and in where it is low. 0: a plain sphere")
        st = t.n("GeometryNodeAttributeStatistic", data_type="FLOAT", domain="POINT", Geometry=ico, Attribute=field)
        scaled = t.m("DIVIDE", field, t.m("MAXIMUM", t.m("MAXIMUM", st.outputs["Max"], t.m("MULTIPLY", st.outputs["Min"], -1.0)), 1e-9))
        mesh = t.store(mesh, "_field", field)
        mesh = t.n("GeometryNodeSetPosition", Geometry=mesh,
                   Position=t.vm("SCALE", unit, scale=t.m("ADD", 1.0, t.m("MULTIPLY", amount, scaled)))).outputs[0]
        mesh = t.n("GeometryNodeTriangulate", Mesh=mesh).outputs[0]
        field = t.attr("_field")      # the field was a formula of the position, which has just moved
        keep_f = True
    iso = t.use(contours(), Mesh=mesh, Value=field, Lines=n, Phase=phase, Keep=ex(keep) if keep and not relief else True)
    # Marching triangles leaves a corner at every triangle edge where the field bends; relax them.
    relaxed = t.n("GeometryNodeBlurAttribute", data_type="FLOAT_VECTOR", Value=pos, Iterations=smooth)
    target = first(relaxed.outputs) if relief else t.vm("NORMALIZE", first(relaxed.outputs))
    on_surface = t.n("GeometryNodeSetPosition", Geometry=iso, Position=target)
    return _finish(t, [on_surface.outputs[0]], mesh, values)


def curve_family(name, x, y, z, count, params=(), points=128, cyclic=True, values=None, occluder=None, let=()):
    """`count` curves (a formula of the params) of `points` points each. Formula names: t (0..1 along
    the curve), i (curve number), n (curve count), and the params. occluder: radius of a sphere that
    hides lines behind it (and gets an outline), or None."""
    values = values or {}
    t = T(name)
    env = _params(t, params, values)
    m = t.inp("Points", I, int(values.get("points", points)), 8, 2048, "Points along each curve")
    ex = t.env(**env)
    n = ex(count)
    line = t.n("GeometryNodeCurvePrimitiveLine", End=(1.0, 0.0, 0.0))
    line = t.n("GeometryNodeResampleCurve", Curve=line, Count=m)
    inst = t.n("GeometryNodeInstanceOnPoints", Points=t.n("GeometryNodePoints", Count=n), Instance=line)
    real = t.n("GeometryNodeRealizeInstances", Geometry=inst)
    idx = t.n("GeometryNodeInputIndex").outputs[0]
    e2 = t.env(**env, idx=idx, m=m, n=n)
    e2.names["i"] = e2("floor((idx + 0.5) / m)")
    e2.names["t"] = e2("mod(idx, m) / m") if cyclic else e2("mod(idx, m) / max(m - 1, 1)")
    _let(e2, let)
    moved = t.n("GeometryNodeSetPosition", Geometry=real, Position=t.comb(e2(x), e2(y), e2(z)))
    curves = t.n("GeometryNodeSetSplineCyclic", Curve=moved, Cyclic=cyclic).outputs[0]
    if occluder:
        ball = t.n("GeometryNodeMeshIcoSphere", Radius=float(occluder), Subdivisions=5).outputs[0]
    else:
        ball = t.n("GeometryNodeJoinGeometry").outputs[0]
    return _finish(t, [curves], ball, values)
