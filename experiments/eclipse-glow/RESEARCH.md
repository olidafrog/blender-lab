# eclipse-glow — research

## v2 halo (2026-09-26, after two review rounds on the same complaint)

### Read of the reference
The glow is not an outline. It is the body's own light bleeding outward: widest and hottest under the bright pink-orange base, thin at the sides, absent at the dark top (only the crescent lights the top). Glow reach follows the brightness of the edge it comes from.

### Most likely process
A 2D "self-glow": the image duplicated, heavily blurred, and screened/added back, keyed so dark areas add nothing (Photoshop: blurred duplicate + Blend If). Plus grain on top.

### Techniques to use
- Halo = blur(beauty × luminance key × warm tint), near + far, added outside the object with a soft mask. Brightness then decides where it glows. `5.x` compositor, no new nodes.
- Rejected: coverage-mask halo (v05–v07). It glows evenly on every edge and fills the gaps between bars; height weighting spread back up through the blur.

### Numeric targets
- Glow above a shape's top: at most 25% of the glow below its base.
- Gaps between the bars: at most 35% of the v07 value.

### Sources
- https://abduzeedo.com/node/429 (eclipse effect: outer glow + grain)
- https://phlearn.com/tutorial/glow-effect-photoshop/ (blurred duplicate, Blend If to keep glow out of shadows)

## Rise video (v2 animation): moonrise and mirage

**Read of the reference** (real moonrises; no image supplied): the body rises out of a dark horizon, slowly. Near the horizon it is (1) dimmer and redder (extinction, Rayleigh), (2) flattened vertically (differential refraction, stronger at the bottom limb), (3) cut into shimmering horizontal layers, (4) mirrored upside-down just below the horizon (inferior mirage), and that mirror is squashed and breaks up. All four fade with height above the horizon.

**Most likely process:** 2D. A clean render of the rising object; the atmosphere is a screen-space effect keyed to distance from the horizon line.

