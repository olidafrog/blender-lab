# Review v04

1. **Score:** 5.2 / 10

2. **Targets**
- Background near-white: 255,255,255 all corners. **Hit.**
- Thick rim deeper than thin plate: rim 109,206,194 / 89,194,181 vs plate 113,178,170. The rim is *lighter* and about as saturated as the plate. **Missed.**
- Tint over bright sector glows lighter and more saturated than over dark: bright 255,255,255 / 195,255,255 vs dark 97,131,126. Lighter yes, but it clips to white and loses saturation. **Missed** (half).
- At least 4 hue families with mirror between: hue histogram of all five windows is 150–180° (cyan/teal) plus grey, with a faint yellow smear. That is one family. **Missed.**
- Hub mid-dark grey ~81,78,78: 66,82,80. Close, but teal-cast and a little dark. **Hit** (marginal).

3. **What works**
- The case outline is a clean rounded offset of the logomark, and the stepped bars and peanut read at a glance.
- Moulded details are present: stepped rim, window lips, screw bosses. They say "injection moulded".
- The disc has a correct radial anisotropic streak (bright spoke through the centre window) and a mirror base.

4. **Problems, ranked**
1. **Disc spectrum (all windows).** A cyan-white anisotropic streak, not diffraction. It shows none of ref4's pink, magenta, violet or green. Turning up saturation has not fixed this across rounds, so change the mechanism: drive colour from the angle between half-vector and track tangent (a grating equation, `sin θ = mλ/d`, mapped through a wavelength→RGB ramp, orders m = 1–3). Add a dark studio card or flag in reflection so the sectors sit on dark mirror. Target at least 4 hue families at S > 0.35 in the windows, with 20–40% near-black mirror between sectors.
2. **Case plastic reads frosted/opaque, and wear reads as grime (plates between windows, centre crop).** You cannot see the disc through the plates, but ref2 shows the disc right through the tinted top plate. The speckle is dark and blotchy, like dirt. Fix: roughness 0.0–0.05 on transmission, volume absorption (not a base-colour tint) so the rims go darker than the plates (rim/plate luminance ratio 0.6–0.8). Put scratches and dust only on the *coat* roughness/normal at ≤0.15 strength, and make them light, not dark.
3. **No contact with the table (bottom edge, 700–900,1100+).** The table is pure 255 right up to the case, so the object floats. Add a glossy white table (roughness 0.1–0.2) for a faint tinted reflection like ref2, plus a soft contact occluder shadow (table under the case at 200–235).

   Also: the hub is a teal-tinted puck cut off by a strut edge (a notch at its bottom). The well should clear it with a ring wall.

5. **Research check**
The image contradicts "tinted colour is volume absorption: thick parts deeper" (rims are lighter). It also contradicts "wear must not blur what is seen through" (plates are milky). Broad colour needs dark in the reflection, and the all-white room makes the disc look white-cyan, exactly as the research predicts.

6. **What 8.5 needs**
- A grating-based disc shader plus dark reflectors, giving ≥4 hues.
- Clear volume-absorbing plastic with the disc visible through the plates, and rims darker.
- Wear only on the coat layer.
- A glossy table with a contact shadow and a reflection.
- A clean ring wall around the hub.
