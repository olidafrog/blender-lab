# Review — v02

1. **Score:** 5.6 / 10

2. **Targets**
- Background: #000000–#030000. **Hit.**
- Deep teal #012437–#085c62: absent; the "teal" is muddy green #608267–#749775. **Missed.**
- Sage #7c9f93: #6b9472. **Hit (marginal).**
- Cream #e7c69d: #f3cf89. **Hit.**
- Amber #fdbb55: #f7cb89, washed. **Missed.**
- Orange #fca321: absent. **Missed.**
- Hot pink #fe6f6b: #fb888a, pastel salmon. **Missed.**
- Opal blue skin #9fb8b7: none; only a cyan rim on the cut-outs. **Missed.**
- Micro-type 1–1.5% cap height: top band 0.6%. The other blocks are near-invisible. **Missed.**

3. **What works**
- The right-half gradient, cream → peach → salmon, is smooth and backlit.
- Blur by depth works: the upper gear is crisp, and the dumbbell and blocks melt.
- The black background is clean, and the brackets and rivets give the industrial frame.

4. **Problems, ranked**
1. **The left 40% and the top band read as brown tinted glass, not milky resin** (#472723, #663e2e). The plate only transmits the backlight, so it goes dark where nothing lights it from behind. Fix: give the plate its own scatter. Use subsurface or volume with a near-white albedo (0.85–0.95), dense enough that front light lifts it to #b0a8a0–#d8d0c8 over black. Add a large, soft, cool front key so the skin reads blue-white. This also delivers the opal blue.
2. **The "Wonder" logotype is a flat grey decal** (#424048, bottom left). It has no edge highlight or relief, and it fades out mid-word. The micro-type block at bottom right and the vertical line are lost in the pink. Fix: model the type as raised geometry, 0.3–0.5 mm, in the plate material. Light it with a grazing strip for a top-edge highlight and a soft shadow. Set micro-type to 1–1.5% of frame height.
3. **It reads as CG.** The plate is flat and spotless. The only highlight is a hard vertical bar with a cross (x≈1080), which reads as a light leak. The crops show blotchy denoiser smear. Fix: add a slight surface warp and micro-bump (scratches, smudges). Add 2–3 small wet specular pools from an off-axis strip light. Raise samples, or denoise with albedo and normal passes. Add grain (σ 1–2%).

5. **Research check**
- Opalescence (blue skin, warm core): contradicted. There is no cool skin.
- Frosted plate: contradicted on the left, where the plate is clear and tinted.
- Blur grows with depth: agrees.
- Raised type read by highlight and shadow: the top band agrees. The logotype contradicts it.

6. **What 8.5 needs**
- Self-scatter milk plus a cool front key.
- Orange to #fca321, pink to #fe6f6b, and a deep teal stop.
- Raised, lit geometry for the logotype and micro-type.
- Surface imperfections, wet highlights and grain, with no denoise smear.
