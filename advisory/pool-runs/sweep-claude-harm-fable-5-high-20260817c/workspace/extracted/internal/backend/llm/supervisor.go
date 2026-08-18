package llm

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"math/rand/v2"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
	"syscall"
	"time"

	"github.com/halbritt/striatum-next/internal/backend"
	"github.com/halbritt/striatum-next/internal/backend/supervise"
	"github.com/halbritt/striatum-next/internal/gate"
	"github.com/halbritt/striatum-next/internal/scf"
	spoolclose "github.com/halbritt/striatum-next/internal/spool"
)

// Supervisor owns the post-acceptance lifecycle of exactly one dispatch
// (D0013.C2): the bounded internal-relaunch loop with pristine per-attempt
// reset (A2), pre-submission validation and shape repair, sealed submission
// assembly, and the rename commit (A4). Everything it needs rides the sealed
// bundle; it reads no ledger and holds no lease (A5/A6/A7).
//
// The runtime's whole tree lives under workspaces/<dispatch_id>/work/ —
// that subtree is what the per-attempt reset removes; the outer
// workspaces/<dispatch_id>/ directory is supervisor-owned residue, so the
// reset never unlinks the supervisor's own files.
type Supervisor struct {
	Config Config
	Spool  backend.Spool
	Now    func() time.Time

	// WallClockLimit overrides the declared invocation limit (clock 1 of
	// D0013.C4). Advisory mechanics, never a semantic deadline (those
	// live in driver policy).
	WallClockLimit time.Duration

	// SealKey, when set, seals submissions under the v1-hmac scheme
	// (RFC 0012); nil keeps the plain digest.
	SealKey []byte

	// LaneCredential, when set, drops the runtime to a dedicated uid/gid —
	// rung-2 isolation (D0012.C1). The runtime writes outputs the supervisor
	// (its own uid) reads back, so the per-attempt work tree is made
	// group-accessible to the lane gid. nil on a single-uid host: work stays
	// 0700, byte-identical to the pre-isolation path.
	LaneCredential *supervise.LaneCredential

	// WakeCmd, when set, is exec'd with "-trigger adapter_wake" appended
	// after the rename commit (D0013.C7). Non-authoritative: exit 4 gets
	// the bounded WakeRetries schedule, everything else abandons safely —
	// the standing timer and the post-quiescence re-scan are the floor.
	WakeCmd     []string
	WakeRetries []time.Duration
}

// invocationLimit is clock 1 (D0013.C4a): one runtime invocation's bound.
func (s *Supervisor) invocationLimit() time.Duration {
	if s.WallClockLimit > 0 {
		return s.WallClockLimit
	}
	if s.Config.InvocationLimit > 0 {
		return s.Config.InvocationLimit
	}
	return 30 * time.Minute
}

// dispatchBudget is clock 2 (D0013.C4b): the whole-dispatch bound. The
// manifest's advisory abort_after_s wins over the adapter-block default.
func (s *Supervisor) dispatchBudget(manifest backend.DispatchManifest) time.Duration {
	if raw, ok := manifest.Advisory["abort_after_s"]; ok {
		if seconds, ok := raw.(float64); ok && seconds > 0 {
			return time.Duration(seconds * float64(time.Second))
		}
	}
	if s.Config.DispatchBudget > 0 {
		return s.Config.DispatchBudget
	}
	return time.Hour
}

// Run executes one accepted dispatch to a committed submission or nothing,
// fires the post-commit wake, reclaims its own residue, and returns. The
// Driver's dispatch horizon (clock 3) is deliberately unknown here.
//
// Every controlled exit (success, budget expiry, relaunch exhaustion, or an
// internal execute/commit error) traverses emitTerminalReport — the single
// post-result terminal emission funnel — before the wake fires, so a woken
// Driver never scans ahead of the report that would accelerate its drain
// (stalls-need-no-judgment@3, clause 2). retainSupervisorLog runs alongside
// it, before reclaim unlinks the workspace tree holding the log's only
// on-disk copy, so the detached supervisor log survives at its
// driver-visible retained home regardless of how this dispatch concluded.
func (s *Supervisor) Run(manifest backend.DispatchManifest, bundleDir string) (string, error) {
	started := s.now()
	budget := s.dispatchBudget(manifest)
	target, outcome, err := s.runToResult(manifest, bundleDir, started, budget)
	s.emitTerminalReport(manifest, outcome)
	retainSupervisorLog(s.Spool, manifest.DispatchID)
	if err != nil {
		return "", err
	}
	s.wake()
	s.reclaim(manifest.DispatchID)
	return target, nil
}

