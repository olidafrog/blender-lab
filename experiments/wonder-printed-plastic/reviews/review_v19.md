# Review: v19

## Score: 7.8 / 10

## What works
- The toner now has a body. Inside stem 1, after a 10 px blur, the std is 6.5 (v18: 2.7), with a range of 65–94. The starved patches read at full frame as worn toner, close to ref4.
- The frost halo is smaller. The logo sits under the sheet without smoke around it.
- The core is cool and lifted (71 / 73 / 82). The face is cool (B about +3 over R). The studio, contact shadow, proportion and thickness are still right. The background is a neutral 168.
- The MIC dots read clearly in the detail crop.

## Top problems (ranked by impact)

1. **The fringe is still a zipper, not a thinning screen.** Row y=900 across the left edge of stem 1: face 193, then 186→172→167 over 6 px, then a drop to 116/85. The whole ramp is about 8 px at 1600 wide, which is about 1.7 mm. In the detail crop each line ends in a short, even sawtooth tooth, and every tooth is the same length. In crop1_text the hairlines run far into the blur and fade in density, with bright paper between them.
   *Fix:* the ramp is still too short at this scale (A5 is about 4.7 px/mm here). Blur the coverage by 3–4 mm (30–40 px at 2x) before the threshold. Add a small jitter (low-frequency noise at ±0.05) to the threshold so the teeth do not all end on one contour.

2. **The backer mottle is at the wrong scale.** The face now has clouds, but they are 60–100 mm blobs. They read as uneven light or smoke behind the sheet, not as plastic. The detrended std is only ~3.5, and most of what you see is one large gradient from top-left to bottom-right (209→198).
   *Fix:* use two octaves. One at 10–25 mm with ±4 levels, and one fibre or grain layer at 1–3 mm with ±2 levels. Cut the large-scale layer by half. Put the same noise into roughness at ±0.05.

3. **The pinholes are still an even salt sprinkle.** In the detail crop they are the same size and spread evenly over the ink, including the dense areas. They are not in the starved patches.
   *Fix:* multiply the pinhole mask by the starve mask (gamma 2). Vary the dot size 1–3 px. Add 2–3 short scuffs that break the line pattern.

4. **The print-layer rim does not read in the side.** Side row y=1000: arris spike 216, then a smooth 196→170 ramp, then the front arris. There is no dark line at the print depth. The side reads as a solid white block, not a frosted sheet with ink inside.
   *Fix:* make the rim darker (0.3–0.4 albedo) and 0.3–0.5 mm thick. Lower the side's scatter density so it can show through. Add a faint satin grain to the side's roughness.

5. **The line screen is too even in the core.** The twill is a flat, dense pattern. It reads as fabric at 100%.
   *Fix:* add a ±5% width jitter along each line and a slight density drop inside the starved patches.

## To reach 8.5+
Get the hairline fringe that thins over 3–4 mm (~+0.3). Move the mottle to a material scale with fibre grain (~+0.2). Tie the pinholes to the patches (~+0.1). Make the print rim read in the side (~+0.1).
