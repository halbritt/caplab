package llm_test

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/halbritt/striatum-next/internal/backend"
	"github.com/halbritt/striatum-next/internal/backend/llm"
	"github.com/halbritt/striatum-next/internal/backend/supervise"
)

func TestV2DispatchRefusesChangedBackendDeclaration(t *testing.T) {
	adapter, spool := newAdapter(t, "commit")
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")
	inputBody, err := os.ReadFile(filepath.Join(filepath.Dir(manifestPath), manifest.Inputs[0].Path))
	if err != nil {
		t.Fatal(err)
	}
	if err := os.RemoveAll(filepath.Dir(manifestPath)); err != nil {
		t.Fatal(err)
	}
	declarationBody, err := os.ReadFile(adapter.Declaration)
	if err != nil {
		t.Fatal(err)
	}
	declarationHash := sha256.Sum256(declarationBody)
	manifest.SchemaVersion = 2
	manifest.Expected[0].KindSchemaVersion = 1
	manifest.Expected[0].DerivedFromOutputs = []string{}
	manifest.Lane.DeclarationHash = hex.EncodeToString(declarationHash[:])
	manifest.DispatchID, err = backend.DispatchIDV2(manifest.Run.RunRef, manifest.Run.RunManifestHash, manifest.Lane.LaneID, manifest.Lane.Attempt)
	if err != nil {
		t.Fatal(err)
	}
	dir, err := backend.WriteDispatchBundle(spool, manifest, map[string][]byte{manifest.Inputs[0].Path: inputBody})
	if err != nil {
		t.Fatal(err)
	}
	manifestPath = filepath.Join(dir, "manifest.json")
	if err := os.WriteFile(adapter.Declaration, append(declarationBody, []byte("\n# model changed\n")...), 0o644); err != nil {
		t.Fatal(err)
	}
	if _, err := adapter.Dispatch(manifestPath); err == nil {
		t.Fatal("v2 dispatch executed through a changed backend declaration")
	} else {
		var refusal llm.Refusal
		if !errors.As(err, &refusal) || refusal.Code != llm.RefusalDeclarationMismatch {
			t.Fatalf("Dispatch() error = %v, want declaration_mismatch", err)
		}
	}
	if _, err := os.Stat(spool.SubmissionDir(manifest.DispatchID)); !os.IsNotExist(err) {
		t.Fatalf("changed declaration produced submission state: %v", err)
	}
}

// TestMain lets the test binary play two extra roles: the confinement init
// helper and this backend's process surface (the supervisor exec target the
// adapter forks).
func TestMain(m *testing.M) {
	supervise.MaybeRunInit()
	if id := os.Getenv("STRIATUM_TEST_SURFACE"); id != "" {
		os.Exit(llm.CmdMain(id, os.Args[1:]))
	}
	os.Exit(m.Run())
}

// requireDelegation gates the confined-dispatch tests on a delegated cgroup2
// subtree, mirroring the supervise package's gate: every dispatch here runs
// the runtime under StartConfined, whose lane cgroup an undelegated shell
// (an SSH session scope) cannot create. Skip where delegation is absent so
// `go test ./...` holds in any environment; under STRIATUM_REQUIRE_CGROUP
// (the strict supervision suite) fail instead of skip, so the coverage never
// silently vanishes where delegation is expected.
func requireDelegation(t *testing.T) {
	t.Helper()
	if err := supervise.DelegationAvailable(); err != nil {
		if os.Getenv("STRIATUM_REQUIRE_CGROUP") != "" {
			t.Fatalf("%v — confined dispatch untestable here (STRIATUM_REQUIRE_CGROUP is set)", err)
		}
		t.Skipf("%v — confined dispatch untestable here; run inside a "+
			"systemd-delegated user subtree (STRIATUM_REQUIRE_CGROUP makes this fatal)", err)
	}
}

func TestRenderPromptV2CarriesEveryExactEnvironmentBody(t *testing.T) {
	bundle := t.TempDir()
	decisionBody := []byte("D0006.C11 exact request semantics\n")
	policyBody := []byte("policy_version: 7\n")
	entries := []backend.EnvironmentEntry{
		{Kind: "decision", ID: "D0006.C11", Hash: hashBody(decisionBody), Path: "environment/decision/D0006.C11"},
		{Kind: "policy", ID: "driver", Hash: hashBody(policyBody), Path: "environment/policy/driver"},
	}
	for i, body := range [][]byte{decisionBody, policyBody} {
		path := filepath.Join(bundle, entries[i].Path)
		if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(path, body, 0o600); err != nil {
			t.Fatal(err)
		}
	}
	manifest := backend.DispatchManifest{
		SchemaVersion: 2,
		Run:           backend.DispatchRun{PassID: "build", ContractVersion: 2},
		Objective:     backend.Objective{Summary: "execute exact declared semantics"},
		Environment:   backend.Environment{Entries: entries},
		Expected:      []backend.ExpectedOut{},
	}
	prompt, err := llm.RenderPrompt(manifest, bundle, "/work", "")
	if err != nil {
		t.Fatalf("RenderPrompt(v2) error = %v", err)
	}
	for _, want := range []string{
		"environment decision:D0006.C11:" + entries[0].Hash,
		string(decisionBody),
		"environment policy:driver:" + entries[1].Hash,
		string(policyBody),
	} {
		if !strings.Contains(prompt, strings.TrimSpace(want)) {
			t.Fatalf("v2 prompt omitted %q:\n%s", want, prompt)
		}
	}
}