// runToResult is Run's execute-then-commit body, isolated so every path out
// of it — success and error alike — flows through exactly one post-result
// point before Run decides whether to wake or propagate the error.
func (s *Supervisor) runToResult(manifest backend.DispatchManifest, bundleDir string, started time.Time, budget time.Duration) (string, runOutcome, error) {
	outcome, err := s.execute(manifest, bundleDir, started.Add(budget), budget)
	if err != nil {
		return "", outcome, err
	}
	target, err := s.commit(manifest, outcome, started, s.now())
	if err != nil {
		return "", outcome, err
	}
	return target, outcome, nil
}

// emitTerminalReport is the post-result terminal emission funnel
// (stalls-need-no-judgment@3, clause 2, emission half): it classifies this
// Run invocation's outcome into exactly one of the three permitted reported
// reasons — never the upcast-only unobserved sentinel — and makes one
// best-effort WriteTerminalReport commit through the same fsync-then-rename
// spool discipline as a work submission. A failure here (including an empty
// dispatch or lane id) is exactly the lapse the horizon backstop already
// recovers; it never blocks, retries, or alters Run's own return.
//
// An empty exitReason with outcome.launched true means a runtime invocation
// genuinely ran during this dispatch before a later internal step failed;
// the generic runtime_exit classification is truthful there and stands. An
// empty exitReason with outcome.launched false means execute returned
// before any runtime invocation ever started (attempt-0 render, workspace
// reset, preparation, or input-materialization failure). That is still a
// controlled post-acceptance supervisor exit, not an uncontrolled kill — the
// process is alive and running this very function — so it earns a report
// too; runtime_exit would misreport it (no runtime ever ran), so it
// classifies as relaunch_exhausted: no launch produced a result and no
// further launch will be attempted this dispatch. Absence stays reserved for
// an uncontrolled death that never reaches this function (the horizon
// backstop's actual territory) or a genuine best-effort write failure.
func (s *Supervisor) emitTerminalReport(manifest backend.DispatchManifest, outcome runOutcome) {
	reason := outcome.exitReason
	if reason == "" {
		reason = spoolclose.RuntimeExit
		if !outcome.launched {
			reason = spoolclose.RelaunchExhausted
		}
	}
	_ = backend.WriteTerminalReport(s.Spool, manifest.DispatchID, spoolclose.Envelope{
		LaneID:         manifest.Lane.LaneID,
		ExitReason:     reason,
		SupervisorTail: readFileTail(supervisorLogPath(s.Spool, manifest.DispatchID), spoolclose.SupervisorTailMaxBytes),
	})
}

// wake fires the non-authoritative post-commit wake: bounded retry on exit
// 4 (drive lease held), safe abandonment on everything else.
//
// The exec'd process starts in its own new process group (Setpgid), never
// the detached supervisor's own kill domain (the session/pgid Setsid
// establishes at fork, D0013.C5). A woken Driver that finds this lane
// reported terminal courtesy-aborts that domain by SIGTERMing -pgid
// (session.go's courtesyAbort); sharing the group would let that
// self-directed signal kill the wake-launched process alongside the
// supervisor it named, before it could finish draining or reclaiming.
func (s *Supervisor) wake() {
	if len(s.WakeCmd) == 0 {
		return
	}
	retries := s.WakeRetries
	if retries == nil {
		retries = []time.Duration{2 * time.Second, 10 * time.Second, 30 * time.Second}
	}
	argv := append(append([]string{}, s.WakeCmd...), "-trigger", "adapter_wake")
	for attempt := 0; ; attempt++ {
		cmd := exec.Command(argv[0], argv[1:]...)
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		cmd.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}
		err := cmd.Run()
		if err == nil {
			return
		}
		var exit *exec.ExitError
		if !errors.As(err, &exit) || exit.ExitCode() != 4 || attempt >= len(retries) {
			return // abandon safely; the standing timer is the floor
		}
		time.Sleep(retries[attempt] + rand.N(retries[attempt]/4))
	}
}

