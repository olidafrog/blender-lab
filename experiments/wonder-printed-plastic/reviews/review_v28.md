# Review: v28

## Score: 8.4 / 10

## What works
- The ink layer is still right. The core median is 79 (p5 69, p95 91, max 105). No salt, no pinholes. It reads as a solid toner layer with lifted blacks.
- The diffusion falloff, the line screen and the yellow MIC dots still hold. Row 900 over glyph 1's left edge goes 199→175→141→110→87 over about 20 px. The detail crop shows the diagonal screen staying crisp through the soft edge, as in ref1.
- The face and side now match in colour. Face RGB 199/199/202, side 199/200/204. Both are cool.
- The face texture is up. The 1.5–12 px band-pass std is 5.0 (v27: 4.5). The 3 px high-pass std is 2.2 (v27: 1.5). At full frame the face starts to look like stock, not paint.
- The edge crop now reads as a rounded arris with a glint along it. It no longer reads as a groove between two parts.

## Top problems (ranked by impact)

1. **The dark line at the front arris is still in the numbers.** Row 900: side 200, then 192/181/181/194, then a highlight of 237–238, then face 221. Row 500: side 212, dip to 188, then face 222. The dip is 19–24 levels, the same as v27. The new bevel made the edge read better, but a grey hairline still runs the full height at 1600 px.
   *Fix:* the dip is part of the bevel whose normals face neither the key nor the fill. Add a thin rim light or a vertical strip softbox camera-left, just behind the slab, to fill the 45° normals. Or cut the bevel to 0.5 mm so the dark band falls under one pixel. Test with a flat-grey override material.

2. **The edge damage still does not show at full frame or in the logo crop.** The contours are still clean rounded rectangles. Speck counts in the band just outside glyph 1, per 40 rows, are 3/0/5/0/3/5/2/2/8. So some runs are clean and some are busy, but the heavy runs are too weak to see. There are no pixels above 120 inside the core of glyph 1, so the inner dropouts do not show. In ref4 you see chips, ragged runs and pale holes from across the room.
   *Fix:* in the heavy runs, raise the density by 3×. Add chips 0.4–0.8 mm that break the contour itself (displace the coverage mask edge by ±0.3 mm, not just add specks outside it). Add 2 or 3 inner dropouts per glyph, 0.4–0.8 mm, lifted to about 140–160.

3. **A soft dark band crosses the upper face.** Column 800 goes 217 at y 560 to 204 at y 700, with a wavy edge that runs in from the left edge. It reads as a smudge or a warped sheet, not as light falloff.
   *Fix:* find the environment or softbox edge that reflects there. Widen that light, or give it a gradient falloff so the sheen rolls off in one smooth ramp from top to bottom.

4. **The face is still quiet next to the refs.** The mottle is present, but ref3 and ref4 have visible fibre and tonal cloud.
   *Fix:* add a 5–15 mm cloud at ±3 levels on top of the 1 mm mottle. Add roughness variation of ±0.05 on the same noise.

## To reach 8.5+
Kill the arris hairline with light or a smaller bevel (+0.05). Make the edge damage visible at crop scale: chips that break the contour and pale inner dropouts (+0.1). Smooth the sheen band (+0.05).
