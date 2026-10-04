# apartment-model — progress

## Setup (2026-10-03)

Mac, Blender 5.2, Metal. Builder Opus 5.5 (this session's model); reviewer Opus.

Applies to v01, and where it lands:
- **Measure, don't eyeball.** The Polycam scan is ground truth for plan and heights: every wall, opening and level in `P` comes from the scan, cross-checked with the user's tape and the 1:60 plan. Scan heights (floor = 0): ceiling 4.09, under-mezzanine soffit 1.94, mezzanine girder underside 3.69. User: 4.05 / 1.91 / 3.55.
- **Fit cameras from landmarks** (`matching-a-reference`): each review view gets a camera fitted to its photo from scan landmarks, with the focal length from EXIF (14 mm or 24 mm equiv; 4:3 frame → sensor width 34.6 mm). Hand-guessed cameras missed by 1.6× in `cyber-model`.
- **Separate colour from grade**: white walls and the brick at true albedo; photo white balance goes in `wb_temp`/`wb_tint`.
- **Exterior light physics** (`cycles.md`, aztechno): one Sun lamp in W/m², multiple-scattering sky, indirect clamp 0, exposure via `film_exposure`. Windows face 142° (SE), London 51.53° N; sun from the date/time of the photos (EXIF).
- **Assert something countable** after each risky geometry step (boolean window cuts): print face counts and bounds.
- **Debug sheet** (ortho plan + section + views, random colour per object) before the first review; preflight sheet before round 1.
- **Window glass**: what it reflects matters more than its physics; the view outside is a backplate/HDRI, not modelled context, for now.
- Scan files are large (OBJ 55 MB, GLB 17 MB): keep them out of git.

**Process guess:** a 1909 RC-framed brick factory with a 1988 mezzanine insertion; the model is clean extrusions placed from scan plane fits (±2–5 cm), the plan for unscanned rooms, photos for detail.

**Advisor (Fable, plan stage):** the diagonal "haunches" are splayed heads of RC pilasters on the side walls; model the frame (pilasters, edge beams, girder, central beam). Model the open casements at the photo angles. Edge correlation is a drift measure, not a gate; edges from a Workbench id pass, judged on the upper band. Lift the sky for lighting but show it dimmer to the camera so glazing bars survive. → All applied in v01: pilasters measured in the scan (x 0.85–1.29, 0.20 / 0.12 proud), hinged sashes with `sash_deg`, `sky_camera` 0.3, id-pass overlay in the review sheet.

**Review instrument:** `renders/vNN.png` is a sheet built by `scripts/review_sheet.py`: per photo a row of photo | render | photo with model edges in red. Cameras: `assets/cams/<n>.json`, fitted by `scripts/fit_cam.py` (landmarks) and `scripts/refine_cam.py` (edge match against the textured scan).

## Round two: materials (from v13)

User: "Fix the brick and floor materials". New reviewer brief (`reviews/REVIEWER_PROMPT.md`; the shell brief is `REVIEWER_PROMPT_shell.md`), so scores restart at v13 and compare only within this round. Budget 8 rounds. Instrument: `review_sheet.py <v> mat` (photo | render | 1:1 photo and render crops of brick and floor, rows 2, 5, 1, 8, renders at 2048 px) and `scripts/mat_measure.py` (brick and floor luma relative to the white paint in the same regions of photo and render).

Measured from the photos (rectified onto the model planes with the fitted cameras, `scripts/rectify.py`): herringbone spine along the room in the living room and kitchen; tip lines 0.50 m apart, seam pitch 0.19 m along the spine → 700 × 140 mm planks; brick courses 85–95 mm; brick/paint luma 0.21–0.25, floor/paint 0.89–0.99 (v12: 0.30 and 0.78–0.84). Research: two Sonnet agents (brick, herringbone), both verified their node math in 5.2.

**Process guess:** old cleaned brick lit only by room bounce; a 700 × 140 engineered-oak or LVT herringbone with a satin finish.

Pre-review tests (t13): brick and floor as shader-math groups in `scripts/mat_kit.py`. Brick/paint 1.02–1.07 of the photo ratio; floor/paint 0.82–0.97 of it; texture std brick 5.4–6.5 (photo 3–8), floor 5.8–6.8 (photo 8–13).

Advisor (Fable) on the plan, after t13: (1) the floor's brightness near the windows is window and wall reflection on a satin finish, not albedo → roughness 0.3 with per-plank spread, anisotropy 0.5 along each plank (tangent from the plank orientation); (2) brick: the tone spread between bricks is the pattern, the joints nearly vanish → categorical burnt/common/pale bricks, per-brick gradient, low-frequency smear, mortar near the brick tone, soft-edged and missing in stretches, faint relief, a few mm of warp; (3) grain read as pinstripes → sparse thin latewood faded over plain stretches, bigger taper for arches; (4) match the phone's white balance on the paint before judging hue. → All applied in v13; white balance 13000 K gives paint R/B 1.22 (photo 1.24). AgX desaturated the floor (Khronos PBR Neutral oversaturated the brick), so the view transform stays AgX.

Stall guard after v13 (slope flat v11–v13, "floor appearance" three reviews): v11–v12 were scored on the shell brief; round two restarted the instrument at v13, so the slope and repeat rules count from v13 only. Not acted on.

Stall guard after v14 (floor grain two rounds: "faint lines" v13, "zebrano, not oak" v14): mechanism change for the grain, procedural ring model → a scanned CC0 oak texture sampled in each plank's local coordinates with a random offset and flip per plank (the herringbone math, seams and sheen stay).

Stall guard after v15 ("brick reads as tile" v13–v15): v16 was already rendered as a value round (plum-maroon albedo, bloom across the joints, stronger mottling); the advisor is consulted on a brick mechanism change for v17. The "floor/paint missed" flag is stale (v15 hit 0.90 and 0.95).

Advisor (Fable) after v16, brick mechanism: a whole-wall CC0 scan (Poly Haven factory_brick) at true scale for structure, regraded through its height mask (faces and joints coloured separately from the measured values; one gain on the whole scan turns the mortar violet). Per-brick sampling of a scan would leave ghost joints; a detail layer keeps the straight grid. → v17 brick. Floor in v17: rustic oak scan (oak_wood_planks), each plank inside one randomly chosen source plank (v16: the clean veneer read as fresh-cut).

Stall guard after v17 ("floor too uniform and pale" v15–v17): the floor mechanism changed twice in those rounds (procedural → veneer scan v15 → rustic scan v17); v18 is a scale and contrast round on the same mechanism: planks 700 x 140 → 600 x 120 (photo 8 and two reviewers read them ~20 % smaller than photo 2's rectification), grain contrast 1.4 → 2.0, plank spread 0.4 → 0.6, roughness 0.22 → 0.3.

Stopped after v18 (slope flat: best of v16–v18 6.2 vs v13–v15 6.1). Calibration (round two, `reviews/calibration.md`; round one's is `calibration_shell.md`): v18 5.9 beat v17 5.7 blind (more plank variation and grain contrast; v17's planks evener and glossier). The winner is 2.6 under the target, but the experiment forked once already (v08), so no second fork: finish from v18.

## Round three: the sofa (from v19)

User: "okay let's model the sofa ... it's a swyft model 03 in pumice"; mid-round: "search online ... find loads of pictures and dimensions of the actual sofa because it's still on sale". New reviewer brief (`reviews/REVIEWER_PROMPT.md`; round two's is `REVIEWER_PROMPT_materials.md`), so scores restart at v19. Budget 8 rounds (total 32). Instrument: `review_sheet.py <v> sofa` (rows 1, 2, 3: photo | render | 1:1 photo and render crops of the sofa | model edges over the photo crops for rows 1 and 2) and `mat_measure.py <v> --sofa` (fabric luma / paint luma in photos 1 and 2).

Research: two Sonnet agents (Swyft product pages: sizes, construction, the Pumice fabric, 9 product photos; upholstery technique in Blender, tested headless), then a third for more product photos and drawings. Sizes from Swyft; placement from the scan (arm end x −0.87, seams −1.79 / −2.49, seat front y −1.70) and, for the ottoman, 8 corner pixels in photos 1 and 2 (centre −3.03, −1.33; 11 px rms). Camera 3 misses the radiator by ~100 px in the sofa's corner: no placement from it.

**Process guess:** a factory-made modular box sofa (arm | 3 seats | arm, back blocks on the seats, 1 cm self-fabric flanges) in a matte slub linen-look weave, under the room's overcast window light.

Advisor (Fable) on the plan, before v19's review: (1) the block shape reads CG: the real seats belly down and roll over their fronts, the back blocks are pillows, the seams bow; use a pillow profile (exponent ~1.8), a sag per seat and a low-frequency deformation of the whole block, applied to the flanges too; cloth only if that fails. (2) The flange must follow the deformed block and have a rounded section. (3) Puckers as bump are fine. (4) The fabric mechanism is sound; at room distance colour and sheen read, not the weave. (5) Feet are hidden by the rug. → Built as `slump_field` in `upholstery.py` and a bevelled flange; held for v21 (one change per round; v19's review ranks the fabric first).

Sheen sweep after v19 (`sheen`, 4 variants): Sheen 0.5 → 1.0, roughness 0.3–0.7 move every fabric/paint ratio by ≤ 0.03. The photo's stronger top-vs-front contrast is the room's light (dark leather chairs, plants and units against the render's grey blocks), not a fabric value.

Stall guard after v19 (slope flat, "texture uniformity" three reviews v17–v19, form called wrong): v17–v18 were round two's brief; round three restarted the instrument at v19, so the slope and repeat rules count from v19. The form complaint: the advisor was consulted (above); its mechanism is v21.

Stall guard after v20 (slope v15–v20, "fabric" v18–v20): spans rounds two and three again; not acted on (the rules count from v19). v21 acts on v20's top problem (hard boxes) with the advisor's mechanism.

Stall guard after v21 ("seat tops, arm inner face" missed v19–v21; "flat form" three reviews): v21 was the form mechanism change; the advisor is consulted on the missed levels (fill light) before v22. Slope rule: round three has three rounds, not six.

Third agent (more product material): Swyft's dimension drawings and 2020 spec sheet. The back block is a wedge (21 → 11 cm), the seat front seam 39 with a 45 crown, the arm 80 deep, feet 7 × 4 cm. Queued for v23 as P values (v22 is the advisor's fill change).

Advisor (Fable) after v21, on the missed fabric levels: (1) a measurement bug: photo 2's seat_front box was half on the 0.48 m coffee-table stand-in; clean, the render's front/top was 0.80 against the photo's 0.52 (box now y 1380–1415). (2) Direct-only and bounce tests: no room albedo, sky shape, sun patch or AgX look fixes the front without breaking the rug; darker per-piece stand-ins fix the ceiling level but make the sofa front worse. (3) The front is geometry: on the real sofa the seat top overhangs the front, which rolls under toward the shadow gap. (4) Photo 2 has a per-photo white balance offset (every neutral renders R−B +28–34 vs +21–25). → v22: fronts tucked under the overhang (`slump_field` tuck), with the drawing values bundled as one shape change; stand-in albedos and per-photo white balance left as open items.

Stall guard after v22 ("fabric hue and texture" v20–v22, inside round three): mechanism change for the fabric's look at 1:1. (1) The weave now comes from the real fabric: a high-passed, seamless patch of Swyft's Pumice close-up (`assets/mat/pumice_weave.png`, ~5 px period → 11 cm tile); the scanned linen's tone is off. (2) The photographic output stage (`--scale 2 --finish`: Lanczos, unsharp 1 px 80 %, JPEG q85; `tools/photo_finish.py`), gated by `tools/sharpness.py`: the raw render had 0.34 of photo 2's fine detail and edge ratio 1.15 vs 1.36; finished 1.41, fine detail 0.56 (the rest is content the stand-ins lack: rug pile, objects). Values: short 4.5 mm slubs at 0.3, albedo cooled to (0.405, 0.425, 0.465) so the warm grade lands greige. Learned on the way: the 1 mm weave and 3 mm slubs are sub-pixel at 3–4 m and vanish whatever their gain. Back blocks back to near upright (0.21 at the top).

Trade-off after v23 (fabric hue and slub; reviewers contradict round to round): v22's reviewer "too beige, brushed felt", v23's "too grey, too smooth, prefers v22". Measured against the paint: v23 is ~7 % cooler than photo 1 and right for photo 2 (each photo has its own white balance). Not tuned further: Colour and Slub set midway (v24) and named as designer controls in HOW_TO_TWEAK. Stall guard after v23 (fabric three reviews; tops missed): fabric mechanism already changed at v23; the bright tops are the light (advisor after v21), left open.

Advisor (Fable) after v24 ("flat slabs" three reviews): the edge, not the puff. The 3 cm sag cancelled half of the 6 cm dome (mesh profile: 39.0 front, 42.7 crown, 39.3 back), and a 2.5 cm edge radius keeps each block a crisp box: under this room's near-uniform light a 4° puff slope makes no gradient; the width of the roll band reads as the cushion (5 px at 2.5 cm, 20+ px in the photos). Analytic puff tested fine under raking light; a shoulder profile reads flatter; cloth would spend both rounds on pinning. → v25: `sofa_r` 0.055, sag 0.01, profile 2.0 (tested in the scene), plus vertical ripples on the back fronts at 3 mm.

Trade-off after v25 (edge roll): v24's reviewer "flat slabs" at 2.5 cm, v25's "bolsters and loaves" at 5.5 cm; the stall guard's "form wrong" for v25 is this trade-off, not a new mechanism (advisor consulted after v24). v26 splits it: seats and ottoman 4.5 cm, arms and backs 3 cm (`sofa_r`, `sofa_r_square`; designer controls). Last budgeted round, so v26 also carries the per-photo white balance (`wb_view`: photo 1 9000 K, photo 3 8500 K, photo 2 13000 K): the paint now matches each photo in absolute sRGB (R/B 1.16/1.23/1.13 vs 1.17/1.24/1.13), which settles the reviewers' hue argument by pixels; fabric albedo set to (0.445, 0.44, 0.44) against it. Two changes in one round, logged as such.

Stopped after v26: budget spent (8 rounds of round three). Stall guard after v26 ("seat tops too bright" v24–v26): reviewers measure against the wall in their crops; with v26's per-photo white balance the paint matches each photo in absolute sRGB, and in absolute terms the seat tops are ~10 % darker than photos 1 and 3, not brighter. The two measures disagree because the render's wall-to-seat light ratio differs from the room's (the lighting, advisor after v21). Left open, not tuned.

Pre-review: preflight `reviews/preflight_v19.png` clean (clay reads; nothing bright at albedo 0 but the windows; lights tiles black: the sky lights the scene, as in rounds one and two).

Newest first. Updated after every review. Cost is what the version took: Blender runs and minutes since the last row.

| Version | Score | The one change | Cost | Render |
|---|---|---|---|---|
| v26 | 6.7 (Shape 7.0, Placement 8.0, Detail 6.0, Fabric 6.3); pair preferred v26 | edge roll split (seats, ottoman 4.5 cm; arms, backs 3 cm), sag 2 cm; per-photo white balance (9000 / 13000 / 8500 K) with the fabric matched in absolute sRGB | 4 runs, 25 min | renders/v26.png |
| v25 | 6.1 (Shape 5.8, Placement 7.5, Detail 5.8, Fabric 6.0); pair preferred v24 | edge roll 5.5 cm, sag 1 cm, profile 2.0 (advisor), back-front ripples 3 mm | 3 runs + advisor, 25 min | renders/v25.png |
| v24 | 6.2 (Shape 5.8, Placement 8.3, Detail 5.5, Fabric 6.0); pair preferred v24 | seat fronts bulge 3 cm (V gaps), back tops roll 4 cm; fabric colour and slub set midway (trade-off) | 1 run, 10 min | renders/v24.png |
| v23 | 6.1 (Shape 6.5, Placement 8.0, Detail 5.5, Fabric 5.0); pair preferred v22 (fabric) | fabric mechanism: weave from Swyft's Pumice close-up, short slubs, cooler albedo; photographic output stage (2x, unsharp, JPEG); backs near upright | 7 runs, 45 min | renders/v23.png |
| v22 | 5.8 (Shape 6.0, Placement 8.0, Detail 5.0, Fabric 5.0); pair preferred v22 | shape from Swyft's drawings: seat seam 39 / crown 45, fronts tucked under the overhang (advisor), back blocks raked (a `sed` slip left 11.5 cm at the top: they leaned back ~15°), ottoman bow, 7 × 4 cm feet | 3 runs + advisor, 35 min | renders/v22.png |
| v21 | 5.4 (Shape 5.5, Placement 7.5, Detail 4.0, Fabric 5.0); pair preferred v21 | shape (advisor): pillow profile 1.8, a sag per seat, fronts rolling forward, low-frequency wobble on blocks and flanges, edge radius 2.5 cm | 2 runs, 15 min | renders/v21.png |
| v20 | 5.1 (Shape 5.0, Placement 7.5, Detail 3.5, Fabric 5.0); pair preferred v20 | fabric: slub streaks 5 mm x 3 cm and a 3 mm tone fleck (the weave is sub-pixel at 3–4 m), linen at 1.5x, near-neutral albedo | 5 runs, 30 min | renders/v20.png |
| v19 | 4.7 (sofa brief; Shape 5.5, Placement 8.0, Detail 3.5, Fabric 3.0); overlay hit in rows 1 and 2 | round three start: Swyft Model 03 from product sizes, flanged puffed blocks, ottoman fitted to photos 1 and 2, rough_linen fabric | ~12 Blender runs + 3 agents + advisor, 1.5 h | renders/v19.png |
| v18 | 5.8 (BC 5.8, BP 5.5, FC 6.3, FP 5.8); pair preferred v18 over v17; all luma targets hit | planks 600 x 120, grain contrast 2.0, plank spread 0.6, roughness 0.3 | 1 run, 10 min | renders/v18.png |
| v17 | 6.2 (BC 6.0, BP 6.0, FC 6.5, FP 6.3); pair preferred v17; all luma targets hit | mechanisms: brick from a whole-wall scan regraded by its height mask (advisor); floor from a rustic oak scan per source plank | 3 runs + advisor, 40 min | renders/v17.png |
| v16 | 6.0 (BC 6.2, BP 6.0, FC 6.0, FP 5.8); pair preferred v16; all luma targets hit | brick: plum-maroon albedo, bloom across joints, stronger mottling | 2 runs, 15 min | renders/v16.png |
| v15 | 6.1 (BC 6.0, BP 5.8, FC 6.2, FP 6.3); pair preferred v15; all four luma targets hit | floor grain: scanned CC0 oak veneer per plank (mechanism change) | 3 runs, 25 min | renders/v15.png |
| v14 | 5.3 (BC 5.5, BP 5.5, FC 5.5, FP 5.0); pair preferred v14; brick/paint hit, floor/paint 0.83 (missed) | floor: broad soft latewood bands, 1 mm dark seams, specular 0.3, greyer and lighter oak | 6 runs, 30 min | renders/v14.png |
| v13 | 5.2 (materials brief; BC 5.8, BP 5.5, FC 5.0, FP 4.8); brick/paint hit, floor/paint missed (0.78 vs 0.89–0.99) | round two start: brick and herringbone shader groups (mat_kit.py), white balance 13000 K | ~20 test renders + 2 agents + advisor, 2.5 h | renders/v13.png |
| v12 | 7.9 (L 8.3, W 7.6, S 7.9, B 7.4); pair preferred v12 over v11; all four targets hit | scalloped bookcase bays over a cupboard base; slimmer steel (40/20 mm); door east jamb 0.78 | 2 runs, 15 min | renders/v12.png |
| v11 | 7.7 (L 8.0, W 8.0, S 7.8, B 6.5); pair preferred v11 | reveals shifted 0.09 toward the central pier (asymmetric splay); overlay draws folds | 2 runs, 15 min | renders/v11.png |
| v10 | 7.4 (new brief; L 7.9, W 7.2, S 6.9, B 7.0); pair preferred v10 | windows closed, no secondary glazing (user); pilaster_x0 0.86→0.77; column depth 0.07; brief: rows by photo number | 3 runs, 15 min | renders/v10.png |
| v09 | 8.1 (L 8.3, W 8.0, S 7.8, B 8.2); pair preferred v09 | fork: joint fit of P + cameras; bookshelf block moved to its scan position | 4 runs, 20 min | renders/v09.png |
| v08 | 7.8 (L 8.3, W 7.8, S 7.5, B 7.0); pair preferred v07 | side-wall edge beams → cove (fold 3.60, 0.07 in) | 3 runs + advisor, 30 min | renders/v08.png |
| v07 | 7.6 (L 8.0, W 7.5, S 7.0, B 7.5); pair preferred v07 | pilasters 0.20/0.12→0.10/0.06 proud, head 0.10; splay 1.70→1.60 | 2 runs, 15 min (first reviewer stalled; its file was complete) | renders/v07.png |
| v06 | 7.5 (L 7.8, W 7.5, S 6.8, B 7.5); pair preferred v06 | splayed reveals 1.70→1.45, pier tops 1.57 | 2 runs, 20 min | renders/v06.png |
| v05 | 7.6 (L 7.9, W 7.2, S 7.5, B 7.8); pair preferred v05 | built-ins: full-length shelves, column radiator (top 0.98 from scan), panel heater; furniture blocks from scan components; cameras 6, 8 by landmark PnP | 4 runs, 40 min | renders/v05.png |
| v04 | 7.3 (L 7.5, W 7.5, S 7.3, B 6.5); pair preferred v04 | pilaster heads 0.30→0.12 (+ camera 8 refit at 768 px) | 2 runs, 25 min | renders/v04.png |
| v03 | 6.7 (L 7.0, W 6.8, S 6.2, B 6.3); pair preferred v03 | segmental arches: spring 3.22→3.50, rise 0.58→0.30 | 2 runs + cam 7/8 refits, 30 min | renders/v03.png |
| v02 | 6.7 (L 7.5, W 5.5, S 7.0, B 6.0); pair preferred v02 | internal windows: sill 2.52→2.64, frame flush; coplanar faces removed | 2 runs, 15 min | renders/v02.png |
| v01 | 6.8 (L 7.5, W 6.0, S 6.8, B 6.0) | first build: scan-measured shell, frame, sashes, mezzanine, kitchen blocks | ~25 Blender runs (scan analysis, camera fits), ~2.5 h incl. research | renders/v01.png |

Stall guard after v03: "pilaster heads too large" was raised in v02 and v03 but never changed until v04 (first change, read from photo 6 crops: a ~0.12 m splay, not 0.30). "Mezzanine front missed" in rows 5/6 is attributed by the v03 reviewer to cameras 5 and 6, not the model; photo 3 hits within 5 px. Camera refits queued after v04.

Stall guard after v04 ("camera fit errors" three reviews): mechanism changed for cameras 6 and 8, from edge correlation against the textured scan (stalls when clutter dominates the frame) to landmark PnP on clean architectural corners plus line constraints (`fit_cam.py`): camera 6 4.0 px rms, camera 8 5.9 px rms at 2048 px. Camera 5 had too few landmarks (14.6 px), kept the scan fit. The dining door misses its landmarks by ~33 px with camera 6 locked: suspect the door position (open item).

Stall guard after v05 ("camera fitting" three reviews): the residual pattern (error grows toward the frame edges, far ends fit) is lens distortion, as the camera research predicted ("if residuals grow with distance from the centre, add k1"). Mechanism change: a radial k1 per camera fitted with the pose (`cam_util.py`, `refine_cam.py k1`), and the sheet shows the photos undistorted to the render's pinhole.

Distortion check (after v05): k1 fitted with pose against the scan stays ~0 (|k1| < 0.004) for cameras 1, 2, 3, 5, 7; k1 from landmarks + lines on photo 3 is ill-conditioned (camera to 2.1 m). The edge-beam lines drift 12–28 px at the frame corners in photos 2 and 3; the scan shows no step at the wall tops (a smooth cove within 4 cm), so the photo's "beam" band is a plaster line the scan cannot resolve. Open item; not chased further this loop.

v06 plan: splayed window reveals (room face 1.70 m → glazing plane 1.45 m, both from the scan's reveal transitions), the mechanism behind the near-view misfits in photos 1 and 5 while photo 2 (head-on) fits; pier tops 1.52 → 1.57 (reviewer, photo 2 scale); dining-door coplanar cleanup.

Stall guard after v06 ("camera fit and lens distortion" three reviews): already acted on (k1 fits, landmark PnP; see above); the v06 reviewer's ranked problems are all model geometry. v07: pilaster projection W 0.20→0.10, E 0.12→0.06, head 0.12→0.10 (reviewer: 10–12 cm too proud; the scan's 0.2 at W was the LiDAR-rounded corner); splay reduced 1.70→1.60 (v06 false arris in photo 2).

Advisor (Fable) after v07, on the stall guard for ceiling lines / edge beams: (a) geometry, not distortion: the scan's side walls curve in from about z 3.3 and meet the ceiling 5–8 cm inside the wall plane; a constant 0.08 m step projects to 6 px far / 28 px near, the measured drift. The model's 3.72/4.08 boxes match nothing. (b) End piers in photos 1 and 7 sit 52° off-axis, where focal error dominates. (c) Central beam underside 3.74–3.765 in the scan. → v08: edge beams replaced by a cove (`cove_z` 3.60 by interpolating the photo 3 overlay: 3.72 was 20 px high, 3.40 28 px low; `cove_in` 0.07).

**Fork (after v08): per-round pixel nudges of single P values → joint fit of P (and camera poses) against all photos at once.** Advisor (Fable): the residual is shared between seven cameras and ~20 dimensions, so one-row nudges trade off between photos (v08's cove: 0–5 px in photo 3, 10–20 px in 1, 5, 6). Built as `scripts/joint_fit.py`: Workbench object-colour renders of the model, model edges (furniture edges masked) scored by truncated distance to photo edges, coordinate search over P with scan priors (σ 3 cm). Fork base: v07 (calibration winner). Budget 10 → 16.

Joint fit (fork step 1): 7 cameras then 21 P values then cameras again, 2.5 min. Mean model-edge distance to photo edges 4.24 → 3.90 px per view (768 px). Most gain from cameras; P moved little (col_w 0.115, col_y 0.00, radiator top 0.94, cove_z 3.69, cove_in 0.05, pilaster_x0 0.86, proud 0.108/0.053, pier_top 1.585, pier_proud 0.145, win_w 1.596): the shell values were already near their best for this metric. Bookshelf block moved to its scan position (x −0.95…0.30) — the calibration reviewer's "extra box at the pilaster".

**Instrument change before v10 (user):** the windows have secondary glazing, open in the photos with some factory casements; only the factory windows are needed. Reviewer brief design fact updated (closed factory windows, no secondary glazing); scores from v10 on are on the new brief, so compare across it only by blind pair. Stall guard after v09 ("edge-beam depth") — acted on (cove mechanism, joint fit); the v09 review does not raise it.

Stall guard after v10 ("camera 5" three reviews): k1 in the joint fit against model edges also stays 0 for camera 5, so the cause is geometry. Photo 5 sees the east window obliquely from 3.9 m; its near (pier-side) jamb at the room face is 24 px off, while v07's reviewer found the outer jambs too wide in photo 2: an asymmetric splay. v11: room-face openings shifted 0.09 toward the central pier (`reveal_shift`). Instrument: the overlay now also draws folds inside one object (studio-shaded pass), so the girder's front arris shows (v10's "girder flush" was the id pass missing it).

User (after v11): wrap up this round regardless of score; stairs are 10 steps in two flights (supports an upper floor at 2.08 = 10 × 0.208 risers) but are not to be modelled now. v12 is the last round; its blind pair against v11 stands in for the separate calibration (user asked to finish). Open after v11: rows 3/5 cove/ceiling line drift at frame edges (k1 stays 0; not resolved).

**Final: v12** (user asked to wrap up this round). Open items from the v12 review: lower-tier glazing rail and right-window mullion spacing; radiator 10–15 cm too high and ~15 cm too far from the window wall; central beam 18 px low in photo 5 only (beam west face or camera 5).

## Calibration

Round three (`reviews/calibration_sofa.md`): **v26 6.5 beat v24 6.3** blind (v26's per-photo white balance matches the photos; v24 sits under a yellow-brown cast; same shape). Both miss the fabric levels against the wall and both read the flanges as thin. The winner is 2.0 under 8.5; the experiment forked in round one and the user asked to wrap up, so no fork: finish from v26.

Stopped after v08: slope flat (best of v06–v08 7.8 vs v03–v05 7.6, under +0.3). Calibration: v08 vs v07 (blind). **v07 wins 7.3 vs v08 7.1** (same instrument; the deeper cove fits photo 3 but misses 1, 5, 6). 7.3 is 1.2 under 8.5 → fork once (budget +6).

(At the end of the loop: the best earlier version re-scored blind beside the final. See `review-render`.)
