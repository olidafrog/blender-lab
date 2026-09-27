"""Check the hand-off .blend: one group node per material, ranged inputs, HOW_TO_TWEAK,
the saved-render EXR, and a 1-sample render from the saved source.

    BLEND=experiments/wonder-minidisc/output/wonder-minidisc.blend tools/blender.sh experiments/wonder-minidisc/scripts/verify_blend.py
"""
from pathlib import Path

import bpy

ok = True
for m in bpy.data.materials:
    if not m.use_nodes or m.name in ("Flag Black", "Clay"):
        continue
    groups = [n for n in m.node_tree.nodes if n.bl_idname == "ShaderNodeGroup"]
    others = [n for n in m.node_tree.nodes if n.bl_idname not in ("ShaderNodeGroup", "ShaderNodeOutputMaterial")]
    ranged = all(getattr(s, "min_value", 0) != getattr(s, "max_value", 0)
                 for s in groups[0].node_tree.interface.items_tree
                 if getattr(s, "in_out", "") == "INPUT" and s.socket_type == "NodeSocketFloat") if groups else False
    good = len(groups) == 1 and not others and ranged
    ok &= good
    print(f"[out] material {m.name}: groups {len(groups)}, extra nodes {len(others)}, ranged {ranged} -> {'OK' if good else 'FAIL'}")
print(f"[out] HOW_TO_TWEAK: {'HOW_TO_TWEAK' in bpy.data.texts}")
ok &= "HOW_TO_TWEAK" in bpy.data.texts
tree = bpy.context.scene.node_tree
img = tree.nodes["Saved Render"].image if tree and "Saved Render" in tree.nodes else None
exr = Path(bpy.path.abspath(img.filepath)) if img else None
print(f"[out] saved render: {exr} exists {bool(exr and exr.exists())}")
ok &= bool(exr and exr.exists())
missing = [i.name for i in bpy.data.images if i.filepath and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).exists()]
print(f"[out] missing images: {missing}")
scene = bpy.context.scene
scene.cycles.samples = 1
scene.render.resolution_percentage = 100  # the saved EXR is full size; a smaller render crops it
scene.render.filepath = str(Path(bpy.data.filepath).parent / "verify_1spp.png")
bpy.ops.render.render(write_still=True)
print(f"[out] VERIFY {'OK' if ok else 'FAIL'}")
