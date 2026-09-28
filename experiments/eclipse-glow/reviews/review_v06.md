# Review v06

1. **Score:** 6.8 / 10

2. **Targets**
   - None set.

3. **What works**
   - The body palette is right. Near-black tops, a saturated cobalt band, then pale blue to lilac-pink. It matches the reference sphere's vertical order.
   - The mark is legible: two stepped bars and the pinched hourglass. The proportions match the SVG. The step joints are clean, with no seams, facets or streaks in any crop.
   - The grain is present and even. The background is a warm near-black, not transparent.

4. **Problems, ranked**
   1. **The halo is uniform, so it reads as a Photoshop "outer glow".** It is the same orange at the same width on every side of every shape. In the reference the energy is at the bottom. The lower limb is a thick, hot, white-orange band. The sides are softer, and the top is dark apart from the crescent. Here the brightest spot is the top cap, so the energy is upside down. Fix: weight the halo source by the downward normal, for example the rim pass × clamp(−N_y), before the glow blur. Aim for top and upper-side halo at 10–25% of bottom intensity. Give the bottom halo a yellow-white core that falls off to red-orange.
   2. **Each body has no warm lower limb.** The pink bottoms stop at a thin orange hairline. The reference goes pink → peach → saturated orange-red over the last ~12% of the form and blooms out from there. Fix: add a warm band to the ramp for the most downward-facing values. The flat faces give too few such pixels, so also widen the bevel radius. Or add a per-shape height term so the lowest 10–15% of each shape turns orange.
   3. **The crescent is fused to the halo, and the gaps between shapes fill with glow.** On each top the crescent is a thick cap glued to the edge. The reference crescent is a thin arc lifted above the body, with a dark gap under it and ends that fade out at about ±60° from vertical. In the centre crop, the gap between the bars is solid orange-brown. That kills the dark negative space. Fix: offset the crescent mask up by 1–2% of frame height and thin it to about a third of its current width. Once problem 1 is fixed, the side halo in the gaps drops too. Keep the gap below 30% of the bottom-halo brightness.

5. **Research check**
   - The gradient runs the full height of each flat-faced shape. That looks like a height or position term, not a pure camera-space normal. A flat front face has a constant normal. Fine as a look, but the notes should say which one it is.
   - The spectral rim is a uniform 2–3 px cyan-green line all round each shape. The research puts it at grazing angles, broad and yellow-green-cyan on the mid-height sides, and weak top and bottom. Chromatic dispersion is barely visible anywhere else.

6. **What 8.5 needs**
   - A halo weighted to the bottom, with a hot white-orange lower limb and a dark top.
   - A warm orange band at the bottom of each body.
   - A thin crescent lifted off the top with a dark gap below it, and darker gaps between the shapes.
   - A spectral rim concentrated on the sides at mid-height, not a uniform outline.
