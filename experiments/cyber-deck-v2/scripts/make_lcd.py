"""Draw the LCD texture (assets/lcd.png) with PIL. Run once with system python3; the PNG is committed.

  python3 experiments/cyber-deck-v2/scripts/make_lcd.py

Positive-mode display: cyan backlight, dark ink. Colours are the reference's measured LCD face
(sRGB 131,186,192). Drawn at 2x and downsampled so the tiny text stays crisp, then a faint pixel grid
and vignette are multiplied in.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1536, 832                     # 60 x 32.5 mm at ~25 px/mm
K = 2
BG = (124, 182, 190)
INK = (22, 52, 60)
LIGHT = (198, 232, 236)

FONT_PATHS = ["/System/Library/Fonts/Supplemental/Menlo.ttc", "/System/Library/Fonts/Menlo.ttc",
              "/System/Library/Fonts/Supplemental/Courier New Bold.ttf", "/Library/Fonts/Arial Bold.ttf"]


def font(size):
    for p in FONT_PATHS:
        try:
            return ImageFont.truetype(p, size * K)
        except OSError:
            continue
    return ImageFont.load_default(size * K)


img = Image.new("RGB", (W * K, H * K), BG)
d = ImageDraw.Draw(img)
r = lambda *b: tuple(int(v * K) for v in b)

# header: dark tab + light tab
d.rectangle(r(0, 0, 690, 96), fill=INK)
d.text(r(28, 26), "CURRENT SOURCE", font=font(46), fill=LIGHT)
d.rectangle(r(690, 0, W, 96), fill=BG)
d.rectangle(r(690, 0, 1040, 96), fill=LIGHT)
d.text(r(722, 26), "SPOTIFY", font=font(46), fill=INK)
d.line(r(0, 100, W, 100), fill=INK, width=4 * K)

# message lines
d.text(r(28, 132), "CH 04  LINK 92%  :", font=font(50), fill=INK)
d.text(r(28, 232), "OPEN THE HATCH DOOR NOW!", font=font(60), fill=INK)

# lower left: progress bar and icon
d.rectangle(r(0, 350, 1080, 420), fill=BG, outline=INK, width=4 * K)
d.rectangle(r(0, 350, 420, 420), fill=INK)
d.rectangle(r(0, 560, 190, H), outline=INK, width=4 * K)
cx, cy = 95, 700
d.arc(r(cx - 44, cy - 44, cx + 44, cy + 44), 180, 360, fill=INK, width=8 * K)
d.rectangle(r(cx - 52, cy - 6, cx - 30, cy + 34), fill=INK)
d.rectangle(r(cx + 30, cy - 6, cx + 52, cy + 34), fill=INK)
d.text(r(215, 588), "BLEEDING OUT", font=font(34), fill=INK)
d.text(r(215, 650), "CHILLIN' SOON", font=font(34), fill=INK)
d.line(r(0, 560, 1080, 560), fill=INK, width=4 * K)

# duration box
d.rectangle(r(1080, 350, W, H), outline=INK, width=4 * K)
d.text(r(1100, 372), "DURATION", font=font(42), fill=INK)
d.text(r(1104, 486), "4:27", font=font(158), fill=INK)

img = img.resize((W, H), Image.LANCZOS)
# faint diagonal glass sheen (reflection of the key), 8 % white
sheen = Image.new("RGBA", (W, H), (255, 255, 255, 0))
sd = ImageDraw.Draw(sheen)
sd.polygon([(int(W * 0.05), 0), (int(W * 0.42), 0), (int(W * 0.18), H), (0, H), (0, int(H * 0.55))], fill=(255, 255, 255, 34))
sd.polygon([(int(W * 0.50), 0), (int(W * 0.58), 0), (int(W * 0.34), H), (int(W * 0.26), H)], fill=(255, 255, 255, 20))
img = Image.alpha_composite(img.convert("RGBA"), sheen).convert("RGB")

# faint pixel grid and vignette
px = img.load()
for y in range(H):
    for x in range(W):
        g = 0.975 if (x % 12 == 0 or y % 12 == 0) else 1.0
        vx, vy = (x / W - 0.5) * 2, (y / H - 0.5) * 2
        v = 1.0 - 0.10 * (vx * vx + vy * vy)
        f = g * v
        r0, g0, b0 = px[x, y]
        px[x, y] = (int(r0 * f), int(g0 * f), int(b0 * f))

out = Path(__file__).resolve().parents[1] / "assets" / "lcd.png"
img.save(out)
print("saved", out)
