# aztechno-building — research

Three Sonnet agents (lighting/camera, materials, the building) plus my own read of the reference, 2026-09-30.
Test scripts from the agents: `scratchpad/research-light/`, `scratchpad/research-mat/` (session scratch, not kept).

## Read of the reference

In the order they matter to the look:

1. **Layout and relief.** Freddy Mamani's *Salón de Eventos Crucero del Sur* (El Alto, 2014), photographed by Peter Granser (book *El Alto*, 2016). Near-orthographic straight-on shot, verticals parallel: a shift lens from a raised position (pavement top visible, cornice caps seen near edge-on). Front facade mirror-symmetric about u ≈ 727 px. Mouldings are stacked layers — cream lip, yellow band, cream lip — with thin hand-painted orange lines on top (the Granser close-up shows the lines are paint, the layers relief). Relief depths 0.1–0.3 m; cast shadows are what make it read as 3D.
2. **Sun.** Low-ish, hard, from the **front-right** (not the left): shadows fall to the left of the tower, piers and cap posts; right-hand reveals are dark; both roof tanks are lit on the right. Azimuth ≈ 45° right of the facade normal, elevation ≈ 35° (0.4 m shadow under the 0.3–0.6 m fascia). Sun:sky ≈ 4–5:1; shadows neutral-to-blue grey (cream shade 114,112,110).
3. **Glass.** Large areas of dark curtain-wall glass in thin gold frames (horizontal lines ≈ 0.43 m apart in the big bays). Upper windows reflect sky (60,67,82 median; bright p90 148), lower ones reflect the brick street and a snow peak (29,22,18). Panes show slightly disjoint reflections (pane-to-pane tilt).
4. **Paint.** Saturated, fresh, fairly matte acrylic on cement render, soft roller mottling, no panel joints. Red lit (230,65,70), cream lit (238,233,215), yellow lit (250,219,151), orange lit (230,129,96). Photo is graded: the sunlit red is above any physical albedo.
5. **Context.** Cobbled street (small grey setts), pale concrete slab sidewalk with joints and a kerb; unfinished hollow-brick neighbour on the right (brick courses ≈ 5–6 px) with a concrete frame and rebar; far brick buildings at left; two salmon cylinders on the roof; chrome faceted diamonds in the tower oculi; pale high-altitude sky, bright at the horizon.
6. **Camera and post.** Crisp, no DOF, mild lens character; a JPEG at 1400 px (≈ 2.6 cm/px at the facade).

## Most likely process

A professional architectural photograph: shift lens, level camera raised several metres across the street, midday-to-afternoon sun from the front-right, sky and shadows balanced (probably exposure-blended: the sky is ~0.5 of a lit cream wall, the physical sky ~0.1). The building is a real RC frame with brick infill; the relief is cast plaster in hand-carved moulds, painted with synthetic paint; glass is tinted reflective curtain wall in metal frames. So: model the geometry at true scale with real relief, light it with one physical sun and a physical sky, and match the photographer's sky exposure only for what the camera and reflections see.

## Techniques to use

