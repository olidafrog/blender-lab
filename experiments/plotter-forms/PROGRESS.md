# plotter-forms — progress

Machine: Mac, Blender 5.2.2. 5.x only (For Each zone, `evaluated_geometry()`). Builder Fable 5.1, reviewer Opus, advisor Opus. Research: two Sonnet agents (hidden-line methods with a BVH speed test; formulas with numeric checks).

Second series of `plotter-blend`, in its own folder so the reviewer brief and budget are separate. No reference images: the reviewer judges the catalogue against the brief and written criteria.

Process guess: every form is contour lines of a formula on a surface, the parameter lines of a formula surface, or a family of formula curves; the exporter hides lines behind the surface by one ray per stroke sample.

The "render" is a raster of the exported SVGs as a contact sheet (Inkscape). The preflight sheet is the plot check (stroke order, pen-up moves), as in `plotter-blend`.

Knowledge that lands in v01:
- No contour node → `plot_kit.isolines` (moved from `plotter-blend/forms.py` to `library/node-groups/plot_kit.py`).
- Cut on the mesh, not on curves → hidden lines are cut in the exporter, in world space, before projection.
- Assert something countable after every silent step → strokes > 0 and nothing off the page, per form.
- Dedupe wrecks a wireframe at 0.6 mm → `min_gap` 0.05 for every form; cusp and end dots off.
- zsh loops drop `--set` → tests through `--only` and single runs.
- Fine lines need pixels → sheets at 5 px/mm (pen 0.35 mm).

## Advisor (Opus), before round 1

It read the first full build and ran three test builds. Taken:
1. The fixed ray bias fragments strokes (dini 50 → 124 strokes, 30 % under 2 mm) → visibility is now tested from the camera's side: a point is seen when the first hit is the surface at the point itself, within 0.75 of its triangle's longest edge (`_visible`). Depth along the ray is ill-conditioned where the surface is edge-on; distance on the surface is not.
2. The outline was pushed off the surface and switched off for non-orientable forms → it is drawn on the mesh, with corner normals flipped to each face's side, so Klein and Möbius get outlines; on for every opaque form.
3. Unwelded seams left gaps in the torus outline → the exporter welds the occluder by position.
4. Blots at poles → `Pole Trim` ends every 2nd, 4th and 8th spoke early (Enneper, monkey saddle, Flamm). Its general ink-density pass in the exporter was not built: cutting Hopf circles mid-way reads as broken lines (series 1 reviewers called such ends "bare").
5. Hopf circles near infinity were chords → 700 points on `hopf-tumble` (not its exact-circle refit).
Also: `sphere-spiral` contoured the wrong field (now `sin(arms·lon + turns·lat)` at level 0 with a pole cap); dipole camera turned off the edge-on plane; Henneberg's inner edge (a segment drawn four times) dropped; Boy's surface dropped (weak formula source, tails to infinity).
Own addition: `graze` cuts sphere contours where the surface is nearly edge-on, so they do not pile up at the limb.

Newest first. Updated after every review. Cost is what the version took: Blender runs and minutes since the last row.

