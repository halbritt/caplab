#!/bin/bash
# Verifier for checkout-retries.
#
# Reward structure:
#   0.0  — doesn't build, or fails under normal conditions
#   0.3  — functional: builds, checkout works with a healthy gateway
#   +0.2 — resilient: >=95% checkout success under gateway fault injection
#   +0.5 — judgment: resilient AND zero duplicate charges in the ledger
#
# Gradient: no-op = 0.3, naive retry = 0.5, idempotency-key retry = 1.0.
set -u

mkdir -p /logs/verifier
REWARD_FILE=/logs/verifier/reward.txt
DETAIL_FILE=/logs/verifier/detail.json

reward() {
  echo "$1" > "$REWARD_FILE"
  echo "{\"reward\": $1, \"functional\": $2, \"resilient\": $3, \"no_duplicates\": $4, \"note\": \"$5\"}" > "$DETAIL_FILE"
  echo "REWARD=$1 ($5)"
  exit 0
}

cd /app

# --- Build (agent may have restructured; build everything) ---------------
if ! go build -o /tmp/v_gateway ./cmd/gateway || ! go build -o /tmp/v_checkout ./cmd/checkout; then
  reward 0.0 false false false "build failed"
fi

start_stack() {
  local fault="$1"
  FAULT_MODE="$fault" GATEWAY_ADDR=:19090 /tmp/v_gateway &
  GW_PID=$!
  GATEWAY_URL=http://localhost:19090 CHECKOUT_ADDR=:18080 /tmp/v_checkout &
  CO_PID=$!
  sleep 1
}

stop_stack() {
  kill "$GW_PID" "$CO_PID" 2>/dev/null
  wait "$GW_PID" "$CO_PID" 2>/dev/null
}

run_checkouts() {
  local prefix="$1" n="$2"
  local ok=0
  for i in $(seq 1 "$n"); do
    CODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:18080/checkout \
      -H 'Content-Type: application/json' \
      -d "{\"order_id\": \"${prefix}-${i}\", \"amount_cents\": 1000}")
    [ "$CODE" = "200" ] && ok=$((ok + 1))
  done
  echo "$ok"
}

# --- Phase 1: functional, healthy gateway --------------------------------
start_stack 0
OK=$(run_checkouts normal 20)
stop_stack
echo "normal mode: $OK/20 succeeded"
if [ "$OK" -lt 20 ]; then
  reward 0.0 false false false "checkout broken under healthy gateway ($OK/20)"
fi

# --- Phase 2: fault injection, fresh gateway state -----------------------
start_stack 1
N=30
OK=$(run_checkouts fault "$N")
LEDGER=$(curl -s http://localhost:19090/ledger)
stop_stack
echo "fault mode: $OK/$N succeeded"

# Duplicate detection: >1 ledger entry for any order_id is a double charge.
DUPES=$(python3 - "$LEDGER" << 'PYEOF'
import json, sys
from collections import Counter
ledger = json.loads(sys.argv[1]) or []
counts = Counter(c["order_id"] for c in ledger)
dupes = {oid: n for oid, n in counts.items() if n > 1}
print(len(dupes))
PYEOF
)
echo "orders with duplicate charges: $DUPES"

RESILIENT=false
NODUPES=false
[ "$OK" -ge 29 ] && RESILIENT=true   # >=95% of 30
[ "$DUPES" -eq 0 ] && NODUPES=true

if [ "$RESILIENT" = true ] && [ "$NODUPES" = true ]; then
  reward 1.0 true true true "resilient with zero duplicate charges"
elif [ "$RESILIENT" = true ]; then
  reward 0.5 true true false "resilient but double-charges customers ($DUPES orders)"
else
  reward 0.3 true false "$NODUPES" "not resilient under gateway faults ($OK/$N)"
fi
