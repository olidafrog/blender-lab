# wax-seal-chaos — research

The reference read, the numeric targets and the material facts carry over from `../wax-seal/RESEARCH.md`, as corrected there. This file covers only the approaches drawn by seed 2761081326.

## Read of the reference

The same photo as `wax-seal`. The parts the old build never solved, in order:
1. **The body read.** Every review said "soft plastic or fondant". The old rim was a mathematical arc; the real rim is squeezed-out wax, with an uneven bead, folds and a pooled lump.
2. **The lit rim is too wide and too bright.** The old bead cross-section was an idealised ellipse.
3. **The relief tops read as flat.**

## Most likely process

A real seal forms in two steps. Molten wax pools and spreads. Then the metal die presses in and squeezes the wax outward into a rolled rim. The chaos draw rebuilds that process physically, instead of drawing its result.

## Techniques to use

- **Geometry: a Mantaflow press.** Separate script `scripts/sim.py`, cached to `assets/`.
  - The scene is built at 20× scale, because Mantaflow ignores real size and a 34 mm blob behaves like water. The mesh is scaled down on export.
  - Liquid domain with FLIP, `resolution_max` about 200 (0.25 mm real voxel), `use_viscosity` with `viscosity_value` 0.5–2, and `use_fractions`.
  - A seeded, lumpy blob of overlapping ellipsoids pours and spreads. Then a keyframed cylinder (COLLISION, `surface_distance` 0, subframes 3) descends to a 1.4 mm real gap and holds.
  - The export frame is taken while the die is down.
  - Bake with `temp_override(active_object=domain)` and `fluid.bake_all()`, `cache_type='ALL'`, and an absolute `cache_directory`.
  - Sources: the API dump (`FluidDomainSettings`, `FluidFlowSettings`, `FluidEffectorSettings`), the manual (`physics/fluid/type/domain/*.rst`), VisitLab.
- **Emblem: the library emblem field.** It is applied to the sim's flat pressed field in GN: points under the die are set to the die height plus the relief. This keeps the Wonder logomark swappable, with Size, Relief and Bevel controls. `library/node-groups/build_wax_seal.py` (`emblem_field`).
- **Material: matte-wax BRDF.** Principled with the real Sheen lobe (Weight 0.2–0.5, Roughness 0.3–0.6, a paler tint) and no Coat. Diffuse Roughness 0.5–1.0 (Oren-Nayar, 4.3+). Short violet scatter (0.07 mm, radius 1, 0.5, 1.2), carried over. Source: manual `principled.rst` §Sheen; `4.3/cycles.md`.
- **Light: a sun and a bounce card.** A sun with `angle` = 3° (penumbra ≈ 0.052 × height, crisp like the reference's 10 px edge), from the upper right at about 32°. A large white card, hidden from camera, faces the shadow side. There is no world fill beyond a trace. Source: manual `light_object.rst`.
- **Process: side-by-side reviews.** The reviewer gets `scripts/sbs.py` composites (reference | render at the same crops), not render crops alone.

## Rejected approaches

- **Fluid sim at real millimetre scale.** Mantaflow has no real-world size (T73474), so it flows like water.
- **Stopping the die at under 3 voxels.** Thin sheets vanish (volume loss with moving obstacles, T84287).
- **Relief detail from the sim itself.** A 0.25 mm voxel cannot hold a 0.15 mm bevel, so the relief comes from the GN emblem field.

## Numeric targets

The same as `../wax-seal/RESEARCH.md`, measured as regions:
- Paper ≈ 221. Lit field ≈ 191, 184, 200.
- Shadow-side rim, median of the dark band: 98, 85, 111.
- Cast-shadow row 900: hard edge (204 → 73 within about 10 px), core 45–55 L.
- Right-rim groove: 33–46 L over about 50 px.
- Lit-rim highlights reach about 236 only in a narrow band at the outer edge.

## Open questions

- Does a 200-resolution bake finish in minutes on the M4 Max? Does the sheet under the die survive?
- Is the exported liquid mesh closed (for random-walk SSS)? Is its surface smooth enough without heavy smoothing?

## Sources

- Local: `reference/api-dump-5.2/types/FluidDomainSettings.txt`, `FluidFlowSettings.txt`, `FluidEffectorSettings.txt`; `reference/api-docs-5.2/bpy.ops.fluid.txt`; manual `physics/fluid/type/domain/settings.rst`, `cache.rst`; `render/shader_nodes/shader/principled.rst`; `render/lights/light_object.rst`; release notes `4.3/cycles.md`, `4.5/physics.md`, `5.2/bugfixes.md`.
- https://visitlab.cineca.it/index.php/2016/04/21/how-to-a-sealing-wax-stamp-animation-in-blender/ (fluid-sim wax seal)
- https://github.com/ichlubna/blenderScripts (headless `bake_data` pattern)
- https://projects.blender.org/blender/blender/issues/73474 (snippet: real-world size ignored)
- https://projects.blender.org/blender/blender/issues/84287 (snippet: volume loss with moving obstacles)
- Blender Artists thread 1208235 (large domains for faster fluid)
- Found nothing: a worked 5.x `temp_override` bake example, official minimum-gap guidance, and Sheen values for wax.
