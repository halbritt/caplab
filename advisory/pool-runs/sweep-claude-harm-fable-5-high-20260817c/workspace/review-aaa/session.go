package driver

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"github.com/halbritt/striatum-next/internal/admission"
	"github.com/halbritt/striatum-next/internal/backend"
	"github.com/halbritt/striatum-next/internal/changeset"
	"github.com/halbritt/striatum-next/internal/gate"
	"github.com/halbritt/striatum-next/internal/gitanchor"
	"github.com/halbritt/striatum-next/internal/records"
	"github.com/halbritt/striatum-next/internal/scheduler"
	spoolclose "github.com/halbritt/striatum-next/internal/spool"
	"github.com/halbritt/striatum-next/internal/store"
	"github.com/halbritt/striatum-next/internal/workgraph"
)

// ErrDriveLeaseBusy means another drive session holds the lease (exit 4).
var ErrDriveLeaseBusy = errors.New("driver: drive lease busy")

// Adapter is the driver-facing slice of one execution backend adapter: the
// dispatch verb (exit-0-equivalent nil error is durable acceptance, never a
// wait for execution) and the advisory abort verb the session issues as
// courtesy under the winner rule. Everything else about the backend lives
// below the seam (RFC 0007).
type Adapter interface {
	Dispatch(manifestPath string) (string, error)
	Abort(dispatchID string) error
}

// Session executes drive sessions over one Graph Store.
type Session struct {
	Graph          *store.Graph
	Spool          backend.Spool
	Adapters       map[string]Adapter
	Catalog        Catalog
	Policy         Policy
	Kinds          map[string]store.ArtifactKind
	Backends       []scheduler.Declaration
	Checks         *CheckWorld
	FailureClasses admission.Catalog
	SealKeys       map[string][]byte
	// Backlog is the declared scheduling backlog (policy/backlog.yaml) the
	// post-quiescence schedule phase consults
	// (planner-auto-schedules-the-backlog@1). Read-only Principal policy
	// (C1): the session never mutates it and holds no path back to its file.
	Backlog         Backlog
	Now             func() time.Time
	Instance        string
	Trigger         string
	maxIterations   int
	abandonedInThis int
	// backlogIssuedInThis counts planner-scheduled requests appended during
	// the current drive invocation: the per-drive cap (C7) spans every
	// re-entry of the schedule phase within one Drive, and resets when the
	// next Drive begins.
	backlogIssuedInThis int

	// Incremental fold: the session folds the ledger once and applies only
	// the appended tail thereafter (fold-equivalence guarded). Derived,
	// destroyable — a rolled or truncated segment forces a full refold.
	foldState *State
	foldScan  store.TailScan
}

// Report summarizes one drive session.
type Report struct {
	Quiescence   string         `json:"quiescence_reason"`
	Drained      []string       `json:"drained"`
	ActionCounts map[string]int `json:"action_counts"`
	NextHorizon  string         `json:"next_horizon,omitempty"`
	Notes        []string       `json:"notes,omitempty"`
	SessionSeq   uint64         `json:"session_seq"`
}

// Blocked reports whether the session ended quiescent-blocked (exit 5).
func (r Report) Blocked() bool {
	switch r.Quiescence {
	case "satisfied", "idle":
		return false
	}
	return true
}

// Drive runs one drive session to quiescence: drain, progress, mark, plan,
// dispatch, sweep — deterministic over (graph, ledger, catalog, policy).
func (s *Session) Drive() (Report, error) {
	report := Report{ActionCounts: map[string]int{}}
	if s.Now == nil {
		s.Now = time.Now
	}
	if s.Instance == "" {
		s.Instance = "drive"
	}
	if s.Trigger == "" {
		s.Trigger = "principal"
	}
	if s.maxIterations == 0 {
		s.maxIterations = 64
	}
	// The per-drive planner cap (C7) spans every re-entry of the schedule
	// phase within this Drive and resets when the next Drive begins.
	s.backlogIssuedInThis = 0

	lease, err := s.Graph.TryDriveLease()
	if err != nil {
		if errors.Is(err, store.ErrLockBusy) {
			return report, ErrDriveLeaseBusy
		}
		return report, err
	}
	defer lease.Unlock()

	// Cheap tail check at session start.
	if _, err := s.Graph.RecoverActiveSegment(); err != nil {
		return report, err
	}
	startState, err := s.fold()
	if err != nil {
		return report, err
	}
	cursorStart := startState.LastSeq

	for iteration := 0; ; iteration++ {
		if iteration >= s.maxIterations {
			return report, errors.New("driver: session did not quiesce")
		}
		actions := 0
		count := func(phase string, n int) {
			if n > 0 {
				report.ActionCounts[phase] += n
				actions += n
			}
		}
		n, err := s.drain(&report)
		if err != nil {
			return report, err
		}
		count("drain", n)
		if n, err = s.progress(&report); err != nil {
			return report, err
		}
		count("progress", n)
		if n, err = s.mark(); err != nil {
			return report, err
		}
		count("mark", n)
		if n, err = s.plan(&report); err != nil {
			return report, err
		}
		count("plan", n)
		if n, err = s.dispatch(&report); err != nil {
			return report, err
		}
		count("dispatch", n)
		if n, err = s.sweep(&report); err != nil {
			return report, err
		}
		count("sweep", n)
		if actions == 0 {
			// Post-work spool re-scan closes the wake-drop race.
			pending, err := s.undrainedSubmissions()
			if err != nil {
				return report, err
			}
			if len(pending) == 0 {
				// Active advancement is quiescent for this invocation: the
				// planner-scheduling phase consults the declared backlog
				// (C2). Fresh issuance re-enters the loop so the scheduled
				// requests plan and dispatch in this same session; the next
				// quiescence's re-consultation is a no-op by construction —
				// every issued entry now has an active request (C4, C10).
				scheduled, err := s.schedule()
				if err != nil {
					return report, err
				}
				if scheduled == 0 {
					break
				}
				count("schedule", scheduled)
			}
		}
	}

	state, err := s.fold()
	if err != nil {
		return report, err
	}
	report.Quiescence = s.quiescenceReason(state)
	report.NextHorizon = s.nextHorizon(state)

	sessionSeq, err := s.appendSessionRecord(state, cursorStart, report)
	if err != nil {
		return report, err
	}
	report.SessionSeq = sessionSeq
	if err := s.writeProjections(state, report); err != nil {
		return report, err
	}
	return report, nil
}

func (s *Session) fold() (*State, error) {
	if s.foldState != nil {
		tail, next, ok, err := s.Graph.ScanRecords(s.foldScan)
		if err != nil {
			return nil, err
		}
		if ok {
			s.foldState.Apply(tail)
			s.foldScan = next
			return s.foldState, nil
		}
		s.foldState = nil
	}
	all, scan, _, err := s.Graph.ScanRecords(store.TailScan{})
	if err != nil {
		return nil, err
	}
	s.foldState = Fold(all)
	s.foldScan = scan
	return s.foldState, nil
}

// CurrentStatus recomputes the status projection on read: derived,
// rebuildable, never stored authority.
func (s *Session) CurrentStatus() (Status, error) {
	if s.Now == nil {
		s.Now = time.Now
	}
	state, err := s.fold()
	if err != nil {
		return Status{}, err
	}
	return BuildStatus(state, s.Catalog, s.acceptanceQueue(state), Report{}, s.Now().UTC()), nil
}

func (s *Session) append(recordType, component string, causes []uint64, payload map[string]any) (store.AppendResult, error) {
	return s.appendSchema(recordType, 1, component, causes, payload)
}

func (s *Session) appendSchema(recordType string, schemaVersion uint16, component string, causes []uint64, payload map[string]any) (store.AppendResult, error) {
	if causes == nil {
		causes = []uint64{}
	}
	return s.Graph.AppendRecord(store.AppendOptions{
		Type:          recordType,
		SchemaVersion: schemaVersion,
		Actor:         records.Actor{Component: component, Instance: s.Instance},
		Causes:        causes,
		Payload:       payload,
		WrittenAt:     s.Now(),
	})
}

func (s *Session) appendPassRunClosedV2(causes []uint64, payload map[string]any) (store.AppendResult, error) {
	return s.appendSchema("pass_run_closed", 2, "driver", causes, payload)
}

// --- drain ---

type pendingSubmission struct {
	dispatchID string
	dir        string
	manifest   backend.SubmissionManifest
}

func (s *Session) undrainedSubmissions() ([]pendingSubmission, error) {
	state, err := s.fold()
	if err != nil {
		return nil, err
	}
	submissionsDir := filepath.Join(s.Spool.Root, "spool", "submissions")
	entries, err := os.ReadDir(submissionsDir)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return nil, nil
		}
		return nil, err
	}
	var pending []pendingSubmission
	for _, entry := range entries {
		if !entry.IsDir() {
			continue
		}
		dir := filepath.Join(submissionsDir, entry.Name())
		manifest, err := backend.ReadSubmissionManifest(filepath.Join(dir, "manifest.json"))
		if err != nil {
			continue
		}
		if state.Drained[entry.Name()] {
			// Drained is a ledger fact for the dispatch id. Failed or partial
			// submissions without an actionable terminal report can leave their
			// run open until the horizon backstop; re-draining them would keep
			// replaying the same bundle inside one drive session.
			continue
		}
		pending = append(pending, pendingSubmission{dispatchID: entry.Name(), dir: dir, manifest: manifest})
	}
	// Canonical drain order: dispatch_id, then manifest end time.
	sort.Slice(pending, func(i, j int) bool {
		if pending[i].dispatchID != pending[j].dispatchID {
			return pending[i].dispatchID < pending[j].dispatchID
		}
		return pending[i].manifest.Attribution.EndedAt < pending[j].manifest.Attribution.EndedAt
	})
	return pending, nil
}

func (s *Session) drain(report *Report) (int, error) {
	pending, err := s.undrainedSubmissions()
	if err != nil {
		return 0, err
	}
	actions := 0
	for _, item := range pending {
		state, err := s.fold()
		if err != nil {
			return actions, err
		}
		if err := item.manifest.VerifySealWith(s.SealKeys[item.manifest.Attribution.BackendID]); err != nil {
			if _, err := s.append("submission_refused", "admission", nil, map[string]any{
				"dispatch_id": item.dispatchID,
				"run_ref":     int64(item.manifest.RunRef),
				"lane_id":     item.manifest.LaneID,
				"attempt":     item.manifest.Attempt,
				"reason":      string(store.RefusalSealInvalid),
				"detail":      err.Error(),
			}); err != nil {
				return actions, err
			}
			report.Drained = append(report.Drained, item.dispatchID)
			actions++
			continue
		}
		sub, err := s.submissionFromBundle(state, item)
		if err != nil {
			return actions, err
		}
		result, err := s.Graph.Admit(sub, store.AdmitOptions{Kinds: s.Kinds, Now: s.Now, Instance: s.Instance})
		if err != nil {
			return actions, err
		}
		if result.BundleRefusal == "" && !result.SubmittedLate {
			switch item.manifest.Status {
			case "complete", "":
				payload := map[string]any{"run_ref": int64(sub.RunRef), "outcome": "submitted"}
				if _, err := s.append("pass_run_closed", "driver", []uint64{sub.RunRef}, payload); err != nil {
					return actions, err
				}
				// Integration losers surface as typed conflict records (§7.3).
				if n, err := s.surfaceIntegrationConflicts(sub.RunRef, item.dir); err != nil {
					return actions, err
				} else {
					actions += n
				}
			case "partial", "failed":
				// Failed and partial integration submissions may still carry typed
				// conflict exhaust. Surface it once, even when no terminal report is
				// available to close the run before the horizon.
				if n, err := s.surfaceIntegrationConflicts(sub.RunRef, item.dir); err != nil {
					return actions, err
				} else {
					actions += n
				}
				state, err := s.fold()
				if err != nil {
					return actions, err
				}
				run := state.Runs[sub.RunRef]
				terminal, err := s.loadTerminalReport(item.dispatchID)
				if err != nil {
					return actions, err
				}
				if closed, err := s.closeRunFromTerminalReport(state, run, terminal, s.Now().UTC(), report); err != nil {
					return actions, err
				} else if closed {
					actions++
				}
			}
		}
		report.Drained = append(report.Drained, item.dispatchID)
		actions++
	}
	reportActions, err := s.drainTerminalReports(report)
	if err != nil {
		return actions, err
	}
	return actions + reportActions, nil
}

func missingOutputs(manifest backend.SubmissionManifest) []any {
	var missing []any
	for _, output := range manifest.Outputs {
		if output.Status == "missing" {
			missing = append(missing, output.OutputID)
		}
	}
	if missing == nil {
		missing = []any{}
	}
	return missing
}

func (s *Session) drainTerminalReports(report *Report) (int, error) {
	state, err := s.fold()
	if err != nil {
		return 0, err
	}
	actions := 0
	for _, runSeq := range sortedRunSeqs(state) {
		state, err = s.fold()
		if err != nil {
			return actions, err
		}
		run := state.Runs[runSeq]
		if run == nil || !run.Open() || run.DispatchID == "" {
			continue
		}
		terminal, err := s.loadTerminalReport(run.DispatchID)
		if err != nil {
			return actions, err
		}
		closed, err := s.closeRunFromTerminalReport(state, run, terminal, s.Now().UTC(), report)
		if err != nil {
			return actions, err
		}
		if closed {
			report.Drained = append(report.Drained, run.DispatchID)
			actions++
		}
	}
	return actions, nil
}

func (s *Session) terminalReportPath(dispatchID string) string {
	return filepath.Join(s.Spool.Root, "spool", "reports", dispatchID, "terminal_report.json")
}

func (s *Session) retainedSupervisorLogPath(dispatchID string) string {
	return filepath.Join(s.Spool.Root, "spool", "retained-logs", dispatchID, "supervisor.log")
}

