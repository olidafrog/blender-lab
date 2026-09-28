# clouds — research

## Read of the reference

In order of how much they matter to the look:

1. **Billow structure (all refs).** Cauliflower lobes at several scales: big lobes (~1/3 cloud width), lobes on lobes, and fine "popcorn" puffs at the edge (ref 02 has the finest). Each lobe has a crisp silhouette and a soft, few-pixel falloff. This is the single most important thing — a smooth blob or noise fog never reads as cloud.
2. **Multiple scattering brightness.** Lit sides are near-white (refs 04, 05: 204–238 sRGB); shadowed crevices stay light and coloured, not black. A single-scatter render looks "dirty/smoky".
3. **Self-shadowing between lobes.** Each lobe shades the one behind it — the soft grey/violet undersides of refs 02 and 04 are shadow from lobes above, filled by sky.
4. **Dark base / bright top** (refs 03, 04). Optical depth: a thick cloud reflects most light up, so its base is grey (ref 04 base 66,74,82 vs top 238).
5. **Coloured clouds (refs 01, 02).** Pink with deeper, more saturated pink in the core and violet in shadow (ref 02 right side 148,101,135). Deeper = more saturated: the colour comes from a per-channel albedo below 1, compounded over many bounces — not a tint on top.
6. **Sky fill colour.** Shadow sides take the sky colour (ref 02: violet = pink albedo × blue sky; ref 03: blue-grey shadow).
7. **Emitters inside the volume (refs 01, 02, 05).** A neon ring/rod: sharp and hot where it is outside or near the surface; where it passes inside, it disappears into a soft pink glow whose spread ≈ its depth below the surface. Ref 05: lava lights the plume base red, fading upward within ~1 lobe.
8. **Silver lining** (ref 04, backlit edges): thin edges glow when the sun is behind. Needs a forward-peaked phase function.
9. **Camera/post.** Refs 01 and 02 have film grain and a slightly lifted, low-contrast grade; ref 01 is a photo (smoke bomb) with a comped glow; ref 02 is a 3D render (VDB-style).

## Most likely process

Refs 03–05 are photographs. Ref 02 is a 3D volumetric render (VDB cloud, emissive rod, grain added). Ref 01 is most likely a coloured smoke plume photographed in a quarry with the ring added in post, though it could be a render on a photo plate. For us the process is the same for all: **a procedural density grid built in geometry nodes (lobes of lobes → smooth field → billow noise), rendered in Cycles with a Mie phase function, near-1 albedo and many volume bounces, under a sun + physical sky; emitters are real emissive meshes inside the volume.**

## Techniques to use

| Effect | Blender approach | Version | Source |
|---|---|---|---|
| Lobes of lobes | Seed points in Python (tiers: big lobes, lobes on their upper surface, puffs) with a `radius` attribute → GN **Points to Volume** (fills spheres) → **Grid Dilate & Erode** → **Grid Mean** (smooth union) | 5.1+ | code.blender.org volume-grids post; 5.0/5.1 GN release notes |
| Billows / edge detail | Billow noise (1 − Voronoi F1, 2 octaves + Noise) added to the smooth field, then a Map Range threshold with a narrow edge = crisp silhouette, soft falloff. In the shader (resolution-free) or via Field to Grid | 5.0+ | research agent (Voronoi billows); Schneider "Nubis" remap idea |
| Grid naming | Store the final grid as **`density`**. A grid named `shape` rendered nothing in Cycles (tested). | 5.2 | local test t2/t6 |
| Scattering | **Volume Scatter, phase = Mie, Diameter ≈ 10–20 µm**; colour = albedo; optional HG g=0.857 fallback | 4.3+ | manual volume_scatter.rst; 4.3 release notes; Jendersie–d'Eon (NVIDIA 2023) |
| Multiple scattering | `volume_bounces` 64–256, `max_bounces` ≥ that; unbiased null scattering (5.0 default) | 5.0+ | 5.0 Cycles notes; Wrenninge 2015 ("upwards of 100 bounces"); Kallweit 2017 |
| Density scale | density = target τ / cloud size. Small cumulus τ 25–120; stylised soft clouds τ 5–20. 3 m cloud, τ 60 → density 20 | — | Hillaire 2016 (σ 0.05–0.12/m, Hess 1998) |
| Colour | Scatter colour = albedo per channel (pink ≈ 1.0, 0.8, 0.88), not a surface tint; saturation grows with depth by itself | — | physics: albedo^N over N bounces |
| Sky | Sky Texture `MULTIPLE_SCATTERING` + Sun lamp (not both suns); low sun elevation 2–6° for sunset; lower exposure | 5.0+ | 5.0 rendering notes; manual sky texture |
| Emitters inside | Emissive mesh (ring = torus, rod = cylinder) inside the volume. Glow spread ≈ depth below surface; keep hue (droplets are grey) | — | diffusion result; Peterson lightning paper |
| Dark base | Comes from τ and bounces; add a height gradient (denser base, thinner wispy top) and a flat-ish base cut | — | Hillaire; research agent |
| Grain / grade | Compositor: grain, slight lift (refs 01, 02) | 5.x | knowledge `compositor.md` |

