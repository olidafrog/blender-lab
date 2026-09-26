---
name: review-render
description: Use when a Blender experiment render needs scoring, judging or critique against its brief and references, when deciding what to fix next in a look-dev iteration, or when the user asks for a review, a judge, a score, or "how close is it".
---

# Review a render

One round of the adversarial review loop. The reviewer is a fresh subagent that sees only the brief, the references and the render. It never sees the build history, so it cannot grade the effort. Background: `knowledge/process/review-loop.md`.

## Steps

1. **Find the render.** Default: the newest file in `experiments/<name>/renders/`. Call its version `vNN` from the filename. If it is under about 1200 px wide, re-render it at `--scale 1` first. Crops of a small render repeat the full frame and hide nothing.
2. **Reviewer brief.** If `reviews/REVIEWER_PROMPT.md` exists, use it unchanged. Scores are only comparable when the brief is fixed. If it does not exist, fill `REVIEWER_PROMPT.template.md` from `BRIEF.md`, `references/` and any research notes, show it to the user, and save it. Change it later only if the user asks; then note in the next review that scores reset.
3. **Crops.** Run `tools/blender.sh tools/crops.py <render> 512 experiments/<name>/reviews/crops_vNN`. Add `x,y` points for any area a previous review flagged. For "recreate this image" work, also run `tools/compare.py` against the main reference.
4. **Spawn the reviewer** with the Agent tool (general-purpose, model opus). Its prompt is: the contents of `REVIEWER_PROMPT.md`, then the absolute paths of the render, each crop and each reference, then "Write your review to `<abs path>/reviews/review_vNN.md`." Pass nothing else: no build notes, no earlier scores, no hopes.
5. **Report** to the user, short:
   - score this round, and the trend from earlier `review_v*.md` files,
   - the single top-ranked problem and your planned fix,
   - any complaint that repeats from earlier rounds (flag it: likely a mechanism problem, not a value),
   - any contradiction with an earlier round, and which way the brief and the measured pixels point.

## Rules

- Fix one ranked problem per round.
- If the last three scores are within 0.2 and only crop-level notes remain, recommend stopping.
- If a new review contradicts an old one, the brief and references decide, not the newer reviewer.
- Log surprises in the experiment's `LEARNINGS.md`.
