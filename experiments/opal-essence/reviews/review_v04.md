# Review — v04

1. **Score:** 5.6 / 10

2. **Targets**
- Background: #000000 at all corners and edges. **Hit.**
- Deep teal/navy behind dark parts (#012437–#085c62): dark parts read brown, #2c201d–#3e302a (gear #372d2b, top band #59392b). Left edge #275343 is green, not teal. **Missed.**
- Sage #7c9f93: #83925f at (560,1400) is olive, too yellow. **Near miss.**
- Cream #e7c69d: no cream zone. It jumps from yellow #e4ac63 to peach #f8b19a. **Missed.**
- Amber #fdbb55: #eeaa65 at best. **Near hit.**
- Orange #fca321: best #ec9649, mostly #f3a974. Washes to apricot. **Missed.**
- Hot pink/coral #fe6f6b: #f25c56. Close, but leans red. **Hit.**
- Opal blue skin #9fb8b7: no blue-white anywhere (17 of 32,000 samples). **Missed.**
- Micro-type: "WONDER MATERIALS" cap height is ~14 px, 0.7% of frame. Too small. The lower-right lockup is almost invisible. **Missed.**

3. **What works**
- The black ground and the plate's cut-out silhouette with its brackets sit well in the ref 02 family.
- Depth blur varies with distance. The right-hand dumbbell and blocks melt; the upper gear stays crisp.
- The top micro-type band has real edge glints and the right feel of moulded lettering.

4. **Problems, ranked**
1. **Whole plate: it reads as coloured gel filter, not milky resin.** The gradient tints the plate like cellophane. Dark parts show through as muddy brown at full contrast, so the plate has no body. In refs 02–04 the milk lifts deep parts toward cream or teal-grey, and the colour glows from behind. Fix: change the mechanism, not the tint value. Put the gradient on emissive backlight cards behind the parts. Make the plate near-white volume scatter with scatter albedo about 0.9 and density high enough that parts 10 mm or more behind reach 45–65% of the surrounding luminance. Tint the darkest parts navy/teal (#0a3a44) so that where they show they read cool, not brown.
2. **Vertical white strip highlight at x≈1075.** It is a perfect, full-height stripe that clips to #fdf6f3 and flattens everything under it. It reads as a CG plane. Fix: give the plate a very gentle warp or low-frequency bump (0.2–0.5 mm amplitude) so the reflection bends and breaks. Cap the peak at 0.85. Move the strip light so its reflection grazes an edge, not the centre.
3. **The "Wonder" logotype is flat grey paint.** It is opaque #4b484f with no edge light, so it looks like a decal under the plate. Fix: model it as raised clear resin (0.3–0.5 mm) in the plate material with no albedo change. Add a raking key from about 15° so it reads by highlight lines and a soft shadow, like "Imagined Wreckage" in ref 03.

5. **Research check**
- Contradicts the opalescence claim: there is no blue skin or warm transmitted core. The colour is a painted left-to-right gradient.
- Contradicts "clear resin, read by edge highlights" for the logotype.
- Distance blur agrees with the research.
- Surface realism is weak. There is no grain, no satin frosting, no wet droplet highlights and no edge thickness glow.

6. **What 8.5 needs**
- Put the gradient in a backlight behind the parts, with a milky scatter plate over it. Dark parts should read teal, not brown.
- Add a blue-white opal sheen where the plate faces the key light.
- Make the logotype and lockups raised clear relief with cap height 1–1.5% of frame.
- Break up the strip highlight with a surface warp. Add wet edge highlights and fine film grain.
- Saturate the orange band toward #fca321 and add a cream zone between sage and amber.
