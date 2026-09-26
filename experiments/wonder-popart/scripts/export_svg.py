"""Export the saved .blend as a layered, editable SVG.

Renders ID passes (every colour region painted a unique flat colour), splits
them into masks, traces each with potrace and stacks the traced shapes in
paint order, filled with the real colours from the file. The Line Art ink is
written as real SVG strokes, straight from the evaluated Grease Pencil points.

Shadows come from a Cycles pass instead of EEVEE: raytraced, so the edges are
exact instead of shadow-map stair steps. The cast shadow is rendered with the
logo hidden from the camera, so it comes out as one whole shape, written as a
fill, the dots clipped to it, and an outline stroke.

Run on a copy (an open Blender session saving the file would undo edits):
  blender -b copy.blend -P scripts/export_svg.py -- --out export/name.svg [--stroke 0.016]
"""
import bpy, os, sys, subprocess, argparse, tempfile
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--scale", type=int, default=200)      # trace resolution, % of the scene resolution
ap.add_argument("--stroke", type=float, default=0)     # >0: one even Line Art stroke of this radius
args = ap.parse_args(argv)
OUT = os.path.abspath(args.out)
TMP = tempfile.mkdtemp(prefix="popsvg_")
POTRACE = "/opt/homebrew/bin/potrace"

from bpy_extras.object_utils import world_to_camera_view
sc = bpy.context.scene
logo_g = next(n for n in bpy.data.materials["PopLogo"].node_tree.nodes if n.type == 'GROUP')
wall_g = next(n for n in bpy.data.materials["PopWall"].node_tree.nodes if n.type == 'GROUP')
ink_mat = bpy.data.materials["Ink Stroke"]


def to_hex(c):
    s = [(12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055) for v in c[:3]]
    return "#%02X%02X%02X" % tuple(round(max(0, min(1, v)) * 255) for v in s)


# real colours, read before the ID overrides
REAL = {
    "wall": to_hex(wall_g.inputs["Wall Color"].default_value),
    "shadow": to_hex(wall_g.inputs["Shadow Color"].default_value),
    "shadow_dot": to_hex(wall_g.inputs["Shadow Dot Color"].default_value),
    "full": to_hex(logo_g.inputs["Full Color"].default_value),
    "highlight": to_hex(logo_g.inputs["Highlight Color"].default_value),
    "mid_base": to_hex(logo_g.inputs["Mid Base Color"].default_value),
    "mid_lines": to_hex(logo_g.inputs["Mid Line Color"].default_value),
    "face": to_hex(logo_g.inputs["Face Color"].default_value),
    "strokes": to_hex(ink_mat.grease_pencil.color),
}

def ink_paths(tol=0.35):
    """Evaluated Line Art strokes -> [(points_px, width_px)] in scene pixels."""
    ob = bpy.data.objects.get("Ink Lines")
    if not ob:
        return []
    dg = bpy.context.evaluated_depsgraph_get()
    gp = ob.evaluated_get(dg).data
    cam = sc.camera
    Ws, Hs = sc.render.resolution_x, sc.render.resolution_y
    px_per_unit = max(Ws, Hs) / cam.data.ortho_scale
    mw = ob.matrix_world
    out = []
    for layer in gp.layers:
        if layer.hide or not layer.current_frame():
            continue
        for st in layer.current_frame().drawing.strokes:
            pts = []
            for p in st.points:
                v = world_to_camera_view(sc, cam, mw @ p.position)
                pts.append((v.x * Ws, (1 - v.y) * Hs))
            if len(pts) < 2:
                continue
            closed = st.cyclic or (abs(pts[0][0] - pts[-1][0]) + abs(pts[0][1] - pts[-1][1]) < 0.5)
            if closed:   # RDP needs distinct endpoints: split the loop in two
                h = len(pts) // 2
                pts = rdp(pts[:h + 1], tol)[:-1] + rdp(pts[h:] + [pts[0]], tol)[:-1]
            else:
                pts = rdp(pts, tol)
            out.append((pts, closed, 2 * st.points[0].radius * px_per_unit))
    return out


