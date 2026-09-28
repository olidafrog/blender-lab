# Blender 4.4 versus 5.x

## Compositor

- In 5.x the compositor is a node group. Create a `CompositorNodeTree`, assign it to `scene.compositing_node_group`, and add a `NodeGroupOutput` with an `Image` socket. `scene.node_tree` does not exist, so 4.4 scripts fail with `'Scene' object has no attribute 'node_tree'`. `eclipse-glow/scripts/eclipse_glow.py` shows one script that builds either (`LEGACY_COMP`). `5.x`
- In 5.x many compositor nodes are gone (Composite, MixRGB, compositor Math). Use shader nodes in their place: `ShaderNodeMix` (RGBA) for mix and add, `ShaderNodeMath` for maths, `ShaderNodeTexWhiteNoise` with `CompositorNodeImageCoordinates` for grain. `5.x`
- In 5.x compositor node settings are input sockets, for example `Blur.inputs["Size"]`. Wrap enum-socket writes in `try`, because names change between versions. In 4.4 they are node properties, so you cannot expose them on a group. `5.x`
- `ShaderNodeMix` defaults to `clamp_factor = True`; 4.4 MixRGB never clamped. Set it `False` when a factor goes above 1, or amounts silently cap at 1. `5.x` `eclipse-glow`
- Translate and Transform default to Bilinear in 5.x and Nearest in 4.4. Set `inputs["Interpolation"]` to `"Nearest"` to match a 4.4 render. `5.x` `eclipse-glow`
- In 4.4, setting Glare `threshold` from Python did nothing; the node rendered at 1.0. `mix` and `size` did apply. When porting, copy the saved `.blend`, not the script. `4.4` `eclipse-glow`
- Blur settings are sockets in 5.x: `inputs["Size"]` is a 2D pixel vector, and `inputs["Type"]` is a menu (`"Gaussian"`, …). No compositor ColorRamp or MapRange either; use the `ShaderNode*` versions. `5.x` `threshold-orbit`
- Lens Distortion, Ellipse Mask, Color Balance, RGB Curves and Hue/Saturation still exist in 5.2. Glare `Size` is a 0–1 factor. `5.x`

## Shaders and objects

- The Refraction BSDF does not accept `MULTI_GGX`. Use `GGX`. `5.x`
- Area lights have `visible_transmission`, `visible_glossy`, `use_temperature` with `temperature` in Kelvin, `spread` and `diffuse_factor`. `5.x`
- Caustics flags live under `.cycles`: `light.cycles.is_caustics_light`, `ob.cycles.is_caustics_caster`, `ob.cycles.is_caustics_receiver`. `5.x`
- 4.4 compositor: `scene.use_nodes`, `scene.node_tree`, a Composite node, File Output with `base_path`, `format.file_format = "OPEN_EXR"`, `file_slots[0].path`; it appends the frame number (`x0001.exr`). Switch uses `.check`. `tools/comp.py` handles both (`comp.LEGACY`). `4.4`
- `Collection.collection_objects` has no name lookup; index it to set `light_linking.link_state`. `4.4`
- For a noisy pass, set `view_layer.cycles.denoising_store_passes = True`. Render Layers then has a `Noisy Image` output. `5.x`
- Geometry-nodes modifier inputs in 5.2: `mod.properties.inputs.Socket_N.value`. `mod["Socket_N"] = v` raises "id properties not supported for this type". `5.x` `eclipse-glow`
- `bpy.data.materials.new()` gives a node tree with `use_nodes` False, so the nodes are ignored and a volume renders nothing. Set `use_nodes = True`; it is deprecated but still needed in 5.2. `5.x` `clouds`
