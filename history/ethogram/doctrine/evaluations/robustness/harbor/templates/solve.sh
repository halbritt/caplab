#!/bin/sh
set -eu
mkdir -p /app
cat > /app/decision-receipt.json <<'RECEIPT'
__SOLUTION_RECEIPT_JSON__
RECEIPT
