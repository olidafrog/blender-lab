# cyber-model — session notes

Everything here is promoted to `knowledge/` (pointers in brackets). Kept as this experiment's record: what each round changed, and what it cost.

## Learnings

- Overlapping joined cutters cancel in an Exact boolean: empty plate or missing cuts, no message. `use_self = True`, assert the polygon count. [gotchas/geometry.md]
- Boolean leaves an empty material slot 0; `material_mode = "TRANSFER"` carries a cutter's material (black vents, holes, moats) into the new walls. [gotchas/geometry.md]
- Flat tops mirror a far-side softbox: render with base colour black to see how much brightness is reflection. Fix is the light, not the albedo. [gotchas/cycles.md, insights.md]
- Light linking per collection (backdrop, device, steel only) gives independent control of gradient, plate tone and metal. [gotchas/cycles.md]
- Crisp chamfer: 1 segment, Harden Normals off, flat shading, fine corner arcs. Harden Normals + Smooth by Angle gives soft shoulders. [gotchas/modelling.md]
- Black gaps by geometry (gaps, undercut, moat, liner, black cutter walls); AO cubed and AO on the backdrop for the contact halo. [gotchas/modelling.md, shader-nodes.md]
- Rectify the reference to a plan, trace in plan px, overlay an ortho plan render; fit the camera from 12 landmarks; map the reference's near-black pixels before tuning. [process/matching-a-reference.md]
- Fine grain albedo-only at two scales; drawn stroke mask for scratches; wall lift from Geometry Normal. [gotchas/shader-nodes.md]

## Process

- The ten-round loop used a Sonnet reviewer (yes/no list, script-measured table, weighted sub-scores, anchor, blind pair) and an Opus advisor twice. The pair picked the newer render nine times in nine; absolute scores sat near 6 for six rounds. [process/review-loop.md]
- `tools/blender.sh` hid `sys.exit` messages and, with `set -e`, stopped silently when `grep` matched nothing. Fixed: it now prints the raw tail on a failed or empty run. [process/improvements.md, gotchas/headless.md]
- Two hand-written zsh loops dropped their `--set` values. `tools/sweep.sh` worked every time. [process/improvements.md]
- Eight proposals (reviewer template, advisor cadence, promoting `fit_camera.py`, `measure.py` and `hs_kit.py`, `--expect-same`, a hard-surface start in `new-experiment`, a `--set` guard) are in `knowledge/process/improvements.md` under Proposed.

## Cost

- v01 to v03 (5.9, 5.8, 6.0): a 6 mm tray with far-side light. The first fix raised heights and added a fill that also lit the backdrop; it took the advisor's mirror test to find that the key itself was the problem (v04).
- v05 to v06: base slab was void black (read as a tray), then polymer; blacks and grain were tuned by value for two rounds before mapping where the reference's blacks are (a contact halo).
- v07 to v09: soft "pillow" edges fixed by mechanism (flat chamfer), black gaps by moats and a liner. Two rounds went to boolean failures that looked like design changes (silver slab, no vent slots), about 1.5 hours in all.
- v10 (6.4) lost the blind calibration to v09 (6.7) because of a near-black base foot; the ship configuration is v09, reproduced with MAE 0.00. `--set cut_self=True` adds the vent slots and the screw.
- Numbers: 84 Blender runs, 102 active minutes, 2 Sonnet research agents (about 13 min each), 10 Sonnet reviews and 1 calibration (80–165 s each), 2 Opus consults (about 6.5 min each).
