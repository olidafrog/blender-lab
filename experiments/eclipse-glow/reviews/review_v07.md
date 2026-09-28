# Review — eclipse_logo_v07

1. **Score:** 7.1 / 10

2. **Targets** — none set.

3. **What works**
- The body gradient reads right: near-black tops, saturated blue in the middle, lilac to pink at the base. The palette matches the reference's upper two-thirds.
- The mark is legible. The two stepped bars and the pinched dot match the SVG proportions. The dot's waist is clean.
- The surfaces are clean at 1:1: no seams, faceting or streaks. The grain is even and film-like.

4. **Problems, ranked**

1. **Halo is uniform and fills the negative space (whole mark, worst in the centre crop).** The orange glow is equally strong on every edge, including beside the dark tops. It floods the gaps between the bars with flat rust-brown. The shapes then read as slots cut in a glowing orange plate, not as luminous objects. In the reference the halo follows the body's brightness: weak beside the dark top, strongest around the bright lower half. Fix: stop driving the halo from a uniform silhouette mask. Drive it from the body's own luminance, or multiply the mask by a screen-space ramp (0.15 at the top of each shape, 1.0 at the bottom). Keep the gap between the bars at or below 35% of the current halo value.

2. **The bottoms lack the warm band (bottom of every shape).** The reference goes lilac, pink, hot orange, then red at the lower limb, and that band blooms outward. Here the pink runs to a thin 3–4 px orange line. The eclipse's defining "sunset" end is missing. Fix: extend the gradient ramp so the bottom 12–18% of the normal's Y range (the most downward-facing normals) goes pink, then orange (~#FF6A2A), then red. Push emission there to 2–3× the pink so the bloom picks it up. A halo tweak will not fix this; the colour must come from the body.

3. **Rim and body edge are too crisp and too thin (left and right sides of every bar).** The spectral rim is a 2–4 px cyan line, and the body edge is razor-sharp. The reference rim is a broad, soft yellow-green-cyan band about 3–5% of the shape's width, and the sphere's edge melts into the glow. Fix: widen the rim's Fresnel/facing ramp so it spans 8–14 px at this resolution. Add warm yellow and green stops, not only cyan. Add a small body bloom (1–2% of frame width) so the silhouette edge softens.

Minor: the crescents are stubby 20 px "eyebrows" that stop at the corners. The reference arc is thinner and trails down the sides.

5. **Research check** — The emission gradient, crescent and grain agree with the findings. Two claims fail. Chromatic dispersion is barely visible: I see no RGB split on any edge. Bloom lives only in the orange halo and does not spread from the bright body.

6. **What 8.5 needs**
- Halo weighted by body luminance, bottom-heavy, with dark gaps between the bars.
- A pink-orange-red band at the base of each shape that blooms.
- A wider, softer, multi-hue rim, plus visible dispersion on the edges.
