# Review v03 (Opus)

1. **Score:** 6.4 / 10. Sphere 5.0, funnel 7.8, line/dot 7.2, plot readiness 6.5.
   Pair: P is v03. Q is closer: P fixes eye rings and funnel radii, but its sphere no longer reads as a ball.

2. **Targets** (orig px)
   - Lines across disc: 13–16 centre-column crossings (ref, same scan: 19–22). Hit, borderline.
   - Rings per eye: 2 and 2. Hit.
   - Eyes upper right / lower left, opposite: hit.
   - Pole ellipses: none. Missed.
   - Dots per line 3–6, uneven: hit.
   - Line width about 0.65 %: hit. Dot about 1.9 %: hit.
   - Funnel 16 × 5: hit. Radii 1, 0.61, 0.43, 0.36, 0.35: hit.
   - Height / rim (centre to centre) 0.46: hit. Minor / major 0.20: hit.
   - Dot at every true crossing: hit.

3. **What works**
   - The funnel profile: thin wide lip, near-vertical throat, back side drawn.
   - Clean monoline strokes and dots at the right scale.

4. **Problems, ranked**
   1. **The sphere outline is broken** (x 450–700). The upper left is empty and stepped, with hairpins at four different x values. Two loops hang below the disc at (675,885) and (885,895). A field on a unit sphere cannot leave the disc, so the bump displaces geometry. Fix: contour the field on an undisplaced sphere, clip to the front hemisphere, and end each clipped line on a dot at the limb, as the ref does on its upper left.
   2. **No pole ellipses, and the bands are too steep** (35–45°; ref 10–25°). Tilt the latitude axis so both poles sit just inside the top and bottom limb. Then the last 1–2 levels close as small ellipses.
   3. **Blot zones.** At the funnel throat sides (x 2220–2240 and 2570–2590, y 660–810), front and back meridians run 4–8 px apart and three dots touch. At the sphere's right limb (1050–1120, 386–436), four lines converge. Fix: rotate the funnel by half a meridian step (11.25°) and merge dots closer than 1.5 diameters.

5. **Research check:** The funnel agrees: a catenoid wireframe. The sphere contradicts "level sets on a sphere", because lines leave the disc. Visible poles should also give polar ellipses, and there are none.

6. **What 8.5 needs:** an undisplaced sphere with limb clipping and limb dots. A tilted axis. About 30 % more levels. Clear the doubling. Trim the bare tail at (495,390).

**Checklist**
1. Yes.
2. Weak yes: a diagonal band with a mild S, with ends that bulge out of the disc.
3. No.
4. No: the tail at (495,390) runs 15 px past its dot.
5. Yes: see problem 3.
6. Yes.
7. Yes.
8. Yes. The hairpin at (560,375) is the only near-kink.
