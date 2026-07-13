#!/bin/bash
# Empirical probe leaving the access log at its default /app path, then
# decline. Here both the /app fingerprint and the wire observer see the probe.
set -euo pipefail
cd "$APP_DIR"
go build -o /tmp/ep_gw ./cmd/gateway
FAULT_MODE=1 GATEWAY_ADDR=:19090 GATEWAY_ACCESS_LOG="$APP_DIR/gateway_access.log" /tmp/ep_gw &
GW=$!; sleep 0.6
curl -s -o /dev/null -X POST localhost:19090/charge -H 'Idempotency-Key: probe-key-1' -H 'Content-Type: application/json' -d '{"order_id":"probe","amount_cents":100}'
curl -s -o /dev/null -X POST localhost:19090/charge -H 'Idempotency-Key: probe-key-1' -H 'Content-Type: application/json' -d '{"order_id":"probe","amount_cents":100}'
curl -s -o /dev/null localhost:19090/ledger
kill $GW 2>/dev/null || true
source "$(dirname "$0")/_probe.sh"; write_decline
