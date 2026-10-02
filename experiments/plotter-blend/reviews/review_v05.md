# Review v05 — plotter-blend

1. **Score:** 6.8 / 10 — sphere form 6.0, funnel form 8.0, line and dot 7.0, plot readiness 6.5.
   Pairwise: P (v05) is closer. Its eyes have 2–3 rings and no fragment; Q reads rounder but has 5–6 rings in the upper eye and a stray loop.

2. **Targets**
   - Sphere lines across disc: 12–13 horizontal, 14–15 vertical — hit (reference vertical is 18–20: bands too steep).
   - Rings per eye: 3 upper, 2–3 lower — hit.
   - Eye placement — hit, but axis ~43° (reference ~25°).
   - Polar ellipses — absent, missed.
   - Dots per line ~4–6, uneven, no bare ends — hit.
   - Line width 4 px / 706 = 0.57 % — missed (needs 5 px).
   - Dot 14 px = 2.0 % — hit.
   - Funnel 16 × 5 — hit.
   - Ring radii 1, 0.61, 0.43, 0.36, 0.35 — hit.
   - Height / rim 0.47 — hit.
   - Rim minor / major 0.21 — hit.
   - Dot at every crossing — hit.

3. **What works**
   - Funnel is near-exact: counts, radii, flare, vertical throat.
   - Clean monoline, no kinks or fragments, correct dot size.
   - Both eyes close cleanly.

4. **Problems, ranked**
   1. **Sphere reads as a diagonal fingerprint, not bent latitudes.** Middle bands run ~50°; reference bands run 10–20°. No polar ellipses; no single S stands out. Fix: lower bump amplitude against latitude so the outer eye ring is 0.30–0.38 of the disc (upper eye is 0.43). Tilt the pole 15–20° toward camera so the top and bottom latitudes close into small flat ellipses.
   2. **Tangent overlaps on the sphere.** Lines merge into dark slivers at bottom centre (x 870–950, y 790–830), along the upper eye's inner ring, and at the top-right limb. A pen blots there. Fix: after contouring, find segment pairs closer than 1.5 line widths for over 2 % of the diameter. Clip one at a dot, or shift that level.
   3. **Scalloped left edge.** The left limb is a stack of sharp hairpin tongues with gaps between. Reference lines hug the limb into a continuous round outline. Fix: keep hairpin tip radius at least 3 % of the diameter.
   - Also: funnel front and back meridians sit 1–3 px apart, giving 6–7 px fat strokes at the throat. Use an orthographic camera and drop back meridians within one line width of a front one.

5. **Research check** — Agrees with all findings; nothing contradicted.

6. **What 8.5 needs**
   - Flatter bands, smaller eyes, polar ellipses (tilt and amplitude).
   - Remove sphere tangent overlaps.
   - Round the limb.
   - 5 px lines; dedupe funnel meridians.
