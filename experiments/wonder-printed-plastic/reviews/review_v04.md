# Review — v04

## Score: 5.7 / 10

## What works
- Real progress since v01. The cloudy low-frequency mottle is gone. Glyph edges now have a sharp core: about 6 px from face to ink at 1600 px, against 15–20 px in v01.
- A diagonal line screen is now in the ink. You can see it in the logo crop.
- The face white is down to ~211 sRGB with a slight cool bias (B +5). Blacks are lifted to ~98–140. The tonal direction is right.
- The right edge now reads as clear acrylic. It has a thin bright rim and a visible thickness band. The contact shadow is soft and believable.

## Top problems (ranked by impact)

1. **The logo no longer sits *under* the plastic.** v01 was all blur. v04 has swung too far the other way. The ink is crisp and flat, like a sticker on the top face. It has no halo, no veil and no depth. The brief asks for "slightly diffused by the plastic". The refs have a sharp screen *plus* a soft bloom around every shape.
   *Fix:* add a blurred copy of the mask (radius ~1–1.5 mm at A5, 8–12 px here) at 25–35% under the sharp core. Or lift the print plane 0.5–1 mm below a roughness-0.35 transmission sheet.

2. **The line screen reads as felt or noise, not print.** In the detail crop the lines are low-contrast and broken up by random speckle. You can't count them. In ref crop1 the lines are regular and high-contrast inside the ink, and they stay crisp.
   *Fix:* raise the screen contrast (threshold harder: 0.35 → 0.65 smoothstep). Cut the speckle amplitude by about 50% and apply it only as dropout at the ink edges. Fix the frequency so the lines are 3–4 px apart in the final render.

3. **The slab disappears into the background.** Face ~211, sweep ~207. With no specular, the object has no presence, and the surface texture can't be read.
   *Fix:* add a large grazing strip light from the upper left for a satin sweep (coat roughness 0.45). Drop the sweep to ~185–190, or lift the face with a key light.

4. **The surface grain is the wrong texture.** The edge crop shows a regular diagonal twill, like canvas or fabric. Frosted acrylic has isotropic micro-grain.
   *Fix:* swap it for fine isotropic noise (scale ~0.1 mm). Drive bump at 0.02–0.05 and roughness 0.3–0.5 from it. Keep base-colour variation at ±2%.

5. **The ink tone is inconsistent and dull.** The top of the dot is ~140 and the bottom ~98. It reads like a rendering fall-off, not a design choice. The ink is also neutral grey with no warm/cool counterpoint.
   *Fix:* make ink density uniform across the glyphs. Push the ink to a warm or blue-black, and cool the whites a little more.

6. **Thickness is timid.** The edge looks like 3–4 mm. "Thick-ish" wants 6–8 mm, with a visible bevel catch-light and some inner glow on the edge.

## To reach 8.5+
Keep v04's crisp core and add the diffusion halo back beneath it, so it reads as sharp print seen through haze. Make the line screen legible. Give the plastic a satin specular sweep with isotropic grain on top, and separate the slab from the sweep. Fixes 1–3 get this to ~7. Fixes 4–6 and a bit of colour make it shippable.
