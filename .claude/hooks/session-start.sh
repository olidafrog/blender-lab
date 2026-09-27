#!/usr/bin/env bash
# SessionStart hook: stamp the session's start time, so the Stop hook can tell which
# renders, reviews and knowledge edits belong to this session.
input="$(cat)"; source "$(dirname "$0")/lib.sh"
sid="$(field session_id)"
[[ -n "$sid" ]] || exit 0
m="$marker_dir/blender-lab-start-$sid"
[[ -e "$m" ]] || touch "$m"   # a resumed or compacted session keeps its first stamp
exit 0
