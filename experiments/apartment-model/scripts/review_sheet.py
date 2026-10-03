"""Review sheet for one version: per view a row of photo | render | overlay (model edges on the photo).

  tools/blender.sh experiments/apartment-model/scripts/review_sheet.py -- v01 [views=1,2,3,...]
Writes renders/<v>.png (the image review_round.py expects). Rows are 1024 x 768 per panel.
"""
import sys
from pathlib import Path

import bpy
import json
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cam_util import undistort  # noqa: E402

EXP = Path(__file__).resolve().parents[1]
PW, PH = 1024, 768


def load(path, w=PW, h=PH):
    img = bpy.data.images.load(str(path))
    if tuple(img.size) != (w, h):
        img.scale(w, h)
    a = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1][..., :3]
    bpy.data.images.remove(img)
    return a


def edges_ids(a):
    d = np.zeros(a.shape[:2], bool)
    d[:, 1:] |= np.abs(a[:, 1:] - a[:, :-1]).sum(-1) > 0.02
    d[1:] |= np.abs(a[1:] - a[:-1]).sum(-1) > 0.02
    return d


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    v = argv[0]
    views = argv[1].split(",") if len(argv) > 1 else sorted(
        {p.stem.split("_")[1] for p in (EXP / "renders").glob(f"{v}_*_ids.png")}, key=int)
    rows = []
    for n in views:
        photo = load(EXP / f"references/{n}.jpeg", PW * 2, PH * 2)
        d = json.load(open(EXP / f"assets/cams/{n}.json"))
        f = d.get("joint") or d.get("refined") or d.get("fit")
        photo = undistort(photo, f.get("k1", 0.0), f["lens"], f.get("sensor_w", 34.62), PW, PH)   # to the render's pinhole
        ren = load(EXP / f"renders/{v}_{n}.png")
        e = edges_ids(load(EXP / f"renders/{v}_{n}_ids.png"))
        shade = EXP / f"renders/{v}_{n}_shade.png"
        if shade.exists():                                     # folds within one object
            sl = load(shade).mean(-1)
            f2 = np.zeros_like(e)
            f2[:, 1:] |= np.abs(sl[:, 1:] - sl[:, :-1]) > 0.06
            f2[1:] |= np.abs(sl[1:] - sl[:-1]) > 0.06
            e |= f2
        g = photo.mean(-1, keepdims=True) * 0.75
        ov = np.repeat(g, 3, -1)
        ov[e] = (1.0, 0.1, 0.1)
        row = np.concatenate([photo, np.ones((PH, 6, 3)), ren, np.ones((PH, 6, 3)), ov], 1)
        rows.append(row)
        rows.append(np.ones((6, row.shape[1], 3)))
    sheet = np.concatenate(rows[:-1], 0)
    H, W = sheet.shape[:2]
    o = bpy.data.images.new("sheet", W, H)
    o.pixels[:] = np.concatenate([sheet, np.ones((H, W, 1))], -1)[::-1].ravel()
    o.filepath_raw = str(EXP / f"renders/{v}.png")
    o.file_format = "PNG"
    o.save()
    print(f"[out] sheet {W}x{H} views {views} -> renders/{v}.png")


main()
