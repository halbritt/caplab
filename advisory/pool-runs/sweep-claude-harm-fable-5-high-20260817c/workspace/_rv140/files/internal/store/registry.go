package store

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"slices"
)

type workstationRegistry struct {
	Graphs []registryEntry `json:"graphs"`
}

type registryEntry struct {
	RepoID           string              `json:"repo_id"`
	Path             string              `json:"path"`
	Alias            string              `json:"alias,omitempty"`
	GraphStorePath   string              `json:"graph_store_path"`
	SeenWorkingTrees []string            `json:"seen_working_trees"`
	Resolution       *registryResolution `json:"resolution,omitempty"`
}

// registryResolution is a registered repository's standing resolution
// declaration (fleet-catalog-resolution@2, checks-resolve-to-repo@2):
// repository policy the driver reads, never compiler semantics.
// instance_catalog_overlay names the single overlay root whose target-states
// the driver layers over the product catalog when an invocation passes no
// explicit -catalog-overlay. check_registry names the check-registry file
// the driver gates a session on when an invocation passes no explicit
// -checks; it is pointer-shaped because absent and present-empty are
// distinct states — a nil pointer round-trips to an absent key (a registry
// that never declares saves byte-identically to the pre-declaration shape),
// while a non-nil pointer to "" emits "check_registry": "", a declaration,
// refused at the point of use like every other unusable declared value. Any
// future writer must preserve the pointer shape and never collapse
// present-empty into absent; a future third sibling needing the
// absent-vs-present-empty distinction must copy CheckRegistry's
// (value, declared, err) lookup shape, not the overlay's string-only one.
type registryResolution struct {
	InstanceCatalogOverlay string  `json:"instance_catalog_overlay,omitempty"`
	CheckRegistry          *string `json:"check_registry,omitempty"`
}

func upsertRegistryEntry(graph *Graph, alias, repoRoot string) error {
	registry, err := loadRegistry(graph.RegistryPath)
	if err != nil {
		return err
	}
	for i := range registry.Graphs {
		if registry.Graphs[i].RepoID == graph.RepoID {
			registry.Graphs[i].Path = repoRoot
			registry.Graphs[i].GraphStorePath = graph.GraphDir
			if alias != "" {
				registry.Graphs[i].Alias = alias
			}
			if !slices.Contains(registry.Graphs[i].SeenWorkingTrees, repoRoot) {
				registry.Graphs[i].SeenWorkingTrees = append(registry.Graphs[i].SeenWorkingTrees, repoRoot)
			}
			return saveRegistry(graph.RegistryPath, registry)
		}
	}
	registry.Graphs = append(registry.Graphs, registryEntry{
		RepoID:           graph.RepoID,
		Path:             repoRoot,
		Alias:            alias,
		GraphStorePath:   graph.GraphDir,
		SeenWorkingTrees: []string{repoRoot},
	})
	return saveRegistry(graph.RegistryPath, registry)
}

func recordSeenWorkingTree(graph *Graph, repoRoot string) ([]Notice, error) {
	registry, err := loadRegistry(graph.RegistryPath)
	if err != nil {
		return nil, err
	}
	for i := range registry.Graphs {
		if registry.Graphs[i].RepoID != graph.RepoID {
			continue
		}
		if slices.Contains(registry.Graphs[i].SeenWorkingTrees, repoRoot) {
			return nil, nil
		}
		registry.Graphs[i].SeenWorkingTrees = append(registry.Graphs[i].SeenWorkingTrees, repoRoot)
		if err := saveRegistry(graph.RegistryPath, registry); err != nil {
			return nil, err
		}
		return []Notice{{
			Code:   NoticeMultiWorkingTree,
			Detail: repoRoot,
		}}, nil
	}
	registry.Graphs = append(registry.Graphs, registryEntry{
		RepoID:           graph.RepoID,
		Path:             repoRoot,
		GraphStorePath:   graph.GraphDir,
		SeenWorkingTrees: []string{repoRoot},
	})
	return nil, saveRegistry(graph.RegistryPath, registry)
}

func loadRegistry(path string) (workstationRegistry, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) {
			return workstationRegistry{}, nil
		}
		return workstationRegistry{}, err
	}
	var registry workstationRegistry
	if err := json.Unmarshal(raw, &registry); err != nil {
		return workstationRegistry{}, err
	}
	return registry, nil
}

