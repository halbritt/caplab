package cli

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/halbritt/striatum-next/internal/backend/local"
	"github.com/halbritt/striatum-next/internal/records"
	"github.com/halbritt/striatum-next/internal/store"
)

// Standing guards for checks-resolve-to-repo@2: registration-derived
// check-registry resolution at the CLI seam. Resolution happens once per
// invocation, inside buildSession — after OpenGraph names the repository,
// before the adapters snapshot wake argv and before the registry loads —
// and the effective decision threads through the returned Config for
// verbatim consumption. These guards observe exactly that seam
// (resolveEffectiveChecks, buildSession, and the wakeCommand/timer argv
// derivation), beside their overlay siblings in overlay_resolution_test.go.
// The @1 path-resolution rule keeps its own guard in checks_resolve_test.go,
// untouched.

// checksSessionConfig extends the shared resolution fixture with what
// buildSession needs beyond openGraphAndCatalog: a backends directory
// carrying the minimal accepted local declaration, and an absent policy
// file (a tolerated default).
func checksSessionConfig(t *testing.T, repoID string) Config {
	t.Helper()
	config := newResolutionFixture(t, repoID)
	config.BackendsDir = t.TempDir()
	declaration := filepath.Join(config.BackendsDir, "local", "backend.yaml")
	if err := os.MkdirAll(filepath.Dir(declaration), 0o755); err != nil {
		t.Fatalf("mkdir backends: %v", err)
	}
	if err := os.WriteFile(declaration, []byte(`schema_version: 1
id: local
kind: execution-backend
declaration_version: 1
status: accepted
aliasing:
  aliasing_class: deterministic
capabilities:
  effects: [E0, E1]
  supported_pass_types: [intent-capture, observation, review]
`), 0o644); err != nil {
		t.Fatalf("write backend declaration: %v", err)
	}
	config.PolicyPath = filepath.Join(t.TempDir(), "absent-driver.yaml")
	return config
}

// declareCheckRegistry is the v1 authoring path, the declareInstanceOverlay
// sibling: a direct edit of the workstation registry writing
// resolution.check_registry — no CLI verb writes the declaration yet.
// Existing resolution keys are preserved.
func declareCheckRegistry(t *testing.T, dataHome, repoID, checkRegistry string) {
	t.Helper()
	path := filepath.Join(dataHome, "striatum", "registry.json")
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read registry: %v", err)
	}
	var registry map[string]any
	if err := json.Unmarshal(raw, &registry); err != nil {
		t.Fatalf("decode registry: %v", err)
	}
	declared := false
	graphs, _ := registry["graphs"].([]any)
	for _, item := range graphs {
		entry, _ := item.(map[string]any)
		if entry["repo_id"] == repoID {
			resolution, _ := entry["resolution"].(map[string]any)
			if resolution == nil {
				resolution = map[string]any{}
			}
			resolution["check_registry"] = checkRegistry
			entry["resolution"] = resolution
			declared = true
		}
	}
	if !declared {
		t.Fatalf("repo %s not registered in %s", repoID, path)
	}
	out, err := json.MarshalIndent(registry, "", "  ")
	if err != nil {
		t.Fatalf("encode registry: %v", err)
	}
	if err := os.WriteFile(path, append(out, '\n'), 0o600); err != nil {
		t.Fatalf("write registry: %v", err)
	}
}

// writeCheckRegistryFile authors a minimal valid check registry (any JSON
// driver.LoadCheckWorld accepts) at an absolute path and returns the path
// and its exact bytes, so a load can be attributed to this file by content.
func writeCheckRegistryFile(t *testing.T) (string, []byte) {
	t.Helper()
	body := []byte(`{"schema_version": 1, "registry_version": 1, "checks": [], "sets": {}}` + "\n")
	path := filepath.Join(t.TempDir(), "declared-checks.json")
	if err := os.WriteFile(path, body, 0o644); err != nil {
		t.Fatalf("write check registry fixture: %v", err)
	}
	return path, body
}

// corruptWorkstationRegistry makes any registry lookup error, so a branch
// that succeeds over it provably never consulted registration.
func corruptWorkstationRegistry(t *testing.T, dataHome string) {
	t.Helper()
	path := filepath.Join(dataHome, "striatum", "registry.json")
	if err := os.WriteFile(path, []byte("{not json"), 0o600); err != nil {
		t.Fatalf("corrupt registry: %v", err)
	}
}

