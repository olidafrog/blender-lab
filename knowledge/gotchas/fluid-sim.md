# Fluid simulation (Mantaflow)

- Mantaflow has no real-world size (T73474). A 34 mm pour at true scale flows like water. Build at 10–30× and scale the mesh down on export. `5.x` `wax-seal-chaos`
- A GEOMETRY flow made of joined, overlapping shells fills only their union, so most of the planned volume goes missing. Voxel-remesh the lumps into one shell, then scale that to the target volume. `wax-seal-chaos`
- `bmesh.calc_volume()` on the liquid mesh is meaningless: it read 282 mm³ for a visible 22 × 12.7 mm dome. Judge by bounds and a height profile. It cost ~5 bakes chasing a "volume loss" that did not exist. `wax-seal-chaos`
- Give each variant its own `cache_directory`. A shared one can serve cached frames from other settings. `wax-seal-chaos`
- A viscous press is the wrong tool for a wax seal:
  - At real gravity even `viscosity_value` 10 slumps into a 1 mm pancake before the die lands.
  - At gravity 0.8 the squeeze splashes 15 mm up the die wall.
  - A slow press at gravity 3 goes unstable: frames slow to ~4 min, then it explodes into spray.
  Use an SDF sculpt instead (`decisions/wax-seal-chaos.md`). `5.x` `wax-seal-chaos`
- For a quick look at a cached frame, rebuild the scene with the same settings, skip the bake and `frame_set(n)`. `scripts/sim.py` `export_frame`. `wax-seal-chaos`
