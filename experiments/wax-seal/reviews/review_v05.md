# Review v05

1. **Score:** 6.6 / 10

2. **Targets** (12 px box means)
- Paper: 212, 207, 204. Missed by a little (B low, slightly grey-warm).
- Lit field: 192, 180, 201 (B > R > G). Hit.
- Relief tops: about 194, 182, 203, the same as the field. Missed badly (target 228, 222, 233).
- Outer rim, shadow side (110, 800): 82, 73, 85. Missed. The value is close, but B−G is 12 against 26: grey, not violet.
- Rim, lit side (1120, 700): 237, 226, 244. Missed. It clips about 45 levels too bright.
- Cast-shadow core (60, 950): 49, 45, 42. Missed. It is neutral black; the ref is 83, 67, 59, warm.
- Seal width: about 89%. Hit. Rim bead: about 8–9%. Missed by a little. Field: about 80%. Hit.

3. **What works**
- The overall blob shape, the true-circle stamp edge and the dark inner wall at the top read correctly.
- The field hue and value match the ref, and the pastel pigment is right.
- The key comes from the upper right, and the relief shades on the correct sides.

4. **Problems, ranked**
1. **The emblem is not pressed out of wax (centre).** The relief tops match the field value, so the mark reads as a low CAD chamfer with a dark AO-like outline. In the ref, the tops glow white (about 228) with crisp shoulders. Fix: raise the relief height to 1.5–2× and tighten the bevel to a small radius with a steep wall. Make the tops catch the key. Add a slight top-face roughness drop (by about −0.1) through a relief mask. Do not add emission. Remove the near-black purple contact line (79 at x=660) by cutting AO/contact darkening, and let geometry make the shadow.
2. **The shadow is black and too heavy (left and bottom edge).** It wraps under the bottom (47 at y=1280), where the ref has almost none. It is neutral, not warm. Fix: move the key further right and lower (azimuth about 45° off vertical, elevation 35°). Enlarge it for a softer penumbra. Add warm bounce/fill so the core sits at 60–85 with R > B. Tint the paper's shadow side by giving the wax a saturated subsurface colour that bleeds into the contact.
3. **The rim is matte and clips; it looks like fondant or soap (right and bottom right).** The lit side blows to 237. There are no glossy specular streaks, and the bottom-right lumps are ghost smears with no geometry. The crop at 1000_1050 shows pale banding seams across the bead. Fix: lower the key intensity or the rim albedo so the lit rim is 190–215. Use roughness 0.3–0.4 with noise variation for satin streaks. Displace real pooled lumps into the mesh instead of painting them.

5. **Research check**
Contradicted: the shadows are grey-black, not saturated violet (both wax and paper). The flow lines are thin raised threads that look like stray hairs lying on the surface, not faint flow marks. The direction of the soft key agrees. The dense, opaque wax with no glow agrees.

6. **What 8.5 needs**
- A taller, crisper emblem with bright tops and no outline darkening.
- A warm, softer cast shadow that falls only lower-left, with violet shadow on the rim.
- The lit rim below 215, satin specular streaks, and geometric lumps; remove the banding.
- Broad, low flow marks instead of hairline threads.
