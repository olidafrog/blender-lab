# Review v05 — plotter-forms

## 1. Score: 6.8 / 10

3D read 7.0 · hidden lines and silhouettes 6.3 · plot readiness 5.8 · variety 8.0

Pairwise: P is better. Its harmonics (tesseral, pair, charges) are lumpy volumes and its wave-field is in perspective; Q has flat discs. P adds silhouette dashes.

## 2. Targets

| Target | Measured | Result |
|---|---|---|
| ≥ 40 forms, 5 families | 50 (7 / 12 / 8 / 15 / 8) | hit |
| Lines through a surface | none seen | hit |
| Stray fragments | about 40 dashes in ridgeline-ripple; more in wave-field, mobius, enneper, kuen, harmonic-tesseral, harmonic-pair | missed |
| Blots > 15 px | hopf-nested centre: lines 3 px (0.6 mm) apart over about 60 px; hopf-torus and harmonic-relief look the same | missed (borderline) |
| Lines leaving the cell | only hopf-tumble | hit |

## 3. What works

- Klein-bottle, seashell, torus-waffle, knot-slices, flamm, scherk and blobs are finished plots.
- The v05 harmonics read as volumes. Monkey-slices proves the any-mesh path.
- Each family has its own line language, so the range is wide.

## 4. Problems, ranked

1. **ridgeline-ripple, wave-field, mobius twist, enneper centre.** Lines break into dashes next to occluding edges. Per-sample depth tests toggle. Split segments exactly where they cross the projected occluder, then merge gaps under 0.5 mm and drop runs under 1 mm.
2. **harmonic-tesseral (top, right rim), harmonic-pair (top-left), kuen (top-left, right lobe).** Grazing contours flicker at the silhouette. Draw the true silhouette (n·v = 0) as its own stroke. Suppress contour runs within 0.5 mm of it.
3. **hopf-nested, hopf-onion (centre right).** Fibres pinch through the axis: a tangle and a near-blot. Drop the far line where two strokes run closer than 0.6 mm, or trim fibres inside a core radius.
4. **hopf-tumble, hopf-links.** See-through loops have short gaps. Find the HLR or clip step that splits them.
5. **catalan centre, henneberg fold, kuen lower half.** Zigzag tangles at branch points. Sample finer near cusps and stop the domain short of the branch points.

## 5. Checklist

1. No: hopf-meridian reads flat; the centres of hopf-nested, hopf-onion and catalan, and kuen's lower half, are tangles.
2. No: gaps in ridgeline-ripple, wave-field, mobius and hopf-tumble.
3. No: rim dashes on harmonic-tesseral, harmonic-pair and kuen; a stray curl in helicoid-catenoid frame 5.
4. Yes: hopf-nested, hopf-torus, harmonic-relief.
5. No: henneberg and catalan zigzag at their folds.
6. Mostly yes. Hopf torus, nested, onion and spiral share one swirl. Tesseral, pair and charges are close.
7. No for hopf-nested, hopf-onion, catalan and ridgeline-ripple. About 30 cells are ready.
8. No errors visible.

## 6. What 8.5 needs

- Exact splitting at occluders, then a gap-merge and short-run cull.
- A true silhouette stroke on each opaque form.
- Thinning by screen spacing at the Hopf cores and in harmonic-relief.
- Unbroken see-through Hopf loops.
- Trimmed domains for catalan, henneberg and kuen.
