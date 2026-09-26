# Library

Reusable things for any experiment. Empty for now; it fills as experiments produce things worth reusing.

- `models/` — meshes (`.blend`, `.glb`, `.obj`).
- `textures/` — image textures.
- `hdri/` — environment maps.
- `materials/` — one `.blend` per material, holding one material with the same name as the file.
- `node-groups/` — one `.blend` per node group, same naming rule.

## Rules

- Promote a thing here the second time an experiment needs it.
- Names are `snake_case`. The file name matches the material or node-group name inside it.
- Put a source and licence line in `SOURCES.md` in each folder for anything not made here.
- Scripts reach the library through `common.LIBRARY`. Append from it; never edit a library file from an experiment build.
- A model built by a script keeps the script beside it (for example `models/wonder-logos/build_logos.py`).
- Big binaries here are committed. Keep them small, or ask before adding anything over 20 MB.
