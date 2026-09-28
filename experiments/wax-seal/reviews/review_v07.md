# Review — v07

1. **Score:** 6.2 / 10

2. **Targets**
- Paper: 215–221, 209–215, 204–210. Missed on B (too warm, B < R).
- Lit field: 190, 177, 203. Missed: G is 7 low and R is 2 low. The field is too purple (R−G 13 against the reference's 8).
- Relief tops: 189, 176, 202, the same as the field. Missed by about 40 per channel. The tops do not catch the key at all.
- Outer rim, shadow side: 107, 95, 109. Missed. It is grey-mauve with R > B; the target is violet with B > R.
- Rim, lit side: 234, 221, 240. Missed by about 40. Blown.
- Cast-shadow core: 56, 43, 40. Hit.
- Seal width: about 90%. Hit. Bead: 9% on the left, 12% on the right. Hit. Field: about 78%. Hit.

3. **What works**
- Framing, proportions and the circular stamp wall against the irregular outer blob.
- The key direction is right. The cast shadow falls lower-left with a correct core value.
- The emblem bevel is soft and round-cornered, and it clearly belongs to the same body as the field.

4. **Problems, ranked**
1. **Relief and stamp-wall shading (centre, top inner wall at y≈330).** Every relief edge and the stamp wall carry a hard, saturated dark-violet line (78, 38, 99; 57, 16, 80 at the wall). It reads as an ink outline or a cartoon cel line, not an occluded crease. Relief tops never brighten. Cause: the relief is too low with a steep wall, so only a thin sliver faces away from the light, and the SSS or colour boosts that sliver's saturation. Fix: raise the relief to about 0.6–0.9 mm with a wider bevel (profile over 40–60% of the height), so the top plane tilts toward the key. Clamp the saturation of the shadow term. Do not darken it with an AO or cavity multiply.
2. **Material reads as soft-touch plastic or fondant, not wax.** The field is perfectly uniform with no micro-relief. The "flow lines" are 3–4 isolated hair-thin curves that look like stray hairs. Fix: add a low-amplitude (0.02–0.05 mm), large-scale noise bump to the field so the satin highlight breaks up. Replace the hairlines with many faint, wide, overlapping shallow ridges that radiate from under the stamp. Keep specular roughness at 0.35–0.45 with a slight clearcoat sheen on the rim only.
3. **Rim lighting and colour.** The right rim is blown (234+). The lower-right rim shows ghosted pale translucent streaks and banding (crop 1000_1050), which look like an SSS or normal seam. The shadow-side rim is grey, not violet. Fix: lower the key intensity or raise the rim roughness until the lit rim sits at 190–200. Cut the SSS radius to at most 0.3 mm and check the rim's normals and UV seams. Push the base colour toward blue (for example, linear 0.62, 0.55, 0.75) so the shadows go violet.

5. **Research check:** The rim is too regular; it lacks the thick pooled lobe on the right side of the reference. The deep saturated shadows go to the wrong places: to thin creases instead of the rim's shadow side. That contradicts "shadows turn deep violet" on broad forms. The "satin, not glossy" finding is half met: the field is matte, the rim is glossy.

6. **What 8.5 needs**
- Taller, broader-bevelled relief with bright tops and no ink-line creases.
- Micro-bump plus real flow-line texture on the field.
- Rim at 190–200 lit and violet in shadow, with no streak artefacts.
- A more irregular rim with one pooled lobe.
