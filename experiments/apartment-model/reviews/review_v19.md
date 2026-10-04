# Review v19: sofa, round three

1. **Score: 4.7 / 10.** Shape 5.5, Placement 8.0, Detail 3.5, Fabric 3.0. No pair given.

2. **Targets.** Same patches in photo and render (sRGB luma, wall above the radiator), converted to the builder's scale.
- Photo 1 seat tops 1.24: render 0.99 vs photo 0.87 sRGB, about 1.6. **Missed**, too bright.
- Ottoman top 1.28: 0.99 vs 1.02, about 1.2. **Hit**.
- Ottoman front 0.74: 0.55 vs 0.55. **Hit**.
- Back block front 0.89: 0.89 vs 0.82, about 1.07. **Missed**, too bright.
- Photo 3 seat top 1.16: 1.03 vs 0.87, about 1.6. **Missed**.
- Photo 3 arm inner face 1.39: 1.07 vs 1.06. **Hit**.
- Overlay: arms, seat fronts, ottoman corners and back tops within about 10–15 px in rows 1 and 2. **Hit**.

3. **What works**
- The modules, their order and proportions are right, and the red edges land on the photo's edges.
- The ottoman's size and front-face value match.

4. **Problems, ranked**
1. **No fabric (every 1:1 crop).** The crops read as smooth painted MDF: no weave, slub, flecks or grazing sheen. The fabric also has the wall's hue (render fabric 186/174/157, wall 187/175/159). In the photo, the warm greige separates from the neutral wall; in the render they merge. Fix: a plain-weave normal and roughness map at true scale (threads about 1 mm), ±4 % tonal fleck noise, sheen 0.3–0.5, and a base colour from the swatch.
2. **Hard boxes, not upholstery (row 3 seat and arm, row 1 seats).** The tops are flat with sharp 90° edges. In the photo the tops are domed, the edges roll over 3–5 cm and the faces puff. The flat tops take full skylight, which is why the seat tops miss their luma targets. Fix: about 4 cm edge radius, a 1.5–2 cm crown on the tops and 1 cm on the faces.
3. **Construction detail almost missing (row 1 ottoman, row 2 near arm).** The flange is a faint 1 px line. The photo shows a pale, wavy lip with pinched corner ears. There are no feet and no shadow gap: the blocks sit flush on the floor. Fix: a 1 cm flange tube with slight wobble, corner ears, 3 cm feet set in about 5 cm, and a 2–3 cm dark gap.

5. **Research check.** The image contradicts the findings on the flange, the feet and shadow gap, the puffed faces and the matte slubby weave. Sizes and layout agree.

6. **What 8.5 needs**
- A woven fabric shader at true scale, with sheen and the swatch hue.
- Domed, rolled, puffed blocks.
- A visible flange with ears, feet and a shadow gap.
