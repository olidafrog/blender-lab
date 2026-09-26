#!/usr/bin/env bash
# UserPromptSubmit hook: when a prompt looks like experiment work, remind Claude of the pipeline.
# Whatever this prints is added to Claude's context for that turn.
prompt="$(cat | tr '[:upper:]' '[:lower:]')"
if printf '%s' "$prompt" | grep -Eq 'experiment|new version|\bv[0-9]+\b|version [0-9]|recreate|reference|look[- ]?dev|render|iterate|improve the look'; then
  echo "blender-lab pipeline applies (see CLAUDE.md): new-experiment → research-reference → build → review-render loop (Opus) → finish-experiment → capture-learnings. Invoke each with the Skill tool. Skip a step only if the user said so, and note it in PROGRESS.md."
fi
exit 0
