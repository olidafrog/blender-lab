# cyber-deck-v2 — research

## Read of the reference

`references/ref_dt03.png` (736×552) is a finished 3D portfolio render ("DT-03 Multifunction Radio Device", AFI). v1 (`cyber-model`) measured the same image; its camera fit, rectified plan and numeric table are reused (`experiments/cyber-model/RESEARCH.md`). This read is about what v1 did not build. Crops at 3–4×: scratchpad `ref_sstep.png`, `ref_bottom.png`, `ref_left.png`, `ref_right.png`.

Effects, in the order they matter:

1. **Section profile — sloped, filleted steps.** Where one level drops to the next (the big S-step, the shield round the LCD, the lower block) the transition is a broad sloped face, about 45–60° and 4–6 mm wide in plan, with a soft rounded top edge (fillet ~1 mm) and a tight crease at the foot. It is a moulded part with draft, not a vertical wall with a hairline chamfer. The sloped faces face the camera and read **lighter** than the tops (tops ~70–80 sRGB, slopes ~90–105). v1 used vertical walls and a 0.5 mm chamfer everywhere: this is the main reason it read as flat CAD plates.
2. **Plan shapes with generous radii.** Every outline corner is rounded (3–10 mm radii on the shells, sharp only on small inserts). Concave corners are filleted too (the S-step inner corners).
3. **Layered massing.** A thick core body (side walls visible along the right and bottom, 13+ mm, with its own recesses, the gear-roller slot and the connector panel), an upper shield that rises over the LCD and the lid area, a lower-left battery block wrapped by a bright sheet-metal frame, a bottom-right end cap that turns into a horizontal cylinder, a left dial module on a silver bracket over a thick knurled gear. Parts overlap and cast deep contact shadow into each other.
4. **Secondary and tertiary detail.** Panel seams (thin dark grooves with a lighter lip), the recessed "DT-03" lid with a latch, sunk screws in rounded bosses, small triangle marks, a logo and small labels, the INSERT slot, connector sockets, a stacked gear-roller thumbwheel, a slide switch, selector knob, red LED, round button.
5. **Materials.** Satin dark polymer with fine grain and sparse light scratches; dark gunmetal and bright brushed aluminium (frame, bracket, dial ring, antenna collar) with bright worn edges; black rubber (gear, cord, antenna); emissive cyan LCD under glass in a steel bezel.
6. **Light and camera.** Big soft key from the upper right (backdrop brightest top-right), camera-side lift on the walls, soft short shadows plus a dark contact halo; high three-quarter camera, near-orthographic (v1 fit: azimuth 41.0°, elevation 48.65°, 200 mm).
7. **Backdrop and post.** Mid-grey fine-grained backdrop (luma std ~15 at 1:1), slight grain, no bloom.

### From the original artwork (found this session)

The research agent found the source: ArtStation `VgGQyg`, "DT-03 RADIO DEVICE — 谛听" by AFI_ (2020), made in **Fusion 360 + KeyShot + Photoshop**. Copies in `references/`: `ref_dt03_4k.jpg` (the reference at 3840×2880), `ref_front.jpg` (near-orthographic front view, 9.6 px/mm at 4K: body about 110 × 185 mm), `ref_line_3view.jpg` (Fusion shaded-with-edges render, three views). The 4K crops show: plate edges are **3–5 mm tangent fillets** (double edge lines in the Fusion render), the polymer has a strong bead-blast speckle (~0.2–0.3 mm), wear is speckled light along the fillets, scratches are sparse thin straight lines 5–20 mm long, the lid is a pocket with a filleted rim, screws are domed steel buttons in small dimples.

## Most likely process

A CAD model (Fusion 360: sketches extruded, shelled, booleaned, then constant-radius fillets on every edge, 3–5 mm on the shells, ~1 mm on the panels), rendered in KeyShot with a curvature-driven edge-wear texture and a bead-blast bump, labels as decals, soft studio light on a grey grain backdrop, then Photoshop for the graphics. The moulded look comes from the fillets and the sloped, filleted steps in the CAD section, not from subdivision or shading tricks.

## Techniques to use

Tested by three research agents headless on 5.2.2 (scratchpad `research_A/`, `research_B/`, `research_C/`); `(tested)` = rendered or measured, `(source)` = read only.

