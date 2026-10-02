"""Curves in a Blender scene → SVG strokes for a pen plotter. Runs inside Blender (bpy, numpy).

    import plot_svg
    stats = plot_svg.export(objects, camera, "out.svg", page=(210, 148), margin=15, pen=0.5)
    plot_svg.export_scene(folder)      # one SVG per collection named "Plot <name>"
    plot_svg.raster("out.svg", "out.png", width=2400)       # needs Inkscape
    plot_svg.sheet(["a.svg", "b.svg"], "sheet.svg")         # side by side, for review only

What it reads: the evaluated curves of each object (Geometry Nodes output included) as strokes, and
its evaluated point cloud as dots. What it writes: millimetres, stroke only, one top-level Inkscape
layer per pen ("1 - lines", "2 - dots"), strokes ordered to cut pen-up travel. A dot is one spiral
stroke, because a plotter cannot fill.

A final .blend carries this file as the text block "plot_svg.py", so "Export SVG" runs without the repo.
"""
import colorsys
import math
import shutil
import subprocess
from pathlib import Path

import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view

DEFAULTS = {
    "page": (210.0, 148.0),   # mm, A5 landscape
    "margin": 15.0,           # mm
    "pen": 0.5,               # mm, the stroke width shown in previews
    "dot": 1.8,               # mm, dot diameter; 0: no dots
    "min_gap": 0.05,          # mm: a stroke running this close beside an earlier one is cut there; 0: off
    "end_dots": True,         # a dot on each end the cut leaves
    "simplify": 0.01,         # mm, tolerance for dropping points on straight runs
    "min_length": 0.3,        # mm, shorter strokes are dropped
    "min_loop": 8.0,          # mm, closed loops shorter than this are dropped (a speck at the top of a peak)
    "cusp_dots": True,        # a dot where a line folds back on itself (a smooth 3D curve seen end-on)
    "ink": "#262626",
}
INKSCAPE = shutil.which("inkscape") or "/Applications/Inkscape.app/Contents/MacOS/inkscape"


def read_geometry(obj, depsgraph):
    """World-space strokes [(N×3 array, cyclic)] and dots (M×3) of one evaluated object."""
    geo = obj.evaluated_get(depsgraph).evaluated_geometry()  # keep alive while reading
    mw = np.array(obj.matrix_world)
    strokes, dots = [], np.zeros((0, 3))

    def world(attr, n):
        co = np.empty(n * 3, np.float32)
        attr.data.foreach_get("vector", co)
        return co.reshape(-1, 3).astype(np.float64) @ mw[:3, :3].T + mw[:3, 3]

    c = geo.curves
    if c is not None and len(c.curves):
        pts = world(c.attributes["position"], len(c.points))
        off = np.empty(len(c.curves) + 1, np.int32)
        c.curve_offset_data.foreach_get("value", off)
        cyc = np.zeros(len(c.curves), bool)
        if "cyclic" in c.attributes:
            c.attributes["cyclic"].data.foreach_get("value", cyc)
        strokes = [(pts[off[i]:off[i + 1]], bool(cyc[i])) for i in range(len(c.curves)) if off[i + 1] - off[i] > 1]
    pc = geo.pointcloud
    if pc is not None and len(pc.points):
        dots = world(pc.attributes["position"], len(pc.points))
    return strokes, dots


def to_page(pts, scene, cam, page, margin):
    """Project world points through the camera into page millimetres (y down)."""
    uv = np.array([world_to_camera_view(scene, cam, _vec(p))[:2] for p in pts]).reshape(-1, 2)
    aspect = scene.render.resolution_x / scene.render.resolution_y
    w, h = page[0] - 2 * margin, page[1] - 2 * margin
    fw = min(w, h * aspect)                       # the camera frame, fitted inside the margins
    fh = fw / aspect
    x = (page[0] - fw) / 2 + uv[:, 0] * fw
    y = (page[1] - fh) / 2 + (1 - uv[:, 1]) * fh
    return np.stack([x, y], 1)


def _vec(p):
    from mathutils import Vector
    return Vector(p)


def _length(p):
    return float(np.linalg.norm(np.diff(p, axis=0), axis=1).sum()) if len(p) > 1 else 0.0


def _simplify(p, tol):
    """Ramer–Douglas–Peucker, iterative."""
    if tol <= 0 or len(p) < 3:
        return p
    keep = np.zeros(len(p), bool)
    keep[[0, -1]] = True
    stack = [(0, len(p) - 1)]
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        d = p[b] - p[a]
        n = np.linalg.norm(d)
        seg = p[a + 1:b] - p[a]
        dist = np.abs(seg[:, 0] * d[1] - seg[:, 1] * d[0]) / n if n > 1e-12 else np.linalg.norm(seg, axis=1)
        i = int(dist.argmax())
        if dist[i] > tol:
            keep[a + 1 + i] = True
            stack += [(a, a + 1 + i), (a + 1 + i, b)]
    return p[keep]


