# aztechno-building — progress

## Setup notes (2026-09-30)

Mac, Blender 5.2.2 LTS, Metal (M4 Max). 5.x only is fine; no 4.4 constraint.

Knowledge that lands in v01:
- **View transform:** AgX turns saturated red and orange paint peach (`colour.md`); Khronos PBR Neutral keeps them. Default `P["view"]="Khronos PBR Neutral"`, A/B once against AgX via `sweep.sh`.
- **Sky gradient over the frame's own span** (`colour.md`): the sky must vary across the frame, not only over 0–45°.
- **Isolate before guessing / base-colour-black render** (`insights.md`): glass is a mirror subject; design what it reflects (street, opposite buildings, mountains) before tuning the glass shader.
- **Most early look problems are render bugs** (`review-loop.md`): run `build.py --preflight` before round 1 (clay, mirror, albedo 0, each light alone).
- **Fit the camera from landmarks** (`matching-a-reference.md`, `tools/fit_camera.py`): facade corners → camera; render at the reference's exact 1400×979 aspect for `compare.py`.
- **Measure a table on both images** (`tools/measure.py`): wall red median, shadow ratio, sky gradient, glass level.
- **Black gaps / depth from geometry, not AO** (`modelling.md`): the facade relief (bands, frames, arches) must be real extruded depth so the sun casts real shadows; no Bevel modifier after booleans (clamp overlap).
- **Supersample fine patterns** (`cycles.md`): window mullions and shutter slats alias; render 2× and downsample for finals.
- **Build every value into `P`**; use `tools/nodes.py` one-node materials from v01.

Newest first. Updated after every review. Cost is what the version took: Blender runs and minutes since the last row.

## Process guess

A shift-lens architectural photo of a real cast-plaster facade, low sun from the front-right: build the relief at true scale from a traced spec, physical sun and multiple-scattering sky at 4000 m, reflective coated curtain glass that mirrors a modelled street behind the camera.

## Advisor (Fable), plan stage, 2026-10-01

Measured the reference sky at 0.75–0.95 of a lit cream wall (the physical sky 0.3–0.5), and the upper glass at 40–65 % of the sky. Top risks and the change taken:
1. Glossy-ray sky lift puts a 4x sky in every paint, mullion and chrome reflection → lift **camera rays only**, about 2x; get glass brightness from the glass: coated, F0 0.2–0.3 (IOR, never Specular IOR Level above 1).
2. Voronoi pane tilt ignores the mullion grid (bent-glass look) → **tilt per pane**: hash the pane cell from each opening's own pitch (object attributes), ±0.3°, ±20 % F0.
3. Perfect regularity of the slabs → low-frequency plaster waviness (taken as a low-frequency bump in Paint for v01, not a Displace; edges stay straight at 2.6 cm/px).
4. Sub-pixel mullions, slats and lines → review at 1x, final at 2x and downsample.
5. AO grime darkens sunlit inner corners → **directional dirt**: dust on up-facing tops, streaks under ledges, strength ~0.1; drop plaster bump.
Also: add an emissive "room card" at 5–8 % in the lower glass (later); context and pavement behind the camera feed reflections and neutral bounce (kept).

## Advisor (Fable), glass, after round 4

Measured the reference panes: flat top-band panes p50 43 (dark navy) against a sky of 0.6-0.8 linear, so F is about 0.05: plain tinted float glass, not a 0.35 coating. The bright streaks (135-166) are sunlit interiors seen through the tint; the pale corner bays are Fresnel at grazing angles. v04 matched the median by accident (F 0.35 x a sky 4.5x too dark). Change taken in v06: F 0.05 thin-wall glass transmitting ~40 % with shadow rays passing, dark rooms with columns and curtains, sky lift for camera and glossy rays (paint Specular IOR Level 0.3 to compensate), a staggered 3-4 storey street with gaps, rebar, poles, cable and a snowy peak, pane tilt up to 1 degree, darker mullions.