def rdp(pts, tol):
    """Ramer-Douglas-Peucker: drop points within tol px of the line."""
    if len(pts) < 3:
        return pts
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    dx, dy = x1 - x0, y1 - y0
    n = (dx * dx + dy * dy) ** 0.5 or 1e-9
    far, idx = 0.0, 0
    for i in range(1, len(pts) - 1):
        d = abs(dy * (pts[i][0] - x0) - dx * (pts[i][1] - y0)) / n
        if d > far:
            far, idx = d, i
    if far <= tol:
        return [pts[0], pts[-1]]
    return rdp(pts[:idx + 1], tol)[:-1] + rdp(pts[idx:], tol)


if args.stroke > 0:   # merge every Line Art modifier into one: contour + crease, one radius
    _ob = bpy.data.objects.get("Ink Lines")
    arts = [m for m in _ob.modifiers if m.type == 'LINEART'] if _ob else []
    if arts:
        keep = arts[0]
        keep.use_contour = any(m.use_contour for m in arts)
        keep.use_crease = any(m.use_crease for m in arts)
        keep.radius = args.stroke
        for m in arts[1:]:
            _ob.modifiers.remove(m)

INK = ink_paths()
_lines = bpy.data.objects.get("Ink Lines")
if _lines:
    _lines.hide_render = True        # fills render complete under where the ink sits

ID = {  # flat ID colours, far apart so antialiased edges classify cleanly
    "wall": (0, 0, 0), "shadow": (1, 0, 1), "full": (0, 0, 1), "highlight": (0, 1, 0),
    "mid_base": (0, 1, 1), "mid_lines": (1, 1, 0), "face": (1, 0, 0), "strokes": (1, 1, 1),
}
for sock, key in (("Face Color", "face"), ("Full Color", "full"), ("Mid Line Color", "mid_lines"),
                  ("Mid Base Color", "mid_base"), ("Highlight Color", "highlight")):
    logo_g.inputs[sock].default_value = (*ID[key], 1)
wall_g.inputs["Wall Color"].default_value = (*ID["wall"], 1)
wall_g.inputs["Shadow Color"].default_value = (*ID["shadow"], 1)
dot_size = wall_g.inputs["Dot Size"].default_value
wall_g.inputs["Dot Size"].default_value = 0.0             # dots off: shadow is one flat region
self_shadow = logo_g.inputs["Self Shadow"].default_value
logo_thresh = logo_g.inputs["Shadow Threshold"].default_value
wall_thresh = wall_g.inputs["Shadow Threshold"].default_value
logo_g.inputs["Self Shadow"].default_value = 0.0          # re-applied from the raytraced pass below
ink_mat.grease_pencil.color = (*ID["strokes"], 1)
for n in sc.world.node_tree.nodes:
    if n.type == 'BACKGROUND' and n.inputs["Strength"].default_value > 0:
        n.inputs["Color"].default_value = (*ID["wall"], 1)

sc.render.resolution_percentage = args.scale
sc.render.filter_size = 0.7
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_depth = '8'
sc.view_settings.view_transform = 'Standard'
W = sc.render.resolution_x * args.scale // 100
H = sc.render.resolution_y * args.scale // 100


def render(name, linear=False):
    """linear=True writes float EXR, so light values compare to the shader thresholds."""
    sc.render.image_settings.file_format = 'OPEN_EXR' if linear else 'PNG'
    sc.render.image_settings.color_depth = '32' if linear else '8'
    sc.render.filepath = os.path.join(TMP, name + (".exr" if linear else ".png"))
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(sc.render.filepath)
    a = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)[::-1, :, :3]   # top row first
    bpy.data.images.remove(img)
    return a


def classify(a, keys):
    ids = np.array([ID[k] for k in keys], dtype=np.float32)
    d = ((a[:, :, None, :] - ids[None, None]) ** 2).sum(-1)
    return {k: (d.argmin(-1) == i) for i, k in enumerate(keys)}


full_pass = render("id_full")
masks = classify(full_pass, list(ID))