## Rejected approaches

- **Points to SDF Grid → Sample Grid:** narrow band only (3 voxels); the inside samples as background, so the cloud renders hollow with a box of fog around it (test t1). Points to Volume fills the spheres.
- **Pure procedural shader on a cube:** soft lobes, visible box edges, and every noise costs per null-scattering step.
- **Metaballs + Volume Displace (Clouds texture):** least control over lobe scale; the old Clouds texture is lattice-y.
- **Disney/JangaFX VDBs:** best realism but fixed shapes; against the brief (modular, configurable). Kept as a possible later comparison.
- **Principled Volume:** HG only, no Mie. Its emission/blackbody are useful only for the lava-type preset.
- **Beer–powder fakes (HZD):** a real-time trick; with true multiple scattering it is not needed.
- **Light tree / emitters for key light:** use a Sun; emitters only for the in-cloud objects.

## Numeric targets

Measured from the references (sRGB 0–255, region means):

| Ref | Region | Value |
|---|---|---|
| 01 pink ring | cloud lit / core / shadow | 169,105,129 / 217,127,155 / 183,130,145 |
| 01 | sky / ground / cyan under cloud | 196,208,218 / 158,173,184 / 133,159,168 |
| 02 pink rod | cloud lit top / left / violet shadow / bottom | 180,146,170 / 183,123,148 / 148,101,135 / 127,76,104 |
| 02 | sky top / bottom | 63,109,155 / 134,165,184 |
| 03 sunset | lit / shadow side / sky top / sky mid | ~153,129,118 (lit peaks ~225,200,170) / 95,78,86 / 41,88,120 / 100,94,99 |
| 04 cumulonimbus | bright body / base / sky | 238,236,227 / 66,74,82 / 33,49,85 |
| 05 plume | bright / lower / sky | 204,209,209 / 149,140,140 / 111,117,119 |

- Billow scale: ref 02 has ~25–40 visible puffs across the cloud width at the edge; ref 01 ~12–20 larger lobes.
- Edge softness: 2–4 px falloff at 700 px image width (ref 02), wider (6–10 px) in ref 01 smoke.
- Emitter entry glow (ref 02): pink bloom about 3–5 rod widths around the entry point; the rod is invisible inside the cloud beyond ~1 lobe depth.
- Shadow side never below ~0.35 of lit side luminance in the pink refs; ref 04 base ~0.3 of top.

## Open questions

- Does Mie at 10 µm vs HG 0.857 change the look visibly at our τ? (A/B render.)
- Render time on Metal at 128–256 bounces with τ 60: acceptable (<3 min at 1600 px)?
- Billow noise in the shader (sharper, costly) vs baked into the grid (fast, resolution-bound)? Test both at v01.
- How many bounces before a pink albedo of 0.8 goes too red/saturated?
- Do emissive meshes inside the volume converge (light tree note says they sample poorly)? If noisy, add a hidden point/line light at the emitter.

## v13: camera distance and aerial perspective (added 2026-09-28, user request)

- **Perspective depends on distance ÷ size only.** The scene is a scale model (cloud 3–6 m), so compare that ratio with real shots.
  - A lone cumulus (~1 km) on a telephoto lens at 5–20 km is 5–20 widths away. sunset v11 sat at ~7 widths on 85 mm, so a longer lens at 15–20 widths flattens it the way a telephoto photo does.
  - A cumulonimbus (~10 km tall) seen from 15–20 km subtends ~30°. Ref 04 fills half of a phone frame. So ~2–3 heights away is realistic for the tower. What is wrong is the camera level: a real viewer stands on the ground, far below the cloud base, looking up.
