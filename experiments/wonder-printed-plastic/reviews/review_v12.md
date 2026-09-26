# Review: v12

## Score: 6.5 / 10

## What works
- The screen is finally one family. Every glyph has the same single-angle diagonal lines, from the left stroke to the dot. The v09 stipple/lines mismatch is gone.
- The focus is fixed. Both strokes are equally sharp. Nothing is lost to DOF.
- The ink tone is solid. Cores are ~63–67 with a cool bias (65/67/76). The blacks are lifted and do not crush.
- The slab is clean and calm. The thickness reads, and the internal print plane shows in the edge as a real layer.

## Top problems (ranked by impact)

1. **The ink now reads as a fabric on the surface, not print under frost.** The screen is too strong. Ink pixels span 28–137 (std 12–14). At full size the glyphs look like twill or carbon weave. In crop1 the line screen is fine and quiet, and it sits inside a soft tone. Also, the 8 mm depth does not show. A stroke edge goes 196 → 84 in ~8 px, about the same as v09. With 8 mm behind a frosted face it should be 20–30 px of soft falloff. The logo looks stuck on top.
   *Fix:* cut the line contrast to ~35–40% of now (target ink range ~50–95). Raise the frequency ~1.5× so the lines are 2–3 px apart at 1600 px. Blur the coverage mask before the screen (radius ~1.5–2 mm) so the edges go soft while the lines stay crisp. That is the ref1 signature.

2. **The white face is still sterile.** High-pass std on the face is 1.34. I found 10 yellow-ish pixels in 219k. The "crisp dark specks" do not register on the white at full size. What shows is white specks on the ink, which read as dust on a sticker. The refs are all grit.
   *Fix:* put MIC dots on the white backer layer: 1 mm pitch, 0.1 mm dots, ~30% yellow, enough to see at 100%. Add ±4–6 levels of low-frequency mottle (5–10 mm) to face albedo and roughness. Add dark toner speckle at 2–3× the current density on the white, not only on the ink.

3. **The offset shadow copy is invisible.** I see no ghost under the ink in the logo crop. The effect is doing nothing for depth.
   *Fix:* make it 3–5 px down-right, blur ~6 px, at ~15% darkening. It should read as a soft second image, not a drop shadow.

4. **The lower face is dull again.** The lower face is ~191. The floor beside it is ~217. The gradient runs 209 → 192 from top to bottom and the lower third looks grey.
   *Fix:* add a front-low fill card (+0.5 stop on the lower face), or pull the floor key down ~0.7 stop.

5. **The edge reads as two laminated panes.** The seam line in the edge crop looks like a glass box with an insert. The side band is flat (~211, std 4.7). There is no transmitted glow and no catch light.
   *Fix:* soften the seam into a faint grey line (the print layer seen through frost, ~10–15 levels darker, blurred). Give the sides a thin bright chamfer catch and a faint cool absorption tint.

## To reach 8.5+
Make the ink quiet and deep first: a soft, blurred glyph with a fine, low-contrast line screen that stays sharp. Then grit the white: dots, mottle and dark speckle that you can see at 100%. Fix the lower-face light. Items 1–2 alone should reach ~7.5. A visible ghost and a living edge would take it past 8.