func (s *Session) loadTerminalReport(dispatchID string) (*spoolclose.Report, error) {
	if dispatchID == "" {
		return nil, nil
	}
	raw, err := os.ReadFile(s.terminalReportPath(dispatchID))
	if err != nil {
		return nil, nil
	}
	var report spoolclose.Report
	if err := json.Unmarshal(raw, &report); err != nil {
		return nil, nil
	}
	switch report.ExitReason {
	case spoolclose.BudgetExpiry, spoolclose.RelaunchExhausted, spoolclose.RuntimeExit:
		return &report, nil
	default:
		return nil, nil
	}
}

func (s *Session) closeRunFromTerminalReport(state *State, run *RunState, terminal *spoolclose.Report, now time.Time, report *Report) (bool, error) {
	if run == nil || !run.Open() || terminal == nil {
		return false, nil
	}
	decision := spoolclose.ScanClose(s.laneForReport(state, run, terminal, now))
	if !decision.Close {
		return false, nil
	}
	switch decision.Mode {
	case spoolclose.ModeProvisionalAbandon, spoolclose.ModeReportedTerminal:
	default:
		return false, nil
	}
	if _, err := s.closeFromScan(run, decision, terminal, now); err != nil {
		return false, err
	}
	s.courtesyAbort(run, report)
	return true, nil
}

func (s *Session) laneForReport(state *State, run *RunState, terminal *spoolclose.Report, now time.Time) spoolclose.Lane {
	return spoolclose.Lane{
		LaneID:         run.LaneID,
		AgeSeconds:     durationSecondsInt(observedActive(run, now)),
		HorizonSeconds: durationSecondsInt(s.Policy.DeadlineFor(run.DeadlineClass)),
		IsWinner:       state.LaneWon(run),
		Report:         terminal,
	}
}

func (s *Session) closeFromScan(run *RunState, decision spoolclose.CloseDecision, terminal *spoolclose.Report, now time.Time) (store.AppendResult, error) {
	payload := map[string]any{
		"run_ref":             int64(run.Seq),
		"closure_source":      "terminal_report",
		"scan_close_mode":     string(decision.Mode),
		"exit_reason":         string(terminal.ExitReason),
		"supervisor_tail":     terminal.SupervisorTail,
		"supervisor_log_path": s.retainedSupervisorLogPath(run.DispatchID),
		"closure_reason":      decision.Reason,
		"observed_active":     int64(observedActive(run, now) / time.Second),
	}
	switch decision.Mode {
	case spoolclose.ModeProvisionalAbandon:
		payload["outcome"] = "abandoned"
		payload["cause"] = "exit_reported"
	case spoolclose.ModeReportedTerminal:
		payload["outcome"] = "error"
	default:
		return store.AppendResult{}, fmt.Errorf("driver: terminal report scan returned unsupported close mode %q", decision.Mode)
	}
	if failure := s.failureValue(string(terminal.ExitReason), string(terminal.ExitReason), decision.Reason, []uint64{run.Seq}); failure != nil {
		payload["failure"] = failure
	}
	return s.appendPassRunClosedV2([]uint64{run.Seq}, payload)
}

func observedActive(run *RunState, now time.Time) time.Duration {
	if run == nil || run.OpenedAt.IsZero() || now.Before(run.OpenedAt) {
		return 0
	}
	return now.Sub(run.OpenedAt)
}

func durationSecondsInt(duration time.Duration) int {
	if duration <= 0 {
		return 0
	}
	seconds := duration / time.Second
	if seconds > time.Duration(^uint(0)>>1) {
		return int(^uint(0) >> 1)
	}
	return int(seconds)
}

func (s *Session) submissionFromBundle(state *State, item pendingSubmission) (store.Submission, error) {
	run := state.Runs[item.manifest.RunRef]
	var inputPins []store.Pin
	var subjectPin *store.Pin
	if run != nil {
		if pins, ok := run.Manifest["input_pins"].([]any); ok {
			for _, entry := range pins {
				pin, _ := entry.(map[string]any)
				inputPins = append(inputPins, store.Pin{
					Identity:    str(pin, "identity"),
					VersionSeq:  num(pin, "version_seq"),
					ContentHash: str(pin, "content_hash"),
				})
			}
		}
		if pin, ok := run.Manifest["subject_pin"].(map[string]any); ok {
			subjectPin = &store.Pin{
				Identity:    str(pin, "identity"),
				VersionSeq:  num(pin, "version_seq"),
				ContentHash: str(pin, "content_hash"),
			}
		}
	}

	sub := store.Submission{
		DispatchID:       item.manifest.DispatchID,
		RunRef:           item.manifest.RunRef,
		RunManifestHash:  item.manifest.RunManifestHash,
		LaneID:           item.manifest.LaneID,
		Attempt:          item.manifest.Attempt,
		Status:           item.manifest.Status,
		EnvironmentReads: item.manifest.EnvironmentReads,
		Attribution: store.Attribution{
			BackendID:      item.manifest.Attribution.BackendID,
			BackendVersion: item.manifest.Attribution.BackendVersion,
			AliasingClass:  item.manifest.Attribution.AliasingClass,
			AgentRuntime:   item.manifest.Attribution.AgentRuntimeID,
			LaneID:         item.manifest.LaneID,
			LaneRole:       item.manifest.Attribution.LaneRole,
			SessionNonce:   item.manifest.Attribution.SessionNonce,
		},
	}
	for _, entry := range item.manifest.Outputs {
		if entry.Status != "present" {
			continue
		}
		body, err := os.ReadFile(filepath.Join(item.dir, entry.Path))
		if err != nil {
			return sub, err
		}
		output := store.SubmissionOutput{
			OutputID:           entry.OutputID,
			Kind:               entry.Kind,
			Identity:           entry.Identity,
			Placement:          entry.Placement,
			Body:               body,
			ContentHash:        entry.ContentHash,
			DerivedFromOutputs: entry.DerivedFrom,
		}
		role := ""
		if kind, ok := s.Catalog.Kinds[entry.Kind]; ok {
			role = kind.Role
		}
		if role == "evidence" && subjectPin != nil {
			// Mirror the evidence verdict into the evidences edge claim so
			// gate and re-stamp folds never open evidence bodies.
			output.Edges = append(output.Edges, store.Edge{
				Kind:           "evidences",
				Pin:            *subjectPin,
				Claim:          evidenceClaim(entry.Kind, body),
				BindingClosure: []store.Pin{*subjectPin},
			})
		} else {
			// Provenance edges are the sealed manifest's input pins. A pin with
			// no identity is content-addressed context (e.g. a build's composed
			// base — the tree it edits, D0010.C5), never a provenance parent.
			for _, pin := range inputPins {
				if pin.Identity == "" {
					continue
				}
				output.Edges = append(output.Edges, store.Edge{Kind: "derived_from", Pin: pin})
			}
		}
		sub.Outputs = append(sub.Outputs, output)
	}
	return sub, nil
}

// --- progress: gate evaluation and head movement ---

func (s *Session) progress(report *Report) (int, error) {
	state, err := s.fold()
	if err != nil {
		return 0, err
	}
	actions := 0
	for _, id := range sortedIdentityIDs(state) {
		identity := state.Identities[id]
		if n, err := s.restampStaleHead(state, identity); err != nil {
			return actions, err
		} else if n > 0 {
			actions += n
			continue
		}
		candidate := latestCandidate(identity)
		if candidate == nil {
			continue
		}
		kind, ok := s.Catalog.Kinds[candidate.Kind]
		if !ok {
			continue
		}
		if kind.Role == "evidence" {
			// Evidence never head-moves, but its check-class gates run:
			// receipt-checks and verification-report-checks validate the
			// candidate so claims can count it (RFC 0010 §5.5).
			n, err := s.progressEvidence(state, identity, candidate, kind)
			if err != nil {
				return actions, err
			}
			actions += n
			continue
		}
		n, err := s.progressCandidate(state, identity, candidate, kind, report)
		if err != nil {
			return actions, err
		}
		actions += n
	}
	if n, err := s.surfaceFlakes(state); err != nil {
		return actions, err
	} else {
		actions += n
	}
	return actions, nil
}

// progressEvidence evaluates check-class gates on an evidence candidate.
// Evidence has no head to move; the gate results are what claim computation
// and the Dual-Signal Rule read.
func (s *Session) progressEvidence(state *State, identity *IdentityState, candidate *VersionState, kind KindSpec) (int, error) {
	actions := 0
	for _, gateID := range kind.Gates {
		spec, ok := s.Catalog.Gates[gateID]
		if !ok {
			return actions, fmt.Errorf("driver: gate %q not cataloged", gateID)
		}
		if spec.Class != "check" {
			continue // evidence faces mechanical validation only
		}
		key := gateKey{Identity: identity.ID, Version: candidate.Seq, GateID: gateID}
		if latestResult(state.GateResults[key]) != nil {
			continue
		}
		outcome, detail := s.evaluateCheckGate(state, identity, candidate, spec)
		if _, err := s.appendGateResult(identity, candidate, spec, outcome, "", detail, true); err != nil {
			return actions, err
		}
		actions++
	}
	return actions, nil
}

// restampStaleHead performs the licensed re-stamp of a stale accepted head
// once an accepting revalidation Review Ledger has been admitted: the single
// gate-exempt head movement (W6), attributed to the revalidation run.
func (s *Session) restampStaleHead(state *State, identity *IdentityState) (int, error) {
	if identity.Head == 0 {
		return 0, nil
	}
	head := identity.Versions[identity.Head]
	if head == nil || !head.Stale {
		return 0, nil
	}
	ledgerIdentity, ledgerVersion := findRevalidationLedger(state, identity.ID, head)
	if ledgerVersion == nil {
		return 0, nil
	}

	// Move the pins: every freshness-bearing edge repoints at the current
	// accepted head of its identity; diagnostic lineage (evidence pins,
	// prior-version self-references) is carried unmoved. An upstream
	// without a fresh head blocks the re-stamp.
	diagnostic := func(pin store.Pin) bool {
		if pin.Identity == identity.ID {
			return true
		}
		pinned, ok := state.Identities[pin.Identity]
		return ok && pinned.Role == "evidence"
	}
	var moved []store.Edge
	for _, pin := range head.DerivedFrom {
		if diagnostic(pin) {
			moved = append(moved, store.Edge{Kind: "derived_from", Pin: pin})
			continue
		}
		upstream := state.HeadVersion(pin.Identity)
		if upstream == nil || upstream.Stale {
			return 0, nil
		}
		moved = append(moved, store.Edge{Kind: "derived_from", Pin: store.Pin{
			Identity: pin.Identity, VersionSeq: upstream.Seq, ContentHash: upstream.ContentHash,
		}})
	}
	for _, pin := range head.ConstrainedBy {
		if diagnostic(pin) {
			moved = append(moved, store.Edge{Kind: "constrained_by", Pin: pin})
			continue
		}
		upstream := state.HeadVersion(pin.Identity)
		if upstream == nil || upstream.Stale {
			return 0, nil
		}
		moved = append(moved, store.Edge{Kind: "constrained_by", Pin: store.Pin{
			Identity: pin.Identity, VersionSeq: upstream.Seq, ContentHash: upstream.ContentHash,
		}})
	}

	license := store.ReStampLicense{
		RevalidationRun: ledgerVersion.ProducedByRun,
		ReviewLedger: store.Pin{
			Identity:    ledgerIdentity,
			VersionSeq:  ledgerVersion.Seq,
			ContentHash: ledgerVersion.ContentHash,
		},
		Verdict:    ledgerVersion.ReviewVerdict,
		MovedEdges: moved,
	}
	if _, err := s.Graph.ReStamp(identity.ID, license, s.Now); err != nil {
		return 0, err
	}
	return 1, nil
}

// findRevalidationLedger finds an admitted accepting review ledger whose
// subject is the given (stale) head version.
func findRevalidationLedger(state *State, subjectID string, head *VersionState) (string, *VersionState) {
	for _, id := range sortedIdentityIDs(state) {
		evidenceIdentity := state.Identities[id]
		if evidenceIdentity.Kind != "review-ledger" {
			continue
		}
		for i := len(evidenceIdentity.Order) - 1; i >= 0; i-- {
			version := evidenceIdentity.Versions[evidenceIdentity.Order[i]]
			if version.ReviewVerdict != "accept" && version.ReviewVerdict != "accept_with_findings" {
				continue
			}
			if version.ReviewSubjectIdentity == subjectID &&
				(version.ReviewSubjectVersion == head.Seq || version.ReviewSubjectHash == head.ContentHash) {
				return id, version
			}
		}
	}
	return "", nil
}

func latestCandidate(identity *IdentityState) *VersionState {
	for i := len(identity.Order) - 1; i >= 0; i-- {
		version := identity.Versions[identity.Order[i]]
		if version.Seq == identity.Head {
			return nil // newest version already accepted
		}
		if version.ProductionMode == "re_stamp" {
			return nil // re-stamps move heads through their license, not gates
		}
		return version
	}
	return nil
}