// Guard 1 — auto-resolution (C4.2): a registered repository declaring a
// valid absolute check-registry file resolves it with no flag passed, and a
// session built through buildSession loads its Checks from exactly the
// declared file — while the @1 default path stays absent in the fixture
// repository, so the load is attributable to the declaration alone.
func TestChecksAutoResolveFromRegistration(t *testing.T) {
	const repoID = "01912345-0000-7000-8000-0000000000c1"
	config := checksSessionConfig(t, repoID)
	config.ChecksPath = "policy/checks/repository.json" // the flag default, not explicit
	declared, declaredBody := writeCheckRegistryFile(t)
	declareCheckRegistry(t, config.DataHome, repoID, declared)

	effective, err := resolveEffectiveChecks(config, repoID)
	if err != nil {
		t.Fatalf("resolveEffectiveChecks() error = %v", err)
	}
	if effective != declared {
		t.Fatalf("resolveEffectiveChecks() = %q, want the declared path %q", effective, declared)
	}

	session, resolved, err := buildSession(config)
	if err != nil {
		t.Fatalf("buildSession() error = %v", err)
	}
	if resolved.ChecksPath != declared {
		t.Fatalf("resolved config carries ChecksPath %q, want the declared path %q", resolved.ChecksPath, declared)
	}
	if session.Checks == nil {
		t.Fatal("session Checks = nil, want the declared registry loaded")
	}
	if string(session.Checks.Raw) != string(declaredBody) {
		t.Fatalf("session Checks loaded other bytes than the declared file:\n%s", session.Checks.Raw)
	}
}

// Guard 2 — precedence (C4.1 on C3's parse-time fact): with a declaration
// present, an explicit -checks of a distinct path, the default string, and
// the empty string each resolve to the flag's @1 resolution, never the
// declaration. Never-consulted is proven sharply: the explicit branch
// succeeds over a malformed workstation registry, which errors any lookup.
func TestExplicitChecksFlagOverridesRegistration(t *testing.T) {
	const repoID = "01912345-0000-7000-8000-0000000000c2"
	config := checksSessionConfig(t, repoID)
	declared, _ := writeCheckRegistryFile(t)
	declareCheckRegistry(t, config.DataHome, repoID, declared)
	corruptWorkstationRegistry(t, config.DataHome)

	cases := []struct {
		name, checks string
	}{
		{"distinct explicit path", filepath.Join(t.TempDir(), "explicit-checks.json")},
		{"the default string is explicit too", "policy/checks/repository.json"},
		{"the empty string is explicit too", ""},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			explicit := config
			explicit.ChecksPath = tc.checks
			explicit.ChecksExplicit = true
			effective, err := resolveEffectiveChecks(explicit, repoID)
			if err != nil {
				t.Fatalf("explicit branch consulted registration (malformed registry errored): %v", err)
			}
			if want := explicit.resolvedChecksPath(); effective != want {
				t.Fatalf("resolveEffectiveChecks() = %q, want the @1 resolution %q", effective, want)
			}
			if effective == declared {
				t.Fatalf("explicit flag resolved to the declaration %q: override must not blend", declared)
			}
		})
	}
}

// Guard 2, Main-level — the flag.Visit plumbing is covered end-to-end, not
// only the field: on a fixture whose declaration is broken (a relative
// path), a Main invocation without -checks refuses, and the same invocation
// with an explicit -checks succeeds because registration is never consulted
// under the explicit flag.
func TestMainSetsChecksExplicitness(t *testing.T) {
	const repoID = "01912345-0000-7000-8000-0000000000c3"
	config := checksSessionConfig(t, repoID)
	declareCheckRegistry(t, config.DataHome, repoID, "relative/checks.json")

	base := []string{
		"-repo", config.Repo,
		"-data-home", config.DataHome,
		"-catalog", config.CatalogDir,
		"-backends", config.BackendsDir,
		"-policy", config.PolicyPath,
	}
	if code := Main(append(base, "status")); code != ExitRefusal {
		t.Fatalf("Main(status) without -checks over a broken declaration exit = %d, want %d", code, ExitRefusal)
	}
	withFlag := append(base, "-checks", filepath.Join(t.TempDir(), "explicit.json"), "status")
	if code := Main(withFlag); code != ExitOK {
		t.Fatalf("Main(status) with explicit -checks exit = %d, want %d (registration must not be consulted)", code, ExitOK)
	}
}

