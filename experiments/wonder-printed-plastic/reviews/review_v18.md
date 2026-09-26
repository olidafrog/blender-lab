# Review: v18

## Score: 7.7 / 10

## What works
- The lines now go into the fringe. The edge profile has a short shoulder (~152–156 over 5 px) before it drops to the core. In v17 the lines stopped at a hard wall. This is the right direction.
- The face is clean. Dark specks in a face strip fell from ~330 px to ~8 px. The terrazzo sprinkle is gone. The MIC dots now read on their own in the detail crop.
- The studio is still right: 168 neutral background, soft contact shadow, clean arris, good A5 proportion and thickness.
- The core is cool and lifted (75 / 75 / 81) and sits behind the frost.

## Top problems (ranked by impact)

1. **The fringe is a comb, not a thinning screen.** In the detail crop each line ends as a wedge tooth of about the same length. Past the teeth is a smooth grey halo with no lines. At full frame this reads as fur or motion blur, not as ref1. In crop1_text the lines get thinner and fainter as hairlines far into the blur, and the paper between them stays bright.
   *Fix:* the threshold ramp is still too short. Threshold against coverage blurred by 20–30 px at 2x. Use `step(1 - cov, line)` with a line profile that is a triangle wave, not a sine, so the width goes to zero in a linear way. Take the frost blur down to ~3–4 px so it does not smear the hairlines back into a halo.

2. **The patchy toner does not show.** Inside stem 1, after a 10 px blur, the std is 2.7 (v17: 3.4). The ink is 7 levels lighter overall. So the noise lifted the mean but added no visible patches. The stems still read as even twill.
   *Fix:* use ±15–20% low-frequency noise at 6–15 mm, with a contrast curve so a few areas starve clearly. Add 2–3 scuffs that break the line pattern. Pull the core back to ~62–66 so the starved areas have room.

3. **The mottle and warm/cool swing are almost unchanged.** Upper face, plane-detrended: std 2.3 (v17: 1.8). B−R residual std 0.23, the same as v17. The clouds you see at full frame sit mostly around the logo and lower face. They read as smoke or uneven light, not as the sheet body.
   *Fix:* check the mottle reaches the final colour. It is likely being normalised out or masked by the backer. Aim for ±6–8 levels and a B−R swing of ±3. Use a smaller scale (15–30 mm) so it reads as material. Put the same noise in roughness.

4. **The pinholes are an even salt sprinkle.** They are the same size and evenly spread over the whole ink.
   *Fix:* tie them to the starved patches in fix 2. Vary the size 1–3 px. Cut the global rate by half.

5. **The side is still dead.** It is a flat gradient 202→172 with no print plane.
   *Fix:* add a faint dark line at the print depth. Add satin grain and darken the transmission toward the back.

## To reach 8.5+
Make the lines thin to hairlines through a wide ramp with a lighter frost pass (~+0.4). Make the toner patches visible (~+0.2). Get real sheet mottle and a warm/cool swing into the output (~+0.2). Give the side a print plane (~+0.1).
