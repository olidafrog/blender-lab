# Review loop — evidence

The rules live in `.claude/skills/review-render/SKILL.md`. This file keeps the evidence behind them, so a retro can judge whether a rule still earns its place. Each bullet names the rule it produced.

## Reviewer setup

- **Reviewers see only the listed files** (step 6, `tools/review_prompt.py`). In `cyber-deck-v2` reviewers opened `reviews/build_vNN.py` snapshots and graded the diff ("only value changes"), and four read earlier reviews and `PROGRESS.md` before scoring. A general-purpose reviewer has file access; the folder it is pointed at must hold nothing but the brief and crops.
- **Fixed reviewer brief** (step 3). A reviewer that changed how it measured mid-run (`caustics-v2`) made the scores incomparable. The same holds for a metrics script.
- **Fresh Opus reviewer, no history** (step 5). A reviewer that saw the builder's arguments "accepted your read of the optics" and withdrew complaints. A reviewer that sees the history grades the effort.
- **Crops, at full scale** (steps 1 and 4). Without crops reviewers missed aliasing, seams and ink texture. The reviewer passed `caustics` v1 at 8.6 on 35–50% renders; the user then found jagged edges.
- **Capped output: 3 ranked problems, under 450 words, ranges for more or less** (reviewer template). Uncapped 20 KB reviews gave asks that fought each other.
- **Research findings and refusals in the brief** (template). Reviewers flag real optics as bugs, such as corner-prism refraction read as "floating chips", and ask for things that break the brief (octagon corners, a hollow shell against "solid perspex"). Put the decision in the reviewer brief, so they do not return. `caustics-v2`
- **Save each review to a file.** The history survives a context reset.

## Before round 1

- **Correctness pass** (skill, first section). In `printed-plastic` a DOF focus bug cost 3 rounds (read as "noise"), aliasing cost about 10 (read as "felt", "twill"), and a flipped screen angle ran until v16.
- **Numeric targets** (`research-reference` step 5). Without them, blur and black levels swung back and forth for 15 rounds in `printed-plastic`.
- **Correctness pass extras** (skill, first section). For glossy subjects render a mirror-material override too; diffuse clay hides bad normals. `minidisc`

## Working the loop

- **Gate on changed pixels** (step 2). Three `printed-plastic` rounds were lost to changes that never showed. In `eclipse-glow` v04 a blur fix left the frame identical to v03; `tools/metrics.py` reports 0.00% changed.
- **One ranked problem per round, one research lever at a time** (Rules). `caustics-v2` applied a whole diagnostic brief at once and fell from 5.6 to 4.6; 40 versions only got back to 8.3.
- **Anchor to the brief, not an earlier version** (Rules). `caustics-v2` was scored "still not v1", which rewarded the sharpness the user wanted gone.
- **Trust recurring complaints; on contradiction the brief, targets and pixels decide** (Rules). The same image scores ±0.4 between reviewers, and consecutive reviewers often contradict each other (thinner, then thicker).
- **A repeated structural complaint means a new mechanism** (Rules). Reviewers describe structure ("two overlapping circles", "ears") better than numbers. Every plateau (6.5–6.8, 7.7–7.9, 8.4) broke only with a new mechanism, never with tuning.
- **Reproduce the reviewer's own measures before each review** (step 2, `tools/metrics.py`). Gradient share, clipping and lit share predicted the direction of the score in `caustics-v2`.
- **Skip 400%-zoom changes** unless the reviewer names them. They cost a round and move nothing.
- **The user's markup is the strongest tie-breaker.** When the circled artefacts are fixed and only reviewer taste remains, say so and stop. `caustics-v2`
- **Hand score-neutral trade-offs to the user** as a `--set` override. `caustics-v2`
- **Test swappable content before finishing** (a text lockup, another subject). It shows problems the hero content hides.
- **State design facts in the reviewer brief from round 1** (correctness pass). When the subject departs from the references (a logo-shaped disc vs a round one), say so. `minidisc` lost four rounds at 6.2–6.3 to "the disc should show through the bands"; stating it broke the plateau.
- **Hand contradicting asks to the designer** (Rules). When the top asks flip across rounds (stronger tint vs more pink through that tint), expose the trade-off as one control. `minidisc`. In `clouds` the sun flipped from warm side key (v05) to front key (v06), and the colour from "too magenta" to "not lavender enough" (v04–v08).
- **Several targets in one experiment.** One fixed `REVIEWER_PROMPT.md` with a table that maps a render-name suffix to its reference (`v09_sunset` → ref 03) kept scores comparable across presets. `clouds`
- **Tune numeric complaints locally** (Rules). For coverage, hue families or clipping, write a small metric script and review only the result. `minidisc/scripts/disc_metrics.py` took the disc from 3 % to 21 % saturated in two local runs.
- **Video: contact sheet plus six consecutive 1:1 crops** (step 4). Reviewers still misjudge motion from stills ("the shimmer does not move" when it did). Before acting on a motion or "dark hole" complaint, measure against a control render. `eclipse-glow`

