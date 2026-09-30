# cyber-deck-v2 — progress

## Setup notes (read first)

**Machine:** Mac, Blender 5.2.2 LTS, Cycles on Metal (M4 Max). `reference/` docs present. 5.x-only is fine (light linking, Boolean `material_mode`); Windows 4.4 not in play.

**Prior attempt:** `experiments/cyber-model/` (untracked; Sonnet reviewer, 6.7 best at v09). Its method: 2D plan outlines traced from a rectified reference → extruded plates → booleans → 1-segment chamfer, flat shading. By eye it reads as thin flat CAD plates: vertical walls everywhere, no section profile, no moulded curvature, pods too big, forms too shallow. v2 must change the **modelling mechanism**, not tune v1. v1's hard-won traps are reused below.

**Gotchas that apply, and where each lands in v01**

| Gotcha (source) | Lands in |
|---|---|
| Exact boolean with overlapping joined cutters cancels or returns empty; assert poly count and print z-levels after every cut (`cyber-model` proposed) | `cut()` helper: `use_self=True`, assert `len(polygons)>0` |
| Boolean apply leaves a `[None]` material slot; appended material lands in slot 1 (`cyber-model` proposed) | `cut()` clears/reassigns slots after apply |
| Far-side softbox mirrors in dark satin tops (albedo 0 still read 120–137) (`cyber-model` proposed) | light rig: device key on camera side, light-linked; albedo-0 test before round 1 |
| Black creases need geometry (moats, undercuts) + AO on backdrop for the contact halo (`cyber-model` proposed) | panel gaps are real cuts; backdrop AO in the floor group |
| Flat-shade planar caps; `set_sharp_from_angle` sets every face smooth (`cycles.md`) | `finish()` helper; mirror-override render before round 1 |
| Bevel wider than 1/3 of the narrowest cap overlaps (`geometry.md`) | bevel widths per part in `P`, clamp checks |
| Coplanar faces render black/speckled: lift 0.03 mm (`cycles.md`) | `P["eps_mm"]` on stacked parts |
| `Standard` view transform for literal LCD cyan (`colour.md`) | `P["view"]="Standard"` |
| Grain must be albedo-only, two scales, coarse enough to survive OIDN (`cyber-model` proposed) | backdrop group |
| Debug sheet + silhouette IoU catch proportion errors early (`modelling.md`) | `tools/debug_views.py`, `tools/silhouette.py` before round 1 |
| zsh word-splitting drops `--set` in loops (`headless.md`) | variants only via `tools/sweep.sh` |

**Process guess (research done):** Fusion 360 CAD solids (sketch → extrude → 3–5 mm fillets, sloped filleted steps) rendered in KeyShot with curvature wear and bead-blast bump. v2 mechanism: every shell is a plan outline lofted through a designed section (`scripts/hs2.py`), pockets from profiled cutters, wear from faces tagged at loft time.

**Correctness pass (before round 1):** clay and mirror overrides clean (flat caps, continuous fillet highlights, no domes). Polymer albedo 0 still gives subject median 38 (reflection is half the tone). Silhouette IoU 0.81 → 0.83 after shortening the antenna pods (25 mm) and levelling the antenna (tilt 6°). Build 4 s, full 1600×1200 render at 256 samples 13 s.

## Versions

Newest first. Updated after every review. Cost is what the version took: Blender runs and minutes since the last row.

