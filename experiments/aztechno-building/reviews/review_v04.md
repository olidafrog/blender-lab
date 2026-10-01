# Review v04

## 1. Score: 5.7 / 10

## 2. Targets

- Hit: red lit 217,55,64. Cream lit 236,231,204. Cream shade 119,121,111. Yellow lit 240,223,143. Orange lit 230,133,92. Glass lower 31,15,3. Sky top 148,175,210. Sky low right 203,227,249.
- Missed: glass upper 49,72,99 (blue +17). Glass upper p90 88.5 (target 148). Pavement 186,167,160. Brick neighbour 101,55,32.
- Layout IoU mean 0.337, level with a flat trace.

## 3. What works

- The lit paint colours, the sky and the exposure are right.
- The symmetry, the arches with their oculi and the octagonal oculus frame with its crest all read correctly.

## 4. Problems, ranked

1. **Every surface is CG-clean.** The paint is uniform and the edges are razor sharp. There is no dust or streaking. The yellow bands have no hand-painted orange lines. Fix: bevel the moulding edges 1–2 cm. Add albedo noise (±3–5 % value) and AO-driven grime in the crevices. Add vertical streaks under the sills. Add 3–5 cm orange lines on the yellow and cream bands as edge-offset strips.
2. **The glass is dead.** The upper glass is flat navy. The tall central panes show stepped horizontal bands, and the lower panes reflect untextured brown boxes. Apply the sky lift to glossy rays as well as camera rays. Tilt each pane 0.2–0.5° at random. Replace the proxy boxes with a textured street plate that only reflections see.
3. **Modelling errors.** The roof tanks have dome tops; the reference has taller flat-topped cylinders. The tower caps are oversized slabs that overhang too far; the reference has small plinths. The diamonds are tiny triangles; the reference has mirror gems about 40 % of the oculus width. The left tower has square windows where the reference has round oculi. The neighbours are flat tiled boxes with no concrete frame, voids or rebar.

## 5. Research check

- The sun direction, the shadows to the left, the parallel verticals and the scale agree.
- The image contradicts "relief 0.1–0.3 m proud". The yellow and orange shade shares are 0.28 and 0.33 (reference 0.17), so the caps and rails project too far or the sun is below 35°.
- The shadows are warm and saturated: the shade blue channels are 21–68 (reference 46–85). The sky fill is too weak.

## 6. What 8.5 needs

- Bevels, grime, streaks and painted lines.
- Sky lift on glossy rays, pane tilt and a reflection plate. Upper glass p90 140–155.
- Flat-topped tanks, small caps, large mirror diamonds and round oculi on the left tower.
- Yellow and orange shade shares of 0.15–0.20, and bluer fill in the shadows.
- Unfinished-brick neighbours. Pavement and brick in range.
