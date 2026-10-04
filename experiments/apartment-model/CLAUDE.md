# apartment-model

A photoreal Blender model of the user's own flat: Flat 233, Manhattan Building, Bow Quarter, London E3. It is a long-running project. The user adds to it in chunks: one piece of furniture, one room or one material at a time. Each chunk is one **round** of the lab pipeline (root `CLAUDE.md`).

Blender 5.x only (Mac, Metal). Everything is rebuilt from `scripts/build.py`; every tunable value is in its `P` dict.

## State (2026-10-04)

- **Round one, shell (v01–v12):** the living room built from a LiDAR scan, the plan and 8 phone photos. Final v12, **7.9**. The rest of the flat is grey boxes.
- **Round two, materials (v13–v18):** the brick window wall and the herringbone oak floor. Final v18, **6.2** (calibrated 5.9).
- **Round three, the sofa (v19–v26):** the Swyft Model 03 three-seater and ottoman in Pumice, from Swyft's sizes and drawings, placed from the scan and photos 1–2. Final v26, **6.7**. From this round the renders have a white balance per photo and the photographic output stage (`--scale 2 --finish`).
- **Next:** furniture piece by piece, then the other rooms. See [docs/roadmap.md](docs/roadmap.md).

## Read first

- [docs/flat.md](docs/flat.md): the flat itself. Rooms, levels, directions (plan "north" is not compass north), structure terms and the names they have in `build.py`.
- [docs/references.md](docs/references.md): every photo, scan and plan, what each is good for, and which ones not to trust.
- [docs/navigation.md](docs/navigation.md): which file does what, and which tool to use for which job.
- [docs/roadmap.md](docs/roadmap.md): what is left, open items and what is waiting on the user.
- [docs/adding-furniture.md](docs/adding-furniture.md): how to add a piece of furniture.
- [Decision record](../../knowledge/decisions/apartment-model.md): the mechanisms chosen and rejected in each round, and why.
- `BRIEF.md` (the user's words per round), `PROGRESS.md` (every version, advisor and stall-guard log), `RESEARCH.md` (measurements and sources).

## Run

From the repo root:

```bash
tools/blender.sh experiments/apartment-model/scripts/build.py --out v27 --views 1,2,3 --scale 2 --samples 64 --finish   # 2x, then sharpened JPEG at photo size
tools/blender.sh experiments/apartment-model/scripts/build.py --out wip --set furniture=False   # any P key
tools/blender.sh experiments/apartment-model/scripts/review_sheet.py v27 sofa                   # no "--"; mat for material rounds
python3 tools/review_round.py apartment-model v27 <x,y ...>
```

Three views at `--scale 2 --samples 64 --finish` take about 2 minutes on the M4 Max. Renders go to `renders/` (not in git).

## Rules for this folder

- **Measured, not guessed.** The scan is the truth for plan and heights. The 1:60 plan is the truth for rooms the scan did not reach. Photos give the detail. The user's tape measurements are from the iPhone Measure app (±3 cm).
- **Never use other flats' listings or plans for dimensions.** Bow Quarter flats differ. Only this flat's photos, scan and plan count.
- **Do not break what earlier rounds settled.** Geometry is frozen at v12 and the brick and floor at v18, unless the round is about them. A piece that replaces a grey block must not move the shell.
- **The kitchen layout on the plan is out of date.** The photos win.
- **Windows:** model only the factory windows, closed. The secondary glazing in the photos is not wanted.
- **Stairs:** 10 steps in two flights. Do not model them until the user sends photos.

## Starting a new round

1. Add `## Round N: <topic> (date)` to `BRIEF.md` with the user's words, the target and what is frozen.
2. Raise the first number in the Budget line by the round's review count (`review_round.py` reads it as the total).
3. Rename the current `reviews/REVIEWER_PROMPT.md` to `REVIEWER_PROMPT_<old topic>.md`, then write a new one for this round. Scores compare only within one round.
4. Keep numbering versions from the last one (v27 is next). The slope and stall rules count from the round's first version.
5. Before `finish-experiment` writes new finals, rename the current `output/FINAL_*.png` with the previous round's suffix (`_sofa`), as round one's are `_shell` and round two's `_materials`.
6. At the end, add the round to the decision record and update **State** above and `docs/roadmap.md`.
