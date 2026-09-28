# Review — v04

1. **Score:** 6.4 / 10

2. **Targets**
- Paper: 208–234, 203–228, 199–226. Values hit, but warm (R>G>B); the reference is neutral-violet. Minor.
- Lit field: 191–198, 179–185, 200–207. Hit (G at the floor), B>R>G correct.
- Relief tops: 190–198, 179–185, 199–207 vs 228, 222, 233. **Missed by about 35.** The tops match the field.
- Rim, shadow side: 74–94, 63–85, 76–98 vs 93, 79, 105. Value hit, hue **missed**: R≈B, grey-mauve rather than violet.
- Rim, lit side: 228–241, 216–229, 236–247 vs 191, 184, 200. **Missed**, 35–45 too bright over a wide band.
- Cast-shadow core: 48, 43, 42 vs 63, 48, 49. **Missed**: too dark and neutral grey. The reference is warm brown.
- Seal width: 1127 px, 93%. Hit (slightly large).
- Rim bead: 12% on the left, 15% on the right. **Missed** on the right.
- Stamped field: 74%. Near miss (target 78%).

3. **What works**
- Composition and key direction are right: upper-right key, shadow falls lower-left.
- A rolled bead with a steep inner wall at a true circle, and an irregular outer blob.
- The emblem reads as pressed out of the same wax, with a correct lit edge and shadow edge.

4. **Problems, ranked**
1. **The whole seal reads as soft-touch plastic or fondant.** There is no specular sheen and no micro texture at 1:1. The shadows lack violet saturation. In the reference, the top-right rim shows satin specular streaks, and the dark tones go to about 45, 32, 58. Fix: roughness 0.3–0.4 with a low-frequency roughness map (0.25–0.5) so streaks appear. Add fine bump noise (≈0.05–0.1 mm). Make the subsurface/absorption colour a deeper violet so the core shadows reach B−R ≥ +12.
2. **The relief tops are flat plateaus at field brightness.** The emblem looks like a UI bevel-and-emboss, not a moulded form. Fix: dome the tops (a profile curve or a displacement falloff from the edge distance), so the crowns face the key and reach about 225–235. Widen the inner-rim groove on the right (x≈1020–1075). It should be a 40–60 px band near 45, 32, 58, not one dark pixel.
3. **The flow lines are wrong.** They are a few bold, snaking ridges in the lower half, like cracks or veins, and they cross the tops of the logo bars (see crop 450_950). Fix: use many faint hairlines with a height of ≤0.02 mm, spread radially across the whole field. Mask them to zero on the relief.
- Also: the lit right rim is a broad, shapeless white plane (crop 1050_650), and there is a pale halo on the paper above and right of the seal. Lower the key or add more rim curvature variation. Check for glare or bloom.

5. **Research check**
- "Shadows deep, saturated violet": **contradicted**. They are grey-mauve.
- "Satin, not glossy": the render goes too far toward matte and shows no sheen at all.
- "Faint hairline flow lines": **contradicted**. They are bold and sparse.
- Opaque, short scatter, no edge glow: agrees.

6. **What 8.5 needs**
- Satin specular with roughness variation, plus micro bump.
- Violet-saturated shadows. The cast-shadow core warm, near 63, 48, 49.
- Domed, brighter relief crowns and a deep, wide inner-rim groove.
- Faint radial hairline flow lines, masked off the relief.
- Lit rim brought down to about 190–210.
