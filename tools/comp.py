"""Compositor hand-off pattern (Blender 4.4 and 5.x): live preview plus one-node controls.

    Render Layers ─┐
                   ├─ Source switch ─ [Post group node] ─┬─ Group Output (final image)
    Saved render ──┘   (EXR)            one node, key      └─ Viewer (draws the backdrop)
                                        inputs; Tab to see
                                        the constituent nodes
    Render Layers ─ File Output → renders/<out>_raw.exr (same render, no second pass)

In the saved .blend the Compositing tab has the backdrop on and the saved EXR as the
source, so every slider on the Post node updates the image at once, no re-render.

    from comp import compositor, use_saved_render, post_group
    ng, gi, go = post_group("Post", [("Glow", "NodeSocketFloat", 0.8, 0.0, 2.0)])
    ... build glare/lens nodes inside ng from gi.outputs["Image"] to go.inputs["Image"]
    tree = compositor(scene, ng, raw_exr=EXP["renders"] / "v01_raw.exr")
    render ...
    use_saved_render(scene, EXP["renders"] / "v01_raw.exr", EXP["output"])   # before --save

On 4.4 (LEGACY) the tree is scene.node_tree and ends in a Composite node. Node settings
there are properties, not sockets, so a Post group input cannot drive a Glare or Blur
setting: set those on the node and keep only socket-valued controls on the group.
"""
import shutil
from pathlib import Path

import bpy

from nodes import auto_layout, group, use

LEGACY = "node_tree" in bpy.types.Scene.bl_rna.properties  # 4.x compositor API


def post_group(name, ins):
    """A compositor group with an Image in/out plus the designer inputs `ins`
    (same tuples as nodes.group). Returns (group, input_node, output_node)."""
    return group(name, [("Image", "NodeSocketColor", None, None, None)] + list(ins),
                 [("Image", "NodeSocketColor")], kind="CompositorNodeTree")


def compositor(scene, post_ng=None, raw_exr=None):
    """Build the scene compositor. `raw_exr`: where the File Output node writes the
    linear pre-post beauty pass during the render."""
    if LEGACY:
        scene.use_nodes = True
        tree = scene.node_tree
        tree.nodes.clear()
    else:
        tree = bpy.data.node_groups.new("Compositor", "CompositorNodeTree")
        scene.compositing_node_group = tree
        tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    scene.render.use_compositing = True
    n = tree.nodes

    rl = n.new("CompositorNodeRLayers")
    saved = n.new("CompositorNodeImage")
    saved.name = saved.label = "Saved Render"
    switch = n.new("CompositorNodeSwitch")
    switch.name = switch.label = "Source (On = saved render)"
    _set_switch(switch, False)
    tree.links.new(rl.outputs["Image"], switch.inputs["Off"])
    tree.links.new(saved.outputs["Image"], switch.inputs["On"])

    final = switch.outputs[0]
    if post_ng is not None:
        post = use(tree, post_ng)
        post.name, post.width = "Post", 240
        tree.links.new(final, post.inputs["Image"])
        final = post.outputs["Image"]

    out = n.new("CompositorNodeComposite" if LEGACY else "NodeGroupOutput")
    viewer = n.new("CompositorNodeViewer")
    tree.links.new(final, out.inputs["Image"])
    tree.links.new(final, viewer.inputs["Image"])

    if raw_exr is not None:
        raw_exr = Path(raw_exr)
        fo = n.new("CompositorNodeOutputFile")
        fo.name = fo.label = "Raw EXR"
        if LEGACY:
            fo.base_path = str(raw_exr.parent) + "/"
            fo.format.file_format = "OPEN_EXR"
            fo.format.color_depth = "32"
            fo.file_slots[0].path = raw_exr.stem
        else:
            fo.directory = str(raw_exr.parent) + "/"
            fo.file_name = raw_exr.stem
            fo.format.file_format = "OPEN_EXR_MULTILAYER"  # 5.2 offers only multilayer here
            fo.format.color_depth = "32"
            fo.file_output_items.new("RGBA", "Image")
        tree.links.new(rl.outputs["Image"], fo.inputs[0])

    auto_layout(tree, dx=300)
    return tree


def use_saved_render(scene, exr_path, store_dir=None):
    """Point the Saved Render node at an EXR, switch the source to it, and turn on the
    compositor backdrop, so the .blend opens ready to tweak on the Compositing tab.
    The active tab itself cannot be saved from a headless run (see knowledge)."""
    tree = scene.node_tree if LEGACY else scene.compositing_node_group
    fo = tree.nodes.get("Raw EXR")
    if fo is not None:
        tree.nodes.remove(fo)  # a later F12 in the GUI must not overwrite the saved pass
    exr_path = _written(Path(exr_path))
    if store_dir is not None:  # keep the preview source next to the .blend, not in renders/
        dst = Path(store_dir) / exr_path.name
        shutil.copyfile(exr_path, dst)
        exr_path = dst
    img = bpy.data.images.load(str(exr_path), check_existing=True)
    img.colorspace_settings.name = "Linear Rec.709"
    tree.nodes["Saved Render"].image = img
    _set_switch(tree.nodes["Source (On = saved render)"], True)
    for scr in bpy.data.screens:
        for area in scr.areas:
            for sp in area.spaces:
                if sp.type == "NODE_EDITOR":
                    sp.tree_type = "CompositorNodeTree"
                    sp.show_backdrop = True
                    sp.backdrop_zoom = 0.5


def _set_switch(node, on):
    if LEGACY:
        node.check = on          # 4.4: a node property
    else:
        node.inputs["Switch"].default_value = on


def _written(p):
    """File Output appends a frame number; find what was actually written."""
    if p.exists():
        return p
    hits = sorted(p.parent.glob(p.stem + "*.exr"))
    if not hits:
        raise FileNotFoundError(p)
    return hits[-1]
