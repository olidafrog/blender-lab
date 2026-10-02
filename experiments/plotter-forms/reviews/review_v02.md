# Review v02 — plotter-forms

## 1. Score: 7.0 / 10

3D read 7.0 · hidden lines 6.5 · plot readiness 6.5 · variety 8.0.

Pairwise: P is better. Q's Hopf tori are see-through tangles with ink knots at the poles. P makes them opaque, readable surfaces.

## 2. Targets

| Target | Measured | Result |
|---|---|---|
| ≥40 forms, 5 families | 49, 5 | hit |
| Lines through an opaque surface | none clear; klein-eight is suspect | hit, with a doubt |
| Stray fragments | about 8 cells have ticks or dashes | **missed** |
| Blots ≤15 px | largest 11 px (hopf-torus pole) | hit |
| Lines leaving the cell | none | hit |

## 3. What works

- The slice family (blobs, gyroid-ball, schwarz-cube, knot-slices) reads as solid objects with clean occlusion.
- klein-bottle, klein-ghost, seashell, helicoid-catenoid and flamm are ready to plot.
- The variety answers the brief: every family has visibly different variations.

## 4. Problems, ranked

1. **Fragments where lines end at folds.** klein-eight: hook dashes on the right rim. mobius: squiggles inside the twist, lower right. henneberg: ticks along the lower fold. kuen: ticks on the upper-left rim. catalan: ticks at the cusps. enneper: stubs at the centre. Fix: after the hidden-line cut, drop strokes under 1.5 mm and join ends less than 0.5 mm apart. More mesh resolution will not fix this.
2. **klein-eight, right half.** The u-lines bend into V shapes, and some arcs seem to cross lines that should hide them. Fix: split the figure-8 into its two lobes before the hidden-line test.
3. **Sphere rims.** sphere-ripples and sphere-noise end in short dashes all round the rim, and their rings are polygonal. Fix: use a finer grid, and drop contours where the surface is nearly edge-on (n·v < 0.15).
4. **monkey-slices.** The slices step along the low-poly faces, and there are hooked stubs at the neck and the right cheek. Fix: subdivide the mesh before slicing.
5. **Weak 3D read.** mobius reads as a plain ring; tilt the view to show the half-twist. hopf-meridian has faceted outer ellipses (add samples) and a knot at the lower left. sphere-spiral ends in a ragged empty cap; end every stripe on one latitude.

## 5. Checklist

1. 3D read: no. mobius, hopf-meridian, hopf-links (spikes) and wave-field read flat or tangled.
2. Hidden lines correct: no. klein-eight is suspect; flamm's far radial lines stop unevenly.
3. Silhouettes clean: no. Ticks (see 1); doubled rims on dini and gyroid-ball.
4. Blot at a pole: no. hopf-torus and hopf-onion are dense but under 15 px.
5. Lines smooth: no. monkey-slices, sphere-ripples, sphere-noise and hopf-meridian are faceted.
6. Variations varied: yes.
7. Each cell plots on its own page: no. About 8 cells need cleanup.
8. Wrong for its label: no clear errors. mobius hides its twist.

## 6. What 8.5 needs

Fixes 1–5 above, with the stroke filter first: it clears most of the fragments at once.