- **A second model on mechanism when the whole form is wrong** (Rules). In `roman-model` rounds 1–3 said "barrels", "inflatable" and "stacked barrels". A Fable advisor named the cause at once: subdivide + decimate cannot make planes. The rebuild changed the facet read in one round. The planning consult also cut SDF body fusion and set the skirt and helmet mechanisms.
- **Trust the reviewer's landmark numbers over your own read.** In `roman-model` the helmet was lowered by eye, "to sit into the shoulders", while four reviews measured it 20–35 px too low.
- **A measured target that misses three rounds is a mechanism problem too** (Rules). In `cyber-deck-v2` p5 sat at 20–23 through moats, undercuts and liners; a Fable consult (reviews withheld, test renders allowed) named the light rig and fixed it in one round (5.7 → 6.2).
- **A new review instrument needs a control** (Rules). Side-by-side composite reviews scored the original `wax-seal` final 5.8, against 6.4 from render-only crops. Re-score a known render with the new instrument before comparing numbers across it. `wax-seal-chaos`

- **A blind pair needs neutral file names** (`review_round.py --pair`). In `cyber-model` the "blind" pairwise question listed `v04.png` and `v05.png`, with the newer render always second; "picked the newer render nine times in nine" was not evidence. `audit 2026-09-30`
- **Prose steps decay, tool steps hold** (steps 3–4, `review_round.py`; the correctness pass, `preflight.py`). Across seven loops every hook and tool check held; the pixel gate ran on 4 of 11 rounds in `clouds`, the fewer-crops rule was never followed in `roman-model`, and the scatter-0 render was skipped in `wax-seal-chaos`. `audit 2026-09-30`
- **A reviewer on another model is another instrument** (Models). One Opus pair scored `cyber-deck-v2` v10 at 5.9 and `cyber-model` v09 at 5.0; the Sonnet reviewer had given that render 6.7. Opus built and reviewed every earlier experiment, so a Fable builder with an Opus reviewer is the first real separation. `audit 2026-09-30`

## A weaker reviewer and an advisor (cyber-model)

The user asked for a Sonnet reviewer and an Opus advisor on a hard-surface task, to test how Sonnet performs. Scores are not comparable with Opus-reviewed experiments.

- **A structured brief kept a Sonnet reviewer concrete.** Ten yes/no questions tied to places in the frame, a table measured by a script on both images (the reviewer was told to trust it over its own estimates), five weighted sub-scores, an anchor image of grey boxes as the 4, and from round 2 a blind pairwise question against the previous render. It flagged its own estimates as "my estimate". `cyber-model`
- **Absolute scores were anchored; the pair was sensitive.** Scores over ten rounds: 5.9, 5.8, 6.0, 5.9, 6.0, 6.5, 6.6, 6.5, 6.7, 6.4. The pair picked the newer render in rounds 2 to 10, including rounds where the score did not move. The last pair (v10 over v09) was reversed by the blind calibration (v09 6.7, v10 6.5), so a pair between near-identical renders is noise; use the pair to steer and the calibration to decide. `cyber-model`
- **A repeated top problem is a mechanism problem, and it is a usable signal.** "Blacks are grey" was the top or second problem in every round from 2 on; "edges pillowy" was flagged in rounds 3, 5 and 6. Value tuning did not move either. The changes that did were mechanisms: a device-only key (v04), a flat unhardened chamfer with flat shading (v07), and a black liner plus moats (v09). `cyber-model`
- **Two consults with an Opus advisor found what the reviews did not.** At the plan stage and after three reviews, mechanism only, with the reviews withheld. The advisor named the softbox reflecting in every flat top (verified with a base-colour-black render), the missing real gaps, and the bead-round edges. The reviewer never named the light cause. `cyber-model`
- **Advisor and reviewer disagreed on wall brightness** (lighter than tops against as dark as tops). A wall measured on the reference (about 13 mm tall, dark to mid) was the tie-break, in line with "the brief, the targets and the pixels decide". `cyber-model`
- **The 12-level tolerance is wrong for small values.** Grain std and share under 12 passed every round while off by a third to 3×; the reviewer overrode the rule in its text from round 3. Give ratio tolerances for such rows. `cyber-model`
- **Keep the calibration blind.** The A/B request carried `renders/v09.png` and `renders/v10.png`, so the reviewer could order them. Copy the two renders to neutral names first. `cyber-model`
- **Sonnet as a research agent was good when told to test.** One agent ran seven headless tests and reported measured normal errors, timings and a coplanar-cutter failure; its untested claim, that joined cutters are fine, was wrong for overlapping cutters. Ask research agents to run small tests, and to say which advice was only read. `cyber-model`

## Stopping

- **Budget and slope rule** (Stopping). Scores rise fast (4.6 → 7.5) and then slowly; the last 0.5 comes from crop-level detail. `printed-plastic` ran 29 versions to 8.4 and `caustics-v2` 45 to 8.3, while `caustics` v1 reached 8.6 in 22. The old rule, "three scores within 0.2", almost never fired with ±0.4 noise.
- **Calibration at the end** (Stopping). Nothing checked whether the final beat an earlier version; the v1-versus-v2 caustics numbers suggest late versions sometimes do not.
- **Reviewers contradicting each other round to round is taste** (Stopping). Haze gone by 40 px, then 150 px. `eclipse-glow`
- Set numeric targets relative to the subject, not only the physics. A "20–60 px core" target fought 110 px wide logo bars for eight rounds. `eclipse-glow`
- Judge glow and highlight strength at full scale. Blur radii scale with the render and grain does not, so half-scale tests look far more blown out. `eclipse-glow`
- Before acting on a highlight or reflection complaint, sample a pixel column across the line. Twice the cause was a different node than the one being tuned (a fade reach, a tint). `eclipse-glow`
