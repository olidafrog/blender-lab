# Review v06

1. **Score:** 6.3 / 10

2. **Targets**
- Background near-white: 255,255,255 in all four corners. **Hit.**
- Thick rim deeper than thin plate: plate 109,181,174. Inner window walls seen edge-on 68,112,109 (deeper, good). Outer perimeter wall 136,197,190 to 171,214,207, which is *paler* than the plate. **Missed** on the perimeter, the thickest part.
- Tint glows over a bright sector, darkens over a dark one: plates read a flat 90–118 R / 157–188 G whatever lies under them. The disc windows are untinted (the white ray reads 255,244,255, and the dark mirror 72,73,84 has no teal cast). **Missed.** No tinted plastic sits visibly over the disc.
- At least 4 hue families with mirror between: violet, blue, cyan, magenta, peach/orange and yellow-white, with grey mirror (72,73,84) between. **Hit**, but as thin spokes.
- Hub steel ~81,78,78: 54,69,68, darker and teal-cast under the dome. **Near miss.**

3. **What works**
- The logomark shape language carries well: the rounded offset outline, the windows following the three strokes, and the peanut form all read cleanly.
- Moulded detail is right: screw bosses with a centre pin, a stepped inner lip round each window, and top/bottom plates visible as two lines on the outer edge.
- The disc has real mirror plus diffraction behaviour: dark mirror with coloured spokes radiating from the hub, and the hue order within a spoke is correct.

4. **Problems, ranked**
1. **Case plates read as frosted solid resin, not a translucent case (every teal area).** Nothing of the disc shows through the plates, and the windows look like open holes. That kills the ref2/ref3 read of internals glowing through tint. Fix: make the top plate one continuous ~1 mm sheet that also covers the windows (thinner there, not cut away). Set transmission roughness to 0.00–0.05, and keep scratch/dust roughness on a separate clearcoat or specular layer only. Drive colour with Volume Absorption, density tuned so a 1 mm plate transmits 65–80%. Remove any SSS or milkiness.
2. **Disc spectrum is narrow starburst spokes, not ref4's broad sectors (centre and left windows).** Colour covers perhaps 25% of the disc, not 60–70%. Changing values won't fix this; the lighting has to change. Put 2–3 large, long emissive strips or softboxes where the disc reflects them, set against a dark card in reflection, so each band spans 20–40°. Raise saturation to the ref4 pink/green level.
3. **No grounding, and the hub reads wrong.** The case floats: there is no contact shadow and no table reflection like ref2. Add a glossy white floor (roughness 0.15–0.3) and a soft contact shadow. The hub sits under a dark teal lens dome, and a flat chord seam cuts its bottom edge (crop_centre). Replace it with a flat clear ring well and a visible steel clamp plate.

5. **Research check:** The diffraction physics agrees: the colour sits in the highlight, with mirror between. The image contradicts the claim that wear must not blur what is seen through the plastic, because the plates are fully diffused. It also contradicts thickness-dependent colour, since the perimeter wall is paler than the plate. The disc dust specks (tl, bl crops) are dense, uniform 1–3 px white dots that read as noise. Cut the density by about 70% and vary the size.

6. **What 8.5 needs**
- Clear, tinted, continuous plates that show the disc through them.
- Broad sector lighting on the disc.
- Deeper perimeter walls through absorption.
- A floor with contact shadow and reflection.
- A cleaned-up hub, and sparser dust.
