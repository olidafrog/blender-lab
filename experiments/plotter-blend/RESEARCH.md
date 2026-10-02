# plotter-blend — research

## Read of the reference

A sheet of thin monoline icons with a dot at each node, on light grey paper. Two targets.

1. **Sphere** (`ref_sphere.png`). About 12–14 lines that run as tilted parallels and bend into an S through the middle. Around two "eyes" (upper right, lower left) the innermost lines are closed rings with no free ends. Small polar ellipses at the top and bottom. Front and back are both drawn. Dots sit along the lines at uneven spacing, 3–6 per line.
2. **Funnel** (`ref_vortex.png`). A surface of revolution: 16 meridians × 5 parallels, both sides drawn, a dot at every crossing. The bottom ring is the throat; the sides are vertical there. Viewed about 12° above side-on, no visible perspective.

## Most likely process

The sphere is a **contour drawing**: level sets (isolines) of a scalar field on a sphere. The field is latitude plus one raised and one sunken bump: `f(p) = p·a + A·exp(−(1−p·c1)/σ²) − A·exp(−(1−p·c2)/σ²)`. Latitude circles are the level sets of `p·a`; the bumps close the lines into rings around a peak and a trough, with an S-shaped separatrix between. A point warp (Illustrator Twirl, Simple Deform Twist, point-vortex advection) cannot make it: it moves the points of a line, so a line can spiral but never become a closed ring. Names to search: "contour lines / isolines on a sphere", "level sets of a scalar field", "Kelvin's cat's eyes" (the fluid-dynamics name for the eye-and-separatrix pattern), and "Rex block / dipole block" on weather maps (search snippet only). The funnel is a wireframe of a **catenoid** (the wormhole-throat embedding shape), stretched vertically. The original was probably drawn in a vector tool or exported from a maths/CAD wireframe; the dots mark nodes.

## Techniques to use

- **Contours in Geometry Nodes** (5.x). There is no contour node. Build marching triangles: a For Each Element zone over the levels; per level, each triangle of an icosphere that the level crosses gives one 2-point segment (corner values through Corners of Face → Evaluate at Index); Merge by Distance joins the segments; Mesh to Curve gives closed splines. The field is an input, so the same group draws contours of any field on any mesh. Zone API tested by the GN agent (`ri.pair_with_output(ro)`); For Each exists since 4.3 (release notes in `reference/dev-docs`).
- **Funnel in Geometry Nodes.** Meridians: Curve Line → Resample → Set Position to `(r(z), 0, z)` → Instance on Points with rotation → Realize. Parallels: Curve Circle instances scaled by `r(z_k)`. Dots: Curve to Points (COUNT = meridians) on the parallels; the circle starts at φ = 0, so the dots land on the meridians (tested, error 1.3e-5). Profile `r = a·cosh(z/(s·a))`.
- **Readback.** `g = obj.evaluated_get(dg).evaluated_geometry()`; keep `g` alive; `g.curves` (`curve_offset_data`, `attributes["position"]`, `attributes["cyclic"]`) and `g.pointcloud` for dots. Tested on 5.2.2.
- **SVG.** Own exporter: project with the camera, write one `<polyline>` per stroke, `width/height` in mm with a matching `viewBox`, `fill="none"`, one top-level Inkscape layer per pen (`1 - lines`, `2 - dots`). Optional hidden-line removal by ray cast against an occluder (BVH: 40,000 rays in 0.07 s), strokes split at visibility changes; dashes as real short polylines (plotters ignore `stroke-dasharray`). Dots as small open circles: filled shapes do not plot.
- **Plot optimisation.** vpype 1.15 (installed): `linemerge`, `linesimplify`, `linesort`. Inkscape (installed) rasterises the SVG for review.
- **Modifier inputs from Python** (5.2): `getattr(mod.properties.inputs, item.identifier).value = v`.

## Rejected approaches

