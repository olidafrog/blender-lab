# Review: v21

## Score: 7.9 / 10

## What works
- The defocus is gone. Row y=900 on stem 1 goes 192→172→84 in about 6 px on the left, and 88→180 in 3 px on the right. The core is solid, and hairlines trail out past the edge as in crop1_text.
- The core stays lifted and cool: mean 72, range 42–150. The MIC dots read in the detail crop. The background is a neutral grey (166 at the top, 212 at the floor).
- The side face is no longer glass. Column x=345 is 206–229 all the way down, a bright satin white. Face and side now read as one material.
- Proportion, thickness and contact shadow are still right.

## Top problems (ranked by impact)

1. **The toner wear is at the wrong scale. It reads as marble or smoke.** Stem 1 core std is 11.6 (v20 was lower). The logo crop shows big soft pale clouds, 10–20 mm across, like camouflage. In ref3/ref4 the wear is fine: speckle dropout, small scratches, and broken edges at 0.2–1 mm. Soft clouds read as a texture overlay, not worn toner.
   *Fix:* cut the large starve layer to about 40% of its current amplitude. Add a high-frequency dropout: Voronoi or thresholded noise at 0.3–0.8 mm, 5–10% coverage, biased toward the glyph edges. Target core std of about 7, with the variance in specks, not clouds.

2. **The ink now sits on the surface, not under it.** The swing from v20 went too far. The edge is a hard cut with a comb of hairlines. There is no soft optical halo. The brief says "slightly diffused". In crop1_text the black letters are firm, but a soft grey bloom sits 1–2 mm around them.
   *Fix:* keep the crisp core and the hairline tail. Add a separate, unscreened veil: a 1.5–2 mm blur of the artwork at 8–12% darkening, multiplied over the face. Soften the core edge itself with a 0.2–0.3 mm blur. The goal is a transition of about 4–6 px here, not 3.

3. **The face mottle still reads as uneven light.** Mid-scale std is 7.2 on the lower face. There are grey smoky clouds in the lower left and upper middle. Fine-scale std is 3.4, but most of that is the MIC dots. At full frame no fibre grain is visible.
   *Fix:* cut the 10–20 mm mottle layer by half. Push fibre grain into roughness at ±0.1 so the key light shows it as a satin sparkle. Add a clear-coat roughness variation at 1–2 mm.

4. **The side face is flat, opaque white.** It is brighter than the front face (about 225 against 195). It has no depth, and there is still no print line inside the thickness. It reads as painted, not translucent.
   *Fix:* drop the side albedo or scatter so it sits at about 190–205. Add a faint 0.4 mm grey rim 1–2 mm in from the front arris, where the print layer meets the edge.

## To reach 8.5+
Fine-scale toner dropout instead of clouds (~+0.3). A soft veil bloom that puts the ink under the surface (~+0.2). Grain you see in the sheen, not in the albedo (~+0.1). A side face with depth and a print rim (~+0.1).
