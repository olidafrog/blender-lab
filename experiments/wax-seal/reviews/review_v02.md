# Review v02

1. **Score:** 6.2 / 10

2. **Targets** (row 720 and patch means)
- Paper 215, 210, 207: R and G hit, B just missed (207 vs 208–222). Too warm-grey.
- Lit field 186, 176, 195: missed, about 6–8 too dark. B > R > G holds.
- Relief tops ~193, 181, 201 (face mean): missed. Target 228, 222, 233. Tops barely lift off the field.
- Outer rim, shadow side, 105–122, 96–110, 105–127: near miss. Too light and too grey.
- Rim, lit side, 234, 223, 238: missed. About 40 too bright, washed out.
- Cast-shadow core ~105, 96, 105 at the band centre: missed. Target 63, 48, 49. Only a 1–2 px contact line reaches 44, 35, 39.
- Seal width 93%: hit. Rim bead ~13.7%: missed (10–12%). Field ~73% of seal: missed (78%). The reference measures ~71% on the same row.

3. **What works**
- The rim and field build is right: a raised bead, a circular stamp edge and a flat field.
- Colour family and value order (B > R > G) are correct.
- The outline is irregular, with a soft contact on the paper.

4. **Problems, ranked**
1. **Lighting is flat and soft; the reference light is hard.** The reference has a crisp cast shadow (31–52 core) and a black-violet groove inside the right rim at x 1040–1080 (43, 30, 58). The render has 126, 107, 134 there. Fix: shrink the key (angular size or radius) until the shadow edge is 10–20 px wide. Raise its power. Cut fill and world light so the groove falls to 40–70 and the cast shadow reaches ~55.
2. **The wax reads as soft-touch plastic or fondant.** It has no specular. The reference has tight satin streaks along the top-right rim and on the relief edges (254 peaks). Every surface in the render is diffuse mush. The lit rim at 234 suggests SSS or diffuse lift, not gloss. Fix: roughness 0.25–0.35 with a low-frequency roughness noise. Specular IOR level ~0.5. SSS radius under 0.5 mm, scale checked against scene units. Lower the base albedo so the lit rim sits near 200.
3. **The relief and field detail are CG.** The emblem has a pillowy, uniform bevel with a purple outline at its base, like a vinyl button. The field "flow lines" are straight polygon edges, which read as Voronoi or facet seams (crop_br). Fix: set the emblem bevel radius to 25–35% of relief height, with crisper shoulders. Take out the tinted base darkening. Replace the Voronoi lines with curved, stretched noise (a wave or distorted-noise bump flowing radially), bump strength ≤ 0.05.

5. **Research check**
- The research says "one large soft key". The reference contradicts this: its shadow edges are hard, so the source is small (like a sun or bare lamp). This is why the lighting stays wrong.
- The render contradicts the research's "satin" finish and "deep saturated violet shadows".

6. **What 8.5 needs**
- A hard, small key, with the groove and cast shadow at the target values.
- Satin specular with varied roughness, and the lit rim near 200.
- Crisper emblem shoulders and curved flow lines in place of polygon seams.
- A rim bead of 10–12% with one pooled lump at lower right.
