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
- `textures/brick/factory_brick/` — Poly Haven factory_brick (CC0, 1.5 m tile, 16 courses): colour, 16-bit displacement, roughness. Regraded through its height mask by `experiments/apartment-model/scripts/mat_kit.py` (`brick_group`).
- `textures/wood/oak_wood_planks/` — Poly Haven oak_wood_planks (CC0, 1.2 m, rustic oak in ~90 mm planks, grain along U): colour and roughness; sampled one source plank per herringbone plank by `mat_kit.py` (`herringbone_group`).
- `textures/imperfections/` — CC0 wear masks (scratches, fingerprints, dust) used by `tinted_plastic`.

- `node-groups/cloud_shape.blend` — the "Cloud Shape" geometry-nodes group: a mesh of lobe points (each with a `radius` attribute) becomes a `density` volume with a flat-base option. It brings `cloud_material` along; append this file alone. From `clouds`.
- `materials/cloud_material.blend` — volumetric cloud: Mie scatter plus albedo absorption. Colour means how the lit cloud looks. For any volume object.
- `node-groups/build_clouds.py` — builds both, plus the lobe-tier seeder (`seed_points`) and a `Neon` emitter group. Experiments import it; see its docstring and `knowledge/decisions/clouds.md`.

- `node-groups/wax_seal.blend` — the "Wax Seal" GN group: a live heightfield seal (rim bead, stamped field, emblem relief). Its Emblem input takes any curve, text or mesh object, auto-fitted to Emblem Size, with Relief, Bevel and Bevel Shape controls. Built by `node-groups/build_wax_seal.py` (`from build_wax_seal import seal_group, gn_input`). From `wax-seal`.

- `node-groups/plot_kit.py` — line-art forms for a pen plotter as Geometry Nodes groups: a formula compiler (`"cos(u)*sinh(v)"` → Math nodes), `Isolines` (contours of any field on any mesh), and factories for a parametric surface, a sliced solid (parametric, implicit, tube, any object), a field on a sphere and a curve family. Each form outputs curves plus its surface as the occluder for `tools/plot_svg.py`. A code module. From `plotter-blend` and `plotter-forms`, whose `scripts/catalog.py` is the worked example.

- `models/lowpoly-character/character_kit.py` — low-poly character kit: IK (`two_bone`, `frame_from`), superellipse and planar torso rings, loft/grid/box bmesh builders, `jitter_triangulate` for the irregular-facet look, and `finish_mesh` (flat faces, a per-face `facet` attribute). A code module, not a `.blend`. From `roman-model`, whose `build.py` is the worked example.

- `models/hardsurface-kit/hardsurface_kit.py` — CAD-style hard-surface parts from code: a rounded plan outline (`Outline`, `rrect`, `circle`, `toothed`) lofted through a designed section (`sec_slab`, `sec_step` with slope, fillets and undercut; `sec_rod`), profiled pocket cutters (`sec_cutter`), `rod` for lathe parts with an optional knurl twist, a checked `cut()` (Collection operand, Manifold then Exact, material transfer, slot clean-up), `helix_cord`. Convex top-fillet crests carry a FACE attribute `wear`. A code module. From `cyber-deck-v2`, whose `build.py` is the worked example.
- `models/arch-kit/` — facades from a straight-on photo at true scale: `arch_shapes.py` (plain python: traced shapes in reference px, winding-safe offset) and `arch_kit.py` (px → metres, filled-curve slabs with holes, `at_depth`, shift-lens camera, Paint and Curtain Glass control groups). A code module. From `aztechno-building`, whose `scripts/facade.py` and `build.py` are the worked example.

Python builders for both materials: `from build_materials import disc_group, case_group` (add `LIBRARY / "materials"` to `sys.path`).

## Rules

- Promote a thing here the second time an experiment needs it.
- Names are `snake_case`. The file name matches the material or node-group name inside it.
- Put a source and licence line in `SOURCES.md` in each folder for anything not made here.
- Scripts reach the library through `common.LIBRARY`. Append from it; never edit a library file from an experiment build.
- A model or material built by a script keeps the script beside it (for example `models/wonder-logos/build_logos.py`, `materials/build_materials.py`). Write a material file with `bpy.data.libraries.write(path, {mat}, path_remap="RELATIVE_ALL", fake_user=True)` so it holds just that material and finds its textures by relative path.
- Big binaries here are committed. Keep them small, or ask before adding anything over 20 MB.
