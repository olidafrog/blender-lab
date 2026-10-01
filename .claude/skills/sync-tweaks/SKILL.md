---
name: sync-tweaks
description: Use when the designer has changed values by hand in a saved blender-lab .blend (a control node, a light, the camera, the Post node) and those values should survive the next rebuild, or when the user says "sync my tweaks", "keep what I changed in Blender", "pull the values back into the script", or "/sync-tweaks".
---

# Sync tweaks back into build.py

A `.blend` is rebuilt from `build.py`, so values changed in the GUI are lost on the next build unless they go back into `P`.

1. Run `python3 tools/sync_tweaks.py <experiment>` (add `--blend <file>` if the edited file is not `output/<experiment>.blend`). It dumps the edited file and a fresh build, and lists each value that differs, with the matching `P` key.
2. Read the list with the user if anything is ambiguous ("P keys with the old value: none" or several). Those values come from a formula or a shared key; edit `build.py` by hand.
3. Run again with `--apply` to rewrite the single-match keys in `P`.
4. Rebuild and render, then `tools/metrics.py` against the designer's render: only the tweaked areas should change. Log the change in `PROGRESS.md` as a user tweak, not a review round.
