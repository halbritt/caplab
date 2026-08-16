// Package probe fetches the status document from every configured
// regional endpoint at once and returns the quickest healthy answer.
package probe

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"time"
)

// Status is the health document each regional endpoint serves.
type Status struct {
	Region    string    `json:"region"`
	Healthy   bool      `json:"healthy"`
	UpdatedAt time.Time `json:"updated_at"`
}

// Result pairs a decoded status with the endpoint that answered and
// how long the answer took.
type Result struct {
	Endpoint string
	Status   Status
	Elapsed  time.Duration
}

// Prober issues the concurrent status fetches.
type Prober struct {
	client *http.Client
}

// New returns a Prober whose requests give up after timeout.
func New(timeout time.Duration) *Prober {
	return &Prober{client: &http.Client{Timeout: timeout}}
}

type attempt struct {
	endpoint string
	resp     *http.Response
	elapsed  time.Duration
	err      error
}

// Fastest asks every endpoint at once and returns the first answer that
// comes back 200 with a decodable status document. If every endpoint
// fails, the per-endpoint errors are returned together.
func (p *Prober) Fastest(ctx context.Context, endpoints []string) (*Result, error) {
	if len(endpoints) == 0 {
		return nil, errors.New("probe: no endpoints configured")
	}

	ch := make(chan attempt)
	for _, ep := range endpoints {
		go func(ep string) {
			start := time.Now()
			resp, err := p.client.Get(ep)
			ch <- attempt{endpoint: ep, resp: resp, elapsed: time.Since(start), err: err}
		}(ep)
	}

	var errs []error
	for range endpoints {
		a := <-ch
		if a.err != nil {
			errs = append(errs, fmt.Errorf("%s: %w", a.endpoint, a.err))
			continue
		}
		if a.resp.StatusCode != http.StatusOK {
			errs = append(errs, fmt.Errorf("%s: unexpected status %s", a.endpoint, a.resp.Status))
			continue
		}
		var st Status
		if err := json.NewDecoder(a.resp.Body).Decode(&st); err != nil {
			a.resp.Body.Close()
			errs = append(errs, fmt.Errorf("%s: decode: %w", a.endpoint, err))
			continue
		}
		a.resp.Body.Close()
		return &Result{Endpoint: a.endpoint, Status: st, Elapsed: a.elapsed}, nil
	}
	return nil, fmt.Errorf("probe: all %d endpoints failed: %w", len(endpoints), errors.Join(errs...))
}
