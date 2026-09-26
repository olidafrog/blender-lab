---
name: capture-learnings
description: Use at the end of a blender-lab session, before stopping, when the learnings nudge hook fires, or when the user says "capture learnings", "what did we learn", or "save the lessons". Also use when something cost real time mid-session and should not be lost.
---

# Capture learnings

Move what this session taught us into `knowledge/`, so the next project starts from it.

## Steps

1. **Gather.** Read `knowledge/README.md` (format, tags, index). Collect candidates from:
   - this conversation: errors, wrong API names, silent failures, retries, reviewer surprises, approaches that changed,
   - `LEARNINGS.md` in each experiment touched this session.
2. **Filter.** Keep a candidate only if a future session would act differently because of it. Drop what the code already shows, and one-off typos.
3. **Sort** each into one kind:
   - **Gotcha** → the matching `knowledge/gotchas/<topic>.md`. Symptom, cause, fix.
   - **Process** → `knowledge/process/`.
   - **Insight** → `knowledge/insights.md`. Only lessons that would change how we approach a different project.
   - **Decision** → `knowledge/decisions/<experiment>.md`: what we chose, what we rejected, why.
   - **Reusable asset** (a material, node group, model used twice) → suggest moving it to `library/`; do not move it without asking.
4. **Dedupe.** Search `knowledge/` for the same fact (`grep -ri`). If it exists, sharpen that entry: add the version tag, the new source, or correct it. If a new fact proves an old one wrong, replace the old one.
5. **Write** with tags (`4.4`/`5.x`, `mac`/`win`, source experiment). One to three lines each, plain words. Add any new file to the index in `knowledge/README.md`.
6. **Clear** promoted items from each `LEARNINGS.md`. Leave anything not promoted.
7. **Report** a short list: file → one-line summary of each change. If nothing qualified, say so.
