---
name: capture-learnings
description: Use at the end of a blender-lab session or experiment, before stopping, when the learnings nudge hook fires, or when the user says "capture learnings", "what did we learn", "retro", "improve the process", or "save the lessons". Also use when something cost real time mid-session and should not be lost.
---

# Capture learnings and improve the process

The goal is a system that gets better with every project. Two outputs: **knowledge** (facts about Blender and looks) and **process changes** (edits to the skills, templates and tools themselves).

## Steps

1. **Gather.** Read `knowledge/README.md`. Collect candidates from:
   - this conversation: errors, wrong API names, silent failures, retries, reviewer surprises, approaches that changed, anything the user corrected,
   - `LEARNINGS.md` in each experiment touched (Learnings and Process sections),
   - `PROGRESS.md`: where the score stalled, how many rounds each fix took, which change broke a plateau.
2. **Filter.** Keep a candidate only if a future session would act differently because of it. Drop what the code already shows, and one-off typos.
3. **Sort** each into one kind:
   - **Gotcha** → `knowledge/gotchas/<topic>.md`. Symptom, cause, fix.
   - **Process lesson** → `knowledge/process/`.
   - **Insight** → `knowledge/insights.md`. Only lessons that would change how we approach a different project.
   - **Decision** → `knowledge/decisions/<experiment>.md`.
   - **Reusable asset** → suggest moving it to `library/`; ask before moving.
   - **Process change** → step 5.
4. **Dedupe and write knowledge.** Search first (`grep -ri`). Sharpen an existing entry rather than add a near-copy; replace an entry a new fact proves wrong. Tag entries (`4.4`/`5.x`, `mac`/`win`, source). One to three lines each. Index new files in `knowledge/README.md`.
5. **Retro: change the process.** Ask of this session:
   - Where did time go that a skill, template or tool could have saved?
   - What did a skill tell us to do that was wrong, missing, or ignored?
   - What worked that no skill encodes yet?
   - What did the user have to ask for or correct?
   Then:
   - **Small, evidence-backed change** (a step, a rule, a template default, a helper in `tools/`): make it now, in the skill or file itself.
   - **Bigger change** (a new skill, a changed loop, anything risky): add it under Proposed in `knowledge/process/improvements.md` and tell the user.
   - Log every change made under Changed in `improvements.md`: date, evidence, what changed, which file.
6. **Clear** promoted items from each `LEARNINGS.md`. Leave anything not promoted.
7. **Report** a short list: knowledge changes, process changes made, proposals. If nothing qualified, say so.
