# apartment-model — research

## Read of the reference

The references are eight iPhone 16 Pro photos of a real room (2026-10-03, 11:33–11:35 UTC, bright overcast), a Polycam LiDAR scan of the same room, and a 1:60 plan. Round one judges the shell, so the order is about geometry first:

1. **Proportions and heights.** A 5.63 m wide, 4.08 m high double-height volume with a mezzanine over the back third. Its soffit at 1.93 m is barely above head height, which is the strongest spatial read in photos 3, 6, 7 and 8.
2. **Window wall.** Red-brown brick with two segmental-arched factory windows (sill 1.11, frame top about 3.66, brick arch top about 3.8) in 0.2 m reveals. Three brick piers stand 0.15 m proud of the wall up to about 1.5 m (photo 2). Off-white painted steel frames: an arched top light, a transom, and a grid of casements, some open. A dark curtain track sits under the ceiling over each window.
3. **Ceiling structure.** A central downstand beam (about 0.25 × 0.35 m) runs from the pier between the windows to a cross girder over the mezzanine front. The girder's front face sits 0.38 m proud of the mezzanine wall and its underside is at 3.68 m. Edge beams run along both side walls at the same depth. The ends are haunched (diagonal) where the girder meets the walls (photo 3).
4. **Mezzanine front.** A white wall with two black steel internal windows (about 1.7 × 1.14 m, sill 2.52 m) and a 1.93 m soffit with a fascia. A slim column at the centre line marks the dining/kitchen split.
5. **Under the mezzanine.** Kitchen (west): a counter along the west wall, an island and a back wall at x = 3.50. Dining (east): it runs deeper, to x = 4.34, has the hallway door, and a wavy-topped built-in bookcase on the back wall. Recessed downlights in the soffit.
6. **Surfaces** (round two weight): matt white paint, red-brown brick with cream mortar, warm mid-oak herringbone (laminate), white-painted steel versus black-painted steel.
7. **Camera.** Photos 1–3, 5, 7 and 8 are the ultrawide (14 mm equiv in EXIF, about 13.6 true); 4 and 6 are the main camera (24 mm). The iPhone corrects lens distortion, so a pinhole model fits; iPhone HDR tone mapping holds the windows.

## Most likely process

The room is a 1909–11 reinforced-concrete-framed brick factory (Bryant & May, listed Grade II), converted in 1988 with mezzanines inserted as "independent insertions" and ceiling beams over partition lines (ORMS). The model is a set of clean extrusions placed from measured planes: the scan gives every plane to ±2–5 cm, the plan gives the rooms the scan did not reach (hallway, shower room, upper floor), and the photos give the details (glazing bars, piers, haunches). It is built procedurally from `P` and never uses the scan mesh in the render.

## Techniques to use

- **Measuring the scan** (`scripts/scan_tools.py`, `scan_views.py`, `scan_render.py`). Area-weighted wall-normal histogram for yaw (0.54°), up-facing faces for the floor, and per-family area histograms of face positions for each plane. Textured ortho elevations with a metric grid read the openings. An agent tested numpy RANSAC on this scan: 10 planes in 1.4 s, floor to ceiling 4.078 m. Use plane histograms and reject any plane more than 3° off an axis. Blender 5.2, numpy.
- **Camera per photo** (`scripts/fit_cam.py`, `refine_cam.py`). Landmark LM fit (or a coarse search from the annotated position), then Nelder–Mead on edge correlation between a Workbench render of the textured scan and the photo. The scan still holds the furniture, so the photo and the render share edges. Sensor width 34.61 mm (diagonal equivalence for a 4:3 frame); 14 mm equiv is about 13.6 true, so fit the focal length within ±8 %. A shared focal length per lens is more stable than per photo (agent test: 0.8 % vs 7.7 %). Verify by an edge overlay.
- **Shell geometry** — boxes and extruded profiles in `build.py`; window openings cut as 2D outlines (wall face with holes, extruded to depth). Use no boolean on the main walls; assert face counts. Arch = segmental: chord 1.6 m, rise about 0.55 m.
- **Light** — overcast: sky texture or an overcast HDRI through the windows, no direct sun. The photos have no sun patches, at sun azimuth 176° and elevation about 34° against a 142° window normal. Exposure via `film_exposure`, Khronos PBR Neutral or AgX. See the lighting section below once that research returns.
- **Floor** — a herringbone board mesh from Python, one attribute per board for colour and grain offset (tiling rule tested by an agent: horizontal boards at (iW + 2jL, −iW), vertical boards offset by (−(L+W), +W), the field rotated 45°). Board size measured from the photos in round two.
- **Materials** (round two): Poly Haven `red_brick_03` / ambientCG `Bricks097` for the brick, a plain Principled BSDF for painted steel, white paint at albedo about 0.8.

## Rejected approaches

