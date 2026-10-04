# Review v20: the sofa

## 1. Score: 5.1 / 10

Shape 5.0 · Placement 7.5 · Detail 3.5 · Fabric 5.0.

**Pairwise:** Q is closer. Its weave breaks up P's smooth plastic faces. The geometry is the same in both.

## 2. Targets

Same boxes in photo and render, scaled to the builder's units.

- Seat tops 1.24: about 1.34. **Missed** (8 % high).
- Ottoman top 1.28: about 1.25. **Hit.**
- Ottoman front 0.74: about 0.71. **Hit.**
- Back front 0.89: about 0.95. **Borderline.**
- Photo 3 seat 1.16: about 1.13. **Hit.**
- Photo 3 arm inner face 1.39: about 1.17. **Missed** (dark; uncertain, camera offset).
- Edges: rows 1–2 hit. The row 1 left arm is about 20 px right. **Borderline.**

## 3. What works

- The modules, their order and their sizes are right. The red overlay sits on the ottoman, the back blocks and the seat fronts.
- The ottoman's top and front values match.
- The fabric has a weave now.

## 4. Problems, ranked

1. **Hard-edged boxes** (row 2 near arm, row 1 ottoman). The photo's arm top is crowned, the faces puff out between the seams and the seats are domed. The render's faces are flat, with a tight bevel. *Fix:* puff each face 1.5–2.5 cm at its centre, dome the seat tops about 3 cm, and use a rounded edge radius of about 3 cm.
2. **No flanges, ears, feet or shadow gap.** The photo has a pale 1 cm lip on every edge, with pinched corner ears. The render has a faint hairline. The ottoman sits flush on the floor with no dark line under it. *Fix:* model a proud, wavy flange strip about 1 cm × 4 mm with ears. Raise each block 3 cm onto dark feet.
3. **Wrong weave and hue** (row 1 ottoman front, row 3 seat front). The render has long horizontal streaks with too much contrast on vertical faces. The photo has a fine, even, low-contrast slub. The fabric has the same hue as the beige paint, so it melts into the wall. *Fix:* use an even plain weave at a 1–1.5 mm pitch and halve the streak contrast. Then shift the fabric's hue away from the paint's.

## 5. Research check

The model contradicts these findings: domed tops and puffed faces, flanges with ears, and a dark gap under every block. The module sizes and the 70 × 70 × 45 cm ottoman agree.

## 6. What 8.5 needs

- Puffed faces and domed seats.
- Real flanges with ears.
- Raised blocks with feet and a dark gap.
- An even, low-contrast slub, and a hue that separates from the walls.
- Seat tops 8 % darker.
