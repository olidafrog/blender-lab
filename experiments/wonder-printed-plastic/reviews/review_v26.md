# Review: v26

## Score: 8.3 / 10

## What works
- The blacks now sit where they should. Core median is 80 (p5 69, p95 91). It was 74. Contrast against the face is about 2.6:1. The core is cool (RGB 77/78/87), so it reads as toner seen through a cool veil.
- The side face is no longer brighter than the front. It runs 210 at the top to 189 at the bottom, with std 4.1 (it was 3.3). In the edge crop it has a faint mottle and reads as the same stock.
- The pinholes are calmer. There are 12 spikes in the core sample (44 in v25).
- The diffusion falloff is still right. At row 900 the glyph edge goes 201→187→166→133→98 over about 15 px.
- The line screen in the detail crop reads like crop1_text. The yellow tracking dots on the white are a good touch at crop scale.

## Top problems (ranked by impact)

1. **The edge erosion does not show.** The left edge of glyph 1 has a residual wobble of 1.51 px. In v25 it was 1.44 px. The contours still look like clean vector shapes, with perfect rounded corners. The blur removes notches this small. In ref3 and ref4 the edges have toner scatter and chips.
   *Fix:* do not add more notch depth. Keep the shape and add toner scatter at the edges: sparse ink specks (0.1–0.3 mm) in a 0.5–1 mm band just outside the outline, and dropouts just inside it. Apply these to the ink mask after the depth blur, or with a smaller blur, so they survive.

2. **The front arris still reads as a separate laminate panel.** Row 900 goes from side 199 to a dark groove at 183/186, then a hairline at 231, then the face at 217. The edge crop shows a dark seam, like a panel set into a frame.
   *Fix:* remove the cause of the groove. It is most likely a gap or overlap between the face and side meshes, or a separate face object. Use one mesh with a 0.5–1 mm bevel (3 segments). Frosted acrylic edges should glow a little lighter, not darker. Add slight transmission or SSS to the side.

3. **The face grain still does not read at full frame.** High-pass std on the clean face is 3.2 (it was 3.0). At 1600 px the face looks like smooth satin paint.
   *Fix:* add albedo mottle of ±3–4 levels at 1–3 mm on the face base colour, like the fibre mottle in ref4. Keep the fine grain as it is.

4. **The pinholes are still too bright.** The brightest ones reach 150–177 on an 80 core, which is +70 to +95. They still read as salt on top of the ink.
   *Fix:* clamp pinhole lift to +35–45 (about 115–125).

5. **The side tint does not match the face.** The side is neutral-warm (200/198/199). The face is cool (199/199/202).
   *Fix:* use the face's cool tint on the side colour.

6. **The sheen band has not changed.** Column 800 still peaks at 217, above the logo. It is acceptable.

## To reach 8.5+
Toner scatter at the edges that shows at crop scale (+0.1). A single beveled edge with no dark seam that glows a little (+0.1). Face mottle that reads at full frame, and grey pinholes (+0.05).
