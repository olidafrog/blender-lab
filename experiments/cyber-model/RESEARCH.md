# cyber-model — research

Read and numeric sections are the lead agent's own analysis of the reference. Technique sections come from two Sonnet research subagents (A: modelling technique, B: materials/lighting); claims marked *(test)* were run headless on Blender 5.2.2 by agent A, and claims the lead re-checked are marked *(lead-verified)*.

## Read of the reference

`references/ref_radio.jpg` is a finished 3D render (a portfolio piece, "DT-03 Multifunction Radio Device", credited AFI). Effects, in the order they matter to the look:

1. **Form language — layered plates.** The body is not one moulded shape. It is a stack of separate chamfered plates: a Z/L-shaped top shield plate wrapping the LCD pocket and running down past the "DT-03" battery lid; a lower, flatter left wing plate carrying the switches; a lower-left battery block with a thin silver frame; a bottom end cap with a vent window and a silver pivot cylinder. Plates are separated by shallow steps and groove lines rather than blended. Every edge carries a small bevel that catches light as a hairline. This is the hard-surface look.
2. **Detail hierarchy.** Primary: the plates and the LCD pocket. Secondary: antenna base (two parallel cylinders and a knurled silver collar), thumb rack, dial and gear on the left, coiled cord with jack and plug, round button, selector knob, ON/OFF slide switch, red LED. Tertiary: screws, tiny labels, arrow marks, vents, "DT-03" engraving, the logo decal, edge scratches.
3. **Materials.** Satin dark-grey polymer body (not black: sRGB ~80–90, linear ~0.08–0.10 under a big soft key), brushed and bright steel (dial ring, bezel, bracket, screws, collar), dark green-grey rubberised side pieces (lower frame), matte black rubber (cord, gear, knob), and a cyan backlit LCD with dark text and a dark bar UI. Scratches and edge wear read as light fine lines on the polymer, not paint chips.
4. **Light.** One large soft key from the upper right of frame (the backdrop is brightest top-right: sRGB ~145 vs ~96 at top-left) plus generous fill. Shadows are soft and short. Chamfers on the lit side show a bright thin line; the body has real blacks: about 7 % of subject pixels are under sRGB 12 (creases, foot of each step, gaps), so do not lift the blacks. (Correction from the Opus advisor, verified with `scripts/measure.py`: an earlier draft said the body never goes below 55.)
5. **Camera.** A high three-quarter view: measured by rectifying the reference, the device long axis is rotated about 41° from the image vertical and the camera looks down at about 50° elevation (orthographic estimate). Moderate lens (perspective is mild: rectification with a single homography-like affine straightens all edges).
6. **Backdrop.** A mid-grey fine-grained textured surface (fabric or coarse paper), luma std ~14 at 1:1 in a flat patch. Not smooth.
7. **Post.** Slight grain, mild sharpening, no bloom on the LCD beyond its own emission.

## Plan-view rectification (for layout)

`assets/ref_plan_rectified.png` is the reference warped to a top-down plan (affine: elevation 50°, azimuth 41°, 1.3× scale, centre (430,300)). Edges become vertical/horizontal and the LCD becomes level, so layout can be read off it in plan px. Scale used: 3.6 plan px per mm (assumes the LCD bezel is about 65 × 36 mm). Device origin (LCD-centre area) at plan (500, 480); +x right, +y up.

Layout landmarks (plan px, then mm from origin):

