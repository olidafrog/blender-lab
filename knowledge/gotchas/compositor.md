# Compositor

See [API changes](api-changes.md) for how the compositor differs between 4.4 and 5.x.

- Blur `size` is a hard radius, not a softness. The kernel is zero past it, so a 70 px blur never reaches 88 px away. Size it for the full reach you need.
- Glare / Fog Glow keeps its source sharp. With a bright source the core clips into a visible shape.
- Lens Distortion `Dispersion` splits thin bright lines into grey and blue fringes. Keep it at or under 0.005 unless you want that.
- The Transform node scales about the image centre, not the object. That is fine only while the subject is centred.
- `film_transparent = True` with `image_settings.color_mode = "RGB"` gives an object-coverage alpha in the compositor and still writes an opaque PNG.
- Add shader AOVs to `view_layer.aovs` before you build the compositor, or the Render Layers node has no socket for them.
- 4.4 settings cannot go on a node group. Keep post effects as labelled top-level nodes inside a frame. `4.4`