func TestArgPromptSpillsNULBearingContextToMaterializedPaths(t *testing.T) {
	bundle := t.TempDir()
	environmentBody := []byte("decision-before\x00decision-after\n")
	inputBody := []byte("input-before\x00input-after\n")
	environmentPath := "environment/decision/D0006"
	inputPath := "inputs/00-binary-context"
	for path, body := range map[string][]byte{environmentPath: environmentBody, inputPath: inputBody} {
		full := filepath.Join(bundle, path)
		if err := os.MkdirAll(filepath.Dir(full), 0o700); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(full, body, 0o600); err != nil {
			t.Fatal(err)
		}
	}
	manifest := backend.DispatchManifest{
		SchemaVersion: 2,
		Run:           backend.DispatchRun{PassID: "build", ContractVersion: 2},
		Objective:     backend.Objective{Summary: "execute exact declared semantics"},
		Environment: backend.Environment{Entries: []backend.EnvironmentEntry{{
			Kind: "decision", ID: "D0006", Hash: hashBody(environmentBody), Path: environmentPath,
		}}},
		Inputs: []backend.DispatchInput{{
			Identity: "evidence/binary", VersionSeq: 1, ContentHash: hashBody(inputBody), Path: inputPath,
		}},
		Expected: []backend.ExpectedOut{},
	}
	prompt, err := llm.RenderPrompt(manifest, bundle, "/work", "")
	if err != nil {
		t.Fatal(err)
	}
	if strings.IndexByte(prompt, 0) >= 0 {
		t.Fatal("argv-mode prompt retained a NUL byte")
	}
	for _, path := range []string{environmentPath, inputPath} {
		if !strings.Contains(prompt, "materialized at "+path) {
			t.Fatalf("argv-mode prompt did not preserve NUL-bearing context by path %q:\n%s", path, prompt)
		}
	}
}

func TestArgPromptSpillsOversizeEnvironmentToItsExactMaterializedPath(t *testing.T) {
	bundle := t.TempDir()
	path := "environment/decision/D0007.C11"
	body := append(bytes.Repeat([]byte("e"), 300<<10), []byte("OVERSIZE_DECLARED_ENVIRONMENT_SENTINEL\n")...)
	full := filepath.Join(bundle, path)
	if err := os.MkdirAll(filepath.Dir(full), 0o700); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(full, body, 0o600); err != nil {
		t.Fatal(err)
	}
	manifest := backend.DispatchManifest{
		SchemaVersion: 2,
		Run:           backend.DispatchRun{PassID: "build", ContractVersion: 2},
		Objective:     backend.Objective{Summary: "execute exact declared semantics"},
		Environment: backend.Environment{Entries: []backend.EnvironmentEntry{{
			Kind: "decision", ID: "D0007.C11", Hash: hashBody(body), Path: path,
		}}},
		Expected: []backend.ExpectedOut{},
	}
	prompt, err := llm.RenderPrompt(manifest, bundle, "/work", "")
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(prompt, "OVERSIZE_DECLARED_ENVIRONMENT_SENTINEL") {
		t.Fatal("oversize declared environment body was inlined into one argv element")
	}
	if !strings.Contains(prompt, "materialized at "+path) {
		t.Fatalf("prompt does not preserve oversize environment by exact path:\n%.2000s", prompt)
	}
	if len(prompt) >= 128<<10 {
		t.Fatalf("prompt still exceeds the single-argv bound: %d bytes", len(prompt))
	}
}

func TestArgPromptRefusesUnspillableOversizeFraming(t *testing.T) {
	manifest := backend.DispatchManifest{
		Run:       backend.DispatchRun{PassID: "build", ContractVersion: 2},
		Objective: backend.Objective{Summary: strings.Repeat("x", 140<<10)},
		Expected:  []backend.ExpectedOut{},
	}
	if _, err := llm.RenderPrompt(manifest, t.TempDir(), "/work", ""); err == nil || !strings.Contains(err.Error(), "maximum") {
		t.Fatalf("unspillable argv prompt error = %v", err)
	}
}

func TestArgPromptSpillsContextUntilFullRenderedPromptFits(t *testing.T) {
	bundle := t.TempDir()
	environmentPath := "environment/decision/D0007.C11"
	inputPath := "inputs/00-design"
	environmentBody := append(bytes.Repeat([]byte("e"), 47<<10), []byte("ENVIRONMENT_SENTINEL\n")...)
	inputBody := append(bytes.Repeat([]byte("i"), 43<<10), []byte("INPUT_SENTINEL\n")...)
	for path, body := range map[string][]byte{
		environmentPath: environmentBody,
		inputPath:       inputBody,
	} {
		full := filepath.Join(bundle, path)
		if err := os.MkdirAll(filepath.Dir(full), 0o700); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(full, body, 0o600); err != nil {
			t.Fatal(err)
		}
	}
	manifest := backend.DispatchManifest{
		SchemaVersion: 2,
		Run:           backend.DispatchRun{PassID: "build", ContractVersion: 2},
		Objective:     backend.Objective{Summary: strings.Repeat("f", 42<<10)},
		Environment: backend.Environment{Entries: []backend.EnvironmentEntry{{
			Kind: "decision", ID: "D0007.C11", Hash: hashBody(environmentBody), Path: environmentPath,
		}}},
		Inputs: []backend.DispatchInput{{
			Identity: "design", VersionSeq: 1, ContentHash: hashBody(inputBody), Path: inputPath,
		}},
		Expected: []backend.ExpectedOut{},
	}

	prompt, err := llm.RenderPrompt(manifest, bundle, "/work", "")
	if err != nil {
		t.Fatalf("RenderPrompt() error = %v; path-backed context should spill before refusal", err)
	}
	if len(prompt) >= 128<<10 {
		t.Fatalf("rendered argv prompt = %d bytes, want below 128 KiB", len(prompt))
	}
	if !strings.Contains(prompt, "materialized at "+environmentPath) {
		t.Fatalf("largest preservable context was not spilled by exact path:\n%.2000s", prompt)
	}
	if !strings.Contains(prompt, "INPUT_SENTINEL") {
		t.Fatal("renderer spilled more context after the full prompt already fit")
	}
}

