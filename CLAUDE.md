# blender-lab

Blender experiments, driven headlessly from Python. One folder per experiment. What we learn goes into `knowledge/`, and every new experiment starts from it. Sibling lab for 2D and Photoshop: `~/GitHub/photoshop-lab`.

Runs on two machines: Mac (Blender 5.2, Metal) and Windows (Blender 4.4, OptiX). Scripts can break across the version gap; see [API changes](knowledge/gotchas/api-changes.md).

## Run

```bash
tools/blender.sh <script.py> [script args]      # from the repo root
tools/blender.sh tools/smoke_test.py            # check the toolchain (~5 s)
```

It finds Blender on either machine, runs headless with `--factory-startup` and a real exit code, and filters the output. `BLENDER=`, `BLEND=`, `PREFS=1`, `VERBOSE=1` change that; see the script header.

## Blender docs

`reference/` holds a local copy of the Blender docs: an exact API dump of the installed version, the Python API docs, the manual and the release notes. It is not in git; build it with `tools/fetch_docs.sh`. Look names up there before guessing (`blender-docs` skill).

## The pipeline — the default for every experiment

Any request to start an experiment, make a new version, match a reference, or improve a look runs this pipeline, whether or not the user names a skill:

1. `new-experiment` (new) — or read the experiment's `BRIEF.md`, `PROGRESS.md` and `LEARNINGS.md` (existing).
2. `research-reference` — before building. On a new version, rerun it for any effect a review said is still wrong.
3. Build, then `review-render` in a loop until its stop rule or the round budget in `BRIEF.md`; on a stall it forks once to a new mechanism.
4. `finish-experiment` — final render plus an editable `.blend` with one control node per material.
5. `capture-learnings` — knowledge plus the process retro.

Invoke each skill with the Skill tool; do not work from memory of what it says. Skip a step only when the user says so ("no review", "just a quick test"), and note the skip in `PROGRESS.md`. Tasks that are not look work (fix a script, convert a model, set up tooling) skip steps 2–4.

Hooks check the artifacts, not the skill names: edits to `build.py` (by any tool) wait for a `RESEARCH.md` with Sources and a link (or `research skipped: <why>` in `PROGRESS.md`); shell loops around `blender.sh --set` are blocked in favour of `tools/sweep.sh`; before stopping, each experiment rendered this session needs a review of its newest version and a learnings capture that names it.

**Models.** The builder is the session's model (Fable by default). The reviewer is always Opus. The advisor is a model other than the builder, consulted on mechanisms at the plan stage and when a loop stalls. Web research fans out to Sonnet subagents. The rules live in `review-render` and `research-reference`; the scoreboard records the builder and reviewer per session.

Read [knowledge/README.md](knowledge/README.md) and the entries that touch the task before starting.

## Skills

- `/new-experiment` — scaffold an experiment and load relevant learnings.
- `/research-reference` — work out how the reference was made and find Blender techniques on the web, before building.
- `/review-render` — one round of the adversarial review loop (always an Opus reviewer).
- `blender-docs` — how to look things up in `reference/`. Loads by itself when writing bpy code.
- `/finish-experiment` — final PNG plus an editable `.blend` where each material is one control node.
- `/sync-tweaks` — bring values the designer changed in a saved `.blend` back into `build.py`'s `P`.
- `/capture-learnings` — promote this session's lessons into `knowledge/`, log the session's cost in `knowledge/process/scoreboard.md`, and run the process retro.

## Layout

- `experiments/<name>/` — `BRIEF.md`, `RESEARCH.md`, `PROGRESS.md`, `references/`, `assets/`, `scripts/build.py`, `renders/` (not in git), `reviews/`, `output/` (FINAL PNGs; `.blend` not in git), `LEARNINGS.md`.
- `tools/` — shared helpers: `common.py` (`enable_gpu`, `experiment_paths`, `LIBRARY`), `nodes.py` (one-node materials), `comp.py` (compositor with live preview), `compare.py`, `crop_compare.py`, `crops.py`, `screen_fft.py` (line-screen pitch and angle), `metrics.py` (pre-review gate: did the change reach the pixels), `review_round.py` (plain `python3`: one review round in one command: budget, preflight, gate, crops, snapshot, prompt; `--pair` for blind A/B), `preflight.py` (correctness sheet: clay, mirror, albedo 0, scatter 0, each light alone; `build.py --preflight`), `silhouette.py` (subject outline vs reference: IoU, band widths, overlay), `debug_views.py` (Workbench subject mask and four-view debug sheet), `mesh_profile.py` (an object's height along a line, from a build.py), `measure.py` (plain `python3`: same-procedure table for reference and render — backdrop corners, subject levels, blacks, grain), `fit_camera.py` (plain `python3`: camera from landmark pairs), `sweep.sh` (render one build per `--set` variant and tile them), `session_cost.py` (plain `python3`: what a session cost), `photo_finish.py` and `sharpness.py` (a photo reference's processing: 2× → unsharp → JPEG, and the gate), `measure_classes.py` (per-paint-colour table with regions masked out), `mirror_studio.py` (flag, ring lights and the mirror-direction check for mirror-like subjects), `video_encode.sh` and `video_sheet.sh` (encode a sequence; contact sheet and motion crops), `sync_tweaks.py` (GUI tweaks back into `P`).
- `knowledge/` — gotchas, process, insights, decisions.
- `library/` — reusable models, textures, HDRIs, materials, node groups.

