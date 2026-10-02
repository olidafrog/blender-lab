# plotter-forms — decisions

Second series of `plotter-blend`: 50 mathematical forms in five families, as Geometry Nodes curves exported as SVG strokes with hidden lines removed. No reference images; the reviewer judged the whole catalogue sheet against written criteria. Final v07: 7.1 in a blind pair against v06 at 6.7; v06 also scored 6.7 against v04 at 6.5 (Opus; target 8.5). Round scores 6.8, 7.0, 7.0, 7.1, 6.8.

## Chosen

- **A form is data.** Three formula strings and a few sliders per form (`scripts/catalog.py`), compiled to Math nodes by `plot_kit.Env`. Four factories cover everything: a parametric surface (parameter lines, edges, contours, dots), a sliced solid (parametric, implicit volume, tube, any mesh object), a field on a sphere (with optional relief), a family of curves.
- **Hidden lines in the exporter, not in nodes.** Each form outputs its triangulated surface with its curves; `plot_svg` tests every stroke sample from the camera's side against a BVH of that mesh. Three switches: `plot_hidden` on the scene or a plot (0, 1, or 2 for a second-pen layer), and the form's `Solid` checkbox.
- **Outline in the exporter** (zero set of normal·view), on for every opaque form except row drawings.
- **Anti-blot cut** after hidden lines, except on row drawings (ridgelines, wave field): there it broke the rows, and the blind pair preferred whole rows with small blots at the crests (7.1 against 6.7).
- **Anti-blot cut** elsewhere (`min_gap`, `gap_angle`, `gap_run`, `gap_remnant`), then stroke ends joined.
- **Hopf fibration as opaque tori**: fibres are the u-lines of one surface per latitude; open arcs nest.
- **Own folder**, not a v2 inside `plotter-blend`: `review_round.py` allows one reviewer brief and one budget per experiment.

## Rejected

- A ray from the point with a fixed bias (fragments), and a 3D distance tolerance (tails past self-intersections).
- Pushing the outline off the surface before its visibility test (doubled rims).
- Free Hopf circles for every variant (ink knots); exact-circle refits (700 points were enough).
- Raising the minimum stroke length to remove fragments (three rounds, no effect: they were remnants of the anti-blot cut).
- Boy's surface (weak formula source, tails to infinity), the figure-8 Klein bottle (creased at its self-crossing), Costa's surface (needs elliptic functions).
- vpype `occult`, exact segment-triangle splitting, Blender Line Art (see `RESEARCH.md`).

## Open

- **Fragments at folds** were the top complaint in every round from v02. Left: lines that end at a self-intersection curve, which nothing draws (Catalan, Henneberg, Kuen). Next mechanism: compute the mesh's self-intersection curves and draw them as outline.
- **Near-blots** at the centres of `hopf-nested` and `hopf-onion` (lines about 0.6 mm apart). `Fibres` per torus, or `plot_min_gap` 0.6 on those plots.
- **Over/under gaps (`weave`)**: one reviewer asked for them, the next read them as dashes. A control: on for `hopf-links` only.
- The see-through set (`output/svg-see-through/`) was exported and not reviewed.
- No fork (the brief says so: a catalogue has no single mechanism). The score was flat (6.8, 7.0, 7.0, 7.1, 6.8) while each blind pair preferred the newer sheet.
