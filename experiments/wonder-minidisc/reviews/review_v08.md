# Review v08

1. **Score:** 6.2 / 10

2. **Targets**
- Background near-white: 255,255,255 at all corners and below the object. **Hit.**
- Thick rim deeper than thin plate: plate 72,167,155; outer side wall seen edge-on 160–184,247–255 (paler, near-white), with only a 1–2 px dark line at 29,54,48. **Missed.** The thick edge reads as a bright glassy band, not denser teal.
- Tint over bright sector vs over dark sector: web plates read 70–78,165–178,153–166 whether the disc beneath is a bright ray or a dark sector (x670 and x960 columns). The disc in the windows is untinted neutral (200,202,222 bright; 55,68,77 dark). **Missed.**
- At least four hue families: violet (h 284), blue (227–231), cyan (206), green (133), plus a weak warm 175,157,136. **Hit on the letter, missed on the spirit:** no pink/magenta or yellow, and HLS saturation only 0.16–0.46.
- Hub steel ~81,78,78: 37,55,54, dark and teal-cast under a lens cap. **Missed.**

3. **What works**
- The disc reads as a CD: radial rays through a highlight, grey mirror between, sectors converge on the hub.
- Construction vocabulary is right: perimeter wall, inner well rim, screw bosses with holes, rounded offset of the logomark with an even gap. The outline carries the mark well.
- Dust and flecks are small, sparse and sit in the reflection, not blurring the disc.

4. **Problems, ranked**
1. **The plastic is a teal slab with holes, not a tinted shell (whole case).** The webs are opaque, uniform teal and the disc never shows through them. The windows look like cut-outs because the disc behind them has no tint. Fix the mechanism, not the values: make the top plate one continuous ~1 mm sheet over the disc and webs, with the walls as separate thin ribs below it. Remove the solid fill and stacked coplanar faces under the webs. Use one Principled BSDF with transmission 1 and roughness 0.02–0.06, and set the colour with Volume Absorption so a 1 mm path keeps 60–75% of the light and a 6 mm edge path keeps 15–30%. Set the transmission and total bounces to at least 16. Goal: the rays run continuously under the webs, glowing teal over bright sectors and going dark over dark ones.
2. **The spectrum is cool and pastel (every disc window).** There is no pink, magenta or warm yellow, and ref4's dominant hues are pink and magenta. Extend the diffraction ramp through 380–700 nm and add the 2nd order, since the red/violet overlap is what makes magenta. Put 2–3 bright, small sources at different azimuths so more sectors appear. Target a saturation of 0.5–0.7 in the bright sectors.
3. **No contact with the table (bottom edge).** The render goes to 255 white 2 px below the case. There is no contact shadow and no reflection like ref2's. Add a glossy shadow-catcher floor with 5–12% reflection and a contact shadow of 200–230 within about 15 px of the edge. The hub should also read as bare steel at 75–90 grey, not under a teal lens. There is a notch artefact where the hub cap meets the well rim.

5. **Research check**
The image contradicts "tinted colour is volume absorption; thick parts deeper": the edges are paler. It also contradicts "tint glows over bright sectors, dark over dark": the tint doesn't vary with the disc. The diffraction finding (sectors plus mirror, needing dark reflections beside bright sources) is honoured.

6. **What 8.5 needs**
- A thin transmissive shell so the disc reads through all the plastic, with depth from absorption.
- Pink and magenta in the spectrum, with more saturation.
- A contact shadow and floor reflection.
- A steel hub, and the notch at the hub cap fixed.
