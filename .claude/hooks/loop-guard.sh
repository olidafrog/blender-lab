#!/usr/bin/env bash
# PreToolUse hook on Bash: block a shell loop that calls tools/blender.sh with --set.
# The Bash tool runs zsh, which does not word-split $var, so such a loop passes "a=1 b=2" as one
# value or drops every --set, and the run fails silently. It cost renders in clouds, wax-seal and
# cyber-model after three written warnings. tools/sweep.sh is bash and tiles the variants.
input="$(cat)"; source "$(dirname "$0")/lib.sh"
cmd="$(field command)"
[[ "$cmd" == *blender.sh* && "$cmd" == *--set* ]] || exit 0
printf '%s' "$cmd" | grep -Eq '(^|[;&|({[:space:]])(for|while|until)[[:space:]]' || exit 0
printf '%s' "$cmd" | grep -Eq '(^|;)[[:space:]]*do([[:space:]]|$)' || exit 0     # a real loop body, not prose in a heredoc
reason="Loop guard: no shell loops around tools/blender.sh --set (zsh does not word-split, so variants get dropped). Use tools/sweep.sh <build.py> <name> \"k=v k2=v2\" \"k=v3\" -- <build args>; it renders each variant and tiles them. For anything sweep.sh cannot do, write a bash script file and run it with 'bash <file>'."
printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":%s}}\n' "$(json_str "$reason")"
exit 0
