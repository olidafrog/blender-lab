"""plotter-forms: build every form in the catalogue, export SVG strokes, raster contact sheets.

Run from the repo root:
  tools/blender.sh experiments/plotter-forms/scripts/build.py --out v01
  ... --only hopf,enneper     build only these forms or families (quick tests)
  ... --set enneper.n=2       override any value in P ("<form>.<key>", or a page value)
  ... --set hidden=0          draw every line (no hidden-line removal)
  ... --save                  also write output/svg/, output/svg-see-through/, the family sheets and the .blend
  ... --preflight             the plot-check sheet (stroke order, pen-up moves) to reviews/preflight_<out>.png

Writes renders/<out>/<form>.svg (the plots), renders/<out>_<family>.png and renders/<out>.png (the
catalogue sheet: the image a reviewer scores).
"""
import argparse
import ast
import math
import shutil
import sys
import time
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "library" / "node-groups"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalog  # noqa: E402
import plot_kit as pk  # noqa: E402
import plot_svg  # noqa: E402
from common import experiment_paths  # noqa: E402
from nodes import how_to_tweak  # noqa: E402

EXP = experiment_paths(__file__)

# Every value a designer might tune lives here. Override with --set key=value. Angles in degrees.
P = {
    # page (mm)
    "page_w": 150.0, "page_h": 150.0,
    "margin": 10.0,
    "pen": 0.35,                        # pen width, used for previews and to fill dots
    "dot": 1.3,                         # dot diameter; 0: no dots
    "hidden": 1,                        # 0: draw every line. 1: cut lines behind a surface. 2: keep them on their own layer
    "outline": 1,                       # draw the outline of every opaque surface (a plot can switch it off)
    "min_gap": 0.05,                    # lines that project exactly onto an earlier line are cut
    "fill": 0.9,                        # share of the page inside the margins that a form fills
    "sheet_px_per_mm": 5.0,             # raster density of the contact sheets
    # one entry per form value: "<form>.<key>", filled from catalog.FORMS below
}
for _f in catalog.FORMS:
    for _k, _v in _f["values"].items():
        P[f"{_f['name']}.{_k}"] = _v

HOW_TO_TWEAK = """\
plotter-forms — how to tweak

Each plot is a collection named "Plot <form>": one object with one Geometry Nodes modifier, and
the camera that frames its page. Select the object and change the sliders in the Modifiers tab.
Hover a slider for what it does. The lines are curves; the grey surface is only there to hide
the lines behind it.

Hidden lines, three switches:
- Scene > Custom Properties > plot_hidden: 1 cuts lines behind a surface, 0 draws every line,
  2 keeps the hidden parts on their own SVG layer ("0 - hidden") for a second pen.
- The same property on a "Plot" collection overrides the scene for that plot.
- The "Solid" checkbox on a form's modifier: off makes that form see-through.

Families
- Hopf *: circles from the Hopf fibration. Rings and Fibres count them; Latitude From/To choose the
  tori; Arc under 1 opens them; Spiral and Tumble give the wilder variants.
- Harmonic *, Sphere *: contour lines of a formula on a sphere. Lines and Phase set the levels.
- Dipole: field lines of a magnet round a sphere.
- Torus *, Blobs, Gyroid Ball, Schwarz Cube, Knot, Monkey: a solid drawn as parallel cuts.
  "Monkey Slices" takes any mesh object in its Object slot.
- Helicoid, Enneper, Scherk and the other surfaces: the two sets of parameter lines of a formula.
- Ridgeline *, Mesh Hills, Gravity Wells, Contour Terrain, Flamm, Wave Field: height fields.

To plot: Scripting tab, pick the text "Export SVG", press Run Script. It writes one SVG per
"Plot ..." collection next to this file, in millimetres, strokes only, lines on layer
"1 - lines", dots on "2 - dots". Page, margin, pen and dot size are the plot_* values under
Scene > Custom Properties. plot_outline on a collection draws the surface's outline.
A new plot: a collection named "Plot <name>" holding the curves and one camera.

New formulas: library/node-groups/plot_kit.py builds a form from three formula strings
(see experiments/plotter-forms/scripts/catalog.py).

Built by experiments/plotter-forms/scripts/build.py. Changes made here are lost on rebuild;
run /sync-tweaks or copy good values back into P.
"""

