# Review v03 — eclipse_logo_v03.png

1. **Score:** 6.2 / 10

2. **Targets** — no numeric targets set.

3. **What works**
- The body gradient matches the palette: near-black navy top, saturated blue middle, lilac-pink bottom. It repeats cleanly per shape.
- The mark is legible and correct against the SVG: both bars step down-right (left at ~60%, middle at ~51% of height), the hourglass dot sits top-right at ~48% height.
- Grain is present and even, with no banding in the gradients.

4. **Problems, ranked**

1. **No halo (whole frame).** The reference sits in a wide orange-red glow that bleeds 10–15% of the sphere's width into the black. Here every shape ends at a hard edge on pure black. It reads as an enamel pin or a neon sign, not an eclipse. Threshold bloom cannot find this: the body is not bright enough. Build the halo from the object mask instead. Dilate the alpha by 4–8 px, blur it 60–120 px (at 1200 px width), tint it orange (about #FF5A1F). Add it under the body. Peak just outside the edge should be 0.3–0.5 of the rim's brightness, falling to black over 100–150 px.

2. **The "rim" is the extrusion side wall, not a fresnel rim (all edges).** Bars left of centre show a hard 2–4 px yellow band on their right edge only; the dot, right of centre, shows it on its left edge. That is perspective exposing the side walls. The reference rim is soft, symmetric, 3–5% of the shape width, orange-red at the bottom and spectral on the sides. Fix: use an orthographic camera or a focal length of 150 mm or more, and give the mesh a rounded bevel (radius 15–25% of bar width), so the fresnel term forms the rim. Then blur the rim 4–8 px.

3. **No crescent (top caps).** The reference has a bright, lifted arc that floats clear above the top edge. Here the top caps have only a thin 1–2 px highlight on the edge. Make a top-edge mask (rim × normal.y > 0.5), shift it up 12–24 px, blur it 6–10 px, tint it warm white, and add it. The arc must separate from the body by a dark gap.

5. **Research check** — The body gradient agrees with the research. The glow claims do not: no halo, no lifted crescent, no visible bloom, and dispersion shows only as a thin cyan line on the inner edges. The spectral rim contradicts the research: it is a lit side wall, not a grazing-angle term.

6. **What 8.5 needs**
- A mask-based orange halo behind every shape.
- A symmetric, soft fresnel rim from a bevelled mesh seen by an orthographic or long-lens camera.
- A lifted crescent above each top cap.
- Soften the body edges by 1–2 px, so the forms glow instead of looking cut out.