| Effect | Blender approach | Source | Version |
|---|---|---|---|
| Facade layout | Trace in reference px (`scripts/facade.py`), px → m with `P["ppm"]` ≈ 38 (shutters, door, storey pitch agree ±8 %). Mirror the right half. | subject agent | any |
| Relief | Each moulding a filled 2D curve with holes (fill BOTH), extruded to its depth, round bevel 0.6–1.5 cm, converted to mesh; no booleans. Tested in scratch: holes and bevel clean. | own test; knowledge `geometry.md` (bevel ≤ 1/3 narrowest part) | 5.x |
| Camera | Level camera, `lens = 36 · ppm · D / W`, `shift_x`/`shift_y` so the facade plane lands on the reference pixels; `shift_y` is a fraction of the longer side (verified: eye level at `H/2 + shift_y·W`). | lighting agent test | any |
| Sky | `ShaderNodeTexSky`, `sky_type = MULTIPLE_SCATTERING`, `altitude = 4050`, `air_density = 2` (the photo's paler blue), disc off. `sun_rotation = atan2(x, y)` of the sun vector (0 = +Y, toward +X). | 5.0 release notes; manual `sky.rst`; agent test | 5.0+ |
| Sun | Sun lamp ≈ 135 W/m² (= the sky model's own disc at 4000 m), angle 0.526°; one sun only. | agent test | any |
| Photographer's sky | Multiply the sky by `sky_view` for camera and glossy rays only (Light Path), so shadow fill stays physical. | manual `world_settings` "Tricks" | any |
| Exposure | `cycles.film_exposure` ≈ 2⁻⁵ (linear, before the compositor: no glare veil). Indirect clamp 0 (10 crushed the shade side). | agent test; manual `film.rst` | 5.x |
| View transform | Khronos PBR Neutral (keeps saturated red/yellow; AgX turns yellow saturation 0.81 → 0.38). A/B against AgX once. | agent measurement; knowledge `colour.md` | 4.2+ |
| Glass | Opaque Principled, near-black base, roughness 0.02, reflectance 4–8 % (IOR from reflectance), no transmission: 3× less noise and faster than thin-wall; interior barely visible. Per-pane tilt 0.15–0.4° and ±20 % reflectance per pane. | materials + lighting agent tests; National Glass data | 5.x |
| Reflections | Model the street behind the camera (brick blocks, edges crossing the panes), camera-invisible, no shadows. Snow peak optional. | materials agent; knowledge `insights.md` (the environment is the material) | any |
| Paint | Principled, albedo red ≈ (0.58, 0.05, 0.03), roughness ≈ 0.62; broad faded patches (noise ≈ 0.35/m) not fine bump (plaster grain is invisible at 2 cm/px); light AO grime; freshly painted. | materials agent (ambientCG scan, APCO LRV) | any |
| Shutters | Painted texture (drawn per shutter: cream slats, orange hexagon, maroon stripes) + slat bump; slat pitch 55–77 mm ≈ 3 px → supersample the final. | materials agent; knowledge `cycles.md` | any |
| Brick, pavement, street | Poly Haven CC0: `large_red_bricks` (scale up 1.5–2×), `concrete_pavement_02`, `cobblestone_03`, box-projected in object space. | materials agent, `assets/SOURCES.txt` | any |
| Lens | Compositor asset groups (Vignette 0.15–0.3, Chromatic Aberration ≤ 0.03 at 1400 px, Sensor Noise ≈ 0.03) — at the end, subtle. | agent test | 5.x |

## Rejected approaches

- **Glass BSDF / transmission panes** — noisier (0.30–0.32 relative noise vs 0.036), slower, and the interior is invisible behind this glass. Glass BSDF's colour also darkens the reflection 7×.
- **Coated mirror glass (≥ 11 % reflectance)** — the reference reflects the sky at ~4 % if its sky is the photo's sky; with the sky lifted for glossy rays, plain tinted glass matches.
- **Plaster bump / normal maps on the paint** — +0.08 levels of grain at this distance: wasted.
- **Sky disc plus a sun lamp** — two suns. **Indirect clamp 10** — crushed the shade side 2.4×.
- **AgX** — desaturates the paint the building is about.
- **HDRI as the world** (`kiara_5_noon_4k`) — kept as a fallback; the physical sky ties sun direction and sky colour together and is tunable.
- **Auto-vectorising the reference colours into the model** — wobbly edges; hand-traced primitives with a per-colour IoU check instead.

## Numeric targets

From `scripts/measure_facade.py` (sRGB medians at 1400×979) and `scripts/labels.py`:

| Row | Reference |
|---|---|
| red lit | (230, 65, 70) |
| cream lit / shade | (238, 233, 215) / (114, 112, 110) |
| yellow lit / shade | (250, 219, 151) / (138, 114, 85) |
| orange lit / shade | (230, 129, 96) / (137, 87, 56) |
| glass upper (sky) median / p90 luma | (60, 67, 82) / 148 |
| glass lower (street) median / p90 luma | (29, 22, 18) / 55 |
| sky top / low right | (141, 176, 211) / (214, 230, 245) |
| pavement / street | (170, 151, 134) / (160, 147, 131) |
| brick neighbour | (83, 56, 48) |
| gf cream / gf base | (227, 207, 178) / (192, 88, 69) |

- Scale ≈ 38 px/m; facade 29 m wide, ~19.8 m to the parapet; tanks ≈ 1.2 / 1.0 m diameter.
- Tower cast shadow on the red to its left ≈ 11–12 px wide.
- Layout: paint-class mean IoU of the traced spec, flat-filled, 0.33 (the gate: a render must not fall below it; aim ≥ 0.45).

## Open questions

- Camera distance and height (D ≈ 20–30 m, h ≈ 8–12 m): settle by the visible side faces (reveals, cap undersides) and the pavement's depth in the frame.
- Sun azimuth/elevation: settle by the tower's left shadow (11–12 px) and the fascia shadow (≈ 15 px).
- Glass reflectance 4 % vs 8 %: settle on the "glass upper" row with the sky lift in place.
- Left corner: chamfer 45° + side facade angle — fit to the reference widths.

## Sources

Opened and used (full lists in the agent reports):
- https://developer.blender.org/docs/release_notes/4.2/rendering/ and local `reference/dev-docs` release notes 5.0–5.2 (multiple-scattering sky, Thin Wall)
- https://fgarlin.com/blog/spectral-sky/ (sky model; aerosols ignored)
- https://github.com/KhronosGroup/ToneMapping/blob/main/PBR_Neutral/README.md
- https://jayargonaut.com/2024/08/11/achieving-realistic-rendering-with-agx-and-khronos-pbr-neutral-in-blender-4-2/
- https://blenderartists.org/t/correct-sun-strength-value/1255199
- https://blenderartists.org/t/noise-n-glass-problems/1589976
- https://blendergrid.com/articles/cycles-physically-correct-brightness
- https://cgconnect.chaos.com/insights/articles/6ae07fc2-photorealistic-architectural-rendering-15-tips-to-follow
- https://renderartstudio.com/our-stories/mastering-the-art-of-arch-viz-images/
- https://www.superrendersfarm.com/article/blender-render-settings-optimization-guide
- https://seblagarde.wordpress.com/2014/04/14/dontnod-physically-based-rendering-chart-for-unreal-engine-4/
- https://dev.epicgames.com/documentation/unreal-engine/physically-based-materials-in-unreal-engine
- https://api.physicallybased.info/materials
- https://www.apcosigns.com/techpdf/lrv.pdf
- https://www.nationalglass.com.au/assets/main/Energy-Performance-Data-May2023.pdf
- https://mannleeco.com/insights/glass-distortion-anisotropy/
- https://www.blender3darchitect.com/architectural-visualization/bathroom-interior-and-architectural-glass/
- https://api.polyhaven.com (textures, HDRI) and https://ambientcg.com/api/v2/full_json
- https://maquispe.wordpress.com/2014/09/07/el-crucero-del-sur-otra-obra-de-mamani-silvestre/
- https://www.pinupmagazine.org/articles/freddy-mamani-jonathan-castro (Granser close-up)
- https://www.wallpaper.com/architecture/peter-granser-freddy-mamani-silvestre-edition-taube-book
- https://tatewakinio.com/Neo-andina
- https://trans-americas.com/cholets-architecture-in-el-alto-bolivia/ (Eric Mohl obliques and interior)
- https://www.anthropologyofarchitecture.com/cholets-cosmogonic-achitecture-aymara (construction)
- https://www.lostiempos.com/oh/actualidad/20150801/cholets-alto-su-arquitectura-exportacion
- https://en.wikipedia.org/wiki/El_Alto, https://en.wikipedia.org/wiki/Huayna_Potos%C3%AD

Local: `reference/manual` — `render/shader_nodes/textures/sky.rst`, `render/cycles/render_settings/film.rst`, `light_paths.rst`, `world_settings.rst`, `optimizations/reducing_noise.rst`, `color_management/displays_views.rst`, `shader_nodes/shader/principled.rst`.

Found nothing / could not open: a higher-resolution full frame of the photo; any night view; the exact plot on a map; projects.blender.org PR 140480 (403); Dezeen, ResearchGate, artsy (403); `ShaderNodeRaycast` streak masks (would not hit from a vertical wall).
