package config

import (
	"strings"
	"testing"
)

func TestEndpointsParsesAndDedupes(t *testing.T) {
	got, err := Endpoints(" https://a.example.net/health, http://b.example.net/health ,https://a.example.net/health")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	want := []string{"https://a.example.net/health", "http://b.example.net/health"}
	if len(got) != len(want) {
		t.Fatalf("got %d endpoints, want %d: %v", len(got), len(want), got)
	}
	for i := range want {
		if got[i] != want[i] {
			t.Errorf("endpoint %d: got %q, want %q", i, got[i], want[i])
		}
	}
}

func TestEndpointsRejectsEmpty(t *testing.T) {
	for _, raw := range []string{"", "   ", ",,,"} {
		if _, err := Endpoints(raw); err == nil {
			t.Errorf("Endpoints(%q): expected error, got nil", raw)
		}
	}
}

func TestEndpointsRejectsBadScheme(t *testing.T) {
	_, err := Endpoints("ftp://files.example.net/health")
	if err == nil {
		t.Fatal("expected error for ftp scheme, got nil")
	}
	if !strings.Contains(err.Error(), "http") {
		t.Errorf("error should mention required scheme, got: %v", err)
	}
}
