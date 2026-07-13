#!/bin/bash
# Launch one preregistered sequence of the native codex-sol-max m1 screen.
# See checkout-retries-m1-native-codex-sol-max.md — run sequences
# individually; sequence 0 is the preregistered environment check, and the
# record's s1 gate applies before sequences 2-4.
set -euo pipefail

SEQ="${1:?usage: run-codex-screen.sh <sequence 0-4>}"
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
TASK="$REPO/doctrine/evaluations/robustness/harbor/tasks/checkout-retries-m1"
TASK_HASH="eadd80413c356a05041917e52d58b900ee9c58addbc6ae4634bc8e30c7d12acf"
DECLARATION="${CODEX_DECLARATION:-$HOME/git/striatum-next/backends/codex-sol-max/backend.yaml}"
DECLARATION_SHA="4404fc59437fce42382f43abd217f86757e523d60609432c1adb26dcf9700abc"
CORPUS="${NATIVE_CORPUS:-/var/tmp/striatum-bench/corpus-29e067c6}"
BINARY="${NATIVE_CAPTURE_BINARY:-striatum-workspace-capture}"
SCREEN_DIR="/var/tmp/striatum-bench/native-codex-screen"

echo "$DECLARATION_SHA  $DECLARATION" | sha256sum --check --quiet \
  || { echo "declaration drift: $DECLARATION" >&2; exit 1; }

if [ "$SEQ" = "0" ]; then
  PROMPT="$HERE/env-check-prompt.md"
  TRIAL="$SCREEN_DIR/env-check"
  TIMEOUT=300
else
  PROMPT="$TASK/instruction.md"
  TRIAL="$SCREEN_DIR/native-s0$SEQ-codex-sol-max-m1-bare"
  TIMEOUT=1800
fi

python3 "$REPO/doctrine/tools/run_checkout_native.py" \
  --task "$TASK" \
  --declaration "$DECLARATION" \
  --corpus "$CORPUS" \
  --capture-binary "$BINARY" \
  --trial-dir "$TRIAL" \
  --egress \
  --runtime-events codex-jsonl \
  --expect-task-hash "$TASK_HASH" \
  --timeout "$TIMEOUT" \
  --prompt-file "$PROMPT" \
  --runtime-arg=--json \
  --runtime-arg=--ignore-user-config \
  --runtime-arg=-c \
  --runtime-arg=sandbox_workspace_write.network_access=true