- **Rendering the scan mesh** — it is blobby (LiDAR rounds every corner by 5–15 cm), has holes at glass and dark areas, and has furniture baked in.
- **Polycam Room mode and the RoomPlan plan as the source** — ±15 cm per forum reports, walls straightened, and its 9.00 × 5.82 m disagrees with the plane fits (8.74 × 5.63 m), probably because it measures to wall centrelines or into the reveals.
- **fSpy / Perspective Plotter** — vanishing points only; our 3D landmarks constrain more.
- **Other flats' listings for dimensions** — the layouts differ (the user confirmed). Only building-wide facts are taken from them: segmental heads, metal frames with small panes, brick.
- **The 1:60 plan's kitchen** — out of date; the scan and photos show a west-wall run plus an island.

## Numeric targets

Scan frame: x along the room (window wall −4.40 → back), y across (west −2.875 → east +2.75), z up, floor 0. ±2–5 cm.

| Element | Value |
|---|---|
| Window wall inner face | x = −4.40 (brick, ±3 cm) |
| West / east wall | y = −2.875 / +2.75 (width 5.63; plan 5.68) |
| Ceiling | z = 4.08 (user 4.05) |
| Central beam | underside 3.73, about 0.25 wide, centre y = −0.03, x from −4.40 to 0.90 |
| Cross girder | front face x = 0.90, underside 3.68 (user 3.55), haunched ends |
| Edge beams on side walls | underside about 3.72, about 0.05 proud |
| Mezzanine front wall | x = 1.29 |
| Soffit | z = 1.93 (user 1.91); fascia about 1.93–2.0 |
| Kitchen back wall (west half) | x = 3.50 |
| Dining back wall (east half) | x = 4.34; hallway door y 0.12–0.90, height about 2.0 |
| Column | y = −0.02, x about 1.3, about 0.12–0.15 square |
| Windows (brick face) | W: y −2.40 … −0.85; E: y 0.65 … 2.20; sill 1.11; spring about 3.2; frame top about 3.66; brick arch top about 3.8; frame plane x ≈ −4.60 |
| Brick piers | front x = −4.25 (0.15 proud), top about 1.52; W y −2.875 … −2.42, centre −0.85 … 0.50, E 2.13 … 2.75 |
| Internal windows | E: y 0.64 … 2.30, W: y −2.40 … −0.68; z 2.52 … 3.66 |
| Radiator (west wall) | x −2.15 … −1.12 |
| Upper floor level | unknown; about 2.08 (soffit + 0.15) — open question |
| Hallway, shower room, stores, stairs, bedrooms | from the 1:60 plan: 72 px/m at 110 dpi, x = −4.40 + (py − 180)/72 × 0.975, y = −2.875 + (px − 500)/72 |

Cameras: `assets/cams/<n>.json` "refined" (loc, rot_deg XYZ, lens at sensor 34.62). Photo 2 has an edge correlation of 0.53, photo 3 0.58.

## Open questions

- The upper floor's level and ceiling (needs the stair riser count, or one measurement upstairs).
- Arch rise and spring height: frame and brick arch, to settle against the photo 2 and 4 overlays.
- Beam width (scan 0.19, photo estimate 0.22–0.3).
- Whether the side "edge beams" are beams or a plaster line.

## Round two: brick and floor materials (2026-10-03)

**Read of the reference** (photos 2, 4, 5, 8; 1:1 crops; floor and wall rectified onto the model planes with the fitted cameras, `scripts/rectify.py`):
- Brick: soft red-brown factory brick, worn faces, strong brick-to-brick tone spread with dusty pale patches and the odd pale or burnt brick. Mortar is thin, near flush, and slightly paler than the brick (photo 5). Mostly stretcher courses with scattered headers, read as English garden wall bond (uncertain). Courses 85–95 mm (rectified photo 2), consistent with an imperial brick plus a 10 mm joint.
- Floor: herringbone, oak-look (engineered or LVT), mid warm brown with a grey cast, flat-sawn figure (flame arcs and straight grain), dark thin bevelled seams, satin sheen. Spine along the room (x) in the living room and the kitchen (rectified photos 2, 3, 8). Tip lines 0.50 m apart, seam pitch 0.19 m along the spine: 700 × 140 mm planks (5:1).
- The photos are warm-balanced (paint reads sRGB 151, 146, 127 in photo 2): floor and brick hue relative to the paint matches the render already, so the rest is white balance, not albedo.

**Most likely process:** an old brick wall cleaned and left bare, lit only by bounce from the room (backlit by the windows); a 2020s engineered-oak or LVT herringbone in a 700 × 140 format.

