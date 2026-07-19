// Command checkout is the customer-facing checkout service.
package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"

	"checkout/internal/payment"
)

type checkoutRequest struct {
	OrderID     string `json:"order_id"`
	AmountCents int    `json:"amount_cents"`
}

type checkoutResponse struct {
	Status   string `json:"status"`
	ChargeID string `json:"charge_id,omitempty"`
}

func main() {
	gatewayURL := os.Getenv("GATEWAY_URL")
	if gatewayURL == "" {
		gatewayURL = "http://localhost:9090"
	}
	addr := os.Getenv("CHECKOUT_ADDR")
	if addr == "" {
		addr = ":8080"
	}

	http.HandleFunc("/checkout", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
			return
		}
		var req checkoutRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.OrderID == "" {
			http.Error(w, "bad request", http.StatusBadRequest)
			return
		}

		chargeID, err := payment.Charge(gatewayURL, req.OrderID, req.AmountCents)
		if err != nil {
			log.Printf("checkout failed for order %s: %v", req.OrderID, err)
			http.Error(w, "payment failed", http.StatusBadGateway)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(checkoutResponse{Status: "paid", ChargeID: chargeID})
	})

	log.Printf("checkout listening on %s (gateway=%s)", addr, gatewayURL)
	log.Fatal(http.ListenAndServe(addr, nil))
}
