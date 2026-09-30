# cyber-model

## Brief

new experiment call it 'cyber-model' [Image #2] The goal is to create something similar to this reference. This is a challenge in hard surface modeling, so I want you to do a lot of research into that because that technique is exactly what's being used here. And it's quite a specific technique. There's a lot of Blender-specific tutorials and resources on it. So you can dispatch an additional two Sonnet agents to help you with research. And for the reviewer, I actually want you to use a Sonnet agent as well. This is a bit of a test of how Sonnet agents perform in this particular challenge. Specifically for this one, I'd like you to report your learnings at the end of the session, but don't actually add them to the learnings file unless I say so. I want to review all of the output and decide what we actually take from this as it's a bit of a test of sonnet performance.

## Overrides for this experiment (from the brief)

- Research: two Sonnet subagents help with the web research.
- Reviewer: a **Sonnet** subagent every round (not Opus). This is a test of Sonnet on hard-surface work. Scores do not compare with Opus-reviewed experiments.
- Advisor: an **Opus** subagent is the second opinion (plan stage, the 3-review mark, and whenever a review calls the whole form wrong). The user asked for it mid-session.
- Learnings: do **not** write to `knowledge/` or `LEARNINGS.md`. Report the proposed learnings in the final reply. The user decides what to keep.

## References

- `references/ref_radio.jpg` (736×552) — "DT-03 Multifunction Radio Device" by AFI. A sci-fi handheld radio in dark matte hard-surface plastic and metal: antenna, coiled cord, backlit LCD, knobs, gear, panel lines, screws, edge wear. Grey studio backdrop, one big soft key from the upper right, three-quarter high camera. Take: the hard-surface form language (panel breaks, chamfered/bevelled edges, layered plates, greebles), the material split (satin black polymer, brushed steel, dark green-grey rubber, cyan LCD), and the lighting.

## Target

Score 8.5 from the reviewer. (Sonnet reviewer; scale does not match Opus.)

## Budget

10 review rounds. When they are spent, `review-render` stops and reports; the user can extend it.

## Deliverables

- `output/FINAL_cyber-model.png`
- `output/cyber-model.blend` with a `HOW_TO_TWEAK` text block
