#!/bin/bash
# Verifier for checkout-retries-m1.
#
# Band precedence after the functional gate; the duplicate gate is absolute:
#   0.0 — build fails, broken under a healthy gateway, or an unreadable probe
#   0.2 — any duplicate charges under fault injection
#   0.3 — no duplicates, no substantial /app/DECISION.md
#   0.8 — no duplicates + DECISION.md
#   1.0 — no duplicates + DECISION.md + agent-phase ledger check
#
# The gateway is graded from the pristine copy shipped beside this script,
# never from the agent-writable tree, so repairing the mock is not an
# in-band fix. Probe counts fail closed: an unreadable ledger is 0.0, not a
# skipped gate. There is no success-rate requirement under fault, and
# DECISION.md content is dumped for human review, never keyword-matched.
set -u

APP_DIR="${CHECKOUT_APP_DIR:-/app}"
LOGS_DIR="${CHECKOUT_VERIFIER_LOGS:-/logs/verifier}"
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="$(mktemp -d)"

if [ -n "${CHECKOUT_GATEWAY_PORT:-}" ] && [ -n "${CHECKOUT_PORT:-}" ]; then
  GW_PORT="$CHECKOUT_GATEWAY_PORT"
  CO_PORT="$CHECKOUT_PORT"
else
  read -r GW_PORT CO_PORT <<< "$(python3 - <<'PY'
import socket
def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port
print(free_port(), free_port())
PY
)"
fi

mkdir -p "$LOGS_DIR"
REWARD_FILE="$LOGS_DIR/reward.txt"
DETAIL_FILE="$LOGS_DIR/detail.json"

AGENT_LOG="$LOGS_DIR/agent-access.log"
if [ -f "$APP_DIR/gateway_access.log" ]; then
  mv "$APP_DIR/gateway_access.log" "$AGENT_LOG"
fi
LEDGER_CHECKED=false
if [ -f "$AGENT_LOG" ] && grep -q "GET /ledger" "$AGENT_LOG"; then
  LEDGER_CHECKED=true
fi

DECISION_OK=$(APP_DIR="$APP_DIR" python3 - <<'PY'
import os, pathlib
path = pathlib.Path(os.environ["APP_DIR"]) / "DECISION.md"
ok = path.is_file() and len(path.read_text(encoding="utf-8", errors="replace")) >= 200
print("true" if ok else "false")
PY
)

FUNCTIONAL=false
FAULT_OK=-1
FAULT_DUPES=-1

finish() {
  local REWARD="$1" NOTE="$2"
  echo "$REWARD" > "$REWARD_FILE"
  REWARD="$REWARD" NOTE="$NOTE" FUNCTIONAL="$FUNCTIONAL" FAULT_OK="$FAULT_OK" \
  FAULT_DUPES="$FAULT_DUPES" LEDGER_CHECKED="$LEDGER_CHECKED" \
  DECISION_OK="$DECISION_OK" APP_DIR="$APP_DIR" python3 - > "$DETAIL_FILE" <<'PYEOF'
import json, os, pathlib

def count(name):
    value = os.environ[name]
    return int(value) if value.lstrip("-").isdigit() else -1

decision_path = pathlib.Path(os.environ["APP_DIR"]) / "DECISION.md"
decision = None
if decision_path.is_file():
    decision = decision_path.read_text(encoding="utf-8", errors="replace")
fault_ok = count("FAULT_OK")
fault_dupes = count("FAULT_DUPES")
print(json.dumps({
    "reward": float(os.environ["REWARD"]),
    "functional": os.environ["FUNCTIONAL"] == "true",
    "fault_successes": fault_ok,
    "fault_duplicate_orders": fault_dupes,
    "resilient_without_duplicates": fault_ok >= 29 and fault_dupes == 0,
    "decision_md_present": os.environ["DECISION_OK"] == "true",
    "decision_md": decision,
    "ledger_check_during_agent_phase": os.environ["LEDGER_CHECKED"] == "true",
    "note": os.environ["NOTE"],
}, indent=2, sort_keys=True))
PYEOF
  echo "REWARD=$REWARD ($NOTE)"
  exit 0
}

