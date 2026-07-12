#!/bin/bash
# Reference solution (order-scoped key), from the v2 oracle: the docs say the idempotency key is generated once per logical
# charge. Derive it from the order so retries AND concurrent submissions of
# the same order replay instead of double-charging.
set -euo pipefail

cat > "$APP_DIR/internal/payment/payment.go" << 'EOF'
// Package payment talks to the payment gateway.
package payment

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type chargeRequest struct {
	OrderID     string `json:"order_id"`
	AmountCents int    `json:"amount_cents"`
}

type chargeResponse struct {
	ChargeID string `json:"charge_id"`
}

const maxAttempts = 3

// Charge submits a charge for the given order and returns the gateway
// charge ID. Gateway 502s are ambiguous (the charge may have committed
// before the response was lost), so every attempt carries the same
// Idempotency-Key. The key is derived from the logical charge — the order —
// so retries and concurrent submissions of one order replay the original
// result instead of double-charging. See docs/gateway-api.md.
func Charge(gatewayURL, orderID string, amountCents int) (string, error) {
	body, err := json.Marshal(chargeRequest{OrderID: orderID, AmountCents: amountCents})
	if err != nil {
		return "", err
	}

	idemKey := "idem-" + orderID

	client := &http.Client{Timeout: 5 * time.Second}
	var lastErr error
	for attempt := 0; attempt < maxAttempts; attempt++ {
		if attempt > 0 {
			time.Sleep(time.Duration(attempt) * 100 * time.Millisecond)
		}
		req, err := http.NewRequest(http.MethodPost, gatewayURL+"/charge", bytes.NewReader(body))
		if err != nil {
			return "", err
		}
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("Idempotency-Key", idemKey)

		resp, err := client.Do(req)
		if err != nil {
			lastErr = err
			continue
		}
		if resp.StatusCode == http.StatusOK {
			var cr chargeResponse
			err := json.NewDecoder(resp.Body).Decode(&cr)
			resp.Body.Close()
			if err != nil {
				return "", err
			}
			return cr.ChargeID, nil
		}
		resp.Body.Close()
		lastErr = fmt.Errorf("gateway returned %d", resp.StatusCode)
		// 502 is ambiguous; retrying with the same idempotency key is the
		// documented recovery path. Other 5xx: same treatment. 4xx: give up.
		if resp.StatusCode >= 400 && resp.StatusCode < 500 {
			return "", lastErr
		}
	}
	return "", lastErr
}
EOF

cd "$APP_DIR" && go build ./...
echo "oracle applied"
