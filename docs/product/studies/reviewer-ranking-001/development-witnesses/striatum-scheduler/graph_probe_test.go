// Added virtually through go -overlay; no original source or test is replaced.
package driver

import (
	"encoding/json"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/halbritt/striatum-next/internal/scheduler"
	"github.com/halbritt/striatum-next/internal/store"
)

func caplabCopyTree(source, destination string) error {
	return filepath.WalkDir(source, func(path string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		relative, err := filepath.Rel(source, path)
		if err != nil {
			return err
		}
		target := filepath.Join(destination, relative)
		if entry.IsDir() {
			return os.MkdirAll(target, 0700)
		}
		if !entry.Type().IsRegular() {
			return fmt.Errorf("unexpected graph file type: %s", relative)
		}
		body, err := os.ReadFile(path)
		if err != nil {
			return err
		}
		return os.WriteFile(target, body, 0600)
	})
}

func caplabError(err error) string {
	if err == nil {
		return ""
	}
	return err.Error()
}

func caplabDeclaration(id string, rank int, supervised bool) []byte {
	body := fmt.Sprintf(`schema_version: 1
id: %s
status: accepted
agent_runtimes:
  - id: fixture-runtime
    version_discovery: probe
aliasing:
  aliasing_class: fixture
capabilities:
  supported_pass_types: [intent-capture]
  forbidden_pass_types: []
constraints:
  internal_retry: { max: 1 }
provenance_fields:
  required: [agent_runtime_id, agent_runtime_version, session_nonce]
scheduler_hints: [rank=%d]
`, id, rank)
	if supervised {
		body += "adapter:\n  command: [fixture-runtime]\n  invocation_limit_s: 1800\n  dispatch_budget_s: 3600\n"
	}
	return []byte(body)
}

