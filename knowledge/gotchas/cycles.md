# Cycles: lighting, refraction, geometry, output

## Lights and emitters

- Anything bright that a transmission ray can reach is imaged through glass as a hard shape. For each emitter decide: seen in reflections, through the glass, or both. Set `visible_transmission` and `visible_glossy` to match. `caustics-v2`
- Gate the glossy lobe with Light Path: multiply the Fresnel mix by `Transmission Depth == 0`, so lamps do not ghost off the inner surface. `caustics-v2`
- Radiance is power over area. A strip 4× narrower at the same power is 4× brighter. Scale power with size.
- Where a light sits sets what it does. Beside the camera gives face speculars. 15° behind gives rim hairlines. 28° behind images through the side walls. `caustics-v2`
- Distance is an attention tool. Light falls with distance squared, so a light at half the distance gives the near side 4× the far side and the eye goes there. For even product light, move the light high and far and raise its power, rather than switching to a sun (too flat). `preflight.py` prints each light's falloff across the subject. Source: [Blender Guru, Fundamentals of Lighting](https://www.youtube.com/watch?v=ENnEYoUpFfU)
- Light size picks which detail reads. A small light makes scratches, rivets and normal-map detail stand out; a large one hides them and shows the whole form. Choose by asking "form or surface detail?", then confirm against a reference's shadow edge (`process/matching-a-reference.md`). Source: Blender Guru, as above
- A spot cone is a cheap light vignette. Place a point light first, then make it a spot and shrink the cone so the floor in front and behind falls dark; a rim spot can light the lid's reflection without touching the visible floor. Source: Blender Guru, as above
- Bright softboxes and reflect cards give a milky wash. Keep reflectors dim and let gaps stay black. `caustics-v2`
- Satin sheen that does not veil a print: a small glossy-only strip light, hidden from diffuse and transmission, placed where the camera sees its mirror reflection. `printed-plastic`
- A camera-invisible black flag is negative fill. It darkens a face that reflects too much, where a material tint does little. Lift it off the floor, or it casts a dark wedge. `printed-plastic`
- Set DOF focus with an empty at the face centre, not the object origin. `printed-plastic`
- Light linking does not survive a transmission bounce: once a reflected ray passes through a clear plate, the plate becomes the "receiver" and an excluded light leaks back in. To keep a light out of a reflection, set its `visible_glossy`/`visible_transmission` False. `minidisc`
- A shadow-invisible flag (reflection matte) blocks what glossy rays see, but not direct light sampling: the world HDRI still lights the object through it. Turn the world off, or make the flag shadow-visible. `minidisc`
- A small area light's radiance is P/(A·π): 0.5 W at 5 cm lit the table to 10× white. Lights meant only for reflections: `visible_diffuse = False`. `minidisc`
- An object resting exactly on the table (coplanar faces) renders its whole interior black and speckled. Lift it 0.03 mm. `minidisc`
- A white table exposed above 1.0 clips every contact shadow away; reviewers then say "the object floats". Measure the raw table value near the object and set lights so it lands at 1.0–1.05. `minidisc`
- A milky scatter volume picks up every front light, even glossy-only lights with `visible_transmission`, `visible_diffuse` and `visible_volume_scatter` all False. Emissive meshes do it too. Use light linking (`light_linking.receiver_collection`) to keep accent lights off the milky object. Make highlight emitters thin and bright: the highlight follows radiance (power ÷ area), the veil follows total power. `5.x` `opal-essence`
- Shadow linking lets parts behind a frosted plate show form: give them their own lights with `light_linking.blocker_collection` set to the parts only, so the plate casts no shadow for those lights. Keep those lights grazing and glossy-only; at the mirror angle, black flat tops turn to grey card. `5.x` `opal-essence`
- To glint the bevels of raised type under a near-overhead camera, put the rake low (~14°) on the camera side. A rake from the far side never mirrors into the lens. `opal-essence`
- A coat reflects only ~4% at normal incidence (IOR 1.49). An environment card in the coat needs strength ~40–80 to show over a backlit plate, and glossy parts behind the plate reflect it too. `Filter Glossy` 1.0 smears a thin card into a broad band. `opal-essence`
- Flat plates cannot show the wet highlights of cast resin; those come from folds and warps. Coat bump and environment cards give nothing, or a uniform band. `opal-essence`

- An evenly lit cyc behind a figure: give the backdrop a low albedo (about 0.2) plus emission in its own colour, and set its `visible_diffuse = False`. Floor and wall then match within 10 levels, the glow does not lift the figure's shadows, and the contact shadow survives. Key and world light the figure alone. `roman-model`

## Geometry under refraction

Refraction magnifies every flaw in a mesh. `caustics-v2`

