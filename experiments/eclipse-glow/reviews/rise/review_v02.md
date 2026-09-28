# Review v02 — eclipse-glow rise video

1. **Score:** 6.8 / 10

2. **What works**
- f24: the crescents come up first as flattened slivers. It reads as a moonrise.
- Extinction works. At f96 the bars are dim and violet, and they reach full colour as they climb.
- At rest (f270) the still's look holds: gradient, spectral rim, crescents and grain. The logo is legible.

3. **Problems, ranked**
1. **Almost no heat shimmer (f160 vs f161, the bodies above the horizon).** The logo is identical in the two frames. Only the mirror's edges wobble. Nothing is cut into shimmering layers, so the mirage part of the brief is missing. *Fix:* add a Displace node driven by noise stretched about 1:40 into horizontal bands, animated over time. Use 4–10 px amplitude at the horizon, falling to 0 by about 150 px above it. Drift the bands 1–3 px per frame.
2. **The mirror reads as a wet-floor reflection and never leaves (f160, f228, f288, f270 crop).** At f160 it is as tall as the visible part and fully coherent. At rest it still shows the bar bottoms at about 60%. *Fix:* squash it to 25–40% of the source height. Break it into 3–6 slivers with gaps. Fade it to 0 as the logo's lowest point clears the horizon by 40–80 px. From f204 on, keep it at 10% or less.
3. **The horizon is a hard neon stripe (all frames; f160 crop, y≈240).** It is a uniform, full-width 2–4 px line with a hot pink core over the bodies. It reads as an 80s grid line, not atmosphere, and it hardens the ground cut. f132 also shows a squashed pill smear off the left bar's step. *Fix:* use a soft haze band instead: a vertical Gaussian of 20–40 px, peak at most 30% of rim brightness, fading toward the frame edges, composited under the logo. Clamp the squash near the horizon so shapes cannot collapse into pills.

4. **Research check**
Extinction and flattening agree with the research. Heat haze is contradicted: there are no visible layers. The mirror is not squashed or broken up, and it persists at rest. That contradicts "all four fade with height". A dark red wash also covers the rested bar bottoms in f270, so the extinction band reaches too high.

5. **What 8.5 needs**
- Visible, banded, animated shimmer near the horizon.
- A squashed, broken mirror that is gone by f204.
- A soft haze band instead of the neon line.
- The rested bottoms back to the still's lilac-pink.
