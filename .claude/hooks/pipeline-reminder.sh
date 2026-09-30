#!/usr/bin/env bash
# UserPromptSubmit hook: when a prompt starts look work (a new experiment, a new version,
# matching a reference), remind Claude of the pipeline. Output is added to Claude's context.
# Bare "render", "reference" or "experiment" do not match: they fire on too many other prompts.
# A version inside a name ("cyber-deck-v2") does not match either.
input="$(cat)"; source "$(dirname "$0")/lib.sh"
prompt="$(field prompt | tr '[:upper:]' '[:lower:]')"
[[ -n "$prompt" ]] || exit 0
if printf '%s' "$prompt" | grep -Eq 'new experiment|start (a|an|the) (new )?experiment|new version|next version|(^|[^a-z0-9-])v[0-9]{1,2}([^a-z0-9]|$)|version [0-9]|recreate (this|the|it)|match (this|the) (reference|ref|image)|look[- ]?dev|improve the look'; then
  echo "blender-lab pipeline applies (see CLAUDE.md): new-experiment → research-reference → build → review-render loop (Opus) → finish-experiment → capture-learnings. Invoke each with the Skill tool. Hooks check the artifacts: RESEARCH.md before build.py, a review for the newest render, knowledge updated before stopping. Skip a step only if the user said so, and note it in PROGRESS.md."
fi
exit 0
