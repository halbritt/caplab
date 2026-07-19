#!/bin/bash
# Run every reference solution against both verifiers on the host and print
# the reward matrix. Requires go, python3, and curl on PATH.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
TASKS="$(dirname "$HERE")"
SCRATCH="${MATRIX_SCRATCH:-$(mktemp -d)}"

run_cell() {
  local TASK="$1" REF="$2"
  local WORK="$SCRATCH/$(basename "$TASK")-$(basename "$REF" .sh)"
  rm -rf "$WORK"
  mkdir -p "$WORK/logs"
  cp -r "$TASKS/$TASK/environment/app" "$WORK/app"
  if ! APP_DIR="$WORK/app" bash "$HERE/$REF" > "$WORK/ref.log" 2>&1; then
    echo "ref-failed"
    return
  fi
  CHECKOUT_APP_DIR="$WORK/app" CHECKOUT_VERIFIER_LOGS="$WORK/logs" \
    bash "$TASKS/$TASK/tests/test.sh" > "$WORK/verifier.log" 2>&1
  if [ -f "$WORK/logs/reward.txt" ]; then
    cat "$WORK/logs/reward.txt"
  else
    echo "no-reward"
  fi
}

printf '%-22s %-24s %-8s\n' "reference" "task" "reward"
for REF in noop.sh naive-retry.sh random-key.sh order-key.sh; do
  for TASK in checkout-retries-v2 checkout-retries-m1; do
    printf '%-22s %-24s %-8s\n' "$REF" "$TASK" "$(run_cell "$TASK" "$REF")"
  done
done
printf '%-22s %-24s %-8s\n' "decline.sh" "checkout-retries-m1" \
  "$(run_cell checkout-retries-m1 decline.sh)"
echo "scratch: $SCRATCH"
