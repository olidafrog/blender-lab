# Review v02 — aztechno-building

## 1. Score: 5.2 / 10

## 2. Targets

- Red lit (216,55,64), cream lit (236,233,207), cream shade (121,121,112), yellow lit (240,225,143), orange lit (229,131,88): all hit.
- Glass upper (51,71,97): hit, at the edge. **p90 luma 89.5 vs 148: missed.**
- Glass lower (32,14,3): hit, at the edge.
- Sky top (148,175,210), sky low right (203,227,249), pavement (179,155,137): hit.
- **Brick neighbour (100,55,31): missed**, too orange.
- Layout mean IoU **0.332**, equal to a flat trace.

## 3. What works

- The paint palette is correct.
- The layout reads right at thumbnail size.
- The sky and exposure match.

## 4. Problems, ranked

1. **The frame reads as a clean SketchUp model.** Each colour is one flat value, with no stains, chips or bevel highlights. The pavement is a repeating tile; the reference has cracked, patched slabs and a broken kerb. Fix: add paint value noise (±3–6 %, 1–3 m scale), AO/pointiness dirt under every ledge and at the base, and 1–2 cm bevels. Model the pavement as irregular slabs with cracks and an uneven kerb.
2. **The glass is a dark, seamless mirror.** The lower panes reflect one box city and a horizon band straight across the mullions. Fix: put the real street behind the camera (brick houses, pale sky, mountain) into reflections only. Tilt each pane at random by 0.2–0.5° so reflections break at the mullions. Brighten the sky seen by the upper glass until p90 is 135–160.
3. **Hero details are wrong or missing.**
   - Left wing: stacked boxes. The reference has a chamfered corner, a glass curtain, a cream oculus strip, the "CRUCERO DEL SUR" sign and the orange portal.
   - Corner towers: cream slabs with a slot. They need a wider arched window in layered yellow and cream frames on red.
   - Roof tanks: domed. They should be flat-topped cylinders.
   - Diamonds: tiny dark pyramids. They should be large chrome gems, about 35 % of the oculus.
   - Oculi: deep drums. They should be shallow rings.

## 5. Research check

- Sun from front-right: agrees.
- Relief 0.1–0.3 m: contradicted. Cast shadows are 1–3 px, and red shade share is 0.01 vs 0.03. The reference shows 6–12 px.
- Gold frames on dark glass and the lifted sky: both agree.

## 6. What 8.5 needs

- Irregular pavement, plus dirt and wear on the paint.
- Real reflected surroundings, with a random tilt on each pane.
- A remodelled left wing, corner towers, tanks and diamonds.
- Mouldings deep enough to cast 6–12 px shadows.
- The right neighbour as an unfinished brick frame with openings and rebar, in the right colour.
