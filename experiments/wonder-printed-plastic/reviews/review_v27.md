# Review: v27

## Score: 8.4 / 10

## What works
- The pinholes are fixed. The core median is 81 (p5 71, p95 92). The brightest pixel is 105, only +24 over the core. No pixel is more than +30 over the core. The ink reads as a solid toner layer, with no salt on it.
- The side now matches the face. The side is 198/198/203 and the face is 210/210/212. Both are cool. The side runs 213 at the top to 186 at the bottom, with std 2.2. It reads as the same stock.
- The toner scatter shows at crop scale. In the band just outside glyph 1's left edge, there are 75 dark specks (at least 8 levels below the local median). The open face has 37 in an area six times larger, so the edge band is about 13 times denser. In the detail crop, the specks sit just off the contour, like laser toner.
- The diffusion falloff, the line screen and the yellow MIC dots are still right. Row 900 goes 205→189→167→133→99 over about 19 px.
- The face mottle is present. A 0.5–3 mm band-pass on the lower face gives std 4.5.

## Top problems (ranked by impact)

1. **The dark seam at the front arris is still there.** Row 900 goes: side 200, then 193/182/181/187, then a hairline at 236, then the face at 219. The dip is 19 levels deep, a little deeper than in v26 (183). The edge crop shows a grey groove running the full height. The lighter print rim did not cause it. It is geometry or shading.
   *Fix:* check for two coplanar or overlapping surfaces at the corner, for example the print plane sitting 0.x mm proud of the slab or inset from it. Merge them into one mesh with one bevel modifier (1 mm, 3 segments, harden normals). If the print is a separate decal, shrink it 2 mm inside the face edge so it never reaches the arris. Then check the result with a flat-grey override material.

2. **The edge character is still too uniform.** The contours are still perfect rounded rectangles in the logo crop. The scatter is a fine, even sprinkle of 1 px specks. In ref4 the damage clumps: chips 0.3–0.8 mm, dropouts inside the stroke, and ragged runs along one side. The "gaps just inside" do not show.
   *Fix:* modulate scatter density with a low-frequency noise (5–10 mm scale), so some edge runs are clean and some are heavy. Add a few larger inner dropouts (0.3–0.6 mm, lifted to about 130) in the heavy runs.

3. **The face still reads as satin paint at full frame.** The mottle measures well but does not show at 1600 px. The fine grain is quiet (3 px high-pass std 1.5).
   *Fix:* push the 1–3 mm albedo mottle to ±5–6 levels. Add a matching roughness variation (±0.05) so the sheen breaks up.

4. **The sheen band is flat.** Column 800 peaks at 217, just above the logo. It is acceptable, but a softbox with a gradient falloff would give the face more form.

## To reach 8.5+
Remove the arris seam (+0.1). Clumpy edge damage with visible inner dropouts (+0.05). A face mottle you can see at full frame (+0.05).