EXPORT_SVG = """\
# Run Script: writes one SVG per "Plot ..." collection next to this .blend.
import bpy
plot_svg = bpy.data.texts["plot_svg.py"].as_module()
plot_svg.export_scene()
"""


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="wip")
    ap.add_argument("--only", default="", help="comma list of form names or families")
    ap.add_argument("--samples", type=int, default=0, help="unused; kept so tools/sweep.sh can call this")
    ap.add_argument("--scale", type=float, default=1.0, help="contact sheet raster scale")
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--norender", action="store_true")
    ap.add_argument("--preflight", action="store_true")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    a = ap.parse_args(argv)
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in P:
            sys.exit(f"unknown P key: {k}")
        P[k] = ast.literal_eval(v)
    return a


def camera(name, collection, target, azimuth, elevation, persp=None):
    """Camera looking at target. azimuth 0: from the front (-Y); positive turns it towards +X."""
    cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    a, e = math.radians(azimuth), math.radians(elevation)
    away = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    if persp:
        cam.data.lens = persp["lens"]
        cam.location = Vector(target) + away * persp["distance"]
    else:
        cam.data.type = "ORTHO"
        cam.location = Vector(target) + away * 40.0
        cam.data.clip_end = 200.0
    cam.rotation_euler = (-away).to_track_quat("-Z", "Y").to_euler()
    collection.objects.link(cam)
    return cam


def points_of(objects, with_mesh):
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    out = []
    for ob in objects:
        strokes, dots, mesh = plot_svg.read_geometry(ob, dg)
        out += [p for p, _ in strokes]
        if len(dots):
            out.append(dots)
        if mesh is not None and with_mesh:
            out.append(mesh[0])
    return np.vstack(out) if out else np.zeros((1, 3))


def in_camera(cam, pts):
    bpy.context.view_layer.update()
    m = np.array(cam.matrix_world.inverted())
    return pts @ m[:3, :3].T + m[:3, 3]


def fit(cam, objects, with_mesh, frame=None):
    """Centre the orthographic camera on the lines and scale it so they fill the page."""
    loc = in_camera(cam, points_of(objects, with_mesh))[:, :2]
    lo, hi = loc.min(0), loc.max(0)
    if frame:
        cam.data.ortho_scale = 2 * frame
        return
    c = (lo + hi) / 2
    rot = cam.matrix_world.to_3x3()
    cam.location += rot @ Vector((c[0], c[1], 0.0))
    w, h = hi - lo
    aspect = (P["page_w"] - 2 * P["margin"]) / (P["page_h"] - 2 * P["margin"])
    cam.data.ortho_scale = max(w, h * aspect, 1e-3) / P["fill"] * (1.0 if aspect >= 1 else 1 / aspect)