// reclaim removes the supervisor's own residue — the outer workspace tree
// and the advisory dir (hint included) — on the way out (D0013.C2).
func (s *Supervisor) reclaim(dispatchID string) {
	_ = os.RemoveAll(s.Spool.WorkspaceDir(dispatchID))
	_ = os.RemoveAll(s.Spool.AdvisoryDir(dispatchID))
}

// runOutcome is one supervised execution's result surface.
type runOutcome struct {
	prompt      string
	outputs     map[string][]byte
	relaunches  int
	attempts    []backend.AttemptClosure
	diagnostics []string
	exhaust     map[string][]byte

	// exitReason is execute's permitted-reason classification of how this
	// invocation concluded, consumed by emitTerminalReport. It starts unset:
	// a setup error (render, workspace reset, or input-materialization
	// failure) returns before any relaunch-loop verdict exists, and
	// emitTerminalReport falls back to spoolclose.RuntimeExit when launched
	// is also true (a runtime genuinely ran this dispatch) or
	// spoolclose.RelaunchExhausted when it is not (no runtime ever launched,
	// so no runtime_exit fact exists — but the exit is still controlled and
	// still earns a report). spoolclose.BudgetExpiry and
	// spoolclose.RelaunchExhausted are otherwise assigned only at the exact
	// point execute observes that more specific outcome.
	exitReason spoolclose.ExitReason

	// launched is set the moment execute starts a confined runtime
	// invocation (immediately before invoke). It distinguishes a dispatch
	// that never got a runtime running — no runtime_exit fact exists to
	// report — from one where a runtime genuinely ran before a later
	// internal step failed.
	launched bool
}

// workDir is the runtime-visible execution tree, pristine per attempt (A2).
func (s *Supervisor) workDir(dispatchID string) string {
	return filepath.Join(s.Spool.WorkspaceDir(dispatchID), "work")
}

// workTreeMode is 0700 under a single uid and 0770 when the runtime drops to
// a lane credential — the latter so the dropped runtime (lane uid, a member of
// the lane gid) can read materialized inputs and write outputs the supervisor
// (the owner) reads back. Ownership only; no contract change (D0012.C4).
func (s *Supervisor) workTreeMode() os.FileMode {
	if s.LaneCredential != nil {
		return 0o770
	}
	return 0o700
}

// prepareWorkTree makes the pristine per-attempt work/outputs tree. Under a
// lane credential it also sets the tree's group to the lane gid with the
// setgid bit, so files the runtime creates inherit the shared group; this
// needs the supervisor to own the tree (it does — it created it). On a
// single-uid host it is exactly os.MkdirAll(work/outputs, 0700).
func (s *Supervisor) prepareWorkTree(work string) error {
	mode := s.workTreeMode()
	outputs := filepath.Join(work, "outputs")
	if err := os.MkdirAll(outputs, mode); err != nil {
		return err
	}
	if s.LaneCredential == nil {
		return nil
	}
	for _, dir := range []string{work, outputs} {
		// -1 keeps the owning uid (the supervisor); only the group moves.
		if err := os.Chown(dir, -1, int(s.LaneCredential.GID)); err != nil {
			return err
		}
		if err := os.Chmod(dir, mode|os.ModeSetgid); err != nil {
			return err
		}
	}
	return nil
}

// materializeInputs copies every declared environment body and pinned input
// from the sealed bundle into the pristine work tree at its manifest path.
// The prompt may inline ordinary text, but large or NUL-bearing argv-mode
// context is referenced by exactly these paths. Bundle-hash verification
// already ran at dispatch admission; this is a byte copy of verified state,
// group-shared under a lane credential exactly like prepareWorkTree.
func (s *Supervisor) materializeInputs(work, bundleDir string, manifest backend.DispatchManifest) error {
	fileMode := os.FileMode(0o600)
	if s.LaneCredential != nil {
		fileMode = 0o640
	}
	materialize := func(path string) error {
		body, err := os.ReadFile(filepath.Join(bundleDir, path))
		if err != nil {
			return err
		}
		target := filepath.Join(work, path)
		dir := filepath.Dir(target)
		if err := os.MkdirAll(dir, s.workTreeMode()); err != nil {
			return err
		}
		if s.LaneCredential != nil {
			if err := os.Chown(dir, -1, int(s.LaneCredential.GID)); err != nil {
				return err
			}
			if err := os.Chmod(dir, s.workTreeMode()|os.ModeSetgid); err != nil {
				return err
			}
		}
		if err := os.WriteFile(target, body, fileMode); err != nil {
			return err
		}
		if s.LaneCredential != nil {
			if err := os.Chown(target, -1, int(s.LaneCredential.GID)); err != nil {
				return err
			}
		}
		return nil
	}
	for _, entry := range manifest.Environment.MaterializedEntries(manifest.SchemaVersion) {
		if err := materialize(entry.Path); err != nil {
			return err
		}
	}
	for _, input := range manifest.Inputs {
		if err := materialize(input.Path); err != nil {
			return err
		}
	}
	return nil
}

