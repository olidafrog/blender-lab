# Review v01 — wax-seal-chaos

1. **Score:** 5.4 / 10

2. **Targets** (render sRGB, 8px means)
- Paper 222,217,212: **hit**.
- Lit field 195,182,212: **missed**. B>R>G holds, but G is low and B−G is 30 against the reference's 17. Too saturated.
- Relief tops ~226,208,242: **missed**. Candy lilac where the target is near-white (228,222,233).
- Outer rim, shadow side: **missed**. The left bead top is lit (226,212,243). The dark outer wall is a sliver of ~114,101,125, about 20px wide. The reference has a band of 33–60 about 70px wide.
- Rim, lit side 229,214,243: **missed**. Too bright and saturated.
- Cast-shadow core 80,75,73: **missed**. It is neutral grey. The target is a warm brown, 63,48,49.
- Seal width 90%: **hit**. Bead ~12%: **hit**. Field ~76%: **hit**.

3. **What works**
- Scale, framing and proportions of bead against field are right.
- The shadow falls lower-left, so the key direction is roughly correct.
- The emblem sits at a believable relief height with a soft bevel.

4. **Problems, ranked**
1. **Rim reads as a lathed plastic cap (whole bead, crops 1000_1050 and 150_650).** You can see concentric terraces on the bead, and the outline is a near-true circle. The small bumps on the right edge look like glitches. Fix: make the radial profile smooth, with a float curve that has more points and smooth handles, or blur the heightfield before displacement. Then vary the outer radius with 1D angular noise, amplitude 6–12% of the radius, 2–4 lobes. Add one or two pooled overflow lobes, like the ref's lower-right and upper-right.
2. **Material is saturated matte candy (field, relief, rim).** It has no specular glints, no micro texture and no chalkiness. It reads as soap or clay. Fix: desaturate the base colour toward 196,186,203. Keep the SSS radius under 0.5 mm and neutral-tinted. Set roughness to 0.35–0.5 with full specular so the rim picks up small sharp glints, like the ref's lower-left lip. Add a fine noise bump at very low strength for satin grain.
3. **Lighting is too frontal and fill too neutral (left rim, cast shadow).** Drop the key elevation to 25–35°, with a larger emitter from the upper right, so the left outer wall falls into a deep violet band. Cut the world fill until the key:fill ratio is about 4:1 (shadow luma ~55). Tint the fill and paper warm so the core goes brown. Let the wax bounce add violet near the seal base.

5. **Research check**
- "Shadows deep and saturated violet": contradicted. The rim's shadow side is lit and the cast shadow is grey.
- "Irregular blob outline": contradicted.
- "Faint hairline flow lines": partly. There are a few raised worm-like squiggles that look like hairs lying on the wax. The reference shows shallow flow sheets and a crack network across the field.
- "Satin, not plastic": contradicted. The surface is flat matte, and the p99.5 luma is 230 against the reference's 238.
- "Thin edges do not glow": minor breach. The lilac edge lines on the relief's right side look like SSS glow.

6. **What 8.5 needs**
- Smooth the rim profile, with no terraces, and give it an irregular lobed outline.
- Desaturate the wax. Add a satin spec with glints and micro grain.
- Use a lower, grazing key with less, warmer fill, so the left outer wall and the cast shadow hit their targets.
- Replace the squiggle lines with shallow flow sheets and cracks.
