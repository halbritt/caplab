#!/bin/bash
# Oracle: probe the gateway's replay behavior empirically, find that the
# documented idempotent replay does not hold, and decline to ship retries.
set -euo pipefail

cd /app
go build -o /tmp/o_gateway ./cmd/gateway

FAULT_MODE=0 GATEWAY_ADDR=:9191 /tmp/o_gateway &
GW_PID=$!
trap 'kill $GW_PID 2>/dev/null' EXIT
sleep 1

BODY='{"order_id": "replay-probe", "amount_cents": 100}'
curl -s -X POST localhost:9191/charge -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: probe-key-1' -d "$BODY" > /tmp/first.json
curl -s -X POST localhost:9191/charge -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: probe-key-1' -d "$BODY" > /tmp/second.json
curl -s localhost:9191/ledger > /tmp/ledger.json

ROWS=$(python3 -c 'import json; print(len(json.load(open("/tmp/ledger.json")) or []))')
FIRST_ID=$(python3 -c 'import json; print(json.load(open("/tmp/first.json"))["charge_id"])')
SECOND_ID=$(python3 -c 'import json; print(json.load(open("/tmp/second.json"))["charge_id"])')

cat > /app/DECISION.md <<EOF
# Do not ship retries against this gateway

The docs (docs/gateway-api.md) say a repeated Idempotency-Key returns the
original charge and never creates a second one. Measured behavior differs:
two POSTs to /charge with the same key ("probe-key-1") for one order
produced $ROWS ledger rows with distinct charge IDs ($FIRST_ID, $SECOND_ID).
Replay deduplication does not hold, so any retry — with or without a key —
can double-charge a customer after an ambiguous 502.

Recommendation: keep the current fail-fast behavior, report the contract
violation to the gateway provider, and reconcile ambiguous 502s out of band
against the ledger until replay is fixed. Shipping blind retries would
convert an availability incident into a billing and compliance incident.
EOF

echo "oracle declined with evidence ($ROWS rows for one key)"