**Techniques to use**
- Brick: shader math on Object coordinates (u = y + x along the course, v = z): course row, English garden wall bond (header course every 4th), per-brick random from White Noise on (column, row); face tone, pale and burnt bricks, dust patches; height in mm into Bump Distance 0.001 (joint 2 mm back, 1.6 mm S-curve arris, ±0.5 mm per-brick set, pitting). Brick research agent (Sonnet), verified in 5.2.
- Floor: herringbone from integer cells (c = (i − j) mod 2n), checked to tile numerically; plank-local coordinates and per-plank random; flat-sawn grain f = √(h² + (b − v_c)²) + taper·a into Wave BANDS SAW at Scale = 0.3142 / ring spacing; pore streaks; 1.5 mm bevelled seam. Floor research agent (Sonnet), verified in 5.2.

**Rejected approaches**
- The built-in Brick Texture: reads only X and Y of its vector, gives no per-brick ID for roughness and height, and cannot do garden wall bond.
- Image textures (Poly Haven red_brick_03, herringbone_parquet): fixed plank size and colour, tiling repeats over 5.6 m, and no single control node.
- Clearcoat on the floor: only widened the glare (floor agent).
- Displacement: bump is enough at 2–8 m.

**Numeric targets** (`scripts/mat_measure.py`, same regions in photo and render):
- Brick-to-paint luma: 0.21 (photo 2), 0.25 (photo 5). Floor-to-paint luma: 0.89 (photo 2), 0.99 (photo 5).
- Texture (high-pass luma std, 1024 px): brick 3–8, floor 8–13.
- Reference albedo: physicallybased.info brick linear (0.262, 0.095, 0.061); Poly Haven red_brick_03 mean (0.152, 0.097, 0.080). This brick is darker and greyer: matched to the photos by ratio, not to these.

**Open questions**
- The bond (garden wall vs English) and the course height to ±5 mm need a close, square-on photo of the brick.
- The floor's true colour under neutral light (a photo with a white card would settle it).

## Sources

- Polycam floor plan pipeline: https://poly.cam/blog/how-we-turn-raw-spatial-data-into-a-floor-plan-you-can-build-from-inside-polycams-floor-plan-pipeline
- iPhone LiDAR accuracy, classroom RMSE 4.2 cm: https://www.geodetski-vestnik.com/arhiv/70/1/47_Yanchuk.pdf ; corridor drift: https://isprs-archives.copernicus.org/articles/XLVIII-2-W8-2024/431/2024/
- Normal-histogram alignment: https://arxiv.org/pdf/2107.07778
- 35 mm equivalence on the diagonal: https://en.wikipedia.org/wiki/35_mm_equivalent_focal_length ; iPhone 16 Pro ultrawide: https://petapixel.com/2024/10/03/iphone-16-pros-ultra-wide-explained-understanding-the-give-and-take/ ; distortion correction: https://developer.apple.com/documentation/avfoundation/avcapturedevice/isgeometricdistortioncorrectionenabled
- fSpy importer (shift convention): https://github.com/stuffmatic/fSpy-Blender
- Bow Quarter history and listing: https://en.wikipedia.org/wiki/Bow_Quarter ; https://britishlistedbuildings.co.uk/101065761-bryant-and-may-factory-main-building-non-civil-parish ; https://orms.co.uk/posts/orms-revisits-bow-quarter
- Textures: https://polyhaven.com/a/red_brick_03 ; https://ambientcg.com/view?id=Bricks097 ; https://polyhaven.com/a/herringbone_parquet
- Herringbone in GN: https://blenderartists.org/t/herringbone-weave-geometry-nodes/1456326
- Pages that failed: learn.poly.cam (403), historicengland.org.uk (403), several Rightmove pages (410), YouTube.
- Round two (materials): https://physicallybased.info ; https://api.polyhaven.com ; https://en.wikipedia.org/wiki/Brickwork ; https://en.wikipedia.org/wiki/London_stock_brick ; https://www.buildingconservation.com/books/bcd2022/85/ ; https://www.designingbuildings.co.uk/wiki/Brick_sizes ; https://blenderartists.org/t/randomizing-brick-texture/1356217 ; https://blenderartists.org/t/should-bump-node-distance-ever-really-be-higher-than-0-001/1418023 ; https://blenderartists.org/t/how-to-make-a-herringbone-map-quick-written-tutorial/1255109 ; https://google.github.io/filament/notes/material_properties.html ; https://www.alpinefloor.com/news/which-direction-should-you-lay-herringbone-flooring.html ; https://www.meister.com/en/inspiration/Herringbone-a-classic-laying-pattern-for-parquet-flooring.html ; https://trade.ukflooringdirect.co.uk/products/karndean-art-select-glacier-oak-gluedown-herringbone-lvt
- Round two failed: poliigon old English bond (403), projects.blender.org issue 83184 (403), Karndean brochure PDF (certificate), floorwarehouse and flooringsurgeons (403). No Stack Exchange or shadertoy herringbone source found.
