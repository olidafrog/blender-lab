# Review v04 — pink_rod (target: 02_pink_rod_sky.jpg)

## 1. Score: 6.4 / 10

## 2. Targets
- Lit top: 218,128,189 vs ~180,146,170 — **missed** (too magenta, G low, B high).
- Left: 235,151,207 vs ~183,123,148 — **missed** (too bright, too blue).
- Violet shadow side: 144,84,144 vs ~148,101,135 — **missed, close** (luminance 101 vs ~113).
- Bottom: 118,69,129 vs ~127,76,104 — **missed** on hue (B +25); luminance hit.
- Sky top: 68,108,153 vs ~63,109,155 — **hit**. Sky bottom: 130,158,179 vs ~134,165,184 — **hit**.
- Shadow/lit luminance: 0.59 (≥0.35) — **hit**.
- Edge falloff: left edge ramps over ~18–20 px at 1400 wide, so ~9–10 px per 700 (target 2–4) — **missed**.
- Entry glow: ~4–5 tube widths — **hit**.

## 3. What works
- The rod passes through: the entry and exit flare at the surface and a saturated hotspot shows through mid-body (~750,830). Correct depth logic.
- Shadows stay light and cool-violet, not smoky. Multiple scattering reads.
- Sky gradient matches the reference.

## 4. Problems, ranked
1. **Cloud body reads as soft wax or mashed potato, not popcorn** (whole cloud; centre crop). Ref 02 has nodules down to ~5–10 px, with crisp silhouettes. Here the lobes are 40–80 px blobs with a ~10 px/700 edge. The centre crop also shows blotchy denoiser smear. Raising density has not fixed this before, so change the mechanism. Add two more billow octaves: inverted Worley displacement of the SDF at 1/3 and 1/9 of the current lobe scale, amplitude falling ~0.5 per octave. Then build density as a steep ramp over the SDF (0 to full over ≤1.5% of the cloud radius), so the surface mean free path is 1–3 px. Render 1024+ samples and denoise with albedo/normal passes, or skip the denoiser and add grain.
2. **Colour is paint, not albedo** (lit left and top). The lit side is bubblegum magenta. In ref 02 the lit side is peach-pastel (G ≈ 0.8×R), and saturation only builds in the core and shadow. Set the albedo to about R 0.99, G 0.95–0.96, B 0.97. Warm the sun to ~4500–5000 K. Let the sky fill make the violet in the shadows.
3. **Rod bloom is too big** (whole rod in the sky). The halo is ~6–8× the tube width along its full length. Ref 02 shows a crisp thin line with a halo ≤2× its width. Cut the glare/bloom size by ~60% or threshold it higher, so only the entry points bloom. Thin the tube by ~30%.

## 5. Research check
- Contradicts "lobes on lobes, crisp silhouette, few-pixel falloff": only one billow scale shows and the edge is soft.
- Partly contradicts "colour deepens in core and shadow, not a flat tint": the lit side is already fully saturated.
- Agrees on multiple scattering, darker base, and emitter hue kept inside with a depth-scaled glow.
- Silver lining is not tested (front-lit), which is acceptable for this reference.

## 6. What 8.5 needs
- 2 extra billow octaves plus a steep SDF density edge (2–4 px/700).
- Albedo near-white with slightly low G and B, and a warm sun, so the lit side reaches ~180,146,170.
- Denoiser smear gone. Light film grain to match ref 02.
- Rod halo ≤2× tube width outside the cloud.