func hashBody(body []byte) string {
	sum := sha256.Sum256(body)
	return hex.EncodeToString(sum[:])
}

// fakeCLI writes a shell script standing in for an agent runtime. The
// adapter never knows the difference — the seam is files (A4/A6). Like any
// real CLI, the fake answers --version promptly.
func fakeCLI(t *testing.T, script string) string {
	t.Helper()
	path := filepath.Join(t.TempDir(), "fake-runtime")
	body := `#!/bin/sh
if [ "$1" = "--version" ]; then echo "fake-runtime 9.9.9"; exit 0; fi
` + script
	if err := os.WriteFile(path, []byte(body), 0o755); err != nil {
		t.Fatal(err)
	}
	return path
}

func testConfig(t *testing.T, cli string) llm.Config {
	t.Helper()
	config, err := llm.LoadConfig(writeDeclaration(t, cli))
	if err != nil {
		t.Fatalf("LoadConfig() error = %v", err)
	}
	return config
}

func TestLoadConfigReadsStdoutOutputMode(t *testing.T) {
	cli := fakeCLI(t, `echo ok`)
	path := writeDeclaration(t, cli)
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	raw = bytes.Replace(raw, []byte("  prompt_mode: arg\n"), []byte("  prompt_mode: arg\n  stdout_output: single-required-output\n"), 1)
	if err := os.WriteFile(path, raw, 0o644); err != nil {
		t.Fatal(err)
	}
	config, err := llm.LoadConfig(path)
	if err != nil {
		t.Fatal(err)
	}
	if config.StdoutOutput != "single-required-output" {
		t.Fatalf("stdout_output = %q, want single-required-output", config.StdoutOutput)
	}
}

func TestLoadConfigRefusesUnknownPromptMode(t *testing.T) {
	cli := fakeCLI(t, `echo ok`)
	path := writeDeclaration(t, cli)
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	raw = bytes.Replace(raw, []byte("  prompt_mode: arg\n"), []byte("  prompt_mode: implicit-default\n"), 1)
	if err := os.WriteFile(path, raw, 0o644); err != nil {
		t.Fatal(err)
	}

	if _, err := llm.LoadConfig(path); err == nil || !strings.Contains(err.Error(), "prompt_mode") {
		t.Fatalf("LoadConfig() unknown prompt_mode error = %v", err)
	}
}

// TestLoadConfigRefusesLLMDeclarationWithoutAttemptsProvenance: an LLM
// declaration (one setting adapter.prompt_mode) whose
// provenance_fields.required omits "attempts" is refused at load — the
// per-attempt invocation closure is a structural fleet-wide requirement,
// not a per-declaration choice.
func TestLoadConfigRefusesLLMDeclarationWithoutAttemptsProvenance(t *testing.T) {
	cli := fakeCLI(t, `echo ok`)
	path := writeDeclaration(t, cli)
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	pruned := bytes.Replace(raw, []byte(", attempts]"), []byte("]"), 1)
	if bytes.Equal(pruned, raw) {
		t.Fatal("fixture no longer lists attempts; the witness cannot prune it")
	}
	if err := os.WriteFile(path, pruned, 0o644); err != nil {
		t.Fatal(err)
	}
	if _, err := llm.LoadConfig(path); err == nil || !strings.Contains(err.Error(), "attempts") {
		t.Fatalf("LoadConfig() with attempts omitted = %v, want a refusal naming attempts", err)
	}

	// A declaration with no provenance_fields block at all omits attempts too.
	stripped := bytes.Split(raw, []byte("provenance_fields:"))[0]
	if err := os.WriteFile(path, stripped, 0o644); err != nil {
		t.Fatal(err)
	}
	if _, err := llm.LoadConfig(path); err == nil || !strings.Contains(err.Error(), "attempts") {
		t.Fatalf("LoadConfig() with no provenance_fields = %v, want a refusal naming attempts", err)
	}
}

// writeDeclaration writes a test backend declaration and returns its path.
func writeDeclaration(t *testing.T, cli string) string {
	t.Helper()
	dir := t.TempDir()
	path := filepath.Join(dir, "backend.yaml")
	declaration := `schema_version: 1
id: test-llm
kind: execution-backend
status: accepted
aliasing:
  aliasing_class: test-family
capabilities:
  supported_pass_types: [proposal-generation, review]
  forbidden_pass_types: [verification]
constraints:
  internal_retry: { max: 1 }
adapter:
  command: [` + cli + `]
  prompt_mode: arg
  version_command: [` + cli + `, --version]
provenance_fields:
  required: [agent_runtime_id, agent_runtime_version, session_nonce, rendered_prompt_hash, attempts]
`
	if err := os.WriteFile(path, []byte(declaration), 0o644); err != nil {
		t.Fatal(err)
	}
	return path
}

