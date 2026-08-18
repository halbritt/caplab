package llm_test

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/halbritt/striatum-next/internal/backend"
	"github.com/halbritt/striatum-next/internal/backend/llm"
	spoolclose "github.com/halbritt/striatum-next/internal/spool"
)

func newSupervisor(t *testing.T, script string) (*llm.Supervisor, backend.Spool) {
	t.Helper()
	adapter, spool := newAdapter(t, script)
	if err := spool.EnsureLayout(); err != nil {
		t.Fatal(err)
	}
	return &llm.Supervisor{Config: adapter.Config, Spool: spool}, spool
}

// TestBudgetExpiryCommitsFailed (D0013.C4b, S3): the dispatch budget kills
// the confined runtime and best-effort commits a failed submission carrying
// diagnostics, an exhaust note naming the limit, and full attribution.
func TestBudgetExpiryCommitsFailed(t *testing.T) {
	requireDelegation(t)
	supervisor, spool := newSupervisor(t, `sleep 300`)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")
	manifest.Advisory = map[string]any{"abort_after_s": 0.5}

	started := time.Now()
	dir, err := supervisor.Run(manifest, filepath.Dir(manifestPath))
	if err != nil {
		t.Fatalf("Run() error = %v — budget expiry must commit, not error", err)
	}
	if elapsed := time.Since(started); elapsed > 10*time.Second {
		t.Fatalf("budget of 0.5s enforced only after %v", elapsed)
	}
	submission, err := backend.ReadSubmissionManifest(filepath.Join(dir, "manifest.json"))
	if err != nil {
		t.Fatal(err)
	}
	if submission.Status != "failed" {
		t.Fatalf("status = %s, want failed", submission.Status)
	}
	if !contains(submission.Diagnostics.Classes, "runtime_crash") {
		t.Fatalf("diagnostics = %v, want runtime_crash (no vocabulary growth)", submission.Diagnostics.Classes)
	}
	var budgetNamed bool
	for _, entry := range submission.Exhaust {
		if entry.Label == "budget" {
			budgetNamed = true
		}
	}
	if !budgetNamed {
		t.Fatal("exhaust does not name the exceeded budget")
	}
	if submission.Attribution.StartedAt == "" || submission.Attribution.EndedAt == "" {
		t.Fatal("attribution does not span the supervision")
	}
}

func TestV2DispatchCommitsV2Submission(t *testing.T) {
	requireDelegation(t)
	supervisor, spool := newSupervisor(t, `true`)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")
	oldDir := filepath.Dir(manifestPath)
	files := map[string][]byte{}
	for _, input := range manifest.Inputs {
		body, err := os.ReadFile(filepath.Join(oldDir, input.Path))
		if err != nil {
			t.Fatal(err)
		}
		files[input.Path] = body
	}
	manifest.SchemaVersion = 2
	manifest.Environment = backend.Environment{Entries: []backend.EnvironmentEntry{}}
	for i := range manifest.Expected {
		manifest.Expected[i].KindSchemaVersion = 1
		manifest.Expected[i].DerivedFromOutputs = []string{}
	}
	manifest.Lane.LaneID = "lane-v2"
	manifest.DispatchID, _ = backend.DispatchIDV2(manifest.Run.RunRef, manifest.Run.RunManifestHash, manifest.Lane.LaneID, manifest.Lane.Attempt)
	manifest.Submission.SpoolPath = "spool/submissions/" + manifest.DispatchID
	dispatchDir, err := backend.WriteDispatchBundle(spool, manifest, files)
	if err != nil {
		t.Fatal(err)
	}
	dir, err := supervisor.Run(manifest, dispatchDir)
	if err != nil {
		t.Fatal(err)
	}
	submission, err := backend.ReadSubmissionManifest(filepath.Join(dir, "manifest.json"))
	if err != nil {
		t.Fatal(err)
	}
	if submission.SchemaVersion != 2 {
		t.Fatalf("submission schema = %d, want dispatch schema 2", submission.SchemaVersion)
	}
	for _, exhaust := range submission.Exhaust {
		if exhaust.Kind == "" {
			t.Fatalf("v2 exhaust lacks exact kind: %+v", exhaust)
		}
	}
}

