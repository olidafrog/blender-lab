# Knowledge base

What we have learned across every experiment. Read the index before you start work. Write to it at the end of a session with `/capture-learnings`.

## Kinds of entry

- **Gotcha** — something that failed or cost time. Say the symptom, the cause and the fix.
- **Process** — a way of working that gave better results, or one to avoid.
- **Insight** — a deeper lesson that is not about one Blender feature.
- **Decision** — why one experiment was built the way it was, and what we rejected.

## Tags

End a bullet with a tag in backticks when it does not apply everywhere:

- Blender version: `4.4`, `5.x`. The Windows PC runs 4.4. The Mac runs 5.2.
- Machine: `mac`, `win`.
- Source: the experiment that taught it, for example `caustics-v2`.

No tag means it holds on both versions and both machines. If you confirm a tagged entry on the other version, remove the tag.

## Rules

- Update an entry before you add a new one. One fact lives in one place.
- Keep entries to one to three lines. Link to an experiment file for detail.
- Record what the code cannot show. Do not describe what a script does.
- A rule lives in one place: the skill that applies it, or `CLAUDE.md`. Knowledge files keep the evidence and point at the rule.
- Prune. When an entry has gone three experiments without being used or confirmed, tag it `stale?`. The next retro deletes it or removes the tag.

## Index

Gotchas
- [Headless runs](gotchas/headless.md) — launching, GPU, exit codes, output, paths.
- [Platform](gotchas/platform.md) — Mac and Windows differences.
- [API changes](gotchas/api-changes.md) — Blender 4.4 versus 5.x.
- [Compositor](gotchas/compositor.md) — node behaviour and traps.
- [Shader nodes](gotchas/shader-nodes.md) — node traps and shading techniques, grain, scratches and creases.
- [Cycles](gotchas/cycles.md) — lighting, refraction, geometry, output quality, dark plastic and light linking, exteriors (sun, sky, glass, context).
- [Colour](gotchas/colour.md) — view transforms, clipping, dark fades.
- [Geometry](gotchas/geometry.md) — curves, SVG import, geometry nodes, booleans and plates, filled-curve facades, GN contours and SVG strokes for plotting, formula-driven forms, hidden lines, outlines and blots.
- [Modelling](gotchas/modelling.md) — characters from code (planar-ring lofts, IK posing, straps and skirts, silhouette checks) and hard-surface plates from traced outlines (edge classes, crisp chamfer, black gaps, detail), architecture from a straight-on photo.
- [Fluid sim](gotchas/fluid-sim.md) — Mantaflow scale, flow volume, why a viscous press failed.
- [Volumes](gotchas/volumes.md) — GN volume grids, albedo vs scatter colour, emitters in volumes, cloud look.

Process
- [Review loop](process/review-loop.md) — evidence behind the `review-render` rules.
- [Matching a reference](process/matching-a-reference.md) — "recreate this image" tasks.
- [Debugging a render](process/debugging.md) — isolating, cropping, measuring.
- [Process improvements](process/improvements.md) — how the skills changed, each with a check, and proposals.
- [Improvements archive](process/improvements-archive.md) — settled changes whose checks held twice.
- [Parallel sessions](process/parallel-sessions.md) — worktrees, when `.claude/` edits take effect, worktree Bash limits.
- [Scoreboard](process/scoreboard.md) — what each session cost: reviews, best score, Blender runs, tokens, time.

- [Insights](insights.md) — deeper lessons.

Decisions
- [plotter-forms](decisions/plotter-forms.md) — a catalogue of 50 formula-driven line-art forms with hidden-line removal: formula strings → GN, camera-side visibility test, anti-blot cut; 7.1 calibrated
- [plotter-blend](decisions/plotter-blend.md) — line art as GN curves → SVG strokes for a pen plotter: contour sphere (marching triangles in GN), flared-catenoid funnel, own exporter; ~6.4 calibrated
- [aztechno-building](decisions/aztechno-building.md) — photoreal facade at true scale from a traced pixel spec; physical sun + sky, coated glass with sky/street reflections, photographic output stage (fork); 6.4
- [cyber-deck-v2](decisions/cyber-deck-v2.md) — same radio redone: plan × section loft shells, profiled cutters, crest-only wear tag, one small key; 6.4 (Opus)
- [cyber-model](decisions/cyber-model.md) — hard-surface radio from a rectified plan: stacked plates, flat chamfers, black by geometry, three linked lights; Sonnet reviewer + Opus advisor test, 6.7
- [roman-model](decisions/roman-model.md) — first character model: IK-posed planar-ring lofts + jitter/triangulate, hand-built armour, silhouette IoU gate
- [eclipse-glow](decisions/eclipse-glow.md)
- [wonder-printed-plastic](decisions/wonder-printed-plastic.md)
- [wonder-caustics and caustics-v2](decisions/wonder-caustics.md) — dispersive glass
- [wonder-minidisc](decisions/wonder-minidisc.md) — CD diffraction BSDF, tinted case, mirror-direction studio
- [opal-essence](decisions/opal-essence.md) — milky opalescent resin over a gradient backlight
- [wax-seal-chaos](decisions/wax-seal-chaos.md) — seed-drawn fork: SDF-sculpted seal, low sun; beat the original blind 6.6 vs 5.4
- [wax-seal](decisions/wax-seal.md) — GN heightfield seal, swappable emblem (curve/text/mesh), short violet scatter
- [clouds](decisions/clouds.md) — modular volumetric clouds: lobe tiers → density grid, Mie + albedo absorption, emitters inside
