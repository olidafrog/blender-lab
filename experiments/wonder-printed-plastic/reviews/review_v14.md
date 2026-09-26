# Review: v14

## Score: 7.1 / 10

## What works
- The blur is tighter. The stem edge 10–90% is now ~8–9 px (v13: ~14 px). The right-side tail is gone.
- The MIC dots are off the ink. 0% yellow pixels on the stroke cores, ~2% on the face. The ink reads as one layer now.
- The ink tone is good: core 69/70/79. The blacks are lifted and cool, close to the Warp black.
- The face has grit now. There are ~700 dark speck px per 120k (v13: 11). High-pass std is 1.8 (v13: 1.0).
- The edge is no longer a white box. The side is cool (196/197/203) and slightly translucent. The chamfer catch light is crisp.

## Top problems (ranked by impact)

1. **The line screen is gone. It reads as noise.** In the detail crop the stroke interior is sandpaper grain with no direction. Core std went *up* to 15.7 (v13: 13.0). The teeth at the edges still show as a ragged sawtooth fringe. So you lost the ref1 signature and kept its artefact. In crop1_text the lines are clearly diagonal, even and low contrast.
   *Fix:* restore a clean `sin` line screen at one angle (~15–20°). Keep the finer pitch, but threshold smoothly (smoothstep width ~0.3) so the lines do not alias into noise. Cut the per-pixel grain on the ink to ~⅓. Target core std ~7–9, with a visible line structure at 100%.

2. **The logo still reads as camera defocus at full frame.** At 8–9 px it is better, but the glyphs still look soft next to the crisp slab edge. The "faint wide glow" does not read. The whole edge is one soft gaussian ramp.
   *Fix:* core blur ~4–5 px (≈0.8 mm), plus a 20–30 px halo at 6–10%. The eye should see a sharp-ish shape with bloom, not a soft shape.

3. **The speckle reads as terrazzo or granite.** It is evenly spread, similar in size and tinted yellow and grey. At full frame it looks like a speckled countertop more than toner dust under frost. There is still no low-frequency mottle: the face is smooth apart from the lighting gradient (190–205).
   *Fix:* halve the count. Vary the size (mostly sub-pixel, a few 2–3 px). Cluster it with a noise mask. Add ±4 levels of 5–15 mm cloudy mottle to albedo and roughness.

4. **The face is still glossy at the top.** Two diagonal softbox streaks cross the upper third (max 217 vs mean 205). That is polished acrylic. Satin frost scatters that highlight into a broad, dim sheen.
   *Fix:* raise the top-coat roughness by +0.1–0.15, or enlarge the key softbox and lower it 20%.

5. **The front has an inset frame.** The edge crop shows a lighter band and a line ~3 mm inside the edge. The face reads recessed, like a lid in a tray.
   *Fix:* make the front one continuous surface up to a single small chamfer. Let the print plane show as a faint grey line inside the translucent side.

## To reach 8.5+
Bring back a quiet, directional line screen that stays sharp over a smaller blur with a visible bloom. That is the Warp look, and it is worth ~0.8. Then swap the uniform glitter for clustered grit with mottle, flatten the gloss to satin, and remove the inset frame so the slab reads as one solid piece of frosted acrylic.