# dots on their own: whole wall treated as shadow, logo gone, so every dot is
# complete; they get clipped to the raytraced shadow shape below
dots = None
if dot_size > 0:
    wall_g.inputs["Dot Size"].default_value = dot_size
    wall_g.inputs["Shadow Color"].default_value = (*ID["wall"], 1)
    wall_g.inputs["Shadow Dot Color"].default_value = (*ID["shadow"], 1)
    wall_g.inputs["Shadow Threshold"].default_value = 1e6
    _logo = bpy.data.objects["Logo"]; _logo.hide_render = True
    dots = classify(render("id_dots"), ["wall", "shadow"])["shadow"]
    _logo.hide_render = False
    wall_g.inputs["Shadow Threshold"].default_value = wall_thresh
    wall_g.inputs["Dot Size"].default_value = 0.0


def grow(m, px):
    out = m.copy()
    for _ in range(px):
        g = out.copy()
        g[1:] |= out[:-1]; g[:-1] |= out[1:]; g[:, 1:] |= out[:, :-1]; g[:, :-1] |= out[:, 1:]
        out = g
    return out


# ---- raytraced light pass: everything white diffuse, Key Light only
sc.render.engine = 'CYCLES'
sc.cycles.device = 'GPU'; sc.cycles.samples = 16; sc.cycles.use_denoising = False
sc.cycles.max_bounces = 0; sc.cycles.use_adaptive_sampling = False
white = bpy.data.materials.new("ExportWhite")   # plain diffuse, like the shaders' toon mask
wt = white.node_tree; wt.nodes.clear()
dfn = wt.nodes.new("ShaderNodeBsdfDiffuse"); dfn.inputs["Color"].default_value = (1, 1, 1, 1)
wt.links.new(dfn.outputs[0], wt.nodes.new("ShaderNodeOutputMaterial").inputs["Surface"])
for ob in sc.objects:
    if ob.type == 'MESH':
        for slot in ob.material_slots:
            slot.material = white
    if ob.type == 'LIGHT':
        ob.data.shadow_soft_size = 0.0
lines = bpy.data.objects.get("Ink Lines")
if lines:
    lines.hide_render = True
for n in sc.world.node_tree.nodes:
    if n.type == 'BACKGROUND':
        n.inputs["Strength"].default_value = 0.0


def unlit(a, thresh):
    """Same test as the shaders: Shader to RGB -> RGB to BW < threshold."""
    bw = a[:, :, 0] * 0.2126 + a[:, :, 1] * 0.7152 + a[:, :, 2] * 0.0722
    return bw < thresh


# self shadow on the logo sides -> full colour, as the Pop Logo Shader does
if self_shadow > 0.5:
    dark = unlit(render("light_logo", linear=True), logo_thresh)
    sides = masks["highlight"] | masks["mid_base"] | masks["mid_lines"] | masks["full"]
    hit = dark & sides
    for k in ("highlight", "mid_base", "mid_lines"):
        masks[k] &= ~hit
    masks["full"] |= hit

# cast shadow on its own: logo invisible to the camera but still casting
logo = bpy.data.objects["Logo"]; logo.visible_camera = False
masks["shadow"] = unlit(render("light_shadow", linear=True), wall_thresh)
if dots is not None:
    masks["dots"] = dots & masks["shadow"]


def shrink(m, px):
    return ~grow(~m, px)


# antialiased edges between two ID colours can land nearest a third colour,
# leaving 1px slivers. Opening every layer (shrink, grow) drops anything
# thinner than 4px; then each lower layer grows under the ones above so the
# stack has no hairline gaps
masks["mid_base"] = masks["mid_base"] | masks["mid_lines"]   # solid under its lines
for k in ("full", "highlight", "mid_base", "mid_lines", "face"):
    masks[k] = grow(shrink(masks[k], 2), 2)
for k in ("full", "highlight", "mid_base", "mid_lines", "face"):
    masks[k] = grow(masks[k], 3)
logo_all = masks["full"] | masks["highlight"] | masks["mid_base"] | masks["face"]
masks["full"] = masks["full"] | shrink(grow(logo_all, 3), 3)  # dark backing fills any pinholes


