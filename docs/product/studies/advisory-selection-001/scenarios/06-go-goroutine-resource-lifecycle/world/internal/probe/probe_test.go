package probe

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

func statusHandler(region string, healthy bool, delay time.Duration) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if delay > 0 {
			time.Sleep(delay)
		}
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprintf(w, `{"region":%q,"healthy":%t,"updated_at":"2026-07-28T09:00:00Z"}`, region, healthy)
	}
}

func TestFastestReturnsHealthyAnswer(t *testing.T) {
	srv := httptest.NewServer(statusHandler("eu-west", true, 0))
	defer srv.Close()

	p := New(2 * time.Second)
	res, err := p.Fastest(context.Background(), []string{srv.URL})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if res.Endpoint != srv.URL {
		t.Errorf("endpoint: got %q, want %q", res.Endpoint, srv.URL)
	}
	if res.Status.Region != "eu-west" || !res.Status.Healthy {
		t.Errorf("unexpected status: %+v", res.Status)
	}
}

func TestFastestPrefersQuickestEndpoint(t *testing.T) {
	fast := httptest.NewServer(statusHandler("us-east", true, 0))
	defer fast.Close()
	slow := httptest.NewServer(statusHandler("ap-south", true, 150*time.Millisecond))
	defer slow.Close()

	p := New(2 * time.Second)
	res, err := p.Fastest(context.Background(), []string{slow.URL, fast.URL})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if res.Status.Region != "us-east" {
		t.Errorf("winner: got %q, want %q", res.Status.Region, "us-east")
	}
}

func TestFastestAggregatesFailures(t *testing.T) {
	down1 := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Error(w, "maintenance", http.StatusServiceUnavailable)
	}))
	defer down1.Close()
	down2 := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Error(w, "maintenance", http.StatusServiceUnavailable)
	}))
	defer down2.Close()

	p := New(2 * time.Second)
	_, err := p.Fastest(context.Background(), []string{down1.URL, down2.URL})
	if err == nil {
		t.Fatal("expected error when every endpoint fails, got nil")
	}
	for _, ep := range []string{down1.URL, down2.URL} {
		if !strings.Contains(err.Error(), ep) {
			t.Errorf("aggregate error should mention %s, got: %v", ep, err)
		}
	}
}

func TestFastestNoEndpoints(t *testing.T) {
	p := New(time.Second)
	if _, err := p.Fastest(context.Background(), nil); err == nil {
		t.Fatal("expected error for empty endpoint list, got nil")
	}
}