| Version | Score | The one change | Cost | Render |
|---|---|---|---|---|
| v11 | 6.3 | v10 problems 1–2: slopes less mirror-like (Card Slopes 10 → 4 W, polymer roughness 0.36 → 0.44); LCD shield trimmed (LCD + 7/10 mm per side). Pod size left: v07 said 1.5× too big, v10 said too small (contradiction) | 1 run, ~5 min | `renders/v11.png` |
| v10 | 6.4 | v09 problem 1–2 as geometry: logo plate a 6–7 mm moulded step (48° flat band, 1.2 mm fillet), upper-body S-band 5 mm at 50°, battery lower; polymer bump off (speckle in albedo/roughness only); wide solid LCD shield carrying the pods (no backdrop between); cord plug a low dome on the body | 3 runs, ~15 min | `renders/v10.png` |
| v09 | 6.3 | v08 problems: dial module seated on a black housing down to the table, bracket light satin aluminium (0.42, rough 0.55), 36-tooth gear; flat 3 mm satin bezel, corner hook removed; glossy-only "Card Slopes" behind the camera at 10 W (trade-off control: 25 W lifts slopes but p5 12 → 19); bead-blast coarser; finer backdrop grain; cord 34 tighter turns looping onto the table | 5 runs incl. 2 sweeps, ~20 min | `renders/v09.png` |
| v08 | 6.3 | v07 problems: metal to dark brushed gunmetal (bracket, battery strip 2.5 mm, pivot) and metal card 24 → 10 W; bracket lobe and arm broader; pods 12.4 → 9.8 mm, closer together, pulled back behind the bezel; satin polymer (roughness 0.36, bump 0.06 at 0.25 mm, speckle moved into roughness) | 1 run, ~10 min | `renders/v08.png` |
| v07 | 6.2 | Advisor mechanisms: one small 0.25 m device key at camera-left, no fill, dome 0.12, polymer 0.085 (blacks p5 20 → 12, <12 % 2.7 → 4.7); dial bracket as a thin aluminium plate (arm + lobe) on a black block, flush 60-rib thumbwheel; finish: wear on the fillet crest only, bead-blast grain ×2, straight scratches, smaller matte screws; hook, lever, jack-ring fixes | 6 runs incl. 2 sweeps, ~30 min, + advisor ~6 min | `renders/v07.png` |
| v06 | 5.7 | v05 problems 1–2 as mechanisms: dial bracket a raised aluminium plate at the top-module level with screws and a black channel; pods end at the LCD frame with dark caps (bare ends mirrored the LCD); knurled collar pod-wide with a diagonal knurl; battery block a separate sloped block with a raised diagonal panel, INSERT latch, 1.8 mm black gap and a steel strip on its side only; outer shells come down to the table on an inset foot, base a hidden black core (its rim read as a tray) | 7 runs, ~30 min | `renders/v06.png` |
| v05 | 5.5 | v04 problem 1 (left side, pods): rebuilt dial (aluminium ring, dark face, maroon ticks, black Y knob, 7 mm gear), pods as gunmetal barrels in a cradle with rubber caps; reviewer: values only, bracket still a triangle, pod ends teal | 4 runs, ~15 min | `renders/v05.png` |
| v04 | 5.6 | v03 problems 1–2: moats (black channels) at every step foot; shallow plan bends get large radii (S-step sweeps); upper body re-grouped from the plan (switch area, strip and lower right one moulding, logo plate on top, battery block lower) | 5 runs, ~25 min | `renders/v04.png` |
| v03 | 5.2 | Problem 1 of v01 (flat slabs, no blacks): planar 50° slope bands with a 1.2 mm top fillet and 0.4 mm crease; 1.2 mm gaps over a black liner; raised LCD frame with a 55° pocket wall; undercut stems on the shield and wing; lower battery block; dial bracket pulled back from the LCD. Bugs: LED no longer lights neighbours; backdrop bump removed (worm grain) | 6 Blender runs incl. v02 test, ~25 min | `renders/v03.png` |
| v02 | — (test) | First half of the v03 change (sections, gaps, LCD pocket); not reviewed: the LCD frame and undercut were still missing | 1 run | `renders/v02.png` |
| v01 | 4.8 | First build: all shells lofted through designed sections (slopes + 2–3 mm fillets), profiled-cutter pockets, tagged edge wear, v1's camera/light/LCD | Research ~25 min (3 Opus agents in parallel) + ~20 Blender runs, ~40 min incl. kit | `renders/v01.png` |

## Calibration

Blind A/B, fresh Opus reviewer, neutral file names in the scratchpad, told to open no other repo files (key: `reviews/calibration_key.txt`).

| | Score | Top problem |
|---|---|---|
| A = v11 (final) | 6.2 | LCD shield reads as a thin extruded frame |
| B = v10 | 6.4 | blacks: 3.5 % of subject under 12 vs 7.6 % |

