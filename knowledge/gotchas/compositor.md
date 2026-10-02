# Compositor

See [API changes](api-changes.md) for how the compositor differs between 4.4 and 5.x.

- Blur `size` is a hard radius, not a softness. The kernel is zero past it, so a 70 px blur never reaches 88 px away. Size it for the full reach you need.
- Glare / Fog Glow keeps its source sharp. With a bright source the core clips into a visible shape.
- Lens Distortion `Dispersion` splits thin bright lines into grey and blue fringes. Keep it at or under 0.005 unless you want that.
- The Transform node scales about the image centre, not the object. That is fine only while the subject is centred.
- `film_transparent = True` with `image_settings.color_mode = "RGB"` gives an object-coverage alpha in the compositor and still writes an opaque PNG. But the GUI shows a checkerboard and the world colour never shows. For a visible world background, turn it off and write coverage to a VALUE AOV (an AOV Output node with Value 1 in the material). `eclipse-glow`
- Add shader AOVs to `view_layer.aovs` before you build the compositor, or the Render Layers node has no socket for them.
- A new view-layer AOV defaults to type COLOR. A shader AOV node that feeds only its `Value` input then writes black. Set `aov.type = "VALUE"` for masks. `threshold-orbit`
- Blur then threshold a line mask to make lines bleed together where they cross, like Photoshop Threshold on a blurred drawing. Send labels to a separate AOV that skips the bleed. `threshold-orbit`
- The 5.x File Output node writes only `OPEN_EXR_MULTILAYER` (`"OPEN_EXR"` raises). An Image node loading that file still has an `Image` output. `5.x`
- A headless run cannot save which workspace tab a `.blend` opens on. Setting `window.workspace` and `workspace_cycle` both do nothing without the UI event loop. Tell the user to click the Compositing tab. `5.x`
- For live compositor tweaking without re-rendering: write the raw beauty pass to EXR during the render, load it into an Image node, and view the result through a Viewer node with the backdrop on. `tools/comp.py` does this. Re-compositing that EXR was pixel-identical to the original render. `5.x`
- 4.4 settings cannot go on a node group. Keep post effects as labelled top-level nodes inside a frame. `4.4`
- 5.2: Blur ignores a linked `Size` unless it comes from a Math node. Linked from Relative To Pixel, or through Combine XYZ, it silently blurs 0 px. A Transform offset from Relative To Pixel failed the same way. Scale pixel sizes by the render height in Python, and multiply controls in with Math. `5.x` `eclipse-glow`
- For a glow that follows brightness, blur the image itself, keyed by luminance and tinted (a "self-glow"). A halo built from the coverage mask glows evenly on every edge and fills the gaps between shapes. `eclipse-glow`
- 5.2 Displace samples the input at (pixel − Displacement), in pixels. To sample higher up (a mirror below a line), the Y offset is negative. `5.x` `eclipse-glow`
- Animated compositor effects need no keyframes: Scene Time (Seconds) → Noise Texture W (4D) → Combine XYZ → Displace. Image Coordinates › Normalized y runs bottom → top. Noise Fac sits mostly in 0.35–0.65; stretch it (× 6 around 0.5) or the wobble is a third of what you set. `5.x` `eclipse-glow`
- Heat shimmer: one smooth noise octave with layers about 20 px tall. Fine octaves (layers under 8 px) read as video tearing. `eclipse-glow`
- Additive grain (±g) disappears on bright subjects. Multiplying by 1 + 2·g·(noise − 0.5) reads as film grain at every brightness; g = 0.06 is light grain. `5.x` `clouds`
- Grain from White Noise on pixel coordinates is frozen on every video frame and reads as dirt on the lens. Use 3D noise with z = Scene Time › Frame. `5.x` `eclipse-glow`
- 5.2 Blur takes an anisotropic size as an unlinked vector (`inputs["Size"].default_value = (900, 12)`): a streak along a horizon, or a sideways blur. Only a linked vector fails (see above). `5.x` `eclipse-glow`
- A hot core per bright shape, not the whole shape: blur the luminance key sideways and threshold near its peak. The blur peaks in the middle of each bright run, so the result is an oval core. `eclipse-glow`
- A displacement that magnifies near a mask edge (a stretch that samples closer to a line) magnifies the edge's 1 px anti-aliased seam into a stripe. Clamp the sample to ≥ 2 px from the edge. `eclipse-glow`
- To fade a reflection as the object lifts, with no keyframes: multiply it by the object's coverage within N px above the line, blurred down over the reflection. Each column fades on its own. `eclipse-glow`
- Glare on many small lights: Streaks at about 0.02 and Bloom at about 0.1. Stronger, distant lights merge into one blur. Source: [Blender Guru, Backrooms](https://www.youtube.com/watch?v=kBsVJSETydU)
