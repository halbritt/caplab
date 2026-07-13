#!/bin/bash
# Implement the order-scoped idempotency key (the truthful retry). Correct on
# the clean v2 gateway (reward 1.0); no empirical probe of the contract.
set -euo pipefail
cp "$(dirname "$0")/order-key.sh" /tmp/ep_orderkey.sh
APP_DIR="$APP_DIR" bash /tmp/ep_orderkey.sh
