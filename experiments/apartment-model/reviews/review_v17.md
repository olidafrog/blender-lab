# Review v17 (materials)

## 1. Score: 6.2 / 10

Brick colour 6.0 · Brick pattern 6.0 · Floor colour 6.5 · Floor pattern 6.3

**Pairwise:** P is closer. Its floor has real oak figure and pale, near-flush mortar; Q's planks were nearly blank and its mortar dark.

## 2. Targets

- Brick/paint: 0.22 vs 0.21 (photo 2), 0.25 vs 0.25 (photo 5). Hit.
- Floor/paint: 0.87 vs 0.89 (photo 2), 0.95 vs 0.99 (photo 5). Hit.
- Course height: about 85–90 mm. Hit.
- Planks: about 15–25 % too large (row 8 right pair: 45 px photo vs 55–60 px render). Missed. Spine along the room: hit.

## 3. What works

- All four value ratios are on target.
- Row 8 floor: close hue and value (82/60/40 vs 85/67/51); it reads as oak herringbone.

## 4. Problems, ranked

1. **Floor too flat at room distance (rows 5 and 2, floor crops).** Texture is 4.9 vs 13.0 (photo 5) and 6.1 vs 8.5 (photo 2). In the photos, plank tones vary and dark straight-grain streaks show. The render planks are one pale blonde with faint flame arcs. Fix: per-plank value spread of about ±12 % with a grey hue jitter. Use mostly straight, darker grain, with flame on some planks only. Scale the planks down to 140 mm wide.
2. **Brick too uniform, and the mortar reads as a CG grid (row 2 wall, row 5 brick, row 1 pier).** Texture is 3.9 vs 7.6 (photo 2). The photos mix dusty grey bricks with redder ones, under pale patches. The render bricks are even plum-brown, with a lit top edge on every joint. Fix: per-brick hue and value variance and a low-frequency dust mask. Halve the mortar recess and bump strength, and round the arrises.
3. **Reveals and sheen.** In photos 5 and 1, the reveal brick near the glass glows orange-red; the render reveals stay grey-mauve. In shade, the render brick is warmer than in photo 5 (R−B 21 vs 5). The row 2 floor near the windows has mirror-like streaks; the photo sheen is soft. Fix: check the brick hue under direct window light, not only in shade. Raise floor roughness by about 0.1.

## 5. Research check

Most findings agree. Two are contradicted: the "strong brick-to-brick spread with dusty pale patches" is missing, and the floor figure is mostly flame, with too little straight grain.

## 6. What 8.5 needs

- Per-plank tone spread and straight grain, bringing floor texture to about 10–13.
- Planks at 140 mm wide.
- Per-brick colour spread, dust patches and softer joints.
- Lit reveals that read orange-red, and a slightly rougher floor.