| Version | Score | The one change | Cost | Render |
|---|---|---|---|---|
| v16 | 6.3 | Tower oculi: rings and link at absolute depths 0.15-0.21 m (the relief factor made them 0.7 m tubes), diamonds forward with no shadow; warm grey-beige sidewalk | 3 runs, ~10 min | renders/v16.png |
| v15 | 6.4 | Left corner: chamfer glass gets its pane grid (missing attributes divided by zero), round oculi, red walls for the grey box, sign letters 1.3 m out so the fascia cannot hide them, gold mullions | 5 runs, ~15 min | renders/v15.png |
| v14 | 6.3 | Glass: reflections see the lifted sky and cirrus above ~14 deg elevation, the street HDRI below; per-pane reflectance +-60 % (upper glass p90 147 vs 148); chrome diamonds bright; corner-tower window bars | 9 runs, ~20 min | renders/v14.png |
| v13 | 6.4 | Roof caps rebuilt as meshes: thin yellow slab 0.32 m proud with an underside sloping to a red pedestal, red top block (were 1 m deep: the relief factor scaled them) | 3 runs, ~12 min | renders/v13.png |
| v12 | 6.3 | Reflection HDRI rotated 300 → 335° (the gold onion dome leaves the glass); flat-topped tanks with a 0.35 r shoulder (bundled geometry fix, flagged 6 rounds) | 6 runs, ~12 min | renders/v12.png |
| v11 | 6.5 | Shadows: sky 1.5 for diffuse fill (camera sky lift 4.5 → 3.0 keeps the visible sky), relief x2.8; cream shade (111,114,110) on target | 5 runs, ~10 min | renders/v11.png |
| v10 | 6.2 | Reflections: modelled low dark houses (1-3 floors) in front of the HDRI sky; chrome brilliant-cut diamonds 30 px (bundled: a geometry bug flagged 8 rounds); vertical mullions in the stepped bays | 4 runs, ~15 min | renders/v10.png |
| v09 | 6.0 | Reflections see a photographed street (construction_yard HDRI, glossy rays only; fork replacement 2); right neighbour traced as RC frame + pale hollow brick, shutter | 14 runs, ~35 min | renders/v09.png |
| v08 | 6.0 | **Fork**: v05 look + photographic output stage (2x, Lanczos, unsharp 1 px 40 %, JPEG q85) | 10 runs, ~30 min | renders/v08.png |
| v07 | 5.9 | Cirrus cloud layer in the world (camera and glossy rays), glass F 0.08, brighter reflected street | 3 runs, ~10 min | renders/v07.png |
| v06 | 5.3 | Glass mechanism (advisor): tinted float glass F 0.05, thin-wall see-through, sunlit rooms, sky lift for glossy rays, staggered street context | 7 runs, ~20 min | renders/v06.png |
| v05 | 5.7 | CG-clean pass: chalky paint blotches, outline layers 1.8 cm behind their core (yellow/orange shade share on target), thinner sills, grey frames on punched windows | 3 runs, ~15 min | renders/v05.png |
| v04 | 5.7 | Outer thirds: offset() winding bug fixed (corner-tower windows were slots, outlines shrank), left corner rebuilt from reference polygons at forward depth (its pier faces the sun), entrance, bronze sign | 7 runs, ~30 min | renders/v04.png |
| v03 | 5.3 | Weathering pass: two-scale paint mottle and roughness, streak and splash-zone dirt, cast-slab pavement with slanted joints; relief x2.2 (tower shadow 11 px) | 3 runs, ~15 min | renders/v03.png |
| v02 | 5.2 | Stepped moulding layers (relief x1.8, 1.5 cm bevels), painted inset lines, tower rebuilt from the close-up | 6 runs, ~25 min | renders/v02.png |
| v01 | 4.4 | First build: traced facade as curve slabs, physical sun + multiple-scattering sky, coated glass, context street, calibrated to the measured table | ~20 runs, ~3 h incl. research | renders/v01.png |

## Calibration

Stopped at round 7 on the slope rule (best of rounds 5-7: 5.9; best of rounds 2-4: 5.7; +0.2 < 0.3).

| Pair | A | B | Winner |
|---|---|---|---|
| v07 vs v05 (blind, `reviews/calibration.md`) | v07 5.3 | v05 5.6 | **v05**: fuller shadows (cream shade share 0.29 vs 0.19) and dim reflective glass; v07's see-through glass mirrors a box city. Both: fat oculus rings, tiny diamonds, the left wing's grey box, repeating ground, sharp edges. |

Winner 5.6 is 2.9 under the 8.5 target: fork once.

After the fork (budget 16 spent):

| Pair | A | B | Winner |
|---|---|---|---|
| v11 vs v05 (blind, `reviews/calib_fork.md`) | v11 6.0 | v05 5.4 | **v11**: the fork beats the pre-fork winner (paint, sky, brick read photographic) |
| v16 vs v11 (blind, `reviews/calib_final.md`) | v16 6.4 | v11 6.1 | **v16**: its model fixes (flat tanks, caps, oculi, sign, left corner) follow the photo; v11's relief read deeper |

**Final: v16, calibrated 6.4** (target 8.5). Trend 4.4 → 6.5 over 16 rounds; the fork (photographic output stage) lifted the plateau from 5.3-5.9 to 6.0-6.5.

**Fork: pinhole image (1.5 px filter, no processing) → photographic output stage** (advisor, Fable). The fault is image formation: the reference is a sharpened JPEG, the render a soft filtered pinhole, so every region reads rendered at once (fine-detail energy 0.72-0.89 of the reference everywhere; mid-frequency structure already at parity). v08 = v05's look (coated glass, camera-only sky lift; chalk 0.15) rendered at 2x, Lanczos to 1400, unsharp 1 px 40 %, JPEG q85 (`tools/photo_finish.py`; gate `tools/sharpness.py`: edge ratio and fine detail against the reference). Fallback: an image-based street for glossy rays. Budget raised to 16.
