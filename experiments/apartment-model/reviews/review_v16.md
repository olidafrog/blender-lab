# Review v16 — materials (brick, floor)

## 1. Score: 6.0 / 10

Brick colour 6.2 · Brick pattern 6.0 · Floor colour 6.0 · Floor pattern 5.8.

**Pairwise:** Q is closer. The floors are identical. Q's brick is cooler maroon and P's is orange-brown, and the photos' brick is maroon to purple-grey (photo 5 region [48,42,46]).

## 2. Targets

- Brick/paint, photo 2: 0.19 against 0.21. Hit.
- Brick/paint, photo 5: 0.23 against 0.25. Hit.
- Floor/paint, photo 2: 0.90 against 0.89. Hit.
- Floor/paint, photo 5: 0.95 against 0.99. Hit.
- Course height: about 14 px per course in both row 2 crops. Hit.
- Planks 700 × 140 mm in herringbone, spine along the room. Hit.
- Texture (high-pass std, not a target but telling): brick 2.5 against 7.6 (photo 2), pier tile 3.2 against 12.8. Floor 6.1 against 8.5 (photo 2) and 5.7 against 13.0 (photo 5). The render is two to four times too uniform.

## 3. What works

- Wall values are right. At room distance, rows 2 and 5 read as a dark brick wall at the right weight against the white paint.
- The floor geometry is right: herringbone, plank proportion, thin dark seams and spine direction all match rows 2, 5 and 8.
- Row 8 kitchen floor: the value matches the photo ([80,59,35] against [81,60,43]).

## 4. Problems, ranked

1. **Floor figure (rows 5, 2 and 8, floor tiles).** The render is clean, pale, fresh-sawn oak with faint fine grain. The photo is a rustic print: dark brown cathedral streaks, knots, splits and grey wire-brushed streaking, with strong contrast inside each plank. Fix: use a rustic, high-contrast oak albedo (a scan, not procedural). Raise the in-plank contrast about 2× and add a grey-brown streak layer. Target floor texture std of 8–13.
2. **Brick surface is flat CG tile (row 1 pier, row 2 pier, row 5 wall).** Each brick is one flat tone with crisp, even, pale mortar on all sides and sharp arrises. The photo shows speckled, dusty, grey-bloomed faces and worn, broken arrises, with mortar that disappears in places. The few pale bricks in row 2 read as pasted rectangles, not dust. Fix: add a per-brick grain and speckle texture at about 3× the current amplitude, plus a large-scale dust and bloom mask that crosses brick edges. Vary the mortar width and recess, and round or chip the arrises in the normal map.
3. **Floor hue and sheen (rows 8 and 2).** The dining tile is about 22 % dark and too yellow (B/R 0.51 against 0.60). The kitchen tile is also too yellow (0.44 against 0.53). It lacks the grey cast. The row 2 tile near the windows is 28 % too bright and matte, where the photo shows a satin sheen gradient. Fix: desaturate the albedo about 15 % toward grey. Lower the roughness to about 0.3 with a clearcoat so the window reflections show.

## 5. Research check

The image agrees on bond, course height, plank size, layout and seams. It contradicts two claims. The floor has no "flame arcs" at a readable contrast and no "satin sheen with window reflections". The brick has no "strong brick-to-brick tone spread with dusty pale patches". The brick hue is still slightly too orange relative to the paint in row 5.

## 6. What 8.5 needs

- A rustic, high-contrast, greyed oak albedo, with satin roughness and visible reflections.
- Brick face grain and dust bloom at 3× the current spread.
- Worn arrises and irregular, partly lost mortar.