// Guard 3 — silence (C4.3): a registered repository declaring nothing
// resolves exactly the @1 rule's path for its config — self-drive unchanged,
// byte-identically — and with an empty ChecksPath the session builds with
// nil Checks exactly as at baseline.
func TestNoChecksDeclarationKeepsV1Resolution(t *testing.T) {
	const repoID = "01912345-0000-7000-8000-0000000000c4"
	config := checksSessionConfig(t, repoID)

	for _, checks := range []string{"policy/checks/repository.json", "", "/etc/striatum/other.json"} {
		undeclared := config
		undeclared.ChecksPath = checks
		effective, err := resolveEffectiveChecks(undeclared, repoID)
		if err != nil {
			t.Fatalf("resolveEffectiveChecks(%q) error = %v", checks, err)
		}
		if want := undeclared.resolvedChecksPath(); effective != want {
			t.Fatalf("resolveEffectiveChecks(%q) = %q, want the @1 resolution %q", checks, effective, want)
		}
	}

	session, _, err := buildSession(config) // ChecksPath empty, nothing declared
	if err != nil {
		t.Fatalf("buildSession() error = %v", err)
	}
	if session.Checks != nil {
		t.Fatalf("undeclared empty -checks built a CheckWorld: %+v", session.Checks)
	}
}

// Guard 4 — refusal shape and ordering (C6): a declaration about to be used
// must name an absolute, clean path to an existing readable regular file;
// each violation refuses — in resolveEffectiveChecks and through
// buildSession — as a registration-resolution failure naming the repo_id
// and the declared path, before any registry load (the resolution function
// contains no load call by construction, and for these inputs no load is
// even possible). A malformed workstation registry with no explicit flag
// refuses in the same shape, named with its cause.
func TestBrokenChecksDeclarationRefusesBeforeRegistryLoad(t *testing.T) {
	const repoID = "01912345-0000-7000-8000-0000000000c5"

	missing := filepath.Join(t.TempDir(), "gone.json")
	dir := t.TempDir()
	broken := []struct {
		name, declared string
	}{
		{"present-empty", ""},
		{"relative path", "relative/checks.json"},
		{"unclean path", missing + string(filepath.Separator) + "."},
		{"missing file", missing},
		{"directory, not a regular file", dir},
	}
	for _, tc := range broken {
		t.Run(tc.name, func(t *testing.T) {
			config := checksSessionConfig(t, repoID)
			declareCheckRegistry(t, config.DataHome, repoID, tc.declared)

			_, err := resolveEffectiveChecks(config, repoID)
			assertChecksRefusal(t, err, repoID, tc.declared)

			_, _, err = buildSession(config)
			assertChecksRefusal(t, err, repoID, tc.declared)
		})
	}

	t.Run("unreadable file", func(t *testing.T) {
		if os.Geteuid() == 0 {
			t.Skip("root reads through 0o000 modes")
		}
		config := checksSessionConfig(t, repoID)
		unreadable := filepath.Join(t.TempDir(), "unreadable.json")
		if err := os.WriteFile(unreadable, []byte("{}"), 0o000); err != nil {
			t.Fatalf("write unreadable fixture: %v", err)
		}
		declareCheckRegistry(t, config.DataHome, repoID, unreadable)
		_, err := resolveEffectiveChecks(config, repoID)
		assertChecksRefusal(t, err, repoID, unreadable)
	})

	t.Run("malformed workstation registry, no explicit flag", func(t *testing.T) {
		config := checksSessionConfig(t, repoID)
		corruptWorkstationRegistry(t, config.DataHome)
		_, err := resolveEffectiveChecks(config, repoID)
		if err == nil {
			t.Fatal("malformed registry did not refuse the lookup")
		}
		if !strings.Contains(err.Error(), "registration resolution") || !strings.Contains(err.Error(), repoID) {
			t.Fatalf("refusal is not the registration-resolution shape naming the repo_id: %v", err)
		}
		if !strings.Contains(err.Error(), "registry") {
			t.Fatalf("refusal does not carry its lookup cause: %v", err)
		}
	})
}