func writeBundle(t *testing.T, spool backend.Spool, passID string) (string, backend.DispatchManifest) {
	t.Helper()
	inputBody := []byte("# Intent {#el:intent}\n\nthe pinned upstream\n")
	sum := sha256.Sum256(inputBody)
	manifest := backend.DispatchManifest{
		SchemaVersion: 1,
		Run: backend.DispatchRun{
			RunRef:          11,
			RunManifestHash: strings.Repeat("ab", 32),
			PassID:          passID,
			ContractVersion: 1, ImplVersion: 1,
		},
		Lane:      backend.DispatchLane{LaneID: "lane-1", Role: "producer", Attempt: 1},
		Objective: backend.Objective{Summary: "produce the proposal", Subject: map[string]string{"identity": "rfcs/x/proposal"}},
		Inputs: []backend.DispatchInput{{
			Identity: "rfcs/x/intent-statement", VersionSeq: 2,
			ContentHash: hex.EncodeToString(sum[:]), Path: "inputs/00-intent",
		}},
		Environment:  backend.Environment{Decisions: []backend.EnvironmentEntry{}, Policies: []backend.EnvironmentEntry{}},
		PromptAssets: []backend.PromptAsset{},
		Workspace:    backend.WorkspaceSpec{EffectClass: "E1", WriteScope: backend.WriteScope{Allow: []string{"**"}, Deny: []string{}}},
		Expected: []backend.ExpectedOut{{
			OutputID: "proposal", Kind: "proposal", Identity: "rfcs/x/proposal",
			Placement: "stored", Required: true,
		}},
		Submission: backend.SubmissionSpec{SpoolPath: "spool/submissions/x"},
	}
	id, err := backend.DispatchID(manifest.Run.RunManifestHash, manifest.Lane.LaneID, manifest.Lane.Attempt)
	if err != nil {
		t.Fatal(err)
	}
	manifest.DispatchID = id
	dir, err := backend.WriteDispatchBundle(spool, manifest, map[string][]byte{"inputs/00-intent": inputBody})
	if err != nil {
		t.Fatalf("WriteDispatchBundle() error = %v", err)
	}
	return filepath.Join(dir, "manifest.json"), manifest
}

func newAdapter(t *testing.T, script string) (*llm.Adapter, backend.Spool) {
	t.Helper()
	spool := backend.Spool{Root: t.TempDir()}
	cli := fakeCLI(t, script)
	declaration := writeDeclaration(t, cli)
	config, err := llm.LoadConfig(declaration)
	if err != nil {
		t.Fatalf("LoadConfig() error = %v", err)
	}
	self, err := os.Executable()
	if err != nil {
		t.Fatal(err)
	}
	t.Setenv("STRIATUM_TEST_SURFACE", "test-llm")
	return &llm.Adapter{
		Config:      config,
		Spool:       spool,
		Surface:     []string{self},
		Declaration: declaration,
	}, spool
}

func setPromptMode(t *testing.T, adapter *llm.Adapter, mode string) {
	t.Helper()
	raw, err := os.ReadFile(adapter.Declaration)
	if err != nil {
		t.Fatal(err)
	}
	raw = bytes.Replace(raw, []byte("  prompt_mode: arg\n"), []byte("  prompt_mode: "+mode+"\n"), 1)
	if err := os.WriteFile(adapter.Declaration, raw, 0o644); err != nil {
		t.Fatal(err)
	}
	adapter.Config, err = llm.LoadConfig(adapter.Declaration)
	if err != nil {
		t.Fatal(err)
	}
}

// waitSubmission polls for the detached supervisor's commit: dispatch
// returns at acceptance, the rename lands later.
func waitSubmission(t *testing.T, spool backend.Spool, dispatchID string) backend.SubmissionManifest {
	t.Helper()
	path := filepath.Join(spool.SubmissionDir(dispatchID), "manifest.json")
	deadline := time.Now().Add(15 * time.Second)
	for time.Now().Before(deadline) {
		if _, err := os.Stat(path); err == nil {
			submission, err := backend.ReadSubmissionManifest(path)
			if err != nil {
				t.Fatalf("committed submission unreadable: %v", err)
			}
			return submission
		}
		time.Sleep(20 * time.Millisecond)
	}
	log, _ := os.ReadFile(filepath.Join(spool.WorkspaceDir(dispatchID), "supervisor.log"))
	t.Fatalf("no committed submission for %s within deadline; supervisor.log:\n%s", dispatchID, log)
	return backend.SubmissionManifest{}
}

const goodScript = `mkdir -p outputs
cat > outputs/proposal <<'EOF'
# Proposal {#el:proposal}

A fake proposal body.
EOF
echo done`

func TestDispatchCommitsSealedSubmission(t *testing.T) {
	requireDelegation(t)
	adapter, spool := newAdapter(t, goodScript)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")

	dir, err := adapter.Dispatch(manifestPath)
	if err != nil {
		t.Fatalf("Dispatch() error = %v", err)
	}
	if dir != spool.SubmissionDir(manifest.DispatchID) {
		t.Fatalf("submission dir = %s, want spool target", dir)
	}
	submission := waitSubmission(t, spool, manifest.DispatchID)
	if err := submission.VerifySeal(); err != nil {
		t.Fatalf("seal: %v", err)
	}
	if submission.Status != "complete" {
		for _, ex := range submission.Exhaust {
			b, _ := os.ReadFile(filepath.Join(spool.SubmissionDir(manifest.DispatchID), ex.Path))
			t.Logf("exhaust %s:\n%s", ex.Path, b)
		}
		t.Fatalf("status = %s, want complete (diagnostics %v)", submission.Status, submission.Diagnostics.Classes)
	}
	if submission.Attribution.AliasingClass != "test-family" {
		t.Fatalf("aliasing class = %s", submission.Attribution.AliasingClass)
	}
	if submission.Attribution.DeclarationHash != manifest.Lane.DeclarationHash {
		t.Fatalf("declaration hash = %s, want %s", submission.Attribution.DeclarationHash, manifest.Lane.DeclarationHash)
	}
	if submission.Attribution.RenderedPrompt == "" {
		t.Fatal("rendered_prompt_hash missing — prompt discipline unpinned")
	}
	if submission.Attribution.SessionNonce == "" {
		t.Fatal("session nonce missing")
	}
	if len(submission.Exhaust) == 0 {
		t.Fatal("transcript exhaust missing")
	}
	body, err := os.ReadFile(filepath.Join(dir, submission.Outputs[0].Path))
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(body), "{#el:proposal}") {
		t.Fatalf("output body unexpected:\n%s", body)
	}
}