- **Primary forms: plan × section loft** (`scripts/hsloft.py`, from agent B, plus my own prototype `scratchpad/proto/loft.py`). Plan outline with a radius per corner, swept through a designed section — foot chamfer, drafted wall, 45–60° slope, 3–5 mm top fillet — capped with flat n-gons. Watertight, 0 non-manifold edges, 2–10 ms per part, ~700 faces per shell (tested). This is Fusion's "sketch → extrude → fillet" in code. Rule: every inset in the section stays below the smallest convex plan radius (outward overhangs below the smallest concave radius), or the offset ring crosses itself. 5.x and 4.4.
- **Shading:** `flatcap` for anything a boolean touches (caps flat, sweep smooth, crisp section stations and sharp plan corners marked sharp: zebra clean after Exact and Manifold) (tested). Analytic per-corner custom normals only on parts no boolean touches (perfect fillets at 8 segments; a boolean corrupts them) (tested).
- **Pockets, grooves, countersinks: profiled cutters** (`section_cutter`, `hs_ring`): the cutter carries the host's rim fillet (1.2 mm) and floor fillet (0.6 mm); the rim arc stops 2° short of flat and rises straight up, so nothing is coplanar (tested). Put each cutter in its **own object in a Collection operand** (overlapping cutters then work in both solvers) (tested). Manifold 8–13 ms, Exact+`use_self` 245–342 ms, Float leaves non-manifold edges (tested). Manifold silently ignores non-manifold operands (text meshes): `remove_doubles` first (tested). Clear material slots after booleans (known v1 trap).
- **No Bevel modifier after booleans.** Clamp Overlap acts on the whole mesh: a 2 mm rim shrank to 1.25 mm with one pocket, 0.16 mm with slots and screw holes (Exact), 0.01 mm (Manifold); with clamp off it overlaps (tested by agents A and B). If a live bevel is needed, agent A's edge-class stack (GN boolean → weighted Bevels with named `edge_weight` attributes → grooves cut after the big bevels → Weighted Normal) works (tested), but the loft makes it unnecessary.
- **Edge wear:** a FACE attribute `fillet` written at loft time for the faces in the section's top-fillet stations (the loft knows them exactly), read by an Attribute node → × speckle noise → lighter albedo, lower roughness. Agent C proved the same idea with Bevel-modifier faces: pixel-exact, convex-only, no noise, free at render time (tested); the shader Bevel node draws double lines, AO doubles, Pointiness and stored Edge Angle smear (tested). Face attributes survive booleans (agent A, tested). Trap: in 5.2 Signed Edge Angle is **positive for convex** edges, opposite to the manual (tested by A and C).
- **Detail parts** (agent B, tested): gear/knurl = trapezoid-tooth outline lofted with a 0.25–0.35 mm chamfer section; stacked roller = toothed and plain discs alternating; screws = circle + domed section, hex or Y-slot cutters as separate objects; engraved text = Text → `new_from_object` → `remove_doubles` → boolean; coiled cord = parallel-transport helix round a path, radius ramped at both ends, NURBS with `bevel_depth`.
- **Polymer material** (agent C + v1 knowledge): base 0.04 linear, roughness 0.42–0.55, bead-blast bump Noise ~4000/m (≈0.25 mm) strength 0.08, distance 0.2 mm (tested), plus v1's two-scale albedo grain; wear on `fillet` faces at 0.4–0.5 of agent C's test strength; scratches from a drawn stroke mask (v1's method; procedural Voronoi read as dashes). Metal: metallic 1, base ~0.75, roughness 0.25–0.35, anisotropy 0.5–0.7 with radial tangent on round parts. Rubber 0.03–0.05, roughness 0.6–0.7 (the gear shows a satin highlight).
- **Light** (agent C, tested + v1 knowledge): keep every big source out of the flat tops' mirror direction. A: key in the mirror direction → tops 107, chamfers 48 (inverted). B: 0.8 m key on the camera side, high + fill at ¼ → tops 38, chamfers 90. The reference sits between (body ~75): set tone by albedo and fill, keep the key off the mirror direction. Separate backdrop key via light linking (v1), backdrop AO for the contact halo (v1).
- **Camera:** v1's landmark fit (azimuth 41.0°, elevation 48.65°, 200 mm, rms 6 px); layout from v1's plan traced on the rectified reference (`experiments/cyber-model/scripts/build.py` `LAYOUT`, 3.6 plan px/mm), cross-checked against `ref_front.jpg`.
- **LCD, decals:** v1's PIL textures (`scripts/make_lcd.py`, `make_decals.py`) as emission under a sharp coat; decals as planes 0.02 mm above the surface, `visible_shadow = False`.
- **Anti-aliasing:** final at 2× (1600×1200 → review crops at 1:1), LCD text drawn at 2× and downsampled.

## Rejected approaches

- **v1's extruded plates with vertical walls and a 0.5 mm flat chamfer** — reads as thin CAD plates; the S-step nearly vanishes (agent A, variant A; v1's 6.7 plateau).
- **Bevel modifier after booleans** — whole-mesh clamp shrinks every rim (see above).
- **Bevel before boolean** — shading smear 19.7° on the tops (agent A).
- **Custom bevel profiles for a rounded chamfer** — 18–46° smears at the S-step (agent A).
- **SubD** — black star on booleaned n-gons (agent A); fine only for uncut small parts, and the loft already gives fillets.
- **SDF grid route** — edges round to a voxel; 0.1 mm voxels = 4.7 M faces, 2.2 GB; rounding by offset wobbles (agent B).
- **GN Mesh Bevel node** — its Miter input explodes the mesh; fine with Miter off, but not needed (agent B).
- **Draft as the main lever** — 3° draft on a 14 mm wall is invisible (agent A); the slope and fillet carry the read.
- **Shader Bevel node / AO / Pointiness for wear** — double lines, doubled bands, smear (agent C).

