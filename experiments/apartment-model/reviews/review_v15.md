# Review v15 — materials

## 1. Score: 6.1 / 10

Brick colour 6.0 · Brick pattern 5.8 · Floor colour 6.2 · Floor pattern 6.3.

Pairwise: **Q is closer.** Its floor is a real oak figure; P's is a cartoon zebra stripe. The brick is the same in both.

## 2. Targets

- Brick/paint: 0.20 vs 0.21 (photo 2), 0.24 vs 0.25 (photo 5). Hit.
- Floor/paint: 0.90 vs 0.89 (photo 2), 0.95 vs 0.99 (photo 5). Hit, but the row-2 1:1 crop is about 25 % paler.
- Brick course about 85 mm: plausible by eye. Hit.
- Planks about 5:1, spine along the room in rows 2, 5 and 8. Hit.

## 3. What works

- All four values against the paint hit.
- Herringbone layout, plank scale and seams read correctly at room distance (row 8 middle).

## 4. Problems, ranked

1. **Brick hue is chocolate-orange; the photos are maroon/purple-grey** (rows 5 and 1, brick crops). Photo: [40,29,26] and [48,42,46]. Render: [48,31,19] and [51,33,21]. Blue is about half, saturation about double. Fix: rotate hue toward red-violet, cut saturation about 40 %, target R/B 1.3–1.5. Keep value.
2. **Floor figure too weak, plank checker too strong** (rows 2 and 5, floor crops). Texture std: 6.1 vs 8.5 and 5.7 vs 13.0. The photo has cathedral arches, dark knots and fine cracks in each plank, with even plank tones. The render has faint straight grain, and whole planks swing from near-white to tan. Fix: use a rustic, knotty oak source or double the figure contrast. Halve the per-plank jitter. Warm the hue: row 8 reads olive-khaki, the photo is red-brown.
3. **Brick reads as tile, not worn brick** (row 1, both brick crops; row 2). Each brick is one flat tone. Pale bricks are crisp rectangles, and the mortar is an even grid. Fine texture is half the photo's (3.5 vs 7.6). There is no dust or soft arris. Fix: add in-brick mottling and a large dust/stain mask that crosses joints, vary joint width, and round the arrises.

Also: the floor is matte; the photos (rows 2, 8) show window reflections. Roughness about 0.35.

## 5. Research check

The image agrees on bond, course height, near-flush mortar and plank layout. It contradicts the floor's "grey cast": the render is olive, the photo warm red-brown. The "satin sheen" is missing. The "dusty pale patches" appear only as clean pale whole bricks.

## 6. What 8.5 needs

- Maroon/purple-grey brick with lower saturation.
- Mottling, dust across joints and soft arrises.
- Knotty oak figure, even plank tone and a warmer hue.
- Satin floor sheen that picks up the windows.
