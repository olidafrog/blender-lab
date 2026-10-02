"""Preflight sheet: the correctness-pass renders in one run, before review round 1.

From a build.py (the new-experiment template has --preflight):
    from preflight import sheet
    sheet(scene, EXP["reviews"] / "preflight_v01.png", tiles_dir=EXP["renders"] / "preflight_v01")

From a saved .blend (older experiments):
    BLEND=experiments/<name>/output/<name>.blend tools/blender.sh tools/preflight.py <sheet.png> [--scale 0.25] [--samples 48]

Renders the scene camera once per variant, small and with the compositor off, and tiles them
four to a row. Each tile is also saved alone in tiles_dir. The legend prints row and column.

  beauty       as built (no compositor): the baseline for the rest
  clay         grey diffuse override: geometry, seams, bevels, intersections
  mirror       glossy metal override: smooth-shaded caps and bad normals that clay hides
  albedo0      every Principled Base Color black: what is left is reflection, emission and spill
  scatter0     Subsurface Weight 0 (only if the scene uses subsurface): what scatter adds or hides
  lights_off   every light object hidden: what the world and emissive meshes contribute
  <light>      one light alone, world off (up to `max_lights`, strongest first): veils, spill,
               a softbox mirrored in a flat top

Before rendering it prints, per light, its purpose (a `purpose` custom property set in build.py;
NO PURPOSE if missing) and its falloff across the subject: (nearest ÷ farthest distance)² over the
subject's bounding-box corners. Under 0.5 the near side gets over twice the light of the far side,
which pulls the eye there; that is a choice, so check it was meant. Subjects are the visible meshes
minus any that spill past both sides of the frame or behind the camera (floors, backdrops); pass
`subjects` to override, e.g. for a close-up the frame crops.

What to look for is in review-render, "Before round 1". Emissive meshes cannot be isolated here;
give them a --set switch in build.py. Everything changed is put back, so the scene can still be
rendered or saved afterwards. Cycles only.
"""
import sys
from contextlib import contextmanager
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector


def _principled_inputs(name):
    trees = [m.node_tree for m in bpy.data.materials if m.node_tree]
    trees += [g for g in bpy.data.node_groups if g.bl_idname == "ShaderNodeTree"]
    return [(t, n.inputs[name]) for t in trees for n in t.nodes
            if n.bl_idname == "ShaderNodeBsdfPrincipled" and name in n.inputs]


@contextmanager
def _patched(name, value):
    """Set one Principled input everywhere to a constant; restore values and links after."""
    saved = []
    for tree, sock in _principled_inputs(name):
        v = sock.default_value
        saved.append((tree, sock, v if isinstance(v, float) else tuple(v), [l.from_socket for l in sock.links]))
        for l in list(sock.links):
            tree.links.remove(l)
        sock.default_value = value
    try:
        yield
    finally:
        for tree, sock, v, sources in saved:
            sock.default_value = v
            for s in sources:
                tree.links.new(s, sock)


@contextmanager
def _override(scene, **principled):
    mat = bpy.data.materials.new("_preflight")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    for k, v in principled.items():
        bsdf.inputs[k].default_value = v
    layer = scene.view_layers[0]
    old = layer.material_override
    layer.material_override = mat
    try:
        yield
    finally:
        layer.material_override = old
        bpy.data.materials.remove(mat)


@contextmanager
def _lights(scene, lights, keep=None, world=True):
    flags = [o.hide_render for o in lights]
    old_world = scene.world
    for o in lights:
        o.hide_render = o is not keep
    if not world:
        scene.world = None
    try:
        yield
    finally:
        for o, f in zip(lights, flags):
            o.hide_render = f
        scene.world = old_world


@contextmanager
def _plain():
    yield


def _uses_subsurface():
    return any(s.is_linked or s.default_value > 0 for _, s in _principled_inputs("Subsurface Weight"))


def _corners(objects):
    return [o.matrix_world @ Vector(c) for o in objects for c in o.bound_box]


def _subjects(scene):
    """Visible meshes, minus any that spill past both sides of the frame (floors, backdrops)."""
    from bpy_extras.object_utils import world_to_camera_view
    meshes = [o for o in scene.objects if o.type == "MESH" and not o.hide_render]
    if not scene.camera:
        return meshes
    keep = []
    for o in meshes:
        uv = [world_to_camera_view(scene, scene.camera, p) for p in _corners([o])]
        xs = [p.x for p in uv]
        if min(p.z for p in uv) > 0 and not (min(xs) < 0 and max(xs) > 1):
            keep.append(o)
    return keep or meshes


