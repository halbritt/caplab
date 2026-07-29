package report

import (
	"testing"
	"time"
)

func TestTrackerTrimsToWindow(t *testing.T) {
	tr := NewTracker(3)
	for i := 0; i < 5; i++ {
		tr.Record(Sample{Endpoint: "https://a.example.net", Healthy: true, Elapsed: 10 * time.Millisecond})
	}
	if got := tr.Snapshot().Polls; got != 3 {
		t.Errorf("window: got %d polls, want 3", got)
	}
}

func TestSnapshotAvailabilityAndTop(t *testing.T) {
	tr := NewTracker(10)
	tr.Record(Sample{Endpoint: "https://a.example.net", Healthy: true, Elapsed: 20 * time.Millisecond})
	tr.Record(Sample{Endpoint: "https://b.example.net", Healthy: true, Elapsed: 40 * time.Millisecond})
	tr.Record(Sample{Endpoint: "https://a.example.net", Healthy: true, Elapsed: 30 * time.Millisecond})
	tr.Record(Sample{}) // failed poll

	s := tr.Snapshot()
	if s.Polls != 4 || s.Available != 3 {
		t.Fatalf("got polls=%d available=%d, want 4/3", s.Polls, s.Available)
	}
	if s.MeanLatency != 30*time.Millisecond {
		t.Errorf("mean latency: got %s, want 30ms", s.MeanLatency)
	}
	if s.TopEndpoint != "https://a.example.net" || s.TopEndpointN != 2 {
		t.Errorf("top endpoint: got %s (%d)", s.TopEndpoint, s.TopEndpointN)
	}
}

func TestLineEmptyWindow(t *testing.T) {
	if got := (Summary{}).Line(); got != "no polls yet" {
		t.Errorf("empty line: got %q", got)
	}
}