func TestDispatchPromptCarriesBundleContent(t *testing.T) {
	requireDelegation(t)
	// The fake runtime dumps its prompt (last arg) so the test can assert
	// the sealed bundle's projection reached the runtime.
	adapter, spool := newAdapter(t, `mkdir -p outputs
printf '%s' "$1" > prompt-received
cat > outputs/proposal <<'EOF'
# Proposal {#el:p}
body
EOF`)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")
	if _, err := adapter.Dispatch(manifestPath); err != nil {
		t.Fatal(err)
	}
	submission := waitSubmission(t, spool, manifest.DispatchID)
	// Workspace is dismantled after commit; recover the prompt from the
	// committed transcript? The prompt file lived in the workspace. Instead
	// re-render deterministically and compare against attribution.
	workAbs, err := filepath.Abs(filepath.Join(spool.WorkspaceDir(manifest.DispatchID), "work"))
	if err != nil {
		t.Fatal(err)
	}
	prompt, err := llm.RenderPrompt(manifest, filepath.Dir(manifestPath), workAbs, "")
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(prompt, "the pinned upstream") {
		t.Fatal("prompt does not materialize the pinned input")
	}
	if !strings.Contains(prompt, "outputs/proposal") {
		t.Fatal("prompt does not state the required outputs")
	}
	if !strings.Contains(prompt, "never ask questions") {
		t.Fatal("prompt lacks the one-shot preamble")
	}
	if submission.Attribution.RenderedPrompt != llm.PromptHash(prompt) {
		t.Fatal("rendered_prompt_hash does not pin the deterministic rendering")
	}
}

func TestStrategyThenExitRelaunches(t *testing.T) {
	requireDelegation(t)
	// First invocation produces nothing (strategy-then-exit); the marker
	// makes the second invocation produce the output.
	marker := filepath.Join(t.TempDir(), "attempted")
	adapter, spool := newAdapter(t, `if [ -f `+marker+` ]; then
mkdir -p outputs
cat > outputs/proposal <<'EOF'
# Proposal {#el:p}
recovered
EOF
else
touch `+marker+`
echo "here is my plan..."
fi`)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")
	if _, err := adapter.Dispatch(manifestPath); err != nil {
		t.Fatal(err)
	}
	submission := waitSubmission(t, spool, manifest.DispatchID)
	if submission.Status != "complete" {
		t.Fatalf("status = %s, want complete after corrective relaunch", submission.Status)
	}
	if submission.Attribution.InternalRelaunch != 1 {
		t.Fatalf("internal_relaunches = %d, want 1", submission.Attribution.InternalRelaunch)
	}
	if !contains(submission.Diagnostics.Classes, "strategy_then_exit") {
		t.Fatalf("diagnostics = %v, want strategy_then_exit surfaced", submission.Diagnostics.Classes)
	}
}

func TestUnrepairedOutputYieldsPartial(t *testing.T) {
	requireDelegation(t)
	adapter, spool := newAdapter(t, `echo "all plan, no artifact"`)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")
	if _, err := adapter.Dispatch(manifestPath); err != nil {
		t.Fatal(err)
	}
	submission := waitSubmission(t, spool, manifest.DispatchID)
	if submission.Status != "partial" && submission.Status != "failed" {
		t.Fatalf("status = %s, want partial/failed", submission.Status)
	}
	if !contains(submission.Diagnostics.Classes, "strategy_then_exit") {
		t.Fatalf("diagnostics = %v", submission.Diagnostics.Classes)
	}
	if submission.Outputs[0].Status != "missing" {
		t.Fatal("missing output must be declared missing, never fabricated")
	}
}

func TestOutputShapeRepairLoop(t *testing.T) {
	requireDelegation(t)
	// First attempt writes markdown without element anchors; the corrective
	// relaunch (fed the validator's error text) repairs it.
	marker := filepath.Join(t.TempDir(), "attempted")
	adapter, spool := newAdapter(t, `mkdir -p outputs
if [ -f `+marker+` ]; then
cat > outputs/proposal <<'EOF'
# Proposal {#el:p}
repaired
EOF
else
touch `+marker+`
cat > outputs/proposal <<'EOF'
# Proposal without anchors
broken
EOF
fi`)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")
	if _, err := adapter.Dispatch(manifestPath); err != nil {
		t.Fatal(err)
	}
	submission := waitSubmission(t, spool, manifest.DispatchID)
	if submission.Status != "complete" {
		t.Fatalf("status = %s, want complete after shape repair", submission.Status)
	}
	if !contains(submission.Diagnostics.Classes, "output_shape_error") {
		t.Fatalf("diagnostics = %v, want output_shape_error surfaced", submission.Diagnostics.Classes)
	}
}

func TestDispatchTypedRefusals(t *testing.T) {
	adapter, spool := newAdapter(t, goodScript)

	manifestPath, _ := writeBundle(t, spool, "verification")
	_, err := adapter.Dispatch(manifestPath)
	refusal, ok := err.(llm.Refusal)
	if !ok || refusal.Code != llm.RefusalUnsupportedPass {
		t.Fatalf("err = %v, want unsupported_pass (forbidden wins)", err)
	}

	adapter.Config.Command = []string{"/nonexistent/runtime"}
	manifestPath2, _ := writeBundle(t, backend.Spool{Root: t.TempDir()}, "proposal-generation")
	_, err = adapter.Dispatch(manifestPath2)
	refusal, ok = err.(llm.Refusal)
	if !ok || refusal.Code != llm.RefusalRuntimeUnavailable {
		t.Fatalf("err = %v, want runtime_unavailable", err)
	}
}

