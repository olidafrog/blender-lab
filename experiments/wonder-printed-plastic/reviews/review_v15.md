# Review: v15

## Score: 7.2 / 10

## What works
- The supersampling helps. The render is clean, with no fireflies and no aliasing on the slab silhouette.
- The blur is tighter. The stem edge 10–90% is now ~6–7 px (row 800: 179 → 60 over ~9 px). The glyphs read as a print at full frame, not as a camera defocus.
- The ink is quieter. Core std is 6.8 (v14: 15.7), which hits the 7–9 target.
- The gloss streaks are gone. The face is a soft satin gradient (211 top-left → 186 bottom-right).
- The inset frame is gone. The edge crop shows one front plane, a crisp top arris and a clean side.

## Top problems (ranked by impact)

1. **The line screen still does not read as lines.** In the detail crop, the stroke interior is a woven-fabric texture, like canvas or denim. The edges are a hairy sawtooth fringe, with teeth ~6–10 px long. In crop1_text the lines are straight, even and parallel, and the edge is clean where they stop. You have the artefact without the signature.
   *Fix:* use one clean `sin` screen at ~15°. Threshold with a smoothstep ~0.3 wide against the *blurred* coverage. Remove the second frequency or the noise that makes the weave. Clamp the line amplitude to 0 where coverage < 0.15 so the fringe goes away. Target: lines you can count at 100%.

2. **The blacks have dropped.** The core is 48/50/58 (v14: 69/70/79). That is ink on top of the plastic, not under frost. The refs sit at ~60–75 with a visible veil.
   *Fix:* raise the black lift so the core lands at ~65–72 and keeps its cool tint. Add a ~3% veil from the top surface.

3. **The halo does not read.** Outside the stroke the face goes 197 → 191 → 179 and then drops. The wide faint bloom does not show at full frame.
   *Fix:* raise the halo to 8–12% over 25–40 px, or add a second, wider 80 px layer at 3–4%.

4. **There is no mottle.** The low-frequency std is 0.96 levels (±2.4). You cannot see it. The face looks like a perfect product-render plastic. ref3 and ref4 feel cloudy and uneven.
   *Fix:* ±5–7 levels of mottle at 10–30 mm on albedo, plus ±0.05 on roughness. Tint it slightly (warmer in some patches, cooler in others).

5. **The specks read as dust on a clean surface.** They are clustered now, but they sit only in the upper-left and upper-right areas, as tidy grey sprinkles. They do not look embedded, and there is none of the toner grain *in* the ink.
   *Fix:* put 30–50% of the specks under the surface, with the same blur as the ink. Add fine toner dropout (lighter pinholes) to the ink. Spread the clusters across the whole face.

6. **The side is dead.** The side face is flat pale grey. It has no internal depth, and you cannot see the print plane.
   *Fix:* add a faint darker line at the print depth. Add a little transmission falloff so the side darkens towards the back.

## To reach 8.5+
Get a true, countable line screen with a clean edge (~+0.6). Lift the blacks back into the veil and make the bloom visible (~+0.4). Then add real cloudy mottle and embedded grit, so the slab stops looking like a spotless CG product shot and starts feeling like a used object printed under frost (~+0.4).
