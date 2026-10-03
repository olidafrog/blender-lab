# Review v18 — materials

## 1. Score: 5.8 / 10

Brick colour 5.8 · Brick pattern 5.5 · Floor colour 6.3 · Floor pattern 5.8.

Pairwise: **Q** is closer. Its floor has more plank spread and some streaky planks; P has a uniform flame figure. The brick is the same.

## 2. Targets

- Brick/paint: 0.22 vs 0.21 (photo 2), 0.25 vs 0.25 (photo 5). Hit.
- Floor/paint: 0.93 vs 0.89, 0.95 vs 0.99. Hit.
- Course height: about 13 px in both (row 2 pier). Hit.
- Spine direction matches in all rows. Row 2 planks look 10–15 % too wide. Borderline.
- Texture std: floor 6.6 vs 8.5 and 5.7 vs 13.0; brick 3.9 vs 7.6. Missed: half the photo's texture.

## 3. What works

- Mean values relative to the paint are right for both materials.
- The herringbone layout and scale hold in every row. Row 8 has the closest floor colour.
- Brick proportion is right.

## 4. Problems, ranked

1. **The floor is clean select oak; the photo is rustic oak** (floor crops, rows 2, 5, 8). The photo planks have dark streaks, cracks and knots. The render has soft flame arcs at low contrast: crop std 16 vs 34 (row 2), 17 vs 46 (row 5). Rows 2 and 5 read blonde-pink. The render varies between planks; the photo varies within each plank. Fix: a rustic straight-grain texture with crack and knot lines at about 2× the albedo contrast. Keep the mean; halve the plank-to-plank tint.
2. **The brick reads as a pale grid on uniform brick** (row 2 pier, row 5 oblique, row 1 pier). Each joint is a crisp pale line. In the photo the joints are recessive, level with the brick or darker. The photo bricks vary strongly, with 10–15 % pale, dusty grey-pink faces. Rows 2 and 5 also have green smudges that the photos lack. Fix: mortar at about 1.1× the brick, recessed with AO. Brick luma spread about ±25 %. Dust that greys the pale bricks. No green.
3. **The floor seams are too strong and even** (rows 8 and 5). In the photo they are faint and broken. Fix: halve the seam darkness and vary it along the edge.

## 5. Research check

Two claims fail at 1:1. "Mortar paler than the brick": on the row 2 pier it is level or darker. "Flame arcs": the planks show mostly straight, streaky grain. Headers are not visible, so stretcher bond is acceptable.

## 6. What 8.5 needs

- A rustic straight-grain floor at 2× the contrast, with faint, broken seams.
- Recessed mortar, ±25 % brick spread, dusty pale bricks, no green.
- Row 2 plank width checked.
