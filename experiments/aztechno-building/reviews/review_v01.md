# Review v01 — aztechno-building

1. **Score:** 4.4 / 10

2. **Targets** (render vs ref)
- red lit (215,55,65) vs (230,65,70): hit, R at limit
- cream lit, cream shade, yellow lit, orange lit: hit
- glass upper (49,73,100) vs (60,67,82): missed, too blue
- glass upper p90 luma 91 vs 148: missed
- glass lower (31,15,4) vs (29,22,18): hit, B at limit
- sky top, sky low right, pavement: hit
- brick neighbour (100,55,32) vs (83,56,48): missed
- Layout IoU mean 0.346, barely above a flat trace (0.33). Yellow 0.12.

3. **What works**
- Paint albedos and sky match the targets.
- The sun is front-right: shadows fall left.
- The bay rhythm is right.

4. **Problems, ranked**

1. **Whole facade: flat slabs instead of stepped plaster mouldings.** The ref stacks 3–4 soft-edged layers per band; the render has single knife-edged boxes. The shadow beside the central plate is 2–3 px (about 0.07 m); the ref needs 6–10 px. Cream shade share is 0.20 (ref 0.30); red shade share is 0.01 (ref 0.03). The painted orange and yellow lines are missing. The upper bands should be yellow, not cream. Fix: sweep a layered profile along each moulding path, 0.15–0.30 m deep, with 1–2 cm bevels. Add inset strips for the painted lines.
2. **Uniform CG materials.** The paint has no variation or grime. The pavement repeats one tile. The brick neighbour is a tiled box, too orange. Fix: vary paint value by ±4% and roughness from 0.5 to 0.8. Add AO-masked dirt under the mouldings. Model irregular slabs with a kerb. Build the neighbour as an RC frame with brick infill and rebar.
3. **Fake glass reflections.** The upper glass is flat navy, not bright sky. The lower bays show horizontal bands from a stretched HDRI, not the street opposite. The diamonds are dark triangles instead of chrome. Fix: add reflection-only street geometry and a clouded sky. Tilt the panes 0.5–1°. Make the diamonds faceted metal, 1.2–1.5 m wide.

**Modelling errors:**
- The corner towers need yellow frames and near-full-width pointed windows.
- The left wing needs a stepped red and orange corner.
- Missing: the central octagon frame, ring stripes, orange entrance portal.

5. **Research check:** The sun and verticals agree. The relief contradicts the 0.1–0.3 m depth: it reads as about 0.07 m. The hand-painted lines are absent. The glass is navy, not dark reflective.

6. **What 8.5 needs**
- Layered mouldings at the true depth, with painted lines.
- Corner towers, left wing and central octagon rebuilt to match the ref.
- Street and cloud reflections in the glass, and chrome diamonds.
- Weathering on the paint, pavement and brick, and a real RC-frame neighbour.
