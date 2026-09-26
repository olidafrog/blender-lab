# Review: v09

## Score: 6.7 / 10

## What works
- The ink tone is right. Cores are 80–91 with a cool bias (~81/82/91). The blacks are lifted and do not crush.
- The diffusion holds. A stroke edge goes 186 → 92 in about 9 px, with a soft halo. It reads as ink behind haze.
- The screen is better on the right stroke and the dot. The detail crop shows one main family of diagonal lines, not the v08 twill. It starts to feel like crop1.
- The slab is a clean, believable frosted block. The thickness reads and the silhouette is calm.

## Top problems (ranked by impact)

1. **The face is still sterile, and the MIC dots are gone.** Face std is 2.5–3.9, and most of that is gradient. I found 9 faintly yellow pixels in 195k on the face. At full size there is no grain on top, no mottle, no dropout. The refs are all grit. This render is a clean product shot.
   *Fix:* put a yellow dot grid on the paper layer: 1 mm pitch, 0.1 mm dots, ~30% opacity, so it shows on white. Add ±4–6 levels of low-frequency mottle (noise scale ~5–10 mm) to face albedo and roughness. Add fine toner speckle (±3 levels, 0.1 mm) on top of the whole face.

2. **The screen is inconsistent across the logo.** In the detail crop the left stroke is random stipple (std 6.7, range 71–119) with no lines. The right stroke shows lines (std 9.6, range 52–120). It is the same ink, so it must have the same screen. v08 flagged this and it is not fixed.
   *Fix:* drive the screen from object or generated coords, not the logo UVs. Use one angle (45°), ~120 lpi at A5 scale. Cut the random noise to ~25% of the line contrast.

3. **A light band cuts across the slab.** At x=1050 the face goes 192 → 206 at y 600–680, then drops to 191 by y 700. It reads as a horizon line just above the logo. It splits the composition and looks like a reflected environment, not a studio softbox.
   *Fix:* widen and soften the strip light (larger size, or roughness 0.45+ on the coat). Move the band into the top 15% of the face, or tilt it off-axis so it grazes as a diagonal.

4. **The lower face goes dull and darker than the floor.** The lower face is 174–180. The floor beside it is 204–222. The bottom half looks grey and dead, and the slab reads as a cut-out.
   *Fix:* add a low fill or a floor bounce card from the front-left (+0.5–1 stop on the lower face). Or lower the floor key by about 1 stop.

5. **The ink still has no depth, and the edge is inert.** There is no parallax or inner ghost. The edge crop shows a milky band (~216, std 7.8) and a soft bevel. There is no transmitted core and no bright catch line.
   *Fix:* offset a softer, darker ink ghost 2–3 px down-right, or put the ink 1–2 mm inside with real transmission. Give the sides roughness ~0.15 and a faint blue absorption. Add a 0.5 mm chamfer that catches a rim light.

## To reach 8.5+
Grit on the white comes first: dots, mottle and speckle, visible at full size. Next, one consistent line screen across every glyph. Then fix the light: no horizon band, and a lit lower face. Items 1–3 should reach about 7.6. Depth and a living edge would take it past 8.
