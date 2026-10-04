# Modelling from code: characters, parts, posing, hard-surface plates

Characters were learned on `roman-model`, the first character built entirely in `build.py`; hard-surface plates on `cyber-model` (last section). The build there is the worked example. The reusable parts are `library/models/lowpoly-character/character_kit.py` and `tools/debug_views.py`.

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

## Hard-surface plates from traced outlines

Learned on `cyber-model` (a sci-fi radio; final calibrated 6.7 with a Sonnet reviewer) and `cyber-deck-v2` (same reference, Opus, 6.4). Code: `experiments/cyber-model/scripts/hs_kit.py`; the loft kit `library/models/hardsurface-kit/hardsurface_kit.py`.

- CAD-style shells from code: loft a rounded plan outline through a designed section (foot, wall, 48–55° flat slope band, 1.2–1.4 mm top fillet, 0.4 mm crease, optional undercut stem) with flat n-gon caps. Watertight, whole device in 4 s, clean in clay and mirror at the first build; this is Fusion's sketch → extrude → fillet. Keep every section inset below the smallest convex plan radius or the offset ring crosses itself. `cyber-deck-v2`
- Pockets from profiled cutters that carry the host's rim and floor fillets, each cutter its own object in a Collection operand (overlaps then work in both solvers). Face attributes on the host (edge-wear tags) survive the boolean. `5.x` `cyber-deck-v2`
- A 3 mm top fillet on a 4 mm slope shades as one pillow; keep the fillet small (1.2 mm) so the slope reads as a flat band. Give shallow plan bends the largest radius the edges allow: a fixed small radius on a shallow bend reads as a crease. `cyber-deck-v2`
- Edge wear: tag only the middle stations of the convex top fillet at loft time (FACE attribute) and read it with an Attribute node. Wear on the whole fillet read as a chalky 15–25 px band for six rounds. `cyber-deck-v2`

- Build a stack of separate extruded 2D outlines, each with its own bevel. Height matters more than it looks: a 6 mm slab with 3–5 mm steps drew "thin tray" in two reviews. Measure a wall on the reference first (about 13 mm here), then use a 13 mm slab, 4–8 mm steps and one 12 mm block for the tallest plate. `cyber-model`
- Bevel by edge class, not by one angle: top rim weight 1, vertical corners 0.35 only where the faces differ by more than 35°, feet and pocket floors 0. One width on every edge makes soft bricks. `cyber-model`
- Crisp chamfer: 1 segment, 0.5–0.65 mm, Harden Normals off, flat shading on the plates, corner arcs of 8+ segments per 90°. Harden Normals plus Smooth by Angle gives a soft gradient shoulder that four reviews called "pillowy". That pair is right for big smooth faces. Unhardened smooth normals after a boolean left a dark triangle on one plate, and flat shading removed it. Weighted Normal measured worse (max normal error 0.022 against 0.000). `5.x` `cyber-model`
- A repeated "wrong part" complaint (the dial bracket: "triangle", "teardrop", four rounds) is fixed by tracing the part from a 4K or orthographic crop, not by reshaping the old outline. Bare flat ends of gunmetal cylinders next to an LCD mirror it ("teal caps"): cap them in dark rubber. `cyber-deck-v2`
- Black gaps come from geometry first: 0.7 mm gaps between same-level plates, an undercut (a slab over a narrower stem), a 3 mm moat cut round the tall plate in its neighbours, a black liner slab under the lower plates, and cutters that carry a black material. An ambient-occlusion multiply alone left creases grey for four rounds. `cyber-model`
- Do not stand the plates on a visible base slab: void-black it read as "a black tray", near-black it lost the calibration (`cyber-model`), polymer its rounded rim read as a tray or "pancakes" for five rounds (`cyber-deck-v2`). Bring the outer shells down to the table on an inset foot and make the base a hidden black core.
- Tertiary detail that read at 1600 px: sunk screws (a hole with the head below the surface), vent slots from joined cutters, engraved lid text and labels as decals, a steel lip round a vent window, scratch strokes from a drawn mask. Raised screw discs read as buttons. `cyber-model`
- Coiled cord: a poly-spline helix round a path, with the coil radius ramped to 0 at both ends so the straight leads join the same tube; 21 turns for a 90 mm run. Give each free part something to sit on: a jack over the body edge and a boss with no body under it were the first "floating" complaints. `cyber-model`

