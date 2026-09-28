# eclipse-glow — progress

## Sunrise video (`scripts/build_sunrise.py`)

The rise reworked as a sunrise over hot water, from the designer's notes on v07: the contact point is a blown-out, blooming, grainy highlight; a gap opens between the logo and its mirage image as it lifts off; the heat haze blurs as well as shimmers. Imports `build_rise.py` and swaps its atmosphere stage; the rise files are untouched. Process guess: 2D compositor, keyed to a vanishing line (see RESEARCH.md, "Sunrise video"). Reviewer brief: `reviews/sunrise/REVIEWER_PROMPT.md` (new brief, so scores do not compare with the rise).

| Version | Score | The one change | Render |
|---|---|---|---|
| v08 | 7.1 | Haze (flagged every round): warm sky drawn before the displace so the line shimmers and is mirrored; shimmer 8 → 12 px reaching 0.11; blur 7 → 12 px over 0.13; 40 px contrast veil. Bug fix: film grain reseeded per frame (was frozen; build.py) | `renders/eclipse_sunrise_v08.mp4` |
| v07 | 7.3 | Reflection softened: Gaussian feather by band depth (no hard cut), slight warm tint, stem 0.55 → 0.65, held until ~100 px of lift (hold 0.03 → 0.05) | `renders/eclipse_sunrise_v07.mp4` |
| v06 | 7.4 | Sun bloom: the core also feeds a 230 px warm bloom and a 900×12 px streak along the line; contact grain 0.8 → 1.4 | `renders/eclipse_sunrise_v06.mp4` |
| v05 | 7.1 | Mechanism change after "the reflection never leaves" repeated 3 rounds: mirror strength × presence (logo coverage within ~30 px above the line, blurred down over the mirror), so it is gone ~80 px after lift-off | `renders/eclipse_sunrise_v05.mp4` |
| v04 | 6.7 | Mechanism change after the "too wide" note repeated 3 rounds: an oval hot core per contact (key blurred sideways, thresholded at its peak) with its own bloom; zone gain 5 → 1.5 so bar bases stay pink | `renders/eclipse_sunrise_v04.mp4` |
| v03 | 6.8 | Highlight hugs the line: contact key width 0.05 → 0.02 frame heights, so the bar bottoms stay pink and only the join blows out | `renders/eclipse_sunrise_v03.mp4` |
| v02 | 6.6 | One sun, not one slab per bar: a wide, flat, untinted bloom (300×45 px, ×6) off the contact source fills the gaps along the line | `renders/eclipse_sunrise_v02.mp4` |
| v01 | 6.2 | First build: vanishing line + bright mirage band, mirror reach 0.12 (gap shows), stem stretch, haze blur, contact highlight with local bloom and grain | `renders/eclipse_sunrise_v01.mp4` |

Loop stopped after v08: scores plateaued (7.4, 7.3, 7.1) and reviewers contradict each other (v05: the contact blooms; v08: "two thin slits"; haze "too weak" then "reaches too high"). Final: v08, the closest to the designer's notes (haze blurs, grain animated). v06 (7.4, sharper haze, frozen grain) is the alternative. Open notes: the stem at the join is subtle; the reflection fades by ~40–80 px of lift; the horizon line is uniform across the frame.

## Rise video (`scripts/build_rise.py`)

The logomark rises out of a horizon like a moonrise, with a mirage. Process guess: 2D atmosphere in the compositor, keyed to the distance from a horizon line (see RESEARCH.md, "Rise video"). Music: an original cue (`scripts/score.py`), not the Terminator theme (copyrighted; `make_video.sh` takes a licensed track instead).

