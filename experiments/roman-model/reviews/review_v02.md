# Review v02 — roman-model

1. **Score:** 5.7 / 10

2. **Targets** (1000 scale)
- Span y 53–941 vs 42–954: missed (crest 11 low, soles 13 high). x 251–807 vs 212–785: missed.
- Helmet dome ≈ 106: hit. Helmet bottom ≈ 290–300: hit.
- Shoulder-pad tops ≈ 315: hit.
- Belt 481–529: hit.
- Skirt hem ≈ 635–645: missed (~25 short).
- Boot tops ≈ 723–737 vs 780: missed.
- Shield x 627–807, y 351–723: missed (22 too far right, tip 27 short).
- Backdrop: upper right (247,215,167) hit; left half clips (255,255,204): missed. Shadow (107,77,36): missed, too dark. Mid (174,141,85), lit (232,195,126): hit.
- IoU 0.717: missed (v01 0.72, no gain).

3. **What works**
- Helmet size and height now land on target.
- Belt, pad tops and a strap that reaches the right hip put the torso landmarks in place.
- Body faceting: irregular mixed triangles, correct mid and lit tones.

4. **Problems, ranked**
1. **Legs and boots** (knee/boot bands: 24–46 % missing, 38–39 % extra). Each boot is three stacked barrels (cuff, shin, rounded foot lump) with no flat sole. The viewer-right leg splays ~50 too far (y 800: 689 vs 639). Fix: one tapered shaft, a turned cuff at y 770–790, and a flat sole slab ~0.1 head thick with a toe box. Rotate the right leg in 8–10° at the hip. Land both soles at y 945–955.
2. **Torso and sword arm.** The torso is wasp-waisted: at y 450 it is ~193 wide vs ~245. The pecs are two round mounds. A see-through gap opens between the sword arm and the waist (x 370–420, y 420–560), while the arm's outer edge sits 30 in (276 vs 243 at y 500). Fix: widen ribcage and lats 20–25 % at y 380–480 so the taper starts at the belt. Flatten the pecs into two planar slabs with a sternum crease. Move the sword arm out 25–35 so it meets the lats.
3. **Helmet and crest.** The head is turned ~65° to viewer-right (reference ~35°), so the T-opening and cheek guards show only in profile, and the helmet is 12–30 % too wide. The dome shows regular UV-sphere bands. The crest is a thin forward blade; the fan's back half is missing (crest band 59 % missing). Fix: turn the head ~30° back to camera. Flare the cheek guards to the jaw. Triangulate and decimate the dome. Make the crest a fan: peak at (545, 42), top edge near level back to x ≈ 470, then curving down to the rim at (410, 145).

5. **Research check**
Mostly agrees. One correction: the reference helmet has irregular triangle facets like the body, not clean planar armour. The crest does sweep back: a fan whose high point is at the front. The skirt pleats are clean planar strips, which the render's decimated skirt contradicts.

6. **What 8.5 needs**
- Shaft-cuff-sole boots, right leg in, soles at y ≈ 950.
- Broader V torso, flat pecs, sword arm out with no gap.
- Head turned to ~35°, fan crest, irregular dome facets.
- 7–9 clean box pleats, no zigzag under the belt, hem at 665–690.
- Shield 20 left with its tip at y 750. Sword blade ~20 % shorter and ~2× wider, with a guard ~0.5 head long.
- Even backdrop with no clipping. Shadow near (127, 95, 44).