func assertChecksRefusal(t *testing.T, err error, repoID, declared string) {
	t.Helper()
	if err == nil {
		t.Fatalf("declaration %q did not refuse", declared)
	}
	if !strings.Contains(err.Error(), "registration resolution") {
		t.Fatalf("refusal is not worded as a registration-resolution failure: %v", err)
	}
	if !strings.Contains(err.Error(), repoID) || !strings.Contains(err.Error(), declared) {
		t.Fatalf("refusal does not name the repo_id and the declared path: %v", err)
	}
	if !strings.Contains(err.Error(), "check_registry") {
		t.Fatalf("refusal does not name the declaration field: %v", err)
	}
}

// Guard 5 — tolerance boundary (C7): legal-unmet survives exactly where @1
// owned it — a missing file on the explicit branch (even with a declaration
// standing, which C4.1 never consults) and on the undeclared default — and
// never on a declared path, which Guard 4 pins as a refusal. The boundary
// is the path's source, never its existence.
func TestMissingChecksStayLegalUnmetOffTheDeclaredBranch(t *testing.T) {
	const repoID = "01912345-0000-7000-8000-0000000000c6"

	t.Run("explicit missing file with a declaration standing", func(t *testing.T) {
		config := checksSessionConfig(t, repoID)
		declared, _ := writeCheckRegistryFile(t)
		declareCheckRegistry(t, config.DataHome, repoID, declared)
		config.ChecksPath = filepath.Join(t.TempDir(), "gone.json")
		config.ChecksExplicit = true

		session, _, err := buildSession(config)
		if err != nil {
			t.Fatalf("buildSession() error = %v, want the legal unmet state", err)
		}
		if session.Checks != nil {
			t.Fatalf("explicit missing -checks built a CheckWorld (from the declaration?): %+v", session.Checks)
		}
	})

	t.Run("undeclared missing default", func(t *testing.T) {
		config := checksSessionConfig(t, repoID)
		config.ChecksPath = "policy/checks/repository.json" // absent under the fixture repo

		session, _, err := buildSession(config)
		if err != nil {
			t.Fatalf("buildSession() error = %v, want the legal unmet state", err)
		}
		if session.Checks != nil {
			t.Fatalf("undeclared missing default built a CheckWorld: %+v", session.Checks)
		}
	})
}

// Guard 6 — wake pinning (C8): the wake argv pins the effective checks
// decision on both surfaces, including the empty decision. A non-empty
// decision rides as -checks <absolute resolved path>; an explicit-empty
// decision rides as -checks immediately followed by the empty string —
// present, never omitted — and the rendered wake-timer ExecStart carries it
// as systemd's literal "" so the empty argument survives the join.
func TestWakeArgvPinsChecksDecision(t *testing.T) {
	const repoID = "01912345-0000-7000-8000-0000000000c7"

	t.Run("derived non-empty decision", func(t *testing.T) {
		config := checksSessionConfig(t, repoID)
		config.ChecksPath = "policy/checks/repository.json"
		declared, _ := writeCheckRegistryFile(t)
		declareCheckRegistry(t, config.DataHome, repoID, declared)

		_, resolved, err := buildSession(config)
		if err != nil {
			t.Fatalf("buildSession() error = %v", err)
		}
		argv := wakeCommand(resolved)
		if argv == nil {
			t.Fatal("wakeCommand() = nil, want a wake argv")
		}
		found := false
		for i := 0; i+1 < len(argv); i++ {
			if argv[i] == "-checks" {
				found = true
				if argv[i+1] != declared {
					t.Fatalf("wake -checks = %q, want the declared path %q", argv[i+1], declared)
				}
				if !filepath.IsAbs(argv[i+1]) {
					t.Fatalf("wake -checks path %q is not absolute", argv[i+1])
				}
			}
		}
		if !found {
			t.Fatalf("wake argv lacks the -checks pair: %v", argv)
		}
		service, _ := wakeTimerUnits("striatum-wake-test", append(argv, "-trigger", "timer"), "", time.Minute)
		if !strings.Contains(service, "-checks "+declared) {
			t.Fatalf("armed wake-timer argv lacks the pinned checks decision:\n%s", service)
		}
	})

	t.Run("explicit-empty decision", func(t *testing.T) {
		config := checksSessionConfig(t, repoID)
		config.ChecksPath = ""
		config.ChecksExplicit = true

		_, resolved, err := buildSession(config)
		if err != nil {
			t.Fatalf("buildSession() error = %v", err)
		}
		argv := wakeCommand(resolved)
		if argv == nil {
			t.Fatal("wakeCommand() = nil, want a wake argv")
		}
		found := false
		for i := 0; i+1 < len(argv); i++ {
			if argv[i] == "-checks" {
				found = true
				if argv[i+1] != "" {
					t.Fatalf("wake -checks = %q, want the explicit empty value", argv[i+1])
				}
			}
		}
		if !found {
			t.Fatalf("wake argv omitted -checks for the empty decision: %v", argv)
		}
		service, _ := wakeTimerUnits("striatum-wake-test", append(argv, "-trigger", "timer"), "", time.Minute)
		if !strings.Contains(service, `-checks ""`) {
			t.Fatalf("ExecStart lost the empty -checks argument:\n%s", service)
		}
	})
}

