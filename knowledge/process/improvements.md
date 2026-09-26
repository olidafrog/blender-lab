# Process improvements

How the system changes itself. `/capture-learnings` adds to this at the end of each session. Newest first.

## Proposed

- **Port `eclipse-glow` to the 5.x compositor** so it runs on both machines. Evidence: it fails on the Mac with `'Scene' object has no attribute 'node_tree'`.
- **Shared metrics script in `tools/`**, generalised from `experiments/wonder-caustics-v2/scripts/metrics.py`, so every loop can prove a fix reached the pixels. Evidence: 3 wasted review rounds in `printed-plastic`.

## Changed

- **2026-09-26 — Autonomous by default.** Removed approval gates from the research and review steps; the user follows `PROGRESS.md`. Evidence: the user wants to kick off experiments and let them run. Files: all skills.
- **2026-09-26 — Compositor hand-off.** `tools/comp.py`: raw EXR written in the same render, a Viewer for the backdrop, a Saved Render source, and a one-node Post group. Evidence: the user asked for live compositor tweaking; `wonder-caustics/scripts/comp.py` proved the EXR re-grade. Files: `tools/comp.py`, new-experiment template.
- **2026-09-26 — Review loop from past sessions.** Opus only, a fresh reviewer each round, a correctness pass before round 1, proving each fix reached the pixels, capped reviews, numeric targets, `PROGRESS.md`. Evidence: mining of the `printed-plastic` transcript and 46 reviews. Files: `review-render`, `research-reference`.
- **2026-09-26 — Research first, one-node materials.** Added `research-reference`, `finish-experiment` and `tools/nodes.py`. Evidence: `printed-plastic` ignored its research for 12 rounds; `wonder-popart`'s one-node materials were the hand-off that worked.