- Do not use the Displace modifier's Clouds texture on the original noise basis. Its lattice kinks read as a comb through glass. Put a crown in a shader Bump instead.
- Do not voxel-remesh a beveled prism; voxels terrace the bevels. One angle-limited bevel with `harden_normals = True` was cleanest (a refraction subject; opaque plates with a crisp chamfer are in [modelling](modelling.md)).
- Flat-shade large n-gon caps. Smooth shading across triangulated n-gons bands the normals. `mesh.set_sharp_from_angle()` (4.1+) sets *every* face smooth, so call it first and set `use_smooth = False` on caps after; otherwise each cap interpolates its bevel normals and renders as a dome. A diffuse clay render hides this; a mirror-material render shows it. Cost `minidisc` 3 review rounds ("crumpled foil", "lens windows").
- Fine surface bumps must stay under about 0.2 mm on a 0.4 m object. 1 mm reads as orange peel.
- A rounded SVG corner on a thick tilted slab can look chamfered. Check the source before you "fix" it.

## Output quality

- Supersample fine patterns: render at 2× and downsample with Lanczos. At 1× a 0.3 mm line screen aliases, and the denoiser smears it. `printed-plastic`
- Partial denoise: mix noisy and denoised passes about 50/50, then add grain. Full denoise looks plastic. `printed-plastic`
- f/8 at 30 cm on a 75 mm tilted object blurs the far half into a soft white glow that looks like a lighting bug. Product shots: f/16. `minidisc`
- To darken the shadow-side outer wall of a low relief (a seal bead), lower the key; a flag or less fill does not do it. At 38° the wall still faced the sun. At 24° the row profile matched the reference. A black flag only darkened the paper, and a bounce card lit exactly the wall that must stay dark. `wax-seal-chaos`

## Dark plastic, light rigs and contact shadows

- Dark satin product with parts shadowing each other: use ONE small key (0.25 m at ~0.8 m) off the tops' mirror direction (camera-left here), a dim dome (0.12) as the only ambient and no fill. Two 0.9 m softboxes wrapped light into every gap, so tops, slopes, walls and moat floors read the same and p5 sat at 20–23 for four rounds of geometry fixes; the small key gave p5 12 in one round. Its cost: 1.2 mm fillet crests mirror the small key as hot "chrome ribbons"; roughen the crests (the wear tag marks them). `cyber-deck-v2`
- Dark satin plastic under a big soft key: every flat top mirrors the softbox when the key sits in the camera's mirror direction (far side, near camera elevation). Render once with base colour black; what remains is reflection. Here it was 120–137 sRGB against about 82 wanted, so the tops read as the light, not the plastic, and no albedo change could fix it. Put the device's key on the camera side, above the camera, and give the backdrop its own key. `cyber-model`
- Light linking as a look tool: each light gets one receiver collection: the backdrop (gradient and cast shadow), the device (plate tone, wall brightness), the steel parts only (a big card, since metal has no diffuse and needs something bright to reflect). The backdrop stayed at the same level while the device light was swept 15 to 60 W. An object can sit in two collections. `5.x` `cyber-model`
- Camera-facing walls only lift with light from the camera side, low. The far-side key never reaches them. A fill that also lit the backdrop lifted every backdrop corner by 10–20 levels; linking it to the device fixed that. `cyber-model`
- An emissive screen lights its neighbours (cyan on nearby metal). Set the glass object's `visible_diffuse = False`: the camera and glossy rays still see it. `cyber-model`
- Decals (labels, logo) as flat planes 0.02 mm above the panel with `visible_shadow = False` render clean at 1600 px with no z-fighting. `cyber-model`

## Exteriors: sun, sky, glass, context

- Physical units (agent-tested, 5.2): a Sun lamp of S W/m² gives a white surface S·cosθ/π; the multiple-scattering sky's own disc is about 135 W/m² at 4000 m. Use one sun, indirect clamp 0 (10 crushed the shade side 2.4×) and `cycles.film_exposure` (linear, before the compositor, so no glare veil). `5.x` `aztechno-building`
- A photographer's bright sky: lift the sky for camera rays only (Light Path); for glossy rays it puts a ×4 sky into every paint, mullion and chrome highlight. Reflections of the sky need their own lift, limited by elevation (`aztechno-building` world tree). `aztechno-building`
- Reflection-only HDRI: a world mix on Is Glossy Ray minus Is Camera Ray swaps a photographed street into every reflection. Above ~14° show the lifted sky instead, tip the equirect down ~12° when it was shot at eye height, and check what lands in the glass: a tower block or an onion dome in a reflection is the strongest tell. Modelled low houses in front of the HDRI hide its ground. `aztechno-building`
- Camera-invisible context still blocks sky light for diffuse rays: houses across the street darken the facade's shade side. Size them to the real street. `aztechno-building`
- Curtain glass: tinted float glass (F 0.05, sunlit rooms behind) was the physically better read and lost blind to an opaque coated dielectric (F 0.35, ±60 % per pane, tilt hashed per pane from the mullion grid): what the glass reflects mattered more than its physics. A hashed per-pane shader needs its attributes on every glass object; a missing one divides by zero and the pane renders flat grey. `aztechno-building`
- Shift: `shift_x` positive moves the frame right (content left); `shift_y` is a fraction of the longer side. `aztechno-building`
