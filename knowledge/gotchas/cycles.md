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

## Geometry under refraction

Refraction magnifies every flaw in a mesh. `caustics-v2`

- Do not use the Displace modifier's Clouds texture on the original noise basis. Its lattice kinks read as a comb through glass. Put a crown in a shader Bump instead.
- Do not voxel-remesh a beveled prism; voxels terrace the bevels. One angle-limited bevel with `harden_normals = True` was cleanest.
- Flat-shade large n-gon caps. Smooth shading across triangulated n-gons bands the normals.
- Fine surface bumps must stay under about 0.2 mm on a 0.4 m object. 1 mm reads as orange peel.
- A rounded SVG corner on a thick tilted slab can look chamfered. Check the source before you "fix" it.

## Output quality

- Supersample fine patterns: render at 2× and downsample with Lanczos. At 1× a 0.3 mm line screen aliases, and the denoiser smears it. `printed-plastic`
- Partial denoise: mix noisy and denoised passes about 50/50, then add grain. Full denoise looks plastic. `printed-plastic`
