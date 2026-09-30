# Review v08

## 1. Score: 6.5 / 10
- Hard-surface form and edges: 6.0
- Part fidelity and detail hierarchy: 6.5
- Materials: 6.5
- Light, colour, backdrop: 7.0
- Technical quality at 1:1: 7.0

Weighted: 1.80 + 1.30 + 1.30 + 1.05 + 1.05 = 6.5.

## 2. Yes/no list
1. Yes, mostly. Soft shoulder on the lid, S-plate and steel plate rims (760-1250, 570-780); dark crease at the S-plate foot. The outer body foot (640-1100, 1000-1170) has a lit bevel and no crease.
2. Yes, but few. Groove around the lid pocket (950-1250, 380-600) and the channel around the S-plate. The flat lower plates (1000-1250, 700-900) have none.
3. Yes. The front body wall (640-1100, 900-1170) reads lighter than the tops.
4. No normal artefacts. The dark disc at (835, 795) reads as a fuzzy blotch, not a part.
5. No. Rod, coil, cylinders and gear are smooth.
6. No floating. The antenna cylinders (430-620, 200-410) sit on the housing with no cradle, so they look placed.
7. Yes. Short strokes on the lid and right plate (crop tr). Faint and thin.
8. Yes. Diagonal glare band and bezel highlights, subtle. Not a flat sticker.
9. No. Creases and gaps are charcoal. Only the flat rectangle at (1260-1450, 790-870) is black.
10. Yes. Fine grain, similar in size; slightly blobby and 15% weaker.

## 3. Targets
- Backdrop TL 104 vs 96, TR 137 vs 142, BL 106 vs 111, BR 111 vs 117: hit.
- Subject share 39 vs 36, median 70 vs 75, p95 85 vs 92: hit.
- Subject p5 18 vs 7: hit by 1 level. Barely.
- Subject <12 %: 2.3 vs 7.6: hit on the 12 rule, but it is one third of the reference. This is the real miss.
- LCD median (141, 202, 210) vs (140, 204, 212): hit.
- Grain std 13.1 vs 15.4: hit.

## 4. What works
- All secondary and tertiary parts are present and attached: gear, dial, selector, slide switch, LED, cord, vents, screws, labels.
- Material split reads: steel bracket, bezel and slider frame against satin polymer and rubber. The LCD colour is within 2 levels.
- The S-plate and lid pocket have the right layered read: soft rim, dark channel, parallel groove.

## 5. Problems, ranked
1. **Blacks are grey.** Channel around the S-plate, gaps between the lower plates, and the body foot. Gap floors catch fill and bounce light. Fix: add a black liner (Diffuse, value 0.005) 3-4 mm down in each gap. Multiply the polymer Base Color by an Ambient Occlusion node (distance about 1.5x the gap width, Inside off) at 0.6-0.8 strength. Add a square dark crease at the outer body foot.
2. **Antenna cylinders are too bright and banded** (430-620, 200-410). Four even bright rings read as stacked washers. The reference has dark satin gunmetal with one groove. Fix: keep one 2 mm inset groove per cylinder. Set Base Color to 0.05-0.08 metallic, roughness 0.35-0.45 with anisotropy. Add a two-piece saddle clamp under them with a contact shadow.
3. **Flat black rectangle at lower right** (1260-1450, 790-870). It reads as a hole with a razor edge. The reference has a dark grey block, silver frame and vent slots. Fix: replace it with a dark grey plate with three 4 x 14 mm slots cut through to a black liner. Add a 1.5 mm steel frame. Set roughness 0.3 so it shows a key-light gradient.

## 6. Research check
The image contradicts three claims. Gaps are charcoal, not "nearly black". The outer body foot has a lit bevel, not a black crease. The antenna cylinders are lighter than "dark". Side walls lighter than tops, parallel grooves and the backdrop agree.

## 7. What 8.5 needs
- Real blacks: p5 of 10 or lower, and <12 % of 6 % or more.
- Dark satin cylinders with a saddle.
- A framed vent block in place of the black rectangle.
- A crease at the outer foot, and grooves on the lower plates.
- More scratch density on the right plate.

**Blind pairwise:** X (v08) is slightly closer. Its cylinders read as satin metal where v07's read as matte lipstick tubes, and its black pocket is nearer the reference blacks. It loses ground on the over-bright banding.