func (s *Session) progressCandidate(state *State, identity *IdentityState, candidate *VersionState, kind KindSpec, report *Report) (int, error) {
	actions := 0
	inputsFresh := true
	for _, pin := range state.FreshnessPins(identity.ID, candidate) {
		if !state.PinFresh(pin) {
			inputsFresh = false
		}
	}

	var licensing []uint64
	for _, gateID := range kind.Gates {
		spec, ok := s.Catalog.Gates[gateID]
		if !ok {
			return actions, fmt.Errorf("driver: gate %q not cataloged", gateID)
		}
		key := gateKey{Identity: identity.ID, Version: candidate.Seq, GateID: gateID}
		results := state.GateResults[key]
		if latest := latestResult(results); latest != nil {
			if latest.Outcome == "pass" {
				licensing = append(licensing, latest.Seq)
				continue
			}
			// integration-checks is a CAS against reality (tree_moved and
			// kin): a refusal recorded under yesterday's reality must
			// re-evaluate as reality moves, appending only when the outcome
			// flips — a refused candidate under a since-repaired predicate
			// or a since-moved head is otherwise wedged forever behind the
			// winner rule.
			if gateID == "integration-checks" && spec.Class == "check" {
				outcome, detail := s.evaluateCheckGate(state, identity, candidate, spec)
				if outcome == "pass" {
					seq, err := s.appendGateResult(identity, candidate, spec, outcome, "", detail, inputsFresh)
					if err != nil {
						return actions, err
					}
					actions++
					licensing = append(licensing, seq)
					continue
				}
			}
			return actions, nil // refused gate: candidate stays inert; planning owns revision
		}
		switch spec.Class {
		case "check":
			outcome, detail := s.evaluateCheckGate(state, identity, candidate, spec)
			seq, err := s.appendGateResult(identity, candidate, spec, outcome, "", detail, inputsFresh)
			if err != nil {
				return actions, err
			}
			actions++
			if outcome != "pass" {
				return actions, nil
			}
			licensing = append(licensing, seq)
		case "review":
			verdict, evidence := findReviewEvidence(state, identity, candidate)
			if verdict == "" {
				return actions, nil // review not yet performed: the plan carries the step
			}
			outcome := "pass"
			if verdict != "accept" && verdict != "accept_with_findings" {
				outcome = "fail"
			}
			seq, err := s.appendGateResultWithEvidence(identity, candidate, spec, outcome, verdict, evidence, inputsFresh)
			if err != nil {
				return actions, err
			}
			actions++
			if outcome != "pass" {
				return actions, nil
			}
			licensing = append(licensing, seq)
		case "acceptance":
			return actions, nil // closes only by Principal authority (accept verb)
		}
	}

	if !inputsFresh {
		report.Notes = append(report.Notes, "head movement suspended (stale inputs): "+identity.ID)
		return actions, nil
	}

	movement := "initial_accept"
	payload := map[string]any{
		"identity":   identity.ID,
		"movement":   movement,
		"to_version": int64(candidate.Seq),
		"licensed_by": map[string]any{
			"gate_results": toAnySeqs(licensing),
		},
	}
	if identity.Head != 0 {
		payload["movement"] = "supersede"
		payload["from_version"] = int64(identity.Head)
	}
	moved, err := s.append("head_movement", "driver", []uint64{candidate.Seq}, payload)
	if err != nil {
		return actions, err
	}
	actions++
	// E2 realized at admission: an integration-produced product head
	// movement binds its change set into product lineage (RFC 0010 §7.2).
	if run, ok := state.Runs[candidate.ProducedByRun]; ok && run.PassID == "integration" && kind.Role == "product" {
		if err := s.recordApplication(state, candidate, identity.ID, moved.Seq); err != nil {
			return actions, err
		}
		actions++
	}
	return actions, nil
}

func latestResult(results []GateResultState) *GateResultState {
	if len(results) == 0 {
		return nil
	}
	return &results[len(results)-1]
}

// evaluateCheckGate dispatches the check-class gate predicates: all
// execution-free Compiler Core computations over content (RFC 0010 §1). The
// default predicate is the v0 mechanical gate — durable body plus anchor
// continuity within the policy retirement budget.
func (s *Session) evaluateCheckGate(state *State, identity *IdentityState, candidate *VersionState, spec GateSpec) (string, string) {
	switch spec.ID {
	case "receipt-checks":
		return s.evaluateReceiptChecks(state, candidate)
	case "verification-report-checks":
		return s.evaluateReportChecks(state, candidate)
	case "integration-checks":
		return s.evaluateIntegrationChecks(state, identity, candidate)
	case "work-graph-legality":
		return s.evaluateWorkGraphLegality(state, candidate)
	case "packet-checks":
		// A change-set that pins a work-graph packet is a build-flow output and
		// faces the strict packet-checks predicate. A cleanly-parsed one that
		// pins none is the single-change-set grain (integrated@2, E4) and falls
		// through to the default mechanical gate — the build flow strengthens,
		// invalidates nothing. A body that is not a well-formed change-set fails
		// closed here; garbage never reaches the lenient default gate.
		switch s.changeSetPacketDisposition(candidate) {
		case "strict":
			return s.evaluatePacketChecks(state, identity, candidate)
		case "fail":
			return "fail", "change-set body is not a well-formed change-set"
		}
	}
	if candidate.BodyAddress == "" {
		return "fail", "candidate has no durable body"
	}
	if identity.Head != 0 {
		prior := identity.Versions[identity.Head]
		result := gate.EvaluateAnchorContinuity(gate.AnchorContinuityInput{
			Prior:            prior.Anchors,
			Candidate:        candidate.Anchors,
			Retired:          toGateRetired(candidate.RetiredAnchors),
			RetirementBudget: s.Policy.RetirementBudget,
		})
		if result.Outcome == gate.AnchorContinuityRefuse {
			return "fail", "anchor continuity refused: missing " + strings.Join(result.MissingAnchors, ",")
		}
		if result.Outcome == gate.AnchorContinuityReviewRequired {
			return "fail", "anchor retirement budget exceeded: review required"
		}
	}
	return "pass", ""
}

func toGateRetired(retired []store.RetiredAnchor) []gate.RetiredAnchor {
	out := make([]gate.RetiredAnchor, len(retired))
	for i, entry := range retired {
		out[i] = gate.RetiredAnchor{Anchor: entry.Anchor, Reason: entry.Reason}
	}
	return out
}

// findReviewEvidence looks for an admitted review-ledger evidencing the
// candidate and returns its verdict and pin.
func findReviewEvidence(state *State, identity *IdentityState, candidate *VersionState) (string, map[string]any) {
	for _, id := range sortedIdentityIDs(state) {
		evidenceIdentity := state.Identities[id]
		if evidenceIdentity.Kind != "review-ledger" {
			continue
		}
		for i := len(evidenceIdentity.Order) - 1; i >= 0; i-- {
			version := evidenceIdentity.Versions[evidenceIdentity.Order[i]]
			verdict := version.ReviewVerdict
			if verdict == "" {
				continue
			}
			if version.ReviewSubjectIdentity == identity.ID &&
				(version.ReviewSubjectHash == candidate.ContentHash || version.ReviewSubjectVersion == candidate.Seq) {
				return verdict, map[string]any{
					"identity":     evidenceIdentity.ID,
					"version_seq":  int64(version.Seq),
					"content_hash": version.ContentHash,
				}
			}
		}
	}
	return "", nil
}

func (s *Session) appendGateResult(identity *IdentityState, candidate *VersionState, spec GateSpec, outcome, verdict, detail string, inputsFresh bool) (uint64, error) {
	return s.appendGateResultWithEvidence(identity, candidate, spec, outcome, verdict, nil, inputsFresh, detail)
}

func (s *Session) appendGateResultWithEvidence(identity *IdentityState, candidate *VersionState, spec GateSpec, outcome, verdict string, evidence map[string]any, inputsFresh bool, detail ...string) (uint64, error) {
	payload := map[string]any{
		"subject": map[string]any{
			"identity":     identity.ID,
			"version_seq":  int64(candidate.Seq),
			"content_hash": candidate.ContentHash,
		},
		"gate_id":                spec.ID,
		"gate_class":             spec.Class,
		"gate_predicate_version": int64(1),
		"outcome":                outcome,
		"inputs_fresh":           inputsFresh,
		"evidence":               []any{},
	}
	if verdict != "" {
		payload["verdict"] = verdict
	}
	if evidence != nil {
		payload["evidence"] = []any{evidence}
	}
	if len(detail) > 0 && detail[0] != "" {
		payload["detail"] = detail[0]
	}
	result, err := s.append("gate_result", "driver", []uint64{candidate.Seq}, payload)
	if err != nil {
		return 0, err
	}
	return result.Seq, nil
}

// --- mark: eager staleness waves ---

func (s *Session) mark() (int, error) {
	state, err := s.fold()
	if err != nil {
		return 0, err
	}
	actions := 0
	for _, movement := range state.HeadMovements {
		if state.MarkedWaves[movement.Seq] {
			continue
		}
		moved := state.Identities[movement.Identity]
		newHead := moved.Versions[movement.To]
		var oldHash string
		if old, ok := moved.Versions[movement.From]; ok {
			oldHash = old.ContentHash
		}
		var subjects []any
		for _, id := range sortedIdentityIDs(state) {
			if id == movement.Identity {
				continue
			}
			dependent := state.Identities[id]
			if dependent.Head == 0 {
				continue
			}
			headVersion := dependent.Versions[dependent.Head]
			via := dependencyVia(headVersion, movement.Identity, newHead)
			if via == "" {
				continue
			}
			subjects = append(subjects, map[string]any{
				"pin": map[string]any{
					"identity":     id,
					"version_seq":  int64(headVersion.Seq),
					"content_hash": headVersion.ContentHash,
				},
				"via":           via,
				"element_grain": false,
			})
		}
		if subjects == nil {
			subjects = []any{}
		}
		var newHash string
		if newHead != nil {
			newHash = newHead.ContentHash
		}
		payload := map[string]any{
			"wave": int64(movement.Seq),
			"cause": map[string]any{
				"kind": "head_moved",
				"moved": map[string]any{
					"identity": movement.Identity,
					"old_hash": oldHash,
					"new_hash": newHash,
				},
			},
			"subjects": subjects,
			"chunk":    map[string]any{"index": int64(0), "of": int64(1)},
		}
		if _, err := s.append("staleness_event", "driver", []uint64{movement.Seq}, payload); err != nil {
			return actions, err
		}
		actions++
	}
	return actions, nil
}

// dependencyVia reports how a dependent's accepted head pins the moved
// identity, when the pin no longer matches the new head (hash-first).
func dependencyVia(version *VersionState, movedIdentity string, newHead *VersionState) string {
	matches := func(pins []store.Pin) bool {
		for _, pin := range pins {
			if pin.Identity != movedIdentity {
				continue
			}
			if newHead == nil || pin.ContentHash != newHead.ContentHash {
				return true
			}
		}
		return false
	}
	if matches(version.DerivedFrom) {
		return "derived_from"
	}
	if matches(version.ConstrainedBy) {
		return "constrained_by"
	}
	return ""
}

// --- plan ---

type planStep struct {
	StepID     string
	PassID     string
	Subject    string
	Inputs     []string
	Revalidate bool
	Reason     string
	// CheckDetail carries a refusing check gate's recorded detail into the
	// revision lane's objective (derived from folded gate results, so it is
	// deterministic for a given ledger and needs no plan serialization).
	CheckDetail string
	// RejectionDetail carries the Principal's acceptance-gate rejection
	// reason into the fresh revision's objective: without it the lane only
	// sees the (passing) review ledger and reproduces the rejected shape —
	// the RQ-7999 write-scope revision proved it.
	RejectionDetail string

	// Verification steps carry the signal ordinal, the sandbox profile the
	// scheduler assigns for execution-independence distinctness, and the
	// resolved check identities.
	Signal   int
	Profile  string
	CheckIDs []string
	// CodeTree marks a verification step whose subject is verified against a
	// materialized filesystem tree (composed base + change-set diff, RFC 0010
	// §5.2) rather than a single artifact body — set when the code check set is
	// selected for a change-set subject.
	CodeTree bool

	// ExcludedAliasing is the independence exclusion set for this step,
	// computed from recorded attribution: a judgment review never binds to
	// the subject producer's aliasing class, and never to the deterministic
	// class (tier-0 has no judgment to give).
	ExcludedAliasing []string

	// DiagnosticIDs are declared diagnostic inputs (W10): the refused prior
	// candidate and its Review Ledger, pinned into revision runs so the
	// findings are addressed, never rediscovered.
	DiagnosticIDs []string

	// Packet is the work-graph packet id a build step implements; the base it
	// composes and its write scope are derived from the pinned work-graph.
	Packet string

	// Batch carries the ordered change-set identities of a batch integration
	// step (Work Graph index order) — the deterministic topological link of the
	// Verified frontier (D0010.C8). Empty for single-change integration.
	Batch []string
}

