# Review v09

1. **Score:** 6.4 / 10

2. **Targets**
- Background: #000000 at all edges and in the cut-outs. **Hit.**
- Deep teal: #12534f on the left rim. **Hit.** But parts behind the plate stay near-black brown (gear #1e1916), not navy/teal.
- Sage #7c9f93: #749b7c. **Hit** (slightly too green).
- Cream #e7c69d: #f0c386 at the bottom. **Hit.** The upper centre is still khaki (#a5966f).
- Amber #fdbb55: #f19d5e. **Missed** (too red, salmon).
- Orange #fca321: the most saturated orange is #d68649 (S 0.66 against 0.87). **Missed.** It washes to peach.
- Hot pink/coral #fe6f6b: #f5706f. **Hit.**
- Opal blue skin #9fb8b7: none on the plate. Every blue-white sample is a screw. **Missed.**
- Micro-type cap height: about 1% on the top strip and the label block. **Hit.**

3. **What works**
- The brightness fix worked. The plate now glows, and the pink edge and the cream bottom sit on target.
- Depth blur is right. The small gear and the bar near the back face stay crisp, and the big gear melts.
- "WONDER MATERIALS & OPTICS" and "OPAL ESSENCE" read as moulded relief with edge glints.

4. **Problems, ranked**
1. **Whole plate: it reads as a CG gel, not a photographed object.** The face has no wet specular, no roughness change, no warp and no grain (flat-area std 0.5/255). Ref 02 has glossy streaks, puddled highlights and bent edges. Keep the strips unlinked from the frosted base (the glowing-bar fix). Add a Coat layer instead (weight 1, roughness 0.02–0.05) over the frosted base. Show a glossy-only emissive strip at the mirror angle. Break the coat with a noise roughness map (0.02–0.2) and a 1–3 mm low-frequency warp. Add film grain at 1.5–3% std. The screws read as black holes. Give them domed chrome heads.
2. **Parts behind: brown-black silhouettes with red-brown halos** (x 250–350, #542f24). Ref 02's parts are navy/teal and lifted by the milk. The plate glows now, so fix the colour at the parts. Use a deep teal glossy base (#0a3a40), add a cool teal rim light-linked to the parts only, and remove the warm rim on the left half. Target: parts at 10–25% lightness, teal hue.
3. **Bottom left: the Wonder logotype is a soft grey fill.** #5d5e63, out of focus, with a highlight only on the baseline. This is the second round. The value tweaks have not fixed it, so change the mechanism. Union the glyphs into the plate mesh on the front face so they share its material and focal plane. The rake then puts a highlight line on every bevel.

5. **Research check**
- Agrees: blur grows with depth, and the micro-type relief is subtle.
- Contradicts: there is no opal response (no blue skin on the lit face) and no wet highlights. The logotype does not read by edge highlights. The top strip is darker than the plate (#866c5c). It reads as a smoked overlay, not milky resin.

6. **What 8.5 needs**
- A clear coat with wet streaks, roughness breakup, warp and grain.
- Teal parts instead of brown.
- A logotype moulded into the plate.
- A saturated orange/amber band. Try the Standard or AgX Punchy view transform.
- A blue-white Fresnel tint (#9fb8b7) at glancing angles.