def build_form(scene, f, origin):
    name = f["name"]
    col = bpy.data.collections.new(f"Plot {name}")
    scene.collection.children.link(col)
    for k, v in f["plot"].items():
        col[f"plot_{k}"] = v
    values = {k: (math.radians(P[f"{name}.{k}"]) if k in f["angles"] else P[f"{name}.{k}"]) for k in f["values"]}
    tree = f["make"](values)
    target = Vector(origin) + Vector((f["persp"] or {}).get("target", (0, 0, 0)))
    cam = camera(f"Cam {name}", col, target, *f["cam"], persp=f["persp"])
    copies, cols = f["sheet"] or ([{}], 1)
    objs = []
    for over in copies:
        ob = bpy.data.objects.new(tree.ng.name, bpy.data.meshes.new(tree.ng.name))
        ob.location = origin
        col.objects.link(ob)
        mod = ob.modifiers.new(tree.ng.name, "NODES")
        mod.node_group = tree.ng
        for k, v in over.items():
            pk.set_input(mod, tree, tree.key_names[k], math.radians(v) if k in f["angles"] else v)
        if "Object" in tree.ids:
            pk.set_input(mod, tree, "Object", bpy.data.objects["Suzanne"])
        objs.append(ob)
    outline = bool(f["plot"].get("outline", P["outline"]))
    if len(objs) > 1 and cols:      # lay the copies out in the camera plane (cols 0: all in one place)
        sizes = []
        for ob in objs:
            loc = in_camera(cam, points_of([ob], outline))[:, :2]
            sizes.append(loc.max(0) - loc.min(0))
        w, h = np.max(sizes, axis=0) * 1.1
        rot = cam.matrix_world.to_3x3()
        rows = -(-len(objs) // cols)
        for k, ob in enumerate(objs):
            ob.location = Vector(origin) + rot @ Vector(((k % cols - (cols - 1) / 2) * w, ((rows - 1) / 2 - k // cols) * h, 0.0))
    if not f["persp"]:
        fit(cam, objs, outline, f["frame"])
    return col


def build_scene(forms):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    inner_w, inner_h = P["page_w"] - 2 * P["margin"], P["page_h"] - 2 * P["margin"]
    scene.render.resolution_x, scene.render.resolution_y = round(inner_w * 10), round(inner_h * 10)
    scene["plot_page_w"], scene["plot_page_h"] = P["page_w"], P["page_h"]
    for k in ("margin", "pen", "dot", "min_gap"):
        scene[f"plot_{k}"] = float(P[k])
    scene["plot_hidden"] = int(P["hidden"])
    scene["plot_cusp_dots"] = scene["plot_end_dots"] = 0
    scene["plot_clip"] = 1
    scene["plot_outline"] = int(P["outline"])
    scene["plot_min_loop"] = 1.5
    scene["plot_min_visible"] = 1.2
    scene["plot_min_outline"] = 5.0
    scene["plot_min_length"] = 1.5      # no stubs: a stroke this short is a leftover of the hidden-line cut

    src = bpy.data.collections.new("Sources")       # meshes that forms read; not plotted
    scene.collection.children.link(src)
    bpy.ops.mesh.primitive_monkey_add()
    monkey = bpy.context.active_object
    monkey.name = "Suzanne"
    for c in monkey.users_collection:
        c.objects.unlink(monkey)
    src.objects.link(monkey)
    monkey.hide_viewport = monkey.hide_render = True

    for k, f in enumerate(catalog.FORMS):
        if f in forms:
            t0 = time.time()
            build_form(scene, f, (16.0 * (k % 8), -16.0 * (k // 8), 0.0))
            print(f"[out] built {f['name']} in {time.time() - t0:.1f} s")
    scene.camera = next(o for o in scene.objects if o.type == "CAMERA")
    how_to_tweak(HOW_TO_TWEAK)
    bpy.data.texts.new("Export SVG").write(EXPORT_SVG)
    bpy.data.texts.new("plot_svg.py").write(Path(plot_svg.__file__).read_text(encoding="utf-8"))
    return scene


def check(stats):
    """Countable checks after the silent steps. A failure here is a build bug, not a look problem."""
    for name, s in stats.items():
        assert s["strokes"] > 0, f"{name}: no strokes reached the SVG"
        assert s["off_page"] == 0, f"{name}: {s['off_page']} points off the page, bounds {s['bounds_mm']}"


def sheets(folder, forms, out, suffix="", scale=1.0, paper="#efefef"):
    """One contact sheet per family and one of everything. Returns the path of the full sheet."""
    R = EXP["renders"]
    made = []
    groups = [(fam, title, [f for f in forms if f["family"] == fam]) for fam, title in catalog.FAMILIES]
    groups = [g for g in groups if g[2]]
    for fam, title, fs in groups + ([("all", "", forms)] if len(groups) > 1 else []):
        name = out if fam == "all" else f"{out}_{fam}"
        cols = 7 if fam == "all" else min(4, len(fs))
        svg = R / f"{name}{suffix}_sheet.svg"
        w, _ = plot_svg.contact([folder / f"{f['name']}{suffix}.svg" for f in fs], svg, cols=cols,
                                labels=[f"{f['name']} — {f['title']}" for f in fs], title=title or None, paper=paper)
        png = (EXP["reviews"] / f"preflight_{name}.png") if suffix else R / f"{name}.png"
        plot_svg.raster(svg, png, width=round(w * P["sheet_px_per_mm"] * scale), paper=paper)
        made.append(png)
        print(f"[out] Saved {png}")
    return made


if __name__ == "__main__":
    args = parse_args()
    only = [s for s in args.only.split(",") if s]
    forms = [f for f in catalog.FORMS if not only or f["name"] in only or f["family"] in only]
    t0 = time.time()
    scene = build_scene(forms)
    folder = EXP["renders"] / args.out
    folder.mkdir(exist_ok=True)
    stats = plot_svg.export_scene(folder, scene=scene, debug=args.preflight)
    check(stats)
    print(f"[out] {len(forms)} forms in {time.time() - t0:.0f} s")
    if args.preflight:
        sheets(folder, forms, args.out, suffix="_check", paper="#ffffff")
    elif not args.norender:
        sheets(folder, forms, args.out, scale=args.scale)
    if args.save:
        out = EXP["output"]
        for sub, hidden in (("svg", int(P["hidden"]) or 1), ("svg-see-through", 0)):
            (out / sub).mkdir(exist_ok=True)
            scene["plot_hidden"] = hidden
            plot_svg.export_scene(out / sub, scene=scene)
        scene["plot_hidden"] = int(P["hidden"])
        blend = out / f"{EXP['name']}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        blend.with_suffix(".blend1").unlink(missing_ok=True)
    print("BUILD OK")
