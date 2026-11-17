#!/usr/bin/env bash
# Claude Code Stop hook: the agent cannot finish while checks are red.
# Exit 2 = block stopping and feed stderr back to the agent.
input="$(cat)"
if echo "$input" | grep -q '"stop_hook_active": *true'; then exit 0; fi  # avoid infinite loops
cd "$(dirname "$0")/.."
if ! out="$(npm run -s check 2>&1)"; then
  echo "npm run -s check failed. Fix the root cause (no eslint-disable, no casts), then finish:" >&2
  echo "$out" | tail -60 >&2
  exit 2
fi
