# Review loop

Each experiment improves in a loop: render, have an adversarial reviewer score it, fix the top problem, render again. `/review-render` runs one round.

## Setup

- Write the reviewer brief once, as `reviews/REVIEWER_PROMPT.md`. Keep it the same every round, so scores stay comparable.
- The brief holds: the designer's brief word for word; paths to every reference and to close crops of them; research findings; what to judge and what not to penalise; the calibration (5 = generic, 7 = good, 8.5 = ship it); the output format (score, what works, ranked problems with CG fixes, what 8.5 needs).
- Use a fresh subagent each round. It must not see the build history, or it grades the effort instead of the image.
- Give the reviewer 1:1 crops as well as the full frame. Without crops it misses aliasing, seams and ink texture. Review a full-scale render: crops of a quarter-scale render only repeat the frame.
- Save each review to `reviews/review_vNN.md`, so the history survives a context reset.

## Working the loop

- Research how the reference was made before you build. See [Insights](../insights.md).
- Fix one ranked problem per round. When several things change at once and the score drops, you cannot find the cause.
- Measure before you spend a review. Sample pixels in crops, or run a metrics script, to confirm a fix.
- Act on complaints that recur across rounds. The same image scores ±0.4 between reviewers, and consecutive reviewers often contradict each other (thinner then thicker). On a contradiction, trust the brief, the references and the measured pixels.
- Reviewers describe structure ("two overlapping circles", "ears") better than numbers. When a structural complaint repeats, stop tuning values and look at a crop. The fix is usually a different mechanism.
- Do not spend rounds on changes that only show at 400% zoom unless the reviewer names them.
- Test swappable content (a text lockup, another subject) before you finish. It shows problems the hero content hides.

## When to stop

- Scores rise fast (4.6 → 7.5) and then slowly. The last 0.5 comes from crop-level detail.
- Stop when three reviews in a row sit at the same score with only small notes left.
