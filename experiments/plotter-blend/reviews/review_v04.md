# Review v04 — plotter-blend (Opus)

1. **Score:** 6.7 / 10 — sphere 6.0, funnel 8.0, line and dot 6.8, plot readiness 6.5.
   Pairwise: Q is closer than P. Q reads as a round ball and both eyes close; P is sparse, dangles open strands and has a notched lower-left edge.

2. **Targets** (sphere diameter 701 px)
- Lines across disc: ~18–20 bands (21–25 crossings on a vertical) → **missed**.
- Rings per eye: right 5 + fragment, left 2 → **missed**.
- Eye placement → **hit**.
- Small top/bottom ellipses: top is nested arcs → **missed**.
- Dots per line 3–6 → **hit**; ends on dots → **missed** (two bare ends).
- Line width 0.57 % → **near hit**. Dot 1.9 % → **hit**.
- Funnel 16 × 5; radii 1, 0.61, 0.42, 0.36, 0.35; height/rim 0.47; minor/major 0.20–0.21; dots at crossings → all **hit**.

**Checklist:** 1 yes. 2 partly: the middle is a diagonal stripe field, not one clear S. 3 no: hooked tails notch the lower-left edge (~455–520, 600–760). 4 no: two hooks end bare at the left. 5 no blots; right limb crowds to ~2 line widths. 6 yes. 7 yes. 8 no: a ~10 px teardrop at the right eye's centre (~997, 408).

3. **What works**
- The funnel is close to ship: profile, radii, ellipses and dots match.
- Line weight and dot size suit a plot.
- Top and right limbs wrap cleanly.

4. **Problems, ranked**
1. **Right eye is a bullseye:** 5 rings plus a degenerate teardrop. Lower the raised bump to ~2.5 level steps and widen it ~1.3× for 2–3 larger rings. In the exporter, drop closed strokes shorter than ~3 % of the sphere circumference.
2. **Lower-left: bare hooks, notched outline.** Run the end-dot pass on the final strokes, after cut and dedupe. Let these strands U-turn round the limb (more back reach on that side) instead of hooking inward.
3. **Too many bands, no pole ellipses.** Cut levels until 12–14 bands cross the disc. Tilt the latitude pole 15–25° toward the viewer so the top and bottom levels close as small flat ellipses inside the disc.

5. **Research check:** Agrees. Latitude + bump + trough contours give the bands and eye rings; the funnel is a two-sided catenoid wireframe. Nothing contradicts the findings.

6. **What 8.5 needs**
- Right eye at 2–3 rings, no fragment.
- No bare ends; a round lower-left edge.
- 12–14 bands with pole ellipses.
- One clear S band between the eyes.