func (s *Session) plan(report *Report) (int, error) {
	state, err := s.fold()
	if err != nil {
		return 0, err
	}
	actions := 0
	for _, requestSeq := range sortedRequestSeqs(state) {
		request := state.Requests[requestSeq]
		if request.Satisfied || request.Canceled {
			continue
		}
		target, ok := s.Catalog.Targets[request.TargetID]
		if !ok {
			continue
		}
		unmet, steps := s.computeSteps(state, request, target)
		if len(unmet) == 0 {
			evidence := []any{}
			for _, conjunct := range target.Conjuncts {
				identity := subjectIdentity(request.Subject, conjunct.ArtifactKind)
				version := state.HeadVersion(identity)
				if conjunct.Kind == "evidence_admitted" {
					version = latestVersion(state, identity)
				}
				if conjunct.Kind == "review_admitted" {
					artifact := harvestArtifact(request.Subject)
					if head := state.HeadVersion(artifact); head != nil {
						if ledger := s.reviewAdmittedUnder(state, request, head); ledger != nil {
							version = ledger
							identity = "review-ledger under RQ-" + fmt.Sprint(request.Seq)
						}
					}
				}
				if version == nil {
					continue
				}
				evidence = append(evidence, map[string]any{
					"conjunct":     conjunct.Kind + ":" + conjunct.ArtifactKind,
					"identity":     identity,
					"version_seq":  int64(version.Seq),
					"content_hash": version.ContentHash,
				})
				if conjunct.Kind == "verified_dual_signal" || conjunct.Kind == "integrated_head" {
					// Pin the two reports whose closure satisfied the rule.
					_, qualified, err := s.dualSignalSatisfied(state, identity, version)
					if err != nil {
						return actions, err
					}
					for _, signal := range qualified {
						evidence = append(evidence, map[string]any{
							"conjunct":     "verification_report",
							"identity":     signal.Identity,
							"version_seq":  int64(signal.Version.Seq),
							"content_hash": signal.Version.ContentHash,
						})
					}
				}
				if conjunct.Kind == "integrated_head" {
					// Pin the product head the application record binds.
					productID := productIdentity(request.Subject)
					if productHead := state.HeadVersion(productID); productHead != nil {
						evidence = append(evidence, map[string]any{
							"conjunct":     "product_head",
							"identity":     productID,
							"version_seq":  int64(productHead.Seq),
							"content_hash": productHead.ContentHash,
						})
					}
				}
			}
			if _, err := s.append("satisfaction_record", "driver", []uint64{request.Seq}, map[string]any{
				"request_ref": int64(request.Seq),
				"target_pin": map[string]any{
					"state_id":          target.ID,
					"predicate_version": int64(target.PredicateVersion),
				},
				// The claim level the satisfaction earns from its conjunct
				// evidence (D0005.C5 — claims are computed; Verified is a
				// predicate, never a declaration): a floor-only satisfaction is
				// Asserted, never a bare "satisfied" reading as Verified.
				"claim_level": satisfactionClaimLevel(target.Conjuncts),
				"evaluation": map[string]any{
					"ledger_seq":             int64(state.LastSeq),
					"conjunct_evidence_pins": evidence,
				},
			}); err != nil {
				return actions, err
			}
			actions++
			continue
		}

		hash, stepsValue, err := planContent(unmet, steps)
		if err != nil {
			return actions, err
		}
		if latest := state.Plans[request.Seq]; latest != nil && latest.ContentHash == hash {
			continue
		}
		if _, err := s.append("plan_record", "driver", []uint64{request.Seq}, map[string]any{
			"request_ref":  int64(request.Seq),
			"content_hash": hash,
			"basis": map[string]any{
				"ledger_seq":   int64(state.LastSeq),
				"heads_digest": headsDigest(state),
			},
			"unmet": toAnyStrings(unmet),
			"steps": stepsValue,
			"policy_pins": []any{map[string]any{
				"policy_id": "driver",
				"version":   int64(s.Policy.PolicyVersion),
			}},
		}); err != nil {
			return actions, err
		}
		actions++
	}
	return actions, nil
}

// computeSteps derives the unmet conjuncts and the plan steps for a request:
// graph reachability over catalog consumes/produces data (RFC 0006).
func (s *Session) computeSteps(state *State, request *RequestState, target TargetSpec) ([]string, []planStep) {
	var unmet []string
	var steps []planStep
	planned := map[string]bool{}

	// ensure walks the consumes/produces graph. conjunctKind is set only for
	// the target's directly-demanded kinds ("" for transitive inputs):
	// evidence_admitted asks for an admitted evidence version,
	// verified_dual_signal demands the Dual-Signal Rule over the subject's
	// accepted head, and accepted_head over a source pass demands a head
	// produced under this request — a new capture command is a new
	// utterance, so the head that satisfied an earlier request does not
	// satisfy this one.
	var ensure func(kind, conjunctKind string) bool
	ensure = func(kind, conjunctKind string) bool {
		identity := subjectIdentity(request.Subject, kind)

		if conjunctKind == "verified_dual_signal" {
			// The subject head must exist and be fresh before verification
			// is meaningful; ensure it through the ordinary walk first.
			if !ensure(kind, "") {
				return false
			}
			head := state.HeadVersion(identity)
			satisfied := s.planDualSignal(state, identity, head, planned, &steps)
			return satisfied
		}

		if conjunctKind == "built" {
			// The work-graph build frontier: fan out one build per ready
			// packet, verify each change-set (D0010.C8/C9).
			return s.planWorkGraphBuild(state, request, kind, planned, &steps, ensure)
		}

		if conjunctKind == "integrated_batch" {
			// The whole work-graph linked into product lineage as a batch.
			return s.planWorkGraphIntegration(state, request, kind, planned, &steps, ensure)
		}

		if conjunctKind == "integrated_head" {
			// Integration consumes claim_min: Verified — the change-set head
			// must be accepted, fresh, and dual-signal verified before the
			// linker stages anything.
			if !ensure(kind, "") {
				return false
			}
			head := state.HeadVersion(identity)
			productID := productIdentity(request.Subject)
			// An application-bound head satisfies the conjunct outright: its
			// own integration moved the composed base, so every later check
			// against that base (tree-moved, re-verification) is vacuous for
			// it — consulted first or they loop forever on a done head.
			if applicationBound(state, head, productID) {
				return true
			}
			// Clause 4 (stalls-need-no-judgment@3), consulted BEFORE the
			// dual-signal demand: an unintegrated head whose pinned base no
			// longer composes can neither re-verify nor lawfully re-integrate
			// — the lawful plan is a bounded rebase-style build revision
			// against the current composed base, and demanding fresh signals
			// on the doomed head first would starve the rebuild forever.
			if rebuild, moved := s.planTreeMovedRebuild(state, request, identity, head, planned); moved {
				if rebuild != nil {
					steps = append(steps, *rebuild)
				}
				return false
			}
			if !s.planDualSignal(state, identity, head, planned, &steps) {
				return false
			}
			if productState, ok := state.Identities[productID]; ok {
				if candidate := latestCandidate(productState); candidate != nil &&
					!s.integrationRefused(state, candidate, productID) {
					return false // staged; progressing through integration-checks
				}
				// A refused candidate (tree_moved and kin) re-stages below.
			}
			stepID := "integrate/" + productID + "/" + head.ContentHash[:16]
			if planned[stepID] {
				return false
			}
			planned[stepID] = true
			steps = append(steps, planStep{
				StepID:  stepID,
				PassID:  "integration",
				Subject: productID,
				Inputs:  []string{identity},
				Reason:  "verified change set awaiting integration",
			})
			return false
		}

		if conjunctKind == "review_admitted" {
			// The harvest review posture (RFC 0008): a second-opinion Review
			// Ledger over the named artifact's current accepted head,
			// produced under THIS request — a prior review never satisfies a
			// new harvest utterance.
			artifact := harvestArtifact(request.Subject)
			if artifact == "" {
				return false // not a harvest subject; unmet and unplannable
			}
			head := state.HeadVersion(artifact)
			if head == nil || head.Stale {
				return false // issuance should have refused; nothing to review
			}
			if s.reviewAdmittedUnder(state, request, head) != nil {
				return true
			}
			stepID := "harvest-review/" + artifact + "/" + fmt.Sprint(request.Seq)
			if planned[stepID] {
				return false
			}
			planned[stepID] = true
			excluded := []string{"deterministic"}
			if head.AliasingClass != "" && head.AliasingClass != "deterministic" {
				excluded = append(excluded, head.AliasingClass)
			}
			steps = append(steps, planStep{
				StepID:           stepID,
				PassID:           "review",
				Subject:          artifact,
				Reason:           "harvest: second-opinion review (delegated issuance)",
				ExcludedAliasing: excluded,
			})
			return false
		}

		if conjunctKind == "evidence_admitted" {
			if latestVersion(state, identity) != nil {
				return true
			}
			if planned[identity] {
				return false
			}
			planned[identity] = true
			if producer, ok := s.Catalog.ProducerOf(kind); ok {
				steps = append(steps, planStep{
					StepID:  "produce/" + identity,
					PassID:  producer.ID,
					Subject: identity,
					Reason:  "no admitted evidence",
				})
			}
			return false
		}

		head := state.HeadVersion(identity)
		if head != nil && !head.Stale {
			// A revision candidate above the accepted head is in flight:
			// progress it (review, bounded revision, acceptance wait) and
			// hold the demand side — consumers must not lower against a
			// head that a pending revision is about to supersede.
			if identityState, ok := state.Identities[identity]; ok {
				if pending := latestCandidate(identityState); pending != nil && pending.Seq > head.Seq &&
					!s.candidateRetired(state, identityState, pending) {
					if planned[identity] {
						return false
					}
					planned[identity] = true
					s.progressPendingCandidate(state, request, kind, identity, identityState, pending, planned, &steps)
					return false
				}
			}
			if conjunctKind != "accepted_head" || s.headSatisfiesRequest(state, request, kind, head) {
				return true
			}
		}
		if planned[identity] {
			return false
		}
		planned[identity] = true

		if head != nil && head.Stale {
			// Revalidation before regeneration (D0005.C3).
			steps = append(steps, planStep{
				StepID:     "revalidate/" + identity,
				PassID:     "review",
				Subject:    identity,
				Revalidate: true,
				Reason:     "stale accepted head",
			})
			return false
		}

		var retired *VersionState
		identityState, exists := state.Identities[identity]
		if exists {
			if candidate := latestCandidate(identityState); candidate != nil {
				if !s.candidateRetired(state, identityState, candidate) {
					s.progressPendingCandidate(state, request, kind, identity, identityState, candidate, planned, &steps)
					return false
				}
				// Retired (Principal-rejected at acceptance): terminal for
				// that version — a fresh revision is the only way forward.
				// The step id must be round-salted: the plain produce
				// objective was won by the run that made the rejected
				// candidate, so an unsalted re-production is refused at
				// admission as a duplicate (the winner rule).
				retired = candidate
			}
		}

		producer, ok := s.Catalog.ProducerOfForSubject(kind, request.Subject)
		if !ok {
			return false
		}
		var inputs []string
		for _, consumed := range producer.Consumes {
			if consumed == "*" {
				continue
			}
			inputs = append(inputs, subjectIdentity(request.Subject, consumed))
			ensure(consumed, "")
		}
		// Optional consumes are pinned when a fresh head exists, never
		// produced on this pass's account and never blocking dispatch.
		for _, consumed := range producer.ConsumesOptional {
			if consumed == "*" {
				continue
			}
			optionalID := subjectIdentity(request.Subject, consumed)
			if head := state.HeadVersion(optionalID); head != nil && !head.Stale {
				inputs = append(inputs, optionalID)
			}
		}
		if retired != nil {
			steps = append(steps, planStep{
				StepID:          fmt.Sprintf("revise/%s/%d-r%d", identity, retired.Seq, len(identityState.Order)),
				PassID:          producer.ID,
				Subject:         identity,
				Inputs:          inputs,
				Reason:          "acceptance gate rejected: fresh revision",
				DiagnosticIDs:   []string{identity},
				RejectionDetail: s.acceptanceRejectionDetail(state, identityState, retired),
			})
			return false
		}
		steps = append(steps, planStep{
			StepID:  "produce/" + identity,
			PassID:  producer.ID,
			Subject: identity,
			Inputs:  inputs,
			Reason:  "no accepted head",
		})
		return false
	}

	for _, conjunct := range target.Conjuncts {
		if !ensure(conjunct.ArtifactKind, conjunct.Kind) {
			unmet = append(unmet, conjunct.Kind+":"+conjunct.ArtifactKind)
		}
	}
	return unmet, steps
}

// headSatisfiesRequest applies the source-pass freshness rule: a head of a
// kind whose producer consumes no artifacts (the input is the Principal's
// utterance) satisfies only the request whose runs produced it.
func (s *Session) headSatisfiesRequest(state *State, request *RequestState, kind string, head *VersionState) bool {
	producer, ok := s.Catalog.ProducerOf(kind)
	if !ok || len(producer.Consumes) > 0 {
		return true
	}
	run, ok := state.Runs[head.ProducedByRun]
	if !ok {
		return false
	}
	return run.RequestRef == request.Seq
}

// latestVersion returns an identity's newest admitted version, if any.
func latestVersion(state *State, identity string) *VersionState {
	identityState, ok := state.Identities[identity]
	if !ok || len(identityState.Order) == 0 {
		return nil
	}
	return identityState.Versions[identityState.Order[len(identityState.Order)-1]]
}

// candidateRetired reports whether the Principal refused the candidate at an
// acceptance gate: a rejected revision is terminal for that version — it
// neither holds the demand side nor receives further progression; a fresh
// revision (a new version) is the only way forward.
func (s *Session) candidateRetired(state *State, identity *IdentityState, candidate *VersionState) bool {
	kind, ok := s.Catalog.Kinds[candidate.Kind]
	if !ok {
		return false
	}
	for _, gateID := range kind.Gates {
		if s.Catalog.Gates[gateID].Class != "acceptance" {
			continue
		}
		key := gateKey{Identity: identity.ID, Version: candidate.Seq, GateID: gateID}
		if latest := latestResult(state.GateResults[key]); latest != nil && latest.Outcome != "pass" {
			return true
		}
	}
	return false
}

// failureClosure builds a pass_run_closed{error} payload carrying the C3
// diagnosis structure (stalls-need-no-judgment@3): stage, a class resolving
// in the governed refusal-classes catalog, detail, and causal refs. When the
// catalog is absent or the class does not validate, the payload degrades to
// the legacy shape with detail preserved — readable, never refused, never
// silently classless when the vocabulary is present.
func (s *Session) failureClosure(runRef uint64, stage, class, detail string, causal []uint64) map[string]any {
	payload := map[string]any{
		"run_ref": int64(runRef),
		"outcome": "error",
		"detail":  detail,
	}
	if len(causal) == 0 {
		// The run being closed is itself the minimal causal citation.
		causal = []uint64{runRef}
	}
	if failure := s.failureValue(stage, class, detail, causal); failure != nil {
		payload["failure"] = failure
	}
	return payload
}

func (s *Session) failureValue(stage, class, detail string, causal []uint64) map[string]any {
	if len(causal) == 0 {
		return nil
	}
	refs := make([]string, 0, len(causal))
	for _, seq := range causal {
		refs = append(refs, fmt.Sprintf("seq:%d", seq))
	}
	failure := admission.Failure{Stage: stage, Class: class, DetailOrEvidence: detail, CausalRefs: refs}
	if admission.ValidateFailure(failure, s.FailureClasses, true) != nil {
		return nil
	}
	anyRefs := make([]any, 0, len(refs))
	for _, r := range refs {
		anyRefs = append(anyRefs, r)
	}
	return map[string]any{
		"stage":              stage,
		"class":              class,
		"detail_or_evidence": detail,
		"causal_refs":        anyRefs,
	}
}