func TestDispatchIdempotentOnCommittedSubmission(t *testing.T) {
	adapter, spool := newAdapter(t, goodScript)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")
	first, err := adapter.Dispatch(manifestPath)
	if err != nil {
		t.Fatal(err)
	}
	waitSubmission(t, spool, manifest.DispatchID)
	raw1, err := os.ReadFile(filepath.Join(first, "manifest.json"))
	if err != nil {
		t.Fatal(err)
	}
	second, err := adapter.Dispatch(manifestPath)
	if err != nil {
		t.Fatal(err)
	}
	raw2, _ := os.ReadFile(filepath.Join(second, "manifest.json"))
	if string(raw1) != string(raw2) {
		t.Fatal("re-dispatch of a committed submission must return the winner unchanged")
	}
	_ = manifest
}

func TestAbortNeverTouchesCommittedSubmission(t *testing.T) {
	adapter, spool := newAdapter(t, goodScript)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")
	if _, err := adapter.Dispatch(manifestPath); err != nil {
		t.Fatal(err)
	}
	waitSubmission(t, spool, manifest.DispatchID)
	if err := adapter.Abort(manifest.DispatchID); err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(spool.SubmissionDir(manifest.DispatchID)); err != nil {
		t.Fatal("abort touched a committed submission")
	}
	if err := adapter.Abort("unknown-dispatch"); err != nil {
		t.Fatal("abort must be safe on unknown ids")
	}
}

// TestAbortRetainsSupervisorLogBeforeReclaim: an abort can reach a live lane
// whose own supervisor never gets to run its own Run()-driven log
// retention, so reclaimResidue must retain the log itself before it unlinks
// the workspace tree that holds the log's only copy.
func TestAbortRetainsSupervisorLogBeforeReclaim(t *testing.T) {
	adapter, spool := newAdapter(t, goodScript)
	_, manifest := writeBundle(t, spool, "proposal-generation")

	logPath := filepath.Join(spool.WorkspaceDir(manifest.DispatchID), "supervisor.log")
	if err := os.MkdirAll(filepath.Dir(logPath), 0o700); err != nil {
		t.Fatal(err)
	}
	body := []byte("abort-path supervisor stdio\n")
	if err := os.WriteFile(logPath, body, 0o600); err != nil {
		t.Fatal(err)
	}

	if err := adapter.Abort(manifest.DispatchID); err != nil {
		t.Fatal(err)
	}
	retained, err := os.ReadFile(spool.RetainedLogPath(manifest.DispatchID))
	if err != nil {
		t.Fatalf("retained supervisor log missing after Abort reclaim: %v", err)
	}
	if string(retained) != string(body) {
		t.Fatalf("retained log = %q, want %q", retained, body)
	}
}

// TestJanitorRetainsSupervisorLogForDeadLaneResidue: the janitor sweep is
// exactly the abandonment path a supervisor that dies before its own
// Run()-driven retention leaves behind — it must retain a dead lane's
// supervisor log before removing its workspace residue.
func TestJanitorRetainsSupervisorLogForDeadLaneResidue(t *testing.T) {
	adapter, spool := newAdapter(t, goodScript)
	_, manifest := writeBundle(t, spool, "proposal-generation")

	logPath := filepath.Join(spool.WorkspaceDir(manifest.DispatchID), "supervisor.log")
	if err := os.MkdirAll(filepath.Dir(logPath), 0o700); err != nil {
		t.Fatal(err)
	}
	body := []byte("dead-lane supervisor stdio\n")
	if err := os.WriteFile(logPath, body, 0o600); err != nil {
		t.Fatal(err)
	}

	if err := adapter.Janitor(map[string]bool{}, map[string]bool{}); err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(spool.WorkspaceDir(manifest.DispatchID)); !os.IsNotExist(err) {
		t.Fatal("janitor left dead-lane workspace residue")
	}
	retained, err := os.ReadFile(spool.RetainedLogPath(manifest.DispatchID))
	if err != nil {
		t.Fatalf("retained supervisor log missing after janitor sweep: %v", err)
	}
	if string(retained) != string(body) {
		t.Fatalf("retained log = %q, want %q", retained, body)
	}
}

func TestProbeReportsRuntime(t *testing.T) {
	adapter, _ := newAdapter(t, `echo "fake-runtime 9.9.9"`)
	report := adapter.Probe()
	if !report.RuntimePresent {
		t.Fatal("runtime present, probe says absent")
	}
	if !strings.Contains(report.RuntimeVersion, "9.9.9") {
		t.Fatalf("runtime version = %q, want probed string", report.RuntimeVersion)
	}
	adapter.Config.Command = []string{"/nonexistent/runtime"}
	if adapter.Probe().RuntimePresent {
		t.Fatal("missing runtime, probe says present")
	}
}

func contains(list []string, value string) bool {
	for _, entry := range list {
		if entry == value {
			return true
		}
	}
	return false
}

