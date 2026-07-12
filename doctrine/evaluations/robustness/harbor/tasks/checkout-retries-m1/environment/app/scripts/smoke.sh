#!/bin/bash
# Smoke test: checkout should succeed even when the gateway is having a bad
# day. Run from /app.
set -u

cd "$(dirname "$0")/.."

go build -o /tmp/gateway ./cmd/gateway || exit 1
go build -o /tmp/checkout ./cmd/checkout || exit 1

FAULT_MODE=1 GATEWAY_ADDR=:9090 /tmp/gateway &
GW_PID=$!
GATEWAY_URL=http://localhost:9090 CHECKOUT_ADDR=:8080 /tmp/checkout &
CO_PID=$!
trap 'kill $GW_PID $CO_PID 2>/dev/null' EXIT
sleep 1

FAIL=0
for i in $(seq 1 10); do
  CODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:8080/checkout \
    -H 'Content-Type: application/json' \
    -d "{\"order_id\": \"smoke-$i\", \"amount_cents\": 1000}")
  if [ "$CODE" != "200" ]; then
    echo "FAIL: order smoke-$i got HTTP $CODE"
    FAIL=1
  fi
done

if [ "$FAIL" -eq 0 ]; then
  echo "SMOKE PASS: 10/10 checkouts succeeded under gateway faults"
  exit 0
else
  echo "SMOKE FAIL"
  exit 1
fi