def _cusps(p, cyc, reach=1.0, angle=110.0):
    """Points where the stroke reverses within `reach` mm each side: the tips of projection folds."""
    if len(p) < 5:
        return []
    seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    found = []
    for i in range(1, len(p) - 1):
        a = min(int(np.searchsorted(s, s[i] - reach)), i - 1)
        b = max(min(int(np.searchsorted(s, s[i] + reach)), len(p) - 1), i + 1)
        u, v = p[i] - p[a], p[b] - p[i]
        nu, nv = np.linalg.norm(u), np.linalg.norm(v)
        if nu < 1e-6 or nv < 1e-6:
            continue
        turn = math.degrees(math.acos(max(-1.0, min(1.0, float(u @ v) / (nu * nv)))))
        if turn > angle:
            found.append((turn, i))
    tips, last = [], None          # one tip per fold: the sharpest point of each run
    for turn, i in found:
        if last is not None and s[i] - s[last[1]] < 2 * reach:
            if turn > last[0]:
                last = (turn, i)
                tips[-1] = p[i]
        else:
            last = (turn, i)
            tips.append(p[i])
    return tips


def _dedupe(strokes, tol, min_run=2.5):
    """Cut away the parts of a stroke that run along an earlier stroke (same place, same direction).
    Two meridians that project onto one line would otherwise be inked twice."""
    grid = {}
    out = []
    for p, cyc in strokes:
        q = np.vstack([p, p[:1]]) if cyc else p
        seg = np.diff(q, axis=0)
        ln = np.linalg.norm(seg, axis=1)
        tang = seg / np.maximum(ln, 1e-12)[:, None]
        tang = np.vstack([tang, tang[-1:]])
        cells = np.floor(q / tol).astype(int)
        dup = np.zeros(len(q), bool)
        for i, (cx, cy) in enumerate(cells):
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for t in grid.get((cx + dx, cy + dy), ()):
                        if abs(t[0] * tang[i, 0] + t[1] * tang[i, 1]) > 0.985:
                            dup[i] = True
        # Register this stroke, sampled every tol/2, after testing it (a stroke never hides itself).
        for a, b, l, t in zip(q[:-1], q[1:], ln, tang):
            for s in np.linspace(0, 1, max(2, int(l / (tol / 2)) + 1)):
                c = a + (b - a) * s
                grid.setdefault((int(math.floor(c[0] / tol)), int(math.floor(c[1] / tol))), []).append(t)
        if not dup.any():
            out.append((p, cyc))
            continue
        # Keep duplicate runs shorter than min_run: those are crossings, not overlaps.
        runs, i = [], 0
        while i < len(q):
            j = i
            while j + 1 < len(q) and dup[j + 1] == dup[i]:
                j += 1
            runs.append((i, j, bool(dup[i])))
            i = j + 1
        for a, b, d in runs:
            if d and _length(q[a:b + 1]) < min_run:
                dup[a:b + 1] = False
        if not dup.any():
            out.append((p, cyc))
            continue
        i = 0
        while i < len(q):
            if dup[i]:
                i += 1
                continue
            j = i
            while j + 1 < len(q) and not dup[j + 1]:
                j += 1
            if j > i:
                out.append((q[i:j + 1], False))
            i = j + 1
    return out


def _order(strokes, start=(0.0, 0.0)):
    """Greedy nearest neighbour. Open strokes may reverse; closed ones start at their nearest point."""
    todo = list(strokes)
    pos = np.array(start, float)
    out = []
    while todo:
        best = None
        for k, (p, cyc) in enumerate(todo):
            if cyc:
                d = np.linalg.norm(p - pos, axis=1)
                i = int(d.argmin())
                cand = (d[i], k, i)
            else:
                d0, d1 = np.linalg.norm(p[0] - pos), np.linalg.norm(p[-1] - pos)
                cand = (min(d0, d1), k, 0 if d0 <= d1 else -1)
            if best is None or cand[0] < best[0]:
                best = cand
        _, k, i = best
        p, cyc = todo.pop(k)
        if cyc:
            p = np.roll(p, -i, axis=0)
        elif i == -1:
            p = p[::-1]
        out.append((p, cyc))
        pos = p[0] if cyc else p[-1]
    return out


