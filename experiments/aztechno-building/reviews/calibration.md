# Calibration review — A vs B

## A

**Score:** 5.3 / 10

**Targets** (hit within 15/channel)
- red lit (220,52,63) hit
- cream lit (236,231,204) hit · cream shade (130,131,119) missed (+16/+19); shade share 0.19 vs 0.30
- yellow lit (241,223,141) hit · orange lit (232,133,90) hit
- glass upper (88,105,121) missed (+28/+38/+39), p90 luma 122 vs 148 missed
- glass lower (25,21,12) hit
- sky top (148,175,210) hit · sky low right (204,228,249) hit
- pavement (188,169,163) missed (too pink, +29 B) · brick (104,58,35) missed (+21 R)
- Label IoU mean 0.338

**Top problem:** curtain-wall reflections (about 45% of the frame). The bays mirror low-poly grey boxes and a tiled brick checkerboard (x 360–470 and 830–1090, y 400–720). The photo shows sharp, dim, warm rooftops and a mountain. Upper glass is flat grey-blue. Fix: replace the proxy city with an equirect photo of a low-rise brick town, seen only by glossy rays (Light Path: Is Glossy Ray). Keep roughness 0.0–0.02 with a dark tint, aiming for upper glass near (60,67,82).

## B

**Score:** 5.6 / 10

**Targets**
- red lit (217,60,69) hit
- cream lit (235,231,204) hit · cream shade (122,123,113) hit; shade share 0.29 vs 0.30
- yellow lit (240,222,144) hit · orange lit (229,134,96) hit
- glass upper (47,72,99) missed (+17 B), p90 luma 89 vs 148 missed badly
- glass lower (31,15,3) hit
- sky top hit · sky low right (203,227,249) hit
- pavement (186,167,160) missed · brick (101,55,32) missed
- Label IoU mean 0.333

**Top problem:** blotchy paint. Every red surface carries 0.5–1 m cloud mottling at about ±15 levels (pilasters x 590–640, left wing, band y 740–770). It reads as camouflage. Granser's red is near-uniform enamel. Fix: value-only noise at ±3–5 levels, blobs 2 m or larger, plus AO-driven grime under sills. Upper glass is also too dark and flat (p90 89) and needs A's fix.

## Shared tells (both)
- Tower rings are fat torus donuts; the diamonds are tiny dark "V"s. The reference rings are flat yellow bands, and the chrome diamonds fill about 1/3 of each ring.
- The left wing is a grey box. The reference has a set-back cream pillar with four oculi.
- Street and pavement are perfect repeats with no dirt. Neighbour brick is oversized, too orange and tiles visibly, with black-rectangle windows.
- Moulding edges are dead sharp, unbevelled.

## Which is closer
B is closer: its relief casts the right shadow (cream shade share 0.29 vs 0.30), and its lower glass reads as dim curtain wall rather than A's mirrored block-out geometry. Its blotchy paint is also a cheaper fix than A's reflection content.