// Guard 7 — the accept/reject boundary (C5/C6 on the acceptance verb): a
// broken check_registry declaration does not refuse accept/reject. The verb
// records the verdict first — recording consults the graph and catalog,
// never the check registry — and the bounded transition's buildSession
// refusal is swallowed by the standing best-effort contract: the verdict
// stands, the bounded drive is skipped (no new drive_session_record), the
// verb exits ExitOK. No weakened drive can occur — the refusal aborts
// buildSession before any registry load — and the loud refusal arrives on
// the next session-constructing invocation (drive/status), in Guard 4's
// shape. This pins the delivered posture; strengthening the loudness is a
// registered deferral (docs/reference/deferrals.md).
func TestAcceptRecordsVerdictAndSkipsBoundedTransitionOnBrokenDeclaration(t *testing.T) {
	const repoID = "01912345-0000-7000-8000-0000000000c8"
	config, graphOf := newAcceptanceFixture(t, repoID)

	step := func(wantCode int, verb string, args ...string) {
		t.Helper()
		code, err := Run(config, verb, args)
		if code != wantCode {
			t.Fatalf("striatum %s %v exit = %d (%v), want %d", verb, args, code, err, wantCode)
		}
	}

	// Build the pending acceptance item with nothing declared: capture the
	// intent, then run the fixture transform to its acceptance block.
	step(ExitOK, "request", "intents/g7", "-target", "fixture-captured", "-note", "Boundary fixture intent.")
	step(ExitOK, "drive")
	step(ExitOK, "request", "intents/g7", "-target", "fixture-noted")
	step(ExitBlocked, "drive")

	// Break the declaration only now, so every prior step ran undeclared.
	brokenDeclared := filepath.Join(t.TempDir(), "gone.json")
	declareCheckRegistry(t, config.DataHome, repoID, brokenDeclared)

	before := readG7Ledger(t, graphOf)
	beforeDrives := countG7Records(before, "drive_session_record")
	beforeVerdicts := countG7AcceptanceResults(before)

	// (i) The verdict is never blocked: accept exits ExitOK with no error.
	code, err := Run(config, "accept", []string{"intents/g7/fixture-note"})
	if code != ExitOK || err != nil {
		t.Fatalf("accept exit = %d (%v), want %d and nil error", code, err, ExitOK)
	}

	after := readG7Ledger(t, graphOf)
	// (ii) The verdict's gate_result is on the ledger.
	if got := countG7AcceptanceResults(after); got != beforeVerdicts+1 {
		t.Fatalf("acceptance gate_result count = %d, want %d", got, beforeVerdicts+1)
	}
	// (iii) The bounded transition was skipped: no new drive session came
	// into being, so no drive — weakened or otherwise — ever ran.
	if got := countG7Records(after, "drive_session_record"); got != beforeDrives {
		t.Fatalf("drive_session_record count = %d, want unchanged %d (the bounded transition must be skipped)", got, beforeDrives)
	}

	// The loud refusal arrives on the next session-constructing invocation.
	for _, verb := range []string{"drive", "status"} {
		code, err := Run(config, verb, nil)
		if code != ExitRefusal {
			t.Fatalf("%s after the broken declaration exit = %d (%v), want %d", verb, code, err, ExitRefusal)
		}
		assertChecksRefusal(t, err, repoID, brokenDeclared)
	}
}

