# Review: v23

## Score: 7.8 / 10

## What works
- The core edge is a little softer. Row 900, stem 1: 164→130→88→78→58 over about 4 px. In v22 it was 166→108→83 over 2 px.
- The side face no longer has a rippled, glassy reflection. The wet-chrome band is gone.
- The line screen, the MIC dots and the hairline comb past the glyph edge all survive at pixel level (detail crop). They still echo crop1_text.
- The background is a clean neutral grey (179 at the top, 218 at the floor). The staging is calm and the thickness reads.

## Top problems (ranked by impact)

1. **The blacks got darker. They should have lifted.** Core RGB is 55/56/64, down from 70/71/79. The face is 204. Contrast went from 2.8:1 to 3.6:1. The "doubled veil" does not show where it counts. Face falloff before the edge is 197→165 over about 10 px, the same as v22. The ink reads as a crisp decal on the surface, not toner seen through frost. In ref1 and ref4 the black sits near 80–100 on a 200 white.
   *Fix:* put the veil in as an additive lift over the ink, not a darkening halo. Target a core of 80–90 with a cool tint (about +6 blue). Widen the edge ramp to 8–10 px (a 0.5 mm pre-screen blur, not 0.3 mm), and keep the comb on top.

2. **The side face is blown out and flat.** It reads 235–249 down its length, 30–45 levels brighter than the front. The edge crop shows a flat white band with no grain, no falloff and no print line. It reads as painted MDF or a lightbox, not satin plastic. It pulls the eye away from the logo.
   *Fix:* lower the side albedo or the fill that hits it until it sits at 185–205, below the front. Keep roughness at 0.4. Add a faint subsurface tint or a gradient toward the floor. Add a 0.4 mm grey print rim 1–2 mm in from the front arris.

3. **The wear still looks procedural.** The pinholes are more varied, and some cluster along the glyph edges. But the interiors still show even salt, and the contours are still clean vector curves at logo-crop scale. The "chipped" outline shows nowhere.
   *Fix:* double the contour erosion amplitude (0.2–0.4 mm) at low frequency so bites show at full frame. Let the clump mask leave some 3–5 mm areas almost clean and others dense.

4. **The face texture and the grazing sheen are invisible.** Upper-face std is 3.19 and lower-face std is 1.86, the same as v22. No sheen crosses the face.
   *Fix:* move the key to within 15–20° of the face plane, or add a strip light that makes a soft highlight on the upper third. Push the roughness mottle to ±0.15 at 1–3 mm scale.

## To reach 8.5+
Lifted, cool blacks (80–90) with an 8–10 px soft edge. This change alone is worth about +0.4. Then a side face that sits darker than the front and has a print rim (+0.2), a visible sheen that shows the grain (+0.1), and contour chipping you can read at full frame (+0.1).
