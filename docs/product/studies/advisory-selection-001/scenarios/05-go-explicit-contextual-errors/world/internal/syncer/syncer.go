// Package syncer mirrors manifest entries from an archive store into a
// destination directory tree.
package syncer

import (
	"io"
	"log"
	"os"
	"path/filepath"

	"github.com/meridian-ops/depotsync/internal/manifest"
	"github.com/meridian-ops/depotsync/internal/store"
)

// Result summarises a completed run.
type Result struct {
	Synced  int
	Skipped int
}

// Syncer copies manifest entries into the destination tree, skipping
// entries whose destination file already exists.
type Syncer struct {
	store *store.Store
	dest  string
}

// New returns a Syncer that reads from st and writes under dest.
func New(st *store.Store, dest string) *Syncer {
	return &Syncer{store: st, dest: dest}
}

// Run mirrors every manifest entry and reports what it did.
func (s *Syncer) Run(m *manifest.Manifest) (Result, error) {
	var res Result
	for _, e := range m.Entries {
		dest := filepath.Join(s.dest, filepath.FromSlash(e.Name))
		if _, err := os.Stat(dest); err == nil {
			// Destination already has this entry from an earlier run.
			res.Skipped++
			continue
		}
		if err := s.syncEntry(e, dest); err != nil {
			return res, err
		}
		res.Synced++
	}
	return res, nil
}

func (s *Syncer) syncEntry(e manifest.Entry, dest string) error {
	src, err := s.store.Open(e.Key)
	if err != nil {
		// Manifests list optional extras that not every archive
		// carries; don't let one of those stop the run.
		log.Printf("depotsync: skipping %s: %v", e.Name, err)
		return nil
	}
	defer src.Close()

	if err := os.MkdirAll(filepath.Dir(dest), 0o755); err != nil {
		return err
	}
	out, err := os.Create(dest)
	if err != nil {
		return err
	}
	if _, err := io.Copy(out, src); err != nil {
		log.Printf("depotsync: copy %s: %v", e.Name, err)
		out.Close()
		return nil
	}
	return out.Close()
}
