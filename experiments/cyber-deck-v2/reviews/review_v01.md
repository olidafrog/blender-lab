# Review v01

1. **Score:** 4.8 / 10

2. **Targets**
- Backdrop TL 108 vs 96: hit (edge of tolerance). TR 137 vs 142: hit. BL 107 vs 111: hit. BR 111 vs 117: hit.
- Subject share 38 vs 36: hit. Median 65 vs 75: hit. p95 86 vs 92: hit.
- Subject p5 21 vs 7: **missed**. Subject <12 % 2.4 vs 7.6 (ratio 0.32): **missed**. Gaps and creases are not black.
- LCD (141,202,210) vs (140,204,212): hit. Backdrop grain 13.1 vs 15.4 (0.85): hit.
- By eye: tops 65–78, S-ridge 94–103. Both in range.

3. **What works**
- Tone ladder is right: flat tops dark, the S-ridge reads lighter as a camera-facing slope.
- Layout is legible: LCD top-left, DT-03 plate right, S-step, battery lower-left, vent block lower-right, thumb gears, coiled cord.
- LCD colour and backdrop gradient match.

4. **Problems, ranked**
1. **Whole body: flat stacked slabs with pillowy bevels, not CAD solids.** Every plate has the same fat round edge (about 8–10 mm, 25+ px), no crease at the foot, no sloped walls. The LCD has only a thin chrome rim. It needs the thick black shield with 45–60° walls. The lower-right block reads as three pancakes. Fix: build each level as a profile (sketch outline, extrude, then a chamfer-slope band). Use Bevel modifier, limit method Weight. Top edge radius 3–5 mm (10–16 px). Crease at the foot 0.5–1 mm. Panels 1 mm. Add real 1–2 mm gap grooves between parts so they go black. That also fixes p5 and <12 %.
2. **Left side and pods: wrong parts, wrong material.** The dial sits face-up on a bright chrome triangle. In the ref it is a gunmetal side frame with a dark gear, set into the body. The two pods are short fat cans on a floating plinth. In the ref they are longer barrels built into the top shell, with a knurled collar. The chrome rim on the battery insert and the chrome cylinder at right have no match in the ref. Fix: rebuild the left frame from `ref_front.jpg`. Set steel to darker brushed metal (base 0.35–0.5, roughness 0.3–0.4). Keep bright chrome only on screw heads.
3. **Surface: chalky edge wear, curly scratches, no grain on tops.** The wear is a blotchy light band about 20 px wide on every edge, like dust. Ref wear is a fine speckle on the fillet crest only, at most 3–4 px. The DT-03 plate scratches curl like hairs; ref scratches are sparse, straight lines. Tops look smooth; ref has a strong fine bead-blast speckle. Fix: drive wear from a Bevel-node or AO edge mask thresholded tight, times fine noise. Use straight line segments for scratches. Add a high-frequency noise bump (scale about 0.2 mm) on the polymer.

Also: the floor texture is wormy cells, not fine sand. The red power LED spills a glow onto the ridge. The antenna and gear cast shadows that are too long and hard; soften the key.

5. **Research check** — Contradicts "constant-radius fillets, sloped steps with crease at the foot" (bevels are uniform and huge, steps are vertical). Contradicts "wear on edges only as light speckle" and "sparse straight scratches". Light direction agrees.

6. **What 8.5 needs**
- Remodel the shells as profile + slope-band solids with 3–5 mm tops, tight foot creases and dark gap grooves.
- Rebuild the LCD shield, the left dial frame and the pods to the reference.
- Tight crest-only wear, straight scratches, bead-blast bump; gunmetal instead of chrome.
