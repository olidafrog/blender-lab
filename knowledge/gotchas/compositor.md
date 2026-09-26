# Compositor

See [API changes](api-changes.md) for how the compositor differs between 4.4 and 5.x.

- Blur `size` is a hard radius, not a softness. The kernel is zero past it, so a 70 px blur never reaches 88 px away. Size it for the full reach you need.
- Glare / Fog Glow keeps its source sharp. With a bright source the core clips into a visible shape.
- Lens Distortion `Dispersion` splits thin bright lines into grey and blue fringes. Keep it at or under 0.005 unless you want that.
- The Transform node scales about the image centre, not the object. That is fine only while the subject is centred.
- `film_transparent = True` with `image_settings.color_mode = "RGB"` gives an object-coverage alpha in the compositor and still writes an opaque PNG.
- Add shader AOVs to `view_layer.aovs` before you build the compositor, or the Render Layers node has no socket for them.
- A new view-layer AOV defaults to type COLOR. A shader AOV node that feeds only its `Value` input then writes black. Set `aov.type = "VALUE"` for masks. `threshold-orbit`
- Blur then threshold a line mask to make lines bleed together where they cross, like Photoshop Threshold on a blurred drawing. Send labels to a separate AOV that skips the bleed. `threshold-orbit`
- The 5.x File Output node writes only `OPEN_EXR_MULTILAYER` (`"OPEN_EXR"` raises). An Image node loading that file still has an `Image` output. `5.x`
- A headless run cannot save which workspace tab a `.blend` opens on. Setting `window.workspace` and `workspace_cycle` both do nothing without the UI event loop. Tell the user to click the Compositing tab. `5.x`
- For live compositor tweaking without re-rendering: write the raw beauty pass to EXR during the render, load it into an Image node, and view the result through a Viewer node with the backdrop on. `tools/comp.py` does this. Re-compositing that EXR was pixel-identical to the original render. `5.x`
- 4.4 settings cannot go on a node group. Keep post effects as labelled top-level nodes inside a frame. `4.4`
