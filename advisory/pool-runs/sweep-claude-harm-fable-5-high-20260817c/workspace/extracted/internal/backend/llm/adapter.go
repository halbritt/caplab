package llm

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"syscall"
	"time"

	"github.com/halbritt/striatum-next/internal/backend"
)

// RefusalCode is a typed dispatch refusal (RFC 0007 dispatch verb contract).
type RefusalCode string

const (
	RefusalCapacityExhausted      RefusalCode = "capacity_exhausted"
	RefusalRuntimeUnavailable     RefusalCode = "runtime_unavailable"
	RefusalUnsupportedPass        RefusalCode = "unsupported_pass"
	RefusalEffectClassUnsupported RefusalCode = "effect_class_unsupported"
	RefusalDeclarationMismatch    RefusalCode = "declaration_mismatch"
	RefusalSpoolUnsuitable        RefusalCode = "spool_unsuitable"
)

// Refusal is a typed dispatch refusal error.
type Refusal struct {
	Code   RefusalCode
	Detail string
}

func (r Refusal) Error() string {
	return fmt.Sprintf("llm: dispatch refused %s: %s", r.Code, r.Detail)
}

// DispatchRefusalCode implements backend.DispatchRefusal.
func (r Refusal) DispatchRefusalCode() string { return string(r.Code) }

// Adapter hosts one-shot LLM lanes behind the file seam. The dispatch verb
// validates, checks committed-idempotence, forks the detached Lane
// Supervisor, verifies its signalable kill domain, writes the Supervisor
// Hint, and returns — in that order (D0013.C1); the seam sees exactly two
// states (committed or nothing), and acceptance is durable at return.
type Adapter struct {
	Config    Config
	Spool     backend.Spool
	StoreRoot string
	Now       func() time.Time

	// Surface is the argv prefix of this backend's process surface — the
	// supervisor exec target. A bare command name resolves on PATH.
	Surface []string

	// Declaration, KeysDir, and IsolationDir travel to the supervision
	// entry, which self-loads its configuration, seal key, and lane
	// credential (the adapter passes paths, never secrets, on the command
	// line). IsolationDir absent keeps the single-uid posture.
	Declaration  string
	KeysDir      string
	IsolationDir string

	// WakeCmd is the post-commit wake argv forwarded to the supervisor.
	// The adapter learns nothing but a command line (A7 undisturbed).
	WakeCmd []string

	// WallClockLimit bounds one runtime invocation. Advisory mechanics,
	// never a semantic deadline (those live in driver policy).
	WallClockLimit time.Duration

	// SealKey seals submissions committed by the in-process Supervisor
	// path (the supervision entry loads its own from KeysDir).
	SealKey []byte
}

var supportedEffects = map[string]bool{"E0": true, "E1": true}

// Dispatch executes one dispatch bundle to a committed submission or nothing.
func (a *Adapter) Dispatch(manifestPath string) (string, error) {
	manifest, err := backend.ReadDispatchManifest(manifestPath)
	if err != nil {
		return "", Refusal{Code: RefusalDeclarationMismatch, Detail: err.Error()}
	}
	if manifest.SchemaVersion >= 2 {
		if err := validateDeclarationPin(a.Declaration, manifest); err != nil {
			return "", Refusal{Code: RefusalDeclarationMismatch, Detail: err.Error()}
		}
	}
	if !supportedEffects[manifest.Workspace.EffectClass] {
		return "", Refusal{Code: RefusalEffectClassUnsupported, Detail: manifest.Workspace.EffectClass}
	}
	if !a.Config.Supports(manifest.Run.PassID) {
		return "", Refusal{Code: RefusalUnsupportedPass, Detail: manifest.Run.PassID}
	}
	if _, err := exec.LookPath(a.Config.Command[0]); err != nil {
		return "", Refusal{Code: RefusalRuntimeUnavailable, Detail: a.Config.Command[0] + " not found"}
	}
	if err := a.checkSpoolPlacement(); err != nil {
		return "", err
	}
	if err := a.Spool.EnsureLayout(); err != nil {
		return "", err
	}

	target := a.Spool.SubmissionDir(manifest.DispatchID)
	if _, err := os.Stat(target); err == nil {
		return target, nil // already committed; two states only
	}
	// Non-authoritative idempotence (D0013.C1): a hint whose token still
	// names a live incarnation means a supervisor already owns this
	// dispatch — succeed without forking. Token verification only; a
	// wrong hint's worst case is a duplicate execution, lawful under
	// pass purity and the rename winner.
	if hint, err := readHint(a.Spool, manifest.DispatchID); err == nil && hintTokenLive(hint) {
		return target, nil
	}
	return a.detach(manifest, manifestPath)
}

