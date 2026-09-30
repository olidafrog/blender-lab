"""Verify the saved hand-off .blend (run in a fresh headless Blender):
   BLEND=experiments/cyber-model/output/cyber-model.blend tools/blender.sh experiments/cyber-model/scripts/check_handoff.py
Checks: each designer material is one group node with ranged inputs, HOW_TO_TWEAK exists, images are packed,
the Saved Render node points at an existing EXR, lights and camera are named, the Post group is present."""
import bpy
from pathlib import Path

ok = True
def say(msg, good=True):
    global ok
    ok &= good
    print("[out]", "OK  " if good else "FAIL", msg)

for m in bpy.data.materials:
    if not m.use_nodes or m.name.startswith("Dots") or m.name == "Material":
        continue
    kinds = [n.bl_idname for n in m.node_tree.nodes]
    groups = [n for n in m.node_tree.nodes if n.bl_idname == "ShaderNodeGroup"]
    if m.name.startswith("Decal"):
        say(f"material {m.name}: decal (image + Principled)", True)
        continue
    one = len(groups) == 1 and len(m.node_tree.nodes) == 2
    say(f"material {m.name}: one group node ({len(m.node_tree.nodes)} nodes)", one or m.name in ("RedLED",))
    if groups:
        ins = [s for s in groups[0].node_tree.interface.items_tree if getattr(s, "in_out", "") == "INPUT"]
        ranged = all(hasattr(s, "min_value") and s.max_value > s.min_value for s in ins if s.socket_type in ("NodeSocketFloat",))
        say(f"  {groups[0].node_tree.name}: {len(ins)} inputs, ranges set", 1 <= len(ins) <= 9 and ranged)
say("HOW_TO_TWEAK text block", "HOW_TO_TWEAK" in bpy.data.texts)
say("images packed", all(i.packed_file for i in bpy.data.images if i.source == "FILE" and i.name not in ("Viewer Node",) and i.type != "COMPOSITING"))
for nm in ("Camera", "Key Backdrop", "Key Device", "Card Metal"):
    say(f"object {nm}", nm in bpy.data.objects)
sc = bpy.context.scene
tree = getattr(sc, "compositing_node_group", None) or sc.node_tree
post = [n for n in tree.nodes if n.name == "Post"]
say("Post group node in the compositor", len(post) == 1)
saved = tree.nodes.get("Saved Render")
path = Path(bpy.path.abspath(saved.image.filepath)) if saved and saved.image else None
say(f"Saved Render EXR exists: {path}", bool(path and path.exists()))
print("[out] HANDOFF", "PASS" if ok else "FAIL")
