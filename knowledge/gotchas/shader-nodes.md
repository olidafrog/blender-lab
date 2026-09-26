# Shader nodes

## Traps

- `ShaderNodeMix` has typed duplicate sockets, so index them. RGBA: factor `inputs[0]`, A `inputs[6]`, B `inputs[7]`, result `outputs[2]`. FLOAT: A `inputs[2]`, B `inputs[3]`, result `outputs[0]`. `inputs["A"]` returns the float socket.
- ColorRamp `EASE` interpolation plateaus at every stop and bands with many stops. Use `LINEAR`.
- A Python variable reused across loops silently rewires a material. A dust loop named `d` shadowed a refraction loop's `d` and turned the material white. Give each layer's temporaries their own names. `caustics-v2`

## Techniques

- Keep albedo noise apart from normal noise. White noise into a bump acts as extra roughness and blurs what is behind it. Keep bump noise larger than a pixel.
- Set Principled `Specular IOR Level` to 0 on printed ink under another surface, or its highlight washes the ink to grey. `printed-plastic`
- Ink damage should darken, not lighten. Grain and pinholes that lighten in a straight line make the ink read as flat mid-grey. `printed-plastic`
- Blur an image inside a shader with jittered image taps on rings (24 taps on 3 rings). Put the radius in mm on the group input so one group serves many radii. `printed-plastic`
- Halftone line screens: rotate the UVs, build a triangle wave, threshold against coverage. Gate by coverage so blank paper stays clean. The rotation angle is 90° from the direction the lines run; test at low samples. `printed-plastic`
- Frosted surface: mix a sharp refraction core with a wide refraction-only halo. A reflection on the wide lobe veils the print. `printed-plastic`
- Surface specks: mix in a Transparent BSDF, not white. White reads as dust. Transparent reads as texture in the plastic. `printed-plastic`

## Imperfections on glass

- Dust must occlude: mix a black Diffuse in by a mask. Emissive or white dust reads as sparkle. `caustics-v2`
- Sparse dust: Voronoi F1 cells picked by White Noise against a density threshold. `caustics-v2`
- Fingerprints and haze change glossy roughness only. Touch the refraction lobes and the image behind blurs. `caustics-v2`
- Scratches: Voronoi distance-to-edge windows under a sparse noise mask, with a tiny bump. Above about 0.15 roughness a Voronoi edge network looks like a mesh. `caustics-v2`
- Haze patches with any gloss reflect lamps as coloured blobs. Keep them small and low. `caustics-v2`
