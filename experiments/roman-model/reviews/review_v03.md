# Review v03 — roman-model

1. **Score:** 6.2 / 10

2. **Targets** (1000 scale)
- Span y 60–935 vs 42–954: missed (crest 18 low, soles ~20 high). x 200–786 vs 212–785: hit (pommel 12 wide).
- Helmet dome ≈ 127 vs 100: missed. Helmet bottom ≈ 317 vs 290: missed. The whole head sits ~25 low.
- Shoulder-pad tops ≈ 297 (left), 310 (right) vs 320: missed (pads high, and above the helmet bottom).
- Belt 483–517: hit.
- Skirt hem ≈ 650–665: hit (short end).
- Boot tops: right cuff ≈ 720, left leg has no cuff: missed.
- Shield x ≈ 640–787, y 347–723: x and top hit; tip 27 short and ~40 left: missed.
- Backdrop (246–254, 218–225, 173–178): hit (left side ~7 hot). Shadow (109,78,35): missed, too dark. Mid (176,146,90): hit. Lit (243,212,161): missed, pale.
- IoU 0.768 (v02 0.717): above 0.75, below 0.85. Missed.

3. **What works**
- The helmet now faces the camera. The T-opening, nose guard and dark eye slot read at once.
- Sword angle, hilt position and shield-arm fist land close to the target.
- Body faceting has the right mixed-triangle character, and the key light, contact shadow and mid tone match.

4. **Problems, ranked**
1. **Legs and boots (second round).** Each leg is stacked barrels: thigh, shin, rounded foot lump. There is no knee, no flat sole and no toe box. The viewer-right leg sits ~25 too far out (y 800: 662 vs 639), and its foot runs ~35 too far right at y 880. Fix: one tapered shin shaft, a turned cuff at y 770–790 on both legs, a sole slab ~0.1 head thick, and a wedge toe. Rotate the right leg in 6–8°. Put the soles at y 945–955.
2. **Torso and arms (second round).** A see-through gap still opens between the sword arm and the waist (red 50–80 px per row, y 440–520). The abdomen is long and pinched. Both arms hang as straight pillars with no elbow bend. Fix: widen the lats 15–20 % at y 400–480 so the arm touches them. Bend the sword arm 15–20° at the elbow. Replace the chest ball with two planar pec slabs. The strap and the skirt top show saw-tooth triangles along their edges. Rebuild both as clean extruded bands.
3. **Head and crest (third round).** The crest is a thin slab leaning forward. The back half of the fan is missing (red from x 410–480, y 42–150). The head sits between the pads with no neck. Fix: a crescent fan ~0.6 head wide, peak at (545, 42), top edge back to (440, 70), back edge down to the rim at (410, 145). Raise the head ~0.13 head units and lower the pads ~15 px. Flare the cheek guards out ~10 % at the jaw.

5. **Research check**
Mostly agrees. The reference helmet dome has irregular triangle facets. The render's dome shows regular UV-sphere rings, which contradicts the reference. The skirt pleats in the reference are clean planar strips, and the render's decimated skirt contradicts that. The reference pads are rounded faceted domes. The render's viewer-left pad is a stepped flat slab.

6. **What 8.5 needs**
- Shaft, cuff and sole boots; right leg in; soles at y ≈ 950.
- Lats that meet the sword arm; bent elbow; planar pecs.
- A crescent crest; head raised ~25 px; decimated dome.
- Clean-band strap and planar skirt pleats; shield tip down to y 750.
- Lift the shadow tone toward (127, 95, 44).
