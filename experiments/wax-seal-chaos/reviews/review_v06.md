# Review v06

1. **Score:** 6.2 / 10

2. **Targets**
- Paper: 221, 214, 208. Hit.
- Lit field: 194, 182, 201, B > R > G. Hit.
- Relief tops: 228, 207, 238. Missed (pink-magenta, G low).
- Shadow-side outer rim: about 105, 88, 102. Missed: R ≥ B, grey-mauve. The reference core is 28, 20, 45.
- Lit rim: 240, 230, 248. Missed (too hot, no mid-tone).
- Cast-shadow core: a flat 84, 72, 64. Missed (about 20 too light, no gradient).
- Seal width: 87%. Near hit.
- Rim bead: 9.5%. Borderline.
- Field: 76%. Hit.

3. **What works**
- The field value and hue match the reference.
- The rim profile is right: a rolled bead, a steep inner wall, and a violet contact line at the stamp edge.
- The emblem height and contact shadow are plausible.

4. **Problems, ranked**
1. **The lighting is wrong (left and bottom).** The cast shadow is a uniform slab that runs down-left and under the seal (row 1250, x 150–700). The reference has no shadow there; its shadow is a narrow, fading band to the left. The shadow flanks are too pale, so the seal looks flat. Fix: put the key due right at 35–40° elevation. Make it an area light at least 1.5× the seal diameter. Cut the world or fill to 5–10% of the key, so the left flank reaches 40–60 luminance with B > R.
2. **The relief edges glow pink-magenta (crops 600_500 and 450_950).** This is SSS bleeding through thin bevels. Fix: set the SSS radius to 0.1–0.3 mm at scene scale, or the weight to 0.05–0.15. Make the radius colour close to neutral. Do not just darken the base colour.
3. **The surface reads as clean soap.** It has no specular breakup and no glossy lower-rim glints. The flow lines are isolated threads that read as hairs or cracks; the reference has overlapping, shallow stepped sheets. The outline lacks the lower-right lobe and the right-side crease. Fix: roughness 0.3–0.4 with noise variation of ±0.1, plus low-roughness (0.15) patches on the bead. Use 3–5 layered sheet edges with 0.02–0.05 mm steps. Add an asymmetric lobe.

5. **Research check**
The render contradicts "thin edges do not glow" and "shadows turn deep saturated violet". The key direction also does not match: the shadow falls long to the lower-left, not due left. The satin, dense field agrees with the research.

6. **What 8.5 needs**
- A large key from the right with minimal fill.
- No SSS fringe on the relief.
- Roughness variation with glints, layered flow sheets, and an irregular outline.
