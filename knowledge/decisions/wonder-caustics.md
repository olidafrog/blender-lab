# Dispersive glass: decisions

Experiments: `wonder-caustics` (v1, 8.6/10 after 8 rounds) and `wonder-caustics-v2` (8.3/10 after 16 rounds, reviewer's pick v2_45). A solid perspex Wonder logo on black, lit so that spectral bands run through the faces. Research is in `experiments/wonder-caustics-v2/reviews/research-brief-v2.md`. General techniques are in [Cycles gotchas](../gotchas/cycles.md) and [shader nodes](../gotchas/shader-nodes.md).

## What makes the look

- **Transparent objects on black are invisible.** Something bright must sit behind them to refract. Thin strip lights alone gave a black frame. A big uniform emitter gave a flat cream slab.
- **Colour needs two things: hard edges in the light, and curvature in the surface.** Bands with black gaps between them, plus crowned faces, give spectral ribbons. Flat faces give colour only at the rims. High-frequency crown noise gives tie-dye.
- **Each band carries its own full red-to-violet ramp**, rotated about 18–22° off the bar axis. A two-colour band gives a fringe at each end, not a spectrum.
- **Blender 5.2 has no dispersion socket.** Sum several Refraction BSDFs with IOR = base + d × spread through Add Shaders. v1 used 3 lobes (R, G, B). v2 uses 6 (R, Y, G, C, B, V, each weighted 1/3). Six lobes give continuous spectra but paler colour. Three lobes are punchier.

## v2 decisions

**No remesh. Flat-shaded caps. Crown as a shader bump, not geometry.**
v1's jagged "comb" on the bevels had three causes: the Displace modifier's Clouds texture used the original noise basis, which has lattice kinks that refraction magnifies; the voxel remesh terraced the tight bevels; and smooth shading across the n-gon caps' sliver triangles banded the normals. v2 imports the SVG, extrudes, runs one angle-limited bevel with hardened normals, sets `use_smooth = False` on faces whose normal is along the depth axis, and adds the face crown as a Bump node weighted by the object-space normal.
Rejected: Quadriflow remesh (row ripples), subdivision surface (rounded corners off-brand), a second vertex-group bevel pass (corrupted the caps).

**Reflectors are reflect-only. The back panel is refract-only. Lamps do not pass through the glass.**
Anything bright that a transmission ray can reach is imaged through the glass as a hard shape. The fix is per-object ray visibility: reflection cards and the camera strip use `visible_transmission = False`, the banded back panel uses `visible_glossy = False`, and lamps use `visible_transmission = False`. A Light Path Transmission Depth gate also removes the glossy lobe once a ray is inside the glass, so lamps do not ghost off the inner surface.
Rejected: emissive strips as rim kickers (they imaged as white bars through the glass), soft dark "holes" painted onto the panel to hide a refraction (the sources were internal reflections, not the panel).

**Two soft kickers 15° behind the object for rim hairlines.**
Kickers give the bottom edges a warm and cool hairline. At 28° behind they image through the side walls as pickets. Wider kickers at lower radiance stop the streaks.

**An imperfection stack that occludes, never emits.**
Dust is Voronoi cells thinned by white noise and mixed as a black diffuse occluder plus a roughness bump. Fingerprints and haze change glossy roughness only. Scratches are Voronoi distance-to-edge windows under a sparse noise mask, with a small bump. Everything is tuned to be findable at 100% and invisible at thumbnail size.
Rejected: squashed-noise scratches (planar slices that read as ribbing), iso-contour scratches (rings), Voronoi-edge scratches above 0.15 roughness (a mesh), ripple bumps above 0.2 mm (hammered or orange-peel glass), haze patches that reflect lamps (orange blobs).

**Six-lobe dispersion at spread 0.45.**
Spread 0.30 gives truer black between bands on the faces but loses 14% of the lit area. The reviewer wanted the black; the brief wanted the ribbons. Left at 0.45, exposed as `--set spread=0.30` for the darker read.

**Compositor as a node group, all values in `P["comp"]`.**
Fog glow off clipped cores, a wide veiling glow, faint streaks, lens-distortion dispersion, an ellipse-mask vignette, a near-black lift, an S-curve, saturation and white-noise grain. Shallow focus at f/2.8 with the focus plane on the front face.

## Known limits

- A rainbow sliver at bar 5's lower-left corner. Isolation renders show it is the back panel refracted through the corner prism. It reads as a floating chip. Retouch it, or add a compositor matte.
- Faint horizontal slats along bar 1's top bevel, from the same panel seen through that bevel.
- The corner "45° chamfer" is real: the SVG arcs have radius about 0.13 m, and a tilted 0.42 m slab's front and back arcs join by a straight tangent in silhouette. Not a bug.
- v2 is cleaner and more glass-like than v1. v1 has more energy in its ribbons.
