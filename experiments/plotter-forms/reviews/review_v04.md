# Review v04 — plotter-forms

## 1. Score: 7.1 / 10

3D read and form 7.0 · hidden lines and silhouettes 6.8 · plot readiness 6.3 · variety 8.3

**Pairwise:** Q is better. It removes P's throat blots (hopf-torus, hopf-onion) and klein-bottle's black band, and adds two relief forms.

## 2. Targets

| Target | Measured | Result |
|---|---|---|
| ≥ 40 forms, 5 families | 50 forms, 5 families | hit |
| Lines through an opaque surface | none found in the crops | hit |
| Stray fragments / silhouette dashes | many: hopf-tumble core, hopf-links, hopf-onion throat, enneper cusps, catalan centre, mobius twist, wave-field folds, ridgeline-ripple back rows, monkey-slices chin | missed |
| Blots > 15 px | largest about 10–12 px (hopf-meridian lower-left, hopf-nested throat) | hit, just |
| Lines leaving the cell | only hopf-tumble | hit |

## 3. What works

- Relief and slice forms (harmonic-relief, blobs, gyroid-ball, schwarz-cube, knot-slices) read as solid volumes with crisp cuts.
- Grid surfaces (scherk, richmond, seashell, flamm, klein-ghost) are clean, correctly occluded plots.
- Wide range: real differences inside each family.

## 4. Problems, ranked

1. **hopf-tumble and hopf-links: see-through forms drawn as dashes.** Fibres break into 5–30 px dashes at every crossing; hopf-tumble's core becomes hatch noise. Fix: no occlusion test for see-through forms. For crossing gaps, cut only the back strand, a fixed 1 mm, at crossings over 20°.
2. **Short fragments at folds and cusps.** enneper (both cusps), catalan (centre crossing), mobius (lower-right twist), hopf-onion and hopf-nested (throat). Fix: after clipping, drop pieces under 1 mm and merge gaps under 0.5 mm.
3. **wave-field and ridgeline-ripple: silhouette dashes.** Rows passing behind a crest leave 2–6 px dashes (ripple: back rows, front ring). Fix: the same filter, and sample the occluder profile finer so visibility does not flicker.
4. **Flat reads.** harmonic-tesseral, harmonic-pair and sphere-charges look like 2D patterns in a circle; wave-field looks like flat moiré. Fix: tilt 20–30° so contours compress at the limb, or add low relief; lower wave-field's camera.
5. **monkey-slices facets.** Face slices zigzag along low-poly faces; stubs at the chin. Fix: subdivide twice before slicing.

## 5. Checklist

1. 3D read — no: harmonic-tesseral, harmonic-pair, sphere-charges, wave-field flat; hopf-tumble a tangle.
2. Hidden lines correct — no: see-through hopf-links and hopf-tumble lose lines; flamm's radials stop raggedly at the far throat.
3. Clean silhouettes — no: wave-field, ridgeline-ripple and the mobius twist have dashes.
4. Blot — no; hopf-meridian lower-left is close.
5. Smooth lines — no: monkey-slices has facets; henneberg's lower-left rim has a kink.
6. Varied families — yes. Every family has distinct members.
7. Each cell a finished plot — no: hopf-tumble, catalan and wave-field are not.
8. Mathematically wrong — no clear errors found.

## 6. What 8.5 needs

- A minimum-length and gap-merge pass on all visible strokes.
- No occlusion on the see-through Hopf forms.
- Tilt or low relief on the flat cells; subdivide Suzanne.
