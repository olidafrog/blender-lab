---
name: review-render
description: Use when a Blender experiment render needs scoring, judging or critique against its brief and references, when deciding what to fix next in a look-dev iteration, or when the user asks for a review, a judge, a score, or "how close is it".
---

# Review a render

One round of the adversarial review loop. The reviewer is a fresh Opus subagent that sees only the brief, the references and the render, so it cannot grade effort or be argued with. The evidence behind these rules is in `knowledge/process/review-loop.md`.

## Models

- **Reviewer: Opus, every round.** It is the measuring instrument; scores from another model do not compare. If the user names another reviewer model, use it for the whole experiment and say so in `PROGRESS.md`.
- **Advisor: a model other than the one building.** Opus if you are Fable, Fable otherwise, or the one the user named. A fresh agent each time, given the references, the latest render and `build.py`. Ask which mechanism is wrong and what should replace it; it may run test renders. No scores, no reviews, no asking for values. Log its answer and your change in `PROGRESS.md`.

## Before round 1 only: correctness pass

Reviewers misread render bugs as look problems (DOF blur as "noise", aliasing as "fabric"), and each costs rounds.

**Preflight sheet.** Run `build.py --out vNN --preflight` (a build without the flag: `tools/preflight.py` on its saved `.blend`). Round 1 is refused without it. Read every tile:
- *clay*: geometry, seams, bevels, intersections.
- *mirror*: smooth-shaded caps that render as domes, bad normals. Clay hides these.
- *albedo0*: what is still bright is reflection or spill, such as a softbox mirrored in a flat top.
- *scatter0*: subsurface that fills grooves, draws crease lines or hides bump detail.
- *each light alone*: which light carries a veil or wash.

For a suspect the sheet does not isolate (one shader component, an emissive mesh), render it alone before guessing.

**Checks the sheet cannot make:**
- DOF off, or focus on an empty at the area that matters.
- Any fine pattern: its pitch in pixels at the review resolution. Under ~4 px → render 2× and downsample.
- Angles and directions of patterns and lights match the reference.
- Exposure: the subject's median against the main reference's (`tools/measure.py`). Re-check after removing a veil or spill; a dim render reads as a material problem.
- A design fact a reviewer could take for a defect: state it under "Design facts" in the reviewer brief now.
- Each compositor effect routed alone to the output: it must visibly change pixels. A 0 px blur reads as "the effect is missing" round after round.
- Video: diff two consecutive frames in a static patch. Grain must change; frozen grain reads as lens dirt.

## Steps

1. **Render at review size.** The version is `renders/vNN.png`. Under about 1200 px wide → re-render at `--scale 1` first; crops of a small render hide nothing.
2. **Reviewer brief.** If `reviews/REVIEWER_PROMPT.md` exists, use it unchanged; scores only compare when it is fixed. Otherwise fill `REVIEWER_PROMPT.template.md` from `BRIEF.md`, `references/` and `RESEARCH.md` (numeric targets, design facts; the checklist, sub-scores and anchor are optional) and save it. Freeze any metrics script and name it in the prompt. Change the prompt only if the user asks; scores then reset.
3. **Prepare the round:** `python3 tools/review_round.py <name> vNN [x,y ...]`. It checks the budget and the preflight sheet, proves the change reached the pixels, makes the crops, snapshots `build.py` to `snapshots/` and writes the prompt. The `x,y` points are the area you changed plus each area the last review or the user flagged. After round 1 they are the only crops the reviewer gets. If it stops, fix what it names (`NO CHANGE`: find why the change did not show, render again). Do not build the round by hand.
   - Check the gate's printed stats against the numeric targets in `RESEARCH.md`. For "recreate this image" work, also run `tools/compare.py` against the main reference.
   - From round 2, `--with-prev` adds a blind pair with the last reviewed render.
   - Video: `tools/video_sheet.sh` (contact sheet, six consecutive 1:1 crops). Before acting on a motion complaint, measure it against a control render with the effect off.
4. **Spawn the reviewer** with the Agent tool: `subagent_type: general-purpose`, `model: opus`, and exactly the one-line prompt the tool printed. A new agent every round; never resume an old one. Add nothing: no change list, no earlier scores.
5. **Update `PROGRESS.md`**: one table row per version (version, score, the one change, cost, render path), newest first. Cost is the Blender runs and minutes since the last row. Then carry on without asking; check **Stopping** after each review.

## Stopping

Stop the loop when any of these holds:
- **Budget spent.** The review count reached the Budget in `BRIEF.md`.
- **Slope flat.** From round 6: the best score of the last three rounds does not beat the best of the three before by 0.3 or more. One score is ±0.4, so compare bests of three, not single rounds.
- **Only taste is left.** The user's flagged problems are fixed, and reviewers now contradict each other round to round.

When you stop:
1. **Calibrate.** `python3 tools/review_round.py <name> --pair <final> <best earlier>` copies the two renders to neutral names in random order and writes the prompt; spawn one fresh Opus reviewer with it. Read `snapshots/calibration_key.txt` only after the review. Record the pair under Calibration in `PROGRESS.md`. The winner is the version to continue or finish from.
2. **Fork once if the target is still far.** If the winner is more than 1.0 under the Target in `BRIEF.md`, and the experiment has not forked and the brief does not say "no fork", do not finish. Ask the advisor for the mechanism most likely at fault and two replacements. Build the best candidate as the next version in the same experiment, with the same `REVIEWER_PROMPT.md`. Raise the Budget in `BRIEF.md` by 6 (the new total as its first number; `review_round.py` reads that) and log "Fork: <old mechanism> → <new>" in `PROGRESS.md`. An infeasible candidate gets three attempts, then take the next. In the fork only the budget and the taste rule stop the loop. Then calibrate the fork's best against the pre-fork winner and finish from the better one.
3. **Report:** score and trend, the top-ranked problem, any complaint that repeated, and one to three mechanism candidates for a next version.
4. Run `/finish-experiment`.

## Rules

- Fix one ranked problem per round. Apply research changes one lever at a time too.
- If the same complaint survives two rounds of value changes, stop tuning. Change the mechanism, and run `/research-reference` for that effect.
- Consult the advisor before the next round when a review after round 1 calls the whole form wrong ("barrels", "inflatable", "a bucket", "plastic"), or when a measured target misses three rounds running despite changes aimed at it.
- The target is the brief and references, never an earlier version.
- On a contradiction between rounds, the brief, the numeric targets and the measured pixels decide.
- When the review instrument changes (composites, other crops, a changed prompt), re-score one known render with it first. Only compare scores within one instrument.
- If the top asks contradict each other across rounds (a trade-off, not a bug), stop tuning: expose it as one control, name it in `PROGRESS.md` and `HOW_TO_TWEAK`, and hand it to the designer.
- If a complaint is numeric (coverage, hue count, clipping), write a metrics script and tune against it locally; review only the result.
- Log surprises in the experiment's `LEARNINGS.md`: facts under Learnings, anything that slowed the loop or a skill got wrong under Process, and why a version took many rounds under Cost.
