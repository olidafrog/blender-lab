# Calibration — pink_rod, A (v08) vs B (v05), against ref 02

Measured with 40 px region means on the 1400 px renders. Edge falloff was measured with the same 10–90 % method on the reference, which gives about 9 px at 699 px. A gives about 8 px per 700 px and B about 6–7 px, so both are on par with the reference.

## Render A — v08.png

1. **Score:** 6.6 / 10

4. **Top problem:** The glow at the rod exit (centre-right, x 700–950, y 780–1000) is wrong. The rod runs along an open cleft between the two lobe clusters, so a long segment of it is exposed. The glow blows out to near-white (about 250,200,215). It spreads about 20 tube widths; the target is 3–5. The 1:1 crop shows sparkly specks and a hard vertical seam inside it: fireflies smeared by the denoiser. It reads as a bright hole, not as light coming through the volume.
   - **Fix, first part:** Fill the cleft. Add a lobe centred on the rod path so the rod stays at least 1–2 tube widths below the density surface everywhere except the entry and exit points.
   - **Fix, second part:** Do not make the surface emitter brighter. Give the buried segment its light from a thin emission volume (Principled Volume Emission in a cylinder domain around the rod), or from a line of small point lights. Clamp indirect to 5–10.
   - Other targets: lit top 246,151,174 against 180,146,170, missed (too hot). Left 226,128,154, missed. Shadow side 177,101,136, missed on R, close on G and B. Bottom 124,89,121, hit. Sky 64,107,152 and 129,158,179, hit. Shadow/lit luminance 0.46, hit. Bottom/top 0.29 (ref about 0.27), hit.

## Render B — v05.png

1. **Score:** 5.9 / 10

4. **Top problem:** The colour is a flat bubblegum-magenta paint over the whole cloud. It does not behave like albedo. Lit top is 229,149,207 against 180,146,170: B is about 40 too high in blue. The core (228,137,200) is as bright as the top. The bottom (155,108,159, missed) gives bottom/top 0.47; the reference is about 0.27, so there is no dark base. The reference is salmon pink with lavender, sky-lit shadows; B is magenta everywhere. Shadow side 164,104,157, missed. Shadow/lit 0.47, hit. Sky, hit. Entry glow about 4–5 tube widths, hit.
   - **Fix:** Remove the tint or colour multiply. Set the scatter albedo per channel just below 1, for example (1.0, 0.93, 0.95), with blue not above green. Raise the optical depth until the base drops to 0.25–0.35 of the top. Let the depth do the saturating, and let the blue sky fill give the lavender in the shadows.

## Which is better

A is better. Its hue, dark base and violet-leaning shadows track reference 02, and its only large fault is local: the exposed, fireflied exit glow. B has the cleaner emitter but a paint-like magenta over the whole body and no dark base, and those faults undermine the realism of the whole cloud.