// TestInvocationLimitFeedsRelaunchLoop (D0013.C4a): expiry of clock 1 is a
// runtime_crash diagnostic into the relaunch loop, never a commit.
func TestInvocationLimitFeedsRelaunchLoop(t *testing.T) {
	requireDelegation(t)
	marker := filepath.Join(t.TempDir(), "attempted")
	supervisor, spool := newSupervisor(t, `if [ -f `+marker+` ]; then
mkdir -p outputs
cat > outputs/proposal <<'EOF'
# Proposal {#el:p}
recovered after limit kill
EOF
else
touch `+marker+`
sleep 300
fi`)
	// The limit clock starts before the confined init has exec'd the runtime,
	// so it must cover race-instrumented startup; attempt 0 burns it entirely.
	supervisor.WallClockLimit = 3 * time.Second
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")

	dir, err := supervisor.Run(manifest, filepath.Dir(manifestPath))
	if err != nil {
		t.Fatal(err)
	}
	submission, err := backend.ReadSubmissionManifest(filepath.Join(dir, "manifest.json"))
	if err != nil {
		t.Fatal(err)
	}
	if submission.Status != "complete" {
		t.Fatalf("status = %s, want complete after relaunch (diagnostics %v)", submission.Status, submission.Diagnostics.Classes)
	}
	if submission.Attribution.InternalRelaunch != 1 {
		t.Fatalf("internal_relaunches = %d, want 1", submission.Attribution.InternalRelaunch)
	}
	if !contains(submission.Diagnostics.Classes, "runtime_crash") {
		t.Fatalf("diagnostics = %v, want runtime_crash", submission.Diagnostics.Classes)
	}
}

// TestRelaunchRenderRefusalCommitsWhatStands: a relaunch whose corrective
// cannot be rendered (here: the crash corrective pushes the framing past the
// argv bound after full spill) must not evaporate attempt 0's real launch.
// Run commits a failed submission carrying exactly the launches that
// happened — attempt 0's closure, transcript, and diagnostics — with the
// render refusal in exhaust as renderr-1 and a context_exhausted class.
func TestRelaunchRenderRefusalCommitsWhatStands(t *testing.T) {
	requireDelegation(t)
	launches := filepath.Join(t.TempDir(), "launches")
	supervisor, spool := newSupervisor(t, `echo launched >> `+launches+`
kill -KILL $$`)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")

	// Pad the objective so attempt 0's rendered prompt sits exactly at the
	// argv bound minus one byte: attempt 0 renders and launches; attempt 1's
	// corrective section pushes the framing over the bound with nothing left
	// to spill (the tiny pinned input's path form is longer than its inline
	// form), so the relaunch render is refused deterministically in-band.
	workAbs, err := filepath.Abs(filepath.Join(spool.WorkspaceDir(manifest.DispatchID), "work"))
	if err != nil {
		t.Fatal(err)
	}
	base, err := llm.RenderPrompt(manifest, filepath.Dir(manifestPath), workAbs, "")
	if err != nil {
		t.Fatal(err)
	}
	pad := 128<<10 - 1 - len(base)
	if pad <= 0 {
		t.Fatalf("base prompt already %d bytes; cannot pad below the bound", len(base))
	}
	manifest.Objective.Summary += strings.Repeat("x", pad)

	dir, err := supervisor.Run(manifest, filepath.Dir(manifestPath))
	if err != nil {
		t.Fatalf("Run() error = %v — a relaunch render refusal must commit what stands, not discard it", err)
	}
	submission, err := backend.ReadSubmissionManifest(filepath.Join(dir, "manifest.json"))
	if err != nil {
		t.Fatal(err)
	}
	if submission.Status != "failed" {
		t.Fatalf("status = %s, want failed", submission.Status)
	}
	if got := len(submission.Attribution.Attempts); got != 1 {
		t.Fatalf("attempts = %d, want exactly the 1 launch that happened", got)
	}
	if submission.Attribution.Attempts[0].Attempt != 0 {
		t.Fatalf("committed closure ordinal = %d, want 0", submission.Attribution.Attempts[0].Attempt)
	}
	if submission.Attribution.InternalRelaunch != 0 {
		t.Fatalf("internal_relaunches = %d, want 0 (attempt 1 never launched)", submission.Attribution.InternalRelaunch)
	}
	labels := map[string]bool{}
	for _, entry := range submission.Exhaust {
		labels[entry.Label] = true
	}
	if !labels["transcript-0"] {
		t.Fatal("attempt 0's transcript evaporated from exhaust")
	}
	if !labels["renderr-1"] {
		t.Fatalf("render refusal not recorded as renderr-1; exhaust = %v", labels)
	}
	if labels["corrective-1"] {
		t.Fatal("corrective-1 pinned for a launch that never happened")
	}
	if !contains(submission.Diagnostics.Classes, "runtime_crash") {
		t.Fatalf("diagnostics = %v, want attempt 0's runtime_crash retained", submission.Diagnostics.Classes)
	}
	if !contains(submission.Diagnostics.Classes, "context_exhausted") {
		t.Fatalf("diagnostics = %v, want context_exhausted for the transport-bound refusal", submission.Diagnostics.Classes)
	}
	raw, err := os.ReadFile(launches)
	if err != nil {
		t.Fatal(err)
	}
	if got := strings.Count(string(raw), "launched"); got != 1 {
		t.Fatalf("runtime launched %d times, want 1 — the closure list must match the launches", got)
	}
}