func writeBundleWithLargeInput(t *testing.T, spool backend.Spool) (string, backend.DispatchManifest, []byte) {
	t.Helper()
	small := []byte("# Intent {#el:intent}\n\nthe pinned upstream\n")
	// Past the per-input inline bound: an anchored-base tree stand-in. Inlining
	// it would push the single-argv prompt past MAX_ARG_STRLEN (128 KiB).
	large := append(bytes.Repeat([]byte("x"), 300<<10), []byte(largeInputSentinel)...)
	smallSum := sha256.Sum256(small)
	largeSum := sha256.Sum256(large)
	manifest := backend.DispatchManifest{
		SchemaVersion: 1,
		Run: backend.DispatchRun{
			RunRef:          12,
			RunManifestHash: strings.Repeat("cd", 32),
			PassID:          "proposal-generation",
			ContractVersion: 1, ImplVersion: 1,
		},
		Lane:      backend.DispatchLane{LaneID: "lane-1", Role: "producer", Attempt: 1},
		Objective: backend.Objective{Summary: "produce the proposal against the base", Subject: map[string]string{"identity": "x/proposal"}},
		Inputs: []backend.DispatchInput{
			{
				Identity: "x/work-graph", VersionSeq: 2,
				ContentHash: hex.EncodeToString(smallSum[:]), Path: "inputs/00-work-graph",
			},
			{
				Identity: "x/base", VersionSeq: 3,
				ContentHash: hex.EncodeToString(largeSum[:]), Path: "inputs/01-base",
			},
		},
		Environment:  backend.Environment{Decisions: []backend.EnvironmentEntry{}, Policies: []backend.EnvironmentEntry{}},
		PromptAssets: []backend.PromptAsset{},
		Workspace:    backend.WorkspaceSpec{EffectClass: "E1", WriteScope: backend.WriteScope{Allow: []string{"**"}, Deny: []string{}}},
		Expected: []backend.ExpectedOut{{
			OutputID: "proposal", Kind: "proposal", Identity: "x/proposal",
			Placement: "stored", Required: true,
		}},
		Submission: backend.SubmissionSpec{SpoolPath: "spool/submissions/y"},
	}
	id, err := backend.DispatchID(manifest.Run.RunManifestHash, manifest.Lane.LaneID, manifest.Lane.Attempt)
	if err != nil {
		t.Fatal(err)
	}
	manifest.DispatchID = id
	dir, err := backend.WriteDispatchBundle(spool, manifest, map[string][]byte{
		"inputs/00-work-graph": small,
		"inputs/01-base":       large,
	})
	if err != nil {
		t.Fatalf("WriteDispatchBundle() error = %v", err)
	}
	return filepath.Join(dir, "manifest.json"), manifest, large
}

const largeInputSentinel = "PROMPT_ONLY_OVERSIZE_INPUT_SENTINEL_7f3c9e"

const largeEnvironmentSentinel = "ARGV_OVERSIZE_ENVIRONMENT_SENTINEL_91d4a7"

func writeBundleWithLargeEnvironment(t *testing.T, spool backend.Spool) (string, backend.DispatchManifest) {
	t.Helper()
	body := append(bytes.Repeat([]byte("d"), 300<<10), []byte(largeEnvironmentSentinel+"\n")...)
	path := "environment/decision/D0007.C11"
	manifest := backend.DispatchManifest{
		SchemaVersion: 1,
		Run: backend.DispatchRun{
			RunRef: 13, RunManifestHash: strings.Repeat("de", 32),
			PassID: "proposal-generation", ContractVersion: 1, ImplVersion: 1,
		},
		Lane:      backend.DispatchLane{LaneID: "lane-1", Role: "producer", Attempt: 1},
		Objective: backend.Objective{Summary: "execute the exact declared decision", Subject: map[string]string{"identity": "x/proposal"}},
		Environment: backend.Environment{Decisions: []backend.EnvironmentEntry{{
			ID: "D0007.C11", Hash: hashBody(body), Path: path,
		}}},
		PromptAssets: []backend.PromptAsset{},
		Workspace:    backend.WorkspaceSpec{EffectClass: "E1", WriteScope: backend.WriteScope{Allow: []string{"**"}, Deny: []string{}}},
		Expected: []backend.ExpectedOut{{
			OutputID: "proposal", Kind: "proposal", Identity: "x/proposal", Placement: "stored", Required: true,
		}},
		Submission: backend.SubmissionSpec{SpoolPath: "spool/submissions/environment"},
	}
	var err error
	manifest.DispatchID, err = backend.DispatchID(manifest.Run.RunManifestHash, manifest.Lane.LaneID, manifest.Lane.Attempt)
	if err != nil {
		t.Fatal(err)
	}
	dir, err := backend.WriteDispatchBundle(spool, manifest, map[string][]byte{path: body})
	if err != nil {
		t.Fatal(err)
	}
	return filepath.Join(dir, "manifest.json"), manifest
}

func TestDispatchArgRuntimeReadsOversizeDeclaredEnvironmentFromMaterializedPath(t *testing.T) {
	requireDelegation(t)
	adapter, spool := newAdapter(t, `if ! grep -q '`+largeEnvironmentSentinel+`' environment/decision/D0007.C11; then
echo "oversize declared environment missing from materialized path" >&2
exit 9
fi
mkdir -p outputs
cat > outputs/proposal <<'EOF'
# Proposal {#el:proposal}

The exact declared environment reached execution.
EOF`)
	manifestPath, manifest := writeBundleWithLargeEnvironment(t, spool)
	if _, err := adapter.Dispatch(manifestPath); err != nil {
		t.Fatal(err)
	}
	submission := waitSubmission(t, spool, manifest.DispatchID)
	if submission.Status != "complete" {
		t.Fatalf("status = %s, want complete (diagnostics %v)", submission.Status, submission.Diagnostics.Classes)
	}
}

func TestDispatchPromptOnlyRuntimeReceivesOversizeInputBody(t *testing.T) {
	requireDelegation(t)
	// This runtime consumes compiler context only from stdin. It deliberately
	// does not read inputs/01-base: prompt-only surfaces must receive the bytes,
	// while path spill remains an argv-mode execution mechanic.
	adapter, spool := newAdapter(t, `if ! grep -q '`+largeInputSentinel+`'; then
echo "oversize input sentinel missing from stdin" >&2
exit 9
fi
mkdir -p outputs
cat > outputs/proposal <<'EOF'
# Proposal {#el:p}

The oversize input reached stdin.
EOF`)
	setPromptMode(t, adapter, "stdin")
	manifestPath, manifest, _ := writeBundleWithLargeInput(t, spool)

	if _, err := adapter.Dispatch(manifestPath); err != nil {
		t.Fatal(err)
	}
	submission := waitSubmission(t, spool, manifest.DispatchID)
	if submission.Status != "complete" {
		t.Fatalf("status = %s, want complete (diagnostics %v)", submission.Status, submission.Diagnostics.Classes)
	}
	body, err := os.ReadFile(filepath.Join(spool.SubmissionDir(manifest.DispatchID), submission.Outputs[0].Path))
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(body), "oversize input reached stdin") {
		t.Fatalf("runtime output does not attest sentinel visibility:\n%s", body)
	}
}