// execute runs the runtime up to 1+InternalRetryMax times within the
// dispatch budget: expected-output validation and mechanical shape
// validation between attempts are the strategy-then-exit and output-shape
// countermeasures from RFC 0007's friction table, fenced inside the
// adapter. Budget expiry stops the loop and falls through to commit — the
// best-effort failed submission of D0013.C4b.
func (s *Supervisor) execute(manifest backend.DispatchManifest, bundleDir string, deadline time.Time, budget time.Duration) (runOutcome, error) {
	outcome := runOutcome{
		outputs: map[string][]byte{}, exhaust: map[string][]byte{},
	}
	corrective := ""
	attempts := 1 + s.Config.InternalRetryMax
	for attempt := 0; attempt < attempts; attempt++ {
		remaining := deadline.Sub(s.now())
		if remaining <= 0 {
			outcome.diagnostics = appendUnique(outcome.diagnostics, "runtime_crash")
			outcome.exhaust["budget"] = []byte(fmt.Sprintf(
				"dispatch budget %s exceeded after attempt %d; committing what stands", budget, attempt))
			outcome.exitReason = spoolclose.BudgetExpiry
			break
		}
		work := s.workDir(manifest.DispatchID)
		workAbs, err := filepath.Abs(work)
		if err != nil {
			return outcome, err
		}
		// Rendering precedes the pristine reset: a relaunch whose corrective
		// cannot be rendered (deterministic in-band refusals — the corrective
		// pushes framing past the argv bound after full spill, or carries a
		// NUL) must not discard the committable outcome of the launches that
		// actually happened. At attempt 0 nothing stands yet, so the render
		// error is the supervision's error; at any relaunch the refusal is
		// recorded (exhaust renderr-<n>, plus context_exhausted when the
		// transport bound is what refused) and the loop breaks to commit
		// what stands — the closure list keeps exactly the launches made.
		prompt, sourceMap, err := renderPrompt(manifest, bundleDir, workAbs, corrective, s.Config.PromptMode)
		if err != nil {
			if attempt == 0 {
				return outcome, err
			}
			outcome.exhaust[fmt.Sprintf("renderr-%d", attempt)] = []byte(err.Error())
			if errors.Is(err, errPromptOverArgBound) {
				outcome.diagnostics = appendUnique(outcome.diagnostics, "context_exhausted")
			}
			break
		}
		if attempt > 0 {
			// partials-collect-before-discard: attempt-1 (this same run's
			// just-concluded attempt) still stands on disk at this point —
			// collect it into exhaust before the pristine reset a few lines
			// below removes it for good. Evidence only: it lands in exhaust,
			// never outcome.outputs, so a collected partial can inform
			// diagnosis but can never fabricate a result that attempt did
			// not itself produce as a validated, collected output.
			collectPartialEvidence(outcome.exhaust, work, attempt-1)
		}
		// A submission describes one invocation. Once a new attempt launches,
		// outputs collected from its predecessor lose all force: the pristine
		// workspace below makes them unavailable to the runtime, so retaining
		// them here would fabricate a cross-attempt result no invocation made.
		outcome.outputs = make(map[string][]byte)
		// A2: pristine runtime tree per attempt.
		if err := os.RemoveAll(work); err != nil {
			return outcome, err
		}
		if err := s.prepareWorkTree(work); err != nil {
			return outcome, err
		}
		if err := s.materializeInputs(work, bundleDir, manifest); err != nil {
			return outcome, err
		}
		outcome.prompt = prompt
		outcome.relaunches = attempt

		// The invocation closure is pinned before the vendor launch
		// (D0007.C11): a relaunch retains the same semantic sources and
		// transport and additionally pins the exact prior-result-derived
		// corrective input, whose preimage goes to exhaust so admission can
		// verify it against the pinned corrective hash. Attempt 0 records
		// corrective input as absent — no prior result existed.
		closure := backend.AttemptClosure{
			Attempt:            attempt,
			RenderedPromptHash: PromptHash(prompt),
			Transport:          s.Config.PromptMode,
			SourceMap:          sourceMap,
		}
		if attempt > 0 {
			closure.CorrectiveHash = PromptHash(corrective)
			outcome.exhaust[fmt.Sprintf("corrective-%d", attempt)] = []byte(corrective)
		}
		closure.ClosureHash = AttemptClosureHash(manifest.DispatchID, closure)
		outcome.attempts = append(outcome.attempts, closure)

		outcome.launched = true
		transcript, runErr := s.invoke(prompt, work, remaining)
		outcome.exhaust[fmt.Sprintf("transcript-%d", attempt)] = transcript
		if runErr != nil {
			corrective = "The previous run crashed or timed out: " + runErr.Error()
			outcome.exhaust[fmt.Sprintf("runerr-%d", attempt)] = []byte(runErr.Error())
			outcome.diagnostics = appendUnique(outcome.diagnostics, "runtime_crash")
			// invoke clamps its wait to the remaining dispatch budget, so a
			// timed-out invocation and a budget-exhausted dispatch are
			// indistinguishable from runErr alone. Check the deadline here —
			// immediately after invoke returns, before continuing to a next
			// attempt or (on the final permitted attempt) falling out of the
			// loop entirely — so the last allowed invocation being clamped by
			// the remaining budget is classified budget_expiry rather than
			// misreported as relaunch_exhausted by the loop's bottom fallback.
			if !s.now().Before(deadline) {
				outcome.exhaust["budget"] = []byte(fmt.Sprintf(
					"dispatch budget %s exceeded after attempt %d; committing what stands", budget, attempt))
				outcome.exitReason = spoolclose.BudgetExpiry
				break
			}
			continue
		}
		if err := s.materializeStdoutOutput(manifest, work, transcript); err != nil {
			return outcome, err
		}

		missing, shapeErrors := s.collect(manifest, work, &outcome)
		if len(missing) == 0 && len(shapeErrors) == 0 {
			outcome.exitReason = spoolclose.RuntimeExit
			return outcome, nil
		}
		// The corrective describes THIS attempt's outcome only — rebuilt
		// from scratch, never concatenated onto a previous attempt's
		// corrective, which would carry stale failure text (a crash
		// sentence, say) into a prompt describing a run that did not crash.
		corrective = ""
		if len(missing) > 0 {
			outcome.diagnostics = appendUnique(outcome.diagnostics, "strategy_then_exit")
			corrective = "Your previous run exited without producing required outputs: " +
				strings.Join(missing, ", ") + ". Produce every required output file now."
		}
		if len(shapeErrors) > 0 {
			outcome.diagnostics = appendUnique(outcome.diagnostics, "output_shape_error")
			if corrective != "" {
				corrective += " "
			}
			corrective += "Output shape errors to repair: " + strings.Join(shapeErrors, "; ")
		}
	}
	// Reached by falling out of the loop after every attempt failed to
	// produce a shape-valid required output, or by the attempt>0
	// render-refusal break above (the relaunch loop giving up without a
	// further launch) — both are genuine relaunch exhaustion. Budget expiry
	// and success each already assigned their own exact reason before
	// reaching here, so this never overwrites a more specific verdict.
	if outcome.exitReason == "" {
		outcome.exitReason = spoolclose.RelaunchExhausted
	}
	return outcome, nil
}

