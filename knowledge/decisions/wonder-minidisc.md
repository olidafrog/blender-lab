# MiniDisc: decisions

Experiment: `wonder-minidisc`. The Wonder logomark as a CD/MiniDisc data surface, inside a moulded translucent case whose outline is a rounded offset of the logo. Final score 6.8–6.9/10 after 11 versions (v11 shipped); the loop stopped on a trade-off, not a plateau of small notes. Built on Windows, Blender 4.4.

## What makes the look

- **CD colour is diffraction, and it only shows against dark.** A grating reflecting a white studio adds all its bands back to white. The disc must see a dark card in its mirror direction, with small bright sources beside it.
- **Hue is set by where the light sits, not by the shader.** First order: λ = d·sin θ, θ = the light's angle off the mirror direction (d = 1.6 µm: 15° violet … 25° red). Each light makes one radial colour sector through the hub; its width comes from the light's extent *around* the mirror direction, so arcs can be wide without losing saturation as long as they are thin radially.

## Decisions

**Diffraction as a real BSDF: one anisotropic Glossy lobe per band, normal tilted about the groove tangent by ½·asin(mλ/d).**
8 bands 400–700 nm, orders ±1 and ±2 (order 2 weighted ~0.15), Zucconi band colours normalised to white. Every light diffracts correctly and there is no noise for the denoiser to smear.
Rejected: HDRI-sampling emission (ignores lights and shadowing), Stam single-light colour (one light only), white-noise wavelength picking (denoiser smear), thin film (no sectors), OSL (no gain), groove bump textures (moiré).

**A studio built around the disc's mirror direction.**
- 3 m black flag on the mirror direction, visible to glossy/transmission rays only.
- 8 "wedge" arc lights round it, glossy-only, each at its own angle for a different hue.
- Big lights (key over the camera, far-table fill, strip) are invisible to glossy and transmission rays. Light linking alone leaked: once a reflected ray passes the case plate, the plate is the "receiver".
- HDRI off: a shadow-invisible flag cannot stop the disc's direct sampling of the world.
- Sweep back wall pushed behind the flag.

**Case colour from Beer–Lambert absorption, one Colour input at a reference depth.**
k = −ln C, density = max k / depth, absorption colour = 1 − k/max k. The depth is the designer's trade-off: small = strongly tinted plates (ref2), large = full spectrum through the plates (ref4). A tinted case filters the spectrum; teal removes pinks. Handed to the designer rather than resolved.

**Case geometry from a numpy SDF of the SVG, marching squares, exact booleans.**
Outer = offset 11 units + 7 closing (rounds the notches). Top and bottom shell plates, perimeter wall, split ring ribs round each well (top and bottom shell, parting gap between), full-height screw posts. Full-height well walls read as "a slab with holes".

**Shadow rays pass the case as Transparent (Shadow Light), still tinted by the volume.** Gives a coloured, bright shadow without caustics. Lower values darken the hollow webs until they read solid.

## Library

Both materials are in the library: `library/materials/cd_diffraction.blend` and `tinted_plastic.blend` (builders in `build_materials.py`). The experiment imports them from there.

## Known limits

- The hub reads as a dark teal puck under a teal case (steel reflecting the black flag, seen through two tinted passes).
- The webs between strokes are plain tinted plastic over a white table; reviewers kept reading them as a solid slab. A real case would show internal detail (text, ejector marks, a shutter) through them.
- No metal shutter, label or moulded text yet.
- A teal hero cannot show ref4's pinks; the clear and violet colourways do.