func TestStdoutOutputMaterializesSingleRequiredReviewLedger(t *testing.T) {
	requireDelegation(t)
	supervisor, spool := newSupervisor(t, `cat <<'EOF'
Here is the review ledger.
`+"```json"+`
{"posture":"adversarial","verdict":"accept","summary":"ok","findings":[]}
`+"```"+`
EOF`)
	supervisor.Config.StdoutOutput = "single-required-output"
	manifestPath, manifest := writeBundle(t, spool, "review")
	manifest.Objective.Summary = "review the proposal"
	manifest.Expected = []backend.ExpectedOut{{
		OutputID: "review-ledger", Kind: "review-ledger", Identity: "rfcs/x/review-ledger",
		Placement: "stored", Required: true,
	}}

	dir, err := supervisor.Run(manifest, filepath.Dir(manifestPath))
	if err != nil {
		t.Fatal(err)
	}
	submission, err := backend.ReadSubmissionManifest(filepath.Join(dir, "manifest.json"))
	if err != nil {
		t.Fatal(err)
	}
	if submission.Status != "complete" {
		t.Fatalf("status = %s, want complete (diagnostics %v)", submission.Status, submission.Diagnostics.Classes)
	}
	body, err := os.ReadFile(filepath.Join(dir, submission.Outputs[0].Path))
	if err != nil {
		t.Fatal(err)
	}
	var ledger struct {
		Verdict string `json:"verdict"`
	}
	if err := json.Unmarshal(body, &ledger); err != nil {
		t.Fatalf("materialized body is not clean JSON: %v\n%s", err, body)
	}
	if ledger.Verdict != "accept" {
		t.Fatalf("verdict = %q, want accept", ledger.Verdict)
	}
	if strings.Contains(string(body), "```") || strings.Contains(string(body), "Here is") {
		t.Fatalf("stdout wrapper text leaked into output:\n%s", body)
	}
}

// TestCorrectiveDescribesOnlyThisAttemptsOutcome: each relaunch corrective
// is rebuilt from the attempt it describes. Attempt 0 crashes; attempt 1
// completes but with a shape error only; the corrective delivered to attempt
// 2 (pinned in exhaust as corrective-2) must carry the shape-error text and
// must NOT still claim the previous run crashed — it did not.
func TestCorrectiveDescribesOnlyThisAttemptsOutcome(t *testing.T) {
	requireDelegation(t)
	counter := filepath.Join(t.TempDir(), "counter")
	supervisor, spool := newSupervisor(t, `count=$(cat `+counter+` 2>/dev/null || echo 0)
echo $((count+1)) > `+counter+`
mkdir -p outputs
if [ "$count" = "0" ]; then
kill -KILL $$
elif [ "$count" = "1" ]; then
cat > outputs/proposal <<'EOF'
# Proposal without anchors
broken
EOF
else
cat > outputs/proposal <<'EOF'
# Proposal {#el:p}
repaired
EOF
fi`)
	supervisor.Config.InternalRetryMax = 2
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")

	dir, err := supervisor.Run(manifest, filepath.Dir(manifestPath))
	if err != nil {
		t.Fatal(err)
	}
	submission, err := backend.ReadSubmissionManifest(filepath.Join(dir, "manifest.json"))
	if err != nil {
		t.Fatal(err)
	}
	if submission.Status != "complete" {
		t.Fatalf("status = %s, want complete after the third attempt (diagnostics %v)",
			submission.Status, submission.Diagnostics.Classes)
	}
	if submission.Attribution.InternalRelaunch != 2 {
		t.Fatalf("internal_relaunches = %d, want 2", submission.Attribution.InternalRelaunch)
	}
	var correctivePath string
	for _, entry := range submission.Exhaust {
		if entry.Label == "corrective-2" {
			correctivePath = entry.Path
		}
	}
	if correctivePath == "" {
		t.Fatal("corrective-2 preimage missing from exhaust")
	}
	corrective, err := os.ReadFile(filepath.Join(dir, correctivePath))
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(corrective), "Output shape errors to repair") {
		t.Fatalf("corrective-2 does not describe attempt 1's shape errors:\n%s", corrective)
	}
	if strings.Contains(string(corrective), "The previous run crashed") {
		t.Fatalf("corrective-2 carries attempt 0's stale crash text — attempt 1 did not crash:\n%s", corrective)
	}
}

