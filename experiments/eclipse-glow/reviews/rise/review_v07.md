# Review v07 — eclipse-glow rise video

1. **Score:** 7.2 / 10

2. **What works**
- The risen logo keeps the look of the still: sunset gradient body, spectral rim, crescent caps, orange halo, grain (f204–288, rested_f270). It stays legible.
- The start of the rise reads as a moonrise. The caps at f24 are squashed flat with a small mirror below them. At f60 the bars are dim and red-shifted. Extinction and refraction both show and both fade with height.
- The shimmer is live. Across f160–165 the edge wobble and the mirror lumps change shape on each frame, and there is no frozen pattern.

3. **Problems, ranked**
- **The mirage is too thin and reads as aliasing, not haze (f160–165, bottom 40 px of each bar).** The displacement lives only in a band about 40 px tall, and it looks like jagged edges on the bar sides. There are no visible horizontal layers. The mirror is a dark smudge that reaches about 30 px below the line. Fix: widen the haze band to 100–160 px above the horizon, with a falloff. Slice it into horizontal strips 6–12 px tall that shift 3–6 px sideways at the line. Add a slight vertical stretch or squash (±10–15 %) for each strip. Make the mirror 60–120 px deep, flipped, squashed to 40–60 % height, broken by the same strips, at 25–40 % brightness.
- **The horizon is a hard graphic line (every frame, full width).** A 1–2 px bright orange line sits on flat black ground. It reads as a synthwave laser line, not a horizon seen through air, and it is the hardest edge in the frame. Fix: bring its peak down to 50–60 % of its current value and blur it to 6–12 px. Add a low glow band 20–40 px tall that bleeds below the line. Lift the ground just under the horizon to a warm dark (about 3–5 % of the sky value) that fades to black over 150–250 px, so the ground has depth.
- **The pacing front-loads the rise, then stops acting (f160–288).** The logo clears the horizon near f160. It then creeps about 70 px over 5 s, and no atmospheric effect touches it. The last 40 % of the video is a static still. Fix: stretch the rise so the bottom clears the horizon at f200–216 with a long ease-out. Hold for no more than 3 s. Keep a faint residual shimmer (1–2 px) and a faint mirror under the bar bottoms until the end.

4. **Research check**
It agrees on extinction, refraction and the fade with height. It only half-meets the heat-haze claim, because there are no visible layers. It only half-meets the inferior-mirage claim, because the mirror is too short and too dark to read as a flipped image. Nothing contradicts the research outright.

5. **What 8.5 needs**
- Widen the haze band into visible layered strips, and give it a deeper, squashed, broken mirror.
- Soften the horizon line and add a warm falloff into the ground.
- Retime the rise to clear at about f200–216, and keep a trace of shimmer during the hold.
