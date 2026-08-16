// Package config parses and validates the daemon's endpoint configuration.
package config

import (
	"errors"
	"fmt"
	"net/url"
	"strings"
)

// Endpoints turns a comma-separated flag value into a validated,
// de-duplicated list of absolute HTTP(S) URLs. Order is preserved;
// the first occurrence of a duplicate wins.
func Endpoints(raw string) ([]string, error) {
	if strings.TrimSpace(raw) == "" {
		return nil, errors.New("config: no endpoints given")
	}

	seen := make(map[string]struct{})
	var out []string
	for _, part := range strings.Split(raw, ",") {
		ep := strings.TrimSpace(part)
		if ep == "" {
			continue
		}
		u, err := url.Parse(ep)
		if err != nil {
			return nil, fmt.Errorf("config: bad endpoint %q: %w", ep, err)
		}
		if u.Scheme != "http" && u.Scheme != "https" {
			return nil, fmt.Errorf("config: endpoint %q must be http or https", ep)
		}
		if u.Host == "" {
			return nil, fmt.Errorf("config: endpoint %q has no host", ep)
		}
		key := u.String()
		if _, dup := seen[key]; dup {
			continue
		}
		seen[key] = struct{}{}
		out = append(out, key)
	}
	if len(out) == 0 {
		return nil, errors.New("config: no endpoints given")
	}
	return out, nil
}
