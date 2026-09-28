# wax-seal — progress

## Setup (2026-09-28)

Mac, Blender 5.2, Metal. 5.x-only is fine (GN SDF grids, `mod.properties.inputs`).

Knowledge that lands in v01:
- **Swappable emblem = a geometry-nodes input.** Emblem is any curve or mesh object fed to one GN "Stamp" group (Object input). Curves use the eclipse-glow inflate profile (wall + quarter-round from Proximity to outline) — no Bevel overlap holes (`geometry.md`). Code: `stamp_group`.
- **Library logomark carries an empty material slot** → end the GN stack with Set Material (`geometry.md`).
- **Grid to Mesh threshold 0** for SDF grids (`geometry.md`).
- **Fine bumps < ~0.2 mm-equivalent** or they read as orange peel (`cycles.md`): wax micro-noise in a shader Bump, scale larger than a pixel.
- **Paper exposure 1.0–1.05**, or contact shadow clips away and the seal floats (`cycles.md`). P: `key_power` checked against paper value.
- **View transform:** AgX desaturates pastels toward grey; start `Khronos PBR Neutral` for the lilac (`colour.md`). P: `view`.
- **Mix/Clamp traps**: `ShaderNodeMix` index sockets (`shader-nodes.md`).
- **Mirror-material correctness render** before round 1 — the wax is glossy (`review-loop.md`).


Newest first. Updated after every review. Cost is what the version took: Blender runs and minutes since the last row.

| Version | Score | The one change | Cost | Render |
|---|---|---|---|---|
| v07 | 6.2 | Violet scatter: radius (1,0.5,1.2) at 0.07 mm, wax colour (0.66,0.58,0.76); shadow-side rim now violet | 7 runs, ~10 min | renders/v07.png |
| v06 | 6.4 | Satin sheen (Coat 0.35 @ 0.22 over roughness 0.6), key 36° / 0.12 m, warm fill 0.14 | 4 runs, ~8 min | renders/v06.png |
| v05 | 6.6 | Narrower rounder rim (radius 16.4, oval 1.03, bulge 0.05), pooled folded lump, finer flow lines off the logo, SSS 0.04 | 6 runs, ~10 min | renders/v05.png |
| v04 | 6.4 | SSS 0.35→0.08 mm (isolation: SSS caused the purple creases, filled groove, hid bump); relief 0.45 / bevel 0.15; curved flow lines | 5 runs, ~8 min | renders/v04.png |
| v03 | 6.2 | Hard key: 0.08 m at 30° el, world 0.11, rim peak 0.3 (cast-shadow profile matches ref row 900) | 4 runs, ~6 min | renders/v03.png |
| v02 | 6.2 | Light: key 40° el, 0.3 m, world 0.11, exposure −0.5 (shadow core, paper, field on target) | 5 runs, ~8 min | renders/v02.png |
| v01 | 6.0 | First build: GN heightfield seal, swappable emblem, RW SSS 0.35 mm | ~12 runs, ~40 min | renders/v01.png |

Process guess: straight product photo, one big soft key upper right, low fill; chalky near-opaque wax with short SSS.

## Stopped after round 7 (slope rule)

Best of the last 3 (6.6) beat the 3 before (6.4) by 0.2 < 0.3. Scores: 6.0, 6.2, 6.2, 6.4, 6.6, 6.4, 6.2.
Repeated complaints (mechanism, not tuning): relief tops no brighter than the field (5 rounds); lit rim too bright over a wide band (7 rounds); "soft plastic / fondant" read (7 rounds).
Contradicting asks (handed to the designer as controls): key hardness (soft ↔ hard), relief height (0.3–0.5 ↔ 0.6–0.9 mm), flow-line style (Voronoi ↔ curved).

## Calibration

Blind pair: v07 6.4 vs v05 6.1 → v07 is better (violet shadows). Finish from v07.
