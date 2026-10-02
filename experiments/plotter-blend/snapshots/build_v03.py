"""plotter-blend: build the playground from nothing, export SVG strokes, raster them for review.

Run from the repo root:
  tools/blender.sh experiments/plotter-blend/scripts/build.py --out v01
  ... --set key=value      override any value in P
  ... --save               also save output/plotter-blend.blend (the playground) and the final SVGs
  ... --preflight          no review raster: the plot-check sheet (stroke order, pen-up moves, starts)
                           to reviews/preflight_<out>.png. Read it before review round 1.

Writes renders/<out>_sphere.svg and <out>_vortex.svg (the plots), and renders/<out>.png (both side by
side on paper grey: the image a reviewer scores).
"""
import argparse
import ast
import math
import shutil
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import forms  # noqa: E402
import plot_svg  # noqa: E402
from common import experiment_paths  # noqa: E402
from nodes import how_to_tweak  # noqa: E402

EXP = experiment_paths(__file__)

# Every value a designer might tune lives here. Override with --set key=value. Angles in degrees.
P = {
    # page (mm)
    "page_w": 210.0, "page_h": 148.0,   # A5 landscape
    "margin": 15.0,
    "pen": 0.5,                         # pen width, used for previews and to fill dots
    "dot": 1.8,                         # dot diameter; 0: no dots
    "dedupe": 0.05,                     # do not ink a line twice where two project onto each other; 0: off
    "sphere_mm": 92.0,                  # sphere diameter on the page
    "vortex_mm": 130.0,                 # rim diameter on the page
    # sphere: contours of latitude + a peak + a trough
    "lines": 6,
    "phase": 0.0,
    "axis_tilt": 18.0,
    "axis_roll": 12.0,
    "eye_strength": 1.3,
    "eye_size": 0.5,
    "eye_spread": 45.0,
    "eye_direction": 26.0,
    "eye_balance": 1.0,
    "back_reach": 2.0,                 # 0: front only. 2: closed loops round the whole sphere
    "ragged_ends": 0.35,
    "dot_spacing": 0.8,
    "dot_dropout": 0.3,
    "seed": 1,
    "radius": 1.0,
    "detail": 6,
    "point_spacing": 0.01,
    # funnel: catenoid wireframe
    "meridians": 16,
    "parallels": 5,
    "throat_radius": 0.35,
    "rim_radius": 1.0,
    "height": 0.96,
    "flare": 1.36,                      # 1: true catenoid; the reference has a straighter throat
    "ring_bias": 1.0,
    "twist": 0.0,
    "funnel_dots": True,
    "resolution": 128,
    "cam_elevation": 12.0,              # funnel camera, degrees above side-on
}
ANGLES = ("axis_tilt", "axis_roll", "eye_spread", "eye_direction", "twist")