| Part | Plan px | Size |
|---|---|---|
| Chassis outline | x 300–700, y 148–815 | 111 × 185 mm |
| LCD bezel outer | x 357–590, y 200–330 | 65 × 36 mm, corner r ~6 mm |
| LCD glass | x 370–575, y 212–318 | 57 × 29 mm |
| Antenna pod L (base) | x 367–430, y 113–195 | dia 17, length 23 mm |
| Antenna pod R | x 430–489, y 95–195 | dia 16, length 28 mm |
| Antenna | base (395,100), leans ~8° left going up | dia 12, length ~150 mm, silver collar 14 mm long |
| Cord jack | (650–720, 142–190) | dia 12, length 20 mm |
| Cord coil | x 740–780, y 190–540 | outer dia ~15, wire ~2.6, ~16 turns |
| Cord plug (capsule) | (690–750, 590–690) | 15 × 27 mm |
| Thumb rack | x 635–680, y 200–320 | ~9 ribs |
| Round button | (660,348) | dia 9 mm |
| Red LED | (413,358) | dia 5 mm |
| Selector knob | (377,370) | dia 12 mm + lever |
| ON/OFF slide | x 360–400, y 420–447 | 11 × 7 mm |
| Dial (silver ring) | centre (277,310) | dia 28 (ring), 19.5 (face), 13 (cap) |
| Gear wheel | centre (263,323) | dia 34, ~24 teeth, dark |
| Lid ("DT-03") | x 552–675, y 392–535 | 34 × 40 mm |
| Screw boss (left) | (278,460) | dia 12 mm, screw 5.5 |
| Bottom vent window | x 490–600, y 720–770 | 6 small slots |
| Silver pivot cylinder (bottom right) | x 610–690, y 730–790 | |
| Battery block | x 300–545, y 600–820 | lower than the shield plate |

Body heights (estimated from shadow and step visibility): chassis 0–14 mm; shield plate +5 mm; lid recess −1.5 mm; battery block top at +6 mm; wing plate at +1 mm; LCD bezel +2.5 mm above the pocket floor; pods sit on the chassis top at +9 mm axis height.

## Numeric targets (measured on the reference, region medians)

| Region | sRGB median | Linear |
|---|---|---|
| Backdrop top-left | 96,96,101 | 0.117 |
| Backdrop top-right | 143,142,148 | 0.275 |
| Backdrop bottom-left | 109,108,112 | 0.153 |
| Backdrop bottom-right | 115,115,120 | 0.171 |
| Body plates (dark polymer) | 78–89 | 0.077–0.10 |
| Cord | 86 | 0.09 |
| Steel plate (dial bracket) | 105 (p95 203) | 0.14 |
| LCD face | 131,186,192 | 0.23, 0.49, 0.53 |
| Backdrop grain (luma std, 1:1) | 14–15 on mean 109 | |
| Subject median luma / p5 / share under 12 | 75 / 7 / 7.6 % | (`scripts/measure.py`, same procedure on the render) |
| Camera (fitted from 12 landmarks, `scripts/fit_camera.py`) | azimuth 41.0°, elevation 48.65°, lens ≥ 200 mm (near-orthographic), rms 6.3 px at 736 px | |
| Chamfer shoulders | soft gradient about 2–3 px at 736 px (about 5–7 px at 1600) on the lit top rim, a black crease at the foot of each step | (advisor, measured on 3–6× crops) |

Backdrop gradient: brightest top-right, darker top-left, mid bottom. Body/backdrop contrast is low (the body is only ~25 levels darker than the backdrop): the look is a soft high-key render of dark grey plastic, not black on grey.

## Most likely process

The piece is a Substance-era hard-surface render: forms built as CAD-like separate chamfered parts (no subdivision), textured with curvature-driven wear and fine-grain roughness/height noise, lit as a soft studio shot. No breakdown of this exact piece could be found (ArtStation pages returned 403 to every fetch; a search snippet says "DT-03 Radio Device, AFI, inspired by Joshua Cotter's MR 3000" — unverified). A comparable breakdown (80.lv, "sci-fi radio device in Plasticity + Blender") uses the same pipeline: CAD-style modelling, seam lines for part breaks, fine-grain noise on the height map "to avoid flat plastic/rubber", tiny LED-pixel LCD detail, minimal wear.

Build in Blender as: separate plates and parts from 2D outlines (extrude), Bevel modifier (angle-limited, 2–3 segments, Harden Normals) + Weighted Normal for clean shading, boolean-cut pockets for the LCD and lid, a shader-side Bevel-node edge-wear mask, a procedural helix cord, and a PIL-drawn emission texture for the LCD.

## Techniques to use (look side — from the materials/lighting research agent, Sonnet)

