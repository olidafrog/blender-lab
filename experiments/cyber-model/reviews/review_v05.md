# Review v05

## 1. Score: 6.0 / 10
Form and edges 5.5 (x0.30) · Parts 6.5 (x0.20) · Materials 5.5 (x0.20) · Light and backdrop 6.0 (x0.15) · Technical 7.0 (x0.15)

## 2. Yes/no list (full frame 1600x1200)
1. Partly. Top rims have a soft shoulder (lid, lower plate). The step feet are grey, not a dark crease (S-step foot, about 850-1200, 640-760).
2. Yes. Grooves run parallel to the lid outline and the right plate (about 1210-1440, 700-830). They are shallow and grey.
3. No. My estimate: side walls 75-91 against tops 76-98 (front wall at 900,1150 is 75; lower plate top is 98).
4. No. The big plates are clean. Wide bevel ramps read as bevels, not artefacts.
5. No. The antenna, cylinders, cord and gear teeth are smooth.
6. One problem. The front-right antenna cylinder end touches the LCD bezel's top-right edge (about 560-640, 330-390). Everything else is seated.
7. Yes. Short thin strokes cluster on the lid and right plate. They are slightly uniform in length.
8. Mostly a flat sticker. There is a faint gradient and no glass reflection.
9. No. The darkest creases and gaps are mid-dark grey (p5 32).
10. Yes, but softer and slightly coarser than the reference (bottom-left crop).

## 3. Targets (within 12)
- Backdrop TL, TR, BL, BR: all hit (6, 9, 7, 6).
- Subject share, median, p95: hit.
- Subject p5 (7 vs 32): missed.
- Subject <12 % (7.6 vs 0.9): missed. The render has about 8x fewer true blacks.
- LCD median RGB: hit.
- Grain std (15.4 vs 10.1): hit by the rule (5.3), but 34 % low.

## 4. What works
- All major parts are present and attached: antenna, cylinder pair, LCD, dial and gear, bracket, cord, plug, LED, knob, slide switch, thumb barrel.
- The body reads as one layered mass with an S-step lid, parallel grooves and clean scratches.
- Backdrop, subject median, shadow direction and LCD colour match the reference.

## 5. Problems, ranked
1. **Blacks are missing** (S-step foot, plate gaps about 1180-1250, 720-780, cylinder undersides, vents). Fix: give gap and groove floors a near-black material (albedo 0.02). Multiply the polymer base colour by an AO node (distance about 1.5x step height) raised to power 3. Add a compositor RGB Curves toe on the subject only, so p5 falls to 8-12 and <12 % rises to 5-8 %.
2. **Edges are pillowy and steps too shallow** (lid, right plate, lower plates). Fix: reduce Bevel width to about 40 % of its current value, 1-2 segments, angle limit 30 degrees, Harden Normals on. Raise step heights 1.5-2x so the walls show. Add a large low fill area light (elevation about 20 degrees, camera side, 25-35 % of the key) so the camera-facing walls read lighter than the tops.
3. **Antenna cylinder pair is oversized and collides with the LCD.** They are about 1.5x the reference diameter, with two silver rings each. Fix: scale radius to about 65 %, lengthen 1.4x, and move the axis up-left so the ends clear the bezel. Seat them on a small dark block. Use one collar. Use dark satin metal (metallic 1, roughness 0.35, anisotropic along the axis) for streaked highlights.

## 6. Research check
The reference agrees with every claim. The render fails three of them: black crease at step feet, near-black gaps, and lighter camera-facing walls. Parallel grooves, soft top shoulder, scratches and materials agree.

## 7. What 8.5 needs
- Fix problems 1-3.
- Add a faint glass gradient or diagonal reflection to the LCD (8-10 % white).
- Raise the grain std to 13-15 with a finer grain scale.
- Make one real overhang gap under the lid over the battery block.

**Blind pairwise:** Y (v05) is closer. Its body reads as one continuous layered mass with a matching median tone, while v04's black tray under floating plates reads as a different object. Y loses the true blacks that X had, and that is its biggest gap.