Closer to the reference: **B (v10)**. The final did not beat v10, so the hand-off ships v10's configuration (`scripts/build.py` restored from `snapshots/build_v10.py`; `chk10.png` matches `v10.png`, MAE 0.00). Budget spent (10 reviews). Trend 4.8, 5.2, 5.6, 5.5, 5.7, 6.2, 6.3, 6.3, 6.4, 6.3; target 8.5 not reached.

**Slope brightness (round 10 complaint), isolated after the loop:** the flat 48° slope band reads 89 (target 90–105, on target). With the device key off it drops to 26; with albedo 0 it stays 33. The "chrome ribbons" are the 1.2 mm fillet crests mirroring the small device key, not the slope faces. Mechanism for next time: rougher fillet-crest faces (the `wear` tag already marks them) or a slightly larger key.

## Log

- **Round 1 (Opus, 4.8):** (1) body reads as stacked flat slabs with fat 8–10 mm round edges, no sloped steps, no crease, no LCD shield, gaps not black (p5 21 vs 7); (2) left dial on a chrome triangle and pods as fat cans: wrong parts and chrome instead of gunmetal; (3) wear a chalky 20 px band, curly scratches, no bead-blast grain. Scores do not compare with v1 (Sonnet reviewer).
- My read of problem 1: the 3 mm top fillet ate most of a 4 mm slope, so slope + fillet shaded as one pillow. v03 makes the slope a flat band with a 1.2 mm fillet.
- **Light test (key sweep):** linking the far-side key to the device too (so parts cast shadows toward the camera, as in the reference) washed every top grey (median 66 → the tops mirror the softbox) and blew the LCD to (198, 243, 249). Research agent C predicted it. Blacks must come from geometry and occlusion, not from that light. Kept `key_on_device=False`.
- **Where the reference's blacks are** (pixels under luma 22): an outline round every part, a deep channel under the S-step above the battery block, the gap between the LCD frame and the dial bracket, and under the lower blocks. v03 has only a few.
- **Rounds 3–5 (5.6, 5.5, 5.7):** moats made thin black creases; the left side and pods were rebuilt twice but still read "triangle / cans"; the finish problem (chalky wear, curly scratches, no grain) went unaddressed for five rounds; p5 stuck at 20–23.
- **Reviewer read the build scripts:** the v05 reviewer quoted "the build diff" — it opened `reviews/build_v0*.py`. Snapshots moved to `snapshots/` from v06 on, so reviewers stay blind to history.
- **Advisor consult (Fable, after round 5, reviews withheld):** the rig was the black-killer. Two 0.9 m softboxes at ~0.7 m subtend ~65°, so every facet (gaps included) reflects softbox and tops, slopes and walls read the same. One small key at camera-left (not in the tops' mirror direction) casts real shadows between parts; a dim dome is the only ambient; lighter, more diffuse polymer. Its test: p5 26 → 11, <12 % 1.7 → 5.4. Also named: dial bracket as a thin plate with a tapered arm, fine-ribbed flush thumbwheel, cassette in a bay with a thin rail, cord too fat, crest-only wear. Applied in v07 (lighting, bracket, wheel, wear); cord and cassette rail pending.
- **Rounds 6–7 (6.2, 6.3):** the advisor's light rig hit the black targets for the first time (p5 12). Recurring: left dial module construction (4 rounds), slopes no lighter than tops, LCD bezel reading as chrome. The v08 reviewer also quoted the v07 review — reviewers list `reviews/` and read earlier reviews. Not fixed mid-loop (moving files could upset the hooks); logged for the retro.
- **Slope rule at round 7:** best of rounds 5–7 (6.3) vs rounds 2–4 (5.6): +0.7, continue.

## Cross-experiment pair (2026-09-30, audit session)

Blind Opus pair, neutral names (`tools/review_round.py --pair`), this experiment's `REVIEWER_PROMPT.md`: **v10 5.9 vs cyber-model v09 5.0** (`reviews/pair_cyber-model.md`, key in `snapshots/pair_cyber-model_key.txt`). This build wins on form (S-step, LCD shield, layout); cyber-model wins on material (satin speckle, wear). Both miss the blacks target.