## Numeric targets

Reference `references/ref_dt03.png`, measured with `scripts/measure.py` (same procedure on the render; from v1):

| Measure | Reference |
|---|---|
| Backdrop TL / TR / BL / BR (luma median) | 96 / 143 / 109 / 115 |
| Subject median / p5 / p95 | 75 / 7 / 92 |
| Subject share under luma 12 | 7.6 % (small quantity: judge by ratio, ±30 %) |
| LCD median RGB | 131, 186, 192 |
| Backdrop grain std (1:1) | 14–15 (ratio ±20 %) |
| Plate tops sRGB | 70–85; sloped camera-facing steps 90–105 (lighter than tops) |
| Fillet size on shells | 3–5 mm (4K crops); panels ~1 mm |
| Body | ~110 × 185 mm plan, ~25–30 mm total thickness (Fusion views; estimate) |
| Camera | azimuth 41.0°, elevation 48.65°, 200 mm |

Silhouette: `assets/ref_mask.png`, hand-traced (±8 px), subject share 35 %. Gate with `tools/silhouette.py`; IoU under 0.75 means a gross proportion error.

## Open questions (first test renders settle these)

1. Does the lofted slope + fillet read as moulded under the reference light at hero scale (not only in close-ups)?
2. Shell heights: body 13–15 mm, shield +7–9 mm with a 45–60° slope — check the S-step against the reference crop.
3. Does `fillet`-face wear read at 1600 px without looking like painted outlines?
4. Can the tops sit at 70–85 with walls at 90–105 without the key in the mirror direction?

## Sources

Read this session (details in each agent's report; scratchpad `research_A/B/C`):

- https://www.artstation.com/projects/VgGQyg.json (via r.jina.ai) — original artwork, software list, other views
- https://www.artstation.com/projects/g2oWNE.json — ZIC edition (low end views)
- https://api.fxtwitter.com/ArtStationHQ/status/1312195916816818180
- https://www.pinterest.com/pin/670121619549223771/ (and …769, …770, …772)
- https://manual.keyshot.com/manual/textures/texture-types/3d-textures/curvature/
- https://manual.keyshot.com/manual/models-tab/rounded-edges/
- https://www.photographystudio.blog/black-on-black-how-to-light-dark-products-so-they-actually-show-up/
- https://80.lv/articles/procedural-micro-scratches-shader-made-with-blender-cycles
- https://hardops-manual.readthedocs.io/en/latest/csharpen/ , …/bwidth/ , …/subdivision/
- Blender Bros, The Hard Surface E-book (PDF): https://s3.amazonaws.com/kajabi-storefronts-production/sites/173317/themes/3514268/downloads/v3FxcT4WSKylD9bD5A3h_The_Hard_Surface_E-book.pdf
- https://doc.plasticity.xyz/blender/how-to-use , https://doc.plasticity.xyz/solid/fillet-shell
- https://www.chrisnicoll.net/2019/04/shading-sharp-edges-in-cycles-with-the-bevel-node/
- https://devtalk.blender.org/t/manifold-boolean-feedback/40150
- https://groups.google.com/g/openvdb-forum/c/xskbPzqUCrU
- https://code.blender.org/2021/09/procedural-curves-in-3-0-and-beyond/
- Local: `reference/manual` (Bevel, Weighted Normal, Smooth by Angle, Booleans, Mesh Bevel, Edge Angle, Bevel shader), `reference/dev-docs` release notes 4.5 (Manifold, free normals), 5.1, 5.2 (Mesh Bevel node), `reference/api-dump-5.2`
- `knowledge/` (modelling, geometry, cycles, shader-nodes, decisions/cyber-model), `experiments/cyber-model/`

Snippets only / blocked: projects.blender.org #132292, #133978, #132071, T57691 (clamp applies to all bevelled edges); polycount FrankPolygon threads (403); blenderartists.net (DNS failure); artstation.com HTML (Cloudflare). Found nothing: 燕鼎 DT-03 on Zcool/Huaban/Behance; any AFI breakdown or wireframe beyond the line render; 80.lv sci-fi radio breakdowns; any public bpy recipe for these workflows.
