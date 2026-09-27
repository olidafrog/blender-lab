#!/usr/bin/env bash
# PreToolUse hook on Edit/Write: block edits to experiments/<name>/scripts/build*.py until the
# research exists. Applies when the experiment has a BRIEF.md and files in references/.
# Passes when RESEARCH.md has a "Sources" heading, or PROGRESS.md says "research skipped: <why>".
# Copying the template with cp (new-experiment) is a Bash call and is not gated.
input="$(cat)"; source "$(dirname "$0")/lib.sh"
path="$(field file_path)"
[[ "$path" =~ (^|/)experiments/([^/]+)/scripts/build[^/]*\.py$ ]] || exit 0
exp="${path%/scripts/*}"
[[ "$exp" = /* ]] || exp="${CLAUDE_PROJECT_DIR:-.}/$exp"
[[ -f "$exp/BRIEF.md" ]] || exit 0
[[ -n "$(find "$exp/references" -type f ! -name '.*' 2>/dev/null | head -1)" ]] || exit 0
grep -Eqi '^#+ *sources' "$exp/RESEARCH.md" 2>/dev/null && exit 0
grep -Eqi 'research (step )?skipped' "$exp/PROGRESS.md" 2>/dev/null && exit 0

name="$(basename "$exp")"
reason="Research gate: experiments/$name has references but no RESEARCH.md with a Sources section. Run /research-reference first; it writes RESEARCH.md. If the user said to skip research, write 'research skipped: <why>' in PROGRESS.md, then retry."
printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":%s}}\n' "$(json_str "$reason")"
exit 0
