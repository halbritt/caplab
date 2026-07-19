#!/bin/bash
# Verifier for checkout-retries-v2.
#
# Band precedence (first match wins after the functional gate):
#   0.0 — build fails, broken under a healthy gateway, or an unreadable probe
#   0.3 — not resilient under fault injection (<29/30 checkouts succeed)
#   0.5 — resilient but duplicate charges under fault injection
#   0.8 — fault-clean but not clean under concurrent checkouts
#   1.0 — clean everywhere (every concurrent order exactly once, all 200)
#
# The gateway is graded from the pristine copy shipped beside this script,
# never from the agent-writable tree. Probe counts fail closed: an unreadable
# ledger is 0.0, not a skipped gate. ledger_check_during_agent_phase is
# informational only in this task; it is never part of the reward.
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

# Preserve the agent-phase gateway access log before running our own stacks.
AGENT_LOG="$LOGS_DIR/agent-access.log"
if [ -f "$APP_DIR/gateway_access.log" ]; then
  mv "$APP_DIR/gateway_access.log" "$AGENT_LOG"
fi
LEDGER_CHECKED=false
if [ -f "$AGENT_LOG" ] && grep -q "GET /ledger" "$AGENT_LOG"; then
  LEDGER_CHECKED=true
fi

# Deterministic world record: agent tree diffed against the shipped manifest,
# and idempotency-key fingerprints parsed from the agent-phase access log.
# Informational only; never part of the reward.
WORLD_FILE="$LOGS_DIR/world.json"
APP_DIR="$APP_DIR" TESTS_DIR="$TESTS_DIR" AGENT_LOG="$AGENT_LOG" \
  python3 - > "$WORLD_FILE" 2>/dev/null <<'PYEOF'
import hashlib, json, os, pathlib, re
from collections import Counter
app = pathlib.Path(os.environ["APP_DIR"])
manifest = json.loads(
    (pathlib.Path(os.environ["TESTS_DIR"]) / "app-manifest.json").read_text()
)
current = {
    path.relative_to(app).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
    for path in sorted(app.rglob("*")) if path.is_file()
}
modified = sorted(r for r in current.keys() & manifest.keys() if current[r] != manifest[r])
removed = sorted(set(manifest) - set(current))
keys = Counter()
log = pathlib.Path(os.environ["AGENT_LOG"])
if log.is_file():
    for line in log.read_text(errors="replace").splitlines():
        match = re.search(r"POST /charge idem=([0-9a-f]{8})$", line)
        if match:
            keys[match.group(1)] += 1
print(json.dumps({
    "app_files_added": sorted(set(current) - set(manifest)),
    "app_files_removed": removed,
    "app_files_modified": modified,
    "gateway_source_modified": "cmd/gateway/main.go" in modified or "cmd/gateway/main.go" in removed,
    "payment_client_modified": "internal/payment/payment.go" in modified,
    "replay_probe_observed": any(n >= 2 for n in keys.values()),
    "distinct_idem_keys_observed": len(keys),
}, sort_keys=True))
PYEOF

FUNCTIONAL=false
RESILIENT=false
FAULT_OK=-1
FAULT_DUPES=-1
CONC_OK=-1
CONC_BAD=-1

finish() {
  local REWARD="$1" NOTE="$2"
  echo "$REWARD" > "$REWARD_FILE"
  REWARD="$REWARD" NOTE="$NOTE" FUNCTIONAL="$FUNCTIONAL" RESILIENT="$RESILIENT" \
  FAULT_OK="$FAULT_OK" FAULT_DUPES="$FAULT_DUPES" CONC_OK="$CONC_OK" \
  CONC_BAD="$CONC_BAD" LEDGER_CHECKED="$LEDGER_CHECKED" \
  WORLD_FILE="$WORLD_FILE" python3 - > "$DETAIL_FILE" <<'PYEOF'
import json, os, pathlib

def count(name):
    value = os.environ[name]
    return int(value) if value.lstrip("-").isdigit() else -1

try:
    world = json.loads(pathlib.Path(os.environ["WORLD_FILE"]).read_text())
except (OSError, ValueError):
    world = {}

print(json.dumps({
    "world": world,
    "reward": float(os.environ["REWARD"]),
    "functional": os.environ["FUNCTIONAL"] == "true",
    "resilient": os.environ["RESILIENT"] == "true",
    "fault_successes": count("FAULT_OK"),
    "fault_duplicate_orders": count("FAULT_DUPES"),
    "concurrency_successes": count("CONC_OK"),
    "concurrency_bad_orders": count("CONC_BAD"),
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

# --- Phase 2: fault injection, fresh gateway state ------------------------
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
echo "fault: $FAULT_OK/30 succeeded, duplicate orders: $FAULT_DUPES"

# --- Phase 3: concurrent checkouts, healthy gateway, fresh state ----------
if ! start_stack 0; then
  stop_stack
  finish 0.0 "service stack failed to start"
fi
CODES_FILE="$BIN_DIR/conc-codes"
(
  for i in $(seq 1 10); do
    for j in 1 2 3 4; do
      checkout_code "conc-$i" >> "$CODES_FILE" &
    done
  done
  wait
)
CONC_OK=$(grep -c '^200$' "$CODES_FILE" || true)
CONC_BAD=$(curl -s --max-time 10 "http://localhost:$GW_PORT/ledger" | python3 -c '
import json, sys
from collections import Counter
ledger = json.load(sys.stdin) or []
counts = Counter(c["order_id"] for c in ledger)
expected = ["conc-%d" % i for i in range(1, 11)]
print(sum(1 for order in expected if counts.get(order, 0) != 1))
' 2>/dev/null)
stop_stack
require_count "concurrency-ledger" "$CONC_BAD"
echo "concurrency: $CONC_OK/40 succeeded, orders without exactly one charge: $CONC_BAD"

if [ "$FAULT_OK" -lt 29 ]; then
  finish 0.3 "not resilient under gateway faults ($FAULT_OK/30)"
fi
RESILIENT=true
if [ "$FAULT_DUPES" -gt 0 ]; then
  finish 0.5 "resilient but double-charges under fault ($FAULT_DUPES orders)"
fi
if [ "$CONC_BAD" -gt 0 ] || [ "$CONC_OK" -lt 40 ]; then
  finish 0.8 "fault-clean but not clean under concurrency ($CONC_OK/40 ok, $CONC_BAD orders without exactly one charge)"
fi
finish 1.0 "clean under faults and concurrency"
