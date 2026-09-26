"""Edge-density metrics used by the reviewer: mean |grad| on lit pixels, strong-edge fraction, clipped share."""
import sys; from PIL import Image, ImageChops
def metrics(path, size=1440):
    im = Image.open(path).convert("RGB").resize((size, size), Image.LANCZOS)
    L = im.convert("L")
    gx = ImageChops.difference(L, L.transform(L.size, Image.AFFINE, (1,0,1,0,1,0)))
    gy = ImageChops.difference(L, L.transform(L.size, Image.AFFINE, (1,0,0,0,1,1)))
    g = ImageChops.add(gx, gy)
    mx = Image.merge("RGB", im.split()).convert("L")
    lit = [max(p) > 25 for p in im.getdata()]
    gd = list(g.getdata()); h = L.histogram(); n = size*size
    litg = [v for v, l in zip(gd, lit) if l]
    mean_g = sum(litg)/max(1,len(litg)); strong = sum(1 for v in litg if v > 40)/max(1,len(litg)); g20 = sum(1 for v in litg if v > 20)/max(1,len(litg))
    return dict(mean_grad=round(mean_g,2), g40=round(strong,4), g20=round(g20,4), clip=round(100*sum(h[251:])/n,3), lit=round(len(litg)/n,3))
for p in sys.argv[1:]: print(p.split('/')[-1], metrics(p))
