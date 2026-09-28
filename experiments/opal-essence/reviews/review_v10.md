# Review v10

1. **Score:** 6.5 / 10

2. **Targets**
- Background: #000000 at the edges and in the cut-outs. **Hit.**
- Deep teal #012437–#085c62: left rim #2f6d69–#376c69. **Missed** (too light and grey). The parts behind read grey-brown (gear #37383a, halos #6f544a), not navy.
- Sage #7c9f93: #7fa98a. **Hit.**
- Cream #e7c69d: #efc891. **Hit.**
- Amber #fdbb55: #f4b079. **Missed.** It is salmon, not amber.
- Orange #fca321: the most saturated orange is #df8d4c (S 0.66). **Missed.** It washes to peach.
- Hot pink/coral #fe6f6b: #f07674. **Hit.**
- Opal blue skin #9fb8b7: none on the plate face. **Missed** (third round).
- Micro-type cap height: about 1.2% on the top strip and 0.8% on the label. **Hit.**

3. **What works**
- Depth blur is right. The small gear and the T-bar are crisp, and the big gear melts.
- "WONDER MATERIALS & OPTICS" and "OPAL ESSENCE" read as moulded relief with edge glints at 1:1.
- Grain is now present (std 1.3–1.7/255). Blacks are clean.

4. **Problems, ranked**
1. **Whole plate: still a lit gel, not a photographed resin slab.** At 1:1 the face has no wet specular, no roughness change and no warp. The edges show only a hairline rim. Ref 02 has puddled highlights, glossy streaks and bright, thick edges. The v09 fix did not land, so check it at the render, not in the node tree. Put a large emissive strip card at the mirror angle, visible to glossy rays only. Add a Coat (weight 1, roughness 0.02–0.05) with a noise roughness map from 0.02 to 0.2. Bevel the plate edge 1.5–3 mm so it picks up transmitted colour. The screws are black holes. Give them domed pearl or chrome heads that catch the strip.
2. **Left half: the parts behind are brown-grey with red-brown halos** (x 250–350, #6f544a). This is the same as v09. The milky layer lifts them to mud. Give the parts a glossy deep-teal base (#0a3a40). Light-link a cool rim to them only, and remove the warm light that makes the halo. Target: 10–25% lightness, teal hue.
3. **Bottom left: the Wonder logotype is a soft grey fill** (#59585e). A thin vertical line cuts through the "d", and it reads "Won|er". It has one baseline glint only. This is the third round of value tweaks. Change the mechanism: boolean-union the glyphs into the plate's front face, bevel them 0.3 mm, and find the stray object that crosses the "d". The right-edge vertical micro-type is unreadable. Raise its relief or drop it.

5. **Research check**
- Agrees: blur grows with depth, and the micro-type relief is subtle.
- Contradicts: there is no opal response (no blue-white skin, no warm core). The logotype does not read by edge highlights. The top strip is darker than the plate (#8b786d) and reads as a smoked overlay, not milky resin.

6. **What 8.5 needs**
- A visible wet coat: a strip reflection, roughness breakup and a thick lit edge.
- Teal parts, with no warm halos.
- A logotype moulded into the face.
- An orange/amber band at S ≥ 0.8. Push the gel colours, not the albedo, or use AgX Punchy.
- A blue-white Fresnel tint (#9fb8b7) at glancing angles.
