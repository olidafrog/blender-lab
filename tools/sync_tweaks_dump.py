"""Blender side of tools/sync_tweaks.py: dump the designer-facing values of the open scene to JSON.

  BLEND=<file.blend> tools/blender.sh tools/sync_tweaks_dump.py -- <out.json>
  tools/blender.sh tools/sync_tweaks_dump.py -- <out.json> --build <build.py>   # build fresh, then dump

Values: every group-node input on every material ("Material/Group/Input"), the Post group's inputs,
each light's energy, colour, size, angle and rotation, the camera's lens and shifts, the view transform
and exposure.
"""
import json
import runpy
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
out = argv[0]
if "--build" in argv:
    build = argv[argv.index("--build") + 1]
    sys.argv = [build, "--", "--norender"]
    runpy.run_path(build, run_name="__main__")


def val(v):
    try:
        return [round(float(x), 6) for x in v]
    except TypeError:
        return round(float(v), 6) if isinstance(v, (int, float)) else v


d = {}
for m in bpy.data.materials:
    if not m.node_tree:
        continue
    for n in m.node_tree.nodes:
        if n.bl_idname == "ShaderNodeGroup" and n.node_tree:
            for s in n.inputs:
                if hasattr(s, "default_value") and not s.is_linked:
                    d[f"{m.name}/{n.node_tree.name}/{s.name}"] = val(s.default_value)
sc = bpy.context.scene
tree = getattr(sc, "compositing_node_group", None) or getattr(sc, "node_tree", None)
if tree:
    for n in tree.nodes:
        if n.bl_idname == "CompositorNodeGroup" and n.node_tree and n.node_tree.name.startswith("Post"):
            for s in n.inputs:
                if hasattr(s, "default_value") and not s.is_linked:
                    d[f"Compositor/{n.node_tree.name}/{s.name}"] = val(s.default_value)
for ob in bpy.data.objects:
    if ob.type == "LIGHT":
        L = ob.data
        d[f"Light/{ob.name}/energy"] = val(L.energy)
        d[f"Light/{ob.name}/color"] = val(L.color)
        for k in ("size", "size_y", "angle", "spot_size"):
            if hasattr(L, k):
                d[f"Light/{ob.name}/{k}"] = val(getattr(L, k))
        d[f"Light/{ob.name}/rotation"] = val(ob.rotation_euler)
        d[f"Light/{ob.name}/location"] = val(ob.location)
    elif ob.type == "CAMERA":
        for k in ("lens", "shift_x", "shift_y"):
            d[f"Camera/{ob.name}/{k}"] = val(getattr(ob.data, k))
d["View/exposure"] = val(sc.view_settings.exposure)
d["View/view_transform"] = sc.view_settings.view_transform
json.dump(d, open(out, "w"), indent=0)
print(f"[out] dumped {len(d)} values to {out}")
