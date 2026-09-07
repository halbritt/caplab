#!/usr/bin/env bash
# Launch one tree-v1 review sweep under the supervisor with the launcher
# environment the probe record names (probe-2026-09-06-tree-v1-stage-b.md,
# finding 3): the lane env files striatum's wake units inject, and
# ~/.npm-global/bin on PATH for opencode. Nothing here is a sandbox property.
#
#   scripts/launch_tree_v1_sweep.sh <backend> [supervise_sweep args...]
set -euo pipefail
backend="$1"; shift
repo="$(cd "$(dirname "$0")/.." && pwd)"
out="$repo/advisory/pool-runs/tree-$backend-20260819"
set -a
for f in zai openrouter; do [ -r "$HOME/.config/striatum/$f.env" ] && . "$HOME/.config/striatum/$f.env"; done
set +a
export PATH="$HOME/.npm-global/bin:$PATH"
export PYTHONPATH="$repo/src"
mkdir -p "$out"
exec python3 -u "$repo/scripts/supervise_sweep.py" "$backend" "$out" "$@"