// invoke runs one confined runtime invocation (D0013.C10): the whole tree
// lives in the supervisor's session and process group and dies with it.
// The invocation limit, clamped to the remaining budget, kills the confined
// tree on expiry and feeds the loop as a runtime_crash diagnostic.
func (s *Supervisor) invoke(prompt, work string, remaining time.Duration) ([]byte, error) {
	limit := s.invocationLimit()
	if remaining < limit {
		limit = remaining
	}
	argv := append([]string{}, s.Config.Command...)
	var stdin io.Reader
	if s.Config.PromptMode == "stdin" {
		stdin = strings.NewReader(prompt)
	} else {
		argv = append(argv, prompt)
	}
	var out bytes.Buffer
	proc, err := supervise.StartConfined(supervise.Spec{
		Argv: argv, Dir: work, Stdin: stdin, Stdout: &out, Stderr: &out,
		Grace: s.Config.AbortGrace, LaneCredential: s.LaneCredential,
	})
	if err != nil {
		return out.Bytes(), err
	}
	done := make(chan error, 1)
	go func() { done <- proc.Wait() }()
	select {
	case err := <-done:
		_ = proc.Cleanup()
		return out.Bytes(), err
	case <-time.After(limit):
		_ = proc.Kill()
		<-done
		_ = proc.Cleanup()
		return out.Bytes(), errors.New("wall-clock limit exceeded")
	}
}

