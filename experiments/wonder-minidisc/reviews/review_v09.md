# Review v09

1. **Score:** 6.8 / 10

2. **Targets**
- Background white: 255,255,255 at all corners and under the object. **Hit.**
- Thick rim deeper than plate: right rim 45,124,109 vs band plate 74,172,160. **Hit.**
- Tint over bright vs dark sector: the windows are untinted. Bright sector 200,202,222 and dark sector 68,108,121 are both neutral disc colour with no teal. **Missed**, because the tint relationship does not exist.
- At least four hue families: of saturated disc pixels, blue is 52% and cyan 38%. Green (3.5%) and violet (2.5%) are faint. Red, orange and yellow are 1.7% combined at saturation 0.38 or less. Pink/magenta is **zero**. **Missed**: the disc has two strong families, and ref4's dominant pink/magenta is absent.
- Hub steel ~81,78,78: measured 37,55,54, which is too dark and tinted teal. **Missed.**

3. **What works**
- The disc reads as a CD: radial spectral sectors run from the hub, with dark mirror between them.
- The layered edge (top plate, gap, bottom plate) is visible on the silhouette. Rims are deeper than the plates and the edges glow bright where light pipes through.
- The outline is a convincing rounded offset of the logomark. Bosses sit in sensible positions.

4. **Problems, ranked**
1. **The windows are clear, not tinted plastic (all three wells).** Against ref2 and ref3, the disc reads as if seen through holes, and the teal only lives on the bands. Fix: carry the top plate across every well as the same tinted material. Use Volume Absorption density so that about 1 mm tints bright sectors to roughly 150–200 G/B with R under 90, and dark sectors go near-black teal. The window glass should tint, not the disc shader.
2. **The spectrum is narrow and cold (all windows).** Blue and cyan make up about 90% of it. ref4 is pink/magenta-led, with violet, cyan and green sectors. A value tweak will not reach this. Change the mechanism: drive hue from the actual grating equation, `λ = d·(sinθi − sinθr)` with d = 1.6 µm, projected onto the track tangent. Add at least two more small, bright area lights at different azimuths so several diffraction orders land in view. Target pink/magenta at 15–30% of saturated pixels.
3. **Hub and grounding.** The hub is a dark teal blob, and its bottom edge is sliced flat where it meets the rib (centre crop). Give it a steel ring around 80 grey and clip the rib around it. The object also floats: the contact is a 1–2 px grey line. Add a soft contact shadow reaching about 15–25 px, 200–235 grey, plus a faint glossy table reflection (ref2) at 5–10% intensity.

Secondary issues: the triple-offset ribs read like topo contours rather than one moulded ring wall. The dust specks are uniform glitter over the dark sectors; cluster them and cut density by about 50%.

5. **Research check**
- The render contradicts the finding "over a bright disc sector the tint glows": nothing tints the disc.
- It contradicts the finding "broad spectrum" (the ref4 target).
- It agrees with the finding that thick parts are deeper, and that colour sits in radial sectors with mirror between.
- Dust stays on the reflection and does not blur the view through the plastic. It agrees.

6. **What 8.5 needs**
- Tinted top plate over the wells.
- A physically driven, broader spectrum with pink/magenta present.
- A steel hub with clean geometry.
- A contact shadow and reflection.
- One clean ring wall per well instead of stacked contours.
