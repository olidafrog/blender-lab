# Review v02 — plotter-blend

1. **Score: 6.5 / 10.** Sphere 5.8, funnel 7.3, line and dot 6.8, plot readiness 6.5.
   Pairwise: P (= v02) is closer. It has two eye systems of closed rings and see-through crossings; Q has one ring per eye and reads as a comb.

2. **Targets** (sphere ≈ 705 px)
- Lines across disc: 17–22. **Missed**.
- Rings per eye: right 6–7, left 5. **Missed**.
- Eye positions: opposite through the centre. **Hit**.
- Top and bottom ellipses: the bottom one is too big (45 % × 21 %); the top is a hairpin. **Missed**.
- Dots per line: 3–6 but even. Every contour is closed, so no line ends. **Partial**.
- Line width: 0.64 %. **Hit**.
- Dot: 1.8 %. **Hit**.
- Funnel: 16 × 5, radii 1/.61/.43/.37/.355, height 0.46, ellipses 0.19–0.21, vertex dots. **All hit**.

**Checklist:** 1 yes. 2 yes, but as a ribbon of 6–8 lines. 3 yes. 4 yes. 5 **yes**: right limb (x 1020–1140, 15 px pitch, dots touching) and funnel throat sides (5–14 px gaps). 6 partly. 7 yes. 8 yes.

3. **What works**
- The level-set mechanism gives opposite eyes, a sheared middle and a round outline.
- The funnel radii, tilt, mesh and dots match closely.

4. **Problems, ranked**
1. **The sphere eyes are bullseyes.** Each bump spans 5–7 level steps. Set the amplitude to about 2.5 level spacings and the sigma to 0.45–0.55 rad. Cut the levels to 12–14 lines across the centre. This also clears the right limb.
2. **The funnel parallels crowd toward the throat.** Gaps from the rim are 0.15/0.13/0.11/0.076 × rim diameter. The reference has 0.11/0.14/0.11/0.11. Replace the stretched catenoid with a spline through (z, r) = (0, .35), (.11, .37), (.22, .44), (.36, .61), (.46, 1).
3. **Blot risks.** There are doubled dots (crop 860_520 at 372,70 and 383,72). Front and back meridians nearly coincide at the throat. Drop any dot within 2.5 dot diameters of another dot. Cull back segments within 2 line widths of a front line.

5. **Research check:** Closed level sets cannot make the reference's strokes that end on dots (ref crop 270,222; 200,290; 708,770), so the reference clips contours. A true catenoid with a 0.35 throat stands only about 0.29 rim diameters tall, so the reference profile is not a catenoid.

6. **What 8.5 needs**
- Lower, wider bumps and fewer levels.
- A small, thin ellipse at the top and the bottom (about 30 % × 6 %).
- 30–40 % of the contours clipped at the limb, ending on dots.
- A funnel profile from the reference pairs.
- Minimum spacing for dots and near-coincident lines.
