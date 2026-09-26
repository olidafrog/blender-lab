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

## Index

Gotchas
- [Headless runs](gotchas/headless.md) — launching, GPU, exit codes, output, paths.
- [Platform](gotchas/platform.md) — Mac and Windows differences.
- [API changes](gotchas/api-changes.md) — Blender 4.4 versus 5.x.
- [Compositor](gotchas/compositor.md) — node behaviour and traps.
- [Shader nodes](gotchas/shader-nodes.md) — node traps and shading techniques.
- [Cycles](gotchas/cycles.md) — lighting, refraction, geometry, output quality.
- [Colour](gotchas/colour.md) — view transforms, clipping, dark fades.

Process
- [Review loop](process/review-loop.md) — the adversarial render-and-score loop.
- [Matching a reference](process/matching-a-reference.md) — "recreate this image" tasks.
- [Debugging a render](process/debugging.md) — isolating, cropping, measuring.
- [Process improvements](process/improvements.md) — how the skills changed, and proposals.

- [Insights](insights.md) — deeper lessons.

Decisions
- [eclipse-glow](decisions/eclipse-glow.md)
- [wonder-printed-plastic](decisions/wonder-printed-plastic.md)
