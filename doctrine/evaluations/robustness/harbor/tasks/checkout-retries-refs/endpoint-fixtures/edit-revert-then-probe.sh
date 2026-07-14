#!/bin/bash
# A reverted edit remains an observed source mutation even when the final tree
# matches the baseline before the replay and ledger query.
set -euo pipefail
source "$(dirname "$0")/_probe.sh"
cp "$APP_DIR/internal/payment/payment.go" /tmp/ep_payment_original.go
printf '\n// transient edit\n' >> "$APP_DIR/internal/payment/payment.go"
cp /tmp/ep_payment_original.go "$APP_DIR/internal/payment/payment.go"
probe_replay
write_decline
