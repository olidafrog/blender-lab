# Review — wax-seal v01

1. **Score:** 6.0 / 10

2. **Targets**
- Paper 213, 209, 205: missed, just. Neutral grey; the reference is warmer.
- Lit field 183, 174, 191: missed, about 9 low. B > R > G holds.
- Relief tops 227, 216, 234: hit.
- Rim shadow side 69–81, 58–62, 69–85: missed. Too dark and too grey.
- Rim lit side 238, 228, 245: missed badly. About 45 too bright.
- Cast-shadow core 19, 8, 14: missed badly. Nearly black.
- Seal width 91%: hit.
- Rim bead 13%: missed, just.
- Stamped field 74%: missed.

3. **What works**
- The key comes from the upper right and the outline is an irregular blob.
- The emblem tops sit at the right value.
- The field is a true circle, and its inner wall is shadowed on the right.

4. **Problems, ranked**
1. **Cast shadow, lower left (bl crop).** It is a hard band of crushed black with a purple fringe. It reads as a drawn outline. Fix: use a larger key (15–25° angular size) and add fill so the core lands at 55–70 sRGB. Check that no AO or compositor multiply darkens the contact. The edge should fall off over 40–80 px.
2. **The material reads as soft-touch plastic or fondant.** The relief bevels have sharp glossy streaks (centre crop), and the lit rim clips. Fix: set roughness to 0.45–0.6 with low noise, specular 0.3–0.4 and no coat. Keep the SSS radius under 0.5 mm. The lit rim should read 190–205.
3. **Relief and field.** The pillowy bevels and a purple occlusion halo make the mark look stuck on. The "flow lines" are straight Voronoi cracks that look like mesh seams (br crop). The dark line at the field edge looks like a stroke. The rim is a uniform torus. Fix: set the bevel to 15–25% of relief height with near-vertical walls. Use a warped radial noise bump for flow lines. Add lumps and pooled overflow to the rim.

5. **Research check**
- "Deep, saturated violet shadows": contradicted. Grey rim shadow, black cast shadow.
- "Satin, not glossy": contradicted on the bevels and the rim.
- "Hairline flow lines": geometric cracks instead.
- "Rolled bead higher than the field": agrees.

6. **What 8.5 needs**
- A soft key plus fill: cast-shadow core about 63, 48, 49; rim shadow about 93, 79, 105.
- Satin roughness 0.45–0.6, with no clipped highlights.
- Crisp relief walls, with no halo.
- Organic flow lines and a lumpy rim.
- A field at 78% of the seal width.
