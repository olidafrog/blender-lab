# Review v10

## 1. Score

**6.4 / 10.** Form and edges 6.0 (x0.30), part fidelity 7.0 (x0.20), materials 6.0 (x0.20), light/colour/backdrop 6.5 (x0.15), technical quality 7.0 (x0.15).

## 2. Yes/no list

1. Yes, partly. Lid and S-plate tops have a thin lit rim. Feet are dark trenches (centre, x 750-1300, y 550-750). The rim is a line, not a 2-3 px soft shoulder.
2. Yes. The lid has an inner groove (x 950-1240, y 380-600). The plates have silver frames. No groove follows the S-step.
3. No. Bottom and right walls (x 1100-1560, y 1000-1170) are darker than the tops. My estimate: about 40 against 67.
4. No. The big flat faces are clean.
5. No. Rod, cord, knobs and antenna cylinders are smooth.
6. No. Cord ends, antenna clamps and thumb rack are attached.
7. Yes. Short thin strokes on the lid and right plate. They are faint.
8. Yes. The LCD has a diagonal glare and a dark vignette at the upper left.
9. No. Creases read dark grey, not black.
10. Yes. The grain is visible and of similar size. It is slightly blotchy and worm-like.

## 3. Targets (within 12 levels)

- Backdrop TL, TR, BL, BR: hit (off by 6, 5, 5, 10).
- Subject share: hit (4 points).
- Subject median: hit (7).
- Subject p5: hit, barely (11).
- Subject p95: hit (9).
- Subject <12 %: **missed** (2.7 against 7.6, about one third). This is my judgement, because the unit is percent.
- LCD median RGB: hit.
- Backdrop grain std: hit (2.1).

## 4. What works

- All secondary parts are present, in proportion and attached: antenna base, cord with jack and plug, gear and dial, selector, slide switch, LED, thumb rack. The v10 connector now has six slots.
- The LCD matches the reference colour and shows glare.
- Backdrop, key direction and lower-left shadows match the reference.

## 5. Problems, ranked

1. **The body has no mass, and its camera-facing walls are dark.** Bottom and right edge, x 1100-1560, y 1000-1170. The device reads as a thin tray. The reference has thick lit walls. Fix: add a large soft fill card on the camera side, at about 30-40 % of the key power. Raise the body slab height by 1.3-1.5x. Give the wall bevels a 2-3 mm face so they catch the key.
2. **The blacks are grey and the highlights are weak.** Creases: S-plate trench, plate feet, lid recess. Fix: put a black (0.005) diffuse gap strip under each plate overhang. Multiply an Ambient Occlusion node (distance 3-5 mm) into the polymer base colour. Lower polymer roughness from about 0.6 to 0.4 to lift p95 toward 90.
3. **The polymer is one flat matte grey.** Big faces: S-plate, right plate, lower block. The reference has satin variation. Fix: drive roughness with a stretched noise (0.35-0.55). Use a Bevel-node curvature mask for lighter, glossier worn edges (roughness 0.25). Add more short scratch strokes near the edges.

## 6. Research check

The image agrees with the research. It does not deliver two findings: gaps that are nearly black, and camera-facing walls lighter than the tops. The reference body also looks thicker than "layered chamfered solids" implies.

## 7. What 8.5 needs

- Lit camera-facing walls and a thicker body slab.
- Real blacks in creases: p5 at or below 10, <12 share 6-8 %.
- Satin polymer with roughness variation and edge wear.
- Finer backdrop grain, with std raised to about 15.
- Soft shoulder on rims, and a groove along the S-step.

**Blind pairwise: X (v10) is closer.** The connector window now holds six slot vents, like the reference's slot block, and the dark hole beside the thumb rack is now a screw. The two renders are otherwise near-identical, so the margin is small (my estimate: 0.1-0.2 points).
