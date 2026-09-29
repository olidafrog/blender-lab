# Wax seal chaos: decisions

Experiment: `wax-seal-chaos`, a fork of `wax-seal`. The user asked for "a completely different approach… use chaos and generate a random seed". It ended at 6.2 after 6 rounds, when the slope rule stopped it. Blind calibration against the same reference scored the fork's v06 at 6.6, its v04 at 6.2, and the original `wax-seal` final at 5.4. The fork beat the original.

## How the chaos worked

Seed 2761081326 (from `os.urandom`) drew one approach per axis from a pool of four. The pool is listed in `experiments/wax-seal-chaos/PROGRESS.md`.
- **Geometry: fluid pour.** It was infeasible, so the same RNG stream rerolled it to **SDF sculpt**.
- **Material: matte wax.** Principled Sheen and Oren-Nayar diffuse, no coat.
- **Light: sun at 3° plus a bounce card.** The card was later dropped.
- **Process: side-by-side reviews.**

Rule: honour the draw, and reroll from the same seed stream only when an attempt proves infeasible, not merely hard.

## What makes the look

- **The seal is one live SDF volume.** Pour slab ∪ bead tube − die − paper, then fillet, SDF mean, and a mesh-position blur ("Relax") to remove voxel terraces. The bead is a tube mesh with lumps, wobble and a pooled blob.
  - An SDF allows what the heightfield could not: a steep, even undercut outer wall, and one continuous concave fillet from the field into the bead.
- **The emblem is raised on the meshed die face by the library `emblem_field`,** so it stays swappable, with a round Bevel and Bevel Shape.
- **The light is a low sun (24°, 3° angle) from the right.** A warm world fill comes from above. The outer wall of the bead turns away from the sun and goes dark, as in the reference; a row-700 pixel profile against the reference set the angle.

## Rejected

- **Mantaflow pour-and-press, five bakes.** Real gravity slumped the wax into a 1 mm pancake before the die landed. Low gravity made a 15 mm crown splash. A slow press went unstable and exploded, at about 4 minutes per frame. `scripts/sim.py` is kept as the record.
- **Bevelling the emblem inside the SDF.** OpenVDB offsets chamfer convex corners into octagons.
- **Growing shapes with SDF Offset.** It grew far less than asked, so the die never cut a field.
- **A bounce card on the shadow side.** It lit the wall that should be darkest.
- **A black flag.** It darkened the paper, not the wall.

## Open

- **A pink-violet glow on the relief bevels under the low sun.** This is the violet-reach scatter showing on thin edges. Try a neutral radius, or scatter at 0.03 mm.
- **The near-black violet crease under the left rim** (reference 33, 22, 48). No render reached it.
- **Chalky micro-texture and layered flow sheets.** The flow lines still read as hairs.
- **Side-by-side reviews run about 0.6 harsher than render-only ones.** The original final scored 5.8 side by side against 6.4 blind. Compare scores only within one instrument.
