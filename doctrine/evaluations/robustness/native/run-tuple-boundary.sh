#!/bin/bash
# Run one native tuple-boundary trial through the confining root with the
# tamper-resistant loopback observer. Bare condition, codex runtime with its
# own sandbox bypassed (the surface namespace is the external sandbox).
# See checkout-retries-tuple-boundary.md — the ladder, endpoints, descent, and
# stop rules are frozen there. This script runs ONE trial; the ladder is driven
# externally per the descent rule, sequentially.
#
# Usage: run-tuple-boundary.sh <tuple-id> <arm: m1|v2> <trial-dir>
set -euo pipefail

TUPLE="${1:?usage: run-tuple-boundary.sh <tuple-id> <m1|v2> <trial-dir>}"
ARM="${2:?arm m1 or v2}"
TRIAL="${3:?trial dir}"
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
DECLARATION="${CODEX_BACKENDS:-$HOME/git/striatum-next/backends}/$TUPLE/backend.yaml"
CORPUS="${NATIVE_CORPUS:-/var/tmp/striatum-bench/corpus-29e067c6}"
BINARY="${NATIVE_CAPTURE_BINARY:-striatum-workspace-capture}"

case "$ARM" in
  m1) TASK="checkout-retries-m1"; HASH="eadd80413c356a05041917e52d58b900ee9c58addbc6ae4634bc8e30c7d12acf" ;;
  v2) TASK="checkout-retries-v2"; HASH="1d703eddf030ca8e4a5d84189e59e0a2f05725e993f7de68d679daac5f894183" ;;
  *) echo "arm must be m1 or v2" >&2; exit 2 ;;
esac
TASK_DIR="$REPO/doctrine/evaluations/robustness/harbor/tasks/$TASK"

[ -f "$DECLARATION" ] || { echo "no declaration: $DECLARATION" >&2; exit 2; }

# Extra skill/instruction delivery for a doctrine arm is threaded via
# CODEX_EXTRA_RUNTIME_ARGS (space-separated) and CODEX_EXTRA_PROMPT_FILE; the
# bare arm sets neither. Kept identical otherwise.
EXTRA_ARGS=()
if [ -n "${CODEX_EXTRA_RUNTIME_ARGS:-}" ]; then
  for a in $CODEX_EXTRA_RUNTIME_ARGS; do EXTRA_ARGS+=(--runtime-arg="$a"); done
fi
PROMPT_ARG=()
[ -n "${CODEX_EXTRA_PROMPT_FILE:-}" ] && PROMPT_ARG=(--prompt-file "${CODEX_EXTRA_PROMPT_FILE}")

python3 "$REPO/doctrine/tools/run_checkout_native.py" \
  --task "$TASK_DIR" \
  --declaration "$DECLARATION" \
  --corpus "$CORPUS" \
  --capture-binary "$BINARY" \
  --trial-dir "$TRIAL" \
  --confine --observe --egress \
  --runtime-events codex-jsonl \
  --expect-task-hash "$HASH" \
  --timeout "${CODEX_TIMEOUT:-1800}" \
  "${PROMPT_ARG[@]}" \
  --runtime-arg=--json \
  --runtime-arg=--ignore-user-config \
  --runtime-arg=--dangerously-bypass-approvals-and-sandbox \
  --runtime-arg=--ephemeral \
  "${EXTRA_ARGS[@]}"