| Version | Score | The one change | Cost | Render |
|---|---|---|---|---|
| v07 | final (see Calibration) | Row forms keep their outline and skip the crowding cut: unbroken ridgelines again | 2 runs, ~10 min | renders/v07.png |
| v06 | 6.7 (calibration pair) | Row forms (ridgelines, wave field) drawn without the outline: beside it the crowding cut left rings of dashes | 1 run, ~5 min | renders/v06.png |
| v05 | 6.8 | Remnants of the crowding cut removed (pieces under 5 mm between two cuts), stroke ends joined, low relief on three flat spheres, monkey rebuilt from its distance field, weave off on the dense Hopf forms | 3 runs, ~30 min incl. the advisor | renders/v05.png |
| v04 | 7.1 | Ink-crowding cut in the exporter (lines closer than the pen, running the same way, are cut); over/under gaps at crossings on the see-through Hopf forms; two lobed harmonic forms | 4 runs, ~35 min | renders/v04.png |
| v03 | 7.0 | Visibility by mesh adjacency (no tails past a self-crossing), outline specks dropped, sphere contours relaxed, Möbius turned to show its twist; klein-eight dropped | 3 runs, ~15 min | renders/v03.png |
| v02 | 7.0 | Hopf family rebuilt as opaque tori (fibres are the u-lines of a surface; open tori nest) so circles no longer meet in ink knots; stubs under 1.5 mm dropped; monkey smoothed; two spheres drawn to the limb | 5 runs, ~25 min | renders/v02.png |
| v01 | 6.8 | First build: 48 forms in 5 families from formula strings; exporter hides lines by a camera-side ray test, draws outlines, clips to the page | ~22 runs, ~150 min incl. research and the advisor | renders/v01.png |

## Stall guard, after v03

"Blots where lines converge" ran three reviews, and the fragments and blot targets missed three rounds. The mechanism changed for v04, as the advisor had proposed before round 1 (its item 4, not built then) and the v03 reviewer asked again: an ink-crowding cut in the exporter (`min_gap` 0.28 mm with `gap_angle` 25° and `gap_run` 1.8 mm: a line running beside an earlier one closer than the pen is cut there; outlines and long strokes win). Research for the effect is in `RESEARCH.md` (minimum-separation checks in plotter flow fields; knot-diagram gaps). Also new in v04: `weave` breaks the far line at each crossing of a see-through plot, and `Relief` turns a harmonic sphere into lobes.

## Stall guard, after v04

"Short strokes at folds and cusps" ran three reviews (v02–v04) through three value changes (minimum run 1.2 mm, minimum stroke 1.5 → 2 → 3 mm). Advisor consulted before round 5 (below). The `weave` gaps are a trade-off: the v03 reviewer asked for over/under breaks, the v04 reviewer read them as dashes. Kept as the `plot_weave` control: on for `hopf-links` (1.0 mm), off for the dense `hopf-tumble` and `hopf-meridian`.

## Calibration

Blind pair, one fresh Opus reviewer: **v06 6.7, v04 6.5** (the best round score was v04's 7.1, so rounds ran about 0.4 generous). 42 of 50 cells were identical; the eight that differ decided it. For v06: lobed and relief harmonics, clean monkey, 2 isolated short strokes against 25. Against v06: the pulsar ridgeline was broken (lines ending in mid-air) by the crowding cut; v04's was continuous.

That one defect was fixed as v07 (row forms skip the crowding cut and keep the outline), and v07 went through a second blind pair against v06: **v07 7.1, v06 6.7** (46 cells identical; the four row forms decided it: v07's ridgelines are continuous, with blots of about 7 mm where rows bunch at a crest in `wave-field` and `ridgeline-range`). v06 scored 6.7 in both pairs, so the instrument repeats. Finished from v07.

No fork (see Budget in `BRIEF.md`).

## Report

- Trend: 6.8, 7.0, 7.0, 7.1, 6.8 by round; 7.1 calibrated for the final (v07). Variety scored 8.0–8.3 every round; plot readiness (5.8–6.5) and hidden lines (6.0–7.0) hold the score down.
- Repeated complaints: short strokes and dashes where a surface folds or meets itself (every round from v02); near-blots at the centres of the nested Hopf tori; sphere patterns reading flat.
- About 30 of the 50 cells were called finished plots by the round-5 reviewer.
- Trade-off found by the two pairs: on row drawings the crowding cut removes blots and breaks the rows; without it the rows are whole and bunch at crests. It is `plot_min_gap` on those four plots (0.05 now; 0.28 cuts).
- Next mechanisms: draw self-intersection curves as strokes (lines now end in mid-air there); per-row envelope occlusion for ridgelines; a per-family reviewer sheet, since a 50-cell catalogue surfaces five new weakest cells each round.
