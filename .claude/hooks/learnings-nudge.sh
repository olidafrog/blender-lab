#!/usr/bin/env bash
# Stop hook, fires at most once per session. Checks artifacts, not skill names:
#  1. each experiment rendered this session has a review at least as new as its newest render;
#  2. knowledge/ or an experiment's LEARNINGS.md changed this session.
# Runs only when Blender ran this session. Never blocks twice.
input="$(cat)"; source "$(dirname "$0")/lib.sh"
[[ "$(field stop_hook_active)" == "true" ]] && exit 0
sid="$(field session_id)"; transcript="$(field transcript_path)"
[[ -n "$sid" && -f "$transcript" ]] || exit 0
nudged="$marker_dir/blender-lab-nudged-$sid"
[[ -e "$nudged" ]] && exit 0
grep -q 'tools/blender.sh' "$transcript" || exit 0        # no Blender work this session
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
start="$marker_dir/blender-lab-start-$sid"                # written by session-start.sh

mtime() { stat -f %m "$1" 2>/dev/null || stat -c %Y "$1" 2>/dev/null || echo 0; }
newest() { local best=0 f t; while IFS= read -r f; do t=$(mtime "$f"); (( t > best )) && best=$t; done; echo "$best"; }

asks=()
if [[ -e "$start" ]]; then
  unreviewed=()
  for r in experiments/*/renders; do
    [[ -d "$r" ]] || continue
    exp="${r%/renders}"
    # Version renders from this session: top-level files, not finals, raw EXRs or crops.
    cur=$(find "$r" -maxdepth 1 -type f -newer "$start" ! -iname '*final*' ! -name '*_raw.exr' ! -name '*crop*' 2>/dev/null | newest)
    (( cur > 0 )) || continue
    rev=$(find "$exp/reviews" -type f -name 'review_v*.md' 2>/dev/null | newest)
    (( rev >= cur )) || unreviewed+=("${exp#experiments/}")
  done
  if (( ${#unreviewed[@]} )); then
    asks+=("run review-render on the newest version of ${unreviewed[*]} (its newest render has no review), or say in one line why not: the user opted out, it was not look work, or it was a test render")
  fi
  learned=$(find knowledge experiments/*/LEARNINGS.md -type f -newer "$start" 2>/dev/null | head -1)
else
  learned=$(git status --porcelain -- knowledge 'experiments/*/LEARNINGS.md' 2>/dev/null | head -1)
fi
[[ -n "$learned" ]] || asks+=("run capture-learnings: record what we learned, add this session's line to knowledge/process/scoreboard.md, and change any skill, template or tool that would have saved time")
(( ${#asks[@]} )) || exit 0

touch "$nudged"
reason="Before stopping: $(IFS=';'; echo "${asks[*]}" | sed 's/;/; then /g')."
printf '{"decision":"block","reason":%s}\n' "$(json_str "$reason")"