- **Sverchok.** Latest release 1.4.0 lists Blender 3.6–5.1; issue #5371 reports it will not activate on 5.1 beta; 5.2 is not listed. It would also need installing into the Blender config, which the lab does not do (factory startup). Geometry Nodes now covers what it was used for here.
- **`wm.grease_pencil_export_svg` headless.** Returns FINISHED but writes garbage coordinates: it projects from the largest 3D viewport, which a background run does not have. Fine in the GUI only.
- **Freestyle + SVG exporter.** Freestyle draws mesh faces only (0 px for curves and loose edges, tested), and the exporter is no longer bundled.
- **Point warp of latitude circles.** Tested by the GN agent: lines spiral, no closed eyes.
- **Point-vortex stream function** `Γ·log(1−p·c)`: a tight spiral of rings at each centre, which the reference does not have.
- **Streamline integration in a Repeat zone.** Works, but needs one seed per contour and the loops do not close exactly.
- **Pure Python shapes.** Easy, but the saved `.blend` has no live sliders.
- **vpype `occult` for hidden lines.** Works on closed polygons in layer order only; a self-occluding 3D curve set needs the test in 3D.

## Numeric targets

Measured on the 4× crops, given relative to the form so they hold at any plot size.

| What | Reference |
|---|---|
| Sphere: line count | 12–14 levels |
| Sphere: closed rings per eye | 2–3 |
| Sphere: eye centres | about 40° off the view axis, opposite each other (upper right, lower left) |
| Sphere: axis | tipped ~20° to the viewer, rolled ~12° clockwise |
| Sphere: field | A ≈ 1.0, σ ≈ 0.45 (agent's test fit) |
| Line width / sphere diameter | ~0.7 % (1.2 px on 178 px) |
| Dot diameter / sphere diameter | ~2 % |
| Sphere dots | 3–6 per line, uneven |
| Funnel: meridians × parallels | 16 × 5 |
| Funnel: ring radii, rim → throat (rim = 1) | 1, 0.61, 0.44, 0.37, 0.35 |
| Funnel: ring depths (of total) | 0, 0.27, 0.55, 0.78, 1 (near-even steps) |
| Funnel: height / rim diameter | ~0.48 |
| Funnel: ellipse minor / major | 0.20 → camera 12° above horizontal, orthographic |

## Open questions

- Do the marching-triangle segments merge into closed loops (count open strokes; expect 0)?
- Is the For Each zone fast enough to feel live (14 levels × 80k triangles)?
- How should a plotter draw a filled dot: one small circle, or concentric rings?

## Sources

- https://en.wikipedia.org/wiki/Schwarzschild_metric — Flamm's paraboloid vs gravity well
- https://mathworld.wolfram.com/Pseudosphere.html — tractricoid profile (ruled out)
- https://arxiv.org/html/2304.00264 — Kelvin–Stuart cat's eyes stream function
- https://github.com/nortikin/sverchok/releases and /issues/5371 — Sverchok version support
- https://extensions.blender.org/add-ons/freestyle-svg-exporter — no longer bundled
- https://blenderartists.org/t/exporting-to-svg-in-blender-5-1/1637131
- Blender source `grease_pencil_io_export_svg.cc` — why the GP exporter fails headless
- https://wiki.evilmadscientist.com/AxiDraw_Layer_Control — layer naming for pens
- https://axidraw.com/doc/cli_api/
- https://penplotterkit.com/guides/how-to-prepare-svg-for-plotting/
- https://vpype.readthedocs.io/en/latest/fundamentals.html
- https://github.com/LoicGoulefert/occult
- https://www.generativehut.com/post/from-obj-to-pen-plotter
- https://code.blender.org/2025/08/bundles-and-closures/
- https://blenderartists.org/t/exporting-curve-objects-with-geometry-nodes-on-them/1615226
- Local: `reference/dev-docs` release notes 4.3–5.2, `reference/manual` `grease_pencil_svg.rst`
- Headless tests on 5.2.2 by three agents (scratchpad `svg-tests/`, `gn-tests/`, `sph.py`).
- Found nothing: the icon sheet's author or source. Could not open: patreon.com/msurguy (403).
