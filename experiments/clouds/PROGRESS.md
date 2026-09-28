# clouds — progress

## Setup (2026-09-28)

- Mac, Blender 5.2.2 LTS, Cycles on Metal (M4 Max). Build is 5.x only unless noted; Windows 4.4 not targeted.
- Relevant knowledge:
  - Volumes: a milky scatter volume picks up every front light regardless of ray-visibility flags; use light linking to keep accents off it (`cycles.md`, opal-essence).
  - Emissive meshes inside a volume light it — that is the effect we *want* for the neon ring/rod; control reach with emitter power, not size (radiance = P/A).
  - AgX desaturates saturated colours (pink → peach). Try Khronos PBR Neutral / AgX Punchy for the pink presets (`colour.md`).
  - Geometry nodes in 5.2: Mesh to SDF Grid / Grid to Mesh threshold 0 for SDFs; GN modifier inputs via `mod.properties.inputs.Socket_N.value` (`geometry.md`).
  - Compositor is a node group in 5.x; Blur size must come from a Math node if linked (`compositor.md`).
  - Long renders (volumes!) exceed 2 min tool timeout: run in background (`headless.md`).
  - Process: correctness pass before round 1; one ranked problem per round; a repeated structural complaint means a new mechanism (`review-loop.md`, `insights.md`).


Newest first. Updated after every review. Cost is what the version took: Blender runs and minutes since the last row.

Process guess (from RESEARCH.md): procedural density grid in geometry nodes (tiers of lobes → Points to Volume → smooth → billow noise → `density` grid), Cycles Volume Scatter with Mie phase + matching absorption for albedo, 128 volume bounces, sun + sky; neon props are emissive meshes inside the volume.

Pre-v01 correctness fixes (scratch tests): GN volume needs Set Material; grid must be named `density`; Field to Grid needs Set Grid Background 0; Scatter Colour is not albedo (added absorption); sun power 15 (sky dominated at 4); density 100/m so the free path stays well under a lobe.

| Version | Score | The one change | Cost | Render |
|---|---|---|---|---|
| v12_pink_ring | 6.2 | pink_ring preset: plume form, soft overcast, ground plane, ring (first review) | 4 runs, ~12 min | renders/v12_pink_ring.png |
| v11_sunset | 7.1 | warm Fill sun opposite the key (4%), noise-displaced ragged base | 2 runs, ~8 min | renders/v11_sunset.png |
| v10_sunset | 6.8 | split sky: camera sees the gradient, cloud lit by gradient + 0.015× physical sky | 7 runs, ~15 min | renders/v10_sunset.png |
| v09_sunset | 6.5 | sunset preset: 5-lobe row, flat base in the shape node, 3-stop dusk sky | 12 runs, ~30 min | renders/v09_sunset.png |
| v08 | 6.7 | big-lobe hierarchy: 3 tier-0 lobes in a row (seed 11). pink_rod loop stopped: slope flat (best of last 3 = 6.8 vs 6.9) | 8 runs, ~14 min | renders/v08.png |
| v07 | 6.8 | sun split to az -60° (reviewers contradicted), bloom 0.6/0.35 | 2 runs, ~9 min | renders/v07.png |
| v06 | 6.7 | sun behind-left (az -110°, warm), albedo less blue | 3 runs, ~10 min | renders/v06.png |
| v05 | 6.9 | 5 lobe tiers down to 2.7 cm puffs, voxel 7 mm, no smoothing, edge 0.04 | 5 runs, ~16 min | renders/v05.png |
| v04 | 6.4 | neon rod 0.3 m nearer the front, strength 800, bloom 0.8: glows through the body | 5 runs, ~12 min | renders/v04.png |
| v03 | 6.2 | Khronos PBR Neutral view + sky gradient mapped to the frame + warmer sun | 5 runs, ~14 min | renders/v03.png |
| v02 | 5.6 | puffs cover the whole skin (tiers on all earlier spheres); full res | 2 runs, ~12 min | renders/v02.png |
| v01 | not reviewed | first full pipeline; superseded before review (bare smooth lobes: puffs only sat on the previous tier) | 1 run, 3.3 min | renders/v01.png |

## Calibration

pink_rod, blind A/B (reviews/calibration.md): **v08 (final) 6.6 beats v05 (earlier best score) 5.9.** Finish from v08.

## Stopped (2026-09-28)

Budget 12 reviews: 11 rounds + calibration used. pink_rod slope was flat (6.7–6.9 for 4 rounds). Sunset rose to 7.1 (target 7.5 not reached). pink_ring had one round (6.2); after it, emitters stopped casting shadows and ring power went 150 → 500 (not re-reviewed).

Open (mechanism candidates for a next version):
- Emitter inside a cloud gap reads as a bright hole (v08): add density along the prop's path so it stays 1–2 cm under the surface; clamp indirect.
- Sunset left lobe merges into the sky (v11): the fill should come from the lower mauve sky, not the teal top. Try the physical sky with higher aerosol as the fill only.
- pink_ring lit flat (v12): softer overcast needs a bigger sun angle or a stronger density so the base darkens.
- Denoiser smear on tiny puffs at 128 spp: finals at 512 spp.
- pink_ring final: ring power 500 (after v12) lights the ground plane bright pink; ref 01 ground stays neutral. Lower Neon Strength (~200) or light-link the ring to the Cloud only. Not re-reviewed.
