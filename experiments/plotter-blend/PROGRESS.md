# plotter-blend — progress

Machine: Mac, Blender 5.2.2, Metal. 5.x only (For Each zone, `evaluated_geometry()`). Builder Fable 5.1, reviewer Opus, advisor Opus. Research: one Opus agent (forms), two Sonnet agents (SVG export, GN), all with headless tests.

Process guess: the sphere is contour lines of "latitude + a peak + a trough" on a sphere; the funnel is a stretched catenoid wireframe.

The "render" here is a raster of the exported SVG (Inkscape), not a Cycles render. The preflight sheet is a plot check (open strokes, pen travel, stroke order), not the clay/mirror sheet.

Knowledge that lands in v01:
- GN modifier inputs: `mod.properties.inputs.<identifier>.value` → `set_input()` helper in `build.py`.
- GN Bounding Box / Mesh Line defaults (Use Radius, Offset 0,0,1) → set explicitly where used.
- Assert something countable after every silent step → open-stroke count, on-sphere error and stroke counts printed as `[out]` lines and asserted.
- Join Geometry reverses order → strokes carry a `layer` attribute; never rely on spline order.
- zsh loops drop `--set` → variants through `tools/sweep.sh`.
- Fine pattern pitch → raster at 2400 px wide so a 0.3 mm line is ≥ 3 px.

Newest first. Updated after every review. Cost is what the version took: Blender runs and minutes since the last row.

## Advisor (Opus), plan stage

Kept marching triangles. Changed four things on its advice:
1. The reference sphere has open strands that end on dots, not only closed loops → `Back Reach` and `Ragged Ends` cut the contours by how far they face the viewer (cut on the mesh, before Mesh to Curve), and every loose end gets a dot.
2. Crossings clamped off the triangle corners (t in 0.001–0.999) so a level through a vertex cannot make a four-way junction.
3. The funnel's front and back centre meridians project onto one line → the exporter cuts a stroke where it runs along an earlier one (`dedupe`).
4. Dots as one spiral stroke each, on their own layer, plotted last. BVH hidden-line modes deferred: both references are see-through.

| Version | Score | The one change | Cost | Render |
|---|---|---|---|---|
| v06 | 7.2 | Pole Ring (levels run pole ring to pole ring → closed ellipses), flatter bands; min-gap rule cuts lines that would blot and ends them on dots; fold-tip dots | 6 runs, 1 sweep, ~20 min | renders/v06.png |
| v05 | 6.8 | Fewer lines (8), balanced eyes at 2–3 rings; dots on fold tips; speck loops dropped | 2 runs, 1 sweep, ~10 min | renders/v05.png |
| v04 | 6.7 | More lines (11), tighter weaker eyes, pole tilted so the ball reads round | 2 runs, 1 sweep, ~10 min | renders/v04.png |
| v03 | 6.4 | Fewer lines (6), eyes at 2 rings; funnel Flare so rings sit at even heights with the measured radii; dots kept apart | 3 runs, 2 sweeps, ~15 min | renders/v03.png |
| v02 | 6.5 | Closed see-through contours (Back Reach 2), stronger eyes, more tilt; funnel rings to the measured radii | 5 runs, 1 sweep, ~15 min | renders/v02.png |
| v01 | 6.0 | First build: GN contours (front + short back reach, ragged ends), catenoid funnel, own SVG exporter | ~14 runs, 3 sweeps, ~70 min incl. research | renders/v01.png |

## Calibration

Blind pair, one fresh Opus reviewer: v05 6.4, v06 6.3 (funnels identical; the sphere decides). A tie inside the ±0.4 noise, so the round-6 score of 7.2 was generous: the calibrated level is about 6.4. Against v06: an undotted V fold at the lower left, a speck-sized inner ring in the upper eye, a deeper notch. For v06: the bottom pole ellipse. Finished from v06 (v05's level spacing predates `Pole Ring` and no longer exists in the code).

No fork (see Budget in `BRIEF.md`). The calibration reviewer again asked to cut the lines at the silhouette. That is the `Back Reach` control: `output/sphere.svg` draws through (2.0), `output/sphere_cut.svg` cuts at the limb (0.15, `ragged_ends=0.2`).

## Report

- Trend: 6.0, 6.5, 6.4, 6.7, 6.8, 7.2; calibrated about 6.4. Funnel 8.0 and on every measured target from v03; the sphere holds the score down (5.6–6.5).
- Repeated complaints: the sphere's left edge (hairpins, not a round outline), no single S-band, lines nearly touching at the right edge and the funnel's flanks.
- Next mechanisms: cut at the silhouette as the default with a drawn limb arc; a third weak bump for the top ellipse; hide the funnel's back meridians near the outline.
