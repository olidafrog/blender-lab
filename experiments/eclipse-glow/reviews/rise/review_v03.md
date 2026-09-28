# Review v03 — eclipse-glow rise video

1. **Score:** 6.6 / 10

2. **What works**
- The rested logo (f204–288, crop f270) keeps the still's look: dark-to-blue-to-pink body, spectral cyan/yellow rim, peach crescent caps. It is legible.
- The sequence reads as a rise. Caps first and squashed (f24), then bars, then the steps (f132) and a settle by about f200. The pacing is calm and ends with a soft ease-out and a 3.5 s hold, which suits the music.
- The inferior mirror is correct in direction. The pink bottoms sit just under the horizon and the blue sits lower, broken into ripples (f160).

3. **Problems, ranked**

1. **The shimmer is frozen.** In crops f160 and f161, the comb teeth on the bar edges and the mirror ripples are almost identical. The blurred luma difference in the horizon band is about 1/255, which is grain and rise only. In the video this will read as a static serrated edge, not heat haze. Fix: drive the displacement noise with time, so the rows slide sideways 1–3 px per frame and the pattern decorrelates in 6–12 frames. The mirror ripples need the same, 1.5–2× faster.

2. **The horizon is a laser line, not an atmosphere.** From f1, a full-width orange stripe at even strength runs edge to edge, before any light source exists. It reads as a Tron grid line and competes with the logo. Also, the body meets the horizon with a hard, bright pink line (f160, y≈238). Fix: make the horizon a soft haze band 40–80 px tall, peak ≤ 50% of its current value, and fade it to near zero at the frame edges. Tie its brightness to the logo's height, so it is dim at f1 and brightens under the logo as it rises. Feather the ground mask 6–12 px so the pink cut is soft.

3. **The haze lingers on the risen logo.** In f270, the lower bars show sawtooth sides for about 200 px above the horizon, and the halo is tighter than in the still. Near-ground effects should be gone once the logo has cleared the horizon. Fix: make the shimmer falloff about 2–3× shorter, so it is below 1 px within 60–80 px of the horizon. Bring the halo radius back to the FINAL still's value on the rested frames.

4. **Research check**
Refraction flattening (f24) and the broken mirror agree with the research. The haze does not agree: it is static, and it stays strong at heights where it should have faded. Extinction is weak. At f132–168 the brightest part of the logo is the pink base right at the horizon, which is the opposite of "dimmer and redder near the horizon". The glowing horizon stripe also adds light where the atmosphere should take it away.

5. **What 8.5 needs**
- Animate the shimmer and mirror ripple over time.
- Replace the stripe with a soft, logo-lit haze band, and feather the ground cut.
- Dim and redden the logo by 30–50% within about 100 px of the horizon.
- Clean edges and the full still halo once the logo has risen.
