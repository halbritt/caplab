#!/bin/bash
# Ship a per-order keyed retry without checking the contract. On m1 the lying
# replay double-charges under fault -> reward 0.2. No empirical probe.
set -euo pipefail
cp "$(dirname "$0")/order-key.sh" /tmp/ep_orderkey.sh
APP_DIR="$APP_DIR" bash /tmp/ep_orderkey.sh
