# Review v16

## 1. Score: 6.3 / 10

## 2. Targets

- Hit: red lit 223,62,73; cream lit 238,238,214; cream shade 109,110,98 (borderline); yellow lit 242,229,150; orange lit 234,136,95; glass upper p90 147; glass lower 40,28,19; sky top 149,175,210; sky low right 203,228,249.
- **Missed:** glass upper 69,81,106 (B +24); pavement 181,162,150 (B +16); brick neighbour 58,50,55 (R −25).
- Layout mean IoU **0.326**, the same as a flat trace.
- Also off: every shade blue channel is 14–24 low; cream shade share 0.17 against 0.30.

## 3. What works

- All lit paint colours and the sky gradient hit.
- The layout reads right: oculus tower, twin arches, stepped notches, orange columns.
- Verticals are parallel, and shadows fall left of proud parts.

## 4. Problems, ranked

1. **Glass and oculi (whole facade).** The oculi are flat near-black discs. The reference shows sky-lit glass. The large windows show a random per-pane tint checkerboard (upper left of both arches). Fix: give the oculi the curtain-wall glass. Remove the per-pane colour jitter. Tilt each pane's normal by 0.2–0.5° so the reflection breaks at mullions. Pull upper glass within 15 of 60,67,82.
2. **Shadow colour and relief depth (all mouldings).** Shadows read warm and muddy, and the mouldings look shallow. Do not just raise a value: check that the world that *lights* the scene is a cool, real sky, not only the camera-lifted one. Aim for a cream shade/lit ratio of 0.45–0.50. Bring cream bands and arches to 0.2–0.3 m proud, so their returns cast 4–8 px shadows.
3. **Ground and context read as a model.** The pavement is a clean slab and the street a uniform tile. No kerb, rubble or grime. The left is a grey void, not brick houses. The right neighbour is pale and flat, with no slab edges or deep openings. A tall beige wall stands where the reference has sky and rebar. Fix: add a 0.15 m kerb, displaced setts, stains and a 0.4 m splash band at the wall base. Model the neighbour as projecting slabs with recessed openings. Delete the beige wall.

## 5. Research check

The shift lens, the front-right sun and the lifted sky agree. The 0.1–0.3 m relief does not: the shade share says it reads shallower.

## 6. What 8.5 needs

- Reflective oculi, and continuous pane reflections.
- Cool shadow fill and deeper relief, with the shade targets met.
- Roofline: separate yellow caps on red plinths, not one wide slab over the left tower.
- A worn kerb, street and wall base, and real neighbours on both sides.
- A left corner bay that curves into the sign fascia.
