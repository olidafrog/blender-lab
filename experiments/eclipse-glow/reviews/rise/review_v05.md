# Review v05 — eclipse-glow rise video

1. **Score:** 7.1 / 10

2. **What works**
- The rested logo (f270) keeps the still's look: dark-to-blue-to-pink body, spectral rim, crescent caps, grain. It is legible.
- The first contact (f24) is right. The crescents come up as flat, squashed orange streaks, which reads as refraction at the horizon.
- The sky has warm extinction near the ground, and the logo body is dimmer and more purple low down (f60) than at rest.

3. **Problems, ranked**

**1. The mirror reads as a lake, and it does not fade (f132–f288, f270 crop).** Below the horizon there is a tall, bright, wavy copy of the bars, about 100–200 px deep, with vertical ripple streaks. That is a water reflection. At f270 the logo is about 60 px above the horizon, but its full pink reflection is still there. An inferior mirage is a thin, squashed, broken strip that hugs the horizon, and it goes away as the object rises. Fix: squash the mirror to 0.2–0.35 of the source height. Key its opacity to the height of the logo's lowest point above the horizon: 100% at contact, 0% by about 40 px of clearance. Break it into horizontal bands, not vertical streaks.

**2. The shimmer is almost frozen (f160–f165 crops).** The slice pattern on the bar edges is nearly the same in all six frames. Heat haze boils. As it is, the shimmer looks like a baked distortion. Fix: animate the noise phase so a given band moves 2–5 px per frame. Use 2 octaves at different speeds so the pattern never repeats in under 1 s.

**3. The pacing is front-loaded, and the halo is thin (sheet).** Almost all of the rise happens by f132 (5.5 s). After that the logo creeps and nothing else happens for 6.5 s. Also, the rested halo is narrower and dimmer than the still's broad orange bloom. Fix: use an ease-in-out rise so the bottom clears the horizon at about f200–f220, then hold for 2–3 s. Widen the halo glow radius by 1.5–2× to match FINAL_eclipse_logo.png.

4. **Research check** — Extinction and refraction agree with the research. Heat haze is present in shape but not in motion (finding 3 implies boiling). The mirror contradicts finding 4: it is not squashed, and it does not fade with height. The horizon line is a uniform, hard neon line across the full frame. It is on style, but a softer 2–4 px falloff would sit better with the haze.

5. **What 8.5 needs**
- A squashed mirage mirror that fades out as the logo clears the horizon.
- Shimmer that visibly changes every frame.
- A slower, eased rise that ends near f210, then a hold.
- A halo width that matches the still.
