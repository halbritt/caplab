package store

import (
	"os"
	"path/filepath"
	"slices"
	"strings"
	"testing"
)

// TestRegistryResolutionRoundTrip pins old-registry compatibility
// (fleet-catalog-resolution@2, C3): a registry written before the resolution
// declaration existed decodes unchanged, and saving it back without a
// declaration emits no resolution key — a repository that never declares one
// is byte-invisible to the new field. A declared overlay round-trips verbatim.
func TestRegistryResolutionRoundTrip(t *testing.T) {
	path := filepath.Join(t.TempDir(), "registry.json")
	baseline := `{
  "graphs": [
    {
      "repo_id": "01912345-0000-7000-8000-0000000000d1",
      "path": "/home/example/repo",
      "graph_store_path": "/home/example/.local/share/striatum/graphs/x",
      "seen_working_trees": [
        "/home/example/repo"
      ]
    }
  ]
}
`
	if err := os.WriteFile(path, []byte(baseline), 0o600); err != nil {
		t.Fatalf("write baseline registry: %v", err)
	}

	registry, err := loadRegistry(path)
	if err != nil {
		t.Fatalf("loadRegistry(baseline) error = %v", err)
	}
	if len(registry.Graphs) != 1 {
		t.Fatalf("baseline graphs = %d, want 1", len(registry.Graphs))
	}
	entry := registry.Graphs[0]
	if entry.RepoID != "01912345-0000-7000-8000-0000000000d1" || entry.Path != "/home/example/repo" {
		t.Fatalf("baseline entry decoded wrong: %+v", entry)
	}
	if entry.Resolution != nil {
		t.Fatalf("baseline entry grew a resolution declaration: %+v", entry.Resolution)
	}

	if err := saveRegistry(path, registry); err != nil {
		t.Fatalf("saveRegistry(no declaration) error = %v", err)
	}
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read saved registry: %v", err)
	}
	if strings.Contains(string(raw), "resolution") {
		t.Fatalf("saving an undeclared registry emitted a resolution key:\n%s", raw)
	}

	registry.Graphs[0].Resolution = &registryResolution{InstanceCatalogOverlay: "/srv/instance/catalog"}
	if err := saveRegistry(path, registry); err != nil {
		t.Fatalf("saveRegistry(declared) error = %v", err)
	}
	reloaded, err := loadRegistry(path)
	if err != nil {
		t.Fatalf("loadRegistry(declared) error = %v", err)
	}
	if reloaded.Graphs[0].Resolution == nil ||
		reloaded.Graphs[0].Resolution.InstanceCatalogOverlay != "/srv/instance/catalog" {
		t.Fatalf("declared overlay did not round-trip: %+v", reloaded.Graphs[0].Resolution)
	}
}

