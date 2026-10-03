"""Material levels: the same clean regions measured in each photo and in the render from its fitted camera.

  python3 experiments/apartment-model/scripts/mat_measure.py vNN [--md]

Regions are boxes in the photos' 2048 x 1536 pixels, chosen clear of furniture, art and windows in both the
photo and the render. Prints median sRGB per region, the render/photo luma ratio, and the brick-to-paint and
floor-to-paint luma ratios (lighting-independent targets: they hold even if the exposure differs).
Texture: the luma std of a high-passed patch (per-brick and per-plank variation), photo vs render.
"""
import statistics as st
import sys
from pathlib import Path

from PIL import Image, ImageFilter

EXP = Path(__file__).resolve().parents[1]
REGIONS = {
    "2": {"paint": [(61, 153, 306, 510), (1734, 306, 1989, 714)],
          "brick": [(938, 459, 1132, 612), (602, 459, 683, 775)],
          "floor": [(1326, 1326, 1683, 1510)]},
    "5": {"paint": [(714, 459, 1428, 816)],
          "brick": [(31, 122, 235, 459)],
          "floor": [(918, 1377, 1326, 1510)]},
}


def luma(p):
    return 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]


def region(im, boxes):
    w, h = im.size
    px, tex = [], []
    for b in boxes:
        box = (int(b[0] / 2048 * w), int(b[1] / 1536 * h), int(b[2] / 2048 * w), int(b[3] / 1536 * h))
        c = im.crop(box)
        px += list(c.getdata())
        c = c.resize((max(8, round((box[2] - box[0]) * 1024 / w)), max(8, round((box[3] - box[1]) * 768 / h))))
        g = c.convert("L")
        lo = g.filter(ImageFilter.GaussianBlur(6))
        tex += [a - b for a, b in zip(g.getdata(), lo.getdata())]
    med = [st.median(q[i] for q in px) for i in range(3)]
    return med, st.pstdev(tex)


def main():
    v = sys.argv[1]
    rows = []
    for n, regs in REGIONS.items():
        ph = Image.open(EXP / f"references/{n}.jpeg").convert("RGB")
        rn = Image.open(EXP / f"renders/{v}_{n}.png").convert("RGB")
        lv = {}
        for name, boxes in regs.items():
            (mp, tp), (mr, tr) = region(ph, boxes), region(rn, boxes)
            lv[name] = (luma(mp), luma(mr))
            rows.append((n, name, [round(x) for x in mp], [round(x) for x in mr], luma(mr) / luma(mp), tp, tr))
        for name in ("brick", "floor"):
            rows.append((n, f"{name}/paint", None, None,
                         (lv[name][1] / lv["paint"][1]) / (lv[name][0] / lv["paint"][0]),
                         lv[name][0] / lv["paint"][0], lv[name][1] / lv["paint"][1]))
    print("| photo | region | photo sRGB | render sRGB | render/photo | photo tex | render tex |")
    print("|---|---|---|---|---|---|---|")
    for n, name, mp, mr, ratio, tp, tr in rows:
        if mp is None:
            print(f"| {n} | {name} | | | {ratio:.2f} | {tp:.2f} | {tr:.2f} |")
        else:
            print(f"| {n} | {name} | {mp} | {mr} | {ratio:.2f} | {tp:.1f} | {tr:.1f} |")


main()