- **Polymer body:** Principled, base colour ~0.03–0.05 linear albedo (the reference reads ~0.08–0.10 lit by a big soft key, so albedo stays near 0.04), roughness 0.35–0.5 (satin), Specular IOR Level 0.5, very small high-frequency bump (under 0.2 mm on a 0.19 m object; local rule).
- **Edge wear / scratches:** Bevel node (radius ~0.5–1.5 mm on a 0.2 m object, samples 8) → Dot with Geometry True Normal → Map Range with close stops → × Noise/Voronoi patch mask → lighter base colour + higher roughness (light scuffs on black plastic, not chipped paint). Scratches: Voronoi Distance-to-Edge, stretched, under a sparse noise mask into roughness and a tiny bump; keep roughness under ~0.15 for the edge network. Bevel node is Cycles-only and costs ~20 % render time; invalid with OSL on OptiX (Windows). Pointiness depends on mesh density; do not use. Needs: 4.4 and 5.x.
- **Brushed steel (dial, bezel, bracket, collar):** Metallic 1, roughness 0.2–0.35, anisotropy ~0.5–0.8; on round parts drive the tangent with a Tangent node in Radial mode on the part's axis; streaks from a stretched Noise into a low bump. Principled Anisotropic Rotation is 90° off Glossy BSDF (add 0.25). The Voronoi hash changed in 5.0, so scratch patterns differ between 4.4 and 5.x.
- **Dark rubber (cord, gear, knob, frame):** roughness 0.6–0.9, base ~0.03–0.06 with a green-grey tint for the frame parts; fine bump. (Tint is our judgement; sources gave no rubber numbers.)
- **LCD:** positive-mode display, emission = backlight × (1 − ink). Draw at 4× with PIL and downsample, add a faint pixel grid and vignette, Colour (sRGB) image texture ≥ 2048 px into Principled Emission (strength 1–3) under a sharp Coat (weight 1, roughness ~0.03); the 5.2 manual says emission sits under the coat "for emissive displays". Avoid real glass transmission over emission (noise, dims text).
- **Coiled cord:** compute in Python. Sample the path with parallel-transport frames, offset by R·(cosθ·N + sinθ·B), write one poly spline to a Curve with `bevel_depth` = wire radius, `bevel_resolution` 2–3, at least 16 points per turn. Ramp R to 0 with smoothstep at both ends so straight leads are part of the same tube. Estimated from the reference: ~22–25 turns, pitch ~1.1 × wire diameter, coil radius 2–2.5 × wire radius (unverified). Add low-frequency noise to R and θ for kinks. (`hs_kit.helix_cord`.)
- **Knurl, gear, screws, vents, text:** knurl and gear as a zig-zag/trapezoid polygon in bmesh, extruded (`hs_kit.knurled_cylinder`, `hs_kit.gear`); screws as one head instanced by linked copies; vents as slot cutters with an Array + Boolean; tiny print as a PIL-made alpha decal about 0.05 mm above the panel, not a text object.
- **Lighting:** big softbox key, 1.2–1.5 m at 45–55° elevation, about 40° off the camera axis, a fill 3× larger at ¼–⅓ of the key, a thin grazing edge strip; black flags for dark products; a 14° low rake on the camera side to glint bevels. (Sources gave few numbers; these are starting points to be checked against the reference.)
- **View transform:** Khronos PBR Neutral (4.2+) or Standard; AgX dulls the cyan LCD. Check dark values are not crushed.
- **Render settings:** Cycles, OIDN denoise (Albedo + Normal, Accurate prefilter), adaptive threshold 0.01, clamp indirect 3–5, Filter Glossy ≤ 0.3 for chamfer lines, pixel filter width ~1.0–1.2 for crisp text, render at 2× and downsample.
- **5.x traps:** compositor API changed (`compositing_node_group`, several nodes removed; see `knowledge/gotchas/api-changes.md`); guard Boolean solver (`MANIFOLD` exists on 4.5+/5.x) and `use_nodes` differences with try/except.