| Version | Score | The one change | Render |
|---|---|---|---|
| v07 | 7.2 | Shimmer softer: one smooth noise octave (was 3), layers ~20 px (was ~7), fades over 38 px (was 75) | `renders/eclipse_rise_v07.mp4` |
| v06 | 7.3 | Mirror fades by the height of the reflected point (only the last ~40 px above the horizon mirror), squashed 3× (was 1.8×) | `renders/eclipse_rise_v06.mp4` |
| v05 | 7.1 | Mechanism change after the horizon-stripe note repeated 4 rounds: broad warm sky fading upward, thin dim line, quick falloff into dark ground | `renders/eclipse_rise_v05.mp4` |
| v04 | 6.7 | Shimmer livelier and lower: evolves 2× faster, fades over 75 px (was 130), so risen edges are clean. Also fixed: --set now reaches the atmosphere inputs | `renders/eclipse_rise_v04.mp4` |
| v03 | 6.6 | Shimmer visible: noise stretched to ±1 (was ±0.3, about 2 px), finer bands, 4× faster, layers drift upward | `renders/eclipse_rise_v03.mp4` |
| v02 | 6.8 | Pacing: rise starts at f12 with a sine ease-out to f288 (was ease-in-out f12→f228, so 2.5 s of nothing and 2.5 s frozen) | `renders/eclipse_rise_v02.mp4` |
| v01 | 6.7 | First build: horizon mask before the glows; shimmer, flatten, mirror, extinction, horizon glow before bloom; 12 s rise keyed on Logo › Location Y | `renders/eclipse_rise_v01.mp4` |

Loop stopped after v07: scores plateaued (7.1, 7.3, 7.2) and the reviewers now contradict each other on haze height (v06: gone by 40 px; v07: 100–160 px). Open notes: horizon line still reads a little "synthwave"; the logo clears the horizon around f160, leaving a long slow drift. Final: `output/FINAL_eclipse_rise.mp4` (v07), `output/eclipse_rise.blend`.

## Still (`scripts/build.py`)

v2 build: `scripts/build.py` (5.x). Research step skipped: no new reference, and the mechanism is v1's (see `knowledge/decisions/eclipse-glow.md`).

| Version | Score | The one change | Render |
|---|---|---|---|
| v09 | 6.8 | Arc line and arc glow gated to each shape's top cap (no arc on the step ledges) | `renders/eclipse_logo_v09.png` |
| v08 | 7.2 | Mechanism change after research: halo = the body's own bright parts blurred and added (self-glow), replacing the silhouette halo | `renders/eclipse_logo_v08.png` |
| v07 | 7.1 | Halo weighted to each shape's base (height AOV; top at 15%) | `renders/eclipse_logo_v07.png` |
| v06 | 6.8 | Crescent only on each shape's top cap (cap AOV from shape_v), glow 28→12 px, amount 1.1→0.6 | `renders/eclipse_logo_v06.png` |
| v05 | 6.8 | Glows actually render: every Post blur was 0 px (5.2 ignores a Blur Size linked from Relative To Pixel or through Combine XYZ); plus a silhouette halo from the coverage mask | `renders/eclipse_logo_v05.png` |
| v04 | not reviewed (correctness step) | First blur fix (Combine XYZ removed); still 0 px | `renders/eclipse_logo_v04.png` |
| v03 | 6.2 | Geometry matched to the final GLB: 0.18 m slab, 0.06 m round edge (GLB 0.03), via Inflate's wall + round profile | `renders/eclipse_logo_v03.png` |
| v02 | skipped (superseded by v03) | Shape Gradient: body colour blends each shape's own bottom → top with the surface-angle gradient (0.7) | `renders/eclipse_logo_v02.png` |
| v01 | 5.2 | First build: inflated logomark, v1 material and lens as one node each, world background | `renders/eclipse_logo_v01.png` |

Loop stopped after v09: scores plateaued (7.1, 7.2, 6.8). The top remaining note is "flat faces, make them pillows", which conflicts with the designer's 0.18 m slab; the Roundness control on the Inflate modifier covers it. Other open notes: crescent reads as a lid on flat tops; halos overlap brown between bars.
