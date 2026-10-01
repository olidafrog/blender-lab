# Review v06

## 1. Score: 5.3 / 10

## 2. Targets

- Red, cream, yellow and orange lit; cream shade (119, 120, 108): all hit.
- Glass upper (63, 81, 95): hit. p90 luma 99 against 148: **missed**.
- Glass lower (12, 12, 8): **missed** (R 17 low).
- Sky top (148, 175, 210) and sky low right (203, 227, 249): hit.
- Pavement (187, 168, 163): **missed** (too pink and bright).
- Brick neighbour (104, 58, 35): **missed** (too orange).
- Layout IoU mean **0.339**, barely above a flat trace. Yellow is 0.17 and orange 0.21.

## 3. What works

- The lit paint colours and the sky are on target.
- The layout reads correctly, from the arcades to the shutters.
- The framing and sun direction are right.

## 4. Problems, ranked

1. **Glass.** The upper panes are flat grey with no sky in them. The lower panes are near-black and hold grey proxy blocks that read as cardboard. Fix: apply the sky lift to `Is Camera OR Is Glossy`. Replace the proxy blocks with a textured backplate of brick buildings. Tilt each pane at random by 0.2–0.5°. Target an upper p90 luma of 135–155.
2. **Clean surfaces, shallow relief.** The paint is uniform with a procedural mottle. The edges are razor sharp, with no grime or streaks. The cream shade share is 0.21 against 0.30. Red shade drifts to brown (138, 62, 20) against (158, 56, 46). Fix: bevel the edges 1–2 cm. Add AO-masked corner grime and drip streaks, 5–10 % darker. Make the relief 0.2–0.3 m proud. Lower the pavement albedo to cut warm bounce.
3. **Signature forms.** The diamonds are tiny black "V" marks; they should be chrome gems about a third of the oculus width. The tanks are pink capsules; they should be flat-topped terracotta cylinders. The roof caps are thin yellow shelves; they should be stacked red-and-yellow caps on piers above a stepped parapet. The left corner has a grey box instead of round medallions on cream. The right neighbour is clean tiled brick instead of an unfinished brick-and-concrete frame.

## 5. Research check

The sun, the parallel verticals and the scale agree. The glass does not read as dark reflective curtain wall. The shadows are 3–5 px wide where about 8 px is expected, so the relief does not read as 0.1–0.3 m proud.

## 6. What 8.5 needs

- Glossy rays see the lifted sky, a street backplate in the reflections, and tilted panes.
- Edge bevels, grime and streaks, and deeper relief.
- Chrome diamonds, flat-topped tanks, correct roof caps and the left-corner medallions.
- A dirtier pavement and an unfinished neighbour.
