# Review v01 — plotter-forms

## 1. Score: 6.8 / 10

3D read 6.6 · hidden lines 6.8 · plot readiness 6.0 · variety 8.0. No pair given.

## 2. Targets

- **Forms:** 48 in 5 families. Hit.
- **Lines through opaque surfaces:** none found. Hit.
- **Fragments:** rim ticks on `kuen`, dash clusters inside `klein-eight`, stubs at the `enneper` centre, a neck dash on `monkey-slices`. Missed.
- **Blots over 15 px** (solid ink after a 15 px opening): `hopf-meridian` 129×83 px, `hopf-spiral` 61×45, `hopf-arcs` 25×38, `hopf-torus` 17×34, `hopf-nested` 17×16. Missed.
- **Lines leaving the cell:** none. Hit.

## 3. What works

- The opaque solids read as volumes, with clean hidden lines: `gyroid-ball`, `schwarz-cube`, `knot-slices`, `seashell`, `torus-waffle`, `mobius`.
- `klein-ghost`: the grey second pen adds depth.
- The range is wide. The surface and terrain rows show different mechanisms.

## 4. Problems, ranked

1. **Hopf blots.** In five Hopf forms, every fibre meets at one knot (lower left in `hopf-meridian`), and the knot is solid ink. Tuning the counts will not fix this. Treat each latitude's torus as an opaque surface for hidden-line removal, so that the back halves of its circles drop out. Also rotate the S³ view so that no fibre passes near the projection pole.
2. **Fragments at silhouettes.** `kuen` has ticks and a doubled rim at its top left. `klein-eight` has dashes on its inner right wall. Add a pass that deletes visible runs under 1 mm and closes gaps under 0.5 mm. Sample visibility more densely near silhouettes, and offset rays along the normal.
3. **`monkey-slices` faceting.** The slice lines zigzag and break across the cheeks. Slice a subdivided mesh and smooth the polylines before hidden-line removal.
4. **The spheres read flat.** All 10 are disc patterns in one outline. `sphere-spiral` and `sphere-waves` show no volume. Tilt the fields so that features wrap round the limb, or add a faint meridian net on the second pen.
5. **Near-copies.** Four Hopf forms share one view and one knot. Give each its own camera. `helicoid-catenoid` step 5 has a torn flap on its left lip.

## 5. Checklist

1. Every form reads as 3D? **No.** The Hopf tangles, `sphere-spiral` and `sphere-waves` read flat.
2. Hidden lines correct? **No.** See the flap on `helicoid-catenoid` step 5 and the dashes on `klein-eight`.
3. Silhouettes clean? **No.** `kuen` has a doubled rim.
4. Any blots? **Yes**, in five Hopf forms.
5. All lines smooth? **No.** `monkey-slices` zigzags. The `ridgeline-pulsar` peaks are sawtooth noise, not smooth bumps.
6. Variations varied? **Mostly.** The exceptions are the Hopf group and helicoid steps 1–3.
7. Each cell a finished plot? **No:** the Hopf forms, `monkey-slices` and `klein-eight` are not.
8. Any form mathematically wrong? **No.** The viewpoint of `hopf-torus` hides its torus hole.

## 6. What 8.5 needs

- Opaque-torus hidden-line removal and new views for the Hopf forms.
- The fragment cleanup pass.
- A smoothed `monkey-slices`.
- A volume cue on the spheres.
- Smoother peaks for `ridgeline-pulsar`.
