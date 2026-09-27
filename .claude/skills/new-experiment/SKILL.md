---
name: new-experiment
description: Use when starting a new Blender experiment, look-dev test, or "recreate this image" task in blender-lab, or when the user says "new experiment", "start a new one", or gives a brief with no experiment folder yet.
---

# New experiment

Every experiment gets the same folder shape and starts from what past experiments learned.

## Steps

0. **Check the machine first.** `tools/blender.sh tools/smoke_test.py`, and check `reference/` exists (else run `tools/fetch_docs.sh` in the background). Setup problems (a 5.x-only helper on 4.4, a missing docs folder) should surface before any experiment work.
1. **Get the inputs.** You need a brief and reference images. Ask only if one is missing. Derive a short kebab-case name from the brief.
2. **Scaffold** `experiments/<name>/`:
   - `references/`, `assets/`, `renders/`, `reviews/`, `output/`, `scripts/`
   - Copy `templates/build.py` to `scripts/build.py`, and `BRIEF.md`, `LEARNINGS.md`, `PROGRESS.md` from `templates/` to the experiment root. Replace `__NAME__` with the name.
   - Paste the brief word for word into `BRIEF.md`. Copy references into `references/`.
   - Stop if the folder already exists. Never overwrite an experiment.
3. **Load the knowledge.** Read `knowledge/README.md`, then every file it indexes whose topic touches this brief (for example glass → `cycles.md` and the glass section of `shader-nodes.md`). Always read `process/review-loop.md` and `insights.md`.
4. **Note what applies.** Write to the top of `PROGRESS.md` (do not stop to ask):
   - which Blender version and machine you are on (`tools/blender.sh` prints it), and any `4.4`/`5.x` gotchas that apply,
   - the 3–8 gotchas and process notes most relevant to this brief,
5. **Research before building.** Run `/research-reference`. Do not build the real scene until `RESEARCH.md` exists.
6. **Smoke the template.** Run `tools/blender.sh experiments/<name>/scripts/build.py --out v00 --samples 16 --scale 0.25` to prove the scaffold renders. Then replace the placeholder scene.

## Conventions

- All tunable values go in the `P` dict. Override with `--set key=value`; never edit the `.blend` by hand.
- Name renders `v01`, `v02`… Never overwrite a render the user liked; add `_b`.
- Note surprises in `LEARNINGS.md` as they happen. `/capture-learnings` promotes them later.
- Anything reusable across experiments (a material, node group, model) belongs in `library/`. See `library/README.md`.
- Score versions with `/review-render`. End with `/finish-experiment`: a final PNG plus an editable `.blend` where each material is one control node.
- Build designer materials with `tools/nodes.py` from the start, not at the end.
