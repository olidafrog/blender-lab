# Clouds: decisions

Experiment: `clouds`. A modular volumetric cloud system: one shape node (geometry nodes), one material node, and presets for a pink cloud pierced by a neon rod (ref 02), a pink plume with a neon ring (ref 01), a lone sunset cumulus (ref 03), a cumulonimbus tower and a lava-lit plume. It stopped at the 12-review budget.

| Preset | Best | Rounds |
|---|---|---|
| pink_rod | 6.9 (v05), final v08 6.7; blind calibration v08 6.6 > v05 5.9 | 7 |
| sunset | 7.1 (v11), target 7.5 missed | 3 |
| pink_ring | 6.2 (v12), then two unreviewed fixes | 1 |
| tower, plume | built, not reviewed | 0 |

Research is in `experiments/clouds/RESEARCH.md`.

## What makes the look

- **Lobes on lobes, as geometry.** Python places 5 tiers of spheres, from 2–5 big lobes (in a row along x) down to 9000 puffs of radius 0.009 × size. Each tier sits on the exposed skin of every earlier sphere, picked by surface area. GN: Points to Volume, Dilate, Field to Grid, Set Grid Background 0, then a grid named `density`, then Set Material. The popcorn detail comes from the puffs. Noise on the grid added almost nothing.
- **Density high enough that the free path is well under a lobe.** At 100/m (free path 1 cm on a 3 m cloud), lobes shade each other. At 20/m, 128 bounces washed every lobe flat.
- **Colour as albedo.** Volume Scatter (Mie, 12 µm) plus Volume Absorption, both at the same density, with Absorption Color = albedo. The designer Colour runs through the Christensen–Burley multiple-scatter inversion, so it means "how the lit cloud looks".
- **Emitters are real emissive meshes inside the volume.** They show through only within ~0.3 m of the surface, and need strength ~500–800 on a 12 mm tube. They do not cast shadows.
- **Khronos PBR Neutral view.** AgX made the pink pastel and the sky grey.
- **Sunset light:** a key sun at 4°, a warm fill sun opposite it at 4 % of its power, and a "split" world. The camera sees the designed gradient; the cloud is lit by the gradient plus 0.015× the physical multiple-scattering sky.

## Rejected

- Points to SDF Grid plus Sample Grid: narrow-band, so the cloud came out hollow.
- Pure shader noise on a cube, and VDB assets: the first gives soft lobes, the second fixed shapes (against the modular brief).
- Principled Volume: it has Henyey-Greenstein only, no Mie.
- A base cut done in Python by rejecting puffs: it left bare spheres. The base is a height fade in the shape node.
- The physical sky as the visible background: 50× too bright and wrong for dusk. The designed gradient is the backplate.

## Open

- An emitter crossing a gap between lobes reads as a bright hole (v08). Add density along its path, or clamp indirect light.
- The sunset shadow lobe merges into the sky (v11). The fill should come from the lower mauve sky.
- pink_ring is lit flat (v12). Try a larger sun angle for overcast light.
- Denoiser smear on the tiny puffs at 128 spp.
