# aztechno-building — decision record

Freddy Mamani's *Crucero del Sur* (El Alto, Bolivia), from Peter Granser's straight-on photo, as a photoreal architectural render at true scale. Opus built and reviewed, Fable advised (plan, glass, fork). 16 rounds with a fork at round 8. Final **v16, calibrated 6.4** (beat v11 6.1 blind; v11 beat the pre-fork winner v05 6.0 vs 5.4) of a target 8.5. Trend 4.4, 5.2, 5.3, 5.7, 5.7, 5.3, 5.9 | fork 6.0, 6.0, 6.2, 6.5, 6.3, 6.4, 6.3, 6.4, 6.3.

## Chosen

- **Traced facade spec** (`scripts/facade.py`): every element in reference pixels, mirrored about the axis, converted to metres at 38 px/m (shutters, door and storey pitch agree). Each moulding a filled 2D curve with holes, extruded to its depth and round-bevelled, converted to mesh: 750 objects, 50k faces, 2 s, no booleans. Stacked outline layers sit 1.8 cm behind their core so the strips stay in the sun.
- **Shift-lens camera computed from the spec** (lens = 36 · ppm · D / W, shifts put the facade plane on the reference pixels), and `at_depth()` to place set-back parts (tanks, wing, sign) on their reference pixels at any depth.
- **Light**: one Sun lamp (135 W/m², 35° high, 45° to the right) and the 5.x multiple-scattering Sky at 4000 m, strength 1.5 for diffuse fill; the sky the camera sees is lifted ×3, desaturated and darkened to the top (the photographer's exposure and grad), with a procedural cirrus layer. Film exposure 0.043, indirect clamp 0, Khronos PBR Neutral.
- **Glass**: opaque coated dielectric (F 0.35 ± 60 % per pane, tilt per pane hashed from each opening's own mullion grid). Reflections see the lifted sky and cirrus above ~14° and a photographed street (Poly Haven `construction_yard`, rotated 335°, tipped down 12°) below, with modelled low dark houses across the street in front of it.
- **Photographic output stage (the fork)**: render 2×, Lanczos to 1400, unsharp 1 px 40 %, JPEG q85 (`tools/photo_finish.py`), gated by `tools/sharpness.py` (edge ratio and fine-detail energy against the reference).
- **Paint** as one node: colour, roughness, two-scale fading, chalk blotches (kept low), streak and splash-zone grime, low-frequency waviness.
- Roof caps, tanks, oculi rings and diamonds at **absolute depths**, not scaled by the global relief factor.

## Rejected

- **Tinted float glass with sunlit rooms** (v06–v07, advisor's physically better read): lost the blind calibration to coated glass; its reflected box street mattered more than the glass physics.
- **A modelled street alone in the reflections** ("box city", three rounds) and **the street HDRI alone** (tower blocks and a gold onion dome in the glass).
- **Sky lifted for glossy rays everywhere**: it put a ×4 sky into every paint, mullion and chrome highlight.
- **Plaster bump / fine grain**: invisible at 2.6 cm/px. **AO grime**: darkened sunlit inner corners.
- **Global relief factor on everything**: turned 0.2 m caps and rings into 0.7–1 m tubes and slabs.

## Open items

- Shadows on the coloured paint lack ~15–20 levels of blue; cream shade share 0.17–0.21 against 0.30, partly because the measure counts grey glass as shade.
- Per-pane reflectance ±60 % reads as a checkerboard to the last two reviewers; ±20–30 % with more tilt is the next try.
- Pavement and kerb too clean; the right neighbour's brick too grey; left street empty.
- Layout IoU stayed ~0.33 (paint-class labels are dominated by glass and shading, so the metric is weak).
- Brick, pavement, street and decal materials are not single control nodes.
