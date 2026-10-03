# Review v13 — materials

## 1. Score: 5.2 / 10

Brick colour 5.8 · Brick pattern 5.5 · Floor colour 5.0 · Floor pattern 4.8. No pair was given.

## 2. Targets

- Brick/paint: 0.20 (photo 2, target 0.21) and 0.23 (photo 5, target 0.25). Hit.
- Floor/paint: 0.78 and 0.78 (targets 0.89 and 0.99). Missed: too dark near the camera. The far floor in row 2 is washed-out cream.
- Brick course: about 29 courses over the row 2 window in photo and render. Hit.
- Planks: the spine and layout are right. In row 8 the planks look 20–30 % wider than the photo's. Check the scale.
- Floor texture std is a half to a third of the photo's (4.7 vs 8.5, 4.2 vs 13.0).

## 3. What works

- Brick value against the walls.
- The bond and the reveals. Row 1, right crop, wraps the returns well.
- The herringbone layout matches all four photos.

## 4. Problems, ranked

1. **Floor figure, seams and sheen** (rows 2, 5 and 8, floor crops). The render planks are flat boards with faint straight lines. The photos show bold flame arcs, dark streaks and thin dark seams. The sheen is a milky veil that washes out the far floor in row 2. Fix: an oak albedo with 2–3× the current contrast, a dark 1 mm bevel at each seam, and roughness near 0.3 with a weaker specular, so reflections stay local.
2. **Floor colour** (rows 5 and 8). The floor is honey-yellow (B/R 0.58 vs 0.71) with no grey cast. Tone alternates by chevron direction, so it reads striped; the photos vary randomly per plank. Fix: desaturate about 20 % toward grey-brown, and use a per-plank random tone instead of tone by direction.
3. **Brick hue and face** (rows 2 and 5, brick crops). The render is orange-umber [47,30,18]. The photo is maroon to plum-grey ([40,29,26] and [48,42,46]). The mortar is a crisp, pale, even grid that reads as tile. The pale bricks are whole tan rectangles, and the faces are blocky. Fix: raise blue and lower saturation, and make the joints thinner, darker, irregular and recessed. Use soft dust clouds instead of tan bricks, and add fine noise to each brick face.

## 5. Research check

Two findings are contradicted. The floor is yellow-blond, not "warm brown with a grey cast". The mortar is prominent and grid-like, not "thin near-flush".

## 6. What 8.5 needs

- Strong oak figure, dark seams and local window reflections on the floor.
- A grey-brown floor with random variation per plank, at the target values.
- Maroon brick with subtle, irregular mortar, soft dust and a fine-grained face.
