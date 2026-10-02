# plotter-forms — research

No reference images. This research fixes the formulas, the classic look of each family, and the hidden-line method. Two Sonnet agents (web, with numeric checks); builder Fable 5.1.

## Read of the brief

"Interesting 3D volumetric shapes expressed in wireframe-esque graphics", as SVG strokes, in many variations. The first series gave two mechanisms: contour lines of a formula on a surface, and the parameter lines of a surface given by a formula. Every form here is one of those, or a family of curves from a formula.

## Most likely process (for the classic pictures)

Each family has a canonical picture made the same way: sample a formula, project, remove hidden lines. Harold Craft's 1970 pulsar plot ("Unknown Pleasures") was a hidden-line plot; Hopf pictures are fibres over latitude circles; minimal-surface plates are parameter-line wireframes.

## Techniques to use

- **Formula compiler.** Formula strings → Math nodes (`plot_kit.Env`), so a form is three strings and a few sliders. All forms stay live Geometry Nodes. `5.x`
- **Hopf fibration.** Fibre over (a,b,c) on S²: z0 = sqrt((1+c)/2) e^{it}, z1 = sqrt((1−c)/2) e^{i(t−φ)}, φ = atan2(b,a); point (Re z0, Im z0, Re z1, Im z1); stereographic (x1,x2,x3)/(1−x4). Latitude circles → nested tori of Villarceau circles; a longitude arc → partial tori. The Wikipedia quaternion form did not check against the map; use this one. https://en.wikipedia.org/wiki/Hopf_fibration, https://nilesjohnson.net/hopf.html
- **Spherical harmonics.** P_m^m ∝ (1−x²)^{m/2}; (l−m) P_l^m = (2l−1) x P_{l−1}^m − (l+m−1) P_{l−2}^m; times cos(mφ). Zonal: parallels; sectoral: orange slices; tesseral: checkerboard. Unrolled in nodes to degree 12, normalised by the field's own max. https://en.wikipedia.org/wiki/Associated_Legendre_polynomials, https://en.wikipedia.org/wiki/Spherical_harmonics
- **Dipole field lines.** r = L sin²θ; lines spaced evenly in 1/L carry equal flux. https://en.wikipedia.org/wiki/L-shell
- **Minimal surfaces** (H = 0 checked numerically by the agent): associate family x = sin a cosh v cos u + cos a sinh v sin u, y = sin a cosh v sin u − cos a sinh v cos u, z = v sin a + u cos a (a = 90°: catenoid, 0°: helicoid) https://en.wikipedia.org/wiki/Catenoid; Enneper order n (x = r cos θ − r^{2n+1}/(2n+1) cos((2n+1)θ), y = −r sin θ − r^{2n+1}/(2n+1) sin((2n+1)θ), z = 2r^{n+1}/(n+1) cos((n+1)θ)) https://en.wikipedia.org/wiki/Enneper_surface; Scherk z = ln(cos x / cos y) https://en.wikipedia.org/wiki/Scherk_surface; Henneberg https://mathworld.wolfram.com/HennebergsMinimalSurface.html; Catalan https://en.wikipedia.org/wiki/Catalan%27s_minimal_surface; Richmond https://en.wikipedia.org/wiki/Richmond_surface.
- **Triply periodic level sets.** Gyroid sin x cos y + sin y cos z + sin z cos x; Schwarz P cos x + cos y + cos z; D; Neovius. Meshed with Volume Cube → Volume to Mesh, then sliced. https://en.wikipedia.org/wiki/Gyroid, https://en.wikipedia.org/wiki/Schwarz_minimal_surface
- **Classic surfaces** for variety: Dini, Kuen (https://mathworld.wolfram.com/DinisSurface.html, https://mathworld.wolfram.com/KuenSurface.html), Klein figure-8 (https://en.wikipedia.org/wiki/Klein_bottle), Möbius, Boy (Apéry; weak source, seams checked), seashell (https://en.wikipedia.org/wiki/Seashell_surface), monkey saddle.
- **Ridgelines.** Stacked profiles, each hiding those behind; signal in the central part, flat edges; fewer lines read better (about 40–90). https://en.wikipedia.org/wiki/Unknown_Pleasures, https://dieghernan.github.io/202205_Unknown-pleasures-R/
- **Gravity well.** Flamm's paraboloid w = 2 sqrt(rs (r − rs)), or the sum of −m/sqrt(r² + ε) for several masses. https://en.wikipedia.org/wiki/Flamm%27s_paraboloid
- **Hidden-line removal.** One ray per stroke sample toward the camera against a BVH of the surface (`mathutils.bvhtree`, 0.5 µs per ray on 80k triangles, measured). This is fogleman/ln's method (https://github.com/fogleman/ln). Lines lie on their own surface, so a hit only counts beyond a tolerance (PENumbra's depth tolerance, https://github.com/de-nsly/PENumbra); the tolerance must exceed the facet sagitta (5.6e-5 on a subdiv-6 unit sphere, measured). Near the silhouette hits are unstable: bridge short gaps, drop short runs. The surface is triangulated once in the node group, so lines and occluder share triangles.
- **Outline.** Zero set of (vertex normal · view) per triangle, chained (Hertzmann and Zorin, https://mrl.cs.nyu.edu/publications/illustrating-smooth/hertzmann-zorin.pdf). Its visibility is unreliable at the contour itself, so the outline is pushed outward along the normal before the ray test. Non-orientable surfaces get false outlines at the normal flip: outline off for those.

- **Blots (added after round 3).** Plotter flow-field work keeps lines apart with a minimum-separation check on a grid or KD-tree while lines grow (https://www.csun.io/2021/12/29/plotting-old-pictures.html, https://nummy.blog/pen-plotter/generative-art/python/creative-coding/2026/02/06/three-months-with-a-pen-plotter.html). Our lines are not grown, so the same check runs afterwards: strokes are laid on a grid in priority order and a stroke is cut where it runs beside earlier ink, closer than the pen, at a shallow angle. Crossings (short runs, steep angles) stay.
- **Depth for see-through plots (added after round 3).** Knot diagrams break the under-strand with a gap at each crossing (https://prideout.net/blog/svg_knots/, https://ctan.math.illinois.edu/graphics/pgf/contrib/spath3/knots.pdf). Same here: project, find crossings, read over/under from depth, cut the far stroke.

## Rejected approaches

- vpype `occult`: 2D only, hides by closed polygons in stacking order (https://github.com/LoicGoulefert/occult). Our lines are not polygons.
- Exact segment-triangle splitting (Trammell Hudson's hiddenwire, https://trmm.net/Hidden_Wireframe/): exact but slow in Python and built for mesh edges, not curves on smooth surfaces.
- Blender Line Art: a Grease Pencil modifier; its SVG export fails headless (`plotter-blend`).
- Baking fields in Python (scipy-style harmonics): loses the live sliders.
- Costa surface: needs Weierstrass elliptic functions; left out.

## Numeric targets

No reference to measure. Plot-quality targets, checked from the SVG stats: no stroke off the page; no visible fragment under 1 mm; hidden-line plots show no line through a surface; pen ≥ 0.3 mm with line gaps mostly ≥ pen width.

## Open questions

- Do isolines on a trimmed or self-intersecting surface (Enneper, Klein) hide correctly with one tolerance?
- Is Volume to Mesh smooth enough at 96³ for clean slices?
- Does a formula field survive two geometry contexts (surface and dot grid) without recompiling?

## Sources

Read this session (by the agents): the links above, plus https://en.wikipedia.org/wiki/Stereographic_projection, https://en.wikipedia.org/wiki/Magnetic_dipole, https://www.pbr-book.org/3ed-2018/Shapes/Managing_Rounding_Error, https://www.redblobgames.com/x/2219-hidden-line-removal/, https://trmm.net/Plotter-Vision/, https://docs.blender.org/manual/en/latest/grease_pencil/modifiers/generate/line_art.html, https://www.labri.fr/perso/pbenard/publications/contours/contours.pdf (abstract only), https://arxiv.org/abs/2111.06006 (abstract only), https://blog.engora.com/2021/06/unknown-pleasures-pulsars-pop-and.html. Local: `reference/api-docs-5.2/mathutils.bvhtree.txt` (`FromPolygons`, `ray_cast` returns four Nones on a miss).

Could not open: MathWorld Catalan, Richmond, Enneper and Boy pages (404); Paul Bourke klein and shell; Wikipedia "Associate family". Unverified: Kuen's u range (±4.5), ridgeline counts in Craft's original, sheet thresholds for the periodic surfaces.
