# Review v05 — eclipse-glow sunrise

1. **Score:** 7.1 / 10

2. **What works**
- The contact moment (f140–f190) now has a real clipped core at each lower bar. I measured 54–80 px wide, 7–18 px tall, at y≈786–804 on a line at y≈800. It is the brightest spot in the frame. The glow between the bars reaches about 180/255 at x≈975, so the two bars start to merge.
- The risen logo (f270) keeps the still's look: crescents, spectral rim, blue-to-pink body, orange halo. It reads cleanly.
- The early frames (f24, f60) work: the crescents break the line as small hot blobs with short reflections under them. It is a good sunrise opening.

3. **Problems, ranked**

**1. The highlight is two flat ovals, not a blooming sun (f140–f190, base of both lower bars).** The cores follow each bar's width, so they read as lit discs on a floor. The bloom around them dies within about 40 px, and the red horizon line is equally bright across the whole frame. The designer asked for "almost blown out", merged, grainy and doubled light. Fix: add a wide bloom driven only by the contact mask, with a radius of 150–250 px and a peak of 1.5–2.5× the current glow. Add a horizontal streak along the line, 600–900 px long, fading out. Brighten the line within ±300 px of the contact point and dim it to about 60% elsewhere. Raise grain 1.5–2× inside that zone. Keep each clipped core at 20–60 px (f140 is 76–80 px, too wide).

**2. The heat haze is edge wobble, not haze (f60–f200, lower 150 px).** In horizon_f160-165 the bar edges ripple by 2–4 px and change a little from frame to frame. The pink interiors, the gradient and the glow do not shimmer or lose contrast. Fix: displace the whole beauty pass, glow included, not only the alpha edge. Aim for 4–10 px at the line, falling to 0 by 120–150 px. Use a noise that scrolls upward at 1–2 px per frame, stretched 3–4× horizontally. Add a vertical blur of 3–6 px at the line, falling to 0. Lower contrast by 15–25% in the same zone.

**3. The reflection is a hard-edged rectangle with no stem or gap stage (f160, f210).** Below the line, each bar's inverted image is a flat block, about 24 px tall, with square corners and a hard bottom. At f210 it floats as a pale lavender slab under a lifted bar. It never stretches into a stem joining the body, and it does not shrink. Fix: squash the reflection vertically (0.3–0.5×). Feather its bottom over 10–16 px. Link its height to the lift, so it stretches into a stem while in contact, then shrinks and fades to 0 by 80–100 px of lift. Tint it from the body's bottom colour (pink), not lavender.

4. **Research check**
- Finding 1 (bright strip): partly met. The strip is bright under the bars (y 806–830), but away from the logo it is only the red line plus about 12 px of falloff.
- Finding 2 (stem, then gap): contradicted. There is no vertical stretching or omega shape. The inverted image keeps a fixed rectangle, then slides off.
- Finding 3 (hottest spot): met for brightness, not for bloom or grain.
- Finding 4 (haze): only the displacement part is present, and it is weak. Blur and contrast loss are missing.

5. **What 8.5 needs**
- A contact-driven wide bloom with a horizontal streak, plus a local line boost and extra grain at the contact point.
- Haze that moves the full image and glow, with vertical blur and contrast loss, strongest at the line.
- A soft, stretching reflection that forms a stem, then a gap, then fades by about 100 px of lift.
