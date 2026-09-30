# cyber-model — decision record

A sci-fi handheld radio ("DT-03") recreated from one 736×552 hard-surface render, built entirely in `build.py`. A test of Sonnet on this task: two Sonnet research agents, ten Sonnet reviews plus a blind calibration, and an Opus advisor at the plan stage and after three reviews. Final 6.7 (v09, calibrated 6.7 against 6.5 for v10) of a target 8.5; scores are not comparable with Opus-reviewed experiments. Trend 5.9, 5.8, 6.0, 5.9, 6.0, 6.5, 6.6, 6.5, 6.7, 6.4.

## Chosen

- **Layout from a rectified plan.** The reference was warped to a top-down plan (azimuth 41°, elevation 50°, 3.6 px/mm); outlines were traced in plan px, and an orthographic plan render was overlaid on it. The hero camera was fitted from 12 landmarks: azimuth 41.0°, elevation 48.65°, 200 mm lens (near-orthographic), rms 6 px.
- **Stacked plates from 2D outlines.** A 13 mm slab, steps of 4–8 mm and a 12 mm shield block. Booleans for pockets, vents and screw holes (joined cutters; v09 leans on a MANIFOLD fallback, `use_self` fixes the cause in v10), then bevel weights by edge class and a flat 1-segment chamfer with flat shading.
- **Black by geometry.** Real gaps between same-level plates, an undercut under the shield, a 3 mm moat cut round it in its neighbours, a black liner slab under the lower plates, black cutter walls via Boolean material transfer, AO cubed on the polymer, and AO on the backdrop for the contact halo.
- **Three linked lights.** A backdrop key (gradient, cast shadow), a device key on the camera side (plate tone, walls) and a card that only the steel parts see. Standard view transform.
- **Drawn textures, one node per material.** LCD, decals and scratch mask drawn with PIL; Polymer, Steel, Rubber, LCD and Backdrop are single group nodes with named, ranged inputs; images are packed in the `.blend`.
- **Advisor at the plan stage and after three reviews**, mechanism only, reviews withheld.

## Rejected

- **Subdivision with support loops, Weighted Normal, the Mesh Bevel node.** Loops multiply with panel lines; Weighted Normal measured worse (max normal error 0.022 against 0.000); the Bevel node has no clamp or hardening.
- **Shader Bevel-node edge wear, and a second polymer material for chamfers.** Double lines on real bevels, a 47 s first Metal compile; the edge slot read as beads.
- **Harden Normals plus Smooth by Angle for plate edges.** Soft "pillow" shoulders in four reviews; kept for cylinders.
- **A void-black base slab** (read as a tray under floating plates) and **a near-black base foot** (v10: walls darker than tops; lost the calibration).
- **A fill light that also lit the backdrop**, and **the key on the far side** (every flat top mirrored the softbox).
- **Stretched-noise scratches and bump-driven backdrop grain** (scribbles, worm-shaped grain).

## Open items

- Creases are still grey by the metrics: 2.2 % of subject pixels under luma 12 against 7.6 %. The reference has a near-continuous black rim round the object that is only partly reproduced.
- The polymer is one matte grey with little satin variation across plates; the S-step has no parallel groove; scratches are sparse; backdrop grain std 13 against 15.
- The vent slots and a screw exist only with `--set cut_self=True` (v10 without the dark foot), not reviewed together. Next mechanism candidates: a facing-ratio dark outline term in the polymer, per-plate roughness variation, an inset groove along the S-step.
