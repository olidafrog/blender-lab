#!/usr/bin/env bash
# Shared by the hooks. Source after reading stdin into $input.
# field <key> — a top-level or tool_input value from the hook's JSON payload.
# Uses jq when present; falls back to sed (Windows Git Bash may lack jq).
field() {
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$input" | jq -r --arg k "$1" '(.[$k] // .tool_input[$k] // empty) | tostring' 2>/dev/null
  else
    printf '%s' "$input" | sed -n "s/.*\"$1\"[[:space:]]*:[[:space:]]*\"\{0,1\}\([^\",}]*\).*/\1/p" | head -1
  fi
}

# json_str <text> — the text as a JSON string literal.
json_str() {
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$1" | jq -Rs .
  else
    printf '"%s"' "$(printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g')"
  fi
}

marker_dir="${TMPDIR:-/tmp}"
