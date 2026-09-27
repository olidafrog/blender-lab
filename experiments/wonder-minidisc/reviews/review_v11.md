# Review v11

1. **Score:** 6.8 / 10

2. **Targets**
- Background: 255,255,255 at the corners, 249 at the top. **Hit.**
- Thick rim deeper than thin plate: side wall 47,138,126 vs band plate 73,171,159 (G ratio 0.81; ref2 is 0.74). **Hit, but weak.**
- Tint over a bright sector vs a dark one: bright centre 201,202,222, dark sector 52,62,73. Neither is teal, so the disc is **not seen through the tint at all**. **Missed.**
- Four or more hue families: saturated pixels are 150–210° (green, cyan, blue) about 95%, red ~1.5%, violet ~1.5%, pink/magenta ~0%. Mirror/dark between the sectors is present. **Missed** (3 strong families, and the pink that dominates ref4 is absent).
- Hub steel ~81,78,78: measured 43,64,62, dark and teal-tinted. **Missed.**

3. **What works**
- The diffraction reads as a real data surface: sharp radial rays converging on one hub, with a dark mirror between them, and consistent across all five windows, so it reads as one disc.
- Case construction: stepped double ring ribs round each well, the plate / gap / plate stack visible on the side edge, and small bosses. It is clearly moulded, and the outline carries the logomark well.
- The scene is clean, bright and white.

4. **Problems, ranked**
1. **Teal bands between the windows (whole frame).** They read as a flat, milky, solid resin slab (uniform ~73,171,159), not two 1 mm plates with an air gap. You cannot see the bottom plate, the table or the inner walls refracted through them. Fix: remove any volume scatter or subsurface; use transmission 1.0 at roughness 0.02–0.06 with an absorption-only volume. Set the density so one thin plate reads around 140–190 in G and walls seen edge-on read around 60–110. Let the hollow and the inner walls show through, as the ref3 internals do.
2. **The windows carry no tint (every window).** The disc sits beside the plastic, not inside it, so the ref2 glow/darken effect (the core of "coloured plastic surrounding the disc") never happens. The dust specks show there is a pane: give it the same teal absorption at plate thickness, so bright rays go luminous teal-white and dark sectors go deep teal.
3. **Spectrum and hub (disc).** The spectrum is cyan/blue-heavy; ref4 is pink/magenta, then violet, cyan and green. Value tweaks will not add pink: add warm/magenta-balanced light sources at other azimuths, or map a wider wavelength range / second order in the diffraction shader. Target at least 15% of saturated pixels in the 280–350° range. The hub is a black plug: make it metallic 1.0, base ~0.3 grey, roughness 0.25–0.35, and add ref4's stepped clear clamp rings.

5. **Research check**
The render agrees on the radial sectors with mirror between them. It contradicts "tint over a bright disc sector glows", because there is no tint over the disc. It also contradicts "thin plates paler": the plates are not see-through, and the plate-to-rim contrast is small. Wear is only dust specks in the windows. The plates show no scratches, and the specks are slightly dense and coarse (bottom-left window).

6. **What 8.5 needs**
- Clear-absorbing plates with a visible air gap and refracted internals.
- A tinted window pane over the disc.
- Pink/magenta in the spectrum, and a steel hub.
- A faint table reflection or contact shadow under the edge, as in ref2.
- Fine scratches on the top plate, reflection only.
