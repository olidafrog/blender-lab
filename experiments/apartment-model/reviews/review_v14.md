# Review v14 — materials

## 1. Score: 5.3 / 10

Brick colour 5.5 · Brick pattern 5.5 · Floor colour 5.5 · Floor pattern 5.0.

Pairwise: Q is closer. The brick is the same in both. P's floor planks are flat tone steps; Q's have figure, but the wrong wood.

## 2. Targets

- Brick/paint, photo 2: 0.20 vs 0.21. Hit.
- Brick/paint, photo 5: 0.23 vs 0.25. Hit, barely.
- Floor/paint, photo 2: 0.83 vs 0.89. Missed, 7 % dark.
- Floor/paint, photo 5: 0.83 vs 0.99. Missed, 16 % dark ([145,121,90] vs [199,169,141]).
- Brick course 85 mm: plausible in row 2. In row 5 the bricks look 15–25 % too big.
- Planks 700 × 140, spine along the room: hit in rows 2, 5 and 8.

## 3. What works

- Herringbone geometry: plank size, chevron direction, thin dark seams.
- Brick value against the paint.
- Warmer reveals near the glass (row 1).

## 4. Problems, ranked

1. **The floor figure is zebrano, not oak** (rows 2, 5, 8, render crops). It is long, high-contrast dark streaks: stretched noise. The photo shows fine, low-contrast grey-brown oak with cathedral arches, ray fleck and small dark cracks. The render is also matte; the photos show soft window reflections (rows 2, 8). Fix: use a scanned rustic-oak texture, or halve the streak contrast, make the stripes finer, and add arches and check marks. Set roughness to 0.35–0.45 with variation.
2. **The brick is too orange and too clean** (rows 2, 5). The render is [47,30,18]; the photo is [40,29,26] and [48,42,46], plum-maroon with a grey-violet bloom. Fix: raise blue and cut saturation by about 40 %. Make the dust a mottled bloom that crosses brick edges. Now whole bricks are tinted tan.
3. **The mortar is a crisp, even grid** (row 2 and row 1 brick crops). Every joint is a pale line, so the wall reads as CG tile. In the photo the joints are near flush and barely show, and the arrises are worn. Fix: cut mortar contrast to a third, vary joint width, chip the edges in the bump, and jitter brick size.

## 5. Research check

The research says flat-sawn oak figure and a satin sheen; the render has neither. "Soft red-brown" brick is too loose: the photos show maroon-plum, and the render went orange-brown.

## 6. What 8.5 needs

- Real oak figure with a satin sheen.
- Floor value up about 15 % in photo 5 and 7 % in photo 2.
- Desaturated maroon brick, with a bloom that crosses bricks.
- Near-flush, irregular, low-contrast mortar and worn arrises.
