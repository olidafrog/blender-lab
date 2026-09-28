---
name: finish-experiment
description: Use when a Blender experiment is done or the user is happy with a version, when producing the final render and .blend, or when the user says "finish", "wrap up", "ship it", "final", or "hand it over".
---

# Finish an experiment

Every experiment ends with two deliverables: the final image, and an editable `.blend` a designer can play with without reading nodes. Pattern from `wonder-popart`: each complex material collapses to one group node whose inputs are the key controls.

## Deliverables

- `output/FINAL_<name>.png` — full resolution and full samples.
- `output/<name>.blend` — rebuilt from `build.py`, opens and renders on its own.

## Steps

1. **Controls.** Every material the designer might touch is built with `tools/nodes.py`: `group(...)` for the internals, `material_from_group(...)` so the material holds one node. On each group:
   - 3–8 inputs, the ones that change the look. Hide plumbing inside.
   - Plain names in designer terms ("Gloss", "Dot Size", "Glow Reach"), not node terms ("Roughness Mix Fac").
   - Real `min`/`max` ranges that stay good-looking across the range, and a unit in a comment.
   - Defaults equal the final `P` values.
   - One control, one place: if a value feeds several nodes (a blur radius used three times), expose it once and wire it to all of them. No custom properties or drivers the designer has to hunt for.
   - Nest sub-groups (pattern, UV, light direction) inside the top group rather than exposing them.
   Lights and cameras the designer might move get clear names ("Key", "Rim", "Camera").
   Compositor: build it with `tools/comp.py`. All post effects go inside one `post_group` node with the key inputs exposed; Tab into it shows the parts. `use_saved_render(...)` before saving, so the Compositing tab shows the final raw EXR and every Post slider updates the backdrop at once. On 4.4 (no compositor group sockets), use one labelled frame plus a Viewer node.
2. **HOW_TO_TWEAK.** `how_to_tweak(...)` text block: which object holds which control node, what each input does, and what to rebuild from.
3. **Final render.** `build.py --out FINAL_<name> --scale 1 --samples <final> --save`, then copy the render to `output/FINAL_<name>.png`. Long renders run in the background. Keep every file in `output/` under 100 MB, since GitHub rejects bigger files; re-encode a final video (higher CRF, or H.265) until it fits.
4. **Raw EXR.** `--save` copies the final `renders/<out>_raw.exr` into `output/` and points the Saved Render node at it. It is the compositor preview source; keep it with the `.blend`.
5. **Portable file.** `build.py --save` makes paths relative and deletes `.blend1`. Pack any images the `.blend` needs (`bpy.ops.file.pack_all()`) unless they live in `library/`.
6. **Verify.** Open the saved `.blend` in a fresh headless Blender (`BLEND=... tools/blender.sh <check.py>`). Check each material is one group node, the inputs have ranges, `HOW_TO_TWEAK` exists, the Saved Render node points at an existing EXR, and a 1-sample render with the source switch On matches the final PNG.
7. **Record.** Add a decision record to `knowledge/decisions/<name>.md` (chosen mechanism, rejected ones, final score, and the calibration pair from `PROGRESS.md`). Then run `/capture-learnings`, including its cost line and retro, so the next experiment runs better.
8. **Report** to the user: the two file paths and the list of controls, one line each.