func TestPromptReferencesOversizeInputInsteadOfInlining(t *testing.T) {
	// Regression: the first anchored-base build (a 4.3 MiB expanded repo tree
	// as inputs/01-base) inlined into the single-argv prompt died at execve
	// (MAX_ARG_STRLEN) with an empty transcript. Oversize inputs must be
	// referenced by their materialized workspace path, never inlined.
	dir := t.TempDir()
	spool := backend.Spool{Root: dir}
	if err := spool.EnsureLayout(); err != nil {
		t.Fatal(err)
	}
	manifestPath, manifest, large := writeBundleWithLargeInput(t, spool)
	prompt, err := llm.RenderPrompt(manifest, filepath.Dir(manifestPath), "/work", "")
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(prompt, string(large[:64])) {
		t.Fatal("oversize input body was inlined into the prompt")
	}
	if !strings.Contains(prompt, "materialized at inputs/01-base") {
		t.Fatalf("prompt does not reference the materialized oversize input:\n%.2000s", prompt)
	}
	if !strings.Contains(prompt, "the pinned upstream") {
		t.Fatal("small input should still inline")
	}
	if len(prompt) > 128<<10 {
		t.Fatalf("prompt still exceeds the single-argv bound: %d bytes", len(prompt))
	}
}

func TestImplementationPlanPromptStatesAcceptanceCheckRegistryRule(t *testing.T) {
	// The recurring plan defect (2026-07-08): lanes name acceptance_checks
	// entries that resolve to no registered set or check id (ac-1.1,
	// check:foo, a not-yet-registered guard set), so work-graph legality
	// refuses every packet as acceptance_check_unresolvable and a full
	// re-plan cycle burns. The plan prompt must state the rule and name the
	// always-available sets so the lane never invents an entry.
	dir := t.TempDir()
	spool := backend.Spool{Root: dir}
	if err := spool.EnsureLayout(); err != nil {
		t.Fatal(err)
	}
	manifest := backend.DispatchManifest{
		SchemaVersion: 1,
		Run: backend.DispatchRun{
			RunRef: 1, RunManifestHash: strings.Repeat("ab", 32),
			PassID: "implementation-planning", ContractVersion: 1, ImplVersion: 1,
		},
		Lane:         backend.DispatchLane{LaneID: "lane-1", Role: "producer", Attempt: 1},
		Objective:    backend.Objective{Summary: "plan the delivery", Subject: map[string]string{"identity": "x/implementation-plan"}},
		Environment:  backend.Environment{Decisions: []backend.EnvironmentEntry{}, Policies: []backend.EnvironmentEntry{}},
		PromptAssets: []backend.PromptAsset{},
		Workspace:    backend.WorkspaceSpec{EffectClass: "E1", WriteScope: backend.WriteScope{Allow: []string{"**"}, Deny: []string{}}},
		Expected: []backend.ExpectedOut{{
			OutputID: "implementation-plan", Kind: "implementation-plan",
			Identity: "x/implementation-plan", Placement: "stored", Required: true,
		}},
		Submission: backend.SubmissionSpec{SpoolPath: "spool/submissions/z"},
	}
	id, err := backend.DispatchID(manifest.Run.RunManifestHash, manifest.Lane.LaneID, manifest.Lane.Attempt)
	if err != nil {
		t.Fatal(err)
	}
	manifest.DispatchID = id
	manifestDir, err := backend.WriteDispatchBundle(spool, manifest, map[string][]byte{})
	if err != nil {
		t.Fatalf("WriteDispatchBundle() error = %v", err)
	}
	prompt, err := llm.RenderPrompt(manifest, filepath.Dir(filepath.Join(manifestDir, "manifest.json")), "/work", "")
	if err != nil {
		t.Fatal(err)
	}
	for _, want := range []string{
		"already exist in the repository check registry",
		"acceptance_check_unresolvable",
		`"code"`, `"subject-default"`, `"stalls-guards"`,
		"may NOT name a check it introduces",
	} {
		if !strings.Contains(prompt, want) {
			t.Fatalf("implementation-plan prompt is missing the acceptance-check rule fragment %q:\n%.3000s", want, prompt)
		}
	}
}

func TestSupervisorMaterializesInputsIntoWorkTree(t *testing.T) {
	requireDelegation(t)
	// The runtime must be able to read every pinned input as a file at its
	// manifest path — the prompt references oversize bodies by exactly that
	// path. The fake runtime copies the materialized base into its output.
	adapter, spool := newAdapter(t, `mkdir -p outputs
printf '# Base Size {#el:base-size}\n\n%s bytes\n' "$(wc -c < inputs/01-base | tr -d ' ')" > outputs/proposal`)
	manifestPath, manifest, large := writeBundleWithLargeInput(t, spool)
	if _, err := adapter.Dispatch(manifestPath); err != nil {
		t.Fatal(err)
	}
	submission := waitSubmission(t, spool, manifest.DispatchID)
	body, err := os.ReadFile(filepath.Join(spool.SubmissionDir(manifest.DispatchID), submission.Outputs[0].Path))
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(body), fmt.Sprintf("%d bytes", len(large))) {
		t.Fatalf("runtime saw the wrong materialized base size (submission status %s):\n%s",
			submission.Status, body)
	}
}