// materializeStdoutOutput is an opt-in bridge for one-shot CLI surfaces
// that can only return a completion on stdout. The artifact contract stays
// the file seam: the supervisor writes the transcript into the single
// required output before the ordinary collector validates its shape.
func (s *Supervisor) materializeStdoutOutput(manifest backend.DispatchManifest, work string, transcript []byte) error {
	if s.Config.StdoutOutput == "" {
		return nil
	}
	if s.Config.StdoutOutput != "single-required-output" {
		return fmt.Errorf("llm: unsupported stdout_output mode %q", s.Config.StdoutOutput)
	}
	var required []backend.ExpectedOut
	for _, expected := range manifest.Expected {
		if expected.Required {
			required = append(required, expected)
		}
	}
	if len(required) != 1 {
		return fmt.Errorf("llm: stdout_output=single-required-output needs exactly one required output, got %d", len(required))
	}
	expected := required[0]
	target := filepath.Join(work, "outputs", expected.OutputID)
	if _, err := os.Stat(target); err == nil {
		return nil
	} else if !errors.Is(err, os.ErrNotExist) {
		return err
	}
	body := stdoutBodyForKind(expected.Kind, transcript)
	if len(bytes.TrimSpace(body)) == 0 {
		return nil
	}
	if body[len(body)-1] != '\n' {
		body = append(body, '\n')
	}
	return os.WriteFile(target, body, 0o600)
}

func stdoutBodyForKind(kind string, transcript []byte) []byte {
	trimmed := bytes.TrimSpace(transcript)
	if kind == "review-ledger" || strings.HasSuffix(kind, "-report") || looksJSON(trimmed) {
		if jsonBody, ok := extractJSONBody(trimmed); ok {
			return jsonBody
		}
	}
	return trimmed
}

func extractJSONBody(body []byte) ([]byte, bool) {
	for _, fenced := range fencedCodeBlocks(body) {
		trimmed := bytes.TrimSpace(fenced)
		if json.Valid(trimmed) {
			return trimmed, true
		}
	}
	for start, b := range body {
		if b != '{' && b != '[' {
			continue
		}
		reader := bytes.NewReader(body[start:])
		decoder := json.NewDecoder(reader)
		var probe any
		if err := decoder.Decode(&probe); err == nil {
			return bytes.TrimSpace(body[start : start+int(decoder.InputOffset())]), true
		}
	}
	return nil, false
}

func fencedCodeBlocks(body []byte) [][]byte {
	var blocks [][]byte
	rest := body
	for {
		start := bytes.Index(rest, []byte("```"))
		if start < 0 {
			return blocks
		}
		afterFence := rest[start+3:]
		if newline := bytes.IndexByte(afterFence, '\n'); newline >= 0 {
			afterFence = afterFence[newline+1:]
		}
		end := bytes.Index(afterFence, []byte("```"))
		if end < 0 {
			return blocks
		}
		blocks = append(blocks, afterFence[:end])
		rest = afterFence[end+3:]
	}
}

