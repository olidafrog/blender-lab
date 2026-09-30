"""Draw the label decals (assets/dec_*.png, white ink on transparent) with PIL. Run once with system python3.

  python3 experiments/cyber-model/scripts/make_decals.py

dec_logo:   logo mark + 'DT-03 / Multifunction Radio Device' block on the shield plate.
dec_lid:    'DT-03' engraved-style text on the battery lid.
dec_labels: POWER, ON/OFF, INSERT and small arrow marks (one sheet, cropped by UV in build.py).
Sizes are pixels at ~40 px/mm so tiny text stays crisp after minification.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "assets"
CJK = ["/System/Library/Fonts/STHeiti Medium.ttc", "/System/Library/Fonts/Hiragino Sans GB.ttc",
       "/System/Library/Fonts/PingFang.ttc"]
LAT = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc",
       "/System/Library/Fonts/Supplemental/Menlo.ttc"]


def font(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


INK = (232, 232, 236, 255)

# logo block: 30 x 12 mm
im = Image.new("RGBA", (1200, 480), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.text((10, 30), "燕鼎", font=font(CJK, 240), fill=INK)
d.line([(520, 40), (520, 250)], fill=INK, width=6)
d.text((545, 40), "DT-03", font=font(LAT, 96), fill=INK)
d.text((545, 160), "Multifunction", font=font(LAT, 40), fill=INK)
d.text((545, 210), "Radio Device", font=font(LAT, 40), fill=INK)
for i, w in enumerate((520, 460, 300)):
    d.rectangle([10, 300 + i * 34, 10 + w, 312 + i * 34], fill=INK)
d.rectangle([10, 430, 1100, 442], fill=INK)
im.save(OUT / "dec_logo.png")

# lid text: 16 x 5 mm, engraved look (mid grey so it reads as a recess)
im = Image.new("RGBA", (640, 200), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.text((20, 20), "DT -03", font=font(LAT, 150), fill=(140, 140, 146, 255))
im.save(OUT / "dec_lid.png")

# labels sheet 1024 x 512: cells of 256 x 128
im = Image.new("RGBA", (1024, 512), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
for cell, txt in enumerate(("POWER", "ON/OFF", "INSERT", "OPEN")):
    d.text((cell * 256 + 12, 30), txt, font=font(LAT, 46), fill=INK)
for k in range(4):        # arrow triangles, row 2
    x, y = k * 256 + 128, 256 + 64
    d.polygon([(x - 30, y + 26), (x + 30, y + 26), (x, y - 30)], outline=INK, width=8)
im.save(OUT / "dec_labels.png")
print("decals saved")