// TestRegistryResolutionSurvivesRewrites pins preservation: registration
// updates from init/open (upsertRegistryEntry, recordSeenWorkingTree) rewrite
// the registry but must never strip a standing declaration.
func TestRegistryResolutionSurvivesRewrites(t *testing.T) {
	path := filepath.Join(t.TempDir(), "registry.json")
	const repoID = "01912345-0000-7000-8000-0000000000d2"
	repoRoot := t.TempDir()
	graph := &Graph{RepoID: repoID, GraphDir: "/home/example/graphs/" + repoID, RegistryPath: path}

	declaredChecks := "/srv/instance/checks/repository.json"
	seed := workstationRegistry{Graphs: []registryEntry{{
		RepoID:           repoID,
		Path:             repoRoot,
		GraphStorePath:   graph.GraphDir,
		SeenWorkingTrees: []string{repoRoot},
		Resolution: &registryResolution{
			InstanceCatalogOverlay: "/srv/instance/catalog",
			CheckRegistry:          &declaredChecks,
		},
	}}}
	if err := saveRegistry(path, seed); err != nil {
		t.Fatalf("seed registry: %v", err)
	}

	if err := upsertRegistryEntry(graph, "alias-after", repoRoot); err != nil {
		t.Fatalf("upsertRegistryEntry() error = %v", err)
	}
	afterUpsert, err := loadRegistry(path)
	if err != nil {
		t.Fatalf("loadRegistry after upsert: %v", err)
	}
	if afterUpsert.Graphs[0].Resolution == nil ||
		afterUpsert.Graphs[0].Resolution.InstanceCatalogOverlay != "/srv/instance/catalog" {
		t.Fatalf("upsertRegistryEntry stripped the declaration: %+v", afterUpsert.Graphs[0].Resolution)
	}
	if afterUpsert.Graphs[0].Resolution.CheckRegistry == nil ||
		*afterUpsert.Graphs[0].Resolution.CheckRegistry != declaredChecks {
		t.Fatalf("upsertRegistryEntry stripped the check_registry declaration: %+v", afterUpsert.Graphs[0].Resolution)
	}
	if afterUpsert.Graphs[0].Alias != "alias-after" {
		t.Fatalf("upsertRegistryEntry did not apply the alias: %+v", afterUpsert.Graphs[0])
	}

	otherTree := t.TempDir()
	if _, err := recordSeenWorkingTree(graph, otherTree); err != nil {
		t.Fatalf("recordSeenWorkingTree() error = %v", err)
	}
	afterSeen, err := loadRegistry(path)
	if err != nil {
		t.Fatalf("loadRegistry after seen-tree: %v", err)
	}
	if afterSeen.Graphs[0].Resolution == nil ||
		afterSeen.Graphs[0].Resolution.InstanceCatalogOverlay != "/srv/instance/catalog" {
		t.Fatalf("recordSeenWorkingTree stripped the declaration: %+v", afterSeen.Graphs[0].Resolution)
	}
	if afterSeen.Graphs[0].Resolution.CheckRegistry == nil ||
		*afterSeen.Graphs[0].Resolution.CheckRegistry != declaredChecks {
		t.Fatalf("recordSeenWorkingTree stripped the check_registry declaration: %+v", afterSeen.Graphs[0].Resolution)
	}
	if !slices.Contains(afterSeen.Graphs[0].SeenWorkingTrees, otherTree) {
		t.Fatalf("seen working tree %s not recorded: %v", otherTree, afterSeen.Graphs[0].SeenWorkingTrees)
	}
}

// TestCheckRegistryRoundTripByteIdentity pins the undeclared cases as saved
// bytes, never decoded structures (checks-resolve-to-repo@2, C1): a registry
// with no resolution key, and one whose resolution declares only the
// overlay, each load and re-save byte-equal to a fixture authored in
// saveRegistry's exact byte shape — the new field is byte-invisible until
// declared, and a registry written before it existed decodes unchanged.
func TestCheckRegistryRoundTripByteIdentity(t *testing.T) {
	fixtures := []struct {
		name, body string
	}{
		{
			name: "no resolution key",
			body: `{
  "graphs": [
    {
      "repo_id": "01912345-0000-7000-8000-0000000000d5",
      "path": "/home/example/repo",
      "graph_store_path": "/home/example/.local/share/striatum/graphs/x",
      "seen_working_trees": [
        "/home/example/repo"
      ]
    }
  ]
}
`,
		},
		{
			name: "overlay-only resolution",
			body: `{
  "graphs": [
    {
      "repo_id": "01912345-0000-7000-8000-0000000000d6",
      "path": "/home/example/repo",
      "graph_store_path": "/home/example/.local/share/striatum/graphs/x",
      "seen_working_trees": [
        "/home/example/repo"
      ],
      "resolution": {
        "instance_catalog_overlay": "/srv/instance/catalog"
      }
    }
  ]
}
`,
		},
	}
	for _, tc := range fixtures {
		t.Run(tc.name, func(t *testing.T) {
			path := filepath.Join(t.TempDir(), "registry.json")
			if err := os.WriteFile(path, []byte(tc.body), 0o600); err != nil {
				t.Fatalf("write fixture registry: %v", err)
			}
			registry, err := loadRegistry(path)
			if err != nil {
				t.Fatalf("loadRegistry() error = %v", err)
			}
			if len(registry.Graphs) != 1 {
				t.Fatalf("fixture graphs = %d, want 1", len(registry.Graphs))
			}
			if resolution := registry.Graphs[0].Resolution; resolution != nil && resolution.CheckRegistry != nil {
				t.Fatalf("undeclared fixture decoded a check_registry: %+v", resolution)
			}
			if err := saveRegistry(path, registry); err != nil {
				t.Fatalf("saveRegistry() error = %v", err)
			}
			saved, err := os.ReadFile(path)
			if err != nil {
				t.Fatalf("read saved registry: %v", err)
			}
			if string(saved) != tc.body {
				t.Fatalf("undeclared registry did not round-trip byte-identically:\nsaved:\n%s\nfixture:\n%s", saved, tc.body)
			}
		})
	}
}

