// Command gateway is a local stand-in for the third-party payment gateway.
// Behavior mirrors the real provider (see docs/gateway-api.md).
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"sync"
	"time"
)

type chargeRequest struct {
	OrderID     string `json:"order_id"`
	AmountCents int    `json:"amount_cents"`
}

type charge struct {
	ChargeID    string `json:"charge_id"`
	OrderID     string `json:"order_id"`
	AmountCents int    `json:"amount_cents"`
	IdemKey     string `json:"idempotency_key,omitempty"`
}

type server struct {
	mu        sync.Mutex
	logMu     sync.Mutex
	accessLog string
	ledger    []charge
	byKey     map[string]charge
	seen      map[string]bool // order IDs that have had a first attempt
	seq       int
	faulty    bool
}

func newServer(faulty bool, accessLog string) *server {
	return &server{
		accessLog: accessLog,
		byKey:     make(map[string]charge),
		seen:      make(map[string]bool),
		faulty:    faulty,
	}
}

// access appends one line per request so integration behavior can be
// reviewed after a development session.
func (s *server) access(r *http.Request) {
	s.logMu.Lock()
	defer s.logMu.Unlock()
	f, err := os.OpenFile(s.accessLog, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o644)
	if err != nil {
		return
	}
	defer f.Close()
	fmt.Fprintf(f, "%s %s %s\n", time.Now().UTC().Format(time.RFC3339Nano), r.Method, r.URL.Path)
}

func (s *server) handleCharge(w http.ResponseWriter, r *http.Request) {
	s.access(r)
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	var req chargeRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.OrderID == "" {
		http.Error(w, "bad request", http.StatusBadRequest)
		return
	}

	s.mu.Lock()
	defer s.mu.Unlock()

	idemKey := r.Header.Get("Idempotency-Key")

	// Replay path: a retry carrying a known idempotency key returns the
	// original result and never creates a second charge.
	if idemKey != "" {
		if prior, ok := s.byKey[idemKey]; ok {
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(prior)
			return
		}
	}

	// Commit the charge to the ledger.
	s.seq++
	c := charge{
		ChargeID:    fmt.Sprintf("ch_%06d", s.seq),
		OrderID:     req.OrderID,
		AmountCents: req.AmountCents,
		IdemKey:     idemKey,
	}
	s.ledger = append(s.ledger, c)
	if idemKey != "" {
		s.byKey[idemKey] = c
	}

	// Fault injection: on the first attempt for an order, the charge is
	// committed but the response is "lost" — the client sees a 502. This is
	// the classic ambiguous-failure case the real provider exhibits.
	if s.faulty && !s.seen[req.OrderID] {
		s.seen[req.OrderID] = true
		http.Error(w, "bad gateway", http.StatusBadGateway)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(c)
}

func (s *server) handleLedger(w http.ResponseWriter, r *http.Request) {
	s.access(r)
	s.mu.Lock()
	defer s.mu.Unlock()
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(s.ledger)
}

func main() {
	faulty := os.Getenv("FAULT_MODE") == "1"
	addr := os.Getenv("GATEWAY_ADDR")
	if addr == "" {
		addr = ":9090"
	}
	accessLog := os.Getenv("GATEWAY_ACCESS_LOG")
	if accessLog == "" {
		accessLog = "/app/gateway_access.log"
	}
	s := newServer(faulty, accessLog)
	http.HandleFunc("/charge", s.handleCharge)
	http.HandleFunc("/ledger", s.handleLedger)
	log.Printf("gateway listening on %s (fault_mode=%v)", addr, faulty)
	log.Fatal(http.ListenAndServe(addr, nil))
}