def light_report(scene, lights, subjects=None):
    """Print each light's purpose and falloff across the subject. Returns {name: ratio}."""
    scene.view_layers[0].update()  # objects added in this build still have stale matrix_world
    pts = _corners(subjects if subjects is not None else _subjects(scene))
    ratios = {}
    for o in lights:
        purpose = o.get("purpose") or o.data.get("purpose") or "NO PURPOSE: set light['purpose'] in build.py, or delete it"
        if o.data.type == "SUN" or not pts:
            ratio = 1.0
        else:
            d = [(p - o.matrix_world.translation).length for p in pts]
            ratio = (min(d) / max(d)) ** 2
        ratios[o.name] = ratio
        note = "  strong: the near side draws the eye" if ratio < 0.5 else ""
        print(f"[out] light {o.name}: falloff {ratio:.2f}{note} | {purpose}")
    return ratios


def sheet(scene, out, tiles_dir=None, scale=0.25, samples=48, max_lights=8, columns=4, subjects=None):
    """Render every variant and write the tiled sheet to `out`. Returns the list of labels."""
    out = Path(out)
    tiles_dir = Path(tiles_dir) if tiles_dir else out.with_suffix("")
    out.parent.mkdir(parents=True, exist_ok=True)
    tiles_dir.mkdir(parents=True, exist_ok=True)
    if scene.render.engine != "CYCLES":
        sys.exit("preflight: Cycles scenes only")
    grey, black = (0.6, 0.6, 0.6, 1.0), (0.0, 0.0, 0.0, 1.0)
    lights = [o for o in scene.objects if o.type == "LIGHT" and not o.hide_render]
    lights.sort(key=lambda o: -o.data.energy)
    light_report(scene, lights, subjects)

    variants = [("beauty", _plain()),
                ("clay", _override(scene, **{"Base Color": grey, "Roughness": 1.0})),
                ("mirror", _override(scene, **{"Base Color": (0.9, 0.9, 0.9, 1.0), "Metallic": 1.0, "Roughness": 0.08})),
                ("albedo0", _patched("Base Color", black))]
    if _uses_subsurface():
        variants.append(("scatter0", _patched("Subsurface Weight", 0.0)))
    if lights:
        variants.append(("lights_off", _lights(scene, lights)))
        variants += [(o.name, _lights(scene, lights, keep=o, world=False)) for o in lights[:max_lights]]

    r = scene.render
    saved = (r.filepath, r.resolution_percentage, r.use_compositing, scene.cycles.samples)
    r.resolution_percentage, r.use_compositing, scene.cycles.samples = round(scale * 100), False, samples
    tiles = []
    try:
        for label, change in variants:
            path = tiles_dir / f"{label.replace(' ', '_').replace('/', '_')}.png"
            with change:
                r.filepath = str(path)
                bpy.ops.render.render(write_still=True)
            img = bpy.data.images.load(str(path))
            w, h = img.size
            px = np.empty(w * h * 4, dtype=np.float32)
            img.pixels.foreach_get(px)
            tiles.append(px.reshape(h, w, 4))
            bpy.data.images.remove(img)
    finally:
        r.filepath, r.resolution_percentage, r.use_compositing, scene.cycles.samples = saved

    h, w = tiles[0].shape[:2]
    gap = 6
    rows = -(-len(tiles) // columns)
    big = np.ones((rows * h + (rows - 1) * gap, columns * w + (columns - 1) * gap, 4), dtype=np.float32)
    for i, t in enumerate(tiles):
        row, col = divmod(i, columns)
        y = (rows - 1 - row) * (h + gap)  # image rows are bottom-up; row 1 is the top row
        big[y:y + h, col * (w + gap):col * (w + gap) + w] = t
        print(f"[out] row {row + 1} col {col + 1}: {variants[i][0]}")
    im = bpy.data.images.new(out.stem, big.shape[1], big.shape[0], alpha=True)
    im.pixels.foreach_set(big.ravel())
    im.filepath_raw, im.file_format = str(out), "PNG"
    im.save()
    bpy.data.images.remove(im)
    print(f"[out] preflight sheet {out}  (single tiles in {tiles_dir})")
    return [label for label, _ in variants]


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if not argv or not bpy.data.filepath:
        sys.exit(__doc__)
    opt = {"--scale": 0.25, "--samples": 48}
    for k in opt:
        if k in argv:
            i = argv.index(k)
            opt[k] = float(argv[i + 1])
            del argv[i:i + 2]
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import enable_gpu
    enable_gpu(bpy.context.scene)
    sheet(bpy.context.scene, Path(argv[0]).resolve(), scale=opt["--scale"], samples=int(opt["--samples"]))