// TestRuntimeCrashRelaunches (S2b shape): a runtime that dies under a live
// supervisor feeds the relaunch loop — expected outcome, not defect.
func TestRuntimeCrashRelaunches(t *testing.T) {
	requireDelegation(t)
	marker := filepath.Join(t.TempDir(), "attempted")
	supervisor, spool := newSupervisor(t, `if [ -f `+marker+` ]; then
mkdir -p outputs
cat > outputs/proposal <<'EOF'
# Proposal {#el:p}
recovered after crash
EOF
else
touch `+marker+`
kill -KILL $$
fi`)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")

	dir, err := supervisor.Run(manifest, filepath.Dir(manifestPath))
	if err != nil {
		t.Fatal(err)
	}
	submission, err := backend.ReadSubmissionManifest(filepath.Join(dir, "manifest.json"))
	if err != nil {
		t.Fatal(err)
	}
	if submission.Status != "complete" {
		t.Fatalf("status = %s, want complete after crash relaunch", submission.Status)
	}
	if submission.Attribution.InternalRelaunch != 1 {
		t.Fatalf("internal_relaunches = %d, want 1", submission.Attribution.InternalRelaunch)
	}
}

// TestRelaunchSubmissionNeverMergesDisjointAttemptOutputs (D0007.C7/A2):
// each relaunch starts from a pristine workspace, so the committed submission
// must describe one attempt. Valid outputs from different attempts never
// combine into a complete result that no runtime invocation produced.
func TestRelaunchSubmissionNeverMergesDisjointAttemptOutputs(t *testing.T) {
	requireDelegation(t)
	marker := filepath.Join(t.TempDir(), "attempted")
	supervisor, spool := newSupervisor(t, `mkdir -p outputs
if [ -f `+marker+` ]; then
cat > outputs/right <<'EOF'
# Right {#el:right}
second attempt only
EOF
else
touch `+marker+`
cat > outputs/left <<'EOF'
# Left {#el:left}
first attempt only
EOF
fi`)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")
	manifest.Expected = []backend.ExpectedOut{
		{OutputID: "left", Kind: "proposal", Identity: "subjects/example/left", Placement: "stored", Required: true},
		{OutputID: "right", Kind: "proposal", Identity: "subjects/example/right", Placement: "stored", Required: true},
	}

	dir, err := supervisor.Run(manifest, filepath.Dir(manifestPath))
	if err != nil {
		t.Fatal(err)
	}
	submission, err := backend.ReadSubmissionManifest(filepath.Join(dir, "manifest.json"))
	if err != nil {
		t.Fatal(err)
	}
	if submission.Status != "partial" {
		t.Fatalf("status = %s, want partial: disjoint attempts must not combine", submission.Status)
	}
	if submission.Attribution.InternalRelaunch != 1 {
		t.Fatalf("internal_relaunches = %d, want 1", submission.Attribution.InternalRelaunch)
	}
	if len(submission.Outputs) != 2 {
		t.Fatalf("outputs = %d, want 2", len(submission.Outputs))
	}
	if submission.Outputs[0].OutputID != "left" || submission.Outputs[0].Status != "missing" {
		t.Fatalf("first output = %+v, want left missing from the final attempt", submission.Outputs[0])
	}
	if submission.Outputs[1].OutputID != "right" || submission.Outputs[1].Status != "present" {
		t.Fatalf("second output = %+v, want right present from the final attempt", submission.Outputs[1])
	}
}

// TestWakeFiresAfterCommitAndResidueReclaimed (D0013.C2/C7): commit, then
// the non-authoritative wake with "-trigger adapter_wake", then residue
// reclaim and exit.
func TestWakeFiresAfterCommitAndResidueReclaimed(t *testing.T) {
	record := filepath.Join(t.TempDir(), "wake-record")
	wake := fakeCLI(t, `echo "$@" >> `+record)
	supervisor, spool := newSupervisor(t, goodScript)
	supervisor.WakeCmd = []string{wake}
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")

	if _, err := supervisor.Run(manifest, filepath.Dir(manifestPath)); err != nil {
		t.Fatal(err)
	}
	raw, err := os.ReadFile(record)
	if err != nil {
		t.Fatalf("wake never fired: %v", err)
	}
	if lines := strings.Count(string(raw), "\n"); lines != 1 {
		t.Fatalf("wake fired %d times, want 1", lines)
	}
	if !strings.Contains(string(raw), "-trigger adapter_wake") {
		t.Fatalf("wake argv = %q, want -trigger adapter_wake appended", raw)
	}
	if _, err := os.Stat(spool.WorkspaceDir(manifest.DispatchID)); !os.IsNotExist(err) {
		t.Fatal("workspace residue survived self-termination")
	}
	if _, err := os.Stat(spool.AdvisoryDir(manifest.DispatchID)); !os.IsNotExist(err) {
		t.Fatal("advisory residue survived self-termination")
	}
	if _, err := os.Stat(spool.SubmissionDir(manifest.DispatchID)); err != nil {
		t.Fatal("reclaim touched the committed submission")
	}
}

