#!/usr/bin/env bash
# Stop hook. Checks artifacts, not skill names, for each experiment rendered this session:
#  1. its newest version render (renders/v*.png) has a review at least as new;
#  2. its learnings were captured: its LEARNINGS.md changed this session, or a knowledge/ file
#     changed this session names it (scoreboard row, decision record, gotcha source tag). Another
#     session's knowledge edits do not count, because they name another experiment.
# Runs only when this session's own commands ran blender.sh, and counts only experiments those
# commands named. A given ask blocks once; a new ask (a second
# experiment in the same session) blocks again.
input="$(cat)"; source "$(dirname "$0")/lib.sh"
[[ "$(field stop_hook_active)" == "true" ]] && exit 0
sid="$(field session_id)"; transcript="$(field transcript_path)"
[[ -n "$sid" && -f "$transcript" ]] || exit 0
# Commands this session ran (Bash tool calls only), so prose that names blender.sh does not count.
cmds="$(grep -oE '"name":"Bash","input":\{"command":"([^"\\]|\\.)*' "$transcript" 2>/dev/null)"
cmds="$(grep 'blender\.sh' <<<"$cmds")"                   # keep only the Blender runs
[[ -n "$cmds" ]] || exit 0                                 # no Blender work this session
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
start="$marker_dir/blender-lab-start-$sid"                # written by session-start.sh

mtime() { stat -f %m "$1" 2>/dev/null || stat -c %Y "$1" 2>/dev/null || echo 0; }
newest() { local best=0 f t; while IFS= read -r f; do t=$(mtime "$f"); (( t > best )) && best=$t; done; echo "$best"; }

asks=()
if [[ -e "$start" ]]; then
  unreviewed=(); unlearned=(); rendered=0
  for r in experiments/*/renders; do
    [[ -d "$r" ]] || continue
    exp="${r%/renders}"; name="${exp#experiments/}"
    grep -q "experiments/$name/" <<<"$cmds" || continue     # only experiments a Blender run named
    # Rendered this session: any top-level render that is not a final, a raw EXR or a crop.
    [[ -n "$(find "$r" -maxdepth 1 -type f -newer "$start" ! -iname '*final*' ! -name '*_raw.exr' ! -name '*crop*' 2>/dev/null | head -1)" ]] || continue
    rendered=1
    cur=$(find "$r" -maxdepth 1 -type f -newer "$start" -name 'v[0-9]*' ! -name '*_raw.exr' ! -name '*crop*' 2>/dev/null | newest)
    rev=$(find "$exp/reviews" -maxdepth 1 -type f -name 'review_v*.md' 2>/dev/null | newest)
    (( cur > 0 && rev < cur )) && unreviewed+=("$name")
    if [[ -z "$(find "$exp/LEARNINGS.md" -newer "$start" 2>/dev/null)" ]] &&
       [[ -z "$(find knowledge -type f -newer "$start" -print0 2>/dev/null | xargs -0 grep -l -- "$name" 2>/dev/null | head -1)" ]]; then
      unlearned+=("$name")
    fi
  done
  if (( ${#unreviewed[@]} )); then
    asks+=("run review-render on the newest version of ${unreviewed[*]} (its newest render has no review), or say in one line why not: the user opted out, it was not look work, or it was a test render")
  fi
  if (( ${#unlearned[@]} )); then
    asks+=("run capture-learnings for ${unlearned[*]}: record what we learned, add the session's line to knowledge/process/scoreboard.md, and change any skill, template or tool that would have saved time")
  elif (( ! rendered )) && [[ -z "$(find knowledge experiments/*/LEARNINGS.md -type f -newer "$start" 2>/dev/null | head -1)" ]]; then
    asks+=("run capture-learnings: record what we learned, add this session's line to knowledge/process/scoreboard.md, and change any skill, template or tool that would have saved time")
  fi
else
  [[ -n "$(git status --porcelain -- knowledge 'experiments/*/LEARNINGS.md' 2>/dev/null | head -1)" ]] ||
    asks+=("run capture-learnings: record what we learned, add this session's line to knowledge/process/scoreboard.md, and change any skill, template or tool that would have saved time")
fi
(( ${#asks[@]} )) || exit 0

reason="Before stopping: $(IFS=';'; echo "${asks[*]}" | sed 's/;/; then /g')."
nudged="$marker_dir/blender-lab-nudged-$sid-$(printf '%s' "$reason" | cksum | cut -d' ' -f1)"
[[ -e "$nudged" ]] && exit 0
touch "$nudged"
printf '{"decision":"block","reason":%s}\n' "$(json_str "$reason")"
