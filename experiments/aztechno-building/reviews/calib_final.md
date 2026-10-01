# Calibration review: calib_final, A vs B (Opus)

## Render A

1. **Score:** 6.4 / 10
2. **Targets** (9/12 hit): red lit (223,62,73) hit · cream lit (238,238,214) hit · cream shade (109,110,98) hit · yellow lit (242,229,150) hit · orange lit (234,136,95) hit · glass upper (69,81,106) **missed** (B +24) · glass upper p90 147 hit · glass lower (40,28,19) hit · sky top (149,175,210) hit · sky low right (203,228,249) hit · pavement (181,162,150) **missed** (B +16) · brick (58,50,55) **missed**. Layout mean IoU **0.326** (flat-trace level).
3. **What works**
   - The paint layout, palette and thin orange lines read as the right building, region by region.
   - Flat-topped salmon tanks, oval oculi on the far-left pier and the full "Crucero del Sur" sign match the photo.
   - Thin gold frames and the sky are right.
4. **Problems, ranked**
   1. *Lower and mid curtain wall (x 360–1100, y 400–720).* The glass is a random checkerboard of pane tints, some pale blue. It reads as a mosaic, not one dark mirror. Remove the per-pane albedo or tint jitter. Vary panes only by normal tilt (0.2–0.5°), and reflect real street geometry or an El Alto HDRI.
   2. *Relief is shallow.* Cream shade share is 0.17 against 0.30. The arches and bands look stuck on. Bring the proud depth to 0.15–0.3 m so the share is 0.25–0.33.
   3. *Shade is too warm, and the ground is CG-clean.* The red shade blue channel is 22 against 46, and every shade row is low by about 20. The pavement shows ruled diagonal joints, the sign is a pristine white panel, and the base has no dirt. Raise the sky-to-sun ratio for lighting (1.3–1.6×). Give the slabs irregular joints and stains, and add a grime gradient 0–40 cm up the wall.
5. **Research check:** The parallel verticals, front-right sun and lifted sky agree. The light checker panes contradict "dark reflective curtain wall". The shallow relief undersells 0.1–0.3 m.
6. **What 8.5 needs:** coherent dark mirror glass, deeper relief, blue shade fill, a weathered ground and sign, redder brick (83,56,48) with recessed openings, flush sky-reflecting pilaster squares instead of deep boxes, and 1.5× chrome diamonds.

## Render B

1. **Score:** 6.1 / 10
2. **Targets** (8/12 hit): red, cream lit, cream shade (111,114,110), yellow, orange, sky top and sky low right hit · glass upper (68,66,90) hit · glass upper p90 **104 missed** · glass lower (48,32,16) **missed** (R +19) · pavement (188,170,165) **missed** · brick (59,49,51) **missed**. Layout mean IoU **0.322**.
3. **What works**
   - Deeper relief (cream shade share 0.26). The oculus rings cast crescent shadows like the close-up.
   - The glass is more uniform than in A.
4. **Problems, ranked**
   1. *Glass.* The upper floors are too dark (p90 104 against 148) and lose the sky band. Amber blobs sit in the left windows (x 220–470, y 300–470) and read as artefacts. Fix with a reflection environment that has a bright sky above the horizon and no warm hotspots.
   2. *Model regressions.* The tanks have domed tops, but the photo shows them flat. The roof caps overhang about 1.3× too far. The far-left pier has square windows instead of ovals, an untextured grey block sits at x 20–80, and the sign is half hidden.
   3. *Shade is too warm, and the ground is clean.* The problem and the fix are the same as in A. The pavement is also too pink (blue 165 against 134).
5. **Research check:** The relief depth and sun direction agree. The warm shade contradicts physical skylight fill.
6. **What 8.5 needs:** A's model (flat tanks, ovals, sign, smaller caps), B's relief depth, a fixed reflection environment, then A's list above.

## Verdict

A is closer to the reference. Its model, glass brightness and target hits (9 against 8) track the photo, and B adds visible model errors. B's deeper relief is better, so carry it into A rather than the other way round.
