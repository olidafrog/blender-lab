# Review: v25

## Score: 8.2 / 10

## What works
- The screen is now quiet. Core fine std is 6.2 (was 10.3). In the detail crop the lines read as a soft toner texture, not loud twill. It is close to crop1_text.
- The floor wedge is gone. Floor at (290, 1100) is 160, in shadow. It was 193.
- The sheen strip gives the face a surface for the first time. It peaks at +9 to +14 over the face, about 80–110 px tall. It runs on a diagonal, y 560 at the left to y 723 at the right. It reads as a satin layer above the ink.
- The edge falloff is still good. Row 900: 200→194→180→156→105 over about 12 px.

## Top problems (ranked by impact)

1. **The blacks are still short.** Core median is 75 and the 5th percentile is 66. The target was 80–85. Contrast is 2.8:1 against a face of 209. The refs sit near 2.2–2.5:1. The glyphs still look like black paint seen through thin film, not toner under frosted plastic.
   *Fix:* add 6–8 levels of veil to the core only (the veil or black-lift node, not the exposure). Keep the white at 205–210.

2. **The side face is still a clean white extrusion.** The top of the side is 219/217/217, *brighter* than the front (209). Side std is 0.77, so there is no grain. The edge crop shows a hard dark arris line at the front edge (row 1000: 205→178→208→226) and a flat, lit side. It reads as painted MDF or a lightbox frame, not the same plastic as the face.
   *Fix:* drop the side albedo so the top sits at 195–200. Feed the face's mottle and grain into the side's roughness and colour. Replace the dark arris with a 0.5 mm bevel that catches a soft highlight. Add a faint grey print rim 1–2 mm in from the front edge.

3. **The face grain still does not read at full frame.** High-pass std on the face is 0.76. The only visible texture is the sparse white specks. At logo-crop scale they read as dust or salt on top, not as pinholes in the ink.
   *Fix:* add a 0.5–1.5 mm albedo mottle at ±2–3 levels to the face base colour, not only to roughness. Make the pinholes grey (inside the ink, about 40 levels above the core), not near-white.

4. **The contours are still clean vector.** The coarse erosion does not show at crop scale. The rounded corners are perfect. The Defying Decay refs have ragged, chipped toner edges.
   *Fix:* push the low-frequency erosion to 0.5–0.8 mm on a 3–5 mm noise, thresholded so it bites 2–4 notches into each glyph edge. Make the pinholes clump near the edges.

5. **The sheen band wobbles.** It curves down to the right, like a reflection on a warped sheet. It is acceptable, but it pulls the eye above the logo.
   *Fix:* make the strip light wider and softer, and flatten the bump normal at low frequency so the band stays straight.

## To reach 8.5+
Core at 80–85 (+0.15). A side face that matches the front in tone and grain, with a bevel highlight instead of the dark arris (+0.1). Face mottle and edge erosion that read at full frame (+0.1).
