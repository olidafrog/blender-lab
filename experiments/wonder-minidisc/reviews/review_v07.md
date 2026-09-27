# Review v07

1. **Score:** 6.3 / 10

2. **Targets**
- Background white: 255,255,255 at all corners and below the object. **Hit.**
- Thick rim deeper than thin plate: rim 63,201,180 (left) and 48,175,155 (right) against plate 72–80,164–181,153–169. The rim is as bright or brighter, only more saturated. The darkest values (31,70,65) are hairline edges only. **Missed.**
- Tint glows over a bright sector, darkens over a dark one: teal bars measure 79,180,167 over dark disc and 48,133,122 near a ray. There is no glow, and the disc does not show through the bars. The windows show the disc with no tint at all (ray 255,255,255; mirror 54,68,72). **Missed.**
- At least four hue families: blue is 56% of saturated disc pixels, cyan 25%, orange 7%, violet 4%, green 4%, pink/magenta 2%, yellow 1%. It passes on paper, but the disc reads blue/cyan. ref4 is mostly pink. **Borderline hit.**
- Hub steel ~81,78,78: measured 42,64,62, too dark and tinted teal. **Missed.**

3. **What works**
- The outline carries the logomark's shape language well. The stacked top and bottom plates show at the outer edge, and the stepped well walls and screw bosses read as moulded.
- The disc has mirror-dark ground between coloured sectors, as the research describes.
- A clean white sweep with a teal caustic under the case (177,246,244) is a good product-shot base.

4. **Problems, ranked**
1. **The case plastic reads as frosted jelly, not tinted polycarbonate** (every teal bar, and most visible in the centre crop). The bars are uniform and grainy, and nothing behind them shows through. The windows are clear or open, so no disc is ever seen through the tint. Fix: make the plate a sharp Refraction/Glass BSDF (roughness 0–0.03) with Volume Absorption only. Remove any scatter, translucency or noise-driven roughness from the transmission lobe, and put the wear on a separate coat/specular layer. Tint the window panels too. Tune the density so a 1 mm plate passes about 65–75% and a 5–6 mm edge-on wall about 20–35%.
2. **The diffraction is thin, star-shaped spokes** (all windows). Small lights make narrow rays that read as a starburst filter, and nearly every ray is blue-white. Fix the mechanism, not the gain. Use 2–3 large softboxes plus a black flag reflected in the disc, so the sectors become wedges 20–40° wide. Also make sure the shader spans 400–700 nm with a second order, so pink and magenta appear. Target: colour covers 35–60% of the visible disc, and pink/magenta is at least 15% of the saturated pixels.
3. **The disc does not read as a disc** (centre and windows). You never see its edge, its ring wall or its clamp, and the hub is a dark teal blob. Fix: open one window over the disc rim with a ring-wall step, and model the hub as steel rings with a clear clamp plate at about 80 grey.

5. **Research check:** The image contradicts three findings. Wear blurs what is seen through the plastic (the bars are frosted). The tint does not deepen with thickness. The tint is not lit up by the disc. The dark mirror between rays does agree.

6. **What 8.5 needs**
- Clear absorbing plastic everywhere, with wear on the coat layer only.
- Broad sectors from large lights, with pink/magenta in them.
- A visible disc edge and a steel hub.
- A faint table reflection or a denser contact shadow under the bottom edge.
- Dust at about a third of the current density, with varied sizes.
