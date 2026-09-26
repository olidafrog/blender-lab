# Geometry: curves, SVG, geometry nodes

- `transform_apply` on a 2D curve fails with "Rotation/Location cannot apply to a 2D curve". Set `dimensions = "3D"` first, then back to `"2D"`. `fill_mode = "NONE"` exists only on 2D curves, so set it after. `5.x` `wonder-logos`
- Bezier segments with VECTOR handles on both ends evaluate to one edge at any resolution. Mark straight SVG segments this way to keep a low-poly outline with round curves intact. `5.x` `wonder-logos`
- GN Extrude Mesh (Faces) moves the faces and leaves the bottom open. Join a Flip Faces copy of the Fill Curve output, then Merge by Distance. Fill Curve in N-gons mode gives tri-free caps that bevel cleanly. `5.x` `wonder-logos`
- `obj.evaluated_get(dg).dimensions` read in the same script that built the object was wrong (off by +2 m per axis). Measure the vertices of `to_mesh()` instead. `5.x` `wonder-logos`
- SVG import ignores `clipPath`, and each `<path>` becomes its own object. Join them per logo. Scale is not 1 px = 1 unit; rescale from the SVG `width`. `wonder-logos`
