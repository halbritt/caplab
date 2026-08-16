// Package report keeps a rolling window of poll outcomes and produces
// the one-line summary the daemon prints after each poll.
package report

import (
	"fmt"
	"sync"
	"time"
)

// Sample is the outcome of a single poll.
type Sample struct {
	Endpoint string        // winning endpoint, empty when the poll failed
	Healthy  bool          // what the winner reported
	Elapsed  time.Duration // winner latency, zero when the poll failed
	When     time.Time
}

// Tracker holds the most recent window of samples.
type Tracker struct {
	mu      sync.Mutex
	window  int
	samples []Sample
}

// NewTracker keeps at most window samples; window must be positive.
func NewTracker(window int) *Tracker {
	if window <= 0 {
		window = 1
	}
	return &Tracker{window: window}
}

// Record appends a sample, discarding the oldest once the window is full.
func (t *Tracker) Record(s Sample) {
	t.mu.Lock()
	defer t.mu.Unlock()
	t.samples = append(t.samples, s)
	if len(t.samples) > t.window {
		t.samples = t.samples[len(t.samples)-t.window:]
	}
}

// Summary describes the current window.
type Summary struct {
	Polls        int
	Available    int           // polls that returned a healthy answer
	MeanLatency  time.Duration // over available polls
	TopEndpoint  string        // endpoint that won most often
	TopEndpointN int
}

// Snapshot computes the summary for the current window.
func (t *Tracker) Snapshot() Summary {
	t.mu.Lock()
	defer t.mu.Unlock()

	var s Summary
	s.Polls = len(t.samples)
	wins := make(map[string]int)
	var totalLatency time.Duration
	for _, smp := range t.samples {
		if smp.Endpoint == "" || !smp.Healthy {
			continue
		}
		s.Available++
		totalLatency += smp.Elapsed
		wins[smp.Endpoint]++
	}
	if s.Available > 0 {
		s.MeanLatency = totalLatency / time.Duration(s.Available)
	}
	for ep, n := range wins {
		if n > s.TopEndpointN || (n == s.TopEndpointN && ep < s.TopEndpoint) {
			s.TopEndpoint = ep
			s.TopEndpointN = n
		}
	}
	return s
}

// Line renders the summary as the daemon's per-poll log line.
func (s Summary) Line() string {
	if s.Polls == 0 {
		return "no polls yet"
	}
	pct := 100 * float64(s.Available) / float64(s.Polls)
	return fmt.Sprintf("window=%d available=%.1f%% mean=%s top=%s (%d wins)",
		s.Polls, pct, s.MeanLatency.Round(time.Millisecond), s.TopEndpoint, s.TopEndpointN)
}
