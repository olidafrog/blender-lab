# Calibration review — A vs B

Silhouette IoU against `ref_mask.png` (render downscaled to 1000, background-difference mask): **A 0.796, B 0.841**.

- **A score:** 5.8 / 10 — The shoulders have no pads: the left one is a lumpy blob, the right one is missing (big red gap at x 280–330, y 320–480 in the overlay). The shield sits about 25 px too far right and too low. Stray shards break the read: a fin on the shield arm and a pleat sticking out of the skirt's lower right.
- **B score:** 6.4 / 10 — The helmet is a flat-fronted bucket. It sits square on the shoulders with no neck, so the head reads chibi, not heroic. The reference has a rounded dome turned three-quarter, cheek guards that taper to the jaw, and the T-opening set to the figure's right.

Shared problems, in order:
1. The pose is too frontal. The reference torso turns about 20° to its left, so its strap and chest planes foreshorten. Both renders face the camera.
2. The torso is a box. Neither has the reference's V taper from the pads to the belt. The pecs and lats read as broken-up planes, not masses.
3. B's shoulder pads are flat discs stuck on like ears. The reference pads are domed caps that wrap over the deltoid.
4. B's skirt flares into a bell. The reference hangs straighter, with deep vertical pleats.
5. Faceting is right on the body, with mixed triangles and flat shading. Props are clean. The fists are too cubic.
6. Light and tones are close to target: shadow ≈ (125,93,46), mid ≈ (185,149,88), lit ≈ (237,196,124). The backdrop is a little hot at (255,225,178) against (247,220,174).

**Better overall:** B. It has real shoulder pads and a correctly placed shield, so the upper-body silhouette matches (+4.5 IoU points). A's shoulder line is the single largest silhouette error in either render.
