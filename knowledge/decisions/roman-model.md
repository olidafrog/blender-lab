# roman-model — decision record

The lab's first character-modelling experiment: a stylised low-poly Roman legionnaire from an AI-generated "Low Poly Factory" figurine image, built entirely in `build.py`. Final clay score 6.5 (calibrated 6.4 vs v08 5.8); best loop score 6.8 (v08). Silhouette IoU 0.84 against the reference mask. A coloured "legion" look ships beside the clay one.

## Chosen

- **IK skeleton in Python, no armature.** Feet and fists are placed in `P` (head units); two-bone IK with a pole vector gives knees and elbows; every part is built already posed. Bone heat weighting fails on multi-part meshes, and a static render needs no rig.
- **Body: low-count planar ring lofts, jittered and triangulated.** 8 points per limb ring, 12 on the torso with per-vertex control (pec push, sternum crease, lat flare), ±0.025 H vertex jitter, then BEAUTY triangulation. This gives the reference's irregular flat facets directly.
- **Armour and props built face by face**, clean and un-jittered: Corinthian helmet as a grid with deleted cells (T cut) plus a nose wedge, crest as a solid between two Bézier arcs, pads as closed flattened caps, skirt as separate stepped plates, boots as tapered prisms with a cuff and a flat-soled foot, strap and belt ray-cast onto the real torso.
- **Clay look matched by measurement:** Standard view, small key (1.2 m) so facets differ 20–30 % in value, world fill for the shadow tone, and a self-lit cyc (`Glow`, low albedo, `visible_diffuse` off) that stays even floor-to-wall.
- **Silhouette IoU gate** (`tools/silhouette.py`): a Workbench mask against a thresholded reference mask, with band widths and a red/blue overlay, before every Opus review.
- **Fable as advisor** at the plan and at the 3-review mark; both consults changed the mechanism.

## Rejected

- **Loft → Subdivision → Decimate (Collapse)** (v01–v03). Round tubes with ring bands and slivers; reviewers read "barrels" three rounds running. Decimate is for sculpts, not built meshes.
- **SDF-fused body.** The armour hides every joint; fusion would add voxel cost and terraces.
- **Skin modifier, metaballs, CC0 base mesh** (see `experiments/roman-model/RESEARCH.md`).
- **85 mm lens.** Flattened the heroic perspective; 50 mm matched the reference.

## Open items (from the last review and calibration)

- The torso faces the camera more than the reference (wants about 20° more turn), and it reads boxy with too little V-taper.
- Legs read thin because the skirt flares into a bell. The fix is a hem that drapes over the thighs: ray-cast each plate's hem outward from the legs. Do not trade the two values against each other.
- The helmet front is flat; the reference dome is rounder, with cheek guards angling to the jaw and a neck flare.
