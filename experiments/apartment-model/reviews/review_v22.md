# Review v22: sofa round

## 1. Score: 5.8 / 10

Shape 6.0 · Placement 8.0 · Detail 5.0 · Fabric 5.0

**Pairwise:** P (v22) is closer: domed seats, soft backs and a footed ottoman read as upholstery, where Q is crisp boxes. But P's back blocks are now thin, raked wedges (row 2 far, row 3).

## 2. Targets

Paint: wall above the radiator, same pixels. Photo vs render:
- Photo 1 seat tops: 0.89 vs 0.98. **Missed**, 10 % bright.
- Ottoman top: 0.95 vs 0.97. **Hit.**
- Ottoman front: 0.54 vs 0.52. **Hit.**
- Back block front: 0.78 vs 0.89. **Missed**, 14 % bright.
- Photo 3 seat and arm: cannot be measured. By eye, bright.
- Overlay: rows 1–2 within about 10–15 px. **Hit.**

## 3. What works

- Placement: red edges sit on the ottoman, arms and back tops (rows 1–2).
- Module rhythm: arm | 3 seats | arm, seats proud of the arms, ottoman at the window seat.
- Feet and a dark shadow gap under the ottoman (row 1).

## 4. Problems, ranked

1. **Fabric (all rows).** The fabric is the same hue as the render walls, (184,172,157) vs (186,175,159). In the photo it is greige against white, less blue and about 10 % darker. At 1:1 (row 2 near arm, row 1 ottoman front) the texture is a horizontal streak with blotchy mottling, like brushed felt. The photo is a fine, even weave. **Fix:** albedo toward green-grey and 10 % down; isotropic weave at about 1 mm pitch; sparse slubs; less low-frequency noise.
2. **Back blocks are wedges (row 2 far, row 3).** The side profile tapers to a knife top and rakes back about 15°. The photo shows a 23 cm upright block with a rounded top. **Fix:** rectangular profile, 4 cm top radius, 5° tilt at most.
3. **Edges and flanges (rows 2–3).** The seat top meets the front in a sharp, overhanging lip with a dark crease (row 3), like a mattress. The photo has a rounded bullnose with a pale 1 cm flange. The flange is faint on the ottoman and arm tops. The ottoman's top-front edge sags in the middle; the photo's is straight. No corner ears, no sat-in wrinkles. **Fix:** 3 cm edge radius, a lighter raised flange lip, ears, a few seat wrinkles.

## 5. Research check

Contradicted: "back block about 23 cm thick" (it is a wedge) and "flange catches light as a pale line" (barely visible).

## 6. What 8.5 needs

- Greige albedo below wall value; fine isotropic weave with slubs.
- Thick, upright back blocks.
- Rounded edges with a visible pale flange, ears and seat wrinkles.