func validateDeclarationPin(path string, manifest backend.DispatchManifest) error {
	if path == "" || manifest.Lane.DeclarationHash == "" {
		return errors.New("v2 dispatch lacks a resolvable declaration pin")
	}
	raw, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	sum := sha256.Sum256(raw)
	currentHash := hex.EncodeToString(sum[:])
	if currentHash != manifest.Lane.DeclarationHash {
		return fmt.Errorf("current declaration hash %s differs from pinned %s", currentHash, manifest.Lane.DeclarationHash)
	}
	return nil
}

// Abort reaches detached work through the Supervisor Hint on the four
// fixed branches (D0013.C5). Advisory, idempotent, unknown-id-safe; it
// never touches a committed submission on any branch.
func (a *Adapter) Abort(dispatchID string) error {
	hint, err := readHint(a.Spool, dispatchID)
	if err != nil {
		// Absent (or unreadable) hint: cleanup-only. Complete when the
		// dispatch was never accepted or has concluded; honestly partial
		// when the hint was deleted over a live lane — that lane runs on
		// lawfully, bounded by its own dispatch budget (C4b) below the
		// seam and the horizon above it. Never a completeness claim.
		return a.reclaimResidue(dispatchID)
	}
	if !hintTokenLive(hint) {
		// Present but unverifiable: the named supervisor is dead, and by
		// fate-sharing (C10) its runtime tree died with it — cleanup is
		// complete.
		return a.reclaimResidue(dispatchID)
	}
	// The token verifies: a live supervisor owns this lane. Signal the
	// group — TERM, bounded grace, KILL — reaching the runtime, which
	// C10 confines to that group.
	grace := a.Config.AbortGrace
	if grace == 0 {
		grace = 5 * time.Second
	}
	if err := syscall.Kill(-hint.PGID, syscall.SIGTERM); err != nil {
		if !hintTokenLive(hint) {
			return a.reclaimResidue(dispatchID) // it concluded under us
		}
		// A verifying token whose named kill domain cannot be signaled
		// is a failed abort over a live lane: reclaim nothing, delete
		// nothing, report incompleteness. A conforming adapter cannot
		// produce this state (S1); behavior here is defined against
		// defect and hostility alike.
		return fmt.Errorf("abort_incomplete: kill domain -%d unsignalable (%v) while supervisor %d verifies live; nothing reclaimed", hint.PGID, err, hint.PID)
	}
	if waitTokenDead(hint, grace) {
		return a.reclaimResidue(dispatchID)
	}
	if err := syscall.Kill(-hint.PGID, syscall.SIGKILL); err != nil || !waitTokenDead(hint, grace) {
		return fmt.Errorf("abort_incomplete: supervisor %d survived TERM-grace-KILL on group -%d; nothing reclaimed", hint.PID, hint.PGID)
	}
	return a.reclaimResidue(dispatchID)
}

// reclaimResidue removes in-flight residue only — the workspace tree and
// the advisory dir. Committed submissions are admission's to reclaim. The
// detached supervisor's log is retained at its driver-visible home first
// (retainSupervisorLog): an abort can reach a live lane whose own supervisor
// never gets to run its own Run()-driven retention.
func (a *Adapter) reclaimResidue(dispatchID string) error {
	retainSupervisorLog(a.Spool, dispatchID)
	if err := os.RemoveAll(a.Spool.WorkspaceDir(dispatchID)); err != nil {
		return err
	}
	return os.RemoveAll(a.Spool.AdvisoryDir(dispatchID))
}