## Techniques to use (modelling side — from the modelling research agent, Sonnet)

- **Workflow: no subdivision.** Sub-d needs support loops for every panel line; the radio is flat plates with constant-width chamfers. Use one Bevel modifier per plate and one Exact boolean per plate for grooves, vents and recesses. Sources: propgon, garagefarm hard-surface guides; the aircraft-panel-line thread on Blender Artists says sub-d "causes weird shapes and loops".
- **Panel lines, in order of preference:** (1) separate plates with a real 0.4–0.8 mm gap over a darker underlay (cheapest, shades cleanly, matches the reference's layered look); (2) join all thin cutters into one object, overshoot the surface by ≥ 1 mm, one Exact boolean, then Bevel on Angle *(test: stayed manifold)*; (3) bmesh `inset_region` with negative depth for shallow recesses. Floating geometry is fine in a Cycles-only render.
- **Bevel modifier (same property names on 4.4 and 5.2):** `offset_type='OFFSET'`, `limit_method='ANGLE'`, `angle_limit=30°`, `segments=2` (1 for tiny parts, 3 for the hero hull; avoid odd counts that give corner triangles), `use_clamp_overlap=True`, `loop_slide=True`, `miter_outer='MITER_SHARP'`, `harden_normals=True`. Build in metres, never scale objects (uneven scale gives uneven bevels). Width tiers, estimated and unverified: primary chamfer 1.5–2.5 mm, plate edges 0.8–1.2 mm, small parts 0.3–0.5 mm. The default 0.1 m is huge for a 0.2 m radio.
- **Normals — measured *(test)* on a bevelled box, max gap between corner normal and face normal:** no fix 0.256; Weighted Normal (keep sharp) 0.022; Harden Normals 0.000; Harden + `face_strength_mode='FSTR_AFFECTED'` + Weighted Normal 0.0001. **Use Harden Normals. Skip Weighted Normal.** Auto smooth is gone since 4.1; use `bpy.ops.object.shade_auto_smooth(angle=…)` (4.2+, adds a Smooth by Angle modifier pinned last; worked headless with `--factory-startup`) *(test)*. **Trap *(test)*:** keep the stack live (Boolean, Bevel-harden, Smooth by Angle 30°). On a mesh baked with `new_from_object`, re-smoothing raised the error to 0.67, probably because custom normals are stored relative to the automatic normals (unverified). Set sharp/smooth flags before beveling, do not re-smooth after baking.
- **Boolean solver *(lead-verified against the 5.2 API dump)*:** `EXACT` works on every version. 4.4 has `FAST`; 5.0 renamed it `FLOAT`; `MANIFOLD` is 4.5+/5.x and needs manifold operands. A flush (coplanar) cutter broke FLOAT, EXACT and MANIFOLD were correct *(test)*, so always overshoot. Forty slots: 40 stacked Exact modifiers 374 ms, one joined cutter 31 ms, MANIFOLD ~2 ms *(test)*. Join cutters first.
- **bmesh.ops signatures *(test)*:** `bevel` defaults to `segments=0, profile=0, affect='VERTICES'`, so set all three; a rounded rectangle is a quad with `affect='VERTICES', segments=6, profile=0.5`. `inset_region` returns `{'faces'}`. `spin` applies `dvec` per step, not in total. `create_cone` with equal radii is a cylinder. `create_grid(size)` uses size as half-extent.
- **Shading traps:** N-gon planar caps are fine; a bevel wider than about a third of the narrowest cap makes the cap overlap itself (local rule, `geometry.md`); Cycles shadow terminator on faceted curved parts: raise Geometry Offset; the Cycles Bevel *shader* node costs ~20 % render time, use it for tiny parts and the wear mask. 5.1 fixed per-corner normals with mixed flat/smooth faces (PR !153836); 4.4 may still show it (test on the Windows machine if it matters).
- **Detail hierarchy:** primary mass and silhouette, secondary panel breaks/bezel/dial/antenna base, tertiary screws/vents/buttons/text. A functionless panel is a named mistake (garagefarm).
- **Recipes:** straight knurl = ring of 2N points alternating R and R−d, N 48–72, extruded; gear = 2D polygon with 24–36 trapezoid teeth, extrude 4–6 mm, bevel 0.3 mm (no source had involute maths); screw = 16–24 segment head with a cross-slot boolean, built once and reused; vents = joined slot cutters + one Exact boolean + bevel; LCD bezel = rounded-rectangle N-gon extruded then `inset_region(thickness≈0.003, depth≈−0.002)`; cord = poly-spline helix around a Bezier path with `bevel_depth≈0.0022`, `bevel_resolution=3` (1401 points, 22 turns, radius 8 mm: 14 k vertices) *(test)*.
- **Checks:** clay render plus a white mirror material under an HDRI (metallic 1, roughness 0); Face Orientation overlay; the numeric normal-error measure above.

## Rejected approaches

- **Subdivision modelling with support loops:** panel lines multiply loops; scripting the loops is fragile. Rejected for this subject.
- **Weighted Normal modifier:** measured worse than Harden Normals and adds an ordering trap *(test)*.
- **Mesh Bevel geometry node (5.2):** no clamp, no loop slide, no hardening, manifold edges only (PR !158151). Keep the modifier.
- **SDF-fillet booleans:** 5.x only, and unreliable in this lab (`knowledge/gotchas/geometry.md`).
- **Pointiness for edge wear:** depends on mesh density; use the Bevel-node mask.
- **Real glass over the LCD emission:** noise, dims text; use a Coat.
- **Text objects for tiny print:** PIL-drawn alpha decals instead. Text objects only for large raised text.
- **GUI add-ons (HardOps, BoxCutter):** cannot run headless; their technique (boolean cutters + bevel) is what we script.

## Open questions (a test render must settle)

1. Does the Bevel-node wear mask read as "worn edge" at 736–1600 px, or does it need a wider radius than 1 mm?
2. Bevel widths: 0.8 mm vs 1.5 mm plate edges. Which gives the reference's thin bright chamfer hairline at the final scale?
3. Perspective: which lens (50–85 mm) matches the reference's mild convergence? Settle by overlay against the reference.
4. Backdrop grain: procedural noise bump on the plane vs an image texture. Which survives a 2× render and downsample?
5. Is a Harden-Normals-only stack clean on the rounded plate corners (arcs at 18° steps sit under the 30° angle limit)?

## Plan for the first build

Mechanism, per effect (build the findings first, do not save them for later):
1. **Plan-view gate.** Render an orthographic top-down of the model with the same framing as `assets/ref_plan_rectified.png` (950 px, 3.6 px/mm, origin (500,480)). Compare to the plan by overlay before touching the hero look. This settles layout in one step, and it is the fast check for proportions.
2. **Plates from outlines** (`hs_kit.extrude_outline`), stacked with gaps, each with Bevel(harden) + Smooth by Angle.
3. **Boolean cutters** joined per plate for the LCD pocket, lid recess, vents.
4. **Parts:** pods, antenna, dial and gear (`hs_kit.gear`), thumb rack, buttons, screws, ON/OFF slide, coil cord (`hs_kit.helix_cord`).
5. **Materials:** one group node per material (`tools/nodes.py`): Polymer (with Bevel-node wear + micro bump), Steel (anisotropic), Rubber, LCD, Backdrop.
6. **Light:** one big softbox key at the upper right (camera space), big fill, edge strip; Khronos PBR Neutral or Standard; check against the backdrop gradient.
7. **Correctness pass before round 1:** clay override, mirror override, plan-view overlay, exposure median vs the targets above.

## Sources

Two Sonnet research subagents read the pages below this session (A: modelling technique, B: materials and lighting). Local copies of the Blender manual, release notes and API dumps in `reference/` were also read.

Modelling side — useful:
- https://propgon.com/en/hard-surface-modeling-blender-game-art-guide/
- https://garagefarm.net/blog/hard-surface-modeling-in-blender
- https://hardops-manual.readthedocs.io/en/latest/subdivision/
- https://davidmkelly.com/blender-non-destructive-panel-lines/
- https://blenderartists.org/t/how-to-cut-grooves-panel-lines-in-an-aircraft/1180933
- https://blenderartists.org/t/boolean-transfer-bevel-weights-or-other-method/1292102
- https://blenderartists.org/t/uniform-bevel-width-across-all-edges/624688
- https://blenderartists.org/t/floating-geometry-on-blender/457761
- https://artisticrender.com/boolean-modifier-problems-and-how-to-solve-them/
- https://3dskillup.art/mastering-bevels-in-blender/
- https://3dskillup.art/how-to-fix-shading-artifacts-on-curved-surfaces-in-blender/
- https://marmoset.co/posts/revolutionize-your-3d-workflow-with-toolbags-bevel-shader/
- https://simmer3d.com/2020/07/23/knurl-mesh-in-blender/
- https://en.wikipedia.org/wiki/Knurling
- https://developer.blender.org/docs/release_notes/4.1/modeling/
- https://developer.blender.org/docs/features/interface/matcaps/
- https://projects.blender.org/api/v1/repos/blender/blender/issues/133978 , /issues/132071 , /issues/140590 , /pulls/153836 , /pulls/158151

Modelling side — partly useful: https://80.lv/articles/hard-surface-modeling-tips-and-tricks, https://tryskilly.app/learn/how-to-add-bevel-modifier-blender/, https://note.com/kitaniosam/n/nb8d239e8fc52?hl=en, https://artisticrender.com/how-to-bevel-in-blender-using-the-tool-and-modifier/, https://gachoki.com/how-to-fix-bevel-overlap-issue-in-blender/, https://victoire.online/blog/blender-shading-glitches-causes-and, https://github.com/JacquesDiringer/Procedural_hardsurface (no recipe).

Modelling side — found nothing or blocked: polycount (403), cgcookie (403), blenderguru (404), code.blender.org, projects.blender.org HTML pages (403), docs.blender.org online pages (navigation only; local copy used), Stack Exchange (no results from the search tool at all), no tested public bpy recipes for procedural hard-surface.

Materials and lighting side — useful:
- https://80.lv/articles/creating-realistic-sci-fi-radio-device-using-plasticity-blender
- https://80.lv/articles/breakdown-how-to-create-a-hard-surface-philips-radio-with-zbrush-substance-3d
- https://www.texturly.com/blog/beyond-the-default-shader-a-guide-to-photorealistic-plastic-rendering
- https://artisticrender.com/how-to-create-an-aluminum-material-in-blender/
- https://odederell3d.blog/2018/06/09/cycles-tangent-node-anisotropic-reflection/
- https://blenderartists.org/t/why-do-i-get-edge-masks-by-dot-producting-bevel-nodes-and-geometry-normal/1494877
- https://blenderartists.org/t/a-better-procedural-pointiness-edge-detection-in-cycles/1283892
- https://blenderartists.org/t/worn-scratched-edges-on-metal-what-is-the-best-method/1531106
- https://3dskillup.art/mastering-bevels-in-blender/
- https://modelviewer.dev/examples/tone-mapping
- https://www.photographystudio.blog/black-on-black-how-to-light-dark-products-so-they-actually-show-up/
- https://b3d.interplanety.org/en/making-spring-by-blender-geometry-nodes/
- https://github.com/xynium/Blender-Gear/blob/master/Add_Mesh_Gear.py
- https://github.com/oblivion8282-1337/LCD-Shader-Blender
- https://gachoki.com/how-to-eliminate-noise-grain-fireflies-from-renders-in-blender/
- https://developer.blender.org/docs/release_notes/5.0/rendering/

Materials and lighting side — found nothing or blocked: ArtStation pages for DT-03 and the Cotter MR 3000 (403, so no breakdown of the exact piece exists in what we could read), zhujinyi.com and 100sheep.art project pages (403/404), Blender issue tracker HTML (#123514, #120968), polycount, Medium, neilblevins.com.

Searches for a breakdown of this exact piece ("DT-03", "AFI", 谛听 / 燕鼎) found nothing readable.
