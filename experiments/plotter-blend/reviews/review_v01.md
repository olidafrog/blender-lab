# Review v01 — plotter-blend

## 1. Score: 6.0 / 10
Sphere 4.5 · funnel 7.5 · line/dot 7.0 · plot readiness 6.0. No pair.

## 2. Targets
(px in the 3200 px render; sphere ≈ 700 px)

- Lines across disc: 11–14, hit.
- Rings per eye: 1 each, missed.
- Eye placement: UR / LL opposite, hit.
- Polar ellipses: absent (hairpins), missed.
- Dots per line: 2–5, hit (2 bare stubs).
- Line / diameter: 0.64 %, hit. Dot: 1.9 %, hit.
- Funnel 16 × 5, hit. Radii 1, **0.67**, 0.47, 0.39, 0.35: ring 2 missed. Height 0.47, hit. Minor/major 0.20, hit. Crossing dots, hit.

Checklist: 1 no (1 ring per eye). 2 no (S spreads through a tilted stack, crosses nothing). 3 no (hairpins, cusps, notch). 4 no (stubs at left cusp, lower-left hook). 5 yes, mild (right limb, x ≈ 1060, y 530: dots touch the next line). 6 mostly (lip a little narrow). 7 yes. 8 no on sphere (cusps), yes on funnel.

## 3. What works
- Funnel count, taper, tilt and dots read as the reference.
- Pen and dot sizes match; one clean weight.

## 4. Problems, ranked
1. **Sphere outline.** Only the front hemisphere is drawn, clipped at the limb. The edge breaks into hairpins (bottom, x 700–1000), cusps with stubs (left limb, y 480–860) and a lower-left notch. The reference is see-through: back contours wrap the limb, so the outline is a clean circle, polar latitudes close as ellipses, and lines cross. Fix: trace each level set as a closed curve over the whole sphere; project with no hidden-line removal; tilt the view 15–20°.
2. **Shallow eyes.** Raise each bump until its peak clears the saddle level by 2.5–3 contour intervals, giving 2–3 closed rings.
3. **Doubled funnel stroke** (y ≈ 516, x 2290–2510): ring 2's front lies on ring 3's back. Set rings 2 and 3 to 0.61 and 0.44, at least 3 line widths apart. Add a check that fails strokes closer than one line width for longer than two dot diameters.

## 5. Research check
Partly contradicted. The reference sphere's lines cross, with dots at crossings (ref crop ≈ (455, 370), (560, 370)). Level sets on one visible hemisphere cannot cross, so the back side is drawn too. Funnel findings agree.

## 6. What 8.5 needs
- See-through closed level sets: round outline, polar ellipses, an S-band that crosses the latitudes.
- 2–3 closed rings per eye.
- Funnel ring 2 at 0.61; no overlapping strokes.
- No cusps or bare stubs.
