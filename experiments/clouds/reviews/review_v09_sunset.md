# Review — v09_sunset (target: 03_lone_sunset_cumulus)

1. **Score:** 6.5 / 10

2. **Targets** (sRGB means, 1400 px frame)
- Lit peak 225,200,170 → measured 202,158,138 (x820–900, y690–740). **Missed**: 25–40 low and too orange (G/R 0.78 vs 0.89).
- Shadow side 95,78,86 → measured 22,57,85 (x480–580, y760–860). **Missed badly**: teal, not warm mauve. R is 73 too low.
- Sky top 41,88,120 → measured 15,80,116. **Near miss**: G and B hit, R is 26 low.
- Shadow/lit luminance → 52/165 = 0.31. The reference is about 0.40. **Missed**.
- Edge falloff → 3–4 px on the left and top. In range but on the crisp side for 1400 px (4–8 px scaled).

3. **What works**
- The right lobe has real cauliflower build-up, and lobes shadow each other. It is the best cloud body so far.
- The sky gradient runs from teal at the top to dusk plum at the bottom and reads as dusk.
- The render is clean: no fireflies, no voxel steps, no denoiser smear in any crop.

4. **Problems, ranked**
1. **The left half is teal (x450–770).** The reference shadow tail is warm brown-mauve. The only fill is the blue zenith sky, so the cloud looks like two clouds with a hard vertical terminator at x≈770. Earlier rounds show a tint tweak does not fix this. The fix is energy transport: raise the volume bounces to 16–32, or add an octave multiple-scatter term (Wrenninge: 3–4 octaves, extinction ×0.5 and phase g ×0.5 per octave). Warm sun light then diffuses into the shadowed mass. Also add a warm horizon band (about 150,110,110 linear-scaled) to the world's lower hemisphere so shadow faces pick up mauve. Target shadow R>G, luminance 0.38–0.45 of lit.
2. **The base is a ruler-straight cut with a dark rim (y≈912–925, full width).** Luminance drops to 30 there, darker than both the base above (56) and the sky below (78), then jumps back in 1 px. This is a density step at a hard floor. Fade the floor with a smoothstep over 6–10% of cloud height. Break it up with low-frequency noise of ±2–3% of height, so the base stays flat overall but soft and uneven.
3. **The lit side is too dim and too saturated.** Raise the sun by +0.3 to +0.4 EV and pull its colour toward cream (G/R about 0.88). Also, a few isolated sphere highlights at lower-mid (x570–610, y850–900) read as beads. Raise the minimum lobe radius or blend small lobes into their parents.

5. **Research check**
- "Shadowed crevices stay light": contradicted. A ratio of 0.31 and a near-black-teal core read as single scatter.
- "Base darker than top": agrees.
- "Lobes on lobes, soft few-pixel falloff": agrees on the right. The left silhouette is fuzzier and looks like a different material.

6. **What 8.5 needs**
- Warm the shadow side through multiple scattering plus a warm horizon fill (problem 1).
- Soften the floor and remove the dark rim.
- Make the sun cream and +0.3 EV brighter. Remove the bead lobes.