// TestCheckRegistryAbsentVsPresentEmpty pins the pointer shape
// (checks-resolve-to-repo@2, C1): a nil CheckRegistry saves with no
// check_registry key, a pointer to the empty string saves the key with an
// empty value and reloads as a non-nil pointer — the two states never
// collapse through a save/load cycle. A declared non-empty value
// round-trips verbatim.
func TestCheckRegistryAbsentVsPresentEmpty(t *testing.T) {
	path := filepath.Join(t.TempDir(), "registry.json")
	entry := registryEntry{
		RepoID:           "01912345-0000-7000-8000-0000000000d7",
		Path:             "/home/example/repo",
		GraphStorePath:   "/home/example/graphs/x",
		SeenWorkingTrees: []string{"/home/example/repo"},
		Resolution:       &registryResolution{InstanceCatalogOverlay: "/srv/instance/catalog"},
	}

	// Absent: nil pointer, no key on disk, nil after reload.
	if err := saveRegistry(path, workstationRegistry{Graphs: []registryEntry{entry}}); err != nil {
		t.Fatalf("saveRegistry(absent) error = %v", err)
	}
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read saved registry: %v", err)
	}
	if strings.Contains(string(raw), "check_registry") {
		t.Fatalf("nil CheckRegistry emitted a check_registry key:\n%s", raw)
	}
	reloaded, err := loadRegistry(path)
	if err != nil {
		t.Fatalf("loadRegistry(absent) error = %v", err)
	}
	if reloaded.Graphs[0].Resolution.CheckRegistry != nil {
		t.Fatalf("absent check_registry reloaded non-nil: %+v", reloaded.Graphs[0].Resolution)
	}

	// Present-empty: pointer to "", key on disk with an empty value,
	// non-nil pointer to "" after reload.
	empty := ""
	entry.Resolution = &registryResolution{
		InstanceCatalogOverlay: "/srv/instance/catalog",
		CheckRegistry:          &empty,
	}
	if err := saveRegistry(path, workstationRegistry{Graphs: []registryEntry{entry}}); err != nil {
		t.Fatalf("saveRegistry(present-empty) error = %v", err)
	}
	raw, err = os.ReadFile(path)
	if err != nil {
		t.Fatalf("read saved registry: %v", err)
	}
	if !strings.Contains(string(raw), `"check_registry": ""`) {
		t.Fatalf("present-empty check_registry did not save its key:\n%s", raw)
	}
	reloaded, err = loadRegistry(path)
	if err != nil {
		t.Fatalf("loadRegistry(present-empty) error = %v", err)
	}
	if got := reloaded.Graphs[0].Resolution.CheckRegistry; got == nil || *got != "" {
		t.Fatalf("present-empty check_registry did not reload as a non-nil empty pointer: %+v", got)
	}

	// Declared non-empty: verbatim round-trip.
	declared := "/srv/instance/checks/repository.json"
	entry.Resolution.CheckRegistry = &declared
	if err := saveRegistry(path, workstationRegistry{Graphs: []registryEntry{entry}}); err != nil {
		t.Fatalf("saveRegistry(declared) error = %v", err)
	}
	reloaded, err = loadRegistry(path)
	if err != nil {
		t.Fatalf("loadRegistry(declared) error = %v", err)
	}
	if got := reloaded.Graphs[0].Resolution.CheckRegistry; got == nil || *got != declared {
		t.Fatalf("declared check_registry did not round-trip verbatim: %+v", got)
	}
}