// newAcceptanceFixture builds a Config able to drive the fixture transform
// to its acceptance block: the production catalog merged with the spine
// fixture's catalog extras, the fixture backend declaration, and a runtime
// carrying the deterministic fixture-transform. It returns the config and a
// ledger reader bound to the fixture graph. (The spine harness's helpers
// live in package cli_test; this white-box guard carries its own minimal
// fixture.)
func newAcceptanceFixture(t *testing.T, repoID string) (Config, func(t *testing.T) []records.DecodedRecord) {
	t.Helper()
	devNull, err := os.OpenFile(os.DevNull, os.O_WRONLY, 0)
	if err != nil {
		t.Fatalf("open devnull: %v", err)
	}
	t.Cleanup(func() { devNull.Close() })

	catalogDir := t.TempDir()
	copyG7CatalogTree(t, filepath.Join("..", "..", "catalog"), catalogDir)
	copyG7CatalogTree(t, filepath.Join("..", "..", "testdata", "v0-spine-fixture", "catalog-extra"), catalogDir)

	runtime := local.DefaultRuntime()
	runtime.Register("fixture-transform", func(ctx local.ExecuteContext) (local.ExecuteResult, error) {
		var upstream []byte
		for _, input := range ctx.Manifest.Inputs {
			body, err := os.ReadFile(filepath.Join(ctx.BundleDir, input.Path))
			if err != nil {
				return local.ExecuteResult{}, err
			}
			upstream = append(upstream, body...)
		}
		note := "# Fixture Note {#el:note}\n\nA deterministic transform of the intent.\n\n" +
			"## Upstream {#el:upstream}\n\n" + string(upstream)
		return local.ExecuteResult{Outputs: []local.ProducedOutput{{
			OutputID: ctx.Manifest.Expected[0].OutputID,
			Body:     []byte(note),
		}}}, nil
	})

	config := Config{
		Repo:        t.TempDir(),
		DataHome:    t.TempDir(),
		CatalogDir:  catalogDir,
		BackendsDir: filepath.Join("..", "..", "testdata", "v0-spine-fixture", "backends"),
		PolicyPath:  filepath.Join("..", "..", "policy", "driver.yaml"),
		Out:         devNull,
		Runtime:     runtime,
		Now:         time.Now,
	}
	if code, err := Run(config, "init", []string{
		"-repo-id", repoID,
		"-root-commit", strings.Repeat("c", 40),
		"-name", "checks-acceptance-boundary-fixture",
	}); code != ExitOK {
		t.Fatalf("init exit = %d (%v), want 0", code, err)
	}

	readLedger := func(t *testing.T) []records.DecodedRecord {
		t.Helper()
		graph, _, err := store.OpenGraph(store.OpenOptions{DataHome: config.DataHome, RepoRoot: config.Repo})
		if err != nil {
			t.Fatalf("OpenGraph() error = %v", err)
		}
		all, err := graph.Records()
		if err != nil {
			t.Fatalf("Records() error = %v", err)
		}
		return all
	}
	return config, readLedger
}

func copyG7CatalogTree(t *testing.T, from, to string) {
	t.Helper()
	for _, section := range []string{"passes", "gates", "artifact-kinds", "target-states"} {
		entries, err := os.ReadDir(filepath.Join(from, section))
		if err != nil {
			if os.IsNotExist(err) {
				continue
			}
			t.Fatalf("read %s/%s: %v", from, section, err)
		}
		for _, entry := range entries {
			if entry.IsDir() || !strings.HasSuffix(entry.Name(), ".yaml") {
				continue
			}
			raw, err := os.ReadFile(filepath.Join(from, section, entry.Name()))
			if err != nil {
				t.Fatalf("read catalog file: %v", err)
			}
			target := filepath.Join(to, section, entry.Name())
			if err := os.MkdirAll(filepath.Dir(target), 0o755); err != nil {
				t.Fatalf("mkdir %s: %v", filepath.Dir(target), err)
			}
			if err := os.WriteFile(target, raw, 0o644); err != nil {
				t.Fatalf("write %s: %v", target, err)
			}
		}
	}
}

func readG7Ledger(t *testing.T, read func(t *testing.T) []records.DecodedRecord) []records.DecodedRecord {
	t.Helper()
	return read(t)
}

func countG7Records(all []records.DecodedRecord, recordType string) int {
	count := 0
	for _, record := range all {
		if record.Type == recordType {
			count++
		}
	}
	return count
}

func countG7AcceptanceResults(all []records.DecodedRecord) int {
	count := 0
	for _, record := range all {
		if record.Type != "gate_result" {
			continue
		}
		if class, _ := record.Payload["gate_class"].(string); class == "acceptance" {
			count++
		}
	}
	return count
}
