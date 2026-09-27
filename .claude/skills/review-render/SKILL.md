---
name: review-render
description: Use when a Blender experiment render needs scoring, judging or critique against its brief and references, when deciding what to fix next in a look-dev iteration, or when the user asks for a review, a judge, a score, or "how close is it".
---

# Review a render

One round of the adversarial review loop. The reviewer is a fresh Opus subagent that sees only the brief, the references and the render. It never sees the build history or your reasoning, so it cannot grade effort or be argued with. This file holds the rules; the evidence behind them is in `knowledge/process/review-loop.md`.

## Before round 1 only: correctness pass

Reviewers misread render bugs as look problems (DOF blur as "noise", aliasing as "fabric"), and each costs rounds. Check these yourself first:
- DOF off, or focus on an empty at the area that matters.
- Any fine pattern: its pitch in pixels at the review resolution. Under ~4 px → render 2× and downsample.
- Angles and directions of patterns and lights match the reference.
- A flat-grey material override render, to see geometry, seams and bevels without shading. For glossy or mirror subjects, also a mirror override: diffuse clay hides smooth-shaded caps that render as domes.
- For reflective subjects, an isolation set before any tuning: the subject alone, each shader component alone, each light group off. One render per suspect finds a cause faster than guessing.
- If the subject departs from the references in a way a reviewer could mistake for a defect, state it under "Design facts" in the reviewer brief now.
- Exposure: the subject's median value against the main reference's (a few lines of PIL). Re-check it after any change that removes a veil or spill; a dim render reads to reviewers as a colour or material problem.
- A veil or wash you cannot explain: render one light at a time at 25% scale, 64 samples (~3 s each), before tuning anything.
- Video: diff two consecutive frames in a static patch of sky. Grain and any noise must change; frozen grain reads as lens dirt and no reviewer caught it for eight versions.
- Each compositor effect routed alone to the output (blurs, glows, crescent, masks): it must visibly change pixels. A 0 px blur looks like "the effect is missing" and reviewers will ask for it round after round.

## Steps

1. **Find the render and check the budget.** Default: the newest file in `experiments/<name>/renders/`. Call its version `vNN`. Under about 1200 px wide → re-render at `--scale 1` first; crops of a small render hide nothing. Count the `reviews/review_v*.md` files. If they reach the Budget in `BRIEF.md` (default 10), do not review; go to **Stopping**.
2. **Gate: prove the change reached the pixels.** Run
   `tools/blender.sh tools/metrics.py <previous render> <this render> <x,y[,size]>`
   with a target crop on the area you changed. If it prints `NO CHANGE`, do not spend a review: find why the change did not show, fix it, render again. With one path it prints stats (levels, clipping, gradients); check them against the numeric targets in `RESEARCH.md`.
3. **Reviewer brief.** If `reviews/REVIEWER_PROMPT.md` exists, use it unchanged; scores only compare when it is fixed. Otherwise fill `REVIEWER_PROMPT.template.md` from `BRIEF.md`, `references/` and `RESEARCH.md` (including its numeric targets) and save it. If the experiment has a metrics script, freeze it and name it in the prompt. Change the prompt only if the user asks; then note that scores reset.
4. **Crops.** Round 1: `tools/blender.sh tools/crops.py <render> 512 experiments/<name>/reviews/crops_vNN` for the centre and quadrants, plus `x,y` points for any area the user flagged. Later rounds: the full frame plus only the crops of areas the last review or the user flagged, and the area you changed. Images are most of a review's cost. For "recreate this image" work, also run `tools/compare.py` against the main reference.
   For a video: a 3×3 contact sheet of labelled frames plus six consecutive 1:1 crops of one patch (motion), e.g. `experiments/eclipse-glow/scripts/rise_sheet.sh`. Before acting on a motion complaint, measure it against a control render with the effect off.
5. **Spawn the reviewer** with the Agent tool: `subagent_type: general-purpose`, `model: opus`. Always Opus, every round, even for a quick check; scores from other models do not compare. A new agent every round; never resume or message an old reviewer. Its prompt is exactly the output of `python tools/review_prompt.py <name> vNN` (the contents of `REVIEWER_PROMPT.md`, the absolute paths of the render, each crop and each reference, then "Write your review to ..."). Nothing else: no change list, no earlier scores, no explanations.
6. **Snapshot** `scripts/build.py` to `reviews/build_vNN.py`, so any version can be diffed or rebuilt.
7. **Update `PROGRESS.md`** in the experiment: one table row per version (version, score, the one change, cost, render path), newest first. Cost is the Blender runs and minutes since the last row. The user reads this to follow along.
8. **Carry on.** Do not stop for approval between rounds; the user follows `PROGRESS.md`. Check **Stopping** after each review.

## Stopping

Stop the loop when any of these holds:
- **Budget spent.** The review count reached the Budget in `BRIEF.md`.
- **Slope flat.** From round 6: the best score of the last three rounds does not beat the best of the three before by 0.3 or more. One score is ±0.4, so compare bests of three, not single rounds.
- **Only taste is left.** The user's flagged problems are fixed, and reviewers now contradict each other round to round.

When you stop:
1. **Calibrate.** Spawn one more fresh Opus reviewer. Give it `REVIEWER_PROMPT.md` and two renders, the final and the best earlier version, labelled A and B in random order. Ask for a score and the top problem for each, in the same format, written to `reviews/calibration.md`. Record the pair under Calibration in `PROGRESS.md`. If the final does not beat the earlier version, say so; finish from the better one.
2. **Report:** score and trend, the plateau, the top-ranked problem, any complaint that repeated (a mechanism problem), and one to three mechanism candidates for the next version. Say the user can extend the budget.
3. Run `/finish-experiment`.

## Rules

- Fix one ranked problem per round. Apply research changes one lever at a time too.
- If the same complaint survives two rounds of value changes, stop tuning. Change the mechanism, and run `/research-reference` for that effect.
- The target is the brief and references, never an earlier version.
- On a contradiction between rounds, the brief, the numeric targets and the measured pixels decide.
- If the top asks contradict each other across rounds (a trade-off, not a bug), stop tuning: expose it as one control, name it in `PROGRESS.md` and `HOW_TO_TWEAK`, and hand it to the designer.
- If a complaint is numeric (coverage, hue count, clipping), write a metrics script and tune against it locally; review only the result.
- When the user is happy, run `/finish-experiment`.
- Log surprises in the experiment's `LEARNINGS.md`: facts under Learnings, anything that slowed the loop or a skill got wrong under Process, and why a version took many rounds under Cost.
