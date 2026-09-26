# Review: v22

## Score: 8.0 / 10

## What works
- The toner clouds are mostly gone. Mid-scale std in the stem 1 core fell from 6.7 to 2.4. Core std is 9.2, and more of it is now in specks. The ink reads as worn toner, not marble.
- Pinhole dropout reads in the detail crop. The line screen and MIC dots survive at pixel level. The hairline comb past the glyph edge still echoes crop1_text.
- The blacks stay lifted and cool: core RGB 75/76/84 on a face of 196/196/199. The background is a neutral grey (163 at the top, 211 at the floor).
- The side face is dimmer (190–215, was 205–229), so it no longer outshines the front.

## Top problems (ranked by impact)

1. **The veil is too weak to see. The ink still sits on the surface.** Row 900, stem 1: the face goes 201→190 over about 12 px before the edge. That is a veil of about 5–8 levels, only 1–4 levels more than v21. The core edge is still a hard cut: 177→108→83 in 2 px. At full frame the logo looks like a decal on the plastic, not ink under it.
   *Fix:* raise the 1.8 mm veil to 15–18% darkening. Give the core its own 0.3 mm blur before the screen, so the edge ramps over 5–6 px. Keep the hairline comb on top.

2. **The side face is now glossy and rippled, not satin.** Around y 700–1000 there is a smeared reflection band with a wavy distortion. Values run from 242 at the arris down to 170 across 50 px. It reads as wet glass or chrome and fights the frosted front. There is still no print line inside the thickness.
   *Fix:* set side roughness to 0.35–0.45 and remove any bump or normal on that face. Add a 0.4 mm grey rim 1–2 mm in from the front arris.

3. **The wear is uniform salt, and the glyph contours are still clean vector.** The pinholes are all one size and evenly spread. Pale 3–8 mm patches are still visible in the logo crop. In ref4 the dropout clusters, the specks vary in size, and the outline itself breaks up.
   *Fix:* vary pinhole size from 0.05 to 0.4 mm and gate them with a 2–4 mm clumping mask. Erode the glyph contour with 0.1–0.3 mm noise so edges chip. Cut the remaining pale patches by a further 50%.

4. **The face texture is invisible.** Fine-scale std on the lower face is 0.82, the same as v21. The 2 mm roughness variation does not show under this light. The face reads as smooth board, not textured plastic.
   *Fix:* raise the roughness variation to ±0.12–0.15. Move the key 10–15° more grazing, or add a low rim light, so a sheen crosses the upper face and shows the grain.

## To reach 8.5+
A veil you can see, with a soft core edge, that puts the ink under the plastic (~+0.25). Satin sides with a print rim (~+0.15). Clumped, varied dropout and chipped contours (~+0.1). A sheen that shows the face grain (~+0.1).
