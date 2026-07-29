package syncer_test

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/meridian-ops/depotsync/internal/manifest"
	"github.com/meridian-ops/depotsync/internal/store"
	"github.com/meridian-ops/depotsync/internal/syncer"
)

func newTestStore(t *testing.T, objects map[string]string) *store.Store {
	t.Helper()
	root := t.TempDir()
	for key, content := range objects {
		path := filepath.Join(root, filepath.FromSlash(key))
		if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	st, err := store.New(root)
	if err != nil {
		t.Fatal(err)
	}
	return st
}

func readFile(t *testing.T, path string) string {
	t.Helper()
	b, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	return string(b)
}

func TestRunMirrorsEntries(t *testing.T) {
	st := newTestStore(t, map[string]string{
		"blobs/aa11": "release payload",
		"blobs/bb22": "helper script",
	})
	dest := t.TempDir()
	m := &manifest.Manifest{Entries: []manifest.Entry{
		{Name: "release/app.bin", Key: "blobs/aa11"},
		{Name: "bin/helper.sh", Key: "blobs/bb22"},
	}}

	res, err := syncer.New(st, dest).Run(m)
	if err != nil {
		t.Fatalf("Run: %v", err)
	}
	if res.Synced != 2 || res.Skipped != 0 {
		t.Fatalf("got %+v, want 2 synced, 0 skipped", res)
	}
	if got := readFile(t, filepath.Join(dest, "release", "app.bin")); got != "release payload" {
		t.Fatalf("app.bin = %q", got)
	}
	if got := readFile(t, filepath.Join(dest, "bin", "helper.sh")); got != "helper script" {
		t.Fatalf("helper.sh = %q", got)
	}
}

func TestRunSkipsEntriesAlreadyPresent(t *testing.T) {
	st := newTestStore(t, map[string]string{"blobs/aa11": "new payload"})
	dest := t.TempDir()
	if err := os.MkdirAll(filepath.Join(dest, "release"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dest, "release", "app.bin"), []byte("existing payload"), 0o644); err != nil {
		t.Fatal(err)
	}
	m := &manifest.Manifest{Entries: []manifest.Entry{
		{Name: "release/app.bin", Key: "blobs/aa11"},
	}}

	res, err := syncer.New(st, dest).Run(m)
	if err != nil {
		t.Fatalf("Run: %v", err)
	}
	if res.Synced != 0 || res.Skipped != 1 {
		t.Fatalf("got %+v, want 0 synced, 1 skipped", res)
	}
	if got := readFile(t, filepath.Join(dest, "release", "app.bin")); got != "existing payload" {
		t.Fatalf("existing file was rewritten: %q", got)
	}
}

func TestRunToleratesMissingOptionalEntry(t *testing.T) {
	st := newTestStore(t, map[string]string{"blobs/aa11": "release payload"})
	dest := t.TempDir()
	m := &manifest.Manifest{Entries: []manifest.Entry{
		{Name: "release/app.bin", Key: "blobs/aa11"},
		{Name: "extras/debug-symbols.tar", Key: "blobs/none", Optional: true},
	}}

	_, err := syncer.New(st, dest).Run(m)
	if err != nil {
		t.Fatalf("Run: %v", err)
	}
	if got := readFile(t, filepath.Join(dest, "release", "app.bin")); got != "release payload" {
		t.Fatalf("app.bin = %q", got)
	}
	if _, err := os.Stat(filepath.Join(dest, "extras", "debug-symbols.tar")); !os.IsNotExist(err) {
		t.Fatalf("optional entry unexpectedly materialised (stat err: %v)", err)
	}
}
