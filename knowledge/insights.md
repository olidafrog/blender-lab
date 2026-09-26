# Insights

Lessons deeper than one Blender feature. Add one when a session changes how we should approach the next project.

- **Find out how the reference was really made.** In `wonder-printed-plastic` the first idea (a physical diffuser blurs the print) was wrong. The references were blurred digitally and then laser-printed. Building the real process raised the score more than any tuning did.
- **Build the research's finding first.** In `printed-plastic` the research said "blur in 2D before the print" before v01. The build modelled physical depth instead, and plateaued at 6.1–6.8 until v13 finally used the research. About 70 minutes lost.
- **Most "look" problems early on are render bugs.** Out-of-focus DOF, aliasing and a flipped angle were each reviewed as texture problems for several rounds. Check correctness before taste.
- **A repeated complaint means the mechanism is wrong.** When tuning values stops moving a reviewer's structural complaint, rebuild that part a different way.
- **Reviewers are noisy instruments.** Treat one score as ±0.4. Trust trends and recurring complaints, not single rounds.
- **Measure before you ask for an opinion.** Pixel sampling and small metrics scripts are cheap. Reviews are expensive and noisy.
- **Build every value into the script.** When the whole scene rebuilds from `build.py`, you can branch, compare and roll back. A hand-edited `.blend` loses that.
- **Expose the controls a designer will reach for.** Named node-group inputs with ranges, plus a `HOW_TO_TWEAK` text block, turn an experiment into a tool.
- **Show progress without being asked.** The user asked "are you finished?" 43 minutes into a long loop with no view of progress. Keep `PROGRESS.md` current.
- **One control, one place.** `wonder-popart` (each material is one node with plain-language inputs and ranges) was the hand-off that worked. `printed-plastic` spread blur radius over three nodes and a custom property.
