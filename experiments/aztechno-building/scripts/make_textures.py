"""Painted textures for the ground floor, drawn from reference crops (plain python3 + Pillow).

  python3 scripts/make_textures.py      -> assets/generated/*.png

shutter.png  1.55 x 2.3 m roll-up shutter: cream slats, orange hexagon, maroon stripes, ribbed valance
door.png     black steel door with an arched panel
shop.png     an open kiosk: shelves of bright packs in the dark
banner.png   the "SNACK PIQUIN" vinyl banner
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(__file__).parents[1] / "assets/generated"
OUT.mkdir(parents=True, exist_ok=True)
PX = 400                       # px per metre

CREAM, ORANGE, MAROON, DEEP = (232, 214, 170), (238, 120, 40), (150, 40, 55), (105, 25, 40)


def hexagon(cx, cy, w, h, cut):
    return [(cx - w / 2 + cut, cy - h / 2), (cx + w / 2 - cut, cy - h / 2), (cx + w / 2, cy),
            (cx + w / 2 - cut, cy + h / 2), (cx - w / 2 + cut, cy + h / 2), (cx - w / 2, cy)]


def shutter():
    W, H = int(1.55 * PX), int(2.3 * PX)
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    val = int(0.2 * PX)
    for x in range(0, W, 10):                                   # ribbed valance box
        d.line([(x, 0), (x, val)], fill=(200, 185, 150), width=3)
    d.rectangle([0, val - 6, W, val], fill=(170, 150, 120))
    band = int(H * 0.60)
    for y in range(band, H, 30):                                # maroon stripes, two tones
        d.rectangle([0, y, W, y + 15], fill=MAROON)
        d.rectangle([0, y + 15, W, y + 30], fill=DEEP)
    cy = int(H * 0.58)
    d.polygon(hexagon(W / 2, cy, W * 0.80, H * 0.24, W * 0.14), fill=ORANGE)
    d.polygon(hexagon(W / 2, cy, W * 0.50, H * 0.09, W * 0.08), fill=MAROON)
    for y in range(val, H, 30):                                 # slat joints (the bump adds the relief)
        d.line([(0, y), (W, y)], fill=(0, 0, 0), width=2) if False else None
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    im.save(OUT / "shutter.png")


def door():
    W, H = int(1.05 * PX), int(2.3 * PX)
    im = Image.new("RGB", (W, H), (22, 20, 20))
    d = ImageDraw.Draw(im)
    m = int(0.12 * PX)
    d.rectangle([m, m, W - m, H - m], outline=(45, 40, 38), width=8)
    x0, x1, y0, y1 = int(W * 0.25), int(W * 0.75), int(H * 0.12), int(H * 0.78)
    d.rectangle([x0, y0 + (x1 - x0) // 2, x1, y1], fill=(170, 120, 55))
    d.pieslice([x0, y0, x1, y0 + (x1 - x0)], 180, 360, fill=(170, 120, 55))
    for x in range(x0, x1, 28):
        d.line([(x, y0), (x, y1)], fill=(60, 40, 25), width=5)
    for y in range(y0 + 60, y1, 70):
        d.line([(x0, y), (x1, y)], fill=(60, 40, 25), width=5)
    im.filter(ImageFilter.GaussianBlur(1.0)).save(OUT / "door.png")


def shop():
    import random
    rng = random.Random(3)
    W, H = int(2.0 * PX), int(2.3 * PX)
    im = Image.new("RGB", (W, H), (12, 11, 10))
    d = ImageDraw.Draw(im)
    for y in range(int(H * 0.12), int(H * 0.8), int(0.32 * PX)):
        d.rectangle([0, y + 90, W, y + 98], fill=(90, 90, 92))
        x = 10
        while x < W - 30:
            w = rng.randint(22, 60)
            col = rng.choice([(235, 200, 40), (250, 250, 240), (40, 140, 60), (220, 60, 40), (240, 240, 60), (30, 60, 150)])
            d.rectangle([x, y + 90 - rng.randint(40, 85), x + w, y + 90], fill=col)
            x += w + rng.randint(3, 12)
    d.rectangle([int(W * 0.55), int(H * 0.55), W, H], fill=(25, 22, 20))        # counter
    d.rectangle([int(W * 0.60), int(H * 0.60), int(W * 0.72), int(H * 0.72)], fill=(240, 240, 235))
    im.filter(ImageFilter.GaussianBlur(1.5)).save(OUT / "shop.png")


def banner():
    W, H = int(2.9 * PX), int(0.55 * PX)
    im = Image.new("RGB", (W, H), (245, 240, 230))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, int(H * 0.18)], fill=(230, 120, 40))
    try:
        f1 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 120)
        f2 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 55)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    d.text((W / 2, H * 0.47), "SNACK PIQUIN", fill=(200, 40, 40), font=f1, anchor="mm")
    d.text((W / 2, H * 0.84), "POLLOS PIQUIN", fill=(40, 40, 40), font=f2, anchor="mm")
    im.save(OUT / "banner.png")


def entrance():
    """The corner entrance (reference u 118-215, v 772-882): orange sculpted jamb, dark tile strip, cream
    door panel with an orange S-ribbon and round holes, stepped blocks, red pier with orange squares."""
    W, H = int(2.55 * PX), int(2.9 * PX)
    im = Image.new("RGB", (W, H), (236, 226, 200))
    d = ImageDraw.Draw(im)
    s = W / 97.0                                    # reference px -> texture px
    O, O2, RED, TILE = (240, 125, 30), (250, 160, 40), (200, 40, 45), (40, 38, 36)
    d.rectangle([0, 0, 36 * s, H], fill=O)          # jamb
    d.rectangle([4 * s, 4 * s, 30 * s, 30 * s], fill=O2)
    d.rectangle([10 * s, 36 * s, 34 * s, 44 * s], fill=(200, 95, 20))
    d.rectangle([14 * s, 50 * s, 30 * s, 80 * s], fill=(150, 140, 110))
    d.rectangle([4 * s, 82 * s, 34 * s, H], fill=(230, 110, 25))
    for y in range(0, H, 10):                       # dark tile strip
        d.rectangle([37 * s, y, 44 * s, y + 8], fill=TILE)
    d.rectangle([45 * s, 0, 78 * s, H], fill=(245, 242, 232))
    ribbon = [(62, 6), (70, 12), (70, 38), (58, 50), (58, 62), (72, 72), (74, 82), (68, 86), (58, 80), (52, 66),
              (52, 48), (64, 36), (64, 16), (56, 10)]
    d.polygon([(x * s, y * s) for x, y in ribbon], fill=O)
    for cx, cy, r in ((63, 11, 3), (67, 20, 2.2), (60, 72, 2.2), (68, 80, 3)):
        d.ellipse([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s], fill=(245, 242, 232))
    for x0, y0, x1 in ((46, 90, 56), (50, 96, 62), (46, 102, 70)):
        d.rectangle([x0 * s, y0 * s, x1 * s, (y0 + 6) * s], fill=O)
    d.rectangle([79 * s, 0, 82 * s, H], fill=RED)
    d.rectangle([82 * s, 0, 97 * s, H], fill=(245, 242, 232))
    for y in (6, 30, 54, 78):
        d.rectangle([84 * s, y * s, 95 * s, (y + 16) * s], fill=O)
    d.rectangle([95 * s, 0, 97 * s, H], fill=RED)
    im.filter(ImageFilter.GaussianBlur(1.2)).save(OUT / "entrance.png")


if __name__ == "__main__":
    entrance()
    shutter()
    door()
    shop()
    banner()
    print("[out] textures in", OUT)
