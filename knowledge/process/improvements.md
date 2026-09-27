# Process improvements

How the system changes itself. `/capture-learnings` adds to this at the end of each session. Newest first.

## Proposed

- **Blender MCP for live sessions** (revisit later). Scripts stay the main engine for unattended runs. Add the official Blender Lab MCP (Blender 5.1+, so Mac only until Windows updates) for sessions at the GUI: copying tweaked values back into `build.py`, exploring old `.blend` files, quick back-and-forth. Rule if adopted: anything changed through MCP is written back to `build.py` before the session ends. The community `ahujasid/blender-mcp` adds Poly Haven and Sketchfab import. Links: https://www.blender.org/lab/mcp-server/, https://github.com/ahujasid/blender-mcp
- **`/sync-tweaks` skill** (can come before MCP). A headless script opens a hand-tweaked `.blend`, reads the control-node values and updates `P` in `build.py`. Evidence: tweaks made in the GUI are lost on the next rebuild.
- **Shared library** (revisit later). Fill `library/` and add tooling to append materials and node groups from it, and to import assets (Poly Haven). Candidates now: `wonder-caustics/assets/monochrome_studio_01_4k.hdr`, the pop art halftone and hatch groups, the printed-plastic blur group.

- **Port `eclipse-glow` to the 5.x compositor** so it runs on both machines. Evidence: it fails on the Mac with `'Scene' object has no attribute 'node_tree'`.
- **Shared metrics script in `tools/`**, generalised from `experiments/wonder-caustics-v2/scripts/metrics.py`, so every loop can prove a fix reached the pixels. Evidence: 3 wasted review rounds in `printed-plastic`; `minidisc/scripts/disc_metrics.py` (hue families, dark and clipped fractions) settled a 3-round disc complaint in two local runs.
- **Mirror-direction studio as a `tools/` helper** (flag + wedge lights + big-light angle check, from `wonder-minidisc/scripts/build.py`). Evidence: it took most of the minidisc session and applies to any mirror, foil or grating subject.
- **Reviewer "design facts" section in `REVIEWER_PROMPT.template.md`.** Evidence: `minidisc` lost four rounds to a design fact the reviewer read as a defect.

## Changed

- **2026-09-27 — First library materials.** `library/materials/cd_diffraction.blend` and `tinted_plastic.blend`, built by `library/materials/build_materials.py`, with their CC0 wear masks in `library/textures/imperfections/`. `wonder-minidisc` now imports its materials from the library, so it rebuilds on either machine after a clone (its maps were in a git-ignored folder). Asked for by the user.

- **2026-09-27 — Windows / Blender 4.4 support and review tooling** (`wonder-minidisc`). Evidence: the repo had never run end-to-end on Windows; the template crashed on 4.4 and `fetch_docs.sh` failed twice.
  - `tools/comp.py`: `LEGACY` branch for the 4.4 compositor (`scene.node_tree`, Composite, `OPEN_EXR` + `file_slots`, `Switch.check`). The new-experiment template's `post()` sets Glare properties on 4.4.
  - `tools/fetch_docs.sh` picks a working `python3`/`python`; `tools/html_to_text.py` reads and writes UTF-8.
  - `tools/review_prompt.py` assembles each round's reviewer prompt (it was pasted by hand 9 times). `review-render` step 5 uses it.
  - `review-render` correctness pass: mirror override for glossy subjects (a diffuse clay render hid the domed-cap bug for 3 rounds), an isolation set for reflective subjects (~30 guess renders), design facts in the brief. New rules: hand contradicting asks to the designer as a control; tune numeric complaints with a metrics script.
  - `new-experiment`: step 0 checks the machine (smoke test, `reference/`) before any experiment work. The template gains a `clay` override switch.

- **2026-09-26 — Pipeline enforced, not just described.** Added a pipeline section to `CLAUDE.md`, a `UserPromptSubmit` hook (`pipeline-reminder.sh`) that reminds Claude of it on experiment-like prompts, and a Stop-hook check that asks for a review round when a session rendered an experiment but never ran `review-render`. Evidence: across three sessions in blender-lab the only skill used was `capture-learnings`, and only because the hook forced it. The printed-plastic v2 session built a version with no research and no review. `threshold-orbit` was built in the retired folder with no skills at all. The old folders now carry a "MOVED" notice.

- **2026-09-26 — Local Blender docs.** `tools/fetch_docs.sh` builds `reference/` (not in git, about 65 MB of text): an exact API dump of the installed Blender (`tools/dump_api.py`, every type, enum and node socket), the Python API docs for 5.2 and 4.4, the manual source and the release notes. The `blender-docs` skill says when and how to look things up. Evidence: past traps (`MULTI_GGX`, `OPEN_EXR`, 5.x compositor sockets) were all exact-name questions that a lookup answers. Windows: run `tools/fetch_docs.sh` there to get the 4.4 dump.

- **2026-09-26 — Library `.blend` files are committed.** Added `!library/**/*.blend` to `.gitignore`, and a rule to `library/README.md` that a built model keeps its build script beside it. Evidence: `library/README.md` says library binaries are committed, but `*.blend` was ignored everywhere, so `wonder_logos.blend` would not reach the Windows machine. Files: `.gitignore`, `library/README.md`.
- **2026-09-26 — Screen FFT tool and visible tool output.** Added `tools/screen_fft.py`, ported from the Photoshop build; it reads ref1's lime screen as 2.04 px at 63.4°, matching that build's findings. `tools/blender.sh` now passes `[out]` lines, and `compare.py` and `crop_compare.py` print with that prefix. Evidence: a flipped screen angle in `printed-plastic` ran until v16; `compare.py` printed nothing through the filter. Files: `tools/screen_fft.py`, `tools/blender.sh`, `tools/compare.py`, `tools/crop_compare.py`.

- **2026-09-26 — Autonomous by default.** Removed approval gates from the research and review steps; the user follows `PROGRESS.md`. Evidence: the user wants to kick off experiments and let them run. Files: all skills.
- **2026-09-26 — Compositor hand-off.** `tools/comp.py`: raw EXR written in the same render, a Viewer for the backdrop, a Saved Render source, and a one-node Post group. Evidence: the user asked for live compositor tweaking; `wonder-caustics/scripts/comp.py` proved the EXR re-grade. Files: `tools/comp.py`, new-experiment template.
- **2026-09-26 — Review loop from past sessions.** Opus only, a fresh reviewer each round, a correctness pass before round 1, proving each fix reached the pixels, capped reviews, numeric targets, `PROGRESS.md`. Evidence: mining of the `printed-plastic` transcript and 46 reviews. Files: `review-render`, `research-reference`.
- **2026-09-26 — Research first, one-node materials.** Added `research-reference`, `finish-experiment` and `tools/nodes.py`. Evidence: `printed-plastic` ignored its research for 12 rounds; `wonder-popart`'s one-node materials were the hand-off that worked.