def flatten(d, sx, sy, ty):
    """Bake potrace's transform (X = sx*x, Y = ty + sy*y) into the path data,
    so editors get plain coordinates and stroke widths stay true."""
    import re
    out, cmd, nums = [], None, []
    toks = re.findall(r"[MmLlCcZz]|-?[\d.]+(?:e-?\d+)?", d)
    def emit():
        if cmd is None:
            return
        if cmd in "Zz":
            out.append("Z"); return
        vals = [float(v) for v in nums]
        res = []
        for i in range(0, len(vals), 2):
            x, y = vals[i], vals[i + 1]
            if cmd.isupper():
                res += [sx * x, ty + sy * y]
            else:
                res += [sx * x, sy * y]
        out.append(cmd + " ".join("%.2f" % v for v in res))
    for t in toks:
        if t.isalpha():
            emit(); cmd, nums = t, []
        else:
            nums.append(t)
    emit()
    return "".join(out)


def trace(key, m):
    pbm = os.path.join(TMP, key + ".pbm")
    with open(pbm, "wb") as f:
        f.write(b"P4\n%d %d\n" % (W, H))
        f.write(np.packbits(m, axis=1).tobytes())
    svg = os.path.join(TMP, key + ".svg")
    subprocess.run([POTRACE, pbm, "-b", "svg", "-t", "4", "-a", "1.0", "-O", "0.4",
                    "-u", "20", "-o", svg], check=True)
    s = open(svg).read()
    g0 = s.index("<g "); g1 = s.index("</g>") + 4
    body = s[g0:g1]
    import re
    ty, sx, sy = (float(v) for v in re.search(
        r'translate\([-\d.]+,([-\d.]+)\) scale\(([-\d.]+),([-\d.]+)\)', body).groups())
    return (sx, sy, ty), re.findall(r'd="([^"]+)"', body)


LAYERS = [  # bottom -> top
    ("shadow", "Shadow"),
    ("dots", "Shadow dots"),
    ("full", "Sides full colour"),
    ("highlight", "Sides highlight"),
    ("mid_base", "Sides mid tone base"),
    ("mid_lines", "Sides mid tone hatch lines"),
    ("face", "Front faces"),
]
S = 100 / args.scale     # back to the scene's pixel size
out = ['<?xml version="1.0" encoding="UTF-8"?>',
       f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(W*S)}" height="{int(H*S)}" '
       f'viewBox="0 0 {int(W*S)} {int(H*S)}">',
       f'  <rect id="Wall" width="{int(W*S)}" height="{int(H*S)}" fill="{REAL["wall"]}"/>']
REAL["dots"] = REAL.pop("shadow_dot")
INK_W = INK[0][2] if INK else 4.0
def paths_of(key):
    (sx, sy, ty), ds = trace(key, masks[key])
    return [flatten(d, sx * S, sy * S, ty * S) for d in ds]

for key, label in LAYERS:
    if key not in masks or not masks[key].any():
        continue
    gid = label.replace(" ", "_")
    out.append(f'  <g id="{gid}" fill="{REAL[key]}" stroke="none">')
    out += [f'    <path d="{d}"/>' for d in paths_of(key)]
    out.append('  </g>')
    if key == "dots" or (key == "shadow" and "dots" not in masks):
        out.append(f'  <g id="Shadow_outline" fill="none" stroke="{REAL["strokes"]}" '
                   f'stroke-width="{INK_W:.2f}" stroke-linejoin="round">')
        out += [f'    <path d="{d}"/>' for d in paths_of("shadow")]
        out.append('  </g>')
if INK:
    col = REAL["strokes"]
    out.append('  <g id="Ink_strokes" fill="none">')
    for pts, closed, w in INK:
        d = "M" + " L".join("%.2f %.2f" % p for p in pts) + (" Z" if closed else "")
        out.append(f'    <path d="{d}" fill="none" stroke="{col}" stroke-width="{w:.2f}" '
                   f'stroke-linecap="round" stroke-linejoin="round"/>')
    out.append('  </g>')
    print("INK", len(INK), "strokes,", sum(c for _, c, _ in INK), "closed, width", round(INK[0][2], 2), "px")
out.append('</svg>')
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w").write("\n".join(out))
print("SVG", OUT, os.path.getsize(OUT), "bytes;", "colours", REAL)