// RegisteredGraph is one entry the workstation registry resolves: a repository
// id and the Graph Store it resolves to. The registry is the sole cross-graph
// resolver for cross-repository compilation (D0014): a foreign accepted head is
// read through it at planning to admit a Foreign Head Attestation, never on the
// gate/admission path (D0010.C11).
type RegisteredGraph struct {
	RepoID         string
	Path           string
	GraphStorePath string
}

// RegisteredGraphs returns the graphs registered under a workstation data home,
// in registry order. The empty slice (no registry, or none registered) is not
// an error — a workstation with one graph is a fleet of one.
func RegisteredGraphs(dataHome string) ([]RegisteredGraph, error) {
	root, err := dataRoot(dataHome)
	if err != nil {
		return nil, err
	}
	registry, err := loadRegistry(filepath.Join(root, "registry.json"))
	if err != nil {
		return nil, err
	}
	out := make([]RegisteredGraph, 0, len(registry.Graphs))
	for _, entry := range registry.Graphs {
		out = append(out, RegisteredGraph{
			RepoID:         entry.RepoID,
			Path:           entry.Path,
			GraphStorePath: entry.GraphStorePath,
		})
	}
	return out, nil
}

// InstanceCatalogOverlay returns the instance catalog overlay root a
// registered repository declares (graphs[].resolution.instance_catalog_overlay),
// verbatim — empty when the registry, the entry, or the declaration is absent.
// Error semantics are the standing loadRegistry contract, no new tolerance: a
// missing registry file is silent (a fleet of one, exactly as RegisteredGraphs
// treats it); an unreadable or malformed registry file is the caller's error,
// named with the registry path. The lookup validates nothing about the
// returned path — validation belongs to the resolution point about to use it.
func InstanceCatalogOverlay(dataHome, repoID string) (string, error) {
	root, err := dataRoot(dataHome)
	if err != nil {
		return "", err
	}
	path := filepath.Join(root, "registry.json")
	registry, err := loadRegistry(path)
	if err != nil {
		return "", fmt.Errorf("store: registry %s: %w", path, err)
	}
	for _, entry := range registry.Graphs {
		if entry.RepoID == repoID && entry.Resolution != nil {
			return entry.Resolution.InstanceCatalogOverlay, nil
		}
	}
	return "", nil
}

// CheckRegistry returns the check-registry path a registered repository
// declares (graphs[].resolution.check_registry), verbatim, with declared
// reporting whether the key is present at all — presence regardless of
// value, so a present-empty declaration returns ("", true, nil), distinct
// from every absent case's ("", false, nil): no matching entry, no
// resolution object, no check_registry key, and a missing registry file are
// all silent (a fleet of one, exactly as RegisteredGraphs treats it). Error
// semantics are the standing loadRegistry contract, no new tolerance: an
// unreadable or malformed registry file is the caller's error, named with
// the registry path. The lookup validates nothing about the returned path —
// validation belongs to the resolution point about to use it. The value is
// copied out, so callers never hold registry-owned memory.
func CheckRegistry(dataHome, repoID string) (path string, declared bool, err error) {
	root, err := dataRoot(dataHome)
	if err != nil {
		return "", false, err
	}
	registryPath := filepath.Join(root, "registry.json")
	registry, err := loadRegistry(registryPath)
	if err != nil {
		return "", false, fmt.Errorf("store: registry %s: %w", registryPath, err)
	}
	for _, entry := range registry.Graphs {
		if entry.RepoID == repoID && entry.Resolution != nil && entry.Resolution.CheckRegistry != nil {
			return *entry.Resolution.CheckRegistry, true, nil
		}
	}
	return "", false, nil
}

// RegisteredRepoIDs returns the repo_ids registered under a workstation data
// home, in registry order.
func RegisteredRepoIDs(dataHome string) []string {
	graphs, err := RegisteredGraphs(dataHome)
	if err != nil {
		return nil
	}
	ids := make([]string, 0, len(graphs))
	for _, graph := range graphs {
		ids = append(ids, graph.RepoID)
	}
	return ids
}

func saveRegistry(path string, registry workstationRegistry) error {
	raw, err := json.MarshalIndent(registry, "", "  ")
	if err != nil {
		return err
	}
	raw = append(raw, '\n')
	return os.WriteFile(path, raw, 0o600)
}
