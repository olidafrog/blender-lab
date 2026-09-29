# Review — ctrl_waxseal_final

1. **Score:** 5.8 / 10

2. **Targets**
- Paper 215,209,204 — missed, just (B below 208, a touch warm).
- Lit field 189,176,203 — missed (G below 184; too saturated, pink-violet instead of grey lilac).
- Relief tops 188,175,201 — missed badly. They match the field. The target is about 228,222,233.
- Rim shadow side (90,800) 94,81,95 — hit on value, weak on violet (B 95 against 105). At (95,600) it is 126,115,131; the reference there is 59,46,72.
- Rim lit side 230,216,242 — missed (about 40 too bright).
- Cast-shadow core 66,56,51 — hit.
- Seal width about 92% — hit. Field about 76% — hit. Rim bead about 12% on average — hit, but uneven (about 8% at the top, 13% at the bottom).

3. **What works**
- Framing, seal scale, irregular outline and cast-shadow direction and depth match the photo.
- The key comes from the upper right and the soft paper contact reads correctly.
- The emblem sits proud of the field with a controllable fillet.

4. **Problems, ranked**
1. **The stamp well is too shallow (whole seal).** In the reference, the inner wall on the right is dark (91,79,103) and the left rim falls into deep violet. In the render the right inner wall is lit (181,167,193), and a thin, inky purple line replaces the wall. It reads as a coin set in a bezel. Fix: sink the field 0.8–1.2 mm below the bead crest and make the inner wall 60–75° steep with a 0.3–0.5 mm fillet, not a crease. Change the bead cross-section from a flat-topped chamfer to a round torus profile, so a single highlight runs along its crest.
2. **The material reads as plastic or soap, not chalky wax.** The colour is uniform and oversaturated, with no micro texture and no dished field. The lit rim clips toward 240. Fix: bring albedo saturation down to about 0.25–0.30 and value down so the lit rim lands at 191–210. Add a fine noise bump (0.02–0.05 mm, high frequency) and roughness variation from 0.45 to 0.6. Dish the field by 0.2–0.3 mm. Replace the few hair-thin scratch curves with broad, low-relief flow ridges.
3. **Geometry artefacts on the rim (lower right and right, crops 1000_1050 and 1050_650).** There are vertical ghost bands, a bright horizontal tick across the bead and a round ghost lump. The outline is visibly faceted. These look like displacement seams or shading-normal breaks. Fix: raise the grid resolution or smooth normals after displacement, and blend lump SDFs with smooth-min.
- **Emblem (secondary):** the tops are flat and the same value as the field, and the dark violet contact line looks like a stroke. Round the shoulders so the tops catch light (220+) and soften the base AO.

5. **Research check**
The render contradicts these findings: "steep inner wall at the stamp's circular edge" (it is a thin line), "field slightly dished" (it is flat), "satin, not glossy plastic, chalky" (it reads as plastic), and "shadows deep, saturated violet" (the left rim is too light). The rim has an irregular blob outline and a true circular stamp edge, which agrees with the research.

6. **What 8.5 needs**
- A deep well and a round bead, so the right inner wall and left outer rim go dark violet.
- Desaturated, chalky albedo with micro bump and a dished field.
- Remove the rim seams and faceting.
- Rounded emblem tops that catch the key.
