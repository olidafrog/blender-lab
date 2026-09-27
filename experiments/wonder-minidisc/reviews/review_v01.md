# Review v01

1. **Score:** 4.8 / 10

2. **Targets**
- Background: 255,255,255. **Hit.**
- Thick rim deeper than thin plate: outer rim (left) 67,177,156 and side wall (bottom) 115,196,183, against top plate 53,153,138. The rim is *lighter*. **Missed.**
- Tint over bright disc glows vs dark: bright 163,242,234 against dark 22,86,72. The direction is right, but the bright end washes toward white instead of getting more saturated. **Partial hit.**
- At least four hue families: saturated disc pixels fall only in 120–210° (green, cyan, blue), with about 75% at 150°. **Missed** (two to three families, no pink, magenta or violet).
- Hub mid-dark grey: 42,65,61, a dark teal puck. **Missed** (too dark and tinted).

3. **What works**
- The outline carries the logomark: stepped bars and a peanut, with an even offset and a stepped perimeter lip.
- The screw bosses and the recessed well rims read as moulded features.
- The frame is clean and white, with soft contact shading under the case edge.

4. **Problems, ranked**
1. **The disc does not read as a CD (all five windows).** It looks like crumpled foil or water caustics: large faceted blue and white shards, with no concentric tracks, no radial sectors, no mirror between. The window tops seem to be domed or thick, so they act as lenses and scramble it. Fix: make the window plates flat, about 1 mm, IOR 1.58. Drive the disc from one centre with a thin-film or grating spectrum keyed to the angle between the tangent and the half-vector, so colour runs in wedges from the hub. Keep roughness at 0.02–0.05 so it stays mirror between the wedges. Add a dark card or softbox gap in the reflection, so dark sectors exist.
2. **The case plastic reads as opaque painted teal, not volume-tinted polycarbonate.** The plate between the windows hides the disc completely, and edges are lighter than faces. Fix: use real Volume Absorption (no diffuse or SSS in the case). Set density so a 1 mm plate transmits about 70–80% and the rim or edge-on wall goes 2–3× darker. The disc must stay visible under *all* the plastic, as in ref2 and ref3. The window-versus-plate split should come from thickness only.
3. **The dust is far too heavy and the wrong colour (centre and 800_600 crops).** Dense red-brown speckle covers every face, so it reads as grime or glitter. Fix: at most ~0.5% coverage, neutral grey-white, and only in roughness and specular, never in base colour or transmission. Add faint directional scratches visible only inside highlights.

5. **Research check**
- The render contradicts "colour runs in radial sectors through the highlight, with a plain mirror between": there are no sectors and no mirror.
- It contradicts "thick parts are deeper, thin plates paler": that relationship is inverted here.
- It contradicts the finding that wear must not change what is seen through the plastic: the dust tints what is seen through the case.
- It ignores the ref2 table reflection: none is visible.

6. **What 8.5 needs**
- A radial-sector diffraction disc with a mirror between and at least four hue families. The case tint must be light enough on thin plates that pink and violet survive, or use clear windows.
- A flat, thin case that shows the disc everywhere, with the air gap visible at the well walls.
- Absorption-driven tint, with the rim clearly darker.
- A hub in steel grey (~80).
- Subtle neutral wear.
- A glossy white table with a faint reflection.
