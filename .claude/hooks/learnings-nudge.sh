#!/usr/bin/env bash
# Stop hook: once per session, if Blender was run and learnings were not captured,
# ask Claude to run /capture-learnings before it stops. Never blocks twice.
input="$(cat)"
field() { printf '%s' "$input" | sed -n "s/.*\"$1\"[[:space:]]*:[[:space:]]*\"\{0,1\}\([^\",}]*\).*/\1/p" | head -1; }

[[ "$(field stop_hook_active)" == "true" ]] && exit 0
sid="$(field session_id)"; transcript="$(field transcript_path)"
[[ -n "$sid" && -f "$transcript" ]] || exit 0

marker="${TMPDIR:-/tmp}/blender-lab-nudged-$sid"
[[ -e "$marker" ]] && exit 0
grep -q 'tools/blender.sh' "$transcript" || exit 0        # no Blender work this session
grep -q '"skill":"capture-learnings"\|"skill": "capture-learnings"' "$transcript" && exit 0

touch "$marker"
cat <<'JSON'
{"decision":"block","reason":"Blender work happened this session and learnings were not captured. If anything cost time or changed the approach, run the capture-learnings skill now. If nothing qualifies, say so in one line and stop."}
JSON
