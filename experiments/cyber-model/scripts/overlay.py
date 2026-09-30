"""Blend a hero render with the reference to fit the camera: python3 scripts/overlay.py renders/h02.png [out.png]
Reference is resized to the render. Red = reference edges, cyan = render edges (both edge-detected) on grey."""
import sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps

root = Path(__file__).resolve().parents[1]
r = Image.open(sys.argv[1]).convert("RGB")
ref = Image.open(root / "references/ref_radio.jpg").convert("RGB").resize(r.size, Image.LANCZOS)
def edges(im):
    g = ImageOps.autocontrast(im.convert("L").filter(ImageFilter.GaussianBlur(1.2)))
    return ImageOps.autocontrast(g.filter(ImageFilter.FIND_EDGES))
er, eg = edges(ref), edges(r)
out = Image.merge("RGB", (er, eg, eg))
out = Image.blend(out, Image.blend(ref, r, 0.5), 0.35)
out.save(sys.argv[2] if len(sys.argv) > 2 else str(Path(sys.argv[1]).with_name(Path(sys.argv[1]).stem + "_overlay.png")))