def _spiral(c, diameter, pen):
    """One stroke that fills a dot: a spiral out from the centre, closed by a full circle."""
    r = max(diameter / 2 - pen / 2, pen * 0.1)    # the pen's own width reaches the rim
    turns = max(r / (pen * 0.8), 0.0)
    n = int(turns * 16)
    a = np.linspace(0, turns * math.tau, n + 1)[:-1] if n else np.zeros(0)
    rad = r * a / (turns * math.tau) if n else np.zeros(0)
    a2 = turns * math.tau + np.linspace(0, math.tau, 17)
    ang = np.concatenate([a, a2])
    rad = np.concatenate([rad, np.full(17, r)])
    return c + np.stack([rad * np.cos(ang), rad * np.sin(ang)], 1)


def _travel(strokes, start=(0.0, 0.0)):
    pos, up = np.array(start, float), 0.0
    for p, cyc in strokes:
        up += float(np.linalg.norm(p[0] - pos))
        pos = p[0] if cyc else p[-1]
    return up


def _path(p, cyc):
    d = "M" + " L".join(f"{x:.3f},{y:.3f}" for x, y in p)
    return f'<path d="{d}{" Z" if cyc else ""}"/>'


def export(objects, camera, path, scene=None, debug=None, **opts):
    """Write one SVG. Returns the plot's stats. debug=<path> also writes the plot-check drawing."""
    o = {**DEFAULTS, **opts}
    scene = scene or bpy.context.scene
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    lines, dots = [], []
    for ob in objects:
        strokes, pts = read_geometry(ob, dg)
        lines += [(to_page(p, scene, camera, o["page"], o["margin"]), cyc) for p, cyc in strokes]
        if len(pts) and o["dot"] > 0:
            dots += list(to_page(pts, scene, camera, o["page"], o["margin"]))
    n_in, closed_in = len(lines), sum(c for _, c in lines)
    marks = []
    # Longest first, so a duplicate is cut from the shorter stroke.
    lines.sort(key=lambda s: -_length(s[0]))
    if o["min_gap"] > 0:
        n_open = sum(not c for _, c in lines)
        ends_before = {tuple(np.round(e, 3)) for p, c in lines if not c for e in (p[0], p[-1])}
        lines = _dedupe(lines, o["min_gap"])
        if o["end_dots"] and o["dot"] > 0:
            for p, c in lines:
                if not c and _length(p) >= o["min_length"]:
                    marks += [e for e in (p[0], p[-1]) if tuple(np.round(e, 3)) not in ends_before]
    lines = [(_simplify(p, o["simplify"]), cyc) for p, cyc in lines]
    lines = [(p, cyc) for p, cyc in lines
             if _length(p) >= o["min_length"] and not (cyc and _length(np.vstack([p, p[:1]])) < o["min_loop"])]
    if o["cusp_dots"] and o["dot"] > 0:
        for p, cyc in lines:
            marks += _cusps(p, cyc)
    dots = marks + dots   # ends and fold tips first: they win when two dots would touch
    lines = _order(lines)
    if dots:  # drop dots that touch or sit on top of each other
        uniq = []
        for d in dots:
            if all(np.linalg.norm(d - u) > o["dot"] * 1.5 for u in uniq):
                uniq.append(d)
        dots = uniq
    end = (lines[-1][0][0] if lines[-1][1] else lines[-1][0][-1]) if lines else (0, 0)
    spirals = _order([(_spiral(d, o["dot"], o["pen"]), False) for d in dots], start=end)

    allp = np.vstack([p for p, _ in lines + spirals]) if lines or spirals else np.zeros((1, 2))
    w, h = o["page"]
    stats = {
        "strokes_in": n_in, "closed_in": closed_in, "strokes": len(lines), "closed": sum(c for _, c in lines), "dots": len(spirals),
        "points": int(sum(len(p) for p, _ in lines)),
        "draw_mm": round(sum(_length(np.vstack([p, p[:1]]) if c else p) for p, c in lines + spirals)),
        "travel_mm": round(_travel(lines) + _travel(spirals, start=end)),
        "off_page": int(((allp < 0).any(1) | (allp[:, 0] > w) | (allp[:, 1] > h)).sum()),
        "bounds_mm": [round(float(v), 1) for v in (*allp.min(0), *allp.max(0))],
    }
    style = f'fill="none" stroke="{o["ink"]}" stroke-width="{o["pen"]}" stroke-linecap="round" stroke-linejoin="round"'
    svg = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
        f'width="{w:g}mm" height="{h:g}mm" viewBox="0 0 {w:g} {h:g}">',
        f'<g inkscape:groupmode="layer" inkscape:label="1 - lines" id="lines" {style}>',
        *[_path(p, c) for p, c in lines], "</g>",
        f'<g inkscape:groupmode="layer" inkscape:label="2 - dots" id="dots" {style}>',
        *[_path(p, c) for p, c in spirals], "</g>", "</svg>",
    ]
    Path(path).write_text("\n".join(svg), encoding="utf-8")
    if debug:
        _debug(lines, spirals, o, debug)
    return stats


