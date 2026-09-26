# Review: v24

## Score: 8.1 / 10

## What works
- The edge is finally soft. Row 900, stem 1: 196→188→180→168→147→125→109→98 over about 7 px, after a faint 10 px falloff on the face. At full frame the logo starts to sit under the surface instead of on it.
- The blacks lifted. Core RGB is 66/67/75, up from 53/54/61 in v23, with a +8 blue tint. Contrast is 3.0:1 (face 207).
- The side face came down. It now runs 216 at the top to 189 at the floor, was 235–249.
- The line screen, MIC dots and the hairline comb past the glyph edge all survive (detail crop). They echo crop1_text.

## Top problems (ranked by impact)

1. **The blacks are still about 12 levels short, and the screen is too loud.** The core median is 71 and the 5th percentile is 55. Along row 900 the lines swing from 53 to 105. In the detail crops, the screen beats against the pixel grid into a stepped herringbone. It reads as twill fabric, not toner. In crop1_text the lines are finer and lower in contrast than the solid.
   *Fix:* raise the veil lift so the core sits at 80–85. Cut the screen amplitude by about 40% (target core fine std of 5–6, now 9.7). Raise the frequency about 1.3×, or pre-filter the screen before the 2× downsample, so it stops aliasing.

2. **The side face reads as brushed aluminium.** The base crop shows a cool, silvery band with a hard dark arris line and no grain. The top 40% (213–216) is still brighter than the front (208). There is still no print rim.
   *Fix:* warm the side tint to match the front. Set roughness to 0.45 and add the face mottle to it. Move the flag so the top of the side sits at 195–200. Add a 0.4 mm grey rim 1–2 mm in from the front arris.

3. **There is a new light leak on the floor.** At about x 290, y 1100 a pale wedge crosses the floor shadow left of the slab. It reads as a stray caustic or a reflection off the flag.
   *Fix:* turn off caustics on the flag and the slab. Or set the flag's glossy ray visibility to off, not only camera.

4. **The face still has no surface.** Face std is 1.6 (top and bottom), the same as v22. No sheen crosses it. Nothing tells the eye that there is a frosted layer above the ink. The slab reads as painted board.
   *Fix:* add a strip light near grazing (15–20° to the face) for a soft sheen on the upper third. Push the roughness mottle to ±0.15 at 1–3 mm.

5. **The contours are still clean vector at full frame.** The coarser chipping and clumped pinholes show only in the 3× crops. Nothing bites into the outline at logo-crop scale.
   *Fix:* double the low-frequency erosion to 0.3–0.5 mm on about a 4 mm noise. Leave 1–2 larger dropout areas per glyph.

## To reach 8.5+
Core at 80–85 with a quieter screen that does not alias (+0.2). A satin side face that matches the front, has a print rim, and no floor leak (+0.15). A grazing sheen that shows the face grain (+0.1).
