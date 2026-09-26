# Review — v01_final

## Score: 4.6 / 10

## What works
- Clean studio setup. Light neutral grey sweep, soft contact shadow, sensible 3/4 angle.
- The slab reads as a thick-ish sheet with a believable bevel line on the right and bottom edges.
- Blacks are lifted to a mid grey (~0.35–0.4). That direction is right.

## Top problems (ranked by impact)

1. **The ink is just Gaussian-blurred. It has no print structure.** In both crops the glyph edges are one uniform ~15–20 px falloff all round. There is no line screen, no toner edge and nothing sharp stays behind. In ref1 the halftone lines stay crisp *through* the blur. Here it reads as "blurred PNG", not "ink under plastic".
   *Fix:* add a per-ink line screen (rotated UV, `sin(u·freq)` thresholded against the blurred coverage, ~45°, 100–150 lpi at A5 scale). Keep a sharp core and blur only a soft halo (mix a sharp and a blurred mask at about 70/30).

2. **The mottle inside the ink is the wrong kind of texture.** v01_crop_logo shows low-frequency cloudy blotches (~40–80 px) inside the bars. They look like dirty smudges or a Noise texture at low scale, not toner. The fine grain is there but weak. It sits almost only in the ink, and the white field is nearly clean.
   *Fix:* drop the low-frequency noise amplitude by about 70%. Add high-frequency toner speckle thresholded into coverage (dropout at the edges). Put a separate fine grain/fibre layer on the *slab surface* (base colour ±3%, roughness 0.35–0.6 variation) so grain sits on top of everything, logo and blank areas alike.

3. **The slab reads as white card or opaque Corian, not translucent frosted plastic.** The face is a flat, near-blown white with almost no tonal change. There is no sense of depth, no subsurface glow at the edges and no cool tint.
   *Fix:* pull the face white down to ~0.8 and tint it cool (slightly blue-green, like ref3/4). Give the edges real transmission/SSS so they glow a little and look thicker than the face. Add a faint backer shadow or a gap between the print layer and the top surface.

4. **The lighting is flat and gives no tactility.** There is one broad soft source. No satin sheen crosses the surface, so you can't read roughness or texture.
   *Fix:* add a large, grazing strip light from the upper left to throw a soft specular gradient across the face (coat roughness 0.4–0.5). Add a rim light on the right edge to show thickness. Add a bump/normal map from the grain at low strength so the sheen breaks up.

5. **There is no second tonal note.** The ink is neutral grey on neutral white. The references get their feel from the cool-white/warm-black shift and a slight colour cast.
   *Fix:* push the ink towards a warm or blue-black (~0.12–0.18 linear before the veil) and cool the whites. Optionally add yellow MIC dots at ~1 mm pitch and ~30% opacity.

## To reach 8.5+
The ink needs to look *printed*: a line screen, toner speckle and edges that are sharp at the core and soft only at the halo. The plastic needs to look *present*: visible surface grain, a satin specular sweep, cool translucent edges and a readable gap between print and surface. Fix problems 1–4 and this moves to ~7. Getting the grain-on-top and the sheen right under a grazing light gets it to ship quality.
