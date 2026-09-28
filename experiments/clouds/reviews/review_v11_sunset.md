# Review — v11_sunset (target: 03_lone_sunset_cumulus)

1. **Score:** 7.1 / 10

2. **Targets**
- Lit peak ~225,200,170: measured 221,172,145 (top 1%: 239,186,156). **Missed.** Green and blue are ~25–30 low, so it reads salmon, not cream-peach.
- Shadow side ~95,78,86: measured 68,75,93 (Y 75). **Missed.** Luminance is close, but the hue is blue-grey, not mauve.
- Sky top ~41,88,120: measured 15,80,116. **Missed.** Red is −26, so the sky is teal and too saturated.
- Edge falloff (3–4 px at this width): a 10–12 px ramp, then a **1 px step of 25–28 levels** (right edge x≈983, top y≈670). **Missed.**

3. **What works**
- A convincing multi-scale billow on the right tower, with self-shadowed lobes and light crevices.
- The lighting direction is right: warm from low right, a cool unlit side, and a flat, darker base (Y 34–60).
- The render is clean. No fireflies, voxel steps or denoiser smear in any crop.

4. **Problems, ranked**
1. **Left lobe dissolves into the sky (x 460–700, y 700–900).** Its Y is 69–75 against sky 72–76, a contrast of about 1.0. It reads as thin blue smoke. In ref 03 the left lobe (Y 65) is darker than the sky (Y 90), mauve, with warm-lit top rims. Fix: raise the sun 5–10° or swing it toward camera, so the left tops get 30–50% of the right side's direct light. Tint the shadow fill toward the lower-sky mauve (~90,80,90), not the teal zenith. More ambient alone only lifts it to sky grey.
2. **Hard cut at the silhouette.** Every edge ends in a 1 px jump from a density threshold or mask clamp. Replace the hard step/clamp with a smoothstep over the outer 3–5% of the density range.
3. **Grade: lit side too orange, sky too teal.** Lit G/B should be ~0.89/0.76 of R (now 0.78/0.66). Set the sun colour to ~1.0,0.88,0.74. Lift the zenith red to ~40. Make the mid-sky at the cloud a neutral lavender (~90,89,98), and add a rose band (~88,78,79) at 70–80% height.

5. **Research check**
- Multiple scattering, light crevices and a dark base agree with the research.
- Shadows take the *zenith* colour. At dusk the fill comes mostly from the lower mauve sky, so this partly contradicts "shadowed crevices take the sky's colour".
- It contradicts "crisp silhouette, soft few-pixel falloff": the outline ends in a hard step.

6. **What 8.5 needs**
- A left lobe darker than the sky, mauve, with warm rims.
- A 3–5 px outline falloff with no 1 px step.
- A creamier lit side (~225,200,170).
- A sky with a lavender mid-band and a rose low band.
