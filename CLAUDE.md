# blender-lab

Blender experiments, driven headlessly from Python. One folder per experiment. What we learn goes into `knowledge/`, and every new experiment starts from it.

Runs on two machines: Mac (Blender 5.2, Metal) and Windows (Blender 4.4, OptiX). Scripts can break across the version gap; see [API changes](knowledge/gotchas/api-changes.md).

## Run

```bash
tools/blender.sh <script.py> [script args]      # from the repo root
tools/blender.sh tools/smoke_test.py            # check the toolchain (~5 s)
```

It finds Blender on either machine, runs headless with `--factory-startup` and a real exit code, and filters the output. `BLENDER=`, `BLEND=`, `PREFS=1`, `VERBOSE=1` change that; see the script header.

## Blender docs

`reference/` holds a local copy of the Blender docs: an exact API dump of the installed version, the Python API docs, the manual and the release notes. It is not in git; build it with `tools/fetch_docs.sh`. Look names up there before guessing (`blender-docs` skill).

## Before you start

Read [knowledge/README.md](knowledge/README.md) and the entries that touch the task. `/new-experiment` does this for you.

## Skills

- `/new-experiment` — scaffold an experiment and load relevant learnings.
- `/research-reference` — work out how the reference was made and find Blender techniques on the web, before building.
- `/review-render` — one round of the adversarial review loop (always an Opus reviewer).
- `blender-docs` — how to look things up in `reference/`. Loads by itself when writing bpy code.
- `/finish-experiment` — final PNG plus an editable `.blend` where each material is one control node.
- `/capture-learnings` — promote this session's lessons into `knowledge/`. A Stop hook reminds you once per session.

## Layout

- `experiments/<name>/` — `BRIEF.md`, `RESEARCH.md`, `PROGRESS.md`, `references/`, `assets/`, `scripts/build.py`, `renders/` (not in git), `reviews/`, `output/` (FINAL PNGs; `.blend` not in git), `LEARNINGS.md`.
- `tools/` — shared helpers: `common.py` (`enable_gpu`, `experiment_paths`, `LIBRARY`), `nodes.py` (one-node materials), `comp.py` (compositor with live preview), `compare.py`, `crop_compare.py`, `crops.py`, `screen_fft.py` (line-screen pitch and angle).
- `knowledge/` — gotchas, process, insights, decisions.
- `library/` — reusable models, textures, HDRIs, materials, node groups.

## Conventions

- Work autonomously. The user kicks off an experiment and leaves it to run: research, build and review without stopping for approval, unless asked. Keep `PROGRESS.md` current so they can check in.

- Rebuild the scene from `build.py`. Every tunable value lives in its `P` dict; override with `--set key=value`. Never hand-edit a `.blend` and lose it on the next build.
- Put designer controls on named node-group inputs with ranges, and add a `HOW_TO_TWEAK` text block to the `.blend`.
- Never overwrite a render the user liked. Add a suffix.
- Fix one ranked problem per review round.
- When something costs time, note it in the experiment's `LEARNINGS.md` straight away. Put friction with the process itself under Process. `/capture-learnings` turns these into skill and tool changes, logged in `knowledge/process/improvements.md`.
- Every final `.blend` is a hand-off: one control node per material (`tools/nodes.py`), and the compositor as one Post node with a live preview (`tools/comp.py`).

## Experiments

- `eclipse-glow` — camera-space normals and compositor glows. Runs on 4.4 and 5.x.
- `wonder-printed-plastic`, `wonder-caustics`, `wonder-caustics-v2`, `wonder-popart` — Wonder look-dev. Blender 5.x, Metal only. They predate this layout: `refs/` not `references/`, finals at the folder root, and `--out` resolves against the shell's cwd.
