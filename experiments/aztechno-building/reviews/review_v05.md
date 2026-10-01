# Review v05

1. **Score:** 5.7 / 10

2. **Targets**
- Red lit (217, 60, 69): hit
- Cream lit (235, 231, 204): hit. Cream shade (122, 123, 113): hit
- Yellow lit (240, 222, 144): hit. Orange lit (229, 134, 96): hit
- Glass upper (47, 72, 99): missed (B +17). p90 luma 89 vs 148: missed badly
- Glass lower (31, 15, 3): hit, at the limit (B −15)
- Sky top (148, 175, 210): hit. Sky low right (203, 227, 249): hit
- Pavement (186, 167, 160): missed (B +26)
- Brick neighbour (101, 55, 32): missed (R +18)
- Not scored: red shade B 26 vs 46, orange shade B 34 vs 56. Shadows lack blue.
- Layout IoU mean **0.333**, the same as a flat trace.

3. **What works**
- The lit paint colours match. The cream shade share (0.29 vs 0.30) shows that the sun and relief depth are right.
- The layout reads correctly: arches, oculus bands, piers, crest.

4. **Problems, ranked**
1. **Glass.** The upper panes are one flat blue. The lower glass reflects tan boxes and a sea-like blue band (y≈560–620). The big stepped windows have only horizontal gold lines, not a grid. Fix: show a cloudy HDRI to glossy rays only. Tilt each pane at random by ±0.3–0.8°. Put real brick-street geometry behind the camera. Target upper p90 luma 135–160.
2. **The red paint is mottled like marble.** It is the worst CG tell; the reference red is flat. Fix: keep albedo noise within ±3 luma. Put wear in a grime mask instead: AO in corners and streaks under sills.
3. **Focal points and silhouette.** The diamonds are tiny dark pyramids; they should be chrome and fill about 40% of the oculus. The roof tanks have domes; they should be flat-topped terracotta cylinders. The roof caps lack the red block and project too far. On the left corner the oculi are squares, a grey slab (x 80–120, y 640–770) has no material, and the sign is illegible. The right neighbour is a flat box; it needs recessed openings, a concrete frame and rebar.

5. **Research check**
The sun direction, hard shadows and shift-lens verticals agree. The glass contradicts "dark reflective curtain wall in gold frames". The perfectly even lines contradict "hand-painted". Check that the world light still reaches diffuse rays after the camera-only sky lift; the shadows are too warm.

6. **What 8.5 needs**
- Glass: HDRI reflections, tilted panes, a reflected street, full mullion grid.
- Flat paint with AO and streak grime.
- Chrome diamonds, flat-topped tanks, correct roof caps.
- Rebuild the left corner and right neighbour.
- Shadow blue up 15–25 levels.
