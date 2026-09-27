# Review v03

1. **Score:** 5.6 / 10

2. **Targets**
- Background: 255,255,255 everywhere, including under the case. **Hit.**
- Thick rim deeper than thin plate: outer lip (left, x≈330) is 53,141,123 and the bottom side wall is 149–179,236–252,221–241, against the top plate at 54,166,150. The side wall is far *paler* and the lip is about equal. **Missed.**
- Tint over bright sector glows: bright is 200,255,255 and 130,254,243, dark is 68,124,124. The direction is right, but the bright end clips to near-white cyan instead of getting more saturated. **Partial hit.**
- At least four hue families: every saturated disc pixel falls in 120–210° (green, cyan, blue). About 78% are at 150–180°. No pink, magenta, violet or yellow, and no dark mirror between the sectors (the darkest are ~70,125,125). **Missed.**
- Hub steel grey: 55,84,80 and 44,74,71. The value is close, but it is a teal puck, not steel. **Missed.**

3. **What works**
- The disc now has radial wedges running out from one centre, which is the right structure. This is a real step up from v01's foil.
- The outline and shape language hold up: an even rounded offset of the logomark, a stepped perimeter lip and a visible parting line.
- Screw bosses, recessed well rims and a clean white field give it a moulded-product feel.

4. **Problems, ranked**
1. **The disc spectrum is one colour (all windows).** The wedges are anisotropic cyan sheen, not diffraction. They are also seen through teal plastic, which removes red, so pink and magenta cannot survive. A value tweak will not fix this. Fix: make the window plates clear or near-clear (density ≤0.1 of the frame; the frame can stay teal, as ref2 mixes clear windows with tinted body). Drive the disc colour from a grating or thin-film ramp indexed by the tangent·half-vector angle, cycling through the full spectrum 2–3 times per quadrant. Set the environment to mostly black with 2–3 narrow bright strips, so mirror-dark gaps (value <40) separate the wedges.
2. **The case still reads as painted teal, not absorbing polycarbonate (the frame bands and side walls).** The disc is invisible under the bands, and the side walls go pale instead of deep. Fix: the case shader should be glass or refraction plus Volume Absorption only, with no diffuse, SSS or base-colour tint. Tune density so a 1 mm plate transmits 70–80%, and the edge-on wall reads 2–3× darker (target wall ≈20–35,90–110,85–100). The disc wedges must show dimly through the bands.
3. **The dust is unchanged since v01 (the centre and 800_600 crops).** It is dense orange-brown speckle on every face and reads as rust or glitter. Fix: under 0.5% coverage, neutral light grey, driving roughness and specular only. Add a few directional micro-scratches that only show inside the highlight.

5. **Research check**
- The render contradicts "colour runs in radial sectors… with a plain mirror between": the sectors exist, but there is no mirror and only one hue.
- It contradicts "thick parts are deeper": the walls are lighter.
- It contradicts "wear must not blur what is seen through": the dust tints the transmission.
- The ref2 table reflection and contact shadow are absent, and the case looks pasted on white.

6. **What 8.5 needs**
- Clear windows over a full-spectrum grating disc, with a dark-strip environment.
- Absorption-only case plastic, with dark walls and the disc visible under the frame.
- Subtle neutral wear.
- A steel hub at ~80 grey.
- A glossy white floor with a faint reflection and a contact shadow.