// TestWakeLeaseBusyRetriesBoundedThenAbandons (D0013.C7): exit 4 retries on
// the bounded schedule; exhaustion abandons safely with the commit standing.
func TestWakeLeaseBusyRetriesBoundedThenAbandons(t *testing.T) {
	record := filepath.Join(t.TempDir(), "wake-record")
	wake := fakeCLI(t, `echo tried >> `+record+`
exit 4`)
	supervisor, spool := newSupervisor(t, goodScript)
	supervisor.WakeCmd = []string{wake}
	supervisor.WakeRetries = []time.Duration{10 * time.Millisecond, 10 * time.Millisecond}
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")

	dir, err := supervisor.Run(manifest, filepath.Dir(manifestPath))
	if err != nil {
		t.Fatalf("wake exhaustion must not fail the supervision: %v", err)
	}
	raw, _ := os.ReadFile(record)
	if tries := strings.Count(string(raw), "tried"); tries != 3 {
		t.Fatalf("wake tried %d times, want 3 (initial + 2 retries)", tries)
	}
	if _, err := os.Stat(dir); err != nil {
		t.Fatal("submission missing after wake abandonment")
	}
}

// TestWakeAbsentSkipsEntirely: no wake argv, no wake — lawful; the standing
// timer is the liveness floor.
func TestWakeAbsentSkipsEntirely(t *testing.T) {
	supervisor, spool := newSupervisor(t, goodScript)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")
	if _, err := supervisor.Run(manifest, filepath.Dir(manifestPath)); err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(spool.SubmissionDir(manifest.DispatchID)); err != nil {
		t.Fatal("submission missing")
	}
}

// TestRunSuccessCommitsRuntimeExitReport (stalls-need-no-judgment@3, clause
// 2, emission half): a cleanly completed dispatch traverses the terminal
// emission funnel and commits a runtime_exit report — the permitted reason
// for the supervisor observing its runtime leave.
func TestRunSuccessCommitsRuntimeExitReport(t *testing.T) {
	requireDelegation(t)
	supervisor, spool := newSupervisor(t, goodScript)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")

	if _, err := supervisor.Run(manifest, filepath.Dir(manifestPath)); err != nil {
		t.Fatal(err)
	}
	report, err := backend.ReadTerminalReport(spool, manifest.DispatchID)
	if err != nil {
		t.Fatal(err)
	}
	if report == nil {
		t.Fatal("no terminal report committed for a clean completed dispatch")
	}
	if report.ExitReason != spoolclose.RuntimeExit {
		t.Fatalf("exit_reason = %q, want runtime_exit", report.ExitReason)
	}
}

// TestBudgetExpiryCommitsBudgetExpiryReport (stalls-need-no-judgment@3,
// clause 2): the dispatch budget breaking the relaunch loop classifies
// distinctly as budget_expiry, never the generic runtime_exit bucket.
func TestBudgetExpiryCommitsBudgetExpiryReport(t *testing.T) {
	requireDelegation(t)
	supervisor, spool := newSupervisor(t, `sleep 300`)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")
	manifest.Advisory = map[string]any{"abort_after_s": 0.5}

	if _, err := supervisor.Run(manifest, filepath.Dir(manifestPath)); err != nil {
		t.Fatalf("Run() error = %v — budget expiry must commit, not error", err)
	}
	report, err := backend.ReadTerminalReport(spool, manifest.DispatchID)
	if err != nil {
		t.Fatal(err)
	}
	if report == nil {
		t.Fatal("no terminal report committed for a budget-expired dispatch")
	}
	if report.ExitReason != spoolclose.BudgetExpiry {
		t.Fatalf("exit_reason = %q, want budget_expiry", report.ExitReason)
	}
}

// TestFinalAttemptClampedByBudgetReportsBudgetExpiry
// (stalls-need-no-judgment@3, clause 2; TRL2-P02-01 regression): invoke
// clamps its wait to the remaining dispatch budget, so a timed-out
// invocation and a budget-exhausted dispatch are indistinguishable from
// runErr alone. When the clamped invocation IS the last permitted attempt,
// the loop falls out with no further iteration to re-check the deadline at
// the top — the fallback must not misreport this as relaunch_exhausted, a
// fact reserved for genuine attempt-capacity exhaustion.
func TestFinalAttemptClampedByBudgetReportsBudgetExpiry(t *testing.T) {
	requireDelegation(t)
	supervisor, spool := newSupervisor(t, `sleep 300`)
	supervisor.Config.InternalRetryMax = 0
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")
	manifest.Advisory = map[string]any{"abort_after_s": 0.5}

	dir, err := supervisor.Run(manifest, filepath.Dir(manifestPath))
	if err != nil {
		t.Fatalf("Run() error = %v — a budget-clamped final attempt must commit, not error", err)
	}
	submission, err := backend.ReadSubmissionManifest(filepath.Join(dir, "manifest.json"))
	if err != nil {
		t.Fatal(err)
	}
	if submission.Attribution.InternalRelaunch != 0 {
		t.Fatalf("internal_relaunches = %d, want 0 (only one attempt was ever permitted)", submission.Attribution.InternalRelaunch)
	}
	report, err := backend.ReadTerminalReport(spool, manifest.DispatchID)
	if err != nil {
		t.Fatal(err)
	}
	if report == nil {
		t.Fatal("no terminal report committed for a budget-clamped final attempt")
	}
	if report.ExitReason != spoolclose.BudgetExpiry {
		t.Fatalf("exit_reason = %q, want budget_expiry — the sole permitted invocation was clamped by the remaining dispatch budget, not exhausted for attempt capacity", report.ExitReason)
	}
}

