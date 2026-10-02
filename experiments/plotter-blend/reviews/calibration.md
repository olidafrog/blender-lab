# Calibration review: A vs B (Opus)

The funnels are pixel-identical. Coordinates are full-frame px. Sphere ≈ 710 px.

## A

1. **Score: 6.4 / 10.** Sphere 5.6, funnel 7.4, line/dot 6.8, plot 6.2.
2. **Targets:**
   - About 14 lines: hit.
   - Rings per eye 2 + 2: hit.
   - Eyes UR/LL: hit.
   - Polar ellipses: missed. There is an open Ω tongue at (770–875, 790–910).
   - Dots 2–5 per line, ends dotted: hit.
   - Line 0.65 %: hit.
   - Dot 2.0 %: hit.
   - Funnel 16×5: hit.
   - Radii 1, .61, .43, .36, .35: hit.
   - Height 0.47: hit.
   - Minor/major 0.21: hit.
   - Crossing dots: hit.
3. **What works:**
   - The eye rings are sized like the ref (inner ≈ 25 % of the disc).
   - The funnel has the right profile.
4. **Problems:**
   1. **The left limb is a comb of hairpin U-turns** (450–640, 240–520). It reads as ribbon, not ball. Fix: clip contours at the silhouette (n·v > 0) and end each cut on a dot.
   2. **No polar ellipses, and the outline has a notch** (0.65 R at (700, 900)). Fix: tilt the latitude axis 15–25° toward the camera. Bump tweaks will not close them.
   3. **Doubled lines will blot.** They are at (450–620, 530–560) and at the right limb (1100–1150, 380–540). Fix: keep a gap of at least 14 px and drop back segments within 10° of the limb.

## B

1. **Score: 6.3 / 10.** Sphere 5.9, funnel 7.4, line/dot 6.3, plot 5.6.
2. **Targets:** as A, except:
   - The bottom ellipse hits. The top is missed.
   - The UR inner ring is 8 % of the disc (ref 20 %).
3. **Top problem:** a sharp V kink with no dot at (502, 746). Fix: split at the cusp and dot both ends.
   - It also has a deeper notch (0.54 R).

## Funnel (both)

3–4 meridians stack at the walls (x 2225–2240 and 2560–2580). Fix: use an orthographic camera.

## Checklist (A / B)

1. Eyes closed: yes / yes.
2. S-band: weak in both.
3. Round outline: no / no.
4. Ends on dots: yes / yes.
5. Blots: yes, in both.
6. Funnel profile: yes.
7. Funnel dots: yes.
8. Smooth: yes / no.

## Research check

The renders agree. The polar ellipses suggest a tilted latitude axis. The findings omit this.

## What 8.5 needs

- Silhouette clipping.
- A tilted axis.
- A minimum line gap.
- A stronger S-band.
- An orthographic funnel camera.

## Verdict

A is closer. Its eyes match the ref and its lines are clean. B's bottom ellipse is a gain, but its tiny eye, kink and notch cost more.