// acceptanceRejectionDetail returns the recorded reason of the acceptance
// gate result that retired the candidate — the Principal's steer for the
// fresh revision. Empty when the candidate is not acceptance-rejected.
func (s *Session) acceptanceRejectionDetail(state *State, identity *IdentityState, candidate *VersionState) string {
	kind, ok := s.Catalog.Kinds[candidate.Kind]
	if !ok {
		return ""
	}
	for _, gateID := range kind.Gates {
		if s.Catalog.Gates[gateID].Class != "acceptance" {
			continue
		}
		key := gateKey{Identity: identity.ID, Version: candidate.Seq, GateID: gateID}
		if latest := latestResult(state.GateResults[key]); latest != nil && latest.Outcome != "pass" {
			return latest.Detail
		}
	}
	return ""
}

// freshInputPins reports whether every freshness-bearing input pin of the
// candidate still resolves to the pinned head: when true, a deterministic
// re-production is guaranteed byte-identical.
func (s *Session) freshInputPins(state *State, identityID string, candidate *VersionState) bool {
	for _, pin := range state.FreshnessPins(identityID, candidate) {
		if !state.PinFresh(pin) {
			return false
		}
	}
	return true
}

// progressCandidate plans a pending candidate's next step — the single owner
// of candidate progression, whether the candidate is first-of-identity or a
// revision above an accepted head. A check-refused candidate revises
// (upstream for a deterministic producer over fresh pins — a D1 re-run over
// unchanged inputs is byte-identical by construction, so the refusal indicts
// the judgment artifact it lowered); an unreviewed candidate gets its review;
// a review-refused one gets a bounded revision; a candidate whose gates are
// passing waits on the Principal.
func (s *Session) progressPendingCandidate(state *State, request *RequestState, kind, identity string, identityState *IdentityState, candidate *VersionState, planned map[string]bool, steps *[]planStep) {
	if gateID, detail, refused := s.checkRefused(state, identityState, candidate); refused {
		producer, ok := s.Catalog.ProducerOf(kind)
		if !ok {
			return
		}
		if producer.Determinism == "D1" && s.freshInputPins(state, identity, candidate) {
			for _, consumed := range producer.Consumes {
				if consumed == "*" {
					continue
				}
				upstream, ok := s.Catalog.ProducerOf(consumed)
				if !ok || upstream.Determinism == "D1" {
					continue
				}
				upstreamID := subjectIdentity(request.Subject, consumed)
				upstreamHead := state.HeadVersion(upstreamID)
				if upstreamHead == nil {
					continue
				}
				if upstreamState, ok := state.Identities[upstreamID]; ok {
					if pending := latestCandidate(upstreamState); pending != nil && pending.Seq > upstreamHead.Seq &&
						!s.candidateRetired(state, upstreamState, pending) {
						// A revision is already pending upstream: progress
						// it instead of planning another.
						if !planned[upstreamID] {
							planned[upstreamID] = true
							s.progressPendingCandidate(state, request, consumed, upstreamID, upstreamState, pending, planned, steps)
						}
						return
					}
				}
				var upstreamInputs []string
				for _, uc := range upstream.Consumes {
					if uc == "*" {
						continue
					}
					upstreamInputs = append(upstreamInputs, subjectIdentity(request.Subject, uc))
				}
				upstreamRound := 0
				if us, ok := state.Identities[upstreamID]; ok {
					upstreamRound = len(us.Order)
				}
				*steps = append(*steps, planStep{
					StepID:        "revise/" + upstreamID + "/" + fmt.Sprint(candidate.Seq) + "-r" + fmt.Sprint(upstreamRound),
					PassID:        upstream.ID,
					Subject:       upstreamID,
					Inputs:        upstreamInputs,
					Reason:        "check gate refused downstream: revision (" + gateID + ")",
					DiagnosticIDs: []string{identity},
					CheckDetail:   detail,
				})
				return
			}
			// No revisable upstream found: fall through to bounded
			// re-production rather than plan nothing.
		}
		var inputs []string
		for _, consumed := range producer.Consumes {
			if consumed == "*" {
				continue
			}
			inputs = append(inputs, subjectIdentity(request.Subject, consumed))
		}
		*steps = append(*steps, planStep{
			StepID:        "revise/" + identity + "/" + fmt.Sprint(candidate.Seq) + "-r" + fmt.Sprint(len(identityState.Order)),
			PassID:        producer.ID,
			Subject:       identity,
			Inputs:        inputs,
			Reason:        "check gate refused: revision (" + gateID + ")",
			DiagnosticIDs: []string{identity},
			CheckDetail:   detail,
		})
		return
	}
	if s.candidateAwaitsReview(state, identityState, candidate) {
		// A review-gate closure is a judgment posture: exclude the
		// producer's aliasing class (independence, RFC 0005) and the
		// deterministic class (tier-0 is revalidation machinery, not
		// judgment).
		excluded := []string{"deterministic"}
		if candidate.AliasingClass != "" && candidate.AliasingClass != "deterministic" {
			excluded = append(excluded, candidate.AliasingClass)
		}
		*steps = append(*steps, planStep{
			StepID:           "review/" + identity + "/" + fmt.Sprint(candidate.Seq),
			PassID:           "review",
			Subject:          identity,
			Reason:           "review gate open",
			ExcludedAliasing: excluded,
		})
		return
	}
	if ledgerID, refused := s.reviewRefused(state, identityState, candidate); refused {
		// Bounded revision (RFC 0006/0010 revision budgets): a new
		// production run pinning the refused candidate and its Review
		// Ledger as declared diagnostic inputs.
		producer, ok := s.Catalog.ProducerOf(kind)
		if !ok {
			return
		}
		var inputs []string
		for _, consumed := range producer.Consumes {
			if consumed == "*" {
				continue
			}
			inputs = append(inputs, subjectIdentity(request.Subject, consumed))
		}
		diagnostics := []string{identity}
		if ledgerID != "" {
			diagnostics = append(diagnostics, ledgerID)
		}
		*steps = append(*steps, planStep{
			StepID:        "revise/" + identity + "/" + fmt.Sprint(candidate.Seq),
			PassID:        producer.ID,
			Subject:       identity,
			Inputs:        inputs,
			Reason:        "review gate refused: revision",
			DiagnosticIDs: diagnostics,
		})
	}
	// Otherwise the candidate is progressing through gates or waiting on
	// the Principal; nothing to plan.
}

// checkRefused reports whether the candidate's latest check-class gate
// result failed, returning the refusing gate id and its recorded detail:
// a mechanical refusal is re-production work for the producing pass.
func (s *Session) checkRefused(state *State, identity *IdentityState, candidate *VersionState) (string, string, bool) {
	kind, ok := s.Catalog.Kinds[candidate.Kind]
	if !ok {
		return "", "", false
	}
	for _, gateID := range kind.Gates {
		if s.Catalog.Gates[gateID].Class != "check" {
			continue
		}
		key := gateKey{Identity: identity.ID, Version: candidate.Seq, GateID: gateID}
		latest := latestResult(state.GateResults[key])
		if latest == nil || latest.Outcome != "fail" {
			continue
		}
		return gateID, latest.Detail, true
	}
	return "", "", false
}

// reviewRefused reports whether the candidate's latest review-class gate
// result refused with a revise/reject verdict, returning the refusing
// Review Ledger's identity for diagnostic pinning.
func (s *Session) reviewRefused(state *State, identity *IdentityState, candidate *VersionState) (string, bool) {
	kind, ok := s.Catalog.Kinds[candidate.Kind]
	if !ok {
		return "", false
	}
	for _, gateID := range kind.Gates {
		if s.Catalog.Gates[gateID].Class != "review" {
			continue
		}
		key := gateKey{Identity: identity.ID, Version: candidate.Seq, GateID: gateID}
		latest := latestResult(state.GateResults[key])
		if latest == nil || latest.Outcome == "pass" {
			continue
		}
		for _, id := range sortedIdentityIDs(state) {
			evidence := state.Identities[id]
			if evidence.Kind != "review-ledger" {
				continue
			}
			for i := len(evidence.Order) - 1; i >= 0; i-- {
				version := evidence.Versions[evidence.Order[i]]
				if version.ReviewSubjectIdentity == identity.ID &&
					(version.ReviewSubjectHash == candidate.ContentHash || version.ReviewSubjectVersion == candidate.Seq) {
					return id, true
				}
			}
		}
		return "", true
	}
	return "", false
}

func (s *Session) candidateAwaitsReview(state *State, identity *IdentityState, candidate *VersionState) bool {
	kind, ok := s.Catalog.Kinds[candidate.Kind]
	if !ok {
		return false
	}
	for _, gateID := range kind.Gates {
		spec := s.Catalog.Gates[gateID]
		if spec.Class != "review" {
			continue
		}
		key := gateKey{Identity: identity.ID, Version: candidate.Seq, GateID: gateID}
		if latestResult(state.GateResults[key]) != nil {
			continue
		}
		if verdict, _ := findReviewEvidence(state, identity, candidate); verdict == "" {
			return true
		}
	}
	return false
}

func planContent(unmet []string, steps []planStep) (string, []any, error) {
	stepsValue := make([]any, len(steps))
	for i, step := range steps {
		stepsValue[i] = map[string]any{
			"step_id":    step.StepID,
			"pass":       step.PassID,
			"subject":    step.Subject,
			"input_pins": toAnyStrings(step.Inputs),
			"revalidate": step.Revalidate,
			"reason":     step.Reason,
		}
	}
	canonical, err := store.RunManifestHash(map[string]any{
		"unmet": toAnyStrings(unmet),
		"steps": stepsValue,
	})
	if err != nil {
		return "", nil, err
	}
	return canonical, stepsValue, nil
}

func headsDigest(state *State) string {
	var parts []string
	for _, id := range sortedIdentityIDs(state) {
		identity := state.Identities[id]
		if identity.Head == 0 {
			continue
		}
		parts = append(parts, id+":"+identity.Versions[identity.Head].ContentHash)
	}
	sum := sha256.Sum256([]byte(strings.Join(parts, "\n")))
	return hex.EncodeToString(sum[:])
}

// --- dispatch ---

func (s *Session) dispatch(report *Report) (int, error) {
	state, err := s.fold()
	if err != nil {
		return 0, err
	}
	actions := 0
	for _, requestSeq := range sortedRequestSeqs(state) {
		request := state.Requests[requestSeq]
		if request.Satisfied || request.Canceled {
			continue
		}
		target, ok := s.Catalog.Targets[request.TargetID]
		if !ok {
			continue
		}
		_, steps := s.computeSteps(state, request, target)
		for _, step := range steps {
			n, err := s.dispatchStep(state, request, step, report)
			if err != nil {
				return actions, err
			}
			actions += n
			if n > 0 {
				// Re-fold so later steps see the opened run.
				state, err = s.fold()
				if err != nil {
					return actions, err
				}
			}
		}
	}
	return actions, nil
}

