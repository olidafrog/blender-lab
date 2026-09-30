# roman-model — progress

**Machine:** Mac, Blender 5.2.2, Cycles on Metal (M4 Max). 5.x only (bmesh/modifier API as dumped for 5.2).

**Process guess:** AI-generated "printable low-poly figurine" image. Rebuild as FK-posed bmesh lofts (body, decimated) plus hand-built low-poly armour parts, one sand clay material, big soft key, warm cyc.

**Knowledge that lands in v01:**
- Colour: AgX shifts saturated colours → `view_transform` "Standard" in `P` (clay look must match sRGB values directly; legion crimson stays crimson). (`gotchas/colour.md`)
- Subject resting on the floor: lift boots 0.03 mm off the cyc to avoid coplanar black speckle. (`gotchas/cycles.md`)
- A white/bright backdrop above 1.0 clips the contact shadow ("floats") → measure the cyc value near the feet and keep it ≈ reference (≈ 205–214 luma). (`gotchas/cycles.md`)
- `--factory-startup` resets the GPU → `enable_gpu()` after the factory reset (template does it). (`gotchas/headless.md`)
- Select/measure by evaluated vertex bounds, not `location` (transform_apply trap) → part-size table measures `to_mesh()` verts. (`gotchas/geometry.md`)
- Flat shading: faces `smooth=False`; do not call `set_sharp_from_angle` (sets every face smooth). (`gotchas/cycles.md`)
- zsh drops `--set` in loops → A/B tests through `tools/sweep.sh`. (`new-experiment`)
- Reviewers misread render bugs → correctness pass (clay override, normals check, debug sheet) before round 1. (`review-render`)

**Review plan (advisor):** round 0 silhouette IoU gate without Opus; rounds 1–6 clay structure; legion colour look from ≈ round 7, judged separately.

Newest first. Updated after every review. Cost is what the version took: Blender runs and minutes since the last row.

| Version | Score | The one change | Cost | Render |
|---|---|---|---|---|
| v09 | 6.5 | Whole upper body raised (hip 2.26 H), wider shoulders, pads as larger shells, shield in/up, head back, crest lower. IoU 0.84 (best) | 5 runs, ~20 min | renders/v09.png |
| v08 | 6.8 | Trapezius slope + neck (helmet up), closed flatter pads, left leg in, belt up, box fist, longer guard, thicker strap, camera re-framed | 8 runs, ~30 min | renders/v08.png |
| v07 | 6.7 | Boots lower/slimmer (cuff 1.05 H), leg no longer pokes through, left knee in, shield fist lower, strap starts below shoulder, helmet jaw pinched | 3 runs, ~15 min | renders/v07.png |
| v06 | 6.6 | Wider torso (waist 0.70 H), elbow tucked in with wide fist (pole change), shield rolled −12° and taller, crest as a long Bezier crescent, clean prism boots, wider strap. IoU 0.80 | 16 runs, ~40 min | renders/v06.png |
| v05 | 6.4 | Head raised 0.2 H (neck shows), pads lowered, crest cantilevered back, helmet dome lower + jittered facets | 5 runs, ~20 min | renders/v05.png |
| v04 | 6.3 | Mechanism change (Fable): body as low-count planar rings + jitter + triangulate (no subdiv/decimate); ray-cast strap/belt; skirt as flat plates; single-cap pads; smaller key, more fill | 12 runs, ~45 min | renders/v04.png |
| v03 | 6.2 | Boots rebuilt (tapered faceted shaft, slim cuff, flat-soled foot), splayed left foot pulled in, sword arm out, crest lengthened, pads to torso top | 9 runs, ~30 min | renders/v03.png |
| v02 | 5.7 | Corinthian helmet rebuilt (flat face plate, T cut, nose wedge, crest on holder) + landmark fixes (belt lower, skirt tucked and pleated, flat strap, wider hips) | 12 runs, ~35 min | renders/v02.png |
| v01 | 5.3 | First full blockout: IK-posed lofts + decimate, hand-built armour, clay look matched to reference tones | 28 Blender runs, ~95 min incl. research | renders/v01.png |

## Calibration

Loop stopped after v09 on the slope rule (best of v07–v09 = 6.8 vs v04–v06 = 6.6, +0.2 < 0.3). One review round of budget left unused.

Blind A/B (`reviews/calibration.md`, key in `calibration_key.txt`): **v09 6.4 vs v08 5.8** — v09 wins (real pads, shield placed, IoU 0.84 vs 0.80). Finish from v09.

Shared open items (both reviewers): torso faces the camera more than the reference (≈20° more turn wanted), torso reads boxy without enough V-taper, skirt flares into a bell while legs read thin (a trade-off: fix with a hem that drapes over the thighs), helmet a flat-fronted bucket rather than a rounded Corinthian dome.
