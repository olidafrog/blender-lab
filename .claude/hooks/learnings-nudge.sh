#!/usr/bin/env bash
# Stop hook, fires at most once per session. If Blender ran and the pipeline's closing steps
# were skipped, ask Claude to do them (or say why not) before it stops. Never blocks twice.
input="$(cat)"
field() { printf '%s' "$input" | sed -n "s/.*\"$1\"[[:space:]]*:[[:space:]]*\"\{0,1\}\([^\",}]*\).*/\1/p" | head -1; }

[[ "$(field stop_hook_active)" == "true" ]] && exit 0
sid="$(field session_id)"; transcript="$(field transcript_path)"
[[ -n "$sid" && -f "$transcript" ]] || exit 0
marker="${TMPDIR:-/tmp}/blender-lab-nudged-$sid"
[[ -e "$marker" ]] && exit 0
grep -q 'tools/blender.sh' "$transcript" || exit 0          # no Blender work this session

used() { grep -Eq "\"skill\": ?\"$1\"" "$transcript"; }
asks=()
# Rendered into an experiment but never reviewed?
if grep -q 'experiments/[^" ]*/renders/' "$transcript" && ! used review-render; then
  asks+=("run the review-render loop on the latest version (or say in one line why this session did not need it, e.g. the user opted out or it was not look work)")
fi
used capture-learnings || asks+=("run capture-learnings: record what we learned, and change any skill, template or tool that would have saved time")
[[ ${#asks[@]} -eq 0 ]] && exit 0

touch "$marker"
reason="Before stopping: $(IFS=';'; echo "${asks[*]}" | sed 's/;/; then /g')."
printf '{"decision":"block","reason":"%s"}\n' "$(printf '%s' "$reason" | sed 's/"/\\"/g')"
