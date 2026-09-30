# Geometry: curves, SVG, geometry nodes

- `transform_apply` on a 2D curve fails with "Rotation/Location cannot apply to a 2D curve". Set `dimensions = "3D"` first, then back to `"2D"`. `fill_mode = "NONE"` exists only on 2D curves, so set it after. `5.x` `wonder-logos`
- Bezier segments with VECTOR handles on both ends evaluate to one edge at any resolution. Mark straight SVG segments this way to keep a low-poly outline with round curves intact. `5.x` `wonder-logos`
- GN Extrude Mesh (Faces) moves the faces and leaves the bottom open. Join a Flip Faces copy of the Fill Curve output, then Merge by Distance. Fill Curve in N-gons mode gives tri-free caps that bevel cleanly. `5.x` `wonder-logos`
- `obj.evaluated_get(dg).dimensions` read in the same script that built the object was wrong (off by +2 m per axis). Measure the vertices of `to_mesh()` instead. `5.x` `wonder-logos`
- SVG import ignores `clipPath`, and each `<path>` becomes its own object. Join them per logo. Scale is not 1 px = 1 unit; rescale from the SVG `width`. `wonder-logos`
- A Bevel wider than about a third of the narrowest part of the cap makes the n-gon cap overlap itself, and the viewport draws dark holes. Clamp Overlap does not stop it. Triangulated caps are no fix: Clamp Overlap then shrinks the bevel to almost nothing. On the Wonder logomark (1.24 m wide) holes start at 0.04 m, and 0.03 m is clean. `5.x` `wonder-logos`
- The library logomark's geometry-nodes mesh keeps its own empty material slot, so the curve's material never reaches Cycles and it renders default grey (near black on a dark world). End the modifier stack with a Set Material node. `5.x` `eclipse-glow`
- Grid to Mesh defaults to Threshold 0.1. An SDF grid (Mesh to SDF Grid) needs 0, or the mesh comes out empty. `5.x` `eclipse-glow`
- Round a flat logo with live controls: curve → slab → Mesh to SDF Grid → Grid to Mesh, then set |z| from the distance to the outline (Geometry Proximity on Curve to Mesh). A straight wall plus a quarter round reproduces a bevelled slab without the Bevel overlap holes. `eclipse-glow/scripts/build.py` `inflate_group`. `5.x` `eclipse-glow`
- Check a `.glb` before using it. The first logomark export was 220 bytes: one empty node with no mesh. `eclipse-glow`
- `bpy.ops.object.transform_apply(scale=True)` straight after `primitive_cube_add(location=...)` left `location` at 0, with the offset baked into the mesh. Select objects by world-space vertex bounds, not `location`. `5.x` `opal-essence`
- GN Bounding Box defaults to Use Radius = True. On curves the default 1 m point radius pads the box, so fitting a logo by its box came out at about 40 % of the size. Turn it off. `5.x` `wax-seal`
- A flat mesh has zero z-range. A raycast height normalised by the bounding box then comes out 0, and the relief vanishes. A Text object evaluates to a flat mesh. Treat zero range as full height, and bevel from the boundary edges (Edge Neighbors face count = 1). `5.x` `wax-seal`
- GN interface panels: use `interface.new_panel()` and `move_to_parent(item, panel, i)`. A panel can share a name with a socket, and a panel's identifier is not a string, so filter on `in_out == "INPUT"` when looking up a socket by name. `5.x` `wax-seal`
- SDF Grid Boolean works like Mesh Boolean: UNION and INTERSECT read only the multi-input Grid 2, and anything on Grid 1 is silently dropped. Link every grid into Grid 2. DIFFERENCE is Grid 1 minus Grid 2. `5.x` `wax-seal-chaos`
- SDF Grid Offset is unreliable for shaping:
  - Grows fell far short (0.8 mm asked, 0.04–0.2 mm delivered, depending on band width).
  - An erode-then-dilate opening chamfers convex corners into octagons.
  Build solids at full size, and bevel crisp shapes by displacing the mesh with a distance profile. `5.x` `wax-seal-chaos`
- Points to SDF Grid carries a band only ~3 voxels deep, so fillet and mean smoothing shred it into holes at fine voxel sizes. Build tubes as a Curve to Mesh and use Mesh to SDF with a wider band. `5.x` `wax-seal-chaos`
- Grid to Mesh leaves voxel terraces that a low sun shows as concentric steps. Blur the mesh positions (Blur Attribute, vector, ~6 iterations) after meshing. `5.x` `wax-seal-chaos`

## Booleans and plates (hard-surface)

- Overlapping cutters joined into one operand cancel each other in an Exact boolean. The plate came back empty, or cuts were silently missing (vent slots never appeared). Set `modifier.use_self = True` (Exact only), and assert `len(mesh.polygons) > 0` after every apply. Print the sorted vertex z-levels of the result: a missing cut floor shows in one line. Retrying with MANIFOLD hid the cause. FAST is called FLOAT from 5.0. `5.x` `cyber-model`
- After `modifier_apply` on a Boolean the target keeps an empty material slot 0, so a later `materials.append` lands in slot 1 and every face renders default grey (white under a soft key). Clear the slots, or give the cutters a material and set `material_mode = "TRANSFER"` (5.x): the new wall faces take it, which gives black vent, screw-hole and moat walls. `5.x` `cyber-model`
- A hand-rolled miter offset of a concave outline self-intersects once the offset exceeds the corner radius, and the ring boolean built from it comes back empty. Round the outline first with a radius larger than the offset (grooves: r above inset + width; outward moats: r above the offset). A bmesh `inset_region` replacement gave empty rings on all five outlines; cause not found. `cyber-model`
- A Bevel modifier after booleans is clamped by the whole mesh (Clamp Overlap is global): a 2 mm rim fell to 1.25 mm with one pocket and 0.16 mm with slots and screw holes (Exact; 0.01 mm Manifold). With clamp off it overlaps. Put fillets in the geometry (loft sections, profiled cutters) instead. `5.x` `cyber-deck-v2`
- The Manifold boolean solver silently ignores a non-manifold operand (a Text mesh with 1236 open edges was not engraved, no error). `remove_doubles` first. `5.x` `cyber-deck-v2`
- Signed Edge Angle (GN) is positive for convex edges in 5.2 (a cube reads +1.571); the manual says the opposite. `5.2` `cyber-deck-v2`
- When you lower a part, recheck every part that sat at its old height. A steel frame set to the block's new top height covered the block and looked like a wrong material. `cyber-model`