## Conventions

- Work autonomously. The user kicks off an experiment and leaves it to run: research, build and review without stopping for approval, unless asked. Keep `PROGRESS.md` current so they can check in.
- Rebuild the scene from `build.py`. Every tunable value lives in its `P` dict; override with `--set key=value`. Never hand-edit a `.blend` and lose it on the next build.
- Never overwrite a render the user liked. Add a suffix.
- When something costs time, note it in the experiment's `LEARNINGS.md` straight away. Put friction with the process itself under Process, and why a version took many rounds under Cost. `/capture-learnings` turns these into skill and tool changes, logged in `knowledge/process/improvements.md`.
- Every final `.blend` is a hand-off: one control node per material (`tools/nodes.py`) with named inputs and ranges, a `HOW_TO_TWEAK` text block, and the compositor as one Post node with a live preview (`tools/comp.py`).

## Experiments

- `eclipse-glow` — camera-space normals and compositor glows. v1 (`eclipse_glow.py`, sphere) runs on 4.4 and 5.x; v2 (`build.py`, Wonder logomark) is 5.x only; `build_rise.py` makes the moonrise video from it; `build_sunrise.py` reworks that as a sunrise over hot water (contact highlight, mirage gap, haze).
- `wonder-minidisc` — logomark as a CD/MiniDisc (diffraction BSDF) in a moulded tinted case; mirror-direction studio. Built on 4.4.
- `opal-essence` — milky opalescent resin plate over hardware, 5-stop gradient backlight (editable stops), raised Wonder type. 5.x only (light/shadow linking, Volume Coefficients). Final 6.5/10; open items in its decision record.
- `clouds` — modular volumetric clouds (lobe tiers → GN `density` grid, Mie + albedo absorption); presets `pink_rod`, `pink_ring`, `sunset`, `tower`, `plume`; neon emitters inside the volume. 5.x only.
- `wax-seal` — sealing-wax seal as a live GN heightfield; the emblem is any curve, text or mesh object on the modifier (Wonder logomark by default), with size and bevel controls; short violet scatter. 5.x only. Final 6.4 (calibrated), open items in its decision record.
- `wax-seal-chaos` — seed-drawn fork of wax-seal: the seal sculpted as one SDF volume (pour ∪ bead − die), low 3° sun, matte Sheen wax; the emblem is the same swappable library field. Beat the original blind (6.6 vs 5.4). `scripts/sim.py` is the abandoned Mantaflow press. 5.x only.
- `roman-model` — first character model: stylised low-poly legionnaire, IK-posed from `P` (head units), body as jittered planar ring lofts, hand-built armour; `look=clay` (reference) or `look=legion` (colour). `tools/silhouette.py` is the IoU gate. 5.x.
- `cyber-model` — hard-surface sci-fi radio from one reference: stacked plates from a rectified plan, flat chamfers, black gaps by geometry, three linked lights; a test of a Sonnet reviewer with an Opus advisor. Final 6.7 (target 8.5), open items in its decision record. 5.x only (Boolean `material_mode`, light linking).
- `cyber-deck-v2` — the same radio redone with lab defaults: every shell a plan outline lofted through a designed section (`library/models/hardsurface-kit/hardsurface_kit.py`), profiled-cutter pockets, crest-only wear tag, one small key light. Final 6.4 (Opus; not comparable with cyber-model's Sonnet 6.7), open items in its decision record. 5.x only.
- `aztechno-building` — Freddy Mamani's Crucero del Sur (El Alto) as a photoreal architectural render: facade traced in reference pixels (`scripts/facade.py`) and built at true scale as extruded curve slabs, physical sun + 4000 m sky, coated glass reflecting sky and a street HDRI, photographic output stage (2x, unsharp, JPEG). Final 6.4, open items in its decision record. 5.x only.
- `threshold-orbit` — looping orbital diagram; lines bleed where they cross (blur → threshold in the compositor). v01 predates the pipeline.
- `wonder-printed-plastic`, `wonder-caustics`, `wonder-caustics-v2`, `wonder-popart` — Wonder look-dev. Blender 5.x, Metal only. They predate this layout: `refs/` not `references/`, finals at the folder root, and `--out` resolves against the shell's cwd.