// TestCheckRegistryLookup mirrors TestInstanceCatalogOverlayLookup for the
// CheckRegistry lookup (checks-resolve-to-repo@2, C2): declared reports key
// presence regardless of value, every absent case is silent (a fleet of
// one), and error semantics are the standing loadRegistry contract — a
// malformed registry file is the caller's error naming the registry path.
// The lookup validates nothing about the returned path.
func TestCheckRegistryLookup(t *testing.T) {
	dataHome := t.TempDir()
	registryPath := filepath.Join(dataHome, "striatum", "registry.json")
	if err := os.MkdirAll(filepath.Dir(registryPath), 0o700); err != nil {
		t.Fatalf("mkdir data root: %v", err)
	}
	const declared = "01912345-0000-7000-8000-0000000000d8"
	const declaredEmpty = "01912345-0000-7000-8000-0000000000d9"
	const keyless = "01912345-0000-7000-8000-0000000000da"
	const undeclared = "01912345-0000-7000-8000-0000000000db"
	declaredPath := "/srv/instance/checks/repository.json"
	empty := ""
	registry := workstationRegistry{Graphs: []registryEntry{
		{
			RepoID:           declared,
			Path:             "/home/example/fleet",
			GraphStorePath:   "/home/example/graphs/" + declared,
			SeenWorkingTrees: []string{"/home/example/fleet"},
			Resolution:       &registryResolution{CheckRegistry: &declaredPath},
		},
		{
			RepoID:           declaredEmpty,
			Path:             "/home/example/fleet-empty",
			GraphStorePath:   "/home/example/graphs/" + declaredEmpty,
			SeenWorkingTrees: []string{"/home/example/fleet-empty"},
			Resolution:       &registryResolution{CheckRegistry: &empty},
		},
		{
			RepoID:           keyless,
			Path:             "/home/example/overlay-only",
			GraphStorePath:   "/home/example/graphs/" + keyless,
			SeenWorkingTrees: []string{"/home/example/overlay-only"},
			Resolution:       &registryResolution{InstanceCatalogOverlay: "/srv/instance/catalog"},
		},
		{
			RepoID:           undeclared,
			Path:             "/home/example/plain",
			GraphStorePath:   "/home/example/graphs/" + undeclared,
			SeenWorkingTrees: []string{"/home/example/plain"},
		},
	}}
	if err := saveRegistry(registryPath, registry); err != nil {
		t.Fatalf("save fixture registry: %v", err)
	}

	cases := []struct {
		name, repoID string
		wantPath     string
		wantDeclared bool
	}{
		{"declared non-empty", declared, declaredPath, true},
		{"declared empty is presence regardless of value", declaredEmpty, "", true},
		{"resolution present without the key", keyless, "", false},
		{"no resolution object", undeclared, "", false},
		{"unregistered repo", "01912345-0000-7000-8000-00000000ffff", "", false},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got, gotDeclared, err := CheckRegistry(dataHome, tc.repoID)
			if err != nil {
				t.Fatalf("CheckRegistry() error = %v", err)
			}
			if got != tc.wantPath || gotDeclared != tc.wantDeclared {
				t.Fatalf("CheckRegistry() = (%q, %v), want (%q, %v)", got, gotDeclared, tc.wantPath, tc.wantDeclared)
			}
		})
	}

	// A missing registry file is silent — a fleet of one.
	got, gotDeclared, err := CheckRegistry(t.TempDir(), declared)
	if err != nil || got != "" || gotDeclared {
		t.Fatalf("CheckRegistry(no registry) = (%q, %v, %v), want empty, false, nil", got, gotDeclared, err)
	}

	// A malformed registry file is the caller's error, naming the path.
	if err := os.WriteFile(registryPath, []byte("{not json"), 0o600); err != nil {
		t.Fatalf("write malformed registry: %v", err)
	}
	if _, _, err := CheckRegistry(dataHome, declared); err == nil {
		t.Fatal("CheckRegistry(malformed) error = nil, want the decode error")
	} else if !strings.Contains(err.Error(), registryPath) {
		t.Fatalf("malformed-registry error does not name the registry path: %v", err)
	}
}