**Techniques to use** (Blender 5.2 compositor, all inside Post, before bloom):
- Occlusion: mask every pass below the horizon before the glows, so hidden parts do not glow.
- Shimmer: Displace driven by Noise Texture stretched along x (horizontal layers), W animated by Scene Time; strength × exp(−height / falloff). [ModDB heat distortion](https://www.moddb.com/groups/blender-artist/tutorials/how-to-create-heat-distortion)
- Mirage: Displace by 2·(horizon − y) samples the mirror image; faded by depth below the horizon; same shimmer, stronger.
- Flattening: extra vertical displacement near the horizon.
- Extinction: multiply by a warm dim tint that fades to white with height.

**Rejected:** a 3D mirror plane (camera-space normals would shade the reflection from below, and it is not a real reflection); a 3D ground plane (horizon then lives in two places, the plane and the compositor).

**Sources:** [EarthSky: odd moons near the horizon](https://earthsky.org/astronomy-essentials/refraction-distortion-moon-sun-near-horizon/), [Sky & Telescope: bending of light](https://skyandtelescope.org/astronomy-news/find-a-horizon-and-savor-the-bending-of-light/), [Wikipedia: atmospheric refraction](https://en.wikipedia.org/wiki/Atmospheric_refraction).

## Sunrise video (v3, 2026-09-27): contact highlight, mirage gap, heat haze

User notes on the rise (v07): the contact point should be the brightest thing in the frame, a blown-out, grainy, blooming highlight, because the "water" doubles the light source. There should be a gap between the shape and its reflection as it arrives, and a stronger heat haze near the ground that blurs, not only displaces. It is a sunrise/sunset, not a mirage in the desert sense.

**Read of the physics** (no reference image; real sunsets over the sea):
1. **The inferior mirage is refraction, not a reflection.** A hot layer over the water bends low rays upward. The observer sees an erect image and, below it, an inverted one. They join at the *vanishing line*, which sits a little *above* the sea horizon. Nothing of the object below the vanishing line is visible; the strip between it and the sea horizon shows miraged sky, so it is bright.
2. **The gap, then the stem (Etruscan vase → omega).** While the sun is above the vanishing line, its inverted image sits below the line with sky between them. As the two limbs reach the line they join in a "stem". At the line the vertical magnification tends to infinity, so the stem is stretched tall, and it is the reddest part. For a rise the order reverses: omega → vase → the stem snaps → gap opens → the inverted image shrinks and fades.
3. **The meeting point is the hottest spot.** Water near grazing incidence is almost a mirror (Fresnel), so the light is doubled there; the stretched stem piles the limb's light into a small area. Photographs of it are blown out, blooming, and grainy (high ISO at dusk, heavy telephoto).
4. **Heat haze = displacement + blur + contrast loss.** Turbulence moves the image (shimmer), smears it (blur, loss of fine detail), and flickers intensity (scintillation). All grow toward the ground, where the air path is longest and hottest.
5. **Sun glitter.** Below the sea horizon, the glint path under a low sun is a column of short horizontal flecks that come and go.

**Most likely process:** 2D, as in v07. A clean render; everything else is compositor work keyed to the height above the vanishing line.

**Techniques to use** (Blender 5.2 compositor, inside Post, `stage`, before the Fog Glow bloom):
- Occlude at the vanishing line (the Horizon control). A bright *mirage band* (miraged sky) of a set depth sits below it, then the dark sea.
- Mirror about the vanishing line, squashed, fading by the height of the reflected point but with a longer reach than v07, so a visible gap opens as the logo lifts off and the inverted image shrinks.
- Stem: sample closer to the line near it (d' = d·(1 − s·e^(−|d|/h))), a local vertical stretch on both sides.
- Haze: blur the displaced image and mix the blur in by e^(−height/h); widen the shimmer band. Blur size from Math only (5.2 gotcha).
- Contact highlight: key = e^(−|d|/w) × image luminance. Add the keyed image × gain (warm white), then a near + far blur of it (local bloom). Values above 1 then feed the existing Fog Glow.
- Grain: animated white noise (pixel, frame) overlaid by the contact key, so the hot spot is grainier than the rest.
- Glitter: animated noise stretched along x, thresholded into flecks, in a column under the logo, below the sea horizon. Test last; drop it if it reads as a pattern.

**Rejected:** a 3D water plane with Glossy (a mirror, not a mirage: no gap, no stem, no vanishing line, and camera-space normals shade it wrongly); a mirror about the sea horizon (v07: the reflection touches the object and can never show a gap).

**Numeric targets:**
- At contact (first ~2 s after the base reaches the line): the contact zone has the highest luminance in the frame, with a clipped core 20–60 px wide at 1080p.
- Mirage band (vanishing line → sea horizon): 12–24 px at 1080p, brighter than the sky above it.
- Gap: visible (≥ 8 px of band between the base and the inverted image) once the base is 0.02 frame heights up; the inverted image is gone by about 0.1 frame heights.
- Haze: a displaced + blurred zone reaching 80–150 px above the line, strongest at the line.

**Open questions:** does the added bloom wash out the logo's eclipse look once risen (it must fade with height)? Does the glitter read as water or as noise?

**Sources:** [Atmospheric Optics: Etruscan vase sunsets](https://atoptics.co.uk/atoptics/sunmir2.htm), [Atmospheric Optics: vanishing lines](https://atoptics.co.uk/blog/selsea-mirage-vanishing-lines/), [A. Young: inferior-mirage sunset simulation](https://aty.sdsu.edu/explain/simulations/inf-mir/inf-mirSS4.html), [Wikipedia: mirage of astronomical objects](https://en.wikipedia.org/wiki/Mirage_of_astronomical_objects), [NOAA: glittering light on water](https://psl.noaa.gov/outreach/education/science/glitter/index.html), [Wikipedia: sun glitter](https://en.wikipedia.org/wiki/Sun_glitter).
