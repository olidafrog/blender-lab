#!/usr/bin/env bash
# Run a Blender Python script headless on Mac or Windows (Git Bash).
#
#   tools/blender.sh <script.py> [script args...]
#
# Env:
#   BLENDER=<path>   override the executable
#   BLEND=<file>     open this .blend before running the script
#   PREFS=1          keep user prefs/add-ons (drops --factory-startup)
#   VERBOSE=1        show all Blender output, not just the useful lines
set -euo pipefail

if [[ $# -lt 1 ]]; then
  sed -n '2,11p' "$0"; exit 2
fi

if [[ -z "${BLENDER:-}" ]]; then
  case "$(uname -s)" in
    Darwin) BLENDER="$HOME/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender" ;;
    MINGW*|MSYS*|CYGWIN*) BLENDER="/f/Games/SteamLibrary/steamapps/common/Blender/blender.exe" ;;
    *) BLENDER="$(command -v blender || true)" ;;
  esac
fi
[[ -x "$BLENDER" ]] || { echo "Blender not found at '$BLENDER'. Set BLENDER=<path>." >&2; exit 1; }

script="$1"; shift
args=(-b)
[[ -n "${BLEND:-}" ]] && args+=("$BLEND")
[[ "${PREFS:-0}" == 1 ]] || args+=(--factory-startup)
args+=(--python-exit-code 1 -P "$script")
[[ $# -gt 0 ]] && args+=(-- "$@")

"$BLENDER" --version 2>/dev/null | head -1
if [[ "${VERBOSE:-0}" == 1 ]]; then
  "$BLENDER" "${args[@]}"
else
  set +o pipefail
  "$BLENDER" "${args[@]}" 2>&1 | grep -E "\[common\]|RENDER TIME|Saved|WROTE|OK$|Error|Traceback|^  File|Exception"
  exit "${PIPESTATUS[0]}"
fi
