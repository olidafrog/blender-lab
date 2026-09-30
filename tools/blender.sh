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
# Absolute path: a relative .blend with --factory-startup crashes 5.2 on Mac (NSURL nil).
[[ -n "${BLEND:-}" ]] && args+=("$(cd "$(dirname "$BLEND")" && pwd)/$(basename "$BLEND")")
[[ "${PREFS:-0}" == 1 ]] || args+=(--factory-startup)
args+=(--python-exit-code 1 -P "$script")
[[ $# -gt 0 ]] && args+=(-- "$@")

"$BLENDER" --version 2>/dev/null | head -1
if [[ "${VERBOSE:-0}" == 1 ]]; then
  "$BLENDER" "${args[@]}"
else
  # Keep the raw log: the filter hides sys.exit() messages and crashes, and Blender exits 0 after sys.exit(msg),
  # so a failed run can look like an empty success. If the run failed or matched nothing, show the raw tail.
  pat="\[common\]|\[out\]|RENDER TIME|Saved|WROTE|OK$|Error|Traceback|^  File|Exception"
  log="$(mktemp)"
  set +eo pipefail                       # grep finding nothing must not end the script before the check below
  "$BLENDER" "${args[@]}" 2>&1 | tee "$log" | grep -E "$pat"
  rc="${PIPESTATUS[0]}"
  if [[ "$rc" -ne 0 ]] || ! grep -qE "$pat" "$log"; then echo "[out] no result line (exit code $rc). Last lines of Blender's output:"; tail -n 12 "$log"; fi
  rm -f "$log"
  exit "$rc"
fi
