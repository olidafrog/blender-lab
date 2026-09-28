# Review — eclipse_sunrise_v08

1. **Score:** 7.1 / 10

2. **What works**
- The contact moment is now the brightest area of the frame. Frames 130–190 clip at the line; the contact zone averages 225 against 179 for the pink body above it.
- The risen logo (f270) keeps the still's look: dark tops, blue-to-pink gradient, crescent caps, spectral rim. It stays legible.
- The strip below the line is brighter than the sky above it: about 79 falling to 55 over roughly 16 px, against 53 for the sky. The early frames (f24, f60) show inverted tops below the line.

3. **Problems, ranked**

   1. **The contact highlight reads as two thin white slits, not a blooming sun** (f140–f190, bases of the two legs). Each clipped core is 60–100 px wide but only 10–15 px tall, with a flat top that traces the leg's base. The bloom around it barely spreads, and the 100 px gap between the legs stays at about 190, so the two cores never merge. Fix: add a highlight pass. Mask the contact band (±15 px of the line), push it to 3–5× exposure, and put it through Fog Glow (size 8–9, threshold 1.0) so the halo reaches 40–80 px. Add a horizontal streak 300–500 px long along the line. Keep the clipped core itself 30–60 px per leg.

   2. **The heat haze is a slow, regular corrugation that reaches too high** (f96–f288, leg edges). The edges show periodic stair-step teeth 3–6 px deep. Between consecutive frames the edges barely change (blurred difference 3.7 at f160→161, against 0.9 in the sky), so it drifts rather than shimmers. At f270 the teeth still show 70–220 px above the line, while the bases sit 80 px up. The haze also does not lower contrast. Fix: drive the displacement with screen-space noise (two octaves, vertical period 12–30 px). Make the pattern change completely within 3–5 frames. Set the amplitude to 4–8 px at the line, falling to 0 by 120 px above it. Add a vertical blur of 3–6 px at the line, falling to 0, and a contrast drop of 10–20 % in the same band.

   3. **The horizon is a hard graphic line with a dark seam** (all frames; clearest in f210 and f270). A 2–3 px line runs across the full 1920 px at the same brightness for all 12 s. About 4 px above it sits a dark row (37 against 53 for the sky). It reads as a CG mask edge. Fix: feather the ground mask by 6–10 px to remove the seam. Make the line 2–3× brighter within ±300 px of the logo, fading to sky level at the frame edges.

4. **Research check** — Findings 3 and 4 are met in part (see problems 1 and 2). Finding 1 is met. Finding 2 is contradicted: there is no stem or omega phase and no gap of bright sky. At f210 there is only a faint 15 px pink ghost. By f230 (about 40 px of lift) the column under each leg falls straight to line level, with no inverted image. The target was an inverted image that stays visible until about 100 px of lift.

5. **What 8.5 needs**
- A contact bloom that merges the legs into one hot spot, with a horizontal streak.
- Fast screen-space shimmer, fading to 0 by 120 px above the line, with blur and a contrast drop.
- No seam at the horizon, and a line that is brighter under the logo.
- An inverted image that stretches, separates with a visible gap, and fades by 100 px of lift.