// collect validates expected outputs mechanically: presence, then the cheap
// shape predicates (markdown element anchors; JSON parses). Full W1
// validation is admission's job — this is the adapter's repair loop input.
func (s *Supervisor) collect(manifest backend.DispatchManifest, work string, outcome *runOutcome) ([]string, []string) {
	var missing, shapeErrors []string
	for _, expected := range manifest.Expected {
		path := filepath.Join(work, "outputs", expected.OutputID)
		body, err := os.ReadFile(path)
		if err != nil {
			if expected.Required {
				missing = append(missing, "outputs/"+expected.OutputID)
			}
			continue
		}
		if len(bytes.TrimSpace(body)) == 0 {
			shapeErrors = append(shapeErrors, "outputs/"+expected.OutputID+" is empty")
			continue
		}
		switch {
		case expected.Kind == "review-ledger":
			var ledger struct {
				Verdict string `json:"verdict"`
			}
			if json.Unmarshal(body, &ledger) != nil || !gate.ReviewVerdictValid(ledger.Verdict) {
				shapeErrors = append(shapeErrors, "outputs/"+expected.OutputID+` must be JSON with verdict accept, accept_with_findings, needs_revision, or reject`)
				continue
			}
		case strings.HasSuffix(expected.Kind, "-report") || looksJSON(body):
			var probe any
			if json.Unmarshal(body, &probe) != nil && looksJSON(body) {
				shapeErrors = append(shapeErrors, "outputs/"+expected.OutputID+" is not valid JSON")
				continue
			}
		case !bytes.Contains(body, []byte("{#el:")):
			shapeErrors = append(shapeErrors, "outputs/"+expected.OutputID+" carries no {#el:...} element anchors on its headings")
			continue
		}
		outcome.outputs[expected.OutputID] = body
	}
	return missing, shapeErrors
}

func looksJSON(body []byte) bool {
	trimmed := bytes.TrimSpace(body)
	return len(trimmed) > 0 && (trimmed[0] == '{' || trimmed[0] == '[')
}

// commit assembles and renames the submission — the sole commit point (A4).
func (s *Supervisor) commit(manifest backend.DispatchManifest, outcome runOutcome, started, ended time.Time) (string, error) {
	target := s.Spool.SubmissionDir(manifest.DispatchID)
	nonce := sessionNonce(s.Config.BackendID, manifest.DispatchID)
	incoming := s.Spool.IncomingDir(nonce)
	if err := os.RemoveAll(incoming); err != nil {
		return "", err
	}
	if err := os.MkdirAll(incoming, 0o700); err != nil {
		return "", err
	}

	status := "complete"
	var entries []backend.SubmissionOutput
	present := 0
	for _, expected := range manifest.Expected {
		body, ok := outcome.outputs[expected.OutputID]
		if !ok {
			if expected.Required {
				status = "partial"
			}
			entries = append(entries, backend.SubmissionOutput{
				OutputID: expected.OutputID, Kind: expected.Kind, Identity: expected.Identity,
				Placement: expected.Placement, Status: "missing", MissingReason: "not produced",
				DerivedFrom: append([]string{}, expected.DerivedFromOutputs...),
			})
			continue
		}
		relPath := filepath.Join("outputs", expected.OutputID, "body")
		full := filepath.Join(incoming, relPath)
		if err := os.MkdirAll(filepath.Dir(full), 0o700); err != nil {
			return "", err
		}
		if err := writeFileDurable(full, body); err != nil {
			return "", err
		}
		sum := sha256.Sum256(body)
		entries = append(entries, backend.SubmissionOutput{
			OutputID: expected.OutputID, Kind: expected.Kind, Identity: expected.Identity,
			Placement: expected.Placement, ContentHash: hex.EncodeToString(sum[:]),
			Path: relPath, Status: "present", DerivedFrom: append([]string{}, expected.DerivedFromOutputs...),
		})
		present++
	}
	if present == 0 && len(entries) > 0 {
		status = "failed"
	}

	// Exhaust: transcripts are bulky non-artifact lane output, content-
	// addressed and referenced, never artifacts (RFC 0007).
	var exhaust []backend.BundleFile
	for _, label := range sortedLabels(outcome.exhaust) {
		body := outcome.exhaust[label]
		relPath := filepath.Join("exhaust", label)
		full := filepath.Join(incoming, relPath)
		if err := os.MkdirAll(filepath.Dir(full), 0o700); err != nil {
			return "", err
		}
		if err := writeFileDurable(full, body); err != nil {
			return "", err
		}
		sum := sha256.Sum256(body)
		exhaust = append(exhaust, backend.BundleFile{
			Label: label, Kind: "runtime_diagnostic", ContentHash: hex.EncodeToString(sum[:]), Path: relPath,
		})
	}
	if exhaust == nil {
		exhaust = []backend.BundleFile{}
	}

	diagnostics := outcome.diagnostics
	if diagnostics == nil {
		diagnostics = []string{}
	}
	reads := manifest.Environment.ReadSet(manifest.SchemaVersion)
	if reads == nil {
		reads = []string{}
	}

	submission := backend.SubmissionManifest{
		SchemaVersion:    manifest.SchemaVersion,
		DispatchID:       manifest.DispatchID,
		RunRef:           manifest.Run.RunRef,
		RunManifestHash:  manifest.Run.RunManifestHash,
		LaneID:           manifest.Lane.LaneID,
		Attempt:          manifest.Lane.Attempt,
		Status:           status,
		Outputs:          entries,
		Evidence:         []backend.BundleFile{},
		Exhaust:          exhaust,
		SynthesizedFrom:  []backend.SynthesisPin{},
		EnvironmentReads: reads,
		Attribution: backend.Attribution{
			BackendID:        s.Config.BackendID,
			DeclarationHash:  manifest.Lane.DeclarationHash,
			AliasingClass:    s.Config.AliasingClass,
			AgentRuntimeID:   s.Config.RuntimeID,
			AgentRuntimeVer:  s.Config.runtimeVersion(),
			LaneRole:         manifest.Lane.Role,
			SessionNonce:     nonce,
			RenderedPrompt:   PromptHash(outcome.prompt),
			InternalRelaunch: outcome.relaunches,
			Attempts:         outcome.attempts,
			StartedAt:        started.UTC().Format(time.RFC3339),
			EndedAt:          ended.UTC().Format(time.RFC3339),
		},
		Diagnostics: backend.Diagnostics{
			Classes:           diagnostics,
			Assumptions:       []string{},
			CapturedQuestions: []string{},
		},
	}
	sealed, err := submission.SealedWith(s.SealKey)
	if err != nil {
		return "", err
	}
	if err := backend.WriteManifest(filepath.Join(incoming, "manifest.json"), sealed); err != nil {
		return "", err
	}
	if err := os.Rename(incoming, target); err != nil {
		if errors.Is(err, os.ErrExist) || errors.Is(err, syscall.ENOTEMPTY) {
			_ = os.RemoveAll(incoming)
			return target, nil
		}
		return "", err
	}
	return target, nil
}