HOW_TO_TWEAK = """\
plotter-blend — how to tweak

Each form is one object with one Geometry Nodes modifier. Select it and change the sliders in
the Modifiers tab. Hover a slider for what it does. The lines are curves, not mesh.

- Sphere: contour lines of "latitude + a peak + a trough". Lines and Phase set the lines;
  Eye Strength, Size, Spread, Direction and Balance shape the two eyes; Axis Tilt and Roll turn
  the pole; Back Reach sets how far lines run onto the far side (2: closed loops all round);
  Dot Spacing, Dot Dropout and Seed place the dots.
- Funnel: Meridians x Parallels on a catenoid. Throat Radius, Rim Radius and Height set the
  shape; Flare straightens the throat; Ring Bias gathers the rings at the throat; Twist turns it into a vortex.
- Any other field or mesh: the "Isolines" group draws contours of any float field on any mesh.

To plot: open the Scripting tab, pick the text "Export SVG" and press Run Script. It writes one
SVG per "Plot ..." collection next to this file, in millimetres, strokes only, with the lines on
layer "1 - lines" and the dots on layer "2 - dots". Each plot's camera frames the page inside
the margins. Page, margin, pen and dot size are the plot_* values under Scene > Custom Properties.
A new plot: make a collection named "Plot <name>" holding the curves and one camera.

Built by experiments/plotter-blend/scripts/build.py. Changes made here are lost on rebuild;
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
    ap.add_argument("--out", default="wip", help="name: renders/<out>.png, <out>_sphere.svg, <out>_vortex.svg")
    ap.add_argument("--samples", type=int, default=0, help="unused; kept so tools/sweep.sh can call this")
    ap.add_argument("--scale", type=float, default=1.0, help="review raster scale; 1 = 3200 px wide")
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


def form(name, tree, collection, location=(0, 0, 0)):
    ob = bpy.data.objects.new(name, bpy.data.meshes.new(name))
    ob.location = location
    collection.objects.link(ob)
    ob.modifiers.new(tree.ng.name, "NODES").node_group = tree.ng
    return ob


def camera(name, collection, target, elevation, width):
    """Orthographic camera `elevation` degrees above side-on, whose frame is `width` world units wide."""
    cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = width
    e = math.radians(elevation)
    cam.location = (target[0], target[1] - 6 * math.cos(e), target[2] + 6 * math.sin(e))
    cam.rotation_euler = (math.radians(90) - e, 0, 0)
    collection.objects.link(cam)
    return cam


def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    inner_w, inner_h = P["page_w"] - 2 * P["margin"], P["page_h"] - 2 * P["margin"]
    scene.render.resolution_x, scene.render.resolution_y = round(inner_w * 10), round(inner_h * 10)
    scene["plot_page_w"], scene["plot_page_h"] = P["page_w"], P["page_h"]
    for k in ("margin", "pen", "dot", "dedupe"):
        scene[f"plot_{k}"] = float(P[k])

    p = {k: math.radians(v) if k in ANGLES else v for k, v in P.items()}

    col = bpy.data.collections.new("Plot sphere")
    scene.collection.children.link(col)
    form("Sphere", forms.contour_sphere(p), col)
    scene.camera = camera("Cam sphere", col, (0, 0, 0), 0.0, inner_w * 2 * P["radius"] / P["sphere_mm"])

    col = bpy.data.collections.new("Plot vortex")
    scene.collection.children.link(col)
    x = 4 * max(P["radius"], P["rim_radius"])
    form("Funnel", forms.funnel(p), col, location=(x, 0, 0))
    camera("Cam vortex", col, (x, 0, P["height"] / 2), P["cam_elevation"], inner_w * 2 * P["rim_radius"] / P["vortex_mm"])

    how_to_tweak(HOW_TO_TWEAK)
    bpy.data.texts.new("Export SVG").write(EXPORT_SVG)
    bpy.data.texts.new("plot_svg.py").write(Path(plot_svg.__file__).read_text(encoding="utf-8"))
    return scene


def check(stats):
    """Countable checks after the silent steps. A failure here is a build bug, not a look problem."""
    for name, s in stats.items():
        assert s["strokes"] > 0, f"{name}: no strokes reached the SVG"
        assert s["off_page"] == 0, f"{name}: {s['off_page']} points off the page, bounds {s['bounds_mm']}"
    if P["back_reach"] >= 2:
        s = stats["sphere"]
        assert s["closed_in"] == s["strokes_in"], f"sphere: {s['strokes_in'] - s['closed_in']} contours did not close"


if __name__ == "__main__":
    args = parse_args()
    scene = build_scene()
    R = EXP["renders"]
    stats = plot_svg.export_scene(R, prefix=f"{args.out}_", scene=scene, debug=args.preflight)
    check(stats)
    names = ("sphere", "vortex")
    if args.preflight:
        plot_svg.sheet([R / f"{args.out}_{n}_check.svg" for n in names], R / f"{args.out}_check.svg", paper="#ffffff")
        plot_svg.raster(R / f"{args.out}_check.svg", EXP["reviews"] / f"preflight_{args.out}.png", width=3200, paper="#ffffff")
        print(f"[out] preflight sheet {EXP['reviews'] / f'preflight_{args.out}.png'}")
    elif not args.norender:
        plot_svg.sheet([R / f"{args.out}_{n}.svg" for n in names], R / f"{args.out}_sheet.svg")
        plot_svg.raster(R / f"{args.out}_sheet.svg", R / f"{args.out}.png", width=round(3200 * args.scale))
        print(f"[out] Saved {R / f'{args.out}.png'}")
    if args.save:
        for n in names:
            shutil.copy(R / f"{args.out}_{n}.svg", EXP["output"] / f"{n}.svg")
        blend = EXP["output"] / f"{EXP['name']}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        blend.with_suffix(".blend1").unlink(missing_ok=True)
    print("BUILD OK")