func (s *Session) dispatchStep(state *State, request *RequestState, step planStep, report *Report) (int, error) {
	// An unresolved escalation on this subject blocks fresh dispatch: the
	// Principal owns the next move, and churning attempts under a standing
	// refusal is capacity burn with no new information.
	for _, escalation := range state.Escalations {
		if !escalation.Resolved && escalation.BlockingScope == step.Subject {
			return 0, nil
		}
	}
	// A resolved bounds escalation licenses fresh attempts: the Principal's
	// proceed means "try again", so only runs after the latest resolved
	// escalation naming this step count against the budget.
	var licensedAfter uint64
	for _, escalation := range state.Escalations {
		if escalation.Resolved && strings.Contains(escalation.Detail, step.StepID) &&
			escalation.Seq > licensedAfter {
			licensedAfter = escalation.Seq
		}
	}
	attempts := int64(0)
	for _, run := range state.Runs {
		if run.StepID != step.StepID || run.RequestRef != request.Seq {
			continue
		}
		if run.Open() {
			return 0, nil // Open-Run Invariant
		}
		if run.Seq > licensedAfter {
			attempts++
		}
	}
	if int(attempts) > s.Policy.RedispatchBound {
		return s.escalateBounds(state, request, step)
	}

	pass, ok := s.Catalog.Passes[step.PassID]
	if !ok {
		return 0, fmt.Errorf("driver: pass %q not cataloged", step.PassID)
	}

	// Gather inputs; a step whose inputs lack fresh accepted heads waits.
	var inputPins []any
	inputBodies := map[string][]byte{}
	var dispatchInputs []backend.DispatchInput
	for i, inputIdentity := range step.Inputs {
		head := state.HeadVersion(inputIdentity)
		if head == nil || head.Stale {
			return 0, nil
		}
		inputPins = append(inputPins, map[string]any{
			"identity":     inputIdentity,
			"version_seq":  int64(head.Seq),
			"content_hash": head.ContentHash,
		})
		body, err := s.Graph.GetObject(head.ContentHash)
		if err != nil {
			return 0, err
		}
		path := fmt.Sprintf("inputs/%02d-%s", i, sanitize(inputIdentity))
		inputBodies[path] = body
		dispatchInputs = append(dispatchInputs, backend.DispatchInput{
			Identity:    inputIdentity,
			VersionSeq:  head.Seq,
			ContentHash: head.ContentHash,
			Path:        path,
		})
	}

	if len(step.DiagnosticIDs) > 0 {
		// Revision bound: versions of the identity beyond the first are
		// revisions; exhaustion trips the revision budget (RFC 0010 §9.1).
		// A resolved bounds escalation licenses fresh revisions the same way
		// it licenses redispatch attempts: only versions after the latest
		// resolved escalation naming this subject count — immutable version
		// history must not re-trip the brake the Principal (or the standing
		// grant) already adjudicated.
		if identityState, ok := state.Identities[step.Subject]; ok &&
			versionsSinceLicense(state, identityState, step.Subject) > s.Policy.RevisionBound+1 {
			return s.escalateRevisionBounds(state, request, step)
		}
		// Declared diagnostic inputs (W10): pinned bodies of the refused
		// candidate and its Review Ledger, materialized for the lane.
		for i, diagID := range step.DiagnosticIDs {
			version := latestVersion(state, diagID)
			if version == nil {
				continue
			}
			inputPins = append(inputPins, map[string]any{
				"identity":     diagID,
				"version_seq":  int64(version.Seq),
				"content_hash": version.ContentHash,
				"role":         "diagnostic",
			})
			body, err := s.Graph.GetObject(version.ContentHash)
			if err != nil {
				return 0, err
			}
			path := fmt.Sprintf("inputs/9%d-diagnostic-%s", i, sanitize(diagID))
			inputBodies[path] = body
			dispatchInputs = append(dispatchInputs, backend.DispatchInput{
				Identity:    diagID,
				VersionSeq:  version.Seq,
				ContentHash: version.ContentHash,
				Path:        path,
			})
		}
	}

	if step.PassID == "integration" && len(step.Batch) > 0 {
		// Batch integration: pin the verified change-sets in Work Graph index
		// order (role batch_change, application_index) plus T_obs as the base
		// (role base — the CAS token). The linked tree is the deterministic
		// union of the disjoint overlays (D0010.C8).
		for i, csID := range step.Batch {
			head := state.HeadVersion(csID)
			if head == nil || head.Stale {
				return 0, nil
			}
			inputPins = append(inputPins, map[string]any{
				"identity":          csID,
				"version_seq":       int64(head.Seq),
				"content_hash":      head.ContentHash,
				"role":              "batch_change",
				"application_index": int64(i),
			})
			body, err := s.Graph.GetObject(head.ContentHash)
			if err != nil {
				return 0, err
			}
			path := fmt.Sprintf("inputs/batch-%02d-%s", i, sanitize(csID))
			inputBodies[path] = body
			dispatchInputs = append(dispatchInputs, backend.DispatchInput{
				Identity: csID, VersionSeq: head.Seq, ContentHash: head.ContentHash, Path: path,
			})
		}
		if productHead := state.HeadVersion(step.Subject); productHead != nil {
			inputPins = append(inputPins, map[string]any{
				"identity":     step.Subject,
				"version_seq":  int64(productHead.Seq),
				"content_hash": productHead.ContentHash,
				"role":         "base",
			})
			body, err := s.Graph.GetObject(productHead.ContentHash)
			if err != nil {
				return 0, err
			}
			inputBodies["inputs/batch-base"] = body
			dispatchInputs = append(dispatchInputs, backend.DispatchInput{
				Identity: step.Subject, VersionSeq: productHead.Seq, ContentHash: productHead.ContentHash, Path: "inputs/batch-base",
			})
		}
	} else if step.PassID == "integration" {
		// Stage against the current observed product tree: the base pin is
		// the CAS token integration-checks compares against reality.
		if productHead := state.HeadVersion(step.Subject); productHead != nil {
			body, err := s.Graph.GetObject(productHead.ContentHash)
			if err != nil {
				return 0, err
			}
			inputPins = append(inputPins, map[string]any{
				"identity":     step.Subject,
				"version_seq":  int64(productHead.Seq),
				"content_hash": productHead.ContentHash,
				"role":         "base",
			})
			if err := s.stageBase(inputBodies, &dispatchInputs, step.Subject, productHead.Seq, body, productHead.ContentHash); err != nil {
				return 0, err
			}
		} else if len(step.Inputs) > 0 {
			// First integration for this lineage: no product head exists, so
			// the base is whatever the change-set itself pins — resolved
			// pin-verified (an anchored world base, or a recomposed packet
			// base). This is where an anchored lineage is born
			// (product-lineage-anchored@1).
			if csHead := state.HeadVersion(step.Inputs[0]); csHead != nil {
				csBody, err := s.Graph.GetObject(csHead.ContentHash)
				if err != nil {
					return 0, err
				}
				baseBody, _, baseHash, err := s.resolveChangeSetBase(state, step.Inputs[0], csBody)
				if err != nil {
					// An unresolvable base pin is the lane's finding to
					// type, not the driver's to fatal: dispatch without a
					// base and the integration refuses with a typed
					// apply_failure conflict (partial-failure discipline).
					baseBody = nil
				}
				if baseBody != nil {
					inputPins = append(inputPins, map[string]any{
						"content_hash": baseHash,
						"role":         "base",
					})
					if err := s.stageBase(inputBodies, &dispatchInputs, "composed-base", 0, baseBody, baseHash); err != nil {
						return 0, err
					}
				}
			}
		}
	}

	// A packet build stages against its composed base (D0010.C5): T_obs folded
	// with admitted ancestor change-sets in Work Graph index order. The lane
	// receives the base tree, the packet's write scope, and the packet pin it
	// must echo into the change-set — buildability is verified downstream.
	var buildPacket *workgraph.Packet
	var buildPacketManifest map[string]any
	buildBaseHash := ""
	if step.PassID == "build" && step.Packet != "" {
		wgHead := state.HeadVersion(step.Inputs[0])
		if wgHead == nil || wgHead.Stale {
			return 0, nil
		}
		wgBody, err := s.Graph.GetObject(wgHead.ContentHash)
		if err != nil {
			return 0, err
		}
		wg, err := workgraph.Parse(wgBody)
		if err != nil {
			return 0, err
		}
		packet, ok := wg.Packet(step.Packet)
		if !ok {
			return 0, fmt.Errorf("driver: packet %q absent from work-graph %s", step.Packet, step.Inputs[0])
		}
		baseBody, baseHash, err := s.composePacketBase(state, request.Subject, wg, step.Packet)
		if err != nil {
			return 0, err
		}
		buildPacket = &packet
		buildBaseHash = baseHash
		// The composed base is the tree the packet edits — content-addressed
		// context, not a provenance parent (the change-set derives_from the
		// work-graph packet element via the pinned work-graph, D0005.C2). Pin
		// it by content only, with no identity, so admission's reference check
		// skips it: the base may be T_obs folded with ancestors and equals no
		// single admitted version.
		inputPins = append(inputPins, map[string]any{
			"content_hash": baseHash,
			"role":         "base",
		})
		if err := s.stageBase(inputBodies, &dispatchInputs, "composed-base", 0, baseBody, baseHash); err != nil {
			return 0, err
		}
		buildPacketManifest = map[string]any{
			"work_graph_identity": step.Inputs[0],
			"work_graph_hash":     wgHead.ContentHash,
			"packet_id":           step.Packet,
			"write_scope":         toAnyStrings(packet.WriteScope),
			"base_hash":           baseHash,
		}
	}

	objectiveSummary := request.Note
	subjectMeta := map[string]string{
		"identity":  step.Subject,
		"principal": request.Principal,
		"request":   fmt.Sprintf("RQ-%d", request.Seq),
	}
	if buildPacket != nil {
		subjectMeta["packet_id"] = buildPacket.ID
		subjectMeta["work_graph_identity"] = step.Inputs[0]
		subjectMeta["work_graph_hash"] = state.HeadVersion(step.Inputs[0]).ContentHash
		subjectMeta["base_hash"] = buildBaseHash
		subjectMeta["write_scope"] = strings.Join(buildPacket.WriteScope, ",")
		objectiveSummary = fmt.Sprintf("build change-set for work-graph packet %q: %s", buildPacket.ID, buildPacket.Purpose)
	}
	manifest := map[string]any{
		"input_pins": toAnyList(inputPins),
		"environment": map[string]any{
			"decisions": toAnyStrings(pass.EnvironmentDecisions),
			"policies":  toAnyStrings(pass.EnvironmentPolicies),
			"catalogs":  []any{},
		},
		"prompt_asset_hashes": []any{},
		"lane_requirements":   []any{},
		"synthesis":           "single",
		"determinism":         defaultString(pass.Determinism, "D0"),
		"effects":             defaultString(pass.Effects, "E1"),
		"diagnostic_inputs":   toAnyStrings(step.DiagnosticIDs),
		"subject":             step.Subject,
		"step_id":             step.StepID,
		"objective":           objectiveSummary,
	}
	if buildPacketManifest != nil {
		manifest["packet"] = buildPacketManifest
	}
	if len(step.DiagnosticIDs) > 0 {
		objectiveSummary = "revise " + step.Subject + ": address every major finding in the pinned review ledger; the refused prior version is pinned for reference"
		if step.CheckDetail != "" {
			objectiveSummary = "revise " + step.Subject + ": a mechanical check refused it or its downstream lowering — " + step.CheckDetail + "; the refused artifact is pinned as diagnostic; produce a corrected version that resolves the refusal"
		}
		if step.RejectionDetail != "" {
			objectiveSummary = "revise " + step.Subject + ": the Principal REJECTED the prior version at its acceptance gate. The rejection reason, verbatim, is the binding steer — address it in full: " + step.RejectionDetail + " (the rejected version is pinned as diagnostic; preserve what the reason calls sound)"
		}
		manifest["objective"] = objectiveSummary
	}
	if step.Revalidate || step.PassID == "review" || step.PassID == "verification" {
		subject := state.HeadVersion(step.Subject)
		// A review of a revision candidate must review the CANDIDATE, not
		// the accepted head it proposes to supersede — the funnel exposed a
		// reviewer dutifully re-reviewing the old head, whose wrong-subject
		// evidence can never close the pending candidate's gate.
		if step.PassID == "review" && !step.Revalidate {
			if identityState, ok := state.Identities[step.Subject]; ok {
				if pending := latestCandidate(identityState); pending != nil &&
					(subject == nil || pending.Seq > subject.Seq) && !s.candidateRetired(state, identityState, pending) {
					subject = pending
				}
			}
		}
		if subject == nil {
			if identityState, ok := state.Identities[step.Subject]; ok {
				subject = latestCandidate(identityState)
			}
		}
		if subject == nil {
			return 0, nil
		}
		subjectPin := map[string]any{
			"identity":     step.Subject,
			"version_seq":  int64(subject.Seq),
			"content_hash": subject.ContentHash,
		}
		manifest["subject_pin"] = subjectPin
		manifest["input_pins"] = []any{subjectPin}
		if step.PassID == "verification" {
			objectiveSummary = fmt.Sprintf("verify %s (signal %d)", step.Subject, step.Signal)
		} else {
			objectiveSummary = "revalidate " + step.Subject
		}
		manifest["objective"] = objectiveSummary
		subjectMeta["subject_version"] = fmt.Sprint(subject.Seq)
		subjectMeta["content_hash"] = subject.ContentHash
		body, err := s.Graph.GetObject(subject.ContentHash)
		if err != nil {
			return 0, err
		}
		path := "inputs/00-" + sanitize(step.Subject)
		inputBodies = map[string][]byte{path: body}
		dispatchInputs = []backend.DispatchInput{{
			Identity:    step.Subject,
			VersionSeq:  subject.Seq,
			ContentHash: subject.ContentHash,
			Path:        path,
		}}
		// A code-bearing subject (a Change Set, verified with the code check
		// set) is verified against a real filesystem tree (RFC 0010 §5.2): flag
		// the lane and pin the composed base it was built against so composed
		// base + diff = the subject tree.
		if step.PassID == "verification" && step.CodeTree {
			subjectMeta["code_tree"] = "true"
			baseBody, baseIdentity, baseHash, err := s.resolveChangeSetBase(state, step.Subject, body)
			if err != nil {
				// An unresolvable or moved base pin means this head can never
				// re-verify — the lawful successor is a rebase-style rebuild
				// (a new candidate), not a fatal that takes the whole drive
				// session (and every other request's progress) down with it.
				// Skip the dispatch, noted; no run record has been written.
				report.Notes = append(report.Notes, fmt.Sprintf("verification skipped for %s: base unresolvable (%v)", step.Subject, err))
				return 0, nil
			}
			if baseBody != nil {
				manifest["input_pins"] = []any{subjectPin, map[string]any{
					"identity":     baseIdentity,
					"content_hash": baseHash,
					"role":         "base",
				}}
				if err := s.stageBase(inputBodies, &dispatchInputs, baseIdentity, 0, baseBody, baseHash); err != nil {
					return 0, err
				}
			}
		}
	}

	var environmentPolicies []backend.EnvironmentEntry
	if step.PassID == "verification" {
		if s.Checks == nil {
			return 0, nil
		}
		// The sealed manifest pins the check identities, registry version,
		// and the sandbox profile the Dual-Signal Rule's distinctness reads;
		// the bundle materializes the registry as declared environment.
		manifest["checks"] = toAnyStrings(step.CheckIDs)
		manifest["registry_version"] = int64(s.Checks.Registry.RegistryVersion)
		manifest["sandbox_profile"] = step.Profile
		registryHash := sha256Hex(s.Checks.Raw)
		manifest["registry_hash"] = registryHash
		policies := append([]string{}, pass.EnvironmentPolicies...)
		policies = append(policies, "checks")
		if env, ok := manifest["environment"].(map[string]any); ok {
			env["policies"] = toAnyStrings(policies)
		}
		subjectMeta["checks"] = strings.Join(step.CheckIDs, ",")
		subjectMeta["sandbox_profile"] = step.Profile
		subjectMeta["registry_version"] = fmt.Sprint(s.Checks.Registry.RegistryVersion)
		registryPath := "environment/checks.json"
		inputBodies[registryPath] = s.Checks.Raw
		environmentPolicies = append(environmentPolicies, backend.EnvironmentEntry{
			ID: "checks", Hash: registryHash, Path: registryPath,
		})
	}

	// Integration build check (RFC 0010 §7.2): when a code check set is
	// registered, thread it into the linker's dispatch so the lane materializes
	// the linked tree and refuses to stage a link that does not build — the
	// integration-checks gate stays execution-free; the checks run below the
	// seam. Gated on the code set, so a body-only registry is unchanged.
	if step.PassID == "integration" && s.Checks != nil {
		if codeIDs := s.Checks.Registry.Set(verificationCodeSet); len(codeIDs) > 0 {
			registryHash := sha256Hex(s.Checks.Raw)
			manifest["link_checks"] = toAnyStrings(codeIDs)
			manifest["registry_version"] = int64(s.Checks.Registry.RegistryVersion)
			manifest["registry_hash"] = registryHash
			if env, ok := manifest["environment"].(map[string]any); ok {
				policies := append([]string{}, pass.EnvironmentPolicies...)
				env["policies"] = toAnyStrings(append(policies, "checks"))
			}
			subjectMeta["link_checks"] = strings.Join(codeIDs, ",")
			subjectMeta["sandbox_profile"] = "v1-profile-a"
			subjectMeta["registry_version"] = fmt.Sprint(s.Checks.Registry.RegistryVersion)
			registryPath := "environment/checks.json"
			inputBodies[registryPath] = s.Checks.Raw
			environmentPolicies = append(environmentPolicies, backend.EnvironmentEntry{
				ID: "checks", Hash: registryHash, Path: registryPath,
			})
		}
	}

	manifestHash, err := store.RunManifestHash(manifest)
	if err != nil {
		return 0, err
	}
	// Concurrency pre-check (D0013.C6): in-flight lanes derive strictly
	// from the ledger fold — lane bindings of open runs — never from
	// process liveness. A step whose every capable backend sits at
	// max_lanes defers: nothing recorded, a session note, retried on the
	// next wake. Deferral is not a refusal.
	lanes := laneOccupancy(state)
	probe := scheduler.ReadyRun{
		PassID:           pass.ID,
		RunManifestHash:  manifestHash,
		LaneID:           "lane-1",
		Attempt:          attempts + 1,
		ExcludedAliasing: step.ExcludedAliasing,
	}
	if _, _, deferred := scheduler.Bind([]scheduler.ReadyRun{probe}, s.Backends, scheduler.Snapshot{Digest: emptySnapshotDigest()}, s.Policy.PolicyVersion, lanes); len(deferred) > 0 {
		report.Notes = append(report.Notes, "dispatch deferred (backend saturation): "+step.StepID)
		return 0, nil
	}
	deadlineClass := "batch"
	if pass.LatencyClass == "interactive" {
		deadlineClass = "interactive"
	}
	planRef := int64(0)
	if plan := state.Plans[request.Seq]; plan != nil {
		planRef = int64(plan.Seq)
	}

	// Record-then-dispatch, in order (RFC 0006).
	opened, err := s.append("pass_run_opened", "driver", []uint64{request.Seq}, map[string]any{
		"pass_id":          pass.ID,
		"contract_version": int64(pass.ContractVersion),
		"impl_version":     int64(pass.ImplVersion),
		"manifest":         manifest,
		"subject_pins":     []any{map[string]any{"identity": step.Subject}},
		"plan_ref":         planRef,
		"request_ref":      int64(request.Seq),
		"deadline_class":   deadlineClass,
	})
	if err != nil {
		return 0, err
	}

	run := scheduler.ReadyRun{
		RunRef:          opened.Seq,
		PassID:          pass.ID,
		RunManifestHash: manifestHash,
		LaneID:          "lane-1",
		// The attempt ordinal salts the dispatch id; the run's own ledger
		// seq is unique forever, so no re-attempt — including one licensed
		// by a resolved bounds escalation — can ever alias a prior
		// dispatch's bundle or its drained marker.
		Attempt:          int64(opened.Seq),
		ExcludedAliasing: step.ExcludedAliasing,
	}
	bindings, refusals, deferred := scheduler.Bind([]scheduler.ReadyRun{run}, s.Backends, scheduler.Snapshot{Digest: emptySnapshotDigest()}, s.Policy.PolicyVersion, lanes)
	if len(deferred) > 0 {
		// Unreachable through the normal path (the pre-check ran on the
		// same fold); close the opened run without consuming semantics.
		report.Notes = append(report.Notes, "dispatch deferred (backend saturation): "+step.StepID)
		if _, err := s.append("pass_run_closed", "driver", []uint64{opened.Seq}, s.failureClosure(
			opened.Seq, step.StepID, "capacity_starved", "deferred: backend saturation", nil)); err != nil {
			return 0, err
		}
		return 1, nil
	}
	if len(refusals) > 0 {
		escalation, err := s.append("escalation", "driver", []uint64{opened.Seq}, map[string]any{
			"reason":         string(refusals[0].Code),
			"detail":         refusals[0].Detail,
			"subjects":       []any{step.Subject},
			"blocking_scope": step.Subject,
			"run_ref":        int64(opened.Seq),
		})
		if err != nil {
			return 0, err
		}
		// Nothing was launched; the run closes immediately. Resolution of
		// the escalation licenses a fresh attempt.
		if _, err := s.append("pass_run_closed", "driver", []uint64{opened.Seq}, s.failureClosure(
			opened.Seq, step.StepID, "admission_refused", string(refusals[0].Code)+": "+refusals[0].Detail,
			[]uint64{escalation.Seq})); err != nil {
			return 0, err
		}
		return 1, nil
	}
	binding := bindings[0]
	if _, err := s.append("scheduling_decision", "driver", []uint64{opened.Seq}, map[string]any{
		"run_ref":         int64(opened.Seq),
		"backend_id":      binding.BackendID,
		"rule_id":         binding.RuleID,
		"policy_version":  int64(binding.PolicyVersion),
		"snapshot_digest": binding.SnapshotDigest,
	}); err != nil {
		return 0, err
	}
	if _, err := s.append("lane_binding", "driver", []uint64{opened.Seq}, map[string]any{
		"run_ref":                int64(opened.Seq),
		"lane_id":                binding.LaneID,
		"attempt":                binding.Attempt,
		"backend_id":             binding.BackendID,
		"dispatch_id":            binding.DispatchID,
		"declaration_hash":       binding.DeclarationHash,
		"independence_partition": binding.IndependencePartition,
	}); err != nil {
		return 0, err
	}

	dispatchManifest := backend.DispatchManifest{
		SchemaVersion: 1,
		DispatchID:    binding.DispatchID,
		Run: backend.DispatchRun{
			RunRef:          opened.Seq,
			RunManifestHash: manifestHash,
			PassID:          pass.ID,
			ContractVersion: pass.ContractVersion,
			ImplVersion:     pass.ImplVersion,
		},
		Lane:      backend.DispatchLane{LaneID: binding.LaneID, Role: "producer", Attempt: binding.Attempt},
		Objective: backend.Objective{Summary: objectiveSummary, Subject: subjectMeta},
		Inputs:    dispatchInputs,
		Environment: backend.Environment{
			Decisions: []backend.EnvironmentEntry{},
			Policies:  append([]backend.EnvironmentEntry{}, environmentPolicies...),
		},
		PromptAssets: []backend.PromptAsset{},
		Workspace: backend.WorkspaceSpec{
			EffectClass: workspaceEffect(pass.Effects),
			WriteScope:  backend.WriteScope{Allow: []string{"**"}, Deny: []string{}},
		},
		Expected:   s.expectedOutputs(pass, step),
		Submission: backend.SubmissionSpec{SpoolPath: "spool/submissions/" + binding.DispatchID},
	}
	bundleDir, err := backend.WriteDispatchBundle(s.Spool, dispatchManifest, inputBodies)
	if err != nil {
		return 0, err
	}
	adapter, ok := s.Adapters[binding.BackendID]
	if !ok {
		report.Notes = append(report.Notes, "dispatch refused: no adapter for backend "+binding.BackendID)
		return 1, nil
	}
	if _, err := adapter.Dispatch(filepath.Join(bundleDir, "manifest.json")); err != nil {
		report.Notes = append(report.Notes, "dispatch refused: "+err.Error())
	}
	return 1, nil
}

