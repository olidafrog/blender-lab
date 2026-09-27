# wonder-minidisc — progress

## Setup (2026-09-27)

- **Machine:** Windows, RTX 3090 Ti, Blender **4.4.3**, Cycles on OptiX. Toolchain smoke test passed (4 s).
- **Fixed before starting:** `tools/comp.py` and the template were 5.x-only and crashed on 4.4; both now branch on `comp.LEGACY`. `tools/fetch_docs.sh` used the Windows `python3` Store stub; now picks a working Python. `reference/` docs being built for 4.4.
- **4.4 gotchas that apply:** compositor is `scene.node_tree` with node properties (Glare settings cannot sit on a Post group input; Glare `threshold` from Python may be ignored); Eevee id is `BLENDER_EEVEE_NEXT`; Refraction BSDF has no `MULTI_GGX`; File Output writes `name0001.exr`.

## Process guess

Real objects photographed in a bright studio. Disc = mirror + 1.6 µm grating that needs a dark reflection with bright sources beside it; case = tinted PC, colour by volume absorption.

## Knowledge that applies

- Transparent/coloured plastic needs something bright behind or under it to read; decide per light whether it is seen in reflection, through the plastic, or both (`visible_glossy`, `visible_transmission`).
- Imperfections: dust occludes (black diffuse mix), never glows. Fingerprints/haze touch glossy roughness only. Scratches = Voronoi distance-to-edge windows under a sparse mask, tiny bump, keep under ~0.15 roughness.
- Fine patterns (disc grooves) alias: supersample at 2× and downsample; check pitch in pixels before round 1.
- Correctness pass before round 1: DOF focus on an empty at the face, flat-grey override render, numeric targets from reference crops.
- AgX desaturates saturated colour (red/orange plastic will go peach). Consider Standard or AgX Punchy; lock the choice early.
- Smooth-shading across triangulated n-gon caps bands normals under refraction; flat-shade caps, bevel with harden normals.
- Colour through thick tinted plastic = volume absorption (depth-dependent saturation), as in ref2 where thick rims read deeper red.
- One control node per material from the start (`tools/nodes.py`).

## Loop stopped at v11 (2026-09-27)

Last three scores 6.8 / 6.9 / 6.8. The remaining top asks contradict each other for a tinted case: "tint the disc strongly like ref2" (needs thin plates to absorb more) vs "pink/magenta like ref4" (teal absorbs red). No score-neutral answer, so it is handed to the designer as the "Colour Depth mm" input (1.5 = ref2-strong tint, 5 = ref4 full spectrum). Other asks left open: hub reads dark under the teal; webs read as a flat slab over a plain white table (design-inherent: the disc is logo-shaped).

Newest first. Updated after every review.

| Version | Score | The one change | Render |
|---|---|---|---|
| FINAL | 6.8 | v11 settings at 1024 samples; `.blend` verified pixel-identical from its saved source. Colourway sheet in output/ | output/FINAL_wonder-minidisc.png |
| v11 | 6.8 | Shadow light 0.55 -> 0.9: webs back to light hollow teal (contact shadow kept from the key change) | renders/v11.png |
| v10 | 6.9 | Grounding: table exposed just at white (key 8 -> 4 W + far fill) so a contact shadow shows; shadow light 0.55; hub clear zone inside the stroke, rougher steel | renders/v10.png |
| v09 | 6.8 | Well walls split into top/bottom shell ribs with the parting gap between. Reviewer brief now states the disc is logo-shaped (no disc under the webs): scores from here are not strictly comparable with v01-v08 | renders/v09.png |
| v08 | 6.2 | Broad wedges: arcs 12 -> 28 deg wide (hue depends only on the angle off the mirror, so width costs no saturation) | renders/v08.png |
| v07 | 6.3 | Colour depth 5 -> 3 mm: disc visibly tinted through the plate | renders/v07.png |
| v06 | 6.3 | Wear: sparse thresholded dust, scratches/fingerprints halved | renders/v06.png |
| v05 | 6.3 | Disc colour by numbers (disc_metrics.py): narrower wedges, less spread, pink layer tint on every order -> 5 hue families, 25 % dark mirror | renders/v05.png |
| v04 | 5.2 | Colour depth 2 -> 5 mm: thin plates pale enough for the spectrum | renders/v04.png |
| v03 | 5.6 | Flat caps (auto-smooth had domed every n-gon: the "crumpled foil"); wedge lights each at their own angle so sectors cycle hues | renders/v03.png |
| v02 | — | Ring of arc lights + spread 0.15 (not reviewed: still had the dome bug) | renders/v02.png |
| v01 | 4.8 | First full build: logo disc (diffraction BSDF), moulded teal case, black-flag studio | renders/v01.png |
| v00 | — | Template smoke render (4.4 compositor path) | renders/v00.png |