// TestRelaunchExhaustionCommitsRelaunchExhaustedReport
// (stalls-need-no-judgment@3, clause 2): a runtime that never produces a
// shape-valid required output across every internal attempt exhausts the
// relaunch loop without ever hitting the dispatch budget, and the funnel
// classifies that distinctly from both budget_expiry and runtime_exit.
func TestRelaunchExhaustionCommitsRelaunchExhaustedReport(t *testing.T) {
	requireDelegation(t)
	supervisor, spool := newSupervisor(t, `mkdir -p outputs
cat > outputs/proposal <<'EOF'
no element anchors here
EOF`)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")

	dir, err := supervisor.Run(manifest, filepath.Dir(manifestPath))
	if err != nil {
		t.Fatal(err)
	}
	submission, err := backend.ReadSubmissionManifest(filepath.Join(dir, "manifest.json"))
	if err != nil {
		t.Fatal(err)
	}
	if submission.Status != "failed" {
		t.Fatalf("status = %s, want failed after every attempt shape-refuses", submission.Status)
	}
	report, err := backend.ReadTerminalReport(spool, manifest.DispatchID)
	if err != nil {
		t.Fatal(err)
	}
	if report == nil {
		t.Fatal("no terminal report committed for a relaunch-exhausted dispatch")
	}
	if report.ExitReason != spoolclose.RelaunchExhausted {
		t.Fatalf("exit_reason = %q, want relaunch_exhausted", report.ExitReason)
	}
}

// TestTerminalReportCarriesTheManifestLaneID: the committed report is keyed
// by the dispatch manifest's lane id — the same lane id the driver's drain
// matches against — never the dispatch id or an adapter-internal identifier.
func TestTerminalReportCarriesTheManifestLaneID(t *testing.T) {
	requireDelegation(t)
	supervisor, spool := newSupervisor(t, goodScript)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")

	if _, err := supervisor.Run(manifest, filepath.Dir(manifestPath)); err != nil {
		t.Fatal(err)
	}
	raw, err := os.ReadFile(spool.ReportPath(manifest.DispatchID))
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(raw), `"lane_id": "`+manifest.Lane.LaneID+`"`) {
		t.Fatalf("committed report does not carry the manifest lane id %q:\n%s", manifest.Lane.LaneID, raw)
	}
}

// TestTerminalReportCommittedBeforeWakeFires (stalls-need-no-judgment@3,
// clause 2): the funnel commits before Run's wake, so a woken Driver can
// never scan ahead of the report that is supposed to accelerate its drain.
func TestTerminalReportCommittedBeforeWakeFires(t *testing.T) {
	requireDelegation(t)
	supervisor, spool := newSupervisor(t, goodScript)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")
	marker := filepath.Join(t.TempDir(), "wake-saw-report")
	reportPath := spool.ReportPath(manifest.DispatchID)
	wake := fakeCLI(t, `if [ -f `+reportPath+` ]; then echo present > `+marker+`; else echo missing > `+marker+`; fi`)
	supervisor.WakeCmd = []string{wake}

	if _, err := supervisor.Run(manifest, filepath.Dir(manifestPath)); err != nil {
		t.Fatal(err)
	}
	raw, err := os.ReadFile(marker)
	if err != nil {
		t.Fatalf("wake never fired: %v", err)
	}
	if got := strings.TrimSpace(string(raw)); got != "present" {
		t.Fatalf("wake observed terminal report state %q, want present before the wake fires", got)
	}
}