func (s *Session) escalateRevisionBounds(state *State, request *RequestState, step planStep) (int, error) {
	for _, escalation := range state.Escalations {
		if !escalation.Resolved && strings.Contains(escalation.Detail, step.Subject) && escalation.Reason == "bounds_exhausted" {
			return 0, nil
		}
	}
	if _, err := s.append("escalation", "driver", []uint64{request.Seq}, map[string]any{
		"reason":         "bounds_exhausted",
		"budget_kind":    "revision",
		"detail":         "revision budget exhausted for " + step.Subject,
		"subjects":       []any{step.Subject},
		"blocking_scope": step.Subject,
	}); err != nil {
		return 0, err
	}
	return 1, nil
}

func (s *Session) escalateBounds(state *State, request *RequestState, step planStep) (int, error) {
	for _, escalation := range state.Escalations {
		if !escalation.Resolved && strings.Contains(escalation.Detail, step.StepID) {
			return 0, nil
		}
	}
	if _, err := s.append("escalation", "driver", []uint64{request.Seq}, map[string]any{
		"reason":         "bounds_exhausted",
		"budget_kind":    "redispatch",
		"detail":         "attempt budget exhausted for " + step.StepID,
		"subjects":       []any{step.Subject},
		"blocking_scope": step.Subject,
	}); err != nil {
		return 0, err
	}
	return 1, nil
}

func (s *Session) expectedOutputs(pass PassSpec, step planStep) []backend.ExpectedOut {
	var out []backend.ExpectedOut
	if step.PassID == "verification" {
		// One receipt per pinned check plus the report, all evidence.
		for i := range step.CheckIDs {
			out = append(out, backend.ExpectedOut{
				OutputID:  fmt.Sprintf("receipt-%02d", i),
				Kind:      "receipt",
				Identity:  receiptIdentity(step.Subject, step.Signal, i),
				Placement: "stored",
				Required:  true,
			})
		}
		out = append(out, backend.ExpectedOut{
			OutputID:  "verification-report",
			Kind:      "verification-report",
			Identity:  reportIdentity(step.Subject, step.Signal),
			Placement: "stored",
			Required:  true,
		})
		return out
	}
	produces := pass.Produces
	if step.PassID == "review" {
		produces = []string{"review-ledger"}
	}
	for _, kind := range produces {
		placement := "stored"
		identity := step.Subject
		if step.PassID == "review" {
			identity = "evidence/review/" + sanitize(step.Subject) + "/" + step.StepID[strings.LastIndex(step.StepID, "/")+1:]
		}
		if spec, ok := s.Catalog.Kinds[kind]; ok && spec.Role == "product" {
			placement = "integrated"
		}
		out = append(out, backend.ExpectedOut{
			OutputID:  kind,
			Kind:      kind,
			Identity:  identity,
			Placement: placement,
			Required:  true,
		})
	}
	return out
}

// laneOccupancy derives per-backend lanes in flight strictly from the
// ledger fold (D0013.C6): a lane binding whose run has no closure is in
// flight. Never process liveness; never an advisory read.
func laneOccupancy(state *State) map[string]int {
	lanes := map[string]int{}
	for _, run := range state.Runs {
		if run.Open() && run.BackendID != "" {
			lanes[run.BackendID]++
		}
	}
	return lanes
}

// courtesyAbort issues the advisory abort for a superseded dispatch —
// courtesy ordering under the winner rule, never correctness. A failure is
// noted and not retried into a guarantee; a degraded abort (deleted hint)
// is indistinguishable from success here and treated as such.
func (s *Session) courtesyAbort(run *RunState, report *Report) {
	if run.DispatchID == "" || run.BackendID == "" {
		return
	}
	adapter, ok := s.Adapters[run.BackendID]
	if !ok {
		return
	}
	if err := adapter.Abort(run.DispatchID); err != nil {
		report.Notes = append(report.Notes,
			"courtesy abort failed for "+run.DispatchID+": "+err.Error())
	}
}

// --- sweep ---

func (s *Session) sweep(report *Report) (int, error) {
	state, err := s.fold()
	if err != nil {
		return 0, err
	}
	actions := 0
	now := s.Now().UTC()
	for _, runSeq := range sortedRunSeqs(state) {
		run := state.Runs[runSeq]
		if !run.Open() || run.OpenedAt.IsZero() {
			continue
		}
		// A run whose binding escalation the Principal resolved with
		// `reissue` closes now: nothing was ever launched for it, and the
		// resolution licenses a fresh attempt.
		reissued := false
		for _, escalation := range state.Escalations {
			if escalation.RunRef == run.Seq && escalation.Resolved && escalation.Disposition == "reissue" {
				reissued = true
			}
		}
		if reissued {
			s.courtesyAbort(run, report)
			if _, err := s.append("pass_run_closed", "driver", []uint64{run.Seq}, map[string]any{
				"run_ref": int64(run.Seq),
				"outcome": "superseded_by_redispatch",
				"detail":  "binding escalation resolved: reissue",
			}); err != nil {
				return actions, err
			}
			actions++
			continue
		}
		// A run whose dispatch bundle is absent can never submit: the
		// record-then-dispatch crash window (record written, bundle write
		// failed or was cleared). Presumed dead now — no live lane exists
		// to wait out a deadline for.
		bundleGone := run.DispatchID != "" &&
			!pathExists(s.Spool.DispatchDir(run.DispatchID))
		if !bundleGone && now.Sub(run.OpenedAt) <= s.Policy.DeadlineFor(run.DeadlineClass) {
			continue
		}
		if s.abandonedInThis >= s.Policy.AbandonmentCap {
			report.Notes = append(report.Notes, "abandonment cap hit; remaining overdue runs deferred")
			break
		}
		if bundleGone {
			// A provisional adjudication, never a fact of death (RFC 0006).
			if _, err := s.append("pass_run_closed", "driver", []uint64{run.Seq}, map[string]any{
				"run_ref":         int64(run.Seq),
				"outcome":         "abandoned",
				"observed_active": int64(observedActive(run, now) / time.Second),
			}); err != nil {
				return actions, err
			}
			// Courtesy abort after the closure is recorded: stop the lapsed
			// lane burning budget; a committed submission stays untouched and
			// still drains provisionally (finished work is never discarded).
			s.courtesyAbort(run, report)
			s.abandonedInThis++
			actions++
			continue
		}
		decision := spoolclose.ScanClose(spoolclose.Lane{
			LaneID:         run.LaneID,
			AgeSeconds:     durationSecondsInt(observedActive(run, now)),
			HorizonSeconds: durationSecondsInt(s.Policy.DeadlineFor(run.DeadlineClass)),
			IsWinner:       state.LaneWon(run),
		})
		if !decision.Close || decision.Mode != spoolclose.ModeHorizon {
			continue
		}
		// A provisional adjudication, never a fact of death (RFC 0006).
		if _, err := s.appendPassRunClosedV2([]uint64{run.Seq}, map[string]any{
			"run_ref":         int64(run.Seq),
			"outcome":         "abandoned",
			"closure_source":  "horizon",
			"scan_close_mode": string(spoolclose.ModeHorizon),
			"closure_reason":  decision.Reason,
			"observed_active": int64(observedActive(run, now) / time.Second),
		}); err != nil {
			return actions, err
		}
		// Courtesy abort after the closure is recorded: stop the lapsed
		// lane burning budget; a committed submission stays untouched and
		// still drains provisionally (finished work is never discarded).
		s.courtesyAbort(run, report)
		s.abandonedInThis++
		actions++
	}
	return actions, nil
}

