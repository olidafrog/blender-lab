"""Re-grade a finished render without touching Cycles.

Feed it the linear EXR that `build.py --exr` writes, tweak the comp params, get a
PNG back in about a second.

  # one-off re-grade
  blender -b -P scripts/comp.py -- --exr renders/v23.exr --out renders/v23_bloom.png \
          --set bloom_strength=0.9 --set streak_angle=30

  # A/B sheet of one param
  blender -b -P scripts/comp.py -- --exr renders/v23.exr --sweep bloom_strength=0.2,0.5,0.9

  # open it in the GUI with a live backdrop preview
  blender -b -P scripts/comp.py -- --exr renders/v23.exr --save renders/comp_play.blend
  open -a Blender renders/comp_play.blend      # then move any slider
"""
import bpy, sys, os, argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comp_nodes import COMP_P, build_comp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = dict(COMP_P)
LOOK = dict(exposure=-0.6, look="AgX - Punchy")


def setup(exr_path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    img = bpy.data.images.load(os.path.abspath(exr_path))
    img.colorspace_settings.name = 'Linear Rec.709'
    w, h = img.size
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.view_settings.view_transform = 'AgX'
    try: sc.view_settings.look = LOOK["look"]
    except Exception: pass
    sc.view_settings.exposure = LOOK["exposure"]

    ng = bpy.data.node_groups.new("Comp", "CompositorNodeTree")
    sc.compositing_node_group = ng
    src = ng.nodes.new("CompositorNodeImage"); src.location = (0, 0); src.image = img
    build_comp(ng, P, src)
    sc.render.use_compositing = True
    return sc


def gui_setup():
    try: bpy.context.window.workspace = bpy.data.workspaces["Compositing"]
    except Exception: pass
    for scr in bpy.data.screens:
        for area in scr.areas:
            if area.type == 'NODE_EDITOR':
                for sp in area.spaces:
                    if sp.type == 'NODE_EDITOR':
                        sp.tree_type = 'CompositorNodeTree'
                        sp.show_backdrop = True
                        sp.backdrop_zoom = 0.6


def render(sc, out):
    sc.render.filepath = os.path.abspath(out)
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_depth = '16'
    bpy.ops.render.render(write_still=True)
    print("WROTE", sc.render.filepath)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--exr", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "renders", "comp.png"))
    ap.add_argument("--save", default="", help="write a .blend set up for GUI preview")
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--sweep", default="", help="key=v1,v2,v3 — writes <out>_<key><v>.png each")
    args = ap.parse_args(argv)
    for kv in args.set:
        k, v = kv.split("=", 1); P[k] = eval(v)

    if args.sweep:
        key, vals = args.sweep.split("=", 1)
        stem, ext = os.path.splitext(args.out)
        for v in vals.split(","):
            P[key] = eval(v)
            render(setup(args.exr), f"{stem}_{key}{v}{ext}")
    else:
        sc = setup(args.exr)
        if args.save:
            gui_setup()
            bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(args.save))
            print("SAVED", args.save)
        else:
            render(sc, args.out)
