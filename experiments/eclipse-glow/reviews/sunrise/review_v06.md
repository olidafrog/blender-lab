# Review v06 — eclipse-glow sunrise

1. **Score:** 7.4 / 10

2. **What works**
- The contact now blooms. At f160 the line brightens from about 60 to 110–125 within ±400 px of the logo. The core is clipped and grainy. It is the brightest area in the frame from f130 to f200.
- The gap stage exists. At f210 the base sits about 18 px above the line, with dark sky between it and the inverted image.
- The risen logo (f270) keeps the still's look: crescents, spectral rim, blue-to-pink body, orange halo.

3. **Problems, ranked**

**1. The reflection is a hard rectangular slab (f140–f210, under both lower bars).** Each inverted image is a flat block about 24 px tall. Square corners, hard bottom, lavender tint. It never stretches into a stem, so the merge stage is missing. It is gone by about 40 px of lift; the target is about 100 px. Fix: squash it to 0.3–0.5× height and feather the bottom over 10–16 px. During contact, stretch the join 1.5–2× vertically into a neck. After lift-off, shrink it and fade it to 0 over 80–100 px of lift. Tint it pink.

**2. The haze is edge ripple only (f60–f200, lower 150 px).** Bar edges wobble 2–4 px (horizon_f160-165). The interiors, glow and line do not shimmer. Frame-to-frame change is no larger at the line than 200 px above it (mean about 2/255). Fix: displace the full beauty and glow pass, 5–10 px at the line, falling to 0 by 120–150 px. Scroll the noise upward at 1–3 px per frame. Add a 3–6 px vertical blur and 15–25% contrast loss in the same zone.

**3. The clipped cores are too wide and do not merge (f150–f190).** Each core fills its bar's width, about 70–95 px (x 816–910 at f170), against a 20–60 px target. Between the bars (x≈975) the peak is about 193, so the lights never fuse. Fix: clip from a contact mask 30–50 px wide per bar. Add a bloom of 150–250 px radius so the gap between the bars reaches 230–250.

4. **Research check**
- Finding 1 (bright strip): weak. Away from the logo the strip is about 10 px at 74–77, against sky at 61–63.
- Finding 2 (stem, then gap): the gap agrees. The stem is missing, and the image fades too early.
- Finding 3 (hottest spot): agrees.
- Finding 4 (haze): weak displacement. Blur and contrast loss are missing.

5. **What 8.5 needs**
- A soft reflection that forms a stem, then fades by about 100 px of lift.
- Full-image haze with blur and contrast loss, strongest at the line.
- Cores 30–50 px wide, with a bloom that merges them.
- A bright strip 12–24 px tall along the whole line, 15–25% brighter than the sky.
