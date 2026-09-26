# Review: v07

## Score: 6.6 / 10

## What works
- The slab is now a real object. 15 mm reads. The rounded inner rim and the bright catch line on the right edge give it a cast-resin weight that v06 lacked.
- The ink is flatter. Glyph cores sit at 61–88 sRGB (v06: 83–124). The ink has a cool bias (~64/66/75) on a cool face (~204/205/210). The blacks are lifted in the right range.
- The glyph edge has a tighter halo: 201 → 101 over about 9 px at y=900. It reads as print behind haze, not a sticker.
- The twill is gone. The edge crop shows fine isotropic grain.
- The face has a satin bloom in the upper-left. That is the first specular life in the series.

## Top problems (ranked by impact)

1. **The ink texture looks like render noise, not a line screen.** In the detail crop the interior swings 59–111 from one pixel to the next. It is random sandpaper. The diagonal hatch shows faintly in the logo crop and vanishes at 1:1. In ref crop1 you can count the lines.
   *Fix:* cut the speckle to about 25% of its current amplitude, or raise samples and denoise the ink pass. Make the screen the dominant signal: sin-threshold at ~120 lpi, contrast of ±15 levels, and sample it after the depth blur.

2. **The whole image is too clean and too "product".** The refs are gritty printed matter, with toner dropout, tracking dots, mottle and misregistration. v07 looks like a premium glass award.
   *Fix:* add a yellow MIC dot grid (1 mm pitch, 0.1 mm dots, ~30%). Add edge dropout on the ink mask with thresholded noise at 0.2–0.4 mm. Add a very low-frequency mottle (±3 levels) to the face albedo and roughness.

3. **The ink has no depth inside a 15 mm slab.** The logo sits like a blurred decal on the front face. At this camera angle, ink on the back face should shift in parallax against the rim and show a faint inner shadow or refraction at the edges. None of that is visible.
   *Fix:* put the ink on the rear face, or 1–2 mm under the front, and let real transmission show it. Or fake it: offset a darker, more blurred ghost of the mask by 2–3 px, down and to the right.

4. **The sheen is a shapeless blob.** It fogs the top of the left stroke (~140 against a ~85 core), and it has no light shape behind it.
   *Fix:* use a long strip softbox at a grazing angle so a clean band crosses the upper third. Set coat roughness to 0.35–0.45.

5. **The staging is weak.** The face (196–204) merges with the sweep on the left (212). The lower-right floor hotspot pulls the eye. The contact shadow is too faint, so the slab floats.
   *Fix:* drop the sweep to ~185–190 behind the slab. Cut the right fill by about 1 stop. Add a tight, dark contact shadow line under the bottom edge.

6. **The edge is inert.** The side band is a flat milky 198. Add a darker transmitted core or a slight internal glow so the thickness reads as translucent material.

## To reach 8.5+
Make the line screen legible at 1:1 and remove the random noise. Add print artefacts: dots, dropout and mottle. Give the ink visible depth inside the slab. Shape the sheen with a strip light. Fixes 1–3 get this to about 7.5.
