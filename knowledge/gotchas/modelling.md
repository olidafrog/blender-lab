# Modelling from code: characters, parts, posing

Learned on `roman-model`, the first character built entirely in `build.py`. The build there is the worked example.

## Getting the low-poly look

- Loft → Subdivision → Decimate (Collapse) gives round tubes with visible ring bands and sliver triangles. Reviewers call it "barrels" or "inflatable". Build at the target count instead: 8-point limb rings and 12-point torso rings with per-vertex control, a ±0.025 H vertex jitter, then `bmesh.ops.triangulate(quad_method="BEAUTY")`. Decimate suits sculpts, not built meshes (the manual says so). `roman-model`
- The torso reads as a body only with planes: a pec push on the front ring points, the dead-front point pulled back (sternum crease), side points pushed out (lats), a ring under the pecs with no push (the shadow shelf). Gaussian bumps on a dense ring read as round mounds. `roman-model`
- Jitter armour only where the reference's armour is faceted too. Jittered boots and straps read as "star-shaped triangles" against a clean-prism reference. `roman-model`
- A small key (about 1.2 m at 5 m) is what makes facets read. With a 3 m softbox, neighbouring facets differ by about 5 % in value and the mesh looks smooth. The reference's differ by 20–30 %. `roman-model`

## Posing without a rig

- Two-bone IK in Python beats joint angles: place feet and fists in `P`; knees and elbows come from a pole vector. Build every part already posed in its bone frame (`frame_from(axis, front)`: local −Z along the bone, −Y to the front). Bone heat (automatic weights) fails on multi-part meshes. `roman-model`
- A repeated "gap between the arm and the body" complaint was the elbow pole, not the fist target. Moving the fist never closed it; pointing the pole inward (elbow tucked, forearm angled out) did. `roman-model`
- Translate "viewer left/right" into character sides before editing. A viewer-right fix landed on the wrong leg. `roman-model`

## Parts on a faceted body

- Straps and belts: ray-cast onto the built torso (`BVHTree.FromBMesh`, cast from outside toward the spine) and offset along the hit normal. A formula surface point missed the facets by up to 2 cm. The belt vanished inside the skirt, and chest facets poked through the strap. `roman-model`
- A ribbon along a steep path: take its width from `normal × tangent`. A fixed "up" width direction collapses and twists the band into a rope. `roman-model`
- A pleated skirt reads only as separate flat plates: one solidified quad per pleat, stepped in and out. A zigzag ring on a frustum reads as a triangulated cone. `roman-model`
- Open shells (pads, helmet) show a dark cavity from below. Close pads with a bottom face; solidify only shells whose inside cannot be seen. `roman-model`
- Intersections that clay hides show in colour: skin poking through boots, skirt and pads. Render the colour look before the final, even in a clay-judged loop. `roman-model`

## Checking a model blind

- Workbench subject mask: FLAT light, SINGLE black, film transparent, backdrop hidden; under a second per render. Compare it with a thresholded reference mask by IoU, and by band widths and a red/blue overlay. `tools/silhouette.py`. `roman-model`
- IoU finds gross pose and proportion errors and goes flat near 0.75–0.8. The look then improved a lot with little IoU change, so do not rank close versions by it. `roman-model`
- Thresholding a sand-on-sand reference: separate on (R−B)/R (subject ≥ 0.45, backdrop ≈ 0.30), not on luma. Floor shadows are as dark as lit clay. `roman-model`
- A debug sheet (ortho front, side and back, plus the hero view; random colour per object; backface culling) shows intersections, flipped normals and hidden parts the hero render hides. `roman-model`
