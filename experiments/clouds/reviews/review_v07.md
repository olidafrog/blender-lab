# Review v07 — pink_rod (target: 02)

1. **Score:** 6.8 / 10

2. **Targets** (masked cloud pixels, sRGB)
- Lit top 180,146,170 → 201,126,155. Missed (G 20 low, oversaturated).
- Left 183,123,148 → 225,148,171. Missed (about 40 too bright).
- Violet shadow 148,101,135 → 145,84,120. Near miss (G, B about 16 low).
- Bottom 127,76,104 → 120,68,102. Hit.
- Sky top 63,109,155 → 63,106,152. Hit.
- Sky bottom 134,165,184 → 129,158,179. Hit.
- Shadow/lit ≥0.35 → 0.60 side, 0.49 base. Hit.
- Edge 2–4 px/700 → about 5. Missed (slightly soft).
- Entry glow 3–5 widths → about 4. Hit.

3. **What works**
- The sky gradient and the dark mauve base are on target.
- The rod vanishes inside the volume and glows through near the surface.
- The shadows stay light and take a violet sky cast. It does not look like smoke.

4. **Problems, ranked**
1. **Colour reads as paint (whole cloud).** The cloud is one salmon pink. The core (180,78,111) gets its saturation from the rod, not from depth. Fix: set albedo to about (0.99, 0.94, 0.97) and make the sun white to slightly cool. Target lit-top G/R of 0.78–0.82 (now 0.63). Cut the rod's light into the volume by about 50%.
2. **Wrong key and no macro form.** The left side is brightest (225 against 201 on top). The body is a round ball of same-size popcorn with no big lobes shadowing each other. Ref 02 has 2–3 large masses, a deep fold left of centre, and brightest tops at upper right. Fix: build the base from 2–3 overlapping big lobes (metaball or SDF union) before the noise. Key from upper right. More noise amplitude will not fix this.
3. **Denoiser smear and rod glare (centre and tl crops).** The inner lobes look waxy and have lost fine detail. The rod's glare in open sky is about 3 tube widths per side; the ref is about 1. The entry points show white starbursts. Fix: more samples, denoise with albedo and normal passes (Accurate), then add grain. Cut glare to ≤1.5 widths and clamp the entry highlight.

5. **Research check**
- Deeper colour in core and shadow: present, but the emitter causes it. Partly contradicted.
- Dark base and sky-tinted crevices: agree.
- Lobes on lobes with crisp edges: contradicted. The lobes are one scale, and the denoiser smears them.
- Emitter hue and spread: agree.

6. **What 8.5 needs**
- Near-white albedo, so depth makes the colour and the lit tops reach lavender-white.
- 2–3 self-shadowing macro lobes, lit from the upper right.
- A crisp 2–4 px edge with no smear. Add grain.
- A thin rod glare with no starbursts.
