# Review v01 — eclipse-glow sunrise video

1. **Score:** 6.2 / 10

2. **What works**
- The risen logo (f270) keeps the still's look: gradient, spectral rim, orange halo, crescents. It reads.
- The contact (f140–f210) is the brightest point in the frame, blown out, with grain in the highlight.
- Pacing is sound: tops at about f24, contact at f140, lift-off at f210, rest by f270.

3. **Problems, ranked**

**1. The highlight is two hard slabs, not one blooming sun (f140–f210, x 810–1130).** Measured: two clipped cores, 105–112 px wide and about 50 px tall, with a dark gap between. The target is one core, 20–60 px wide. Fix: add a radial hotspot centred between the bars. Clip only its 20–60 px core. Feed it into a wide bloom (Glare size 8–9, or a 150–300 px Gaussian) mixed at 0.4–0.7. Hold the bar bottoms to about 0.9 so only the hotspot clips.

**2. No sky strip, and the inverted image never fades (all frames, below y = 801).** In open sky (x = 200), the band 8–24 px under the line is 118–101. The sky just above is 121, so the band is darker. Only a pink slab copied from the logo is bright there. At f270, about 70 px of lift, it is still 240, brighter than the logo's own base. Fix: add a full-width strip, 12–24 px tall, filled with flipped sky and gained 1.2–1.5×. Fade the inverted logo from 1.0 at contact to 0 at 100 px of lift. Before separation, stretch it 1.3–2× vertically so it joins the base in a stem.

**3. The haze looks like scanline jitter (f60–f165, edges up to about 100 px above the line).** Rows shift sideways in steps; interiors stay sharp. The f160–f165 strip barely changes between frames. Fix: 2D noise, vertical scale 3–5× horizontal, rising at 20–40 px/s. Blur 4–8 px at the line, 0 by 120 px. Drop contrast 10–20% in the same band.

Minor: hard 1–2 px horizon rule, with a pale seam at f160–f165.

4. **Research check**
- Finding 1 fails: the strip shows no sky and is not bright.
- Finding 2 fails: no stem or omega, and the inverted image neither shrinks nor fades.
- Finding 3 is partly met: brightest, but split and oversized.
- Finding 4 is partly met: right falloff, almost no blur, too little motion.

5. **What 8.5 needs**
- One merged highlight: 20–60 px clipped core, wide bloom across both bars.
- A sky-filled strip, and an inverted image that forms a stem and is gone by 100 px.
- Rising 2D haze with a blur ramp that changes every frame.
- No hard horizon rule.
