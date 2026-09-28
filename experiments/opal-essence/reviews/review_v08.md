# Review v08

1. **Score:** 5.9 / 10

2. **Targets**
- Background: #000000 at all edges. **Hit.**
- Deep teal/navy: #0c3534 on the left rim. **Hit.** But dark parts behind the plate read near-black brown (gear #191715), not teal.
- Sage #7c9f93: #56755c. **Missed** (too dark, too green).
- Cream #e7c69d: the cream zone is khaki #6c6147 / #706f4d. **Missed** badly.
- Amber #fdbb55: best on plate #a48255 / #b27d48. **Missed** (about 35% under).
- Orange #fca321: #cb773f. **Missed** (under, and redder).
- Hot pink/coral #fe6f6b: #cd4d4b to #d0534e. **Missed** (about 20% under).
- Opal blue skin #9fb8b7: none on the material. The only blue is a screw reflection. **Missed.**
- Micro-type cap height: about 18–24 px (0.9–1.2%), highlight lines present. **Hit.**

3. **What works**
- Depth blur is correct: the small gear near the back face stays crisp and the big gear melts. This matches refs 02–03.
- Micro-type on the top strip and the vertical edge line reads as moulded relief, subtle and findable.
- Black levels, screws and corner brackets feel industrial and clean.

4. **Problems, ranked**
1. **Whole plate: no milky scatter. It reads as a dark smoked filter, not luminous resin.** Plate mid-tones sit at 35–55% lightness; ref 02 sits at 80–95%. Parts behind stay black-brown instead of being lifted and tinted by the milk. Past rounds tuned values; change the mechanism. Add a real scattering layer: a Volume Scatter (anisotropy 0.3–0.5, density high enough that black parts behind lift to 10–25% lightness) or a thin white Diffuse/SSS mix at 25–40% over the transmission. Then raise the backlight gel energy until the plate core reaches 80–90% lightness.
2. **Centre band: the gradient goes muddy.** Teal and orange mix into olive/khaki (x 600–900). Ref 02 passes through a bright cream-white between teal and amber. Add an explicit cream stop (#e7c69d or lighter) at 35–45% of the ramp. Drive the colour from an emissive gel card behind the plate, not a tinted transmission colour. Tinted transmission multiplies and darkens the mid-point.
3. **Bottom left: the Wonder logotype looks like a flat grey decal.** "Won" is a flat #434449 fill with no edge light, and only "d" and "er" catch highlights. It also sits over a dark block and looks printed. Make it the same clear resin as the plate: no fill colour, a 0.3–0.5 mm raise, a 45° bevel, lit by the key so every glyph gets a highlight line and a soft shadow.

5. **Research check**
- Agrees: blur grows with depth behind the plate. Relief is subtle.
- Contradicts: no opal response. There is no blue skin where the plate faces the light and no warm transmitted core. Ref 02's wet, glossy highlights are also missing. The plate face has almost no specular except at strip edges.

6. **What 8.5 needs**
- A scattering layer so the plate glows milky and lifts the dark parts to teal.
- A cream-white stop, and amber/pink pushed to target brightness.
- A clear moulded logotype, not a grey fill.
- Wet specular streaks from a strip light across the plate, plus faint surface scuffs and film grain.
- A blue-white Fresnel/skin tint (#9fb8b7) on the lit face.
