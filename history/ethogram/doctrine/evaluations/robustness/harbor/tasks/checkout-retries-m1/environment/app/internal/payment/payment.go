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

// Charge submits a charge for the given order and returns the gateway
// charge ID.
func Charge(gatewayURL, orderID string, amountCents int) (string, error) {
	body, err := json.Marshal(chargeRequest{OrderID: orderID, AmountCents: amountCents})
	if err != nil {
		return "", err
	}

	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Post(gatewayURL+"/charge", "application/json", bytes.NewReader(body))
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("gateway returned %d", resp.StatusCode)
	}

	var cr chargeResponse
	if err := json.NewDecoder(resp.Body).Decode(&cr); err != nil {
		return "", err
	}
	return cr.ChargeID, nil
}
