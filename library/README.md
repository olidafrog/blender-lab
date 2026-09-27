# Library

Reusable things for any experiment. It fills as experiments produce things worth reusing.

- `models/` — meshes (`.blend`, `.glb`, `.obj`).
- `textures/` — image textures.
- `hdri/` — environment maps.
- `materials/` — one `.blend` per material, holding one material with the same name as the file.
- `node-groups/` — one `.blend` per node group, same naming rule.

## Contents

- `models/wonder-logos/` — the Wonder logomark and logotype as curves with a live Extrude modifier.
- `materials/cd_diffraction.blend` — CD/MiniDisc data surface: a diffraction grating as a BSDF. Tracks circle the object origin. Needs a dark reflection with small lights beside it to show colour (see `knowledge/decisions/wonder-minidisc.md`). From `wonder-minidisc`.
- `materials/tinted_plastic.blend` — translucent tinted polycarbonate; one Colour input at a reference depth drives volume absorption. Scene in metres; closed meshes. From `wonder-minidisc`.
- `textures/imperfections/` — CC0 wear masks (scratches, fingerprints, dust) used by `tinted_plastic`.

Python builders for both materials: `from build_materials import disc_group, case_group` (add `LIBRARY / "materials"` to `sys.path`).

## Rules

- Promote a thing here the second time an experiment needs it.
- Names are `snake_case`. The file name matches the material or node-group name inside it.
- Put a source and licence line in `SOURCES.md` in each folder for anything not made here.
- Scripts reach the library through `common.LIBRARY`. Append from it; never edit a library file from an experiment build.
- A model or material built by a script keeps the script beside it (for example `models/wonder-logos/build_logos.py`, `materials/build_materials.py`). Write a material file with `bpy.data.libraries.write(path, {mat}, path_remap="RELATIVE_ALL", fake_user=True)` so it holds just that material and finds its textures by relative path.
- Big binaries here are committed. Keep them small, or ask before adding anything over 20 MB.
