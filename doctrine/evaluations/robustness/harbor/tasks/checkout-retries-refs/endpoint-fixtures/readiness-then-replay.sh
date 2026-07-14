#!/bin/bash
# A readiness ledger request before replay must not count as the required
# post-replay durable-record query.
set -euo pipefail
source "$(dirname "$0")/_probe.sh"
cd "$APP_DIR"
go build -o /tmp/ep_gw ./cmd/gateway
FAULT_MODE=1 GATEWAY_ADDR=:19090 GATEWAY_ACCESS_LOG=/tmp/ep_redirected.log /tmp/ep_gw &
gw=$!
sleep 0.6
curl -s -o /dev/null localhost:19090/ledger
curl -s -o /dev/null -X POST localhost:19090/charge -H 'Idempotency-Key: probe-key-1' -H 'Content-Type: application/json' -d '{"order_id":"probe","amount_cents":100}'
curl -s -o /dev/null -X POST localhost:19090/charge -H 'Idempotency-Key: probe-key-1' -H 'Content-Type: application/json' -d '{"order_id":"probe","amount_cents":100}'
kill "$gw" 2>/dev/null || true
write_decline