- **Aerial perspective.** Over distance d, light from the cloud is attenuated and air light is added: L = L_cloud · T + L_air · (1 − T), with T = exp(−σ d) (Distance fog; Rotenberg). All cloud pixels sit at about the same distance, so T is nearly constant and air light ≈ the horizon sky colour.
- **Blender mechanism.** A homogeneous box of Volume Absorption plus Emission gives exactly that formula, with no noise: with absorption σ and emission E = σ · air colour, out = in · e^(−σL) + air · (1 − e^(−σL)). Make it camera-only (not visible to shadow, diffuse or volume rays), so it does not dim the sunlight on the cloud. Expose it as one control, "Air" = optical depth τ = σL.
  - Rejected: a scattering world volume, because it attenuates the background to black at infinity and is noisy.
  - Rejected: a Post Mist/Z haze, because Cycles writes no depth for volumes, so the cloud would read as sky.
- **Targets.** In ref 03 the shadow side (95,78,86) sits close to the mid sky (100,94,99): about 30–50 % air light. In ref 04 the distant base (66,74,82) is lifted toward the sky blue.

Sources (this addition):
- https://en.wikipedia.org/wiki/Distance_fog
- https://cseweb.ucsd.edu/classes/sp17/cse168-a/CSE168_14_Volumetric.pdf
- https://www.d5render.com/posts/atmospheric-perspective-for-aerial-rendering
- https://documentation.chaos.com/space/VBLD/117638865 (V-Ray volume aerial perspective, as a product precedent)
- https://photographylife.com/how-to-photograph-clouds and https://www.nikonusa.com/learn-and-explore/c/tips-and-techniques/the-way-up-and-far-away-shot-any-great-cloud-photos-lately (telephoto compresses cloud scenes, 85–200 mm typical)
- Search that found nothing: angular size of a cumulonimbus in km terms (derived instead).

## Sources

Read this session:
- https://developer.blender.org/docs/release_notes/5.0/cycles/ — null-scattering unbiased volumes, stochastic interpolation (also local `reference/dev-docs/.../5.0/cycles.md`)
- Local: `reference/dev-docs/docs/release_notes/4.3/cycles.md` (Mie etc. phase functions), `5.0/geometry_nodes.md`, `5.1/geometry_nodes.md` (grid nodes), `5.0/rendering.md` (Sky multiple scattering, Point Density removed)
- Local manual: `render/shader_nodes/shader/volume_scatter.rst`, `volume_coefficients.rst`
- https://code.blender.org/2025/10/volume-grids-in-geometry-nodes/
- https://projects.blender.org/blender/blender/issues/144706 (5.0 volume slowdowns; Biased option)
- https://blenderartists.org/t/vdb-wda-disney-cloud-scattering-tests/1227871 (bounces 30–50 visible gains)
- https://blenderartists.org/t/cloud-rendering-in-cycles-study-using-the-horizon-zero-dawns-volume-rendering-techniques/1392665 (g 0.7–0.9; density vs dark edges)
- https://media.disneyanimation.com/uploads/production/data_set_asset/1/asset/Cloud_Readme.pdf
- https://research.nvidia.com/labs/rtr/approximate-mie/ (Jendersie & d'Eon approximate Mie)
- https://media.contentapi.ea.com/content/dam/eacom/frostbite/files/s2016-pbs-frostbite-sky-clouds-new.pdf (Hillaire 2016: σ 0.05–0.12/m, dual-lobe HG, single scatter looks dirty)
- https://arxiv.org/pdf/1709.05418 (Kallweit 2017 Deep Scattering: still short of energy at 64 interactions)
- https://history.siggraph.org/wp-content/uploads/2022/10/2015-Talks-Wrenninge_Art-Directable-Multiple-Volumetric-Scattering.pdf (100+ bounces; diffusion changes perceived scale)
- https://www.slideshare.net/slideshow/the-realtime-volumetric-cloudscapes-of-horizon-zero-dawn/51996465 (Schneider; remap/erosion, powder)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC6894159/ (Peterson: light from lightning inside clouds)
- https://eyedesyn.com/tutorial_post/stylized-vdb-clouds-with-cinema-4d-and-redshift/ (stylised VDB clouds exist as a genre; no numbers)

Searches that found nothing useful: 3D breakdown of the neon-ring pink-cloud aesthetic; Oz 2013 octave values; Disney dataset extinction values; Hillaire dual-lobe g values; Cloudify / "fluffy clouds" numbers (video/.blend only).
