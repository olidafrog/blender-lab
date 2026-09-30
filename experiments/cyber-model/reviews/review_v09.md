# Review v09

## 1. Score: 6.7 / 10
- Hard-surface form and edges: 6.0
- Part fidelity and detail hierarchy: 7.0
- Materials: 7.0
- Light, colour, backdrop: 7.0
- Technical quality at 1:1: 7.0

Weighted: 1.80 + 1.40 + 1.40 + 1.05 + 1.05 = 6.7 (v08 was 6.5).

## 2. Yes/no list
1. Partly. Soft shoulder on the lid, S-plate and steel plate rims (760-1250, 380-780); dark crease at the S-plate foot. The outer body foot (640-1100, 1000-1170) still has a lit bevel and no crease.
2. Yes, but few. Lid pocket groove (950-1250, 380-600), S-plate channel, plate lip. The flat lower-right plates (1000-1250, 690-940) have none.
3. Yes. The front body wall (640-1100, 850-1170) reads lighter than the tops.
4. No normal artefacts. The dark disc at (835, 795) reads as a fuzzy blotch.
5. No. Rod, coil, cylinders and gear are smooth.
6. No. The antenna cylinders (430-620, 190-410) now sit on small saddle clamps (crop tl).
7. Yes. Short strokes on the lid (crop tr). Faint, thin and sparse on the right plate.
8. Yes. Diagonal glare band and bezel highlights, subtle. Not a flat sticker.
9. No. Creases and gaps are charcoal, not black.
10. Yes. Fine grain, similar in size; slightly blobby and about 15 % weaker.

## 3. Targets
- Backdrop TL 104 vs 96, TR 137 vs 142, BL 106 vs 111, BR 111 vs 117: hit.
- Subject share 39 vs 36, median 70 vs 75, p95 84 vs 92: hit.
- Subject p5 19 vs 7: hit by exactly 12 levels. Borderline, and it moved the wrong way from v08 (18).
- Subject <12 %: 2.2 vs 7.6: missed. It is 29 % of the reference. The 12-level rule does not fit a percentage.
- LCD median (141, 202, 210) vs (140, 204, 212): hit.
- Grain std 13.1 vs 15.4: hit.

## 4. What works
- The antenna cylinders now read as dark satin metal with one silver collar each, on a saddle. This fixes v08's washer stack.
- The lower-right block now has a steel frame in place of the razor-edged black hole.
- The layered read holds: lid pocket, S-plate with lit shoulder and dark channel, steel plate with lip, all parts attached.

## 5. Problems, ranked
1. **Blacks are still grey.** Metrics did not move from v08 (p5 19, <12 % 2.2). Locations: the S-plate channel (760-1250, 640-780), the gap between the lower plates (1000-1260, 690-940), the outer body foot. Gap floors catch fill light. Fix: fill each gap with a black liner (Diffuse, value 0.005) 3-4 mm down. Multiply polymer Base Color by an Ambient Occlusion node (Only Local, distance about 1.5x the gap width) at 0.6-0.8 strength. Add a square crease at the outer foot. Target: p5 of 10 or less, <12 % of 6-8 %.
2. **The lower-right frame is an empty outline** (1245-1500, 730-910). A thin chrome loop rests on a flat dark-grey face with no depth and no slots. The reference has a vent block. Fix: cut the pocket into the plate, bevel the lip 1.5 mm so the steel is the lip, cut three 4 x 14 mm slots through to the black liner, and set the pocket floor roughness to 0.3 so it picks up the key gradient.
3. **Flat, empty lower plates** (1000-1250, 690-940; the outer body wall). One value, no groove, no screw. Fix: inset a 2 mm wide, 1 mm deep groove 6-8 mm inside each step outline, with the black liner in it. Add one vent set or two screws to bring these plates up to the detail density of the left side.

## 6. Research check
The image contradicts two claims. Gaps are charcoal, not "nearly black". The outer body foot has a lit bevel, not a black crease (the S-plate foot does have one). The antenna cylinders now agree. Side walls lighter than tops, parallel grooves, materials and backdrop agree.

## 7. What 8.5 needs
- Real blacks: liner plus AO. This is the biggest gap to the reference.
- Slots and a lip on the lower-right frame.
- Grooves and a crease at the outer foot.
- More scratch density on the right plate.

**Blind pairwise:** Y (v09) is closer. Its cylinders match the dark satin body with a silver collar, and the framed pocket is nearer the reference's silver-framed lower block than v08's flat black rectangle. Both share the same grey blacks, so the gain is in part fidelity only.
