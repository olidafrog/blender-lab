# Review: v20

## Score: 7.7 / 10

## What works
- The fringe is now a screen, not a zipper. In the detail crop the lines run out into the blur at different lengths and thin as they go. This is the crop1_text behaviour I asked for.
- The core holds: mean 74, range 44–148, cool and lifted. The MIC dots read. The background is a neutral 168. The contact shadow, proportion and thickness are still right.
- Pinholes now sit in the starved patches (lower stem 2, upper stem 2). They no longer spread evenly over the ink.

## Top problems (ranked by impact)

1. **The logo is now too soft for the brief.** The brief says "slightly diffused". At full frame the mark reads as a camera out of focus. Row y=900 on stem 1: 195→167→150→98 on the left, and 89→116→142→164→183 on the right. That is 16+ px, about 3.5 mm at A5. The screen is correct, but the soft zone is so wide that no edge is crisp anywhere. In ref4 and crop1_text the black ink edges are firm, and the texture sits on top.
   *Fix:* keep the screened ramp, but make the solid core reach within ~0.8 mm of the true edge. Use a two-part coverage: a sharp core (0.3 mm blur) max-combined with a faint wide tail (2–3 mm) at ≤35% coverage. Most of the edge then reads crisp, with hairlines that trail off.

2. **The side face reads as clear glass, not frosted plastic.** Side column x=360: 200 down to y≈720, then a hard drop to 150–146. Row y=1000 across the side: 163→134, flat, then the arris. This is a mirror of the grey sweep with a dark reflected band. There is still no dark print line at the print depth (134→137→161 before the arris). The face is milky and the side is glassy, so the two read as different materials.
   *Fix:* raise side transmission roughness to 0.35–0.5 and add a thin volume scatter, so the side is a bright satin grey (175–190). Put the print rim as a 0.4 mm band at 0.3 albedo, 1–2 mm in from the front arris.

3. **The mottle still reads as smoke, not material.** Detrended face std is 1.29 (v19: 1.30). The fibre grain did not register at full or crop scale. The visible variation is soft grey clouds in the lower right, which read as uneven light.
   *Fix:* double the fine grain (1–3 mm, ±4 levels) and route it into roughness at ±0.08, so it catches the key light. Cut the 15 mm layer to ±2.

4. **The starved patches are weaker than in v19.** The worn toner clouds in stem 1 are fainter. The core is now an even twill again.
   *Fix:* restore the v19 starve amplitude (stem std ~6.5) and let the line screen thin inside those patches.

## To reach 8.5+
Crisp edges with trailing hairlines, not a defocus (~+0.4). A frosted side with a visible print rim (~+0.2). Grain that you can see in the roughness (~+0.2). Toner wear back in the core (~+0.1).
