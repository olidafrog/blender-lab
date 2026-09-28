# Review v02 — eclipse sunrise

1. **Score:** 6.6 / 10

2. **What works**
- The risen logo (f270, f288) keeps the still's look and is legible.
- Merge then gap: at f140 the base and a thin inverted slab join at the line. By f210 a dark gap separates them.
- The haze changes every frame (f160–165).

3. **Problems, ranked**

1. **The whole bar bottom clips (f100–f210).** The measured clipped cores are about 110 px wide per bar. The pink bases become white slabs: overexposed logo, not light doubled on water. At f210 the brightest pixels are on the lifted base, not on the line. Fix: stop boosting the logo's own emission. Add a separate additive spot at the line, an ellipse about 40 × 12 px per bar, gain ×3–5, with a wide glare (size 8–9). Fade it over 24 frames after lift-off. Logo pixels stay at 0.85–0.95 of clip.

2. **The haze tears the edges but does not blur them (f60, f140–165).** It makes crisp, stair-stepped horizontal notches that read as a scanline glitch. It reaches only 60–70 px above the line. Fix: use noise at 2–4 cycles per 100 px vertically, 3–6 px amplitude at the line. Extend the mask to 120–150 px. Blur the displaced result by 3–5 px at the line, down to 0 at the top. Cut contrast by 10–20% inside the mask.

3. **The inverted image never goes (f240–f288).** The base rests only 65–70 px above the line. Two pink slabs below the line stay until the last frame. Fix: raise the rest so the base clears the line by 120–160 px. Scale the inverted image's height and opacity to 0 by 100 px of lift.

4. **Research check**
- Finding 1 fails. The strip below the line is only about 10 px tall and barely brighter than the sky (71 vs 66). The horizon is a hard 2 px orange rule, not a vanishing line over bright miraged sky.
- Finding 2 partly holds. The stem forms and the gap opens, but the inverted image does not shrink or fade.
- Finding 3 holds for brightness but fails for shape: the whole base clips, not a 20–60 px spot.
- Finding 4 fails on blur and reach.

5. **What 8.5 needs**
- A separate clipped contact spot, 20–60 px wide, with glare. The logo base stays below clip.
- Haze that blurs and lowers contrast as well as displacing, over 120–150 px, with low-frequency ripples.
- A bright strip 12–24 px tall below the line. Soften the line to 4–8 px.
- The inverted image gone by 100 px of lift, with a higher final rest.
