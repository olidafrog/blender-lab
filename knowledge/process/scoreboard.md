# Scoreboard

What each session cost, so the retro can tell whether a process change made experiments cheaper. One row per session, oldest first. `/capture-learnings` adds the row with `python3 tools/session_cost.py --latest --scoreboard`.

- **Reviews**: Opus reviewer spawns.
- **Best**: best reviewer score in the experiment's `PROGRESS.md` at the end of the session.
- **Output**: output tokens, main thread plus subagents. Cache reads are about 200× larger and track context length; `session_cost.py` prints them in its full table.
- **Active min**: time with gaps over 10 minutes removed.

| Date | Experiment | Session | Reviews | Best | Blender runs | Output | Active min | Note |
|---|---|---|---|---|---|---|---|---|
| 2026-09-26 | wonder-printed-plastic | 9afff771 | 0 | - | 20 | 41k | 51 | v2 poster work, before the pipeline |
| 2026-09-26 | tooling | 5943c0d7 | 0 | - | 14 | 24k | 37 | layout and tools setup |
| 2026-09-26 | tooling | 22bc0aa0 | 0 | - | 0 | 10k | 16 | local Blender docs |
| 2026-09-26 | eclipse-glow | 66d18bbe | 14 | 7.3 | 93 | 251k | 141 | still v01–v09 (7.2), rise v01–v07 (7.3), threshold-orbit migration |
| 2026-09-27 | eclipse-glow | 81e37224 | 4 | 6.8 | 25 | 54k | 41 | sunrise video v01–v04 |
| 2026-09-27 | opal-essence | d9ef3de3 | 1 | 5.3 | 29 | 81k | 30 | in progress when logged; web research ran in subagents, but `build.py` was written before `RESEARCH.md` |
| 2026-09-27 | opal-essence | 517bfecf | 0 | - | 2 | 17k | 16 | short follow-up |
| 2026-09-27 | tooling | edbee1e3 | 0 | - | 6 | 60k | 12 | lab audit: artifact hooks, metrics gate, cost scoreboard, round budget |
| 2026-09-28 | tooling | 81ad5a6d | 0 | - | 1 | 15k | 4 | git: pulled wonder-minidisc, committed eclipse-glow and opal-essence, merged lab-audit, pushed |
| 2026-09-29 | wax-seal-chaos | 5522441b | 8 | 6.4 | 68 | 156k | 220 | fork; seed-drawn approach. 5 Mantaflow bakes abandoned (~1.5 h), SDF reroll; v06 wins blind calibration 6.6 over the original's 5.4. Figures are this session's cumulative totals minus the wax-seal row |
| 2026-09-28 | wax-seal | 5522441b | 8 | 6.6 | 53 | 133k | 42 | v01–v07 + calibration (v07 6.4 wins); slope stop; 3 rounds lost to SSS before an isolation render |
| 2026-09-28 | clouds | 802469a6 | 11 | 7.1 | 60 | 162k | 159 | pink_rod 6.9 (v05; v08 wins calibration), sunset 7.1, pink_ring 6.2; ~20 renders lost to 4 silent GN-volume traps |
