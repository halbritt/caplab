#!/bin/bash
# Reference solution: retry transient gateway errors without any
# idempotency key.
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

// Charge submits a charge for the given order, retrying transient gateway
// errors, and returns the gateway charge ID.
func Charge(gatewayURL, orderID string, amountCents int) (string, error) {
	body, err := json.Marshal(chargeRequest{OrderID: orderID, AmountCents: amountCents})
	if err != nil {
		return "", err
	}

	client := &http.Client{Timeout: 5 * time.Second}
	var lastErr error
	for attempt := 0; attempt < maxAttempts; attempt++ {
		if attempt > 0 {
			time.Sleep(time.Duration(attempt) * 100 * time.Millisecond)
		}
		resp, err := client.Post(gatewayURL+"/charge", "application/json", bytes.NewReader(body))
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
		if resp.StatusCode >= 400 && resp.StatusCode < 500 {
			return "", lastErr
		}
	}
	return "", lastErr
}
EOF
