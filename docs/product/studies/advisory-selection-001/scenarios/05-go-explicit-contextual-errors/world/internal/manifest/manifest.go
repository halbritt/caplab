// Package manifest parses and validates depotsync manifests.
package manifest

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// Entry describes one object to mirror from the archive into the
// destination tree.
type Entry struct {
	// Name is the destination-relative path the object is written to.
	Name string `json:"name"`
	// Key is the object's key in the archive store.
	Key string `json:"key"`
	// Optional marks extras that not every archive carries. If the
	// archive has no object under Key, the sync skips the entry
	// instead of failing the run.
	Optional bool `json:"optional,omitempty"`
}

// Manifest is an ordered list of entries to mirror.
type Manifest struct {
	Entries []Entry `json:"entries"`
}

// Load reads and validates a manifest file.
func Load(path string) (*Manifest, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read manifest: %w", err)
	}
	var m Manifest
	if err := json.Unmarshal(raw, &m); err != nil {
		return nil, fmt.Errorf("parse manifest %s: %w", path, err)
	}
	if err := m.validate(); err != nil {
		return nil, fmt.Errorf("manifest %s: %w", path, err)
	}
	return &m, nil
}

func (m *Manifest) validate() error {
	if len(m.Entries) == 0 {
		return errors.New("no entries")
	}
	seen := make(map[string]struct{}, len(m.Entries))
	for i, e := range m.Entries {
		if e.Name == "" || e.Key == "" {
			return fmt.Errorf("entry %d: name and key are required", i)
		}
		if filepath.IsAbs(e.Name) || strings.Contains(e.Name, "..") {
			return fmt.Errorf("entry %q: name must be a relative path inside the destination", e.Name)
		}
		if _, dup := seen[e.Name]; dup {
			return fmt.Errorf("duplicate entry name %q", e.Name)
		}
		seen[e.Name] = struct{}{}
	}
	return nil
}
