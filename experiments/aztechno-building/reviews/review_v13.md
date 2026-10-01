# Review v13

1. **Score:** 6.4 / 10

2. **Targets**
- Hit: red lit 224/62/72, cream lit 239/239/214, yellow lit 243/229/149, orange lit 234/136/95, glass upper 59/71/94, sky top 149/175/210, sky low right 203/228/249.
- Just hit (one channel 15 off): cream shade 125/127/115, glass lower 44/31/19.
- **Missed:** glass p90 luma 99.7 (target 148). Pavement 189/172/166, pink (blue 32 high). Brick neighbour 59/49/51 (red 24 low).
- Layout mean IoU is **0.331**, no better than a flat trace.

3. **What works**
- All the lit paint colours hit, and so does the sky.
- The layout reads at once: oculi bands, stepped glass heads, twin-ring tower, hexagon shutters.

4. **Problems, ranked**
1. **The glass and the diamonds look dead.** The upper panes are flat blue-grey. The corner tower windows (x 215–275 and 1175–1240) are grey slabs with no mullions. The diamonds are matte grey, but the photo's are bright chrome. Likely cause: the sky is lifted for camera rays only. Fix: let glossy rays see the lifted sky too. Tilt each pane at random by 0.3–0.8°. Add mullions to the tower glass. Make the diamonds faceted metal (roughness ≤0.05) with peak luma above 220.
2. **The shadows are too warm and too weak.** Each shade row is 12–22 levels low in blue. Shadow cover is low: cream 0.21 (target 0.30), red 0.01 (target 0.03). Raise the sky light against the sun until each shade blue is within 10 of its target. Set the relief 0.15–0.3 m proud so the cast shadows lengthen.
3. **The left corner and the surfaces look CG.** An untextured grey box sits at x 30–110, y 330–700. The cream side panel has square windows; the photo has round oculi. The sign is scattered, unreadable letters. The red paint has blotchy noise, not wear. The pavement is pink and spotless. Fix: model the angled left corner from the oblique photos. Make the sign one curved text object. Swap the blotches for dirt streaks under the sills. Make the pavement cracked, dirty grey-brown concrete.

5. **Research check**
- Agrees: shadows fall to the left, verticals are parallel, scale is right.
- Contradicted: "dark reflective curtain wall". The glass does not reflect enough.
- Contradicted: "thin hand-painted lines". They read as moulding steps.
- The roof caps are plain yellow. The photo's caps sit on red bases.

6. **What 8.5 needs**
- Lifted sky in reflections, tilted panes, chrome diamonds.
- Bluer, stronger sky light in the shadows, and deeper relief.
- A modelled left corner and a readable sign.
- Dirt streaks, a concrete pavement, a lighter brick neighbour.
- Two-tone roof caps. Layout IoU of 0.40 or more: correct the orange and cream band widths.