// waitTokenDead polls the hint's incarnation until it no longer verifies.
func waitTokenDead(hint supervisorHint, within time.Duration) bool {
	deadline := time.Now().Add(within)
	for {
		if !hintTokenLive(hint) {
			return true
		}
		if time.Now().After(deadline) {
			return false
		}
		time.Sleep(50 * time.Millisecond)
	}
}

// Janitor reclaims residue for non-live dispatches; the live set arrives as
// verb input (A7). A dead lane's workspace entry retains its supervisor log
// first (retainSupervisorLog) — the janitor sweep is exactly the abandonment
// path a supervisor that dies before its own Run()-driven retention leaves
// behind, and the log survives it under the declared retention window.
func (a *Adapter) Janitor(live map[string]bool, adjudicated map[string]bool) error {
	dirs := []struct {
		path       string
		retainLogs bool
	}{
		{filepath.Join(a.Spool.Root, "dispatch"), false},
		{filepath.Join(a.Spool.Root, "workspaces"), true},
		{filepath.Join(a.Spool.Root, "advisory"), false},
	}
	for _, d := range dirs {
		entries, err := os.ReadDir(d.path)
		if err != nil {
			if errors.Is(err, os.ErrNotExist) {
				continue
			}
			return err
		}
		for _, entry := range entries {
			if live[entry.Name()] {
				continue
			}
			if d.retainLogs {
				retainSupervisorLog(a.Spool, entry.Name())
			}
			if err := os.RemoveAll(filepath.Join(d.path, entry.Name())); err != nil {
				return err
			}
		}
	}
	submissions := filepath.Join(a.Spool.Root, "spool", "submissions")
	entries, err := os.ReadDir(submissions)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return nil
		}
		return err
	}
	for _, entry := range entries {
		if !adjudicated[entry.Name()] {
			continue
		}
		if err := os.RemoveAll(filepath.Join(submissions, entry.Name())); err != nil {
			return err
		}
	}
	return nil
}

// ProbeReport is the probe verb's self-description.
type ProbeReport struct {
	BackendID        string `json:"backend_id"`
	RuntimePresent   bool   `json:"runtime_present"`
	RuntimeVersion   string `json:"runtime_version"`
	SpoolWritable    bool   `json:"spool_writable"`
	SpoolPlacementOK bool   `json:"spool_placement_ok"`
	Detail           string `json:"detail,omitempty"`
}

// Probe answers "could this backend work right now?".
func (a *Adapter) Probe() ProbeReport {
	report := ProbeReport{BackendID: a.Config.BackendID}
	if _, err := exec.LookPath(a.Config.Command[0]); err == nil {
		report.RuntimePresent = true
		report.RuntimeVersion = a.Config.runtimeVersion()
	}
	if err := a.Spool.EnsureLayout(); err == nil {
		report.SpoolWritable = true
	} else {
		report.Detail = err.Error()
	}
	if err := a.checkSpoolPlacement(); err == nil {
		report.SpoolPlacementOK = true
	} else if report.Detail == "" {
		report.Detail = err.Error()
	}
	return report
}

func (a *Adapter) checkSpoolPlacement() error {
	if a.StoreRoot == "" {
		return nil
	}
	if err := a.Spool.EnsureLayout(); err != nil {
		return err
	}
	same, err := backend.SameFilesystem(a.Spool.Root, a.StoreRoot)
	if err != nil {
		return Refusal{Code: RefusalSpoolUnsuitable, Detail: err.Error()}
	}
	if !same {
		return Refusal{Code: RefusalSpoolUnsuitable, Detail: "spool and Graph Store are on different filesystems"}
	}
	return nil
}

// runtimeVersion probes the live version string (declaration
// version_discovery: probe). WaitDelay bounds the pipe wait: a runtime that
// mishandles --version and forks descendants must not stall the probe —
// orphans holding stdout are exactly the shape D0013.C10 warns about.
func (c Config) runtimeVersion() string {
	if len(c.VersionCommand) == 0 {
		return "unknown"
	}
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	cmd := exec.CommandContext(ctx, c.VersionCommand[0], c.VersionCommand[1:]...)
	cmd.WaitDelay = 2 * time.Second
	out, err := cmd.Output()
	if err != nil {
		return "unknown"
	}
	return strings.TrimSpace(strings.Split(string(out), "\n")[0])
}

