# wonder-minidisc — research

## Read of the reference

In order of how much they matter to the look:

1. **Diffraction sectors on the disc** (ref4, ref2, ref1). The colour sits in broad radial sectors that sweep around the hub. Each sector is a smooth hue ramp (pink → magenta → violet → cyan/green in ref4), not a noisy rainbow. Between sectors the disc is a plain grey mirror. It is diffraction from concentric tracks (1.6 µm pitch). Light diffracts only in the plane across the grooves, so colour spreads along spokes through the highlight. ref4 is a **flatbed scan**: the ghosted "INSERT" type shows the moving scanner lamp, and the lamp's extended strip is why the whole disc is covered in colour.
2. **Tinted translucent case** (ref2, ref3). The colour depends on thickness. Thin walls are clear-ish red (170, 28, 26), the thick rim reads deep red (125, 20, 15), and over a bright disc sector it goes orange (255, 129, 39) because the mirror behind sends light back through the tint. This is volume absorption (Beer–Lambert), not a surface tint.
3. **Case shape language** (ref4, ref2). Two moulded shells: thin top and bottom plates, a perimeter wall, a raised ring wall around the disc well, round screw bosses in the corners, ribs and small notches on the walls, rounded corners, and a parting line. Through clear plastic every internal wall refracts and doubles, and that busy internal structure is what makes it read as a *case*.
4. **Hub** (ref4). A dark steel clamping plate (81, 78, 78) with turned concentric rings, inside a clear polycarbonate hub zone with stepped rings and a black printed text ring.
5. **Metal shutter and label** (ref2, ref4). A grey brushed-metal sleeve wraps one edge. The label window is frosted.
6. **Scene**. Pure white background (255). A soft blue-grey reflection on a glossy table under ref2 (169, 186, 204). Soft even studio light.
7. **Pastel holographic mode** (ref1). The same sector sweep, desaturated. Film saturation is only 0.1–0.45, with visible fine concentric lines. This is a rougher, less saturated variant of the same material.

## Most likely process

All four references are photographs or scans of real objects, so the process to copy is the real one:

- **Disc:** an aluminium or magneto-optical mirror with a 1.6 µm grating, under 1.2 mm of polycarbonate, lit by large extended sources, which gives colour over much of the surface.
- **Case:** injection-moulded tinted polycarbonate, 1–1.3 mm walls, colour from absorption.

We render it physically:

- **Disc:** a BSDF (bidirectional scattering function, the rule for how a surface bounces light) that shifts the mirror reflection by the grating angle for each wavelength band.
- **Case:** a closed moulded shell with homogeneous volume absorption.
- **Studio:** real softboxes in a white studio HDRI, so the grating has bright sources to diffract.

## Techniques to use

**Diffraction (disc).** Stack one anisotropic Glossy BSDF per spectral band, each with its normal tilted about the groove tangent by α = ½·asin(mλ/d). Use orders m = ±1 and ±2, and 8 bands from 400 to 700 nm.
- Tangent T = Z × R, where R is the object-space radial direction from the groove centre.
- Band colours come from Zucconi's `spectral_zucconi6`, computed in Python and normalised to sum to white. A "Saturation" input mixes them toward grey, which gives the pastel mode.
- Add an m = 0 mirror base, tinted for the recordable pink.
- Put a polycarbonate coat on top: a Fresnel mix with a clear Glossy, IOR 1.58.
- This is a true BSDF, so every light and the HDRI diffract, and there is no noise-based wavelength picking for the denoiser to smear.
- Works in 4.4 and 5.x with nodes only.
- Sources: GPU Gems ch. 8 (Stam); Zucconi CD-ROM shader; Silverwing diffraction tutorial / 80.lv CD (tilted normals per order).

**Case plastic.**
- Principled BSDF, Transmission 1, IOR 1.585, Roughness about 0.02 plus a scratch map.
- Volume Absorption with density and colour derived from one target colour C at a reference thickness d:
  - k = −ln C
  - density = max(k)/d
  - absorption colour = 1 − k/max(k)
- This gives one Colour input that behaves physically.
- A Clarity input mixes toward a diffuse, opaque plastic (the grey PS1 card).

**Coloured shadows.**
- On shadow rays (Light Path "Is Shadow Ray"), the case becomes a Transparent BSDF. Shadow rays still pass through the volume, so the shadow takes the plastic colour from the same absorption. That gives a bright, tinted shadow like a caustic, with no MNEE noise.

**Case geometry.**
- Offset outlines from a numpy signed distance field of the logomark, with marching squares to trace the edges (`scripts/outline.py`).
- Outer silhouette: an offset of about 11 units with about 7 units of closing, which gives a rounded logo blob.
- Solid prisms and exact booleans:
  - outer shell minus the inner hollow,
  - plus ring walls around each piece's well,
  - plus screw bosses.
