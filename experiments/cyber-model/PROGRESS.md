# cyber-model — progress

## Setup notes (read first)

**Machine:** Mac, Blender 5.2.2 LTS, Cycles on Metal (M4 Max). Docs in `reference/`. Windows (4.4) is not in play for this experiment, but keep bevel/normals code 4.4-safe where it is cheap.

**Process overrides from the user:** research by two Sonnet subagents; reviewer is a **Sonnet** subagent every round (Opus is the lab default, so scores do not compare with other experiments); do **not** write to `knowledge/` or `LEARNINGS.md`. Log surprises in `proposed_learnings.md` in this folder instead and report them at the end.

**One-line process guess (research to confirm):** modelled in a DCC as a stack of separate chamfered plates (boolean-cut pockets + bevel + weighted/harden normals, kitbash greebles), textured with painted-wear masks (Substance-style), lit as a soft studio product shot on a grainy grey backdrop.

**Gotchas that apply, and where each lands in v01**

| Gotcha | Lands in |
|---|---|
| `Standard` view transform for literal colours (`colour.md`). AgX flattens the LCD cyan. | `P["view"] = "Standard"` |
| Flat-shade planar caps; `set_sharp_from_angle` marks everything smooth, so set caps flat after (`cycles.md`). A mirror-material override render shows domes that clay hides. | `finish_part()` helper; mirror-override run before round 1 |
| Bevel width is scene-scale bound: work in metres, device 0.11 × 0.19 m. Bevel wider than 1/3 of the narrowest cap makes n-gon overlap holes (`geometry.md`). | all lengths through `mm()`; `P["bevel_mm"]` |
| Fine bumps stay under 0.2 mm on a 0.4 m object; 1 mm reads as orange peel (`cycles.md`). | micro-bump strength in the plastic group |
| Coplanar faces render black/speckled: lift 0.03 mm (`cycles.md`). | plate stack offsets `P["z_epsilon_mm"]` |
| Small area light radiance is P/(A·π); scale power with size (`cycles.md`). | key/fill built from a size + radiance helper |
| Supersample fine patterns (LCD text, backdrop grain): 2× render then Lanczos (`cycles.md`). | `--scale`, final at 2× |
| f/16 for product shots, focus on an empty at the subject (`cycles.md`). | DOF off by default, `P["dof"]` |
| Silhouette IoU and debug sheet catch gross proportion errors early (`modelling.md`). | `tools/silhouette.py` gate with a hand mask; `tools/debug_views.py` |
| Small key vs big softbox changes how facets read; the reference is a big soft key (`modelling.md`). | `P["key_size_m"]` |

## Versions

Newest first. Updated after every review. Cost is what the version took: Blender runs and minutes since the last row.

| Version | Score | The one change | Cost | Render |
|---|---|---|---|---|
| v10 | 6.4 | Root-cause fix: joined overlapping cutters need `use_self` (no more Exact-empty fallbacks, end-cap slots now cut); base in a dark foot material; wider backdrop contact halo | 4 Blender runs, ~15 min | `renders/v10.png` |
| v09 | 6.7 | Black liner slab under the lower plates; calmer satin pods with clamps; framed vent window | 6 Blender runs, ~25 min (moat 4 mm went empty; back to 3 mm) | `renders/v09.png` |
| v08 | 6.5 | Black cutter material via Boolean TRANSFER; wall lift; ribbed satin pods; backdrop grain rebuilt (albedo-only, two scales) | 8 Blender runs, ~30 min (three grain iterations) | `renders/v08.png` |
| v07 | 6.6 | Mechanism change for edges and gaps: flat unhardened 1-segment chamfer with flat shading, smaller corner radii, 3 mm moat cut around the shield foot, device key lowered | 6 Blender runs, ~25 min (one shading artefact fixed by flat shading) | `renders/v07.png` |
| v06 | 6.5 | Blacks and texture: AO on the backdrop (contact halo) and cubed AO on polymer, fine polymer grain, bevel 0.35 mm, steps 1.4x, drums 0.8x, LCD sheen | 5 Blender runs, ~20 min | `renders/v06.png` |
| v05 | 6.0 | Base slab polymer (was void black); 0.7 mm gaps; shield undercut; sunk screws; wing vents; jack/tab grounded; longer drums; LCD glass invisible to diffuse rays; cut() retries solvers | 10 Blender runs, ~35 min; two empty-boolean debugging detours | `renders/v05.png` |
| v04 | 5.9 | Relight: device-only key on the camera side, old key linked to the backdrop only, metal-only reflection card, dark satin albedo; scratch mask | 9 Blender runs, ~30 min (advisor consult, mirror-vs-albedo test, light sweeps) | `renders/v04.png` |
| v03 | 6.0 | Mechanism change for massing: shield as a 12 mm block over a 5 mm battery block; device-linked fill; AO into polymer; LB groove cut | 14 Blender runs, ~45 min (fill sweeps, coplanar fix) | `renders/v03.png` |
| v02 | 5.8 | Body 13 mm slab with 4–8 mm steps (was a 6 mm tray); low camera-side fill; boss, plug lead and clipped digit fixed | 12 Blender runs, ~40 min (incl. camera fit and light sweeps) | `renders/v02.png` |
| v01 | 5.9 | First full build: layered plates (weighted bevel + edge material), grooves, LCD, antenna, dial, cord, decals-ready | Research ~35 min (2 Sonnet agents in parallel, ~13 min each) + Opus advisor plan review; 22 Blender runs ~35 min incl. camera fit | `renders/v01.png` |