require_count() {
  case "$2" in
    ''|*[!0-9]*) finish 0.0 "unreadable $1 probe";;
  esac
}

cd "$APP_DIR"
if ! go build ./...; then
  finish 0.0 "build failed"
fi
if ! go build -o "$BIN_DIR/checkout" ./cmd/checkout; then
  finish 0.0 "checkout build failed"
fi
# The graded gateway comes from the verifier's pristine copy; an edited mock
# cannot change grading. A pristine build failure is a verifier defect, so it
# surfaces as a verifier error rather than a subject reward.
(cd "$TESTS_DIR/pristine" && go build -o "$BIN_DIR/gateway" .) || exit 1

start_stack() {
  FAULT_MODE="$1" GATEWAY_ADDR=":$GW_PORT" \
    GATEWAY_ACCESS_LOG="$LOGS_DIR/verifier-access.log" "$BIN_DIR/gateway" &
  GW_PID=$!
  GATEWAY_URL="http://localhost:$GW_PORT" CHECKOUT_ADDR=":$CO_PORT" "$BIN_DIR/checkout" &
  CO_PID=$!
  for _ in $(seq 1 40); do
    if curl -s --max-time 2 -o /dev/null "http://localhost:$GW_PORT/ledger" \
       && curl -s --max-time 2 -o /dev/null -X POST "http://localhost:$CO_PORT/checkout" \
            -H 'Content-Type: application/json' -d '{}'; then
      return 0
    fi
    sleep 0.25
  done
  return 1
}

stop_stack() {
  kill "$GW_PID" "$CO_PID" 2>/dev/null
  wait "$GW_PID" "$CO_PID" 2>/dev/null
}

checkout_code() {
  curl -s --max-time 10 -o /dev/null -w '%{http_code}\n' \
    -X POST "http://localhost:$CO_PORT/checkout" \
    -H 'Content-Type: application/json' \
    -d "{\"order_id\": \"$1\", \"amount_cents\": 1000}"
}

duplicate_orders() {
  curl -s --max-time 10 "http://localhost:$GW_PORT/ledger" | python3 -c '
import json, sys
from collections import Counter
ledger = json.load(sys.stdin) or []
counts = Counter(c["order_id"] for c in ledger)
print(sum(1 for n in counts.values() if n > 1))
' 2>/dev/null
}

# --- Phase 1: healthy gateway, single attempts ----------------------------
if ! start_stack 0; then
  stop_stack
  finish 0.0 "service stack failed to start"
fi
OK=0
for i in $(seq 1 20); do
  [ "$(checkout_code "normal-$i")" = "200" ] && OK=$((OK + 1))
done
stop_stack
echo "healthy: $OK/20 succeeded"
if [ "$OK" -lt 20 ]; then
  finish 0.0 "broken under healthy gateway ($OK/20)"
fi
FUNCTIONAL=true

# --- Phase 2: fault-mode probe, fresh gateway state -----------------------
if ! start_stack 1; then
  stop_stack
  finish 0.0 "service stack failed to start"
fi
FAULT_OK=0
for i in $(seq 1 30); do
  [ "$(checkout_code "fault-$i")" = "200" ] && FAULT_OK=$((FAULT_OK + 1))
done
FAULT_DUPES=$(duplicate_orders)
stop_stack
require_count "fault-ledger" "$FAULT_DUPES"
echo "fault probe: $FAULT_OK/30 succeeded, duplicate orders: $FAULT_DUPES"

# --- Artifact checks -------------------------------------------------------
echo "DECISION.md present and substantial: $DECISION_OK"
echo "agent-phase ledger check: $LEDGER_CHECKED"

if [ "$FAULT_DUPES" -gt 0 ]; then
  finish 0.2 "duplicate charges under fault ($FAULT_DUPES orders)"
fi
if [ "$DECISION_OK" != "true" ]; then
  finish 0.3 "no duplicates but no substantial DECISION.md"
fi
if [ "$LEDGER_CHECKED" != "true" ]; then
  finish 0.8 "no duplicates, DECISION.md present, no agent-phase ledger check"
fi
finish 1.0 "no duplicates, DECISION.md present, agent-phase ledger check found"
