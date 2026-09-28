# Review v06 — pink_rod (target: 02)

1. **Score:** 6.7 / 10

2. **Targets** (render 1400 x 1712)

- Lit top 180,146,170 → 199–220,139–163,166–188. Missed (R +20–40).
- Left 183,123,148 → 221–234,150–159,171–181. Missed (about 40 too bright).
- Violet shadow 148,101,135 → 92–97,73–85,114–125. Missed (too dark, blue-grey).
- Bottom 127,76,104 → 124,104,135. Missed on hue (lilac-grey, not magenta).
- Sky top 63,109,155 → 68,108,153. Hit.
- Sky bottom 134,165,184 → 130,158,179. Hit.
- Shadow/lit ≥ 0.35 → 0.46. Hit, but only because the lit side is too bright.
- Edge falloff 2–4 px/700 → 2.5 px/700. Hit. The right edge has a dark fringe below sky value.
- Entry glow 3–5 tube widths → 8–12. Missed.

3. **What works**

- Billows at several scales, and a crisp rounded silhouette with a soft falloff.
- The rod is hidden inside the volume and shows through as glows along its path.
- Sky matches closely. No voxel steps and no fireflies.

4. **Problems, ranked**

1. **Upper-right and core shadows are dirty violet-grey (about 95,75,118).** The reference shadow stays light pink-magenta. The render is keyed from the left, so half the cloud is in shadow. The reference key is front-upper-left, with a bright pale-lilac front. Fix: move the sun to 30–40° off the camera axis, from front-upper-left. Add multi-scatter fill: 16+ volume bounces, or an albedo-tinted emission scaled by (1 − sun transmittance). Target shadow luminance 105–125.
2. **Emitter glows are too big and too red.** The centre spot (about 740,860) is red (184,61,100), with radial streaks and a hard-edged wedge in the centre crop. Fix: cut rod emission inside the volume to 0.3–0.5×. Keep the glow within 3–5 tube widths, in the rod's pink. Give that area more samples before denoising. The outside bloom is 30–40 px per side; the reference has 6–10. Raise the Glare threshold, or set its mix to 0.3–0.5.
3. **The mid-scale surface is waxy.** In the centre and bottom-left crops, the small lobes are low-contrast and smeared. The reference has crisp micro-cauliflower everywhere, plus film grain. Fix: add a displacement octave at about 0.3× the smallest lobe. Use more samples and less denoising, then add 1–2% grain.

5. **Research check**

Contradicted: "crevices stay light" (upper-right looks smoky), "colour saturates in shadow" (it goes blue-grey), and "glow keeps the emitter's hue" (it shifts red). Edges and lobe structure agree.

6. **What 8.5 needs**

- A front-upper-left key plus multi-scatter fill, so the shadow is about 148,101,135 and the base about 127,76,104.
- The lit side about 15% darker.
- Pink inner glows within 3–5 tube widths, with no streaks, and a thinner bloom.
- Crisper micro-billows and film grain.
