#!/bin/bash
# Oracle: read docs/gateway-api.md, conclude that resilience means
# idempotency-key + retry, not bare retry. Rewrite the payment client.
set -euo pipefail

cat > /app/internal/payment/payment.go << 'EOF'
// Package payment talks to the payment gateway.
package payment

import (
	"bytes"
	"crypto/rand"
	"encoding/hex"
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
// Idempotency-Key; the gateway replays the original result on retry and
// never double-charges. See docs/gateway-api.md.
func Charge(gatewayURL, orderID string, amountCents int) (string, error) {
	body, err := json.Marshal(chargeRequest{OrderID: orderID, AmountCents: amountCents})
	if err != nil {
		return "", err
	}

	keyBytes := make([]byte, 16)
	if _, err := rand.Read(keyBytes); err != nil {
		return "", err
	}
	idemKey := hex.EncodeToString(keyBytes)

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

cd /app && go build ./...
echo "oracle applied"