## Architecture from a straight-on photo

Learned on `aztechno-building` (a facade 29 m wide at 38 px/m).

- Trace every element in reference pixels into a data file and convert to metres with one px-per-metre value; a shift-lens camera with `lens = 36 · ppm · D / W` and shifts from the axis and horizon pixels then lands the facade plane on the reference at any distance D. Parts set back or forward (roof tanks, an angled wing, a sign) go through one `at_depth(u, v, y)` helper so they still land on their pixels. `aztechno-building`
- A global relief multiplier must not scale parts with a known size: caps, oculi rings and tanks went 0.7–1 m deep and were flagged for six rounds. Give those absolute depths. `aztechno-building`
- Outline strips stacked round a moulding read right when each outer layer sits a little (1.8 cm) behind the one inside it: they stay in the sun and the core casts the shadow. Equal depths put whole strips in shade. `aztechno-building`

## Interiors from a LiDAR scan and phone photos

Learned on `apartment-model` (the user's flat: a Polycam scan plus 8 iPhone photos; final 7.9, all pixel targets hit). Code: `experiments/apartment-model/scripts/` (`scan_tools.py`, `scan_render.py`, `shell_kit.py`, `fit_cam.py`, `refine_cam.py`, `joint_fit.py`, `review_sheet.py`).

- Measure the scan, never render it. Align by an area-weighted 4-fold wall-normal histogram, take the floor from up-facing faces, and read each plane as a peak in an area-weighted histogram of face positions by normal family. Textured ortho elevations with a metric grid read openings fast. Polycam's own plan (9.00 × 5.82) disagreed with the plane fits (8.74 × 5.63). `apartment-model`
- LiDAR rounds every edge by 5–15 cm and fills small steps. Coves, pilaster heads, reveal splays and frame depths come from the photos, checked against the scan's transitions. The scan read a 0.20 m pilaster (photos: 0.10) and no step at the wall tops (photos: a cove that meets the ceiling about 5 cm in). `apartment-model`
- Window reveals can splay asymmetrically: here toward the central pier. Symmetric splays fitted the head-on photo and missed the oblique ones by 24 px. An oblique view is the test for reveal geometry. `apartment-model`
- Model only what the user wants kept, and ask what a moving part is. Six rounds treated open secondary glazing as factory casements. `apartment-model`

## Upholstery (sofas, cushions, ottomans)

- Under soft, even interior light a puffed face barely shades (a 4° slope gives no gradient); the width of the edge roll is what reads as a cushion. 2.5 cm read as "flat slabs" for four rounds, 5.5 cm as "bolsters and loaves"; 4.5 cm on seats, 3 cm on arms and backs worked. `apartment-model` round three
- A sat-in dip can silently cancel a dome: a 3 cm Gaussian sag left 3.7 of a 6 cm crown. Check puff and sag with a mesh profile (`tools/mesh_profile.py`), not by eye. `apartment-model`
- Build blocks from code: an edge-packed lattice on a rounded box, faces puffed to zero at the seams, then one deformation field (sag, front roll, tuck under the overhang, ripples) applied to the block and to its seam flange alike, so the flange stays on the seam (`experiments/apartment-model/scripts/furniture/upholstery.py`). Cloth with pressure was not needed.
- A front face that stays too bright under window light leans under the seat's overhang in reality; tuck its foot back 3–4 cm (photo 2 front/paint 0.80 → 0.60, photo 0.48). Darker surroundings did not fix it. `apartment-model`
- For a bought piece, the maker's dimension drawings beat photo estimates: they corrected the seat (39 seam / 45 crown), back blocks and arm depth four rounds in. A LiDAR scan bridges the gap behind furniture to the wall (depth read 1.17 m against 0.92). `apartment-model`
