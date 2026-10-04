# Shader nodes

## Traps

- `ShaderNodeMix` has typed duplicate sockets, so index them. RGBA: factor `inputs[0]`, A `inputs[6]`, B `inputs[7]`, result `outputs[2]`. FLOAT: A `inputs[2]`, B `inputs[3]`, result `outputs[0]`. `inputs["A"]` returns the float socket.
- ColorRamp `EASE` interpolation plateaus at every stop and bands with many stops. Use `LINEAR`.
- A Python variable reused across loops silently rewires a material. A dust loop named `d` shadowed a refraction loop's `d` and turned the material white. Give each layer's temporaries their own names. `caustics-v2`
- A gradient driven by Texture Coordinate › Object on a scaled plane squeezes into the unscaled unit range: the stops bunch into a narrow rainbow band. Apply the scale first. `opal-essence`
- In a world shader, `Texture Coordinate › Generated` is not a raw ray direction. For direction masks (softbox cards) use `Geometry › Incoming` × −1. Gate with Light Path › Is Glossy Ray to show them only in reflections. `5.x` `opal-essence`

## Techniques

- Keep albedo noise apart from normal noise. White noise into a bump acts as extra roughness and blurs what is behind it. Keep bump noise larger than a pixel.
- Set Principled `Specular IOR Level` to 0 on printed ink under another surface, or its highlight washes the ink to grey. `printed-plastic`
- Ink damage should darken, not lighten. Grain and pinholes that lighten in a straight line make the ink read as flat mid-grey. `printed-plastic`
- Blur an image inside a shader with jittered image taps on rings (24 taps on 3 rings). Put the radius in mm on the group input so one group serves many radii. `printed-plastic`
- Halftone line screens: rotate the UVs, build a triangle wave, threshold against coverage. Gate by coverage so blank paper stays clean. The rotation angle is 90° from the direction the lines run; test at low samples. `printed-plastic`
- Frosted surface: mix a sharp refraction core with a wide refraction-only halo. A reflection on the wide lobe veils the print. `printed-plastic`
- Surface specks: mix in a Transparent BSDF, not white. White reads as dust. Transparent reads as texture in the plastic. `printed-plastic`
- **Diffraction grating (CD) as a BSDF:** one anisotropic Glossy lobe per band (8 bands 400–700 nm, orders ±1, ±2), normal rotated about the groove tangent by ½·asin(mλ/d), band colours from Zucconi's spectral fit normalised to white. Correct under every light, no noise. `experiments/wonder-minidisc/scripts/materials.py`. `minidisc`
- A grating shows colour only if its mirror direction sees dark: in a white room the bands sum to white. The hue at a point is set by the light's angle off the mirror direction (first order λ = d·sin θ; 15° violet … 25° red). Sector width comes from the light's extent *around* the mirror direction, so wide, radially thin arcs give broad saturated sectors. `minidisc`
- Principled roughness also blurs transmission. Put scratches and fingerprints on a separate rough Glossy mixed by mask, never on the plastic's own roughness. (The glass rule below holds for plastic too.) `minidisc`
- Tinted plastic from one colour: k = −ln C, density = max k / depth, absorption colour = 1 − k/max k into Volume Absorption. The depth input is the tint-strength vs see-through trade-off. `minidisc`
- On 4.4 the Glossy BSDF's id is `ShaderNodeBsdfAnisotropic`; try it before `ShaderNodeBsdfGlossy`. `4.4`
- Milky, see-through resin: the lever is transmission roughness (~0.3), not scatter density or front light. Wide-angle transmission lets backlight wrap around parts behind, so they lift and veil like an opal diffuser, while parts touching the back face stay sharp. Denser scatter only darkens the plate. `opal-essence`
- A frosted Principled base also reflects at its roughness and smears every light across the surface. Set `Specular IOR Level` 0 on the base and let a sharp Coat (~0.02) do the reflecting. `5.x` `opal-essence`
- A Rayleigh-weighted scatter volume (Volume Coefficients, R:G:B ≈ 1:2.3:5.7) is true opalescence, but it shifts all transmitted light warm: a teal gradient stop comes out olive and dark parts brown. Keep it weak (Opal Blue ~0.35) when a designer palette matters. `opal-essence`
- Raised type as a separate object in a frosted material is a second diffuser that greys and re-blurs what is under it. Give it clear faces (the same group node with Frost 0). Without a volume it can also overlap the plate; with one it renders dark. `opal-essence`

