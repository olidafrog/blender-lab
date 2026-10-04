# Review v24 — sofa

## 1. Score: 6.2 / 10

Shape 5.8 · Placement 8.3 · Detail 5.5 · Fabric 6.0.

Pairwise: **P** is closer. Its slub streak at 1:1 has more contrast, like the photo; Q is smoother.

## 2. Targets

Rough same-region estimates (my wall patch differs).
- Photo 1 seat tops 1.24: about 1.5, **missed** (bright).
- Ottoman top 1.28: about 1.28, **hit**.
- Ottoman front 0.74: about 0.9, **missed**.
- Back front 0.89: about 1.1, **missed**.
- Photo 3 seat 1.16: about 1.6, **missed**.
- Photo 3 arm inner 1.39: about 1.4, **hit**. But the arm-to-seat ratio is 1.10 in the render and 1.57 in the photo.
- Edges within 20 px: **hit** in rows 1 and 2. The worst is about 12 px, at the row 1 ottoman's top front edge.

## 3. What works

- Placement: the row 1 ottoman outline sits on all four photo corners.
- Module count, sizes and the seats proud of the arms read as this sofa.
- The slub scale at 1:1 is right (row 2 arm, row 3 seat).

## 4. Problems, ranked

1. **Flat slabs (rows 2 and 3).** In the photo the back fronts bulge, with vertical ripples. The seats crown and roll at the front, and the ottoman top is domed. The render has flat faces, tight edges and blobby dents on the back tops. Fix: puff each face 2–3 cm at the centre, falling to 0 at the flange. Add a seat crown with a 6–8 cm front roll. Replace the dents with vertical ripples.
2. **The hue is wrong against the walls (rows 1 and 3).** In the photo the wall is neutral (214, 218, 214) and the sofa is warmer (196, 190, 177). In the render the wall is beige (176, 164, 147) and the sofa matches it or is cooler, so it merges. Fix: make the fabric warmer than the paint, or remove the warm cast.
3. **The shading is too flat (row 1).** The seats and back fronts are about 25 % too bright against the ottoman top. Fix: occlusion from the puff geometry, and a slightly lower albedo.

## 5. Research check

The image contradicts:
- "Domed" seats and "puffed" faces: the render's are flat.
- "~1 cm wavy flange, pinched ears": the flange is thin and straight, and the ears are faint (row 2 arm corner).
- "Warm greige": the sofa is not warmer than the walls.

## 6. What 8.5 needs

- Puffed faces, a seat crown and roll, and a domed ottoman.
- Belly ripples and a sit-sag.
- A thicker, wavy flange with ears.
- Fabric warmer than the paint, and more contrast between faces.
