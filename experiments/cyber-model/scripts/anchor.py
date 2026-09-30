"""Anchor image for the reviewer's scale: a plain stack of grey boxes, same camera, light and backdrop.
   tools/blender.sh experiments/cyber-model/scripts/anchor.py"""
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as B  # noqa: E402  (module-level code in build.py only runs under __main__)
from hs_kit import box, tube  # noqa: E402

B.P["res_x"], B.P["res_y"] = 1600, 1200
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
B.enable_gpu(sc)
B.mats()
B.add_backdrop()
grey = bpy.data.materials.new("AnchorGrey")
grey.use_nodes = True
grey.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.12, 0.12, 0.12, 1)
grey.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
for nm, size, c in (("b1", (111, 185, 12), (0, 0, 6)), ("b2", (95, 120, 8), (8, 15, 16)), ("b3", (65, 36, 6), (-7, 60, 21)),
                    ("b4", (34, 40, 4), (50, -5, 19))):
    o = box(nm, size, c)
    o.data.materials.append(grey)
    B.hard_edges(o, 0.3, 1)
a = tube("ant", (-20, 90, 19), (-60, 170, 19), 4, segs=24)
a.data.materials.append(grey)
B.add_camera(sc, "hero")
B.add_lights(sc, "hero")
sc.view_settings.view_transform = B.P["view"]
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.render.resolution_percentage = 100
sc.render.filepath = str(B.EXP["root"] / "reviews" / "anchor_score4.png")
bpy.ops.render.render(write_still=True)
print("BUILD OK")