func (s *Supervisor) now() time.Time {
	if s.Now != nil {
		return s.Now()
	}
	return time.Now()
}

// sessionNonce is fresh per dispatch (A3) and stable across replays; the
// backend id salts it so two backends never share a nonce.
func sessionNonce(backendID, dispatchID string) string {
	canonical, err := scf.Marshal([]any{"session_nonce", backendID, dispatchID})
	if err != nil {
		return "nonce-" + dispatchID
	}
	sum := sha256.Sum256(canonical)
	return hex.EncodeToString(sum[:])[:32]
}

func writeFileDurable(path string, body []byte) error {
	file, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o600)
	if err != nil {
		return err
	}
	defer file.Close()
	if _, err := file.Write(body); err != nil {
		return err
	}
	return file.Sync()
}

// collectPartialEvidence archives a just-concluded attempt's on-disk output
// tree into exhaust (partials-collect-before-discard,
// stalls-need-no-judgment@3): same-attempt on-disk evidence collected before
// the pristine per-attempt reset destroys it, labeled with the exact attempt
// it came from so it is never conflated with any other attempt's evidence
// and never promoted into a submission result no invocation actually made.
// Best-effort — an unreadable or absent outputs directory leaves nothing to
// collect.
func collectPartialEvidence(exhaust map[string][]byte, work string, attempt int) {
	outputsDir := filepath.Join(work, "outputs")
	_ = filepath.WalkDir(outputsDir, func(path string, entry os.DirEntry, err error) error {
		if err != nil || entry.IsDir() {
			return nil
		}
		body, readErr := os.ReadFile(path)
		if readErr != nil {
			return nil
		}
		rel, relErr := filepath.Rel(outputsDir, path)
		if relErr != nil {
			rel = entry.Name()
		}
		exhaust[fmt.Sprintf("partial-%d-%s", attempt, filepath.ToSlash(rel))] = body
		return nil
	})
}

func appendUnique(list []string, value string) []string {
	for _, existing := range list {
		if existing == value {
			return list
		}
	}
	return append(list, value)
}

func sortedLabels(m map[string][]byte) []string {
	labels := make([]string, 0, len(m))
	for label := range m {
		labels = append(labels, label)
	}
	sort.Strings(labels)
	return labels
}

