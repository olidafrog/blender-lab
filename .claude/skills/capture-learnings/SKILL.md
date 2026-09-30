---
name: capture-learnings
description: Use at the end of a blender-lab session or experiment, before stopping, when the learnings nudge hook fires, or when the user says "capture learnings", "what did we learn", "retro", "improve the process", or "save the lessons". Also use when something cost real time mid-session and should not be lost.
---

# Capture learnings and improve the process

The goal is a system that gets better with every project: better looks, in fewer rounds, for fewer tokens. Three outputs: **knowledge**, **process changes** (to the skills, templates and tools), and **a cost line** so the next retro can tell whether the changes helped.

## Steps

1. **Measure.** Run `python3 tools/session_cost.py --latest --scoreboard` and add its line to the table in `knowledge/process/scoreboard.md`. Fill the best-score cell from `PROGRESS.md` if the script left it as `-`, and check the Builder and Reviewer cells (a review on another model does not compare). Compare with earlier rows for the same kind of work and builder.
2. **Gather.** Read `knowledge/README.md`. Collect candidates from:
   - this conversation: errors, wrong API names, silent failures, retries, reviewer surprises, changed approaches, user corrections,
   - `LEARNINGS.md` in each experiment touched (Learnings, Process and Cost sections),
   - `PROGRESS.md`: where the score stalled, how many rounds and renders each fix took, which change broke a plateau.
3. **Filter.** Keep a candidate only if a future session would act differently because of it. Drop what the code already shows, and one-off typos.
4. **Sort** each into one kind:
   - **Gotcha** → `knowledge/gotchas/<topic>.md`. Symptom, cause, fix.
   - **Process lesson** → `knowledge/process/`.
   - **Cost** → why this session took the rounds, renders or tokens it did, for example "6 rounds because the blur was 0 px". It becomes a process change (step 6) or a Proposed entry.
   - **Insight** → `knowledge/insights.md`. Only lessons that would change how we approach a different project.
   - **Decision** → `knowledge/decisions/<experiment>.md`.
   - **Reusable asset** → suggest moving it to `library/`; ask before moving.
5. **Dedupe and write knowledge.** Search first (`grep -ri`). Sharpen an existing entry rather than add a near-copy; replace one a new fact proves wrong. Tag entries (`4.4`/`5.x`, `mac`/`win`, source). One to three lines each. Index new files in `knowledge/README.md`. Remove a `stale?` tag from any entry you relied on.
6. **Retro: change the process.**
   1. **Check the open checks first.** Each entry under Changed in `knowledge/process/improvements.md` has a Check line: what the next experiment should show if the change worked. For each open check this session could observe, mark it `held`, `failed` or `unobserved`, with the date and the evidence. A change with two `failed` marks gets rewritten or reverted; log that too.
   2. **Ask of this session:** Where did time or tokens go that a skill, template or tool could have saved? What did a skill tell us to do that was wrong, missing, or ignored? What worked that no skill encodes yet? What did the user have to ask for or correct?
   3. **Act.**
      - **Small, evidence-backed change** (a step, a rule, a template default, a helper in `tools/`): make it now.
      - **Bigger change** (a new skill, a changed loop, anything risky): add it under Proposed in `improvements.md` and tell the user.
      - **One source per rule.** A rule goes in exactly one place: the `SKILL.md` that applies it (or `CLAUDE.md` if it applies to most tasks). The evidence goes in `knowledge/process/`, with a pointer to the rule. Do not copy the rule into both.
      - **Skills have a word budget:** `review-render` 1,300, every other skill 800 (`wc -w .claude/skills/*/SKILL.md`). A skill over budget after an edit loses a rule in the same edit: merge it, cut it, or move it into a tool or hook. A step two experiments skipped becomes a tool step or a hook check, not a longer sentence.
      - **Archive settled entries.** A Changed entry in `improvements.md` whose check has held twice with no `failed` mark moves, verbatim, to `knowledge/process/improvements-archive.md`. The retro reads the live file only.
      - Log every change under Changed in `improvements.md`: date, evidence, what changed, which file, and a **Check** line saying what the next experiment should show if it worked.
7. **Clear** promoted items from each `LEARNINGS.md`. Leave anything not promoted.
8. **Commit this session's work** on the current branch, without asking. Stage only the paths this session changed, never `git add -A`: other sessions may have uncommitted work in the same checkout. Message: what changed and why, one line, plus the attribution lines. Do not push unless the user asks.
9. **Report** a short list: the cost line, the commit, checks marked, knowledge changes, process changes made, proposals. If nothing qualified, say so.
