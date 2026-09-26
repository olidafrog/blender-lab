# Review: v16

## Score: 7.4 / 10

## What works
- The blacks are back under the frost. The core is 67/68/77, with a cool tint, in the 65–72 target. The ink now reads as behind the plastic, not on top of it.
- The veil and halo read at full frame. Outside the stem the face falls 204 → 192 → 183 over ~30 px before the edge. The glyphs sit in a soft grey cloud.
- The yellow tracking-dot grid shows in the detail crop at the right scale and strength.
- The specks now cover the whole face, and some dark specks sit inside the ink.
- The studio is right: neutral 168 grey background, a soft contact shadow, a clean top arris.

## Top problems (ranked by impact)

1. **The screen is still a texture, not lines.** In the detail crop the lines are near-vertical (~75°), not a shallow 15°. A cross-grain beat turns them into corduroy or denim again. The stroke edge is still a comb of teeth ~8–12 px long. In crop1_text the black lines are shallow, even and countable, and they stop cleanly.
   *Fix:* check the UV rotation sign and axis, because the angle reads as 90° − 15°. Render the line frequency at a whole number of pixels per period (e.g. 6 px at 2x) so it cannot alias into a beat. Threshold against coverage *after* a 1–2 px pre-blur, and raise the fringe cut-off from 0.15 to ~0.25.

2. **There is still no mottle.** The low-frequency variation is ±2–5 levels (std 1.2–2.0). The warm/cool shift has a B−R std of 0.3–0.6, so you cannot see it. The face still looks like a perfect CG gradient (207 top-left → 185 bottom-right).
   *Fix:* scale the mottle ×3–4 to reach ±8–10 levels at 15–40 mm. Give the tint a B−R swing of ±3–4. Add ±0.08 roughness in the same noise so the sheen breaks up too.

3. **The face specks read as terrazzo sprinkle.** They are evenly spread, one size, and sharp. They sit on the surface like dust, not in the sheet.
   *Fix:* use three size classes. Blur 60% of the specks with the ink's depth blur. Cluster them with a low-frequency mask. Cut the count by ~40%.

4. **There is no toner dropout.** The ink has dark specks but no light pinholes or voids. ref3 and ref4 are full of dropout.
   *Fix:* threshold high-frequency noise to punch 1–3% light voids into the ink coverage *before* the screen.

5. **The side is still dead.** The side face is flat 187–192 with a hard bright seam. It shows no depth and no print plane.
   *Fix:* add a faint darker line at the print depth. Add transmission falloff, darker toward the back. Add a slight satin grain on the side.

6. **The glyph edge feels close to camera defocus at full frame.** The 10–90% edge is ~12 px, with a wide ramp.
   *Fix:* tighten the ink blur ~20% and keep the wide halo. The contrast between a crisp core and a wide bloom is what sells "under frost".

## To reach 8.5+
Get a true 15°, countable line screen with no beat and a clean stop (~+0.5). Make the sheet visibly cloudy and uneven, with embedded grit and dropout in the ink (~+0.4). Give the side some depth so the slab reads as a thick, used, translucent object (~+0.2).
