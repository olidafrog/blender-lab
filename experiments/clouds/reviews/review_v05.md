# Review v05 (target: 02 pink rod)

1. **Score:** 6.9 / 10

2. **Targets** (sRGB means, 1400 px frame)
- Lit top 214,133,191 vs 180,146,170: missed (G/R 0.62 vs 0.81, too magenta).
- Left 232,148,205 vs 183,123,148: missed (too bright, blue too high).
- Violet shadow (right) 152,90,147 vs 148,101,135: hit.
- Bottom 133,87,141 vs 127,76,104: missed on blue (+37).
- Sky top 68,108,153 vs 63,109,155: hit. Sky bottom 129,158,179 vs 134,165,184: hit.
- Shadow/lit luminance 107/170 = 0.63 (≥0.35): hit.
- Edge falloff ~5 px at 1400 = 2.5 px per 700: hit.
- Entry glow ~40–60 px radius, tube ~10 px: 4–6 widths, borderline hit.

3. **What works**
- Sky gradient and the dark, violet lower-right mass match ref 02.
- Rod reads as passing through: hidden in the middle, with a pink glow inside the body at ~(740,850).
- Silhouette is crisp and lumpy with a soft 2–3 px falloff. No voxel steps.

4. **Problems, ranked**
- **Colour is paint, not albedo (whole cloud).** Lit and shadow sides have the same bubblegum-magenta hue. Ref 02 has a warm peach-pink lit top and a cool violet shadow. Fix: less saturated albedo (about 0.99/0.90/0.95, not the current deep magenta). Warm the key (about 1.0/0.93/0.85). Let the sky fill carry the violet into shadows. Target lit G/R 0.78–0.84, B/R 0.90–0.95.
- **Billow scale and crispness (centre crops).** Ref 02 is popcorn: many small, hard lobes with dark pockets between them. v05 has medium, soft, waxy lobes. The centre crop shows denoiser smear: blotchy flat patches with no micro-shadow. Tweaking density has not fixed this. Add a small-scale octave (lobe size 1–2% of cloud width) and sharpen density with a Map Range. Density should go 0→full over 1–2 voxels. Use a smaller voxel size and at least 2× samples, so the denoiser keeps the crevices.
- **Rod bloom and exit flare.** In open sky the halo stays about +45 luminance for ±40 px and fades out to ±100 px, roughly 8 tube widths. Ref 02's halo is 2–3 widths. The star glint at (940,990) reads as lens glare, not light in the volume. Fix: raise the glare threshold and cut its size to about 1/3. Drop the streak or star glare. Let the volume scattering make the inside glow.

5. **Research check**
- Contradicts "colour deepens and saturates in core and shadow". Saturation is near-uniform, and the lit side is already the most saturated.
- The inner lobes look soft and even. This goes against "lobes on lobes with self-shadowing between lobes".
- Agrees with multi-scatter brightness (no dirty grey), a darker base, and the emitter glow keeping its hue.

6. **What 8.5 needs**
- Warm lit / cool shadow split through a desaturated albedo and a warm key light. Hit the ref 02 RGB targets within about ±15.
- Small crisp popcorn lobes with visible crevice shadow, and no denoiser smear.
- A tight rod halo with no star glint. Add light film grain to match ref 02.
