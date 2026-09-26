# Review: v08

## Score: 6.8 / 10

## What works
- The staging is better. The sweep dropped to ~176–179, and the slab face sits at ~190–209. The slab now reads against the background. In v07 they merged.
- The v07 sheen blob is mostly gone. The face falls off from ~208 at the top to ~190 at mid-height. It is calm, but it has no shape.
- The ink tone holds. Cores are 69–89 with a cool bias (~70/70/77). The edge halo goes 198 → 96 in about 10 px. It reads as print behind haze.
- A screen is now visible at normal size on the middle stroke and the dot. This is the first version where the ink has a structure you can see.

## Top problems (ranked by impact)

1. **The screen reads as woven fabric, not a laser line screen.** In the detail crop the right stroke shows a diagonal cross-weave, like carbon fibre or twill. The left stroke is still random noise (std ~9, range 65–108). In ref crop1 you see one family of parallel lines per ink. They are fine, even and sharp over the blur.
   *Fix:* use a single-angle sin threshold with no second axis. Set 45° for black, at ~120–150 lpi at A5 scale, with ±12–15 levels of contrast. Cut the random speckle to about 25%. Check why the left stroke loses the screen. It is probably UV stretch or a lower sample count on that side.

2. **The face is sterile. There are no print artefacts on the white.** The face std is 1–2 levels. There is no mottle, dropout or grain. The yellow MIC dots appear only as brown specks *inside* the ink, where they are wrong. On the white face they are invisible.
   *Fix:* put the dot grid on the paper layer at 1 mm pitch and ~30% yellow, so it shows on white. Add ±3–4 level low-frequency mottle to the face albedo and roughness. Add thresholded dropout noise to the ink mask edges.

3. **The ink has no depth in the 15 mm slab.** It still looks like a blurred decal on the front face. There is no parallax against the rim and no inner shadow.
   *Fix:* put the ink 1–2 mm under the front face with real transmission. Or fake it with a darker, more blurred ghost offset 2–3 px down and to the right.

4. **The edge is still inert.** The top-left crop shows a flat, milky band (~198–203) with a soft bevel. It has no transmitted core, no bright catch line and no micro-chamfer.
   *Fix:* give the side faces lower roughness (0.15) and a darker, slightly blue absorption core. Add a 0.5 mm chamfer that catches a rim light.

5. **The light has no shape.** The face gradient is shapeless. The floor hotspot at lower right (~224) is the brightest area in the frame and pulls the eye.
   *Fix:* use a strip softbox at a grazing angle for a clean band across the upper third. Cut the right-hand floor light by about 1 stop. Darken the contact shadow under the base.

## To reach 8.5+
Make the screen one clean set of lines that are legible at 1:1. Put grit on the white: dots, mottle and dropout. Give the ink depth inside the slab. Then shape the light. Fixes 1 and 2 alone should reach about 7.5.
