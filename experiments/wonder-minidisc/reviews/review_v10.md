# Review v10

1. **Score:** 6.9 / 10

2. **Targets**
- Background white: 255 at the corners and under the object. **Hit.**
- Thick rim deeper than thin plate: bottom rim 29,72,66 and right rim 29,100,90, against band plate 20,56,51 to 31,71,66. The thin plate is as dark as the rim, or darker. **Missed** (inverted; in v09 this was a hit at 74,172,160).
- Tint glows over bright sectors and goes dark over dark ones: bright 87,174,172 against dark 49,62,72. **Hit** for the cyan sectors. The hub-top highlight is still neutral lavender (192,193,214), with no teal.
- Four or more hue families: of saturated window pixels, blue is 50%, cyan 42%, green 5%, violet 1.5%, orange 0.7%, pink/magenta 0%. **Missed.** Nothing changed since v09.
- Hub steel ~81,78,78: measured 40,59,57, a dark teal puck. **Missed.**

3. **What works**
- A tinted plate now sits over the wells. Sectors pick up teal and read as seen through plastic, not through holes.
- The contact shadow is in: the right edge ramps from 183 to 239 over about 70 px. The object sits on the table.
- The layered edge (plate, gap, plate) and the logomark offset outline still read well.

4. **Problems, ranked**
1. **The bands read as a solid slab, not a hollow case (every teal band).** The bands are near-black teal (20–31, 56–71) over a white table, darker than the thick rims and much darker than the same plate over the wells. Two 1 mm plates over white should glow pale, around 70–110 R, 160–200 G/B, as v09's did. Adding absorption darkened everything. Fix: find the cause rather than turn density down. Check the band cavity for hidden geometry (a disc proxy, a closed solid fill, or the bottom shell's inner faces with flipped normals). Check that Transparent/Transmission bounces are 16 or more, so light passes through four interfaces. Target: band L at least 1.6x the rim L.
2. **Narrow, cold spectrum (all windows).** It is still 92% blue and cyan with no pink, which puts it two rounds behind. Value tweaks have failed, so change the mechanism. Drive hue from the grating equation with d = 1.6 µm, against real light directions. Add two or three small, hot area lights at other azimuths, including a warm one, so the m = 1 orders land red, magenta and green in view. Target 15–30% pink/magenta and 10% or more green.
3. **Hub (centre crop).** It is a flat dark-teal button with a soft bevel. Model a steel clamp ring (roughness 0.25, metal, about 80 grey) with a centre hole and a clear plastic clamp step around it, as in the ref4 hub crop.

Secondary: each well still has three stacked contour lines. Merge them into one ring rib. Dust reads as uniform orange glitter; cluster it and halve it.

5. **Research check**
- The bands contradict the finding "thin plates paler".
- The narrow spectrum contradicts "broad spectrum".
- Radial sectors with mirror between them: agrees.
- Dust affects the reflection only and does not blur the view through: agrees.

6. **What 8.5 needs**
- Pale, glowing hollow bands, with rims darker than the plates.
- Pink/magenta and green sectors from real diffraction plus extra lights.
- A steel hub with a centre hole.
- One ring rib per well, and sparser dust.
