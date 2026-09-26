# Review: v17

## Score: 7.7 / 10

## What works
- The line screen is now at a shallow angle (~15–20°). The lines are even and you can count them in the detail crop. The corduroy beat of v16 is mostly gone.
- Toner pinholes show. Light voids and a few dark grit specks sit inside the ink. The ink reads more like toner and less like paint.
- The ink core is 57–63 / 58–64 / 66–72, cool-tinted and lifted. It still sits behind the frost.
- The edge is tighter. The ink goes from 191 to 67 in ~12 px, and a soft halo sits outside it. That pairing sells "under frost".
- The studio is right: 168 neutral background, a soft contact shadow, a clean arris.

## Top problems (ranked by impact)

1. **The screen stops at a hard cut-off. It does not modulate through the blur.** In the detail crop the lines end in a serrated comb, and outside it is a smooth grey halo with no lines. In crop1_text the lines stay sharp across the blurred edge and get thinner toward the paper. That thinning is the signature of the look.
   *Fix:* threshold the lines against a wider pre-blurred coverage (a 15–25 px ramp at 2x), so line width shrinks through the halo. Drop the fringe cut-off to ~0.05. Keep the frost blur as a separate, gentler pass on top.

2. **The ink is too uniform. It reads as twill fabric.** The density is even from stem to stem (std ~10, all of it the line pattern). ref3 and ref4 have patchy toner, starved areas and scuffs at 5–20 mm.
   *Fix:* multiply the coverage by low-frequency noise (±12–15%) at 8–20 mm before the screen. Add 2–3 small starved patches. Raise the pinhole rate in those patches.

3. **The mottle is still weak.** After a 25 px blur, the upper face spans 193–210 (std 3.7), and most of that is the light gradient. The B−R shift is a flat +4 with std 1.4, so there is no warm/cool swing. At full frame the soft clouds near the top right show, but they read as uneven light, not as the sheet.
   *Fix:* double the amplitude again, to ±8–10 levels. Push the B−R swing to ±3–4. Put the same noise into roughness (±0.08) so the sheen breaks up too.

4. **The face specks are still a terrazzo sprinkle.** They are fewer, but they are still sharp, one size and evenly spread. There are no MIC dots at full frame (fine), but the specks compete with them.
   *Fix:* blur 60% of them with the ink's depth blur. Cluster them with a mask. Cut the dark ones by half.

5. **The side is dead.** It is flat 205–214 with a hard bright seam, plus one dark smear (171) at mid-height. There is no print plane and no depth.
   *Fix:* add a faint dark line at the print depth. Darken the transmission toward the back. Give the side a satin grain.

## To reach 8.5+
Make the lines thin out through the blurred edge instead of stopping (~+0.4). Make the toner patchy and imperfect (~+0.3). Give the sheet a visible cloudy body with a warm/cool swing (~+0.2). Give the side a print plane (~+0.1).
