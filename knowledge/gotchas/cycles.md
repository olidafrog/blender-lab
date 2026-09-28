# Cycles: lighting, refraction, geometry, output

## Lights and emitters

- Anything bright that a transmission ray can reach is imaged through glass as a hard shape. For each emitter decide: seen in reflections, through the glass, or both. Set `visible_transmission` and `visible_glossy` to match. `caustics-v2`
- Gate the glossy lobe with Light Path: multiply the Fresnel mix by `Transmission Depth == 0`, so lamps do not ghost off the inner surface. `caustics-v2`
- Radiance is power over area. A strip 4× narrower at the same power is 4× brighter. Scale power with size.
- Where a light sits sets what it does. Beside the camera gives face speculars. 15° behind gives rim hairlines. 28° behind images through the side walls. `caustics-v2`
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

## Geometry under refraction

Refraction magnifies every flaw in a mesh. `caustics-v2`

- Do not use the Displace modifier's Clouds texture on the original noise basis. Its lattice kinks read as a comb through glass. Put a crown in a shader Bump instead.
- Do not voxel-remesh a beveled prism; voxels terrace the bevels. One angle-limited bevel with `harden_normals = True` was cleanest.
- Flat-shade large n-gon caps. Smooth shading across triangulated n-gons bands the normals. `mesh.set_sharp_from_angle()` (4.1+) sets *every* face smooth, so call it first and set `use_smooth = False` on caps after; otherwise each cap interpolates its bevel normals and renders as a dome. A diffuse clay render hides this; a mirror-material render shows it. Cost `minidisc` 3 review rounds ("crumpled foil", "lens windows").
- Fine surface bumps must stay under about 0.2 mm on a 0.4 m object. 1 mm reads as orange peel.
- A rounded SVG corner on a thick tilted slab can look chamfered. Check the source before you "fix" it.

## Output quality

- Supersample fine patterns: render at 2× and downsample with Lanczos. At 1× a 0.3 mm line screen aliases, and the denoiser smears it. `printed-plastic`
- Partial denoise: mix noisy and denoised passes about 50/50, then add grain. Full denoise looks plastic. `printed-plastic`
- f/8 at 30 cm on a 75 mm tilted object blurs the far half into a soft white glow that looks like a lighting bug. Product shots: f/16. `minidisc`