## Log

- **Round 1 review (Sonnet, 5.9):** top problem "thin tray" (walls too short, no camera-side fill). Measured on the reference: a wall is about 13 mm; v01 had 6 mm. Fixed in v02: base 13 mm, steps 4–8 mm, low camera-side fill. Also fixed the loose parts (boss with no body under it, plug with no lead, clipped "7"). Deferred to next round: scratches, steel brushing, bracket albedo, drum size.
- **Advisor (Opus), plan stage:** changed the plan in five places: weighted bevel by edge class (soft top rim, small vertical break, no foot bevel), chamfers into a second material slot instead of a shader Bevel node, ribbon/ring grooves parallel to step outlines, gunmetal pods, a measured-table + yes/no reviewer brief. See `RESEARCH.md`.
- **Reviewer-brief deviation:** rounds ≥ 2 add a blind pairwise question (previous best vs current, random order) and a script-measured table, both from the advisor. The reviewer is Sonnet on purpose (user's request).
- **Known open:** `ring_wing` and `ring_lb` grooves are empty (offset outline self-intersects); a bmesh-inset replacement failed on all five rings and was reverted.

- **Round 2 review (Sonnet, 5.8):** blind pair said v02 closer than v01, score flat inside ±0.4. Same top problem again (massing / walls too dark), so the mechanism changed in v03 instead of a third height tweak: shield as a 12 mm block overhanging a lower (5 mm) battery block; fill light **light-linked to the device** so walls lift without lifting the backdrop; ambient occlusion into polymer base colour and specular for real blacks; frame/LB coplanar z-fight fixed (found by eye: LB top turned silver).
- **Advisor vs reviewer disagreement:** the Opus advisor read camera-facing walls as 115–140 (lighter than tops); the Sonnet reviewer read the right-hand walls as dark as the tops. I measured a wall on the reference at about 13 mm tall and kept walls dark-to-mid with a linked fill, not a bright one.

- **Round 3 review (Sonnet, 6.0):** blind pair prefers v03 (structure) but calls the plates about 50 levels too light; gaps grey; edges pillow-round; no scratches; blank plates. Scores 5.9 / 5.8 / 6.0: plateau, so the Opus advisor was consulted again at the 3-review mark (mechanism only, no scores given).
- Reviewer contradiction noted: the script table says the subject is too dark (median 59 vs 75) while the reviewer's own patch samples say the plates are too light. Both true: the exposed black chassis drags the median down while the plates sit around 130–155. The tone problem is the plates, not the table.

- **Advisor consult at the 3-review mark (Opus):** found the cause of the light-tone problem: the far-side key mirrored in every flat top (a render with albedo 0 still gave 116–137). Fix in v04. Advisor also listed: no real gaps (`gap_mm` unused), soft AO ramps instead of hard black feet, edges read as beads, blank faces. v05 applies those (one-segment-ish chamfer 0.55 mm, undercut under the shield, 0.7 mm gaps, sunk screws, no perimeter grooves on shield/top module).
- **Round 4 review (Sonnet, 5.9):** blind pair prefers v04 over v03 (tone right, shadows deeper). Top problem repeated: base slab reads as a flat black tray with no shoulder or crease. Fixed in v05 by making the base polymer (was void black), bevelled, plus jack/block grounding, longer drums, no LCD spill (glass invisible to diffuse rays), mottled roughness.
- **Score plateau, pairwise progress:** absolute scores 5.9 / 5.8 / 6.0 / 5.9 while the blind pair picks the newer render every round. The absolute number looks anchored near 6 for this reviewer; the pairwise question is the more sensitive instrument here.

- **Round 5 review (Sonnet, 6.0):** pair prefers v05. Top: blacks missing (p5 32 vs 7), edges pillowy and steps shallow, drums oversized and touching the bezel. I mapped where the reference's near-blacks are: mostly a contact-shadow halo on the backdrop around the whole device plus gaps and recesses; a red-overlay comparison is in the scratchpad, not the repo. v06: AO on the backdrop (12 mm, power 2.5), AO power 3 on polymer, fine albedo grain (the reference plates carry std 13–26; the reviewer measured 1.5 on ours), bevel 0.35 mm, steps 1.4x, drums 0.8x with one collar, LCD sheen.
- **Reviewer's numbers vs script:** grain std passes the ±12 rule at 10.1 vs 15.4 yet the reviewer calls it 34 % low; a percentage tolerance would have flagged it. The metrics table needs ratio tolerances for small-valued rows (grain, share under 12).

- **Round 6 review (Sonnet, 6.5, first real step):** blacks, pillowy edges and walls-vs-tops repeated for the third or fourth time, so v07 changes mechanism rather than values: plates get a flat, unhardened 45° chamfer (1 segment, flat shading, fine corner arcs, smaller corner radii) and a 3 mm moat cut around the shield foot in the neighbouring plates; device key lowered to catch walls. A dark triangle artefact from unhardened smooth normals after a Manifold boolean showed up first; flat shading removed it by construction.
- **Slope rule (from round 6):** best of rounds 4–6 (6.5) beats best of rounds 1–3 (6.0) by 0.5, so the loop continues.

- **Round 7 review (Sonnet, 6.6):** pair prefers v07 (hard chamfer highlights and open moats read as stacked solids). Top: blacks still grey, walls not lifting, antenna pods the weakest part. v08: black material carried into cutter walls (Boolean `material_mode=TRANSFER`: moat, screw holes, vents), wall-lift term in the polymer shader, ribbed satin-metal pods, chamfer 0.65 mm, backdrop grain rebuilt as albedo-only two-scale speckle (worm pattern came from the bump).
- **Slope rule:** rounds 5–7 best 6.6 vs rounds 2–4 best 6.0, +0.6: continue.

- **Round 8 review (Sonnet, 6.5):** flat vs v07 inside noise; pair picked the newer render. Top: blacks still grey, pods too bright and banded (4 washers), the black vent rectangle read as a hole.
- **Round 9 review (Sonnet, 6.7, best so far):** blacks still grey by the metrics, lower-right block flat, vent frame an empty outline. Root cause of the empty vent found after the review: overlapping cutters joined into one operand cancel in Exact (fixed with `use_self`), which was also behind the earlier "Exact returns empty" fallbacks.
- **Slope check at round 9:** rounds 7–9 best 6.7 vs rounds 4–6 best 6.5, +0.2 (< 0.3): the slope rule would stop the loop here. The 10-round budget ends it in any case after round 10.

- **Round 10 review (Sonnet, 6.4):** budget spent. Pair says v10 slightly closer than v09 (vents and screw), absolute score down 0.3 (inside noise). Top: camera-facing walls darker than tops and body reads as a thin tray (the near-black foot I added in v10), creases grey, flat polymer.

## Calibration

Blind A/B, one fresh Sonnet reviewer, same brief, random order (A = v09, B = v10; the render paths in the request carried the version numbers, so it was not fully blind):

| | Score | Sub-scores (form / parts / materials / light / technical) | Top problem |
|---|---|---|---|
| A = v09 | 6.7 | 6.5 / 7.0 / 6.5 / 6.5 / 7.0 | Blacks lifted (p5 19 vs 7): creases read dark grey |
| B = v10 | 6.5 | 6.0 / 7.5 / 6.0 / 6.0 / 7.5 | Base shell and camera-facing walls crushed to near-black; walls darker than tops |

Closer to the reference: **A (v09)**. The final (v10) did not beat the best earlier version, so the hand-off ships **v09's configuration**, reproduced exactly (`chk09.png` against `v09.png`: MAE 0.00, 0.00 % changed). The one v10 change the calibration liked (vent slots and the screw, from `cut_self`) is a flag, `--set cut_self=True`, not reviewed together with the poly foot. Score trend across ten rounds: 5.9, 5.8, 6.0, 5.9, 6.0, 6.5, 6.6, 6.5, 6.7, 6.4; target 8.5 not reached.
