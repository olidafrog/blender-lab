# Debugging a render

- Add debug switches to `build.py`: hide an object, mute named lights. Drive them with `--set`.
- Isolate one emitter at a time and compare crops. Most "floating objects" in glass are one emitter seen from an unexpected direction.
- Crop the problem area at 1:1 before you judge it. For a fast crop render, use `use_border` with `use_crop_to_border`.
- To find which part of an emitter a pixel images, paint the emitter with its own coordinates and read the pixels back. Linearise the sRGB values first.
- Render one intermediate value: open the `.blend`, relink a node output into Emission → Material Output. In 4.4, set `scene.use_nodes = False` to skip the compositor.
- A short metrics script (mean gradient on lit pixels, pixels over two gradient thresholds, clipped %, lit fraction) predicted the direction of the reviewer's score before a review was spent. See `experiments/wonder-caustics-v2/scripts/metrics.py`.
