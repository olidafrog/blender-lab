# Review v15

1. **Score:** 6.4 / 10

2. **Targets**
- red lit (223, 63, 74): hit
- cream lit (238, 238, 214): hit
- cream shade (110, 111, 98): hit (B −12), but shade share is 0.18 (ref 0.30)
- yellow lit (242, 229, 150): hit
- orange lit (234, 136, 95): hit
- glass upper (69, 82, 106): **missed** (B +24, G +15). p90 luma 147.6: hit
- glass lower (40, 29, 19): hit
- sky top (149, 175, 210): hit. Sky low right (203, 228, 249): hit
- pavement (188, 171, 167): **missed** (+18/+20/+33, pink and bright)
- brick neighbour (58, 50, 55): **missed** (R −25, grey-violet)
- Layout IoU mean **0.325**, under the flat-trace 0.33. Orange 0.195 and yellow 0.158 are the weak classes.

3. **What works**
- The paint colours in lit areas all hit, and the sky gradient matches.
- The lower curtain wall has gold mullions and town reflections that hold up side by side.
- The massing, cream oculus bands, orange piers and stepped arch heads read correctly at full frame.

4. **Problems, ranked**
1. **The centre tower oculi (focal point).** The rings stand out as deep tubes. The diamonds are small and dull grey, and each has a dark shadow copy under it, so it reads as two diamonds. Fix: put the disc glass almost flush (recess ≤ 0.05 m). Keep the ring proud by 0.15–0.20 m. Make the yellow band the widest ring, as in the close-up. Use a faceted chrome diamond (metallic 1, roughness ≤ 0.05) at 40–45 % of the disc diameter (now about 30 %). The transom lights above the octagon are glass in the reference, not solid cream.
2. **Glass is a blue checkerboard.** The upper bays, the upper part of the arched bays and the left corner tower show a pane-by-pane tint mosaic, and the tint is too blue. In the reference the reflection runs across all panes as one dark grey-bronze image (the mountain shows in the left corner). Fix: cut the per-pane variation to ≤ ±3 % value with no hue shift. Use small normal tilts, not albedo or tint changes. Use a neutral grey-bronze tint so the mean lands at (60, 67, 82).
3. **The ground plane and context read as CG.** The pavement is a clean pink-grey slab with ruled diagonal joints. The curb is a flat white strip, and the street is a repeating mesh pattern. The shop interior is a set of flat colour blocks, and the SNACK PIQUIN sign is a crisp print, where the real one is a faded tarp. The neighbour's slab ledges cast no shadows. Fix: use a warm concrete albedo (pavement target 170, 151, 134) with patch decals and grime at the base of the walls. Give the curb a real stone profile with chips. Use a paver texture that does not tile visibly. Use red-brown brick with recessed mortar. The darker, warmer pavement also cuts the pink bounce into the shadows.

5. **Research check:** The sun direction agrees with the research. The shadows contradict it: they are too warm. Measured shade blue is low on every paint (red B 22 vs 46, yellow 67 vs 85, orange 42 vs 56), so the skylight fill is missing. Mouldings that are 0.1–0.3 m proud should leave more cream in shade (0.30 in the reference). Here the relief reads shallow and evenly lit.

6. **What 8.5 needs**
- Flush oculus glass and chrome diamonds at the right size.
- One coherent, neutral glass reflection with no tint mosaic.
- Cool, neutral shadow fill: keep the diffuse sky blue and lower the warm ground bounce.
- A worn pavement, curb, street and neighbour that hit their targets.
- Better orange and yellow line placement, to bring the layout IoU above 0.40.
