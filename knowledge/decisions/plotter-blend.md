# plotter-blend — decisions

Line-art forms as Geometry Nodes curves, exported as SVG strokes for a pen plotter. Two forms: the contour sphere and the funnel from the reference sheet. Final v06: 7.2 in round 6, about 6.4 calibrated (blind pair v05 6.4, v06 6.3, Opus; target 8.5).

## Chosen

- **Sphere = contour lines** of `p·a + A·bump(c1) − balance·A·bump(c2)` on a sphere. Research (an Opus agent with its own test renders) ruled out a point warp: it cannot close rings.
- **Contours live in Geometry Nodes** by marching triangles in a For Each zone (`Isolines` group: any float field on any mesh). The saved `.blend` keeps live sliders.
- **Funnel = flared catenoid**, `r = a·cosh(k·u^flare)`. A true catenoid (flare 1) missed the measured ring radii at even heights; flare 1.36 hits all five.
- **Own SVG exporter** (`tools/plot_svg.py`), also embedded in the `.blend` as a text block, so "Export SVG" runs without the repo. Greedy stroke ordering, spiral dots, a per-plot minimum-gap rule, dots on cut ends and fold tips.
- **The review image is an Inkscape raster of the SVG**, and the preflight sheet is a plot check (stroke order, pen-up moves).

## Rejected

- Sverchok: 1.4.0 lists Blender 3.6–5.1 with an open activation bug on 5.1; needs installing into the Blender config. Not tested on 5.2.
- Grease Pencil SVG export and Freestyle: fail headless or ignore curves (see `gotchas/headless.md`).
- Streamline integration in a Repeat zone: one seed per contour, loops do not close exactly.
- Pure Python shapes: no live sliders in the `.blend`.
- vpype as a required step: the exporter orders strokes itself. vpype is still useful for `stat` and for merging several plots.
- BVH hidden-line removal: both references are see-through. `Back Reach` covers front-only for the sphere.

## Open

- **Draw through or cut at the limb.** Round 1 asked for whole see-through loops; round 6 asked to cut each line where it turns away. It is one control, `Back Reach` (2: whole loops; ~0.1: front only), with `Ragged Ends`. Left at 2 with dotted fold tips (`output/sphere.svg`); the cut version ships beside it (`output/sphere_cut.svg`, Back Reach 0.15). The calibration reviewer asked for the cut again.
- No single S-band stands out; the top pole ellipse folds into a hairpin; the sphere has 15–16 lines against 12–14.
- Funnel flanks: front and back meridians run one to two line widths apart at the throat. Rotating the meridians half a step would fix it and lose the reference's centre line.
- No fork was run (budget 6 by choice; the brief is an exploration). Candidate mechanisms for a next version: a third weak bump for the top ellipse; a hidden-line mode for the funnel's back half; contours of other fields (spherical harmonics, moiré) through the same `Isolines` group.