// TestAttemptZeroSetupErrorCommitsRelaunchExhaustedReport
// (stalls-need-no-judgment@3, clause 2; TRL2-P02-02 regression): an
// attempt-0 render refusal (here, an argv-mode NUL byte) never reaches a
// relaunch-loop verdict and never starts a runtime invocation, but it is
// still a controlled post-acceptance supervisor exit, not an uncontrolled
// kill — the process is alive and running the funnel. emitTerminalReport
// must therefore still make its one best-effort commit; runtime_exit would
// misreport it (no runtime ever ran), so the truthful permitted reason is
// relaunch_exhausted: no launch produced a result and no further launch will
// be attempted this dispatch. Run still propagates the error to its caller,
// still commits no submission, and wake still never fires over it — only
// the report changes.
func TestAttemptZeroSetupErrorCommitsRelaunchExhaustedReport(t *testing.T) {
	supervisor, spool := newSupervisor(t, goodScript)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")
	manifest.Objective.Summary = "bad\x00null"
	marker := filepath.Join(t.TempDir(), "wake-fired")
	supervisor.WakeCmd = []string{fakeCLI(t, `touch `+marker)}

	if _, err := supervisor.Run(manifest, filepath.Dir(manifestPath)); err == nil {
		t.Fatal("Run() succeeded despite an unrenderable attempt-0 prompt")
	}
	report, err := backend.ReadTerminalReport(spool, manifest.DispatchID)
	if err != nil {
		t.Fatal(err)
	}
	if report == nil {
		t.Fatal("no terminal report committed for a controlled attempt-0 setup error")
	}
	if report.ExitReason != spoolclose.RelaunchExhausted {
		t.Fatalf("exit_reason = %q, want relaunch_exhausted — no runtime ever launched this dispatch", report.ExitReason)
	}
	if _, err := os.Stat(marker); err == nil {
		t.Fatal("wake fired after an execute error; Run must propagate it without waking")
	}
	if _, err := os.Stat(spool.SubmissionDir(manifest.DispatchID)); !os.IsNotExist(err) {
		t.Fatal("attempt-0 setup error must not commit a submission")
	}
}

// TestWakeSurvivesGroupDirectedCourtesyAbort (stalls-need-no-judgment@3,
// clause 2, plus D0013.C5): the detached supervisor is the leader of its own
// signalable kill domain (Setsid at fork), and a woken Driver that finds
// this lane reported terminal courtesy-aborts that exact domain by
// SIGTERMing -pgid (session.go's courtesyAbort, via adapter.go's Abort).
// Before wake() isolated its exec'd process into its own process group,
// that self-directed group signal killed the wake-launched process along
// with the supervisor that named it, before either could finish.
//
// This drives a real detached supervisor (forked by Adapter.Dispatch,
// Setsid and all — the same path production uses) and has the fake wake
// command replay exactly that courtesy-abort signal against the real kill
// domain named by the on-disk Supervisor Hint, then perform the same
// residue reclaim the driver's Abort would on success. The wake command
// must survive the group signal and finish that reclaim even though the
// original supervisor process it named does not survive it.
func TestWakeSurvivesGroupDirectedCourtesyAbort(t *testing.T) {
	adapter, spool := newAdapter(t, goodScript)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")

	workspaceDir := spool.WorkspaceDir(manifest.DispatchID)
	advisoryDir := spool.AdvisoryDir(manifest.DispatchID)
	hintFile := filepath.Join(advisoryDir, "supervisor.json")
	marker := filepath.Join(t.TempDir(), "wake-survived")

	wake := fakeCLI(t, `
pgid=$(grep -o '"pgid":[0-9]*' `+hintFile+` | cut -d: -f2)
pid=$(grep -o '"pid":[0-9]*' `+hintFile+` | cut -d: -f2)
kill -TERM -"$pgid" 2>/dev/null
tries=0
while kill -0 "$pid" 2>/dev/null; do
tries=$((tries+1))
if [ "$tries" -ge 100 ]; then break; fi
sleep 0.05
done
rm -rf `+workspaceDir+` `+advisoryDir+`
touch `+marker+`
`)
	adapter.WakeCmd = []string{wake}

	if _, err := adapter.Dispatch(manifestPath); err != nil {
		t.Fatal(err)
	}
	waitSubmission(t, spool, manifest.DispatchID)

	deadline := time.Now().Add(10 * time.Second)
	for time.Now().Before(deadline) {
		if _, err := os.Stat(marker); err == nil {
			break
		}
		time.Sleep(20 * time.Millisecond)
	}
	if _, err := os.Stat(marker); err != nil {
		t.Fatal("wake command never completed — it shares the supervisor's kill domain and was killed by the courtesy-abort group signal")
	}
	if _, err := os.Stat(workspaceDir); !os.IsNotExist(err) {
		t.Fatal("workspace residue survived the courtesy-abort race")
	}
	if _, err := os.Stat(advisoryDir); !os.IsNotExist(err) {
		t.Fatal("advisory residue survived the courtesy-abort race")
	}
}

