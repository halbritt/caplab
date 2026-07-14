#!/bin/bash
# Validate the repaired empirical-probe endpoint model-free. Runs each behavior
# fixture through the exact confining root with the loopback observer on, and
# asserts the verifier reward band, historical wire endpoint, and versioned
# pre-edit timeline endpoint match endpoint-fixtures/expectations.json. If any
# case does not reproduce deterministically, the endpoint is not trustworthy
# and live inference must not proceed.
#
# Requires: striatum-workspace-capture (NATIVE_CAPTURE_BINARY), bwrap,
# slirp4netns unnecessary (no egress), go, python3, curl, and NATIVE_CORPUS.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
TASKS="$(dirname "$HERE")"
REPO="$(cd "$TASKS/../../../../.." && pwd)"
SCRATCH="${MATRIX_SCRATCH:-$(mktemp -d)}"
CORPUS="${NATIVE_CORPUS:?set NATIVE_CORPUS to the pinned corpus projection dir}"
BINARY="${NATIVE_CAPTURE_BINARY:-striatum-workspace-capture}"
FIX="$HERE/endpoint-fixtures"

# Flat runtime dir: the six fixtures, the probe helper, and order-key.sh, all
# under one directory bound at /var/tmp/.bench-runtime.
RUNTIME_DIR="$SCRATCH/runtime"
mkdir -p "$RUNTIME_DIR"
cp "$FIX"/*.sh "$RUNTIME_DIR/"
cp "$HERE/order-key.sh" "$RUNTIME_DIR/"

FAIL=0
run_fixture() {
  local NAME="$1" TASK="$2" WANT_REWARD="$3" WANT_WIRE="$4" WANT_PRE="$5" WANT_POST_LEDGER="$6" WANT_EDIT_FIRST="$7" WANT_POST_REPLAY="$8" WANT_DECISION="$9"
  local TRIAL="$SCRATCH/$NAME"
  rm -rf "$TRIAL"
  cat > "$SCRATCH/decl-$NAME.yaml" <<EOF
schema_version: 1
id: fixture-$NAME
aliasing:
  aliasing_class: fixture
adapter:
  command: [/usr/bin/env, APP_DIR=/app, bash, /var/tmp/.bench-runtime/$NAME.sh]
  prompt_mode: arg
provenance_fields:
  required: [attempts]
EOF
  if ! python3 "$REPO/doctrine/tools/run_checkout_native.py" \
    --task "$TASKS/$TASK" \
    --declaration "$SCRATCH/decl-$NAME.yaml" \
    --corpus "$CORPUS" \
    --runtime-dir "$RUNTIME_DIR" \
    --capture-binary "$BINARY" \
    --trial-dir "$TRIAL" \
    --confine --observe --observe-timeline \
    --timeout 300 > "$TRIAL.log" 2>&1; then
    printf '%-24s %-24s driver-failed (see %s)\n' "$NAME" "$TASK" "$TRIAL.log"
    FAIL=1
    return
  fi
  local GOT
  GOT=$(python3 - "$TRIAL/trial.json" "$WANT_REWARD" "$WANT_WIRE" "$WANT_PRE" "$WANT_POST_LEDGER" "$WANT_EDIT_FIRST" "$WANT_POST_REPLAY" "$WANT_DECISION" <<'PY'
import json, sys
trial = json.load(open(sys.argv[1]))
want_reward = float(sys.argv[2])
want = [value == "true" for value in sys.argv[3:]]
reward = trial.get("reward")
wire = (trial.get("wire_endpoint") or {}).get("same_key_replay_observed")
timeline = trial.get("timeline_endpoint") or {}
got = [
    wire,
    timeline.get("pre_edit_same_key_replay_observed"),
    timeline.get("pre_edit_post_replay_ledger_query_observed"),
    timeline.get("source_edit_before_replay_and_ledger"),
    timeline.get("post_edit_same_key_replay_observed"),
    timeline.get("decision_artifact_present"),
]
ok = reward == want_reward and timeline.get("timeline_valid") is True and got == want
print(f"reward={reward} timeline_valid={timeline.get('timeline_valid')} fields={got} {'ok' if ok else 'MISMATCH'}")
sys.exit(0 if ok else 1)
PY
)
  local RC=$?
  printf '%-24s %-24s got[%s]\n' "$NAME" "$TASK" "$GOT"
  [ "$RC" -ne 0 ] && FAIL=1
}

# Drive from the expectations manifest.
while IFS=$'\t' read -r NAME TASK REWARD WIRE PRE POST_LEDGER EDIT_FIRST POST_REPLAY DECISION; do
  run_fixture "$NAME" "$TASK" "$REWARD" "$WIRE" "$PRE" "$POST_LEDGER" "$EDIT_FIRST" "$POST_REPLAY" "$DECISION"
done < <(python3 -c "
import json
m = json.load(open('$FIX/expectations.json'))
for f in m['fixtures']:
    fields = ['wire_replay', 'pre_edit_replay', 'post_replay_ledger', 'edit_before_replay_and_ledger', 'post_edit_replay', 'decision_artifact']
    print(f['name'], f['task'], f['reward'], *(str(f[k]).lower() for k in fields), sep='\t')
")

echo "scratch: $SCRATCH"
if [ "$FAIL" -ne 0 ]; then
  echo "ENDPOINT FIXTURES: FAIL"
  exit 1
fi
echo "ENDPOINT FIXTURES: PASS"
