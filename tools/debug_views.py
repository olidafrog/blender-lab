"""Debug renders for checking a model you cannot look at directly (Workbench, about a second each).

    from debug_views import subject_mask, debug_sheet
    subject_mask(scene, renders / "v01_mask.png", hide=["Cyc"])           # for tools/silhouette.py
    debug_sheet(scene, renders / "v01_sheet.png", height=1.7, hide=["Cyc"])

subject_mask: the subject in black on a transparent background, from the scene camera.
debug_sheet: orthographic front, side and back views plus the scene camera, side by side, one
random colour per object, outlines on and backface culling on, so intersections, hidden parts
and flipped normals (holes) show. `height` is the subject's height in metres; the ortho views
frame it with a small margin around `centre` (x, y on the floor).

Both restore the render engine, film, compositing, camera and hide flags they change, so they can
run after a Cycles render or before a save. From roman-model (knowledge/gotchas/modelling.md).
"""
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector


class _Kept:
    """Remember scene settings and hide flags; put them back on exit."""

    def __init__(self, scene, hide):
        self.scene, self.hide = scene, [bpy.data.objects[n] for n in hide if n in bpy.data.objects]

    def __enter__(self):
        s, r = self.scene, self.scene.render
        self.saved = (r.engine, r.film_transparent, r.use_compositing, r.filepath,
                      r.resolution_x, r.resolution_y, r.resolution_percentage)
        self.cam = (s.camera.location.copy(), s.camera.rotation_euler.copy(), s.camera.data.type,
                    s.camera.data.ortho_scale)
        self.hidden = [o.hide_render for o in self.hide]
        for o in self.hide:
            o.hide_render = True
        r.engine = "BLENDER_WORKBENCH"
        r.use_compositing = False
        s.display.render_aa = "8"
        return self

    def __exit__(self, *exc):
        s, r = self.scene, self.scene.render
        (r.engine, r.film_transparent, r.use_compositing, r.filepath,
         r.resolution_x, r.resolution_y, r.resolution_percentage) = self.saved
        c = s.camera
        c.location, c.rotation_euler, c.data.type, c.data.ortho_scale = self.cam
        for o, h in zip(self.hide, self.hidden):
            o.hide_render = h


def _render(scene, path):
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def subject_mask(scene, path, hide=()):
    """Black subject, transparent background, scene camera. Returns the path."""
    with _Kept(scene, hide):
        sh = scene.display.shading
        sh.light, sh.color_type, sh.single_color = "FLAT", "SINGLE", (0, 0, 0)
        scene.render.film_transparent = True
        _render(scene, path)
    return Path(path)


def debug_sheet(scene, path, height, centre=(0.0, 0.0), size=700, hide=()):
    """Front, side, back (orthographic) and the scene camera in one PNG. Returns the path."""
    path = Path(path)
    cx, cy = centre
    z = height / 2
    views = [("front", (cx, cy - 12, z)), ("side", (cx + 12, cy, z)), ("back", (cx, cy + 12, z)), ("camera", None)]
    tiles = []
    with _Kept(scene, hide) as kept:
        sh = scene.display.shading
        sh.light, sh.color_type = "STUDIO", "RANDOM"
        sh.show_object_outline = True
        sh.show_backface_culling = True          # flipped normals show as holes
        scene.render.film_transparent = False
        scene.render.resolution_x = scene.render.resolution_y = size
        scene.render.resolution_percentage = 100
        cam = scene.camera
        for name, loc in views:
            if loc:
                cam.data.type, cam.data.ortho_scale = "ORTHO", height * 1.15
                cam.location = loc
                cam.rotation_euler = (Vector((cx, cy, z)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
            else:
                cam.location, cam.rotation_euler, cam.data.type, cam.data.ortho_scale = kept.cam
            tmp = path.with_name(f"_{path.stem}_{name}.png")
            _render(scene, tmp)
            img = bpy.data.images.load(str(tmp))
            tiles.append(np.array(img.pixels[:], dtype=np.float32).reshape(size, size, 4))
            bpy.data.images.remove(img)
            tmp.unlink()
    big = np.concatenate(tiles, axis=1)
    im = bpy.data.images.new(path.stem, big.shape[1], big.shape[0], alpha=True)
    im.pixels.foreach_set(big.ravel())
    im.filepath_raw = str(path)
    im.file_format = "PNG"
    im.save()
    bpy.data.images.remove(im)
    print(f"Saved {path}")
    return path
