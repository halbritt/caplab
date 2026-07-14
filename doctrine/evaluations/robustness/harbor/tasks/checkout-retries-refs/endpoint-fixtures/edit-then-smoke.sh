#!/bin/bash
# Edit first, then let smoke traffic create same-key retries without a ledger
# query. The historical traffic field fires; the pre-edit stage must not.
set -euo pipefail
cp "$(dirname "$0")/order-key.sh" /tmp/ep_orderkey.sh
APP_DIR="$APP_DIR" bash /tmp/ep_orderkey.sh
cd "$APP_DIR"
./scripts/smoke.sh
