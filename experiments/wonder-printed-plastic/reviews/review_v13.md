# Review: v13

## Score: 6.8 / 10

## What works
- The pre-blur is the right technique. The lines stay sharp across the soft edge and taper into it. This is the ref1 "Warp" signature, and it reads now.
- The glyphs finally sit *in* something. They do not look like a sticker any more.
- The ink tone holds. Cores are ~62 L with a cool bias (61/62/70). The blacks are lifted.
- MIC dots now show at 100%. About 1.3% of face pixels read yellow.
- The lower face is brighter: ~202 (v12 was 191).

## Top problems (ranked by impact)

1. **The blur is too strong for "slightly diffused".** The 10–90% edge is ~14 px (≈2.5 mm at ~5.7 px/mm), with a long tail on the right side of each stroke. That is ~13% of the stroke width. At full frame the logo looks like camera defocus, not ink seen through frost. In ref1 the hero black type ("Darkstepper") is almost crisp with a small bloom. Only the background layer gets the heavy blur.
   *Fix:* halve the core blur to ~1–1.2 mm (6–7 px). Add a faint wide halo (~3 mm, 8–10% opacity) for depth. Keep the 2.5 mm blur for a future back layer.

2. **The screen is still coarse and loud.** The core std is 13.0, the same as v12. The fix to cut contrast was not applied. At the blurred edges the tapering lines become long spikes. The edges read as a hairbrush or velcro, not a gradient. The detail crop shows twill again.
   *Fix:* cut the line amplitude to ~40% of now. Raise the frequency ~1.5–2×. With a finer pitch, the tapered teeth become short and read as tone, as in crop1_head.

3. **The yellow dots sit on top of the ink.** On the strokes they read as gold glitter or sequins. Yellow toner under black does not show.
   *Fix:* multiply the MIC layer by (1 − ink coverage), or composite it under the ink. Drop the white specks on the ink too.

4. **The face is still clean.** High-pass mean is 1.0. Low-frequency range is 199–207, and that includes the lighting gradient. I count 11 dark specks in 60k px. The diagonal softbox streak across the upper face reads as glossy acrylic, not satin frost.
   *Fix:* ±5 levels of 5–10 mm mottle on albedo and roughness. Triple the dark speckle. Raise the face roughness ~0.1 so the streak widens and flattens.

5. **The slab reads as a white box or book.** The side is flat, opaque and near-clipped. A dark seam line runs under a lip on the front face. There is no translucency and no internal print plane in the edge.
   *Fix:* give the sides transmission with a faint cool tint and a thin chamfer catch light. Remove the lip, or make it a soft ~10-level grey line.

## To reach 8.5+
Pull the blur back to "slight" and make the screen fine and quiet. That is the whole logo read, and it should reach ~7.5. Take the dots off the ink and grit the face. Then make the edge look like solid frosted acrylic, not a case.
