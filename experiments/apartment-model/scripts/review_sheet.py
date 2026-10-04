"""Review sheet for one version: per view a row of photo | render | overlay (model edges on the photo).

  tools/blender.sh experiments/apartment-model/scripts/review_sheet.py v01 [views=1,2,3,...]
  tools/blender.sh experiments/apartment-model/scripts/review_sheet.py v13 mat
      materials round: photo | render | 1:1 details (top: photo crops, bottom: render crops at the same
      pixels; left and right as in DETAIL). Needs the renders at full size (--scale 1).
  tools/blender.sh experiments/apartment-model/scripts/review_sheet.py v19 sofa
      sofa round: as mat, with the sofa details in SOFA (photos 1, 2, 3), plus a column of the same
      photo crops with the model edges (from the _ids pass) in red.
Writes renders/<v>.png (the image review_round.py expects). Rows are 1024 x 768 per panel.
"""
import sys
from pathlib import Path

import bpy
import json
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "library/models/interior-kit"))  # shell_kit, cam_util, fit_cam
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


# materials sheet: per view two 1:1 detail crops (centre x, y in the 2048 x 1536 photo), 512 x 384 each
DETAIL = {"2": [(1030, 560), (1480, 1330)], "5": [(230, 420), (1000, 1330)], "1": [(1880, 420), (1880, 980)],
          "8": [(1075, 1120), (1075, 1400)]}

# sofa round: left seats | ottoman (1), near arm + seat | back cushions + ottoman (2), seat + arm | seat front (3)
SOFA = {"1": [(1100, 1070), (1480, 1170)], "2": [(280, 1300), (700, 1080)], "3": [(1790, 1300), (1790, 1480)]}
SOFA_OVERLAY = ("1", "2")    # camera 3 misses the measured radiator by ~100 px in that corner: no edge overlay there


def crop(a, cx, cy, w=512, h=384):
    H, W = a.shape[:2]
    x0 = int(min(max(cx - w // 2, 0), W - w)); y0 = int(min(max(cy - h // 2, 0), H - h))
    return a[y0:y0 + h, x0:x0 + w]


def mat_sheet(v, detail=DETAIL):
    rows = []
    for n, pts in detail.items():
        d = json.load(open(EXP / f"assets/cams/{n}.json"))
        f = d.get("joint") or d.get("refined") or d.get("fit")
        photo = undistort(load(EXP / f"references/{n}.jpeg", 2048, 1536), f.get("k1", 0.0), f["lens"],
                          f.get("sensor_w", 34.62), 2048, 1536)
        ren = load(EXP / f"renders/{v}_{n}.png", 2048, 1536)
        det = np.concatenate([np.concatenate([crop(photo, *pts[0]), crop(photo, *pts[1])], 1),
                              np.concatenate([crop(ren, *pts[0]), crop(ren, *pts[1])], 1)], 0)
        small = lambda a: a.reshape(PH, 2, PW, 2, 3).mean((1, 3))
        row = [small(photo), np.ones((PH, 6, 3)), small(ren), np.ones((PH, 6, 3)), det]
        ids = EXP / f"renders/{v}_{n}_ids.png"
        if detail is SOFA and n in SOFA_OVERLAY and ids.exists():                    # model edges over the photo crops, at 1:1
            e = edges_ids(load(ids, 2048, 1536))
            ov = np.repeat(photo.mean(-1, keepdims=True) * 0.75, 3, -1)
            ov[e] = (1.0, 0.1, 0.1)
            row += [np.ones((PH, 6, 3)), np.concatenate([crop(ov, *pts[0]), crop(ov, *pts[1])], 0)]
        elif detail is SOFA:
            row += [np.ones((PH, 6, 3)), np.ones((PH, 512, 3)) * 0.5]
        row = np.concatenate(row, 1)
        rows += [row, np.ones((6, row.shape[1], 3))]
    return np.concatenate(rows[:-1], 0), list(detail)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    v = argv[0]
    if len(argv) > 1 and argv[1] in ("mat", "sofa"):
        sheet, views = mat_sheet(v, DETAIL if argv[1] == "mat" else SOFA)
        H, W = sheet.shape[:2]
        o = bpy.data.images.new("sheet", W, H)
        o.pixels[:] = np.concatenate([sheet, np.ones((H, W, 1))], -1)[::-1].ravel()
        o.filepath_raw = str(EXP / f"renders/{v}.png")
        o.file_format = "PNG"
        o.save()
        print(f"[out] materials sheet {W}x{H} views {views} -> renders/{v}.png")
        return
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
