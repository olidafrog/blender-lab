# opal-essence — research

## Read of the reference

In order of how much each matters to the look:

1. **Milky translucent body.** The resin is see-through but hazy. Parts touching the back face read sharp (ref 02 left brackets); parts further back melt into soft shapes. The blur grows with distance from the plate.
2. **Colour glowing through the body.** A wide, smooth gradient (teal → cream → amber → orange → hot pink, ref 02) that reads as light *inside* the plastic, not paint on it. Dark parts behind block it and leave deep teal-black zones.
3. **Opalescence (ref 01).** Blue-white skin where light scatters back at the viewer; warm amber-yellow where light passes through thick sections. The real Lalique glass shows both at once.
4. **Wet glossy surface.** Sharp specular highlights over a frosted body: long streaks along folds, bright rings around rivets (ref 02, 04).
5. **Raised clear type.** Moulded lettering stands proud of the surface; it reads mostly from its highlight edges and a faint shadow (ref 03 blackletter, ref 04 monospaced caps). Clear, same material as the plate.
6. **Industrial hardware.** Black glossy clamps with screws at corners, pearl rivets, organic melted/bitten edges on the plate.
7. **Photographic capture.** Flat-on shot against pure black, shallow depth of field in the close crops, slight grain, mild bloom on the hottest colours.

## Most likely process

Ref 01 is a real photograph of Rayleigh-scattering opalescent glass (Sabino/Lalique), lit with a low spot behind and a soft front light on black. Refs 02–05 are AI images imitating a real studio setup: a milky acrylic sheet over parts, backlit with coloured gels thrown out of focus to form a gradient, plus a hard front or strip light for the wet highlights. In 3D the same result comes from: a frosted transmissive surface for the distance blur, a Rayleigh-weighted scattering volume inside for the opal blue/amber split, and a hidden gradient emitter behind the parts for the colour.

## Techniques to use

- **Distance-dependent blur — rough transmission.** Principled BSDF, Transmission 1, IOR 1.49, roughness ~0.1–0.15. The spread angle turns into a wider patch the further the part sits behind the plate, which is exactly the ref. Cheap and low-noise. [BlenderArtists](https://blenderartists.org/t/blur-items-inside-behind-glass/600295), [Distinctness of image](https://en.wikipedia.org/wiki/Distinctness_of_image). All versions.
- **Wet surface over frosted body — Principled Coat.** Coat Weight 1, Coat Roughness ~0.02, so highlights stay sharp while transmission stays rough. 4.0+.
- **Opalescence — Volume Coefficients with Rayleigh-ratio scatter.** Scatter R:G:B ≈ 1 : 2.3 : 5.7 (Rayleigh 1/λ⁴ at 680/550/440 nm). For a 14 mm plate, blue ~140–250 m⁻¹ gives optical depth ~2–3.5 in blue and ~0.4 in red: blue scatters back, red/amber passes. Small warm absorption. Anisotropy ~0.35. [Opalescence](https://en.wikipedia.org/wiki/Opalescence), [Rayleigh coefficients](http://docs.eclat-digital.com/ocean2018-docs/reference/nodes/scattering/rayleigh.html), [Volume Coefficients](https://docs.blender.org/manual/en/dev/render/shader_nodes/shader/volume_coefficients.html). 4.5+ (Volume Coefficients); on 4.4 use Volume Scatter + Absorption.
- **Colour gradient — gel backlight.** Photographers throw two or more gels out of focus behind a diffuser to make a gradient ([Jake Hicks](https://jakehicksphotography.com/latest-techniques/2021/1/8/creating-gradients-with-coloured-gels)). In Cycles: an emission plane behind the parts, `visible_camera = False`, `visible_glossy = False`, with a 5-stop gradient built from group inputs so every stop colour and position is editable on one node.
- **Long glossy highlights — strip light at the mirror point**, glossy-only (hidden from diffuse and transmission), as in `printed-plastic`. Honeycomb via `light.spread`.
- **Raised type — Text objects** with extrude ~0.2–0.5 mm and a bevel (moulded lettering has radiused edges; relief 0.2–0.5 mm per [Protolabs](https://www.protolabs.com/resources/design-tips/improving-part-moldability-with-draft/), [UPM](https://www.upminc.com/resource/adding-text/)). Stays editable. Same resin material. A low grazing "rake" light to catch edges. Wonder logotype from the library mesh, flattened to the same relief.
- **Camera:** 100 mm, f/4–8, focus empty on the top face. AgX with the Punchy look for the saturated pink/orange.
- **Imperfections (later rounds):** smudges and fine scratches on coat roughness only; tiny wet droplets near rivets.

## Rejected approaches

- **Subsurface scattering (Random Walk) for the body.** Light leaves the surface diffusely, so no image passes through. Kills the "see the parts behind" read. SSS values also changed scale in 5.2 (4.4 files look different).
- **Blur in post / depth-of-field only.** DOF blurs by distance from the camera, not from the plate, and would soften the raised type too.
- **Painting the gradient into the base colour.** Reads as paint on a surface, not light inside. May add a small tint later.
- **Bump-mapped text.** No silhouette or edge highlight; flat at grazing angles.
- **Parts inside the volume.** Known artefacts; keep hardware outside the resin mesh.

## Numeric targets (from the references, sRGB)

- Background: ~#020808 (ref 02), pure #000000 (ref 01). Near-black, never lifted.
- Gradient across ref 02 at mid-height, left → right: #012437 (under parts), #085c62 teal, #7c9f93 sage, #b2b9a3, #d1c3a4, #e7c69d cream, #f2c18b, #fdbb55 amber, #fca321 orange, #f97a33, #fe6f6b hot pink at the right edge. Top of frame is paler: cream #d6c6ac → #fcbd73 → #fe8589 pink.
- Lalique: blue-white skin #9fb8b7, yellow core #c7c185, amber #bca564, cool edge #54787a.
- Secondary palette (ref 06): teal-blue ground #228caa / #014873, mint rim #59d467, coral #fc7562, peach-cream #d2c0b1.
- Raised type in ref 04: cap height ~1.3% of frame height; relief reads only as a highlight line plus a soft shadow.

## Open questions

- Does rough transmission 0.1–0.15 blur parts 2–3 cm behind enough, or do we need more volume forward-scatter?
- Does the Rayleigh volume show blue at the skin with a strong backlight, or does the backlight swamp it? May need a stronger top fill.
- Is the raised type readable at full frame, or only in crops (as in the refs)? It should be subtle.
- Noise and render time of the volume at 256–1024 samples on Metal.

## Sources

- https://en.wikipedia.org/wiki/Opalescence
- http://docs.eclat-digital.com/ocean2018-docs/reference/nodes/scattering/rayleigh.html
- https://docs.blender.org/manual/en/dev/render/shader_nodes/shader/volume_coefficients.html
- https://developer.blender.org/docs/release_notes/5.0/cycles/ (null-scattering volumes, multi-bounce SSS)
- https://developer.blender.org/docs/release_notes/5.2/cycles/ (SSS changes)
- https://blenderartists.org/t/blur-items-inside-behind-glass/600295
- https://jakehicksphotography.com/latest-techniques/2021/1/8/creating-gradients-with-coloured-gels
- https://www.mattbristow.net/index.php/dark-field-lighting/
- https://glassencyclopedia.com/Laliqueglass.html
- https://www.protolabs.com/resources/design-tips/improving-part-moldability-with-draft/
- https://www.upminc.com/resource/adding-text/
- https://projects.blender.org/blender/blender/issues/94323 (objects inside scatter volumes)
