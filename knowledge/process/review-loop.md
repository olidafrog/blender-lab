# Review loop

Each experiment improves in a loop: render, have an adversarial reviewer score it, fix the top problem, render again. `/review-render` runs one round.

## Setup

- Write the reviewer brief once, as `reviews/REVIEWER_PROMPT.md`. Keep it the same every round, so scores stay comparable.
- The brief holds: the designer's brief word for word; paths to every reference and to close crops of them; research findings; what to judge and what not to penalise; the calibration (5 = generic, 7 = good, 8.5 = ship it); the output format (score, what works, ranked problems with CG fixes, what 8.5 needs).
- Use a fresh subagent each round. It must not see the build history, or it grades the effort instead of the image.
- Give the reviewer 1:1 crops as well as the full frame. Without crops it misses aliasing, seams and ink texture. Review a full-scale render: crops of a quarter-scale render only repeat the frame.
- Save each review to `reviews/review_vNN.md`, so the history survives a context reset.

## Before round 1

- Run a correctness pass: DOF off or focused on an empty at the face, fine-pattern pitch checked in pixels, pattern angles checked, a flat-grey override render. In `printed-plastic` a DOF focus bug cost 3 rounds (read as "noise"), aliasing cost ~10 (read as "felt", "twill"), and a flipped screen angle ran until v16.
- Lock numeric targets from reference crops (core RGB, edge ramp in px, background level). Without them, blur and black levels swung back and forth for 15 rounds.

## Working the loop

- Research how the reference was made before you build. See [Insights](../insights.md).
- Fix one ranked problem per round. When several things change at once and the score drops, you cannot find the cause.
- Prove each fix reached the pixels before you spend a review. Three `printed-plastic` rounds were lost to changes that never showed.
- Freeze any metrics script and the reviewer prompt. A reviewer that changed how it measured mid-run (`caustics-v2`) made the numbers incomparable.
- Cap the reviewer at 3 ranked problems in under 450 words, and make it give a range when it asks for more or less. Uncapped 20 KB reviews gave asks that fought each other.
- Never pass your reasoning to the reviewer. A reviewer that saw the builder's arguments "accepted your read of the optics" and withdrew complaints.
- Apply research changes one lever at a time. `caustics-v2` applied a whole diagnostic brief at once and fell from 5.6 to 4.6; 40 versions only got back to 8.3.
- Anchor to the brief, not an earlier version. `caustics-v2` was scored "still not v1", which rewarded the sharpness the user wanted gone.
- Act on complaints that recur across rounds. The same image scores ±0.4 between reviewers, and consecutive reviewers often contradict each other (thinner then thicker). On a contradiction, trust the brief, the references and the measured pixels.
- The reviewer passed `caustics` v1 at 8.6 on 35–50% renders; the user then found jagged edges. Review at full scale.
- Reviewers describe structure ("two overlapping circles", "ears") better than numbers. When a structural complaint repeats, stop tuning values and look at a crop. The fix is usually a different mechanism.
- Do not spend rounds on changes that only show at 400% zoom unless the reviewer names them.
- Reproduce the reviewer's own measures (gradient fractions, connected components, clipping) in a script and run them before each review. `caustics-v2`
- The reviewer flags real optics as bugs, such as corner-prism refraction read as "floating chips". Decide from the brief whether to fix, retouch or keep, and say which in the reviewer brief. `caustics-v2`
- Refuse asks that break the brief (octagon corners, a hollow shell against "solid perspex") in the reviewer brief, so they do not return. `caustics-v2`
- The user's own markup is the strongest tie-breaker. When the circled artefacts are fixed and only reviewer taste remains, say so and stop. `caustics-v2`
- Some trade-offs have no score-neutral answer. Expose the value as a `--set` override and hand the choice to the user. `caustics-v2`
- Test swappable content (a text lockup, another subject) before you finish. It shows problems the hero content hides.

## When to stop

- Scores rise fast (4.6 → 7.5) and then slowly. The last 0.5 comes from crop-level detail.
- Every plateau (6.5–6.8, 7.7–7.9, 8.4) broke only with a new mechanism, never with tuning.
- Stop when three reviews in a row sit at the same score with only small notes left.
