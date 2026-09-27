# Parallel sessions

Several Claude sessions often work in this repo at once, one per experiment.

- Put structural changes (skills, hooks, tools, `CLAUDE.md`) in a git worktree on its own branch, and merge when the other sessions have committed. Expect conflicts only in shared files: `review-render/SKILL.md`, `CLAUDE.md`, `knowledge/process/*`. `lab-audit`
- A session keeps the hooks and skill text it loaded at start. Edits to `.claude/` take effect in the next session, and a worktree session still runs the launch checkout's hooks. The lab-audit session was stopped by the old skill-name Stop hook after replacing it. `lab-audit`
- A worktree session refuses Bash that it cannot prove stays inside the worktree: `cd` to the main checkout, multi-line heredocs, loops over paths. Write the script to the scratchpad and run it with one plain command. Read main-checkout files (renders are not in git) through `../../../`. `lab-audit`
- Check numbers taken from transcripts with `tools/session_cost.py` before acting on them. The audit's counts were wrong twice: 28 Opus reviews (really 14), and "no web research" in opal-essence (it ran in subagents). `lab-audit`
