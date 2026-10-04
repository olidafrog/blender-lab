# Debugging a render

- Add debug switches to `build.py`: hide an object, mute named lights. Drive them with `--set`.
- Isolate one emitter at a time and compare crops. Most "floating objects" in glass are one emitter seen from an unexpected direction.
- Crop the problem area at 1:1 before you judge it. For a fast crop render, use `use_border` with `use_crop_to_border`.
- To find which part of an emitter a pixel images, paint the emitter with its own coordinates and read the pixels back. Linearise the sRGB values first.
- Render one intermediate value: open the `.blend`, relink a node output into Emission → Material Output. In 4.4, set `scene.use_nodes = False` to skip the compositor.
- A short metrics script (mean gradient on lit pixels, pixels over two gradient thresholds, clipped %, lit fraction) predicted the direction of the reviewer's score before a review was spent in `caustics-v2`. `tools/metrics.py` generalises it, and adds a per-region diff between two renders.
- To port a script across versions, open its saved `.blend` in the new Blender and dump the node tree. Blender's own conversion shows the new settings. Rendering that file gives a same-machine target to diff against. `eclipse-glow`
- Mac (Metal) and Windows (OptiX) renders of the same scene differ by about 0.6/255 mean and up to 10/255 at 32 samples, no denoise. Treat a cross-machine diff at that level as matched; do not tune values to it. `eclipse-glow`
- Find a veil or wash with one-light-at-a-time renders at 25% scale and 64 samples (~3 s each). Two runs found what several rounds of tuning had not. Also toggle one material input (milk 0, frost 0) to see which path carries it. `opal-essence`
- Edit `build.py` with `str.replace` plus `assert count == 1`, or `sed` over a line range. A slice splice whose end marker also matched earlier in the file duplicated half the script. Snapshot `build.py` with each reviewed version so you can diff it. `opal-essence`
- Profile the geometry before tuning the look: `tools/mesh_profile.py` prints top-surface height along a line from a build.py in seconds. In `wax-seal-chaos` it found a field 0.46 mm below the die and a 0.2 mm dip ring, after two renders had been misread.

- Check every measuring region on both images. A photo-2 box half on a 0.48 m stand-in block in the render (the real table is a thin top on legs) drove three rounds of "missed levels" (`apartment-model`, advisor).
- After a scripted edit (`sed -i`, string replace), grep the key and check its value before rendering: two silent misses (comment spacing) rendered a version with the wrong back-block shape (`apartment-model` v22).
- Placing an object from photo corners: draw the projected model box on the photo first, then pick points; corner pixels read from gridded crops were wrong twice (a slanted edge read as a corner).
