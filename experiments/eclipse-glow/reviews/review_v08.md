# Review — eclipse_logo_v08

1. **Score:** 7.2 / 10

2. **Targets** — none set.

3. **What works**
- The palette is right. The navy top, cobalt band, sky blue and pink bottom match the reference body closely.
- The mark reads at once: two stepped bars and the hourglass dot, with the correct proportions and orientation from the SVG.
- The halo, grain and warm black ground match the reference well. The grain is even, and the crops show no banding or fireflies.

4. **Problems, ranked**

1. **Seams at the step ledges (centre, y≈760 and y≈840).** Where each bar steps, a dark brown band crosses the inside of the logo, with a thin cream line under it. The crescent/halo pass treats the ledge as an outer top edge, so it cuts the shape in two and reads as a shadow seam. Fix: build the crescent from the silhouette's *outer* top edge only. Offset the alpha mask upward, subtract the original alpha, and multiply by a mask that is zero inside the dilated logo (dilate alpha by about 8 px). Do not let the halo darken pixels where alpha is above 0.5.

2. **The crescents are thick flat lids (top of all three shapes).** Each cap is a uniform cream slab, about 20 px thick, cut square at the corners. It looks like a separate object. In the reference the crescent is a thin arc, 2–4% of the object height, white-hot at the centre, and it fades to orange as it runs down each side to about 45° below the top. Fix: shrink the vertical offset to about half, taper the intensity with a horizontal falloff (centre 1.0, ends 0), and extend it down the upper corners. Blur it by 2–4 px and add a warm glow around it.

3. **The body looks like a flat 2D gradient fill.** On the bars the colour depends only on screen height. The colour does not wrap at the edges, and the rim is a hairline cyan/yellow line of 3–5 px. The reference rim is a wide spectral band, 6–10% of the width, and the bottom goes pink → hot yellow-white → red. Fix: give the front faces real curvature (a larger bevel with more segments, or a displace/inflate so the normals roll over across about 30% of each bar's width). Then drive the rim from the facing ratio over that roll-off, not from a thin edge.

5. **Research check** — Partly contradicted. The research says colour comes from the camera-space normal. On the flat front faces the normal is constant, but the colour still ramps top to bottom, so the gradient must come from position. That explains the flat, graphic look and the thin rim. The crescent, the halo and the grain agree with the research.

6. **What 8.5 needs**
- Remove the ledge seams (crescent and halo only on the outer silhouette).
- A thin, tapered, white-hot crescent instead of the lids.
- Curved front faces so the normals drive the gradient, with a wider spectral rim and a hot bottom edge.