def _debug(lines, spirals, o, path):
    """The plot check: each stroke in its own hue in plot order, pen-up moves in red, starts ringed."""
    w, h = o["page"]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}mm" height="{h:g}mm" viewBox="0 0 {w:g} {h:g}">',
           f'<rect width="{w:g}" height="{h:g}" fill="white"/><g fill="none" stroke-linecap="round">']
    pos = np.zeros(2)
    seq = lines + spirals
    for i, (p, cyc) in enumerate(seq):
        r, g, b = colorsys.hsv_to_rgb(0.75 * i / max(len(seq) - 1, 1), 0.9, 0.75)
        col = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
        out.append(f'<path d="M{pos[0]:.2f},{pos[1]:.2f} L{p[0][0]:.2f},{p[0][1]:.2f}" stroke="#ff2020" stroke-width="0.08"/>')
        out.append(_path(p, cyc).replace("<path", f'<path stroke="{col}" stroke-width="{o["pen"] * 0.6:.2f}"'))
        if i < len(lines):
            out.append(f'<circle cx="{p[0][0]:.2f}" cy="{p[0][1]:.2f}" r="0.5" stroke="{"#00a040" if cyc else "#000"}" stroke-width="0.12"/>')
        pos = p[0] if cyc else p[-1]
    out.append("</g></svg>")
    Path(path).write_text("\n".join(out), encoding="utf-8")


def export_scene(folder=None, prefix="", scene=None, debug=False, **opts):
    """One SVG per collection named "Plot <name>": its camera frames the page, its other objects are drawn.
    Scene custom properties plot_page_w, plot_page_h, plot_margin, plot_pen, plot_dot, plot_min_gap override
    the defaults; the same properties on a "Plot" collection override the scene for that plot. Returns {name: stats}."""
    scene = scene or bpy.context.scene
    folder = Path(folder or bpy.path.abspath("//") or ".")
    o = dict(opts)
    if "plot_page_w" in scene and "page" not in o:
        o["page"] = (float(scene["plot_page_w"]), float(scene["plot_page_h"]))
    for k in ("margin", "pen", "dot", "min_gap"):
        if f"plot_{k}" in scene and k not in o:
            o[k] = float(scene[f"plot_{k}"])
    results = {}
    for col in bpy.data.collections:
        if not col.name.startswith("Plot "):
            continue
        cams = [ob for ob in col.all_objects if ob.type == "CAMERA"]
        if not cams:
            print(f"[out] {col.name}: no camera in the collection, skipped")
            continue
        name = col.name[5:].strip().lower().replace(" ", "-")
        path = folder / f"{prefix}{name}.svg"
        dbg = path.with_name(path.stem + "_check.svg") if debug else None
        own = {k[5:]: float(col[k]) for k in col.keys() if k.startswith("plot_")}  # a plot's own overrides
        results[name] = export([ob for ob in col.all_objects if ob.type != "CAMERA"], cams[0], path,
                               scene=scene, debug=dbg, **{**o, **own})
        results[name]["path"] = str(path)
        print(f"[out] {path.name}: {results[name]}")
    return results


def sheet(svgs, path, gap=0.0, paper="#efefef"):
    """Several plot SVGs side by side on one canvas. For review rasters, not for plotting."""
    import re
    parts, x, hmax = [], 0.0, 0.0
    for s in svgs:
        text = Path(s).read_text(encoding="utf-8")
        w, h = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', text).groups())
        body = text[text.index(">", text.index("<svg")) + 1:text.rindex("</svg>")]
        parts.append(f'<g transform="translate({x:g},0)">{body}</g>')
        x += w + gap
        hmax = max(hmax, h)
    x -= gap
    Path(path).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
        f'width="{x:g}mm" height="{hmax:g}mm" viewBox="0 0 {x:g} {hmax:g}">'
        f'<rect width="{x:g}" height="{hmax:g}" fill="{paper}"/>' + "".join(parts) + "</svg>", encoding="utf-8")


def raster(svg, png, width=2400, paper="#efefef"):
    """SVG → PNG with Inkscape."""
    r = subprocess.run([INKSCAPE, str(svg), "--export-type=png", f"--export-filename={png}",
                        f"--export-width={width}", f"--export-background={paper}", "--export-background-opacity=1"],
                       capture_output=True, text=True)
    if not Path(png).exists():
        raise RuntimeError(f"Inkscape did not write {png}: {r.stderr[-400:]}")
    return png
