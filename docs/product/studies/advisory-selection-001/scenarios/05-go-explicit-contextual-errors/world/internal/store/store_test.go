package store_test

import (
	"errors"
	"io"
	"os"
	"path/filepath"
	"testing"

	"github.com/meridian-ops/depotsync/internal/store"
)

func TestOpenReadsObject(t *testing.T) {
	root := t.TempDir()
	if err := os.MkdirAll(filepath.Join(root, "blobs"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, "blobs", "aa11"), []byte("payload"), 0o644); err != nil {
		t.Fatal(err)
	}
	st, err := store.New(root)
	if err != nil {
		t.Fatalf("New: %v", err)
	}
	rc, err := st.Open("blobs/aa11")
	if err != nil {
		t.Fatalf("Open: %v", err)
	}
	defer rc.Close()
	b, err := io.ReadAll(rc)
	if err != nil {
		t.Fatalf("ReadAll: %v", err)
	}
	if string(b) != "payload" {
		t.Fatalf("got %q, want %q", b, "payload")
	}
}

func TestOpenMissingObjectReportsNotFound(t *testing.T) {
	st, err := store.New(t.TempDir())
	if err != nil {
		t.Fatalf("New: %v", err)
	}
	_, err = st.Open("blobs/absent")
	if err == nil {
		t.Fatal("want error for missing object")
	}
	if !errors.Is(err, store.ErrNotFound) {
		t.Fatalf("error %v does not identify as ErrNotFound", err)
	}
}

func TestNewRejectsMissingRoot(t *testing.T) {
	if _, err := store.New(filepath.Join(t.TempDir(), "nope")); err == nil {
		t.Fatal("want error for missing archive root")
	}
}
