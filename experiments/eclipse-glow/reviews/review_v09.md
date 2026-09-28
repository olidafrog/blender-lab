# Review v09

1. **Score:** 6.8 / 10

2. **Targets** — none set.

3. **What works**
- The mark reads straight away. Both stepped bars and the hourglass match the SVG, including the lower step on the left bar.
- The palette is right: near-black top, deep blue middle, pink-lilac bottom, warm orange-red halo, warm off-black background.
- The grain is fine and even, and it does not break up the gradients.

4. **Problems, ranked**

**1. The bodies read as flat slabs with a gradient, not as lit volumes (all three shapes).** Nothing changes across the width of a bar. The colour changes only from top to bottom, and it runs straight across the step (centre crop). The "spectral rim" is a 2–4 px cyan/yellow hairline, like chromatic aberration on a cut-out. In the reference, the sides turn spectral and brighter over about 5–8% of the width. Fix: stop tuning values. Change the geometry. Make each shape a pillow (a deep bevel with a rounded profile, or remesh, smooth and scale Z) so the normals tilt across the whole face. Then drive the rim from Layer Weight (Facing), with the band at 10–15% of the shape width, about 15–25 px here.

**2. Where the halos overlap they go muddy brown (gaps between the bars, centre crop, and beside the hourglass waist).** The glows add up into dull brown bands that look like drop shadows. The reference halo stays saturated red-orange all the way down to black. It is also bottom-heavy, and the top has a dark gap. Fix: take the halo colour from a ramp keyed on the blurred alpha (black → deep red → orange), not from the blurred beauty, so hue and saturation hold. Weight it by a vertical gradient so the bottom is 1.5–2x the top.

**3. The crescent looks like lids stuck on each shape (all tops, TL and TR crops).** Each cap has an even thickness of about 20 px and stops hard at the shoulders. It does not hand off to the side rim. The reference arc is thin and lifted, brightest at the apex, and it tapers down the sides over about a third of the height. Fix: build it from the silhouette. Use the alpha shifted up 6–10 px, minus the alpha, times the normal-up component so it tapers. Keep the apex at 10 px or less, with a 4–8 px dark gap.

5. **Research check** — The image contradicts "colour from the camera-space normal's vertical component". A flat face should give one flat colour. Here the gradient tracks screen Y across flat faces and runs straight through the step, so it looks position-driven. The glows match the research: halo, crescent, bloom and grain are all present.

6. **What 8.5 needs**
- Pillowed geometry with a real Fresnel spectral band (Problem 1).
- A saturated halo from a ramp, weighted to the bottom (Problem 2).
- A tapered, lifted crescent that runs into the side rims (Problem 3).
- A brighter, near-white pink at the bottom of each body, with orange wrapping in from the rim, as in the reference.
