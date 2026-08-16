// Package store reads objects out of a content archive laid out as
// plain files under a root directory.
package store

import (
	"errors"
	"fmt"
	"io"
	"io/fs"
	"os"
	"path/filepath"
)

// ErrNotFound reports that the archive has no object under the
// requested key. Callers that can tolerate a missing object should
// test for it with errors.Is.
var ErrNotFound = errors.New("object not found")

// Store reads objects from an archive rooted at a directory.
type Store struct {
	root string
}

// New opens an archive rooted at dir.
func New(dir string) (*Store, error) {
	info, err := os.Stat(dir)
	if err != nil {
		return nil, fmt.Errorf("archive root %s: %w", dir, err)
	}
	if !info.IsDir() {
		return nil, fmt.Errorf("archive root %s: not a directory", dir)
	}
	return &Store{root: dir}, nil
}

// Open opens the object stored under key for reading. The caller owns
// the returned reader and must close it. If the archive has no such
// object, the returned error wraps ErrNotFound.
func (s *Store) Open(key string) (io.ReadCloser, error) {
	f, err := os.Open(filepath.Join(s.root, filepath.FromSlash(key)))
	switch {
	case errors.Is(err, fs.ErrNotExist):
		return nil, fmt.Errorf("object %q: %w", key, ErrNotFound)
	case err != nil:
		return nil, fmt.Errorf("open object %q: %w", key, err)
	}
	return f, nil
}
