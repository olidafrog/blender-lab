# Scoreboard

What each session cost, so the retro can tell whether a process change made experiments cheaper. One row per session, oldest first. `/capture-learnings` adds the row with `python3 tools/session_cost.py --latest --scoreboard`.

- **Builder**, **Reviewer**: the main thread's model and the model the reviewer agents ran on. Scores only compare within one reviewer model.
- **Reviews**: reviewer agent spawns, on any model.
- **Best**: best reviewer score in the experiment's `PROGRESS.md` at the end of the session.
- **Output**: output tokens, main thread plus subagents. Cache reads are about 200× larger and track context length; `session_cost.py` prints them in its full table.
- **Active min**: time with gaps over 10 minutes removed.

| Date | Experiment | Session | Builder | Reviewer | Reviews | Best | Blender runs | Output | Active min | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-26 | wonder-printed-plastic | 9afff771 | opus-5-5 | - | 0 | - | 20 | 41k | 51 | v2 poster work, before the pipeline |
| 2026-09-26 | tooling | 5943c0d7 | opus-5-5 | - | 0 | - | 14 | 24k | 37 | layout and tools setup |
| 2026-09-26 | tooling | 22bc0aa0 | opus-5-5 | - | 0 | - | 0 | 10k | 16 | local Blender docs |
| 2026-09-26 | eclipse-glow | 66d18bbe | opus-5-5 | opus | 14 | 7.3 | 93 | 251k | 141 | still v01–v09 (7.2), rise v01–v07 (7.3), threshold-orbit migration |
| 2026-09-27 | eclipse-glow | 81e37224 | opus-5-5 | opus | 4 | 6.8 | 25 | 54k | 41 | sunrise video v01–v04 |
| 2026-09-27 | opal-essence | d9ef3de3 | opus-5-5 | opus | 1 | 5.3 | 29 | 81k | 30 | in progress when logged; web research ran in subagents, but `build.py` was written before `RESEARCH.md` |
| 2026-09-27 | opal-essence | 517bfecf | fable-5-1 | - | 0 | - | 2 | 17k | 16 | short follow-up |
| 2026-09-27 | tooling | edbee1e3 | opus-5-5 | - | 0 | - | 6 | 60k | 12 | lab audit: artifact hooks, metrics gate, cost scoreboard, round budget |
| 2026-09-28 | tooling | 81ad5a6d | opus-5-5 | - | 0 | - | 1 | 15k | 4 | git: pulled wonder-minidisc, committed eclipse-glow and opal-essence, merged lab-audit, pushed |
| 2026-09-29 | wax-seal-chaos | 5522441b | opus-5-5 | opus | 8 | 6.4 | 68 | 156k | 220 | fork; seed-drawn approach. 5 Mantaflow bakes abandoned (~1.5 h), SDF reroll; v06 wins blind calibration 6.6 over the original's 5.4. Figures are this session's cumulative totals minus the wax-seal row |
| 2026-09-28 | wax-seal | 5522441b | opus-5-5 | opus | 8 | 6.6 | 53 | 133k | 42 | v01–v07 + calibration (v07 6.4 wins); slope stop; 3 rounds lost to SSS before an isolation render |
| 2026-09-28 | clouds | 802469a6 | opus-5-5 | opus | 11 | 7.1 | 60 | 162k | 159 | pink_rod 6.9 (v05; v08 wins calibration), sunset 7.1, pink_ring 6.2; ~20 renders lost to 4 silent GN-volume traps |
| 2026-09-30 | roman-model | 7396126c | opus-5-5 | opus | 10 | 6.8 | 100 | 277k | 79 | first character model; 9 reviews + calibration (v09 6.4 beats v08 5.8); slope stop at round 9; 2 Fable advisor consults; mechanism change at v04 (decimate → planar rings) |
| 2026-09-30 | cyber-model | 284578b4 | sonnet-5-5 | sonnet | 11 | 6.7 | 84 | 371k | 102 | first hard-surface model; test of Sonnet: 2 Sonnet research agents, 10 Sonnet reviews + 1 calibration (counted in Reviews; the tool's Opus column reads 2 for the two Opus advisor consults); v09 6.7 beats v10 6.5 blind; ~1.5 h lost to silent boolean failures (empty Exact result, cancelling cutters); mechanism changes at v04 (light), v07 (chamfer), v09 (black liner) |
| 2026-09-30 | cyber-deck-v2 | 679fe8d0 | opus-5-5 | opus | 11 | 6.4 | 113 | 284k | 86 | same radio as cyber-model, lab defaults (Opus): 3 Opus research agents (found the original artwork), 10 Opus reviews + calibration (v10 6.4 beats v11 6.2), 1 Fable consult; mechanism changes at v01 (plan × section loft), v04 (moats, sweep radii), v07 (one small key: blacks fixed); reviewers read snapshots and old reviews |
| 2026-09-30 | tooling | a09bf66e | fable-5-1 | opus | 1 | - | 11 | 74k | 27 | audit of every retro: review_round.py, preflight.py, three hook changes, fork rule, models per role, skill budget, archive; 1 Opus pair (cyber-deck-v2 v10 5.9 vs cyber-model v09 5.0, same instrument) |
| 2026-09-30 | aztechno-building | 3d94ac6b | opus-5-5 | opus | 19 | 6.5 | 117 | 355k | 132 | first architecture: 3 Sonnet research agents, 16 Opus reviews + 3 calibrations, 3 Fable consults; slope stop at round 7, fork to a photographic output stage (2x, unsharp, JPEG) broke the 5.3-5.9 plateau; final v16 calibrated 6.4 |
| 2026-10-02 | plotter-blend | b16b0eec | fable-5-1 | opus | 7 | 7.2 | 74 | 116k | 50 | first vector output (SVG strokes for a pen plotter, scored on a raster of the SVG): 1 Opus + 2 Sonnet research agents, 1 Opus plan consult, 6 Opus reviews + calibration; 6.0 → 7.2 in sequence, but the blind pair put v05 at 6.4 and v06 at 6.3; budget set to 6, no fork (the top ask flipped between rounds 1 and 6: draw through vs cut at the limb) |
| 2026-10-02 | plotter-forms | b16b0eec | fable-5-1 | opus | 9 | 7.1 | 52 | 225k | 145 | same session as plotter-blend (its row subtracted): a 50-form line-art catalogue with no reference images; 2 Sonnet research agents, 2 Opus advisor consults, 5 Opus reviews + 2 blind pairs; flat by round (6.8, 7.0, 7.0, 7.1, 6.8) while every pair preferred the newer sheet; final 7.1 in the second pair (v06 6.7 both times); no fork (a catalogue) |
| 2026-10-03 | apartment-model | 9e84a6fd | opus-5-5 | opus | 15 | 7.9 | 84 | 316k | 300 | first interior from a LiDAR scan + 7 phone photos (user's own flat): 4 Sonnet research agents, 3 Fable consults (plan, edge beams, fork), 12 Opus reviews + 1 calibration (v07 7.3 > v08 7.1); fork at round 8 to a joint fit of P + cameras (v09 8.1); brief revised at v10 after a user fact (secondary glazing), v12 7.9 with all pixel targets hit; user stopped the loop at 12 |
