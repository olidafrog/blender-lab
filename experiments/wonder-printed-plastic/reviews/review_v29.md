# Review: v29

## Score: 8.4 / 10

## What works
- The sheen fix worked. In v28, column 800 went from 219 down to 205 between y 570 and y 690, with a wavy edge. In v29 it holds at 207–210. The upper face now reads as one clean satin surface, not a smudge.
- The ink layer is unchanged, and it is still right. The core median is 79 (p5 68, p95 91). The diagonal screen stays sharp through the soft edge. The MIC dots are there. The blacks are lifted.
- The face and side colours still match and stay cool (face 207/207/209, side 201/201/206).
- The diff against v28 shows new work at the glyph contours. There are extra specks and a few pale nicks at the corners and on the lower bowl of the drop.

## Top problems (ranked by impact)

1. **The arris hairline did not go away.** Halving the bevel did not change the dip. Row 900: side 200, then 192/180/180/189/194, then 215–234. Row 500: side 212, then 198/187/187/194/200, then 218. The dip is still 20–25 levels deep. At row 500 it is now wider, because the glint that used to close it is weaker. The edge crop still shows a grey pencil line down the full height.
   *Fix:* this dip does not come from the bevel. Render with a flat-grey override. If the line is still there, it comes from the face shader, for example the transmission or coat stopping short at the edge, or from a UV or mask border. Then pull the face texture 1 mm past the edge. If it is shading, add a thin vertical strip light camera-left, just behind the slab plane, to fill the side-facing normals.

2. **You still cannot see the edge damage at full frame.** Across the whole glyph 1 edge band, only 30 px changed by more than 10 levels. The speck counts per 40 rows are 0/0/1/0/3/0/2/1/1/0, the same as v28. The contour raggedness std is 2.7 px in both versions. The "3× denser" change does not show up in the pixels.
   *Fix:* check that the new density parameter reaches the shader. Then push it well past "tasteful": displace the coverage-mask edge by ±0.4 mm with 1–2 mm noise, add chips 0.5–1 mm, and add 2–3 inner dropouts per glyph lifted to 140–160. Judge the result at 1600 px, not in the detail crop.

3. **The added tonal cloud does not register.** The 8–60 px band-pass std on the lower face is 6.5 (v28: 6.7). The upper face is about 2.5 levels darker overall, but it has no more cloud.
   *Fix:* use a 10–20 mm noise at ±4 levels on base colour, and ±0.06 on roughness from the same noise. Check that it multiplies after the tone map, not before a clamp.

4. **A bright line runs along the top edge.** The top-edge highlight in the edge crop is cleaner and brighter than the soft side edge. It reads as CG.
   *Fix:* add a little roughness to the bevel (+0.1) or break the line with the same speck noise.

## To reach 8.5+
Find the real source of the arris line and remove it (+0.1). Make the contour damage visible from across the room (+0.1).

## Lockup check (not scored)
The system holds up. The blue flood, the reversed white type, the fluoro square and the orange rule all read as ink under the same frosted sheet. The lockup also sells the material better than the lone logo. Two weak points: the small mono line ("SIGN OFF") blurs until you cannot read it, so small text needs less diffusion. The fluoro green also needs a halo to feel fluorescent.