func TestCAPLABGraphWitness(t *testing.T) {
	capture := os.Getenv("CAPLAB_GRAPH_CAPTURE")
	if capture == "" {
		t.Fatal("private capture directory required")
	}
	for _, condition := range []string{"ordinary", "local-fallback", "supervised-fallback", "unrecognized-terminal", "expired-observation"} {
		t.Run(condition, func(t *testing.T) {
			destination := filepath.Join(capture, condition)
			if err := os.Mkdir(destination, 0700); err != nil {
				t.Fatal(err)
			}
			result := map[string]any{"schema": "caplab.scheduler-graph-output/v1", "condition": condition, "phase": "fixture-setup"}
			var fixture *runOpenFixture
			defer func() {
				if fixture != nil {
					result["adapter_dispatches"] = len(fixture.adapter.dispatched)
					all, err := fixture.graph.Records()
					result["final_records_error"], result["records"] = caplabError(err), all
					result["original_data_root"], result["original_repo_root"] = fixture.graph.DataRoot, fixture.graph.RepoRoot
					for name, source := range map[string]string{"data": fixture.graph.DataRoot, "repo": fixture.graph.RepoRoot} {
						if err := caplabCopyTree(source, filepath.Join(destination, name)); err != nil {
							result["capture_error"] = err.Error()
							t.Error(err)
						}
					}
				}
				body, err := json.MarshalIndent(result, "", "  ")
				if err == nil {
					err = os.WriteFile(filepath.Join(destination, "result.json"), append(body, '\n'), 0600)
				}
				if err != nil {
					t.Error(err)
				}
			}()
			fixture = newRunOpenFixture(t)
			setRecognizedExhaustionPolicy(t, fixture)
			fixture.session.Backends = []scheduler.Declaration{
				putRecoveryBackendDeclaration(t, fixture.graph, caplabDeclaration("capture", 0, true)),
				putRecoveryBackendDeclaration(t, fixture.graph, caplabDeclaration("fallback", 1, condition == "supervised-fallback")),
			}
			result["phase"] = "source-observation-setup"
			if condition != "ordinary" {
				first := openAndBindExhaustionGuardRun(t, fixture, "capture")
				terminal := "Request refused: You've hit your monthly spend limit"
				if condition == "unrecognized-terminal" {
					terminal = "Rate limit exceeded; retry in 30 seconds"
				}
				stageRecognizedExhaustionSubmission(t, fixture, first, terminal)
				_, err := fixture.session.drain(&Report{})
				result["source_drain_error"] = caplabError(err)
				if err != nil {
					t.Fatal(err)
				}
				if condition == "expired-observation" {
					fixture.session.Now = func() time.Time { return fixture.now().Add(6 * time.Hour) }
				}
			}
			run := openExhaustionGuardRun(t, fixture)
			asOf := fixture.session.Now().UTC()
			state := fixture.state(t)
			input, err := fixture.session.schedulerInputForOpenedRun(state, run, asOf)
			if err != nil {
				t.Fatal(err)
			}
			result["input"], result["run_ref"], result["as_of"] = input, run.Seq, asOf
			result["folded_capacity_observations"] = state.CapacityObservations
			result["records_before"] = len(fixture.records(t))
			result["phase"] = "decision"
			decision, created, err := fixture.session.ensureSchedulingDecisionAt(run.Seq, asOf)
			result["decision_error"], result["decision_created"] = caplabError(err), created
			if err != nil {
				result["phase"] = "decision-refused"
				return
			}
			result["decision"] = decision
			selected, outcome, err := decisionBindingPreimage(decision)
			result["binding_preimage_error"], result["outcome"], result["selected"] = caplabError(err), outcome, selected
			if err != nil || outcome != "binding" {
				result["phase"] = "binding-preimage-refused"
				return
			}
			bound, err := fixture.session.ensureLaneBinding(run.Seq, decision, selected)
			result["binding_error"], result["binding_created"] = caplabError(err), bound
			if err != nil {
				result["phase"] = "binding-refused"
				return
			}
			result["phase"] = "reopen"
			graph, _, err := store.OpenGraph(store.OpenOptions{DataHome: filepath.Dir(fixture.graph.DataRoot), RepoRoot: fixture.graph.RepoRoot})
			result["reopen_error"] = caplabError(err)
			if err != nil {
				return
			}
			prior := fixture.session
			fixture.graph = graph
			fixture.session = &Session{Graph: graph, Spool: prior.Spool, Catalog: prior.Catalog, Policy: prior.Policy, Now: prior.Now,
				Instance: prior.Instance, Kinds: prior.Kinds, RuntimeClock: prior.RuntimeClock, Environment: prior.Environment,
				SchedulerPolicy: prior.SchedulerPolicy, SchedulerAliasing: prior.SchedulerAliasing,
				Backends: prior.Backends, Adapters: prior.Adapters}
			reopened := fixture.state(t)
			result["reopened_run"] = reopened.Runs[run.Seq]
			result["reopened_decisions"] = reopened.SchedulingDecisions[run.Seq]
			beforeRepeat := len(fixture.records(t))
			repeated, madeDecision, repeatErr := fixture.session.ensureSchedulingDecisionAt(run.Seq, asOf)
			result["repeat_decision_error"], result["repeat_decision_created"] = caplabError(repeatErr), madeDecision
			if repeatErr == nil {
				madeBinding, bindErr := fixture.session.ensureLaneBinding(run.Seq, repeated, selected)
				result["repeat_binding_error"], result["repeat_binding_created"] = caplabError(bindErr), madeBinding
			}
			result["repeat_added_records"] = len(fixture.records(t)) - beforeRepeat
			without := input
			without.CapacityObservations = nil
			sample, sampleErr := fixture.session.sampleRuntimeClock()
			result["counterfactual_clock_error"] = caplabError(sampleErr)
			if sampleErr == nil {
				without.HostClock = &sample
				counterfactual, counterErr := scheduler.Evaluate(without)
				result["counterfactual_error"], result["counterfactual_bindings"] = caplabError(counterErr), counterfactual.Bindings
			}
			result["phase"] = "completed"
		})
	}
}
