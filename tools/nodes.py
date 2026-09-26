"""Node helpers for the hand-off pattern from wonder-popart: every material is ONE
group node with the key controls on its inputs, so a designer tweaks one node.

    from nodes import group, use, material_from_group, math, auto_layout, how_to_tweak

    ng, gi, go = group("Look Plastic", [
        ("Colour", "NodeSocketColor", (0.9, 0.3, 0.1, 1), None, None),
        ("Gloss", "NodeSocketFloat", 0.7, 0.0, 1.0),   # 0 = matte, 1 = mirror
    ], [("Shader", "NodeSocketShader")])
    ... build the internals inside ng, wiring gi.outputs[...] → nodes → go.inputs[...]
    auto_layout(ng)
    obj.data.materials.append(material_from_group("Plastic", ng))
"""
import bpy


def group(name, ins, outs, kind="ShaderNodeTree"):
    """ins = [(name, socket_type, default, min, max)], outs = [(name, socket_type)].
    Returns (node_group, group_input_node, group_output_node)."""
    ng = bpy.data.node_groups.new(name, kind)
    for n, sock_type, default, lo, hi in ins:
        s = ng.interface.new_socket(n, in_out="INPUT", socket_type=sock_type)
        if default is not None:
            s.default_value = default
        if lo is not None:
            s.min_value, s.max_value = lo, hi
    for n, sock_type in outs:
        ng.interface.new_socket(n, in_out="OUTPUT", socket_type=sock_type)
    return ng, ng.nodes.new("NodeGroupInput"), ng.nodes.new("NodeGroupOutput")


def use(nt, ng, label=None):
    """Instance a node group inside another tree."""
    g = nt.nodes.new("ShaderNodeGroup" if ng.bl_idname == "ShaderNodeTree" else "CompositorNodeGroup")
    g.node_tree = ng
    if label:
        g.label = label
    return g


def material_from_group(name, ng, output="Shader"):
    """A material whose whole tree is one wide group node → Material Output."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    g = use(nt, ng)
    g.location, g.width = (0, 0), 260
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (360, 0)
    nt.links.new(g.outputs[output], out.inputs["Surface"])
    return m


def math(nt, op, a, b=None, c=None, clamp=False):
    """ShaderNodeMath; each operand is a socket (linked) or a number (set)."""
    m = nt.nodes.new("ShaderNodeMath")
    m.operation, m.use_clamp = op, clamp
    for i, v in enumerate((a, b, c)):
        if v is None:
            continue
        if hasattr(v, "bl_rna"):
            nt.links.new(v, m.inputs[i])
        else:
            m.inputs[i].default_value = v
    return m.outputs[0]


def auto_layout(nt, dx=220, dy=200):
    """One column per dependency depth, so group internals stay readable."""
    depth = {}

    def d(n):
        if n.name not in depth:
            depth[n.name] = 0
            depth[n.name] = 1 + max((d(l.from_node) for l in nt.links if l.to_node == n), default=-1)
        return depth[n.name]

    cols = {}
    for n in nt.nodes:
        cols.setdefault(d(n), []).append(n)
    for c, ns in cols.items():
        for i, n in enumerate(ns):
            n.location = (c * dx, -i * dy)


def how_to_tweak(text):
    """Add or replace the HOW_TO_TWEAK text block shown in the Text Editor."""
    t = bpy.data.texts.get("HOW_TO_TWEAK") or bpy.data.texts.new("HOW_TO_TWEAK")
    t.clear()
    t.write(text)
    return t
