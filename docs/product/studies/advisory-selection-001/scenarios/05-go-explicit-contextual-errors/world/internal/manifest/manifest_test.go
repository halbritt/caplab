package manifest_test

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/meridian-ops/depotsync/internal/manifest"
)

func writeManifest(t *testing.T, body string) string {
	t.Helper()
	path := filepath.Join(t.TempDir(), "depot.json")
	if err := os.WriteFile(path, []byte(body), 0o644); err != nil {
		t.Fatal(err)
	}
	return path
}

func TestLoadValidManifest(t *testing.T) {
	m, err := manifest.Load(writeManifest(t, `{
		"entries": [
			{"name": "release/app.bin", "key": "blobs/aa11"},
			{"name": "extras/symbols.tar", "key": "blobs/bb22", "optional": true}
		]
	}`))
	if err != nil {
		t.Fatalf("Load: %v", err)
	}
	if len(m.Entries) != 2 {
		t.Fatalf("got %d entries, want 2", len(m.Entries))
	}
	if m.Entries[0].Optional {
		t.Fatal("first entry should not be optional")
	}
	if !m.Entries[1].Optional {
		t.Fatal("optional flag not parsed")
	}
}

func TestLoadRejectsDuplicateNames(t *testing.T) {
	_, err := manifest.Load(writeManifest(t, `{
		"entries": [
			{"name": "release/app.bin", "key": "blobs/aa11"},
			{"name": "release/app.bin", "key": "blobs/bb22"}
		]
	}`))
	if err == nil {
		t.Fatal("want error for duplicate entry names")
	}
}

func TestLoadRejectsEscapingNames(t *testing.T) {
	_, err := manifest.Load(writeManifest(t, `{
		"entries": [
			{"name": "../outside.bin", "key": "blobs/aa11"}
		]
	}`))
	if err == nil {
		t.Fatal("want error for a name escaping the destination")
	}
}
