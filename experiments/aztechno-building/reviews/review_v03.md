# Review v03 — aztechno-building

1. **Score:** 5.3 / 10

2. **Targets**
- Red lit (217,55,64) hit. Cream lit (236,232,206) hit. Cream shade (120,121,111) hit.
- Yellow lit (240,224,143) hit. Orange lit (229,131,89) hit.
- Glass upper (51,70,96) hit; p90 luma 89 vs 148 **missed**.
- Glass lower (32,14,3) hit (B at the limit).
- Sky top (148,175,210) hit. Sky low right (203,227,249) hit.
- Pavement (185,166,160) **missed**: too pink.
- Brick neighbour (101,55,32) **missed**.
- Layout mean IoU **0.323**, below the flat-trace 0.33. Yellow (0.12) and orange (0.22) are weakest.

3. **What works**
- Every lit paint colour is calibrated.
- The central axis reads right: oculus arches, orange pilasters with square insets, stepped window heads, the octagon.
- The ground-floor rhythm of shutters, striped skirts and hexagons matches.

4. **Problems, ranked**
1. **The outer thirds are the wrong building.** The top corner towers are cream masses with 20 px slots. The reference has red towers, yellow frames and 60 px windows. The left return is loose boxes over a grey void. It lacks the red chamfered corner at y≈290, the glass return, and the red overhang with sign and orange door. Fix: model the left corner as one massing from the Mohl and Nio photos.
2. **The glass reflects a CG backdrop.** Lower panes show flat horizontal bands. Upper glass is too dark. Tall panes lack vertical mullions. Value tweaks will not fix this. Fix: put a brick town and pale sky behind the camera, visible to glossy rays only (cards or an HDRI with a town horizon). Target upper p90 luma 135–160.
3. **Too clean and too perfect.** Paint is uniform, with no streaks or dust. Yellow bands stick out like shelves. Oculus rings are thick tori. The diamonds are tiny dark triangles; the reference has large chrome gems. The tanks are pink capsules, not flat-topped terracotta cylinders. Fix: AO-masked grime, streaks under ledges, 3–8% value noise, 5–15 mm bevels, flat stepped rings, mirror-metal gems, bands 0.10–0.20 m proud.

5. **Research check**
- Parallel verticals and the lifted sky agree.
- Sun front-right: weak. Red shade share is 0.01 against 0.03. The close-up shows hard shadows cast left onto red; the render's fall mostly down.
- "Dark reflective glass" contradicted: it reflects nothing real.
- Yellow bands look over 0.3 m proud.

6. **What 8.5 needs**
- Remodel the corner towers and the left return, with the sign overhang.
- A real reflected town and sky in the glass.
- Grime, bevels, flat rings, chrome gems, cylinder tanks.
- Swing the sun so proud elements cast shadows to the left.
- A concrete-frame brick neighbour, toned to (83,56,48).
- Layout IoU of 0.45 or more.
