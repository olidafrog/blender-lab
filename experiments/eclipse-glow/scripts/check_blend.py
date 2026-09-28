"""Check the hand-off .blend: one control node per material, ranged inputs, HOW_TO_TWEAK, and a
compositor preview that reproduces the final PNG from the saved EXR.

    BLEND=experiments/eclipse-glow/output/eclipse_logo.blend \
        tools/blender.sh experiments/eclipse-glow/scripts/check_blend.py <final.png>
"""
import sys
from pathlib import Path

import bpy
import numpy as np

png = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
sc = bpy.context.scene
bad = []

m = bpy.data.materials["Eclipse Glow"]
groups = [n for n in m.node_tree.nodes if n.bl_idname == "ShaderNodeGroup"]
if len(groups) != 1:
    bad.append(f"material has {len(groups)} group nodes")
for ng in (groups[0].node_tree, bpy.data.node_groups["Post"], bpy.data.node_groups["Inflate Logo"]):
    for it in ng.interface.items_tree:
        if it.item_type == "SOCKET" and it.in_out == "INPUT" and hasattr(it, "min_value") \
                and "Pass" not in it.name and it.min_value == it.max_value:
            bad.append(f"{ng.name}.{it.name} has no range")
if "HOW_TO_TWEAK" not in bpy.data.texts:
    bad.append("no HOW_TO_TWEAK")
tree = sc.compositing_node_group
saved, src = tree.nodes["Saved Render"], tree.nodes["Source"]
exr = Path(bpy.path.abspath(saved.image.filepath))
if not exr.exists():
    bad.append(f"missing EXR {exr}")
for s in src.inputs:
    if s.name.startswith("Saved") and not s.is_linked:
        bad.append(f"Source.{s.name} not linked")
if not src.inputs["Use Saved Render"].default_value:
    bad.append("Source not on the saved render")
if sc.render.film_transparent:
    bad.append("film is transparent")

# Re-composite from the saved EXR (1 sample: the 3D render is ignored) and compare.
sc.cycles.samples = 1
out = Path(bpy.app.tempdir) / "check.png"
sc.render.filepath = str(out)
bpy.ops.render.render(write_still=True)
a = bpy.data.images.load(str(out)); b = bpy.data.images.load(str(png))
if tuple(a.size) != tuple(b.size):
    bad.append(f"size {tuple(a.size)} vs final {tuple(b.size)}")
else:
    pa, pb = np.array(a.pixels[:]), np.array(b.pixels[:])
    d = np.abs(pa - pb) * 255
    print(f"[out] preview vs final: mean {d.mean():.2f}/255, max {d.max():.0f}/255")
    if d.mean() > 1.0:
        bad.append("preview does not match the final")
print("[out] " + ("CHECK OK" if not bad else "CHECK FAILED: " + "; ".join(bad)))
