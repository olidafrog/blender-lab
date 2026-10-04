"""Compositor hand-off pattern (Blender 4.4 and 5.x): live preview plus one-node controls.

    Render Layers ─┐
                   ├─ Source group ─ [Post group node] ─┬─ Group Output (final image)
    Saved render ──┘  (one switch     one node, key       └─ Viewer (draws the backdrop)
      (EXR)            for every       inputs; Tab to see
                       pass)           the constituent nodes
    Render Layers ─ File Output → renders/<out>_raw.exr (same render, no second pass)

AOVs the Post group needs (masks, glow sources) go in `passes`; they ride the same switch
and are saved in the same multilayer EXR.

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


def compositor(scene, post_ng=None, raw_exr=None, passes=()):
    """Build the scene compositor. `raw_exr`: where the File Output node writes the
    linear pre-post passes during the render. `passes`: extra Render Layers outputs
    (AOV names) the Post group needs, as (render_layer_output, post_input) pairs.
    They go through the same Source switch and into the same EXR as the Image.
    5.x only: on 4.4 a switch is a node property, so a group cannot drive it."""
    if LEGACY:
        if passes:
            raise NotImplementedError("compositor(passes=...) needs the 5.x compositor")
        scene.use_nodes = True
        tree = scene.node_tree
        tree.nodes.clear()
    else:
        tree = bpy.data.node_groups.new("Compositor", "CompositorNodeTree")
        scene.compositing_node_group = tree
        tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    scene.render.use_compositing = True
    n = tree.nodes
    chans = [("Image", "Image")] + list(passes)

    rl = n.new("CompositorNodeRLayers")
    saved = n.new("CompositorNodeImage")
    saved.name = saved.label = "Saved Render"
    if LEGACY:  # one plain switch; "check" is On = saved render
        src = n.new("CompositorNodeSwitch")
        src.name = src.label = "Source"
        _set_switch(src, False)
        tree.links.new(rl.outputs["Image"], src.inputs["Off"])
        tree.links.new(saved.outputs["Image"], src.inputs["On"])
    else:
        src = use(tree, _source_group([c for c, _ in chans]), "Source")
        src.name = "Source"
        for c, _ in chans:
            tree.links.new(rl.outputs[c], src.inputs[f"Live {c}"])
        tree.links.new(saved.outputs["Image"], src.inputs["Saved Image"])

    final = src.outputs[0]  # "Image": the first output on both paths
    if post_ng is not None:
        post = use(tree, post_ng)
        post.name, post.width = "Post", 260
        tree.links.new(final, post.inputs["Image"])
        for c, sock in passes:
            tree.links.new(src.outputs[c], post.inputs[sock])
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
            tree.links.new(rl.outputs["Image"], fo.inputs[0])
        else:
            fo.directory = str(raw_exr.parent) + "/"
            fo.file_name = raw_exr.stem
            fo.format.file_format = "OPEN_EXR_MULTILAYER"  # 5.2 offers only multilayer here
            fo.format.color_depth = "16"  # half float: plenty for a preview, half the size
            for c, _ in chans:
                fo.file_output_items.new("FLOAT" if rl.outputs[c].type == "VALUE" else "RGBA", c)
                tree.links.new(rl.outputs[c], fo.inputs[c])

    auto_layout(tree, dx=300)
    return tree


def _source_group(chans):
    """One switch for every pass: Live (Render Layers) or Saved (the EXR)."""
    ins = [("Use Saved Render", "NodeSocketBool", False, None, None)]
    for c in chans:
        ins += [(f"Live {c}", "NodeSocketColor", None, None, None),
                (f"Saved {c}", "NodeSocketColor", None, None, None)]
    ng, gi, go = group("Source", ins, [(c, "NodeSocketColor") for c in chans], kind="CompositorNodeTree")
    for c in chans:
        sw = ng.nodes.new("CompositorNodeSwitch")
        ng.links.new(gi.outputs["Use Saved Render"], sw.inputs["Switch"])
        ng.links.new(gi.outputs[f"Live {c}"], sw.inputs["Off"])
        ng.links.new(gi.outputs[f"Saved {c}"], sw.inputs["On"])
        ng.links.new(sw.outputs[0], go.inputs[c])
    auto_layout(ng)
    return ng


def shrink_exr(path):
    """Re-encode an EXR in place as half float with DWAA compression, keeping every layer (from apartment-model:
    a 2x render's raw EXR was 100 MB, over GitHub's limit; after this ~1-4 MB with the same pixel stats).
    Uses the OpenImageIO bindings bundled with Blender 5.x."""
    import OpenImageIO as oiio
    path = Path(path)
    buf = oiio.ImageBuf(str(path))
    buf.set_write_format(oiio.HALF)
    buf.specmod().attribute("compression", "dwaa:45")
    tmp = path.with_suffix(".tmp.exr")
    assert buf.write(str(tmp)), buf.geterror()
    tmp.replace(path)
    print(f"[out] {path.name}: {path.stat().st_size / 1e6:.1f} MB")


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
    saved, src = tree.nodes["Saved Render"], tree.nodes["Source"]
    saved.image = img
    if LEGACY:
        _set_switch(src, True)
    else:
        # The EXR's layers appear as outputs only once the image is loaded; wire the extra passes now.
        for sock in saved.outputs:
            tgt = src.inputs.get(f"Saved {sock.name}")
            if tgt is not None and sock.name != "Image":
                tree.links.new(sock, tgt)
        src.inputs["Use Saved Render"].default_value = True
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