// TestPartialOutputEvidenceCollectedBeforeReset
// (partials-collect-before-discard, stalls-need-no-judgment@3): attempt 0
// leaves a shape-invalid output on disk; the pristine per-attempt reset
// before attempt 1 launches would otherwise destroy it with no trace. The
// same-attempt on-disk content must survive into the committed submission's
// exhaust, labeled with the exact attempt it came from — evidence only,
// never promoted into outcome.outputs or the submission's own result.
func TestPartialOutputEvidenceCollectedBeforeReset(t *testing.T) {
	requireDelegation(t)
	marker := filepath.Join(t.TempDir(), "attempted")
	supervisor, spool := newSupervisor(t, `mkdir -p outputs
if [ -f `+marker+` ]; then
cat > outputs/proposal <<'EOF'
# Proposal {#el:p}
repaired
EOF
else
touch `+marker+`
cat > outputs/proposal <<'EOF'
# Proposal without anchors
broken beyond shape
EOF
fi`)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")

	dir, err := supervisor.Run(manifest, filepath.Dir(manifestPath))
	if err != nil {
		t.Fatal(err)
	}
	submission, err := backend.ReadSubmissionManifest(filepath.Join(dir, "manifest.json"))
	if err != nil {
		t.Fatal(err)
	}
	if submission.Status != "complete" {
		t.Fatalf("status = %s, want complete after shape repair (diagnostics %v)", submission.Status, submission.Diagnostics.Classes)
	}
	var evidencePath string
	labels := make([]string, 0, len(submission.Exhaust))
	for _, entry := range submission.Exhaust {
		labels = append(labels, entry.Label)
		if entry.Label == "partial-0-proposal" {
			evidencePath = entry.Path
		}
	}
	if evidencePath == "" {
		t.Fatalf("attempt 0's discarded output missing from exhaust as partial-0-proposal; exhaust labels = %v", labels)
	}
	evidence, err := os.ReadFile(filepath.Join(dir, evidencePath))
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(evidence), "broken beyond shape") {
		t.Fatalf("collected evidence = %q, want attempt 0's discarded body", evidence)
	}
	if submission.Outputs[0].OutputID != "proposal" || submission.Outputs[0].Status != "present" {
		t.Fatalf("final output = %+v, want proposal present from attempt 1 only", submission.Outputs[0])
	}
	finalBody, err := os.ReadFile(filepath.Join(dir, submission.Outputs[0].Path))
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(string(finalBody), "broken beyond shape") {
		t.Fatal("discarded attempt 0 content leaked into the committed result")
	}
}

// TestTerminalReportAdmitsSupervisorLogTail (stalls-need-no-judgment@3,
// clause 2 evidence rider): the committed terminal report's supervisor_tail
// carries the detached supervisor's own stdio log, admitted as evidence
// alongside the exit reason.
func TestTerminalReportAdmitsSupervisorLogTail(t *testing.T) {
	supervisor, spool := newSupervisor(t, goodScript)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")

	logPath := filepath.Join(spool.WorkspaceDir(manifest.DispatchID), "supervisor.log")
	if err := os.MkdirAll(filepath.Dir(logPath), 0o700); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(logPath, []byte("synthetic supervisor stdio\n"), 0o600); err != nil {
		t.Fatal(err)
	}

	if _, err := supervisor.Run(manifest, filepath.Dir(manifestPath)); err != nil {
		t.Fatal(err)
	}
	report, err := backend.ReadTerminalReport(spool, manifest.DispatchID)
	if err != nil {
		t.Fatal(err)
	}
	if report == nil {
		t.Fatal("no terminal report committed")
	}
	if !strings.Contains(report.SupervisorTail, "synthetic supervisor stdio") {
		t.Fatalf("supervisor_tail = %q, want it to admit the supervisor log content", report.SupervisorTail)
	}
}

// TestSupervisorLogRetainedAtDriverVisibleHome (schema/exit_report.yaml
// supervisor_log_retention_seconds): reclaim unlinks the workspace tree
// holding the detached supervisor's only log copy, so Run must retain it at
// Spool.RetainedLogPath first — the driver-visible, on-disk home the log
// survives abandonment under.
func TestSupervisorLogRetainedAtDriverVisibleHome(t *testing.T) {
	supervisor, spool := newSupervisor(t, goodScript)
	manifestPath, manifest := writeBundle(t, spool, "proposal-generation")

	logPath := filepath.Join(spool.WorkspaceDir(manifest.DispatchID), "supervisor.log")
	if err := os.MkdirAll(filepath.Dir(logPath), 0o700); err != nil {
		t.Fatal(err)
	}
	body := []byte("retained supervisor stdio\n")
	if err := os.WriteFile(logPath, body, 0o600); err != nil {
		t.Fatal(err)
	}

	if _, err := supervisor.Run(manifest, filepath.Dir(manifestPath)); err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(spool.WorkspaceDir(manifest.DispatchID)); !os.IsNotExist(err) {
		t.Fatal("workspace residue (and the log's only copy) survived reclaim")
	}
	retained, err := os.ReadFile(spool.RetainedLogPath(manifest.DispatchID))
	if err != nil {
		t.Fatalf("retained supervisor log missing: %v", err)
	}
	if string(retained) != string(body) {
		t.Fatalf("retained log = %q, want %q", retained, body)
	}
}

