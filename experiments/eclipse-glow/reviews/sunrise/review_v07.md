# Review v07 — eclipse-glow sunrise

1. **Score:** 7.3 / 10

2. **What works**
- The contact is the brightest area from f130 to f200. The line brightens from about 81 to 108 near the logo at f160, and the core clips with grain.
- The start is good. f24 shows only the glowing crescents on the line, and f60 shows a wavy inverted copy under the tops.
- The risen logo (f270) keeps the still's look: crescents, spectral rim, blue-to-pink body, orange halo. It is legible.

3. **Problems, ranked**

**1. The haze does not touch the ground or the sky (f60–f210).** Frame-to-frame change (9 px box blur) in the sky and line at x 100–600 is 0.0–0.7/255. Only the logo's edges wobble, 2–4 px (horizon_f160-165). On the logo, change is 2.6 at the line and 3.9 at 200 px up, so it is not strongest at the line. The grain is also frozen: sky pixels are identical between f160 and f161. Frozen grain reads as dirt on the lens. Fix: displace the full composite (beauty, glow, line, strip) by 5–10 px at the line, falling to 0 at 120–150 px. Scroll the noise up 1–3 px per frame. Add a 3–6 px vertical blur and 15–25% contrast loss in the same zone. Reseed the grain every frame.

**2. The cores are too wide and do not merge (f140–f190).** At f160 the clipped runs are 94 px and about 80 px, one per bar, against a 20–60 px target. Between the bars (row 795, x 930–1010) the value stays at 182–189, so the two lights never fuse into one sun. The white band has the bar's flat, square ends. Fix: clip from a contact mask 30–50 px wide per bar, centred on each bar. Add a wide bloom (150–250 px radius) so the gap between the bars reaches 230–250.

**3. The reflection fades too early and never forms a stem (f200–f230).** At f210 the inverted image is a pale lavender rectangle about 15 px tall (about 120 against 80 beside it). By f228, at about 36 px of lift, it is gone. The target is about 100 px. During contact there is no inverted image, only a smooth bloom falloff. Fix: during contact, stretch the join 1.5–2× vertically into a pink neck 20–40 px tall. After lift-off, shrink it and fade it to 0 over 80–100 px of lift.

4. **Research check**
- Finding 1 (bright strip): contradicted. Away from the logo the strip is about 8 px above sky (74–81 against 62–66). By 12 px below the line it is darker than the sky.
- Finding 2 (stem, then gap): the gap agrees. The stem is missing, and the image fades too early.
- Finding 3 (hottest spot): agrees, but the two cores do not merge into one spot.
- Finding 4 (haze): contradicted. It does not reach the ground layer, and it has no blur or contrast loss.

5. **What 8.5 needs**
- Full-frame haze with blur and contrast loss, strongest at the line, and live grain.
- Cores 30–50 px wide, with a bloom that fuses them.
- A pink stem during contact that fades by about 100 px of lift.
- A bright strip 12–24 px tall along the whole line, 15–25% brighter than the sky.
