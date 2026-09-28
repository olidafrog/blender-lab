# Review — eclipse_sunrise_v04

1. **Score:** 6.7 / 10

2. **What works**
- The risen logo (f270) keeps the still's look: dark tops, gradient body, spectral rim, halo, crescents, grain. It is legible.
- f24 and f60 read as a sunrise: the crescents come up as flat hot dashes, then the tops wobble above a rippled reflection.
- The contact zone is the brightest area from f120 to f200 (clipped, grainy). The shimmer changes between f160 and f165.

3. **Problems, ranked**

**1. The inverted image never leaves (f210–f288).** The logo lifts only about 66 px. The reflection stays a bright pink slab (+113 to +135 levels over the ground) with a hard bottom edge about 30 px under the line. It does not shrink or fade, and it reads as a cut-out. Fix: drive it from lift. Scale Y = clamp(1 − lift/60, 0, 1), opacity 0 by 80–100 px of lift. Feather its mask 8–12 px. Raise the rest height so the base ends 120–180 px above the line.

**2. The highlight is two flat cores, not one merged sun (f140–f195).** Each clipped core is 86–113 px wide (target 20–60) and flat-topped. Between the bars the line stays orange-brown, so nothing reads as merged or blown out. Fix: clip only the central 30–50 px of each core. Add one shared glow centred between the bars, 400–600 px wide and 60–100 px tall, at 40–60 % of core energy.
**3. The heat haze is too weak and too short (f132–f204).** Displacement is about 3–6 px and visible only about 40 px above the line. Bar edges 60 px up stay crisp. Blur and contrast loss are barely there. Fix: displacement 8–14 px at the line, fading to 0 at 120–150 px. Blur 4–8 px at the line with the same fade. Cut contrast 15–25 % in the bottom 60 px.

4. **Research check**
- Finding 1: partly met. The strip below the line is about 13 px tall but only about 15 levels brighter than the sky. It reads as a thin orange rule.
- Finding 2: contradicted. No stem or omega forms at the join (f180–f204 is a flat seam), and the inverted image never shrinks or fades.
- Finding 3: met for brightness, not for "merged".
- Finding 4: displacement only; blur and reach fall short.

5. **What 8.5 needs**
- Reflection shrinks and fades with lift, gone by 100 px.
- One merged contact sun: 30–50 px core, wide shared bloom.
- Haze reaching 120–150 px that blurs as well as displaces.
- A soft-edged strip 12–24 px tall, at least 30 levels above the sky.
- A 10–20 px stem stretch at the join, f180–f210.