// --- quiescence ---

func (s *Session) quiescenceReason(state *State) string {
	openRequests := false
	for _, request := range state.Requests {
		if !request.Satisfied && !request.Canceled {
			openRequests = true
		}
	}
	if !openRequests {
		if len(state.Requests) > 0 {
			return "satisfied"
		}
		return "idle"
	}
	if len(s.acceptanceQueue(state)) > 0 {
		return "awaiting_principal"
	}
	for _, escalation := range state.Escalations {
		if !escalation.Resolved {
			return "awaiting_principal"
		}
	}
	for _, run := range state.Runs {
		if run.Open() {
			return "awaiting_submissions"
		}
	}
	return "awaiting_capacity"
}

// acceptanceQueue lists candidates whose earlier gates closed and whose
// acceptance gate awaits Principal authority.
func (s *Session) acceptanceQueue(state *State) []QueueItem {
	var queue []QueueItem
	for _, id := range sortedIdentityIDs(state) {
		identity := state.Identities[id]
		candidate := latestCandidate(identity)
		if candidate == nil {
			continue
		}
		kind, ok := s.Catalog.Kinds[candidate.Kind]
		if !ok || kind.Role == "evidence" {
			continue
		}
		pendingAcceptance := ""
		ready := true
		for _, gateID := range kind.Gates {
			spec := s.Catalog.Gates[gateID]
			key := gateKey{Identity: id, Version: candidate.Seq, GateID: gateID}
			latest := latestResult(state.GateResults[key])
			switch spec.Class {
			case "acceptance":
				if latest == nil {
					pendingAcceptance = gateID
				} else if latest.Outcome != "pass" {
					ready = false
				}
			default:
				if latest == nil || latest.Outcome != "pass" {
					ready = false
				}
			}
		}
		if ready && pendingAcceptance != "" {
			queue = append(queue, QueueItem{
				Identity: id,
				Version:  candidate.Seq,
				Kind:     candidate.Kind,
				GateID:   pendingAcceptance,
			})
		}
	}
	return queue
}

func (s *Session) nextHorizon(state *State) string {
	var horizon time.Time
	for _, run := range state.Runs {
		if !run.Open() || run.OpenedAt.IsZero() {
			continue
		}
		deadline := run.OpenedAt.Add(s.Policy.DeadlineFor(run.DeadlineClass))
		if horizon.IsZero() || deadline.Before(horizon) {
			horizon = deadline
		}
	}
	if horizon.IsZero() {
		return ""
	}
	return horizon.UTC().Format(time.RFC3339)
}

func (s *Session) appendSessionRecord(state *State, cursorStart uint64, report Report) (uint64, error) {
	drained := append([]string(nil), report.Drained...)
	sort.Strings(drained)
	counts := map[string]any{}
	for phase, count := range report.ActionCounts {
		counts[phase] = int64(count)
	}
	result, err := s.append("drive_session_record", "driver", nil, map[string]any{
		"trigger":           s.Trigger,
		"cursor_range":      []any{int64(cursorStart), int64(state.LastSeq)},
		"drained":           toAnyStrings(drained),
		"action_counts":     counts,
		"deferrals":         []any{},
		"next_horizon":      report.NextHorizon,
		"quiescence_reason": report.Quiescence,
	})
	if err != nil {
		return 0, err
	}
	return result.Seq, nil
}

func (s *Session) writeProjections(state *State, report Report) error {
	status := BuildStatus(state, s.Catalog, s.acceptanceQueue(state), report, s.Now().UTC())
	derivedDir := filepath.Join(s.Graph.GraphDir, "derived")
	if err := os.MkdirAll(derivedDir, 0o700); err != nil {
		return err
	}
	raw, err := json.MarshalIndent(status, "", "  ")
	if err != nil {
		return err
	}
	raw = append(raw, '\n')
	if err := os.WriteFile(filepath.Join(derivedDir, "status.json"), raw, 0o600); err != nil {
		return err
	}
	horizon := map[string]any{"next_horizon": report.NextHorizon}
	horizonRaw, err := json.MarshalIndent(horizon, "", "  ")
	if err != nil {
		return err
	}
	horizonRaw = append(horizonRaw, '\n')
	return os.WriteFile(filepath.Join(derivedDir, "next-horizon.json"), horizonRaw, 0o600)
}

// --- helpers ---

func subjectIdentity(subject, kind string) string {
	return subject + "/" + kind
}

func sanitize(identity string) string {
	return strings.NewReplacer("/", "-", " ", "-").Replace(identity)
}

func workspaceEffect(effects string) string {
	if effects == "E0" {
		return "E0"
	}
	return "E1"
}

func emptySnapshotDigest() string {
	sum := sha256.Sum256([]byte("telemetry:empty:v1"))
	return hex.EncodeToString(sum[:])
}

func sha256Hex(raw []byte) string {
	sum := sha256.Sum256(raw)
	return hex.EncodeToString(sum[:])
}

func defaultString(value, fallback string) string {
	if value == "" {
		return fallback
	}
	return value
}

func toAnySeqs(values []uint64) []any {
	out := make([]any, len(values))
	for i, value := range values {
		out[i] = int64(value)
	}
	return out
}

func toAnyStrings(values []string) []any {
	out := make([]any, len(values))
	for i, value := range values {
		out[i] = value
	}
	return out
}

func toAnyList(values []any) []any {
	if values == nil {
		return []any{}
	}
	return values
}

func sortedIdentityIDs(state *State) []string {
	ids := make([]string, 0, len(state.Identities))
	for id := range state.Identities {
		ids = append(ids, id)
	}
	sort.Strings(ids)
	return ids
}

func sortedRequestSeqs(state *State) []uint64 {
	seqs := make([]uint64, 0, len(state.Requests))
	for seq := range state.Requests {
		seqs = append(seqs, seq)
	}
	sort.Slice(seqs, func(i, j int) bool { return seqs[i] < seqs[j] })
	return seqs
}

func sortedRunSeqs(state *State) []uint64 {
	seqs := make([]uint64, 0, len(state.Runs))
	for seq := range state.Runs {
		seqs = append(seqs, seq)
	}
	sort.Slice(seqs, func(i, j int) bool { return seqs[i] < seqs[j] })
	return seqs
}

// stageBase writes a product/composed base into a dispatch bundle. An
// anchored base is expanded at dispatch — the planning side owns world
// reads (lanes stay world-blind) — and travels as two hash-verified
// inputs: the small anchored pin body at inputs/00-base-pin (the hash
// change-sets pin) and the expanded tree at inputs/01-base (what lanes
// materialize). Inline bases pass through unchanged.
func (s *Session) stageBase(inputBodies map[string][]byte, dispatchInputs *[]backend.DispatchInput, baseIdentity string, baseSeq uint64, baseBody []byte, baseHash string) error {
	product, err := changeset.ParseProduct(baseBody)
	if err != nil {
		return err
	}
	if product.Anchor == nil {
		inputBodies["inputs/01-base"] = baseBody
		*dispatchInputs = append(*dispatchInputs, backend.DispatchInput{
			Identity:    baseIdentity,
			VersionSeq:  baseSeq,
			ContentHash: baseHash,
			Path:        "inputs/01-base",
		})
		return nil
	}
	expanded, err := gitanchor.Expand(s.Graph.RepoRoot, product)
	if err != nil {
		return err
	}
	expandedBody, err := changeset.CanonicalProduct(expanded)
	if err != nil {
		return err
	}
	expandedHash, err := changeset.TreeHash(expanded)
	if err != nil {
		return err
	}
	inputBodies["inputs/00-base-pin"] = baseBody
	*dispatchInputs = append(*dispatchInputs, backend.DispatchInput{
		Identity:    baseIdentity + "/pin",
		VersionSeq:  baseSeq,
		ContentHash: baseHash,
		Path:        "inputs/00-base-pin",
	})
	inputBodies["inputs/01-base"] = expandedBody
	*dispatchInputs = append(*dispatchInputs, backend.DispatchInput{
		Identity:    baseIdentity,
		ContentHash: expandedHash,
		Path:        "inputs/01-base",
	})
	return nil
}

func pathExists(path string) bool {
	_, err := os.Stat(path)
	return err == nil
}

// harvestArtifact resolves the artifact identity a harvest subject names:
// "<artifact-identity>/harvest/<posture>" — the convention that lets the
// delegation policy bound agent issuance by subject pattern while the
// conjuncts still reach the real artifact.
func harvestArtifact(subject string) string {
	if idx := strings.Index(subject, "/harvest/"); idx > 0 {
		return subject[:idx]
	}
	return ""
}

// reviewAdmittedUnder finds a Review Ledger over the given head produced by
// a run of this request — the non-vacuous core of the harvest review
// posture: old reviews never satisfy a new request.
func (s *Session) reviewAdmittedUnder(state *State, request *RequestState, head *VersionState) *VersionState {
	for _, id := range sortedIdentityIDs(state) {
		evidence := state.Identities[id]
		if evidence.Kind != "review-ledger" {
			continue
		}
		for i := len(evidence.Order) - 1; i >= 0; i-- {
			version := evidence.Versions[evidence.Order[i]]
			if version.ReviewSubjectHash != head.ContentHash {
				continue
			}
			if run, ok := state.Runs[version.ProducedByRun]; ok && run.RequestRef == request.Seq {
				return version
			}
		}
	}
	return nil
}

// CurrentState exposes the current fold for read-side consumers (harvest
// issuance cadence and candidate selection) — derived, never authoritative.
func (s *Session) CurrentState() (*State, error) {
	return s.fold()
}

// versionsSinceLicense counts an identity's versions created after the
// latest resolved bounds escalation naming it — the revision-budget twin of
// the redispatch licensing rule.
func versionsSinceLicense(state *State, identity *IdentityState, subject string) int {
	var licensedAfter uint64
	for _, escalation := range state.Escalations {
		if escalation.Resolved && strings.Contains(escalation.Detail, subject) &&
			escalation.Seq > licensedAfter {
			licensedAfter = escalation.Seq
		}
	}
	count := 0
	for _, seq := range identity.Order {
		if seq > licensedAfter {
			count++
		}
	}
	return count
}

// --- schedule ---

// schedule is the post-quiescence planner-scheduling phase
// (planner-auto-schedules-the-backlog@1): walk the declared backlog in
// declared order (C5 — slice index only, no map iteration, no randomness,
// no clock) and append at most Policy.BacklogCapPerDrive planner-provenance
// compilation requests toward named target states that are neither
// satisfied nor under active request (C3, C4, C7). Deterministic
// bookkeeping over declared state, by construction: the phase appends ONLY
// compilation_request records — it contains no call that appends a
// gate_result, resolution_event, acceptance, or any other authority record,
// and no code path that writes the backlog file (C1, C12).
func (s *Session) schedule() (int, error) {
	if len(s.Backlog) == 0 {
		return 0, nil
	}
	state, err := s.fold()
	if err != nil {
		return 0, err
	}
	// Satisfied and active sets key on the target-state identifier alone
	// (C3/C4), derived from the existing request fold: satisfied when any
	// folded request toward the target carries Satisfied, actively requested
	// when any folded request toward it is neither Satisfied nor Canceled.
	// The active set is a mutable working set for the remainder of this
	// pass: each issuance inserts its target before the next entry is
	// inspected, so a later backlog entry naming the same target — under the
	// same or a different subject — skips under C4 within this same drive,
	// and one drive never appends two planner requests toward one
	// target-state identifier regardless of cap.
	satisfied := map[string]bool{}
	active := map[string]bool{}
	for _, request := range state.Requests {
		switch {
		case request.Satisfied:
			satisfied[request.TargetID] = true
		case !request.Canceled:
			active[request.TargetID] = true
		}
	}
	issued := 0
	for index, entry := range s.Backlog {
		if s.backlogIssuedInThis >= s.Policy.BacklogCapPerDrive {
			break
		}
		if satisfied[entry.Target] || active[entry.Target] {
			continue // skipped entries consume no cap (C6)
		}
		// One selected entry, one captured request (C8), through the shared
		// issuance path — an uncataloged or conjunct-less backlog target
		// refuses here exactly as it would for a principal.
		if _, err := IssueRequest(s.Graph, s.Catalog, RequestOptions{
			Subject:            entry.Subject,
			TargetID:           entry.Target,
			Note:               fmt.Sprintf("planner-scheduled from the declared backlog (entry %d)", index),
			Now:                s.Now,
			Instance:           s.Instance,
			IssuerKind:         "planner",
			ScheduledFromEntry: index,
		}); err != nil {
			return issued, err
		}
		active[entry.Target] = true
		s.backlogIssuedInThis++
		issued++
	}
	return issued, nil
}

