# wax-seal-chaos — progress

## Setup (2026-09-29)

Mac, Blender 5.2, Metal. Fork of `wax-seal` (final 6.4, best 6.6).

Chaos pool (seed 2761081326 picked the **bold** ones):
- Geometry: SDF sculpt + die subtract · **Fluid pour (Mantaflow, stamp as obstacle)** · baked height map + adaptive displacement · library heightfield
- Material: layered pigment + chalk mottle · volume interior under a clear skin · cavity-driven albedo · **matte-wax BRDF (Sheen, no coat)**
- Light: window HDRI · physical window + curtain · key + bounce card · **sun 3° + white bounce**
- Process: numeric optimiser · camera emulation · **side-by-side composite reviews** · 2× render + rim crops

Reroll (2026-09-29): the fluid draw was infeasible after 5 bakes (pancake at real gravity, crown splash at low gravity, unstable explosion when pressed slowly). The same seed stream rerolled geometry to **SDF sculpt + die subtract**. `scripts/sim.py` is kept as the record.

Carried from wax-seal (lands in v01):
- Scatter ≤ 0.08 mm with violet reach (1, 0.5, 1.2); scatter 0 isolation render before round 1 (`shader-nodes.md`).
- Region targets and the shadow-edge profile (hard ~10 px edge, core 45–55 L at row 900) decide light size (`matching-a-reference.md`). P: sun angle.
- Khronos PBR Neutral; paper at ~220 sRGB. P: `view`, `exposure`.
- Emblem via `library/node-groups/build_wax_seal.py` `emblem_field` (any curve/text/mesh, Bounding Box Use Radius off).
- Closed mesh for random-walk SSS; the sim mesh must be watertight.


Newest first. Updated after every review. Cost is what the version took: Blender runs and minutes since the last row.

| Version | Score | The one change | Cost | Render |
|---|---|---|---|---|
| v06 | 6.2 | Sun 38°→24° (the outer wall turns away; row-700 profile vs ref), exposure +1.0; pour tucked under the bead; frame 35.5 mm. A black flag was tried: it darkened the paper, not the wall | 6 runs (sweep), ~12 min | renders/v06.png |
| v05 | 6.2 | Bead cross-section: smaller, lower bead (r 1.6, crest ~1 mm above field), steep outer wall; pour at full height (SDF Offset fell short) so the die cuts a true field; sun az 30 | 9 runs, ~25 min | renders/v05.png |
| v04 | 6.4 | Light: bounce card off (it lit the shadow-side rim), warm world fill 0.08 from above, sun 38°; shadow core 67,55,48 (ref 77,62,55) | 5 runs, ~8 min | renders/v04.png |
| v03 | 6.3 | Material: patchy roughness (0.45 ± 0.25, glints), flow lines cut in, micro bump 0.4, less saturated colour | 1 run, ~4 min | renders/v03.png |
| v02 | 6.0 | Relax (mesh position blur, 6) removes voxel terraces; wobble 0.09, pool 0.8, pour radius 16.2 so the bead covers it | 4 runs, ~10 min | renders/v02.png |
| v01 | 5.4 | Reroll build: SDF sculpt (pour slab ∪ bead tube − die − floor, fillet, smooth), emblem on the die face, matte Sheen wax, sun 3° + bounce card | ~12 bakes (Mantaflow, abandoned) + ~12 SDF runs, ~3 h | renders/v01.png |

Instrument control: the original `wax-seal` final scores **5.8** with this side-by-side reviewer (6.4 blind), so the bar to beat here is 5.8. v02 (6.0) beats it.

## Stopped after round 6 (slope rule)

Scores 5.4, 6.0, 6.3, 6.4, 6.2, 6.2. The best of the last 3 (6.4) beat the 3 before (6.3) by 0.1. Asks flipped on key height (v04 "lower", v06 "35–40°").

## Calibration

Blind A/B/C (labels shuffled by seed; key in reviews/calibration_key.txt): **v06 6.6** > v04 6.2 > original wax-seal final 5.4. Finish from v06.