- Bevel the prisms before the booleans.
- Flat-shade the caps (see `knowledge/gotchas/cycles.md`).

**Imperfections.**
- CC0 maps from ambientCG: Scratches005 (sparse), Fingerprints002, SurfaceImperfections015 (dust). They drive roughness only, with a tiny bump.
- Dust occludes: a dark diffuse mix at low coverage.
- Polar coordinates for swirl scratches on the disc, later.

**Studio.**
- Poly Haven `studio_small_09` HDRI.
- A large overhead softbox (area light) and one strip light for a crisp reflection.
- A white sweep floor with a clearcoat at roughness about 0.2 for the soft reflection.

**Anti-aliasing.** No groove textures at all: colour comes from the tangent maths, so there is nothing fine to alias. The fine concentric lines of ref1 are optional, and would be drawn as a low-contrast ring pattern at 2× only if a reviewer asks.

## Rejected approaches

- **An emission term that samples the HDRI at the diffracted directions.** It is exact for the environment, but ignores the area lights and the case's shadowing, and it glows. The tilted-lobe BSDF gets the same physics as a real closure.
- **Stam single-light colour** (λ = d·u/m with an Empty as the light). Only one light is correct. Kept as a fallback.
- **Thin film only.** That is interference: pastel colour with no sectors. At most a small accent for the recordable MO tint.
- **OSL.** It works on OptiX in 4.4, but there are open bugs and it gains nothing over nodes.
- **White-noise wavelength picking** (the common tutorial trick). The denoiser smears it.
- **Real groove bump textures.** They alias into moiré.
- **MNEE caustics for the coloured shadow.** They ignore volume absorption and are noisy.
- **Voxel remesh of the case.** It terraces bevels.

## Numeric targets

Measured from reference crops (sRGB 0–255):

| Where | Target |
|---|---|
| Background (ref2) | 255 white, pure |
| Table reflection under case (ref2) | ≈ (169, 186, 204), soft blue-grey |
| Red case, thin wall over dark | (170, 28, 26) |
| Red case, thick rim | (125, 20, 15) |
| Red case over bright disc sector | (255, 129, 39) |
| Red case over dark disc sector | (77, 33, 17) |
| Clear case (ref4) | ≈ (187, 187, 183), nearly neutral |
| Disc pink sector (ref4) | ≈ (254, 201, 172) |
| Disc violet band (ref4) | ≈ (48, 51, 79) |
| Disc cyan sector (ref4) | ≈ (73, 136, 175) |
| Hub steel (ref4) | ≈ (81, 78, 78) |
| Pastel film saturation (ref1) | 0.1–0.45, lightness 0.7–0.94 |

The disc must show at least four distinct hue families (pink/magenta, violet, cyan, green, plus yellow if possible) somewhere on the logo. Between sectors, it shows mirror-grey.

## Open questions

- Which anisotropy sign and roughness give radial streaks instead of rings? One test render settles it.
- How many lobes before the colour turns pastel from overlap? Start with 8 bands and m = ±1, ±2.
- Does the dense internal structure read as a case or as clutter at full frame?
- Groove centre: the disc's hub point on the middle stroke, not the logo centre. Does a hub fit the 27-unit stroke?
- AgX versus Standard: a red case under AgX may go peach. Compare early.

## Sources

- Stam, GPU Gems ch. 8, "Simulating Diffraction": https://developer.nvidia.com/gpugems/gpugems/part-i-natural-effects/chapter-8-simulating-diffraction
- Zucconi, CD-ROM shader and "Improving the rainbow": https://www.alanzucconi.com/2017/07/15/cd-rom-shader-2/ , https://www.alanzucconi.com/2017/07/15/improving-the-rainbow-2/
- Anisotropic CD shader (tangent radial): https://odederell3d.blog/2018/06/09/cycles-tangent-node-anisotropic-reflection/ , https://blenderartists.org/t/anisotropic-compact-disc-shader/596516
- Tilted normals per order: https://80.lv/articles/this-compact-disc-shader-made-in-blender-looks-very-impressive , https://blenderartists.org/t/help-with-blender-cycles-diffraction-shader/1527780
- MiniDisc construction: https://www.minidisc.org/ieee_paper.html , https://en.wikipedia.org/wiki/MiniDisc , https://patents.google.com/patent/CA2049705C
- Volume absorption: https://blenderdiplom.com/en/tutorials/419-tutorial-absorption-in-cycles.html
- Transparent product photography: https://www.replicasurfaces.com/blogs/q-as/how-to-photograph-products-with-transparent-or-translucent-materials-effectively
- Shadow caustics limits: https://www.blendernation.com/2022/06/22/using-shadow-caustics-in-blender-3-2/
- Assets (CC0): Poly Haven HDRIs, ambientCG imperfection maps. See `assets/SOURCES.md`.
