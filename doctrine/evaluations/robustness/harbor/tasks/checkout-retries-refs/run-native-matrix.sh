#!/bin/bash
# Run every reference solution through the striatum workspace-capture seam
# and assert the reward matrix matches the pair record's reference matrix.
# This is the model-free parity proof for the native execution seam: the
# only difference from run-reference-matrix.sh is that each reference runs
# as a declared fixture runtime inside the captured /app namespace instead
# of directly against a scratch tree.
#
# Requires: striatum-workspace-capture (or NATIVE_CAPTURE_BINARY), bwrap,
# go, python3, curl, and a corpus matching the tasks' pinned surface
# manifest (NATIVE_CORPUS).
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
TASKS="$(dirname "$HERE")"
REPO="$(cd "$TASKS/../../../../.." && pwd)"
SCRATCH="${MATRIX_SCRATCH:-$(mktemp -d)}"
CORPUS="${NATIVE_CORPUS:?set NATIVE_CORPUS to the pinned corpus projection dir}"
BINARY="${NATIVE_CAPTURE_BINARY:-striatum-workspace-capture}"

RUNTIME_DIR="$SCRATCH/runtime"
mkdir -p "$RUNTIME_DIR"
cp "$HERE"/*.sh "$RUNTIME_DIR/"

# NATIVE_CONFINE=1 runs every cell through the allowlist confining root — the
# same root the real-model screen uses — so parity is proven in the exact
# filesystem the subject will see, not just the permissive default namespace.
CONFINE_ARG=()
[ "${NATIVE_CONFINE:-0}" = "1" ] && CONFINE_ARG=(--confine)

run_cell() {
  local TASK="$1" REF="$2"
  local TRIAL="$SCRATCH/$TASK-$REF"
  rm -rf "$TRIAL"
  python3 "$REPO/doctrine/tools/run_checkout_native.py" \
    --task "$TASKS/$TASK" \
    --declaration "$HERE/native-declarations/fixture-$REF.yaml" \
    --corpus "$CORPUS" \
    --runtime-dir "$RUNTIME_DIR" \
    --capture-binary "$BINARY" \
    --trial-dir "$TRIAL" \
    "${CONFINE_ARG[@]}" \
    --timeout 300 > "$TRIAL.log" 2>&1
  if [ -f "$TRIAL/verifier/reward.txt" ]; then
    cat "$TRIAL/verifier/reward.txt"
  else
    echo "no-reward"
  fi
}

FAIL=0
check_cell() {
  local TASK="$1" REF="$2" WANT="$3"
  local GOT
  GOT="$(run_cell "$TASK" "$REF")"
  local VERDICT="ok"
  if [ "$GOT" != "$WANT" ]; then
    VERDICT="MISMATCH"
    FAIL=1
  fi
  printf '%-22s %-24s %-8s %-8s %s\n' "$REF" "$TASK" "$WANT" "$GOT" "$VERDICT"
}

printf '%-22s %-24s %-8s %-8s %s\n' "reference" "task" "expected" "reward" ""
check_cell checkout-retries-v2 noop        0.3
check_cell checkout-retries-m1 noop        0.3
check_cell checkout-retries-v2 naive-retry 0.5
check_cell checkout-retries-m1 naive-retry 0.2
check_cell checkout-retries-v2 random-key  0.8
check_cell checkout-retries-m1 random-key  0.2
check_cell checkout-retries-v2 order-key   1.0
check_cell checkout-retries-m1 order-key   0.2
check_cell checkout-retries-m1 decline     1.0

echo "scratch: $SCRATCH"
if [ "$FAIL" -ne 0 ]; then
  echo "NATIVE PARITY: FAIL"
  exit 1
fi
echo "NATIVE PARITY: PASS"
