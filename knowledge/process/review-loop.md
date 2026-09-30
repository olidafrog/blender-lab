# Review loop — evidence

The rules live in `.claude/skills/review-render/SKILL.md`. This file keeps the evidence behind them, so a retro can judge whether a rule still earns its place. Each bullet names the rule it produced.

## Reviewer setup

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

- **A second model on mechanism when the whole form is wrong** (Proposed in `improvements.md`). In `roman-model` rounds 1–3 said "barrels", "inflatable" and "stacked barrels". A Fable advisor named the cause at once: subdivide + decimate cannot make planes. The rebuild changed the facet read in one round. The planning consult also cut SDF body fusion and set the skirt and helmet mechanisms.
- **Trust the reviewer's landmark numbers over your own read.** In `roman-model` the helmet was lowered by eye, "to sit into the shoulders", while four reviews measured it 20–35 px too low.
- **A new review instrument needs a control** (Rules). Side-by-side composite reviews scored the original `wax-seal` final 5.8, against 6.4 from render-only crops. Re-score a known render with the new instrument before comparing numbers across it. `wax-seal-chaos`

## Stopping

- **Budget and slope rule** (Stopping). Scores rise fast (4.6 → 7.5) and then slowly; the last 0.5 comes from crop-level detail. `printed-plastic` ran 29 versions to 8.4 and `caustics-v2` 45 to 8.3, while `caustics` v1 reached 8.6 in 22. The old rule, "three scores within 0.2", almost never fired with ±0.4 noise.
- **Calibration at the end** (Stopping). Nothing checked whether the final beat an earlier version; the v1-versus-v2 caustics numbers suggest late versions sometimes do not.
- **Reviewers contradicting each other round to round is taste** (Stopping). Haze gone by 40 px, then 150 px. `eclipse-glow`
- Set numeric targets relative to the subject, not only the physics. A "20–60 px core" target fought 110 px wide logo bars for eight rounds. `eclipse-glow`
- Judge glow and highlight strength at full scale. Blur radii scale with the render and grain does not, so half-scale tests look far more blown out. `eclipse-glow`
- Before acting on a highlight or reflection complaint, sample a pixel column across the line. Twice the cause was a different node than the one being tuned (a fade reach, a tint). `eclipse-glow`