- Use Map Range, not ColorRamp, for any band a designer should tune. A ColorRamp's stops cannot be group inputs; a Map Range's From Min and From Max can, as position and softness. `tools/nodes.py` `step()` builds it in shader and GN trees. Source: [BCON26, 2D comic style in 3D](https://www.youtube.com/watch?v=AFmyCt3MR4M)
- Toon shading per light (EEVEE only): give each light a pure red, green or blue colour, Shader to RGB, Separate Color, then a `step()` per channel. Each channel is one light's mask, with its own band and colour. Source: [BCON26, 2D comic style in 3D](https://www.youtube.com/watch?v=AFmyCt3MR4M)
- Image textures on a procedural mesh with no UVs: Texture Coordinate › Object into each Image Texture set to Box projection (blend about 0.2). Every map in the set needs both changes, or that map reads wrong. Source: [Blender Guru, Backrooms](https://www.youtube.com/watch?v=kBsVJSETydU)
- A share-of-lights-on dial for emissive panels: Brick Texture (mortar 0) → Math Less Than → Factor of a Mix between black and the emission map. Bias sweeps from all off to all on; Scale sets how many panels switch together. Unlit patches give an interior its shadow and mood; even light reads as a convention centre. Source: [Blender Guru, Backrooms](https://www.youtube.com/watch?v=kBsVJSETydU)

## Imperfections on glass

- Dust must occlude: mix a black Diffuse in by a mask. Emissive or white dust reads as sparkle. `caustics-v2`
- Sparse dust: Voronoi F1 cells picked by White Noise against a density threshold. `caustics-v2`
- Fingerprints and haze change glossy roughness only. Touch the refraction lobes and the image behind blurs. `caustics-v2`
- Scratches: Voronoi distance-to-edge windows under a sparse noise mask, with a tiny bump. Above about 0.15 roughness a Voronoi edge network looks like a mesh. `caustics-v2`
- Haze patches with any gloss reflect lamps as coloured blobs. Keep them small and low. `caustics-v2`
- A camera-space normal gradient gives one flat colour on flat faces. Store a per-shape height (Mesh Island → Field Min & Max, grouped by island → Map Range) as a point attribute and blend it in with an Attribute node. `eclipse-glow`

## Subsurface (opaque pigmented materials)

- Keep the Random Walk scale well under the object's thickness. At 1.2–3 mm on a 1.4 mm wax field, light left through the bottom and the lilac went grey-green. `wax-seal`
- SSS on an almost opaque material (sealing wax, clay) fills shadowed grooves, draws a saturated line in every concave crease, and blurs the bump detail, so the bump ends up set 3× too strong. Render scatter 0 beside the chosen value before tuning anything. For wax, 0.04–0.08 mm. `wax-seal`
- Violet (or any saturated) shadows on a pastel: give the Subsurface Radius a coloured reach, such as (1, 0.5, 1.2). The shadow side takes the colour and the lit face stays pastel. A saturated base colour also saturates the lit face, and a coloured world fill loses to the paper bounce. Above ~0.15 mm the creases glow neon. `wax-seal`

## Grain, scratches and creases (opaque, dark)

- Fine grain must be albedo-only and not too fine. Noise at 3000 per metre vanished after the denoiser; bump on a Perlin noise gave worm-shaped grain that reviewers read as coarse. Two albedo noises (1900 and 5200 per metre, strength about 7) matched the reference's speckle (luma std 15 at 1:1). Denoise with albedo and normal passes. `cyber-model`
- Plates in the reference carried luma std 13–26 of fine grain and ours 1.5 (reviewer's patch estimates), so they read as flat paint. Multiply albedo by a fine noise (±28 %) and a low-frequency mottle (±10 %), and roughness by the mottle. `cyber-model`
- Scratches: a stroke mask drawn with PIL (2048² over 250 mm, short light strokes clustered on the lid and right plate), read top-down in object space (Mapping scale 4, Non-Color, `extension = CLIP`), lifting albedo and roughness. Stretched-noise thresholds looked like brushed scribbles at any setting. `cyber-model`
- Black creases: multiply base colour and specular by AO raised to the third power (reach 5 mm for 6 mm steps). AO on the backdrop albedo (12 mm, power 2.5) gives the dark contact halo the reference has round the object. `cyber-model`
- Lift vertical faces without touching the tops: albedo × (1 + k·(1 − |Normal.z|)) from Geometry › Normal. `cyber-model`
- The shader Bevel node used as an edge-wear mask sees only the creases between bevel segments on geometry that already has a real bevel. Put worn chamfers in a second material slot instead (Bevel modifier `material`), or use the flat chamfer highlight. `cyber-model`
- LCD: draw the display with PIL at 2×, downsample, add a faint 12 px pixel grid at 2.5 % (a 6 px grid would alias when the 1536 px texture is minified 3×; not tested) and a diagonal sheen at 8 % white, then use it as Emission colour under a sharp Coat. Digits sized to the full width clipped at the bezel. `cyber-model`
- Bump: use `Distance` 0.001 with the height in millimetres (physical). A 0–1 height at Distance 0.004 drew black outlines on shadowed brick arrises. Strength stays at 1. `5.2` `apartment-model` (brick agent)
- Built-in Brick Texture reads only X and Y of its vector (a wall in XZ came out all mortar), gives no per-brick ID, and cannot do Flemish or garden-wall bond. For per-brick values use FLOOR/FLOORED_MODULO maths and White Noise on (column, row). `5.2` `apartment-model`
- Wave Texture BANDS period is 2π / (20 · Scale) coordinate units: Scale = 0.3142 / spacing in metres (Scale 10 = 31 mm, not 100). `5.2` `apartment-model` (floor agent)
- Herringbone without textures: in plank-width cells (i, j) of axes rotated 45°, c = (i − j) mod 2n (FLOORED_MODULO); c < n is a plank along p with origin cell (i − c, j), else along q with origin (i, j − (2n − c) + 1). Verified to tile for n = 4, 5, 6; the staircase (spine) runs along p + q. `apartment-model` `scripts/mat_kit.py`
- No UVs on generated walls and floors: Object coordinates work for colour and bump, but tangent-space normal maps need UVs. Use the scan's height or roughness map through Bump instead. `apartment-model`

## Fabric at room distance

- Size texture features to the pixel footprint, not the thread: at 3–4 m with a 14 mm phone lens a pixel is ~4 mm, so a 1 mm weave and 1.5 mm slubs average to flat paint ("painted MDF"). What reads is ~5 mm × 1.5–3 cm slub streaks along the weft and a per-3 mm tone fleck; 3 cm streaks at high contrast read as "brushed felt". `apartment-model`
- A material from the real thing: a flat, evenly lit patch of the maker's close-up, high-passed (divide by a 30 px blur), made seamless (half offset, sine-window blend), tile size from its FFT weave period; colour stays a measured input. Keep such a texture with the experiment (not CC0). `apartment-model`
- Principled Sheen on a light fabric moves nothing measurable: 0.5 → 1.0, roughness 0.3–0.7 changed fabric/paint ratios by ≤ 0.03. `5.x` `apartment-model`
- The Attribute node's float output is `Fac` (not `Fact`). `5.x`
