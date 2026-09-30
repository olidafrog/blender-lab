#!/usr/bin/env bash
# PreToolUse hook on Edit/Write/Bash: block changes to experiments/<name>/scripts/build*.py until
# the research exists. Applies when the experiment has a BRIEF.md and files in references/.
# Passes when RESEARCH.md has a "Sources" heading and at least one link, or PROGRESS.md says
# "research skipped: <why>".
# Bash: only commands that write the file are gated (sed -i, perl -i, a redirect, tee, cp or mv
# onto it, a script that writes it). Running it, reading it and snapshotting it pass. Copying the
# template (new-experiment) and filling __NAME__ pass.
input="$(cat)"; source "$(dirname "$0")/lib.sh"
if [[ "$(field tool_name)" == "Bash" ]]; then
  cmd="$(field command)"
  [[ "$cmd" =~ experiments/([A-Za-z0-9_.-]+)/scripts/build[A-Za-z0-9_.-]*\.py ]] || exit 0
  name="${BASH_REMATCH[1]}"; t="${BASH_REMATCH[0]//./\\.}"
  [[ "$cmd" == *__NAME__* || "$cmd" == *templates/build.py* ]] && exit 0
  printf '%s' "$cmd" | grep -Eq "(sed|perl)[^|;&]* -[a-zA-Z]*i|>>?[[:space:]]*[\"']?[^[:space:]\"']*$t|tee[^|;&]*$t|(cp|mv)[[:space:]][^|;&]*[[:space:]][\"']?[^[:space:]\"']*$t[\"']?[[:space:]]*(\$|[;&|])|write_text|\.write\(|open\([^)]*['\"][wa]" || exit 0
  exp="${CLAUDE_PROJECT_DIR:-.}/experiments/$name"
else
  path="$(field file_path)"
  [[ "$path" =~ (^|/)experiments/([^/]+)/scripts/build[^/]*\.py$ ]] || exit 0
  exp="${path%/scripts/*}"
  [[ "$exp" = /* ]] || exp="${CLAUDE_PROJECT_DIR:-.}/$exp"
fi
[[ -f "$exp/BRIEF.md" ]] || exit 0
[[ -n "$(find "$exp/references" -type f ! -name '.*' 2>/dev/null | head -1)" ]] || exit 0
grep -Eqi '^#+ *sources' "$exp/RESEARCH.md" 2>/dev/null && grep -Eq 'https?://' "$exp/RESEARCH.md" && exit 0
grep -Eqi 'research (step )?skipped' "$exp/PROGRESS.md" 2>/dev/null && exit 0

name="$(basename "$exp")"
reason="Research gate: experiments/$name has references but no RESEARCH.md with a Sources section that holds at least one link. Run /research-reference first; it writes RESEARCH.md. If the user said to skip research, write 'research skipped: <why>' in PROGRESS.md, then retry."
printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":%s}}\n' "$(json_str "$reason")"
exit 0