// TestInstanceCatalogOverlayLookup pins the exported lookup and its error
// semantics — the standing loadRegistry contract, no new tolerance: declared
// string verbatim for the matching repo_id, empty for entries declaring
// nothing and for absent entries, missing registry file silent, malformed
// registry file an error naming the registry path.
func TestInstanceCatalogOverlayLookup(t *testing.T) {
	dataHome := t.TempDir()
	registryPath := filepath.Join(dataHome, "striatum", "registry.json")
	if err := os.MkdirAll(filepath.Dir(registryPath), 0o700); err != nil {
		t.Fatalf("mkdir data root: %v", err)
	}
	const declared = "01912345-0000-7000-8000-0000000000d3"
	const undeclared = "01912345-0000-7000-8000-0000000000d4"
	registry := workstationRegistry{Graphs: []registryEntry{
		{
			RepoID:           declared,
			Path:             "/home/example/fleet",
			GraphStorePath:   "/home/example/graphs/" + declared,
			SeenWorkingTrees: []string{"/home/example/fleet"},
			Resolution:       &registryResolution{InstanceCatalogOverlay: "/srv/instance/catalog"},
		},
		{
			RepoID:           undeclared,
			Path:             "/home/example/plain",
			GraphStorePath:   "/home/example/graphs/" + undeclared,
			SeenWorkingTrees: []string{"/home/example/plain"},
		},
	}}
	if err := saveRegistry(registryPath, registry); err != nil {
		t.Fatalf("save fixture registry: %v", err)
	}

	got, err := InstanceCatalogOverlay(dataHome, declared)
	if err != nil {
		t.Fatalf("InstanceCatalogOverlay(declared) error = %v", err)
	}
	if got != "/srv/instance/catalog" {
		t.Fatalf("InstanceCatalogOverlay(declared) = %q, want /srv/instance/catalog", got)
	}

	got, err = InstanceCatalogOverlay(dataHome, undeclared)
	if err != nil || got != "" {
		t.Fatalf("InstanceCatalogOverlay(undeclared) = %q, %v, want empty and nil", got, err)
	}

	got, err = InstanceCatalogOverlay(dataHome, "01912345-0000-7000-8000-00000000ffff")
	if err != nil || got != "" {
		t.Fatalf("InstanceCatalogOverlay(unregistered) = %q, %v, want empty and nil", got, err)
	}

	// A missing registry file is silent — a fleet of one.
	got, err = InstanceCatalogOverlay(t.TempDir(), declared)
	if err != nil || got != "" {
		t.Fatalf("InstanceCatalogOverlay(no registry) = %q, %v, want empty and nil", got, err)
	}

	// A malformed registry file is the caller's error, naming the path.
	if err := os.WriteFile(registryPath, []byte("{not json"), 0o600); err != nil {
		t.Fatalf("write malformed registry: %v", err)
	}
	if _, err := InstanceCatalogOverlay(dataHome, declared); err == nil {
		t.Fatal("InstanceCatalogOverlay(malformed) error = nil, want the decode error")
	} else if !strings.Contains(err.Error(), registryPath) {
		t.Fatalf("malformed-registry error does not name the registry path: %v", err)
	}
}
