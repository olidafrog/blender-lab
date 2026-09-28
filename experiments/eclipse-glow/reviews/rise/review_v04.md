# Review v04 — rise video

1. **Score:** 6.7 / 10

2. **What works**
- The rested logo (f204–288, rested_f270) keeps the still's look. The gradient, spectral rim, crescents, halo and grain all hold, and the logo reads clearly.
- The start of the rise follows the research. The f24 caps are flattened and dim. At f60–96 the bars are dimmer and more purple, and they reach full colour higher up.
- The shimmer moves. The six crops from f160 to f165 show a different ripple pattern on each frame, so the haze is not frozen.

3. **Problems, ranked**
- **A dark holdout halo cuts holes in the horizon.** f160, f161 and f160–165, around every bar and most of all right of the hourglass. A dark-brown rounded block, about 80–120 px wider than the geometry, blanks out the horizon glow. It is the logo's glow region acting as a black matte. The shimmer then distorts that matte's edge, so dark jagged blobs sit where the glow should be. Fix: build the ground holdout from the logo's alpha only, with no glow pass, and composite the halo additively over the horizon. The halo must never darken what is behind it (max darkening 0%).
- **The heat haze looks like VHS tearing, not a mirage.** Horizon crops, 0–60 px above and below the line. The bands are 3–6 px tall and shift 10–15 px sideways with hard sawtooth edges. They are much crisper than the soft logo. Fix: make the bands 12–24 px tall at 1080p and the offset 3–8 px, with a smooth (sine or blurred-noise) profile. Blur the displaced result 1–2 px, and let the distortion fall to zero within about 8% of frame height above the horizon.
- **The horizon line is a neon laser, not an atmosphere.** Every frame from f1. It is a hard, even orange stroke across the full width. At f132–168 it lies over the pink bar bottoms. Sky and ground are the same near-black, so only the line separates them. Fix: replace the line with a warm sky glow that fades upward over 10–20% of frame height. Make the ground 20–40% darker than the sky just above it. If a line stays, keep its peak under 50% of its current brightness and at most 2–4 px thick.

4. **Research check**
The video meets findings 1 and 2: it is redder, dimmer and flattened low. It meets finding 3 in placement but not in character (see Problem 2). It contradicts finding 4, "all four fade with height". At f204–288 the logo floats about 60 px above the horizon, yet the pink mirror below stays strong and sharp-edged. The mirror should be gone, or under 15% opacity, once the logo's base clears the haze band. The mirror is also flat pink blocks with no orange rim or glow, so it reads as a paste-up, not an image of the logo.

5. **What 8.5 needs**
- Holdout from alpha only, with the glow added on top (Problem 1).
- Softer, taller, smaller-amplitude haze bands (Problem 2).
- Sky glow in place of the laser line, and a darker ground (Problem 3).
- Mirror opacity keyed to the logo base height, falling to near zero at rest. The mirror should keep the rim and glow.
- Optional: shorten the static hold at the end (f204–288, 3.5 s). Add slow drift or a haze breath so the last shot is not a freeze frame.
