# Review — eclipse_sunrise_v03

1. **Score:** 6.8 / 10

2. **What works**
- The risen logo (f270) keeps the still's look: the sunset gradient, the spectral rim, the crescents and the halo. It is legible, and the grain is right.
- The contact zone is the brightest area in the frame from f132 to f180. It clips (255), glows orange into the sky, and fades out by f210 without a pop.
- The haze changes on every frame in f160–165, and it is strongest at the line.

3. **Problems, ranked**
- **The contact highlight is two white slabs, not a blooming sun point (f140–f180).** The clipped core is each bar's full width: 100–112 px × about 35 px (y 773–811), with hard vertical sides. It reads as painted-white bar bottoms. It does not read as light doubling on water. Fix: build the clip from a separate additive term. Use an elliptical Gaussian centred on each bar's contact point, with its core 30–50 px wide and 10–16 px tall. Stretch it sideways along the line (glare 3–5× wider than tall). Keep the body under the core at ≤ 0.9 before bloom. Add a horizontal streak on the line of 300–500 px at 30–50% intensity.
- **The inverted image never leaves (f210–f288).** At f288 the base is about 70 px above the line (y 730 vs 800). The reflection slab at y 820–832 is still at luminance 100, against 48 around it. It keeps a flat, cut top. There is no stretched stem at contact and no shrink. Fix: drive the reflection's height and opacity from the lift. Stretch it vertically 1.5–2× while the gap is < 10 px, so the two images join in a neck. Then scale its height and alpha to 0 linearly by 60–80 px of lift. The inverted image must be gone by f240.
- **The haze reads as scanline tearing, not shimmer (f140–f168, bar edges).** The offsets are per-row steps 1–3 px tall, which give stair-step jaggies. The blur is weak. Nothing above about 90 px is touched. Fix: use a smooth 2D noise for displacement, with vertical wavelength 8–20 px and horizontal 40–80 px. Set amplitude to 6–10 px at the line, falling to 0 at 120–150 px. Use a matching directional blur, radius 4–8 px at the line falling to 0. Lower the contrast by 10–20% in the same mask.

4. **Research check**
- Finding 1 is partial. The strip under the line (y 800–812) is brighter than the sky above (77 vs 62), but it is only about 12 px. It is a uniform razor rule across all 1920 px. It does not brighten under the sun.
- Finding 2 is contradicted. There is no stem or omega shape, and the inverted image does not shrink or fade.
- Finding 3 is met in brightness, but its shape is wrong.
- Finding 4 is met in falloff, but the texture and blur are wrong.

5. **What 8.5 needs**
- A narrow elliptical clipped core with a lateral streak, replacing the full-width slabs.
- A reflection that stretches into a neck at contact, then shrinks to nothing by 60–80 px of lift.
- Smooth 2D noise haze with blur, reaching 120–150 px.
- A horizon strip 16–24 px tall that brightens locally, 2–3× more within about 300 px of the contact point.
