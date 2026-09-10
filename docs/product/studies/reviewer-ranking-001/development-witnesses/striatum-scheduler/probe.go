// This witness calls original production packages without importing their tests.
package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"os"
	"time"

	"github.com/halbritt/striatum-next/internal/backend"
	"github.com/halbritt/striatum-next/internal/records"
	"github.com/halbritt/striatum-next/internal/runtimeclock"
	"github.com/halbritt/striatum-next/internal/scheduler"
)

func hash(text string) string {
	sum := sha256.Sum256([]byte(text))
	return hex.EncodeToString(sum[:])
}

func message(err error) string {
	if err == nil {
		return ""
	}
	return err.Error()
}

func declaration(id string, rank int, supervised bool) scheduler.Declaration {
	d := scheduler.Declaration{BackendID: id, DeclarationHash: hash(id), SupportedPasses: []string{"build"},
		AliasingClass: id, Rank: rank, MaxLanes: 2, Supervised: supervised}
	if supervised {
		d.InvocationLimitSeconds, d.DispatchBudgetSeconds, d.InternalRetryMax = 1800, 3600, 1
	}
	return d
}

func observation(id string, ref uint64, at time.Time) scheduler.RecognizedExhaustionObservation {
	return scheduler.RecognizedExhaustionObservation{
		RecordRef: ref, RecordHash: hash(id + "-observation"), BackendID: id, PassID: "build",
		SourceRunRef: 10, DispatchID: "dispatch-10", SignatureID: "monthly-spend-limit",
		Classifier: scheduler.CapacityObservationClassifierPin{PolicyID: "exhaustion_behavior", PolicyVersion: 1, ContentHash: hash("classifier")},
		ObservedAt: at.Format(time.RFC3339Nano), TTLSeconds: 7200,
		ExpiresAt: at.Add(2 * time.Hour).Format(time.RFC3339Nano),
	}
}

func fixture(condition string) scheduler.SchedulerEvaluationInput {
	now := time.Date(2026, 8, 21, 12, 0, 0, 0, time.UTC)
	input := scheduler.SchedulerEvaluationInput{
		ReadySet: []scheduler.ReadyRun{{RunRef: 100, PassID: "build", RunManifestHash: hash("manifest"),
			LaneID: "lane-1", Attempt: 1, DispatchVersion: 2,
			ClockContractID: backend.ExecutionBoundsContractID, ClockContractVersion: backend.ExecutionBoundsContractVersion,
			DriverPolicyID: "driver", DriverPolicyVersion: 10, DriverPolicyHash: hash("driver-policy"),
			DeadlineClass: "batch", DriverHorizonSeconds: 3960, TerminalCommitMarginSeconds: 120}},
		Declarations: []scheduler.Declaration{declaration("local", 0, false), declaration("remote", 1, true)},
		Snapshot:     scheduler.Snapshot{Digest: hash("capacity-snapshot")}, InFlight: map[string]int{},
		Policy:   scheduler.SchedulerPolicyPin{Version: 1, BodyHash: hash("placement-policy")},
		Aliasing: scheduler.SchedulerAliasingInput{RegistryHash: hash("aliasing")}, AsOf: now,
		HostClock:   &runtimeclock.Sample{Scheme: runtimeclock.Scheme, BootID: "witness-boot", MonotonicNS: "1000000000"},
		NextHorizon: now.Add(30 * time.Minute).Format(time.RFC3339Nano), Implementation: scheduler.ImplementationPin(),
	}
	active := observation("remote", 50, now.Add(-time.Hour))
	switch condition {
	case "ordinary-local":
	case "local-unrelated-active":
		input.CapacityObservations = []scheduler.RecognizedExhaustionObservation{active}
	case "exhausted-fallback-local":
		input.ReadySet[0].BackendPreference = []string{"remote", "local"}
		input.CapacityObservations = []scheduler.RecognizedExhaustionObservation{active}
	case "supervised-failover", "all-supervised-exhausted":
		input.Declarations = []scheduler.Declaration{declaration("remote", 0, true), declaration("survivor", 1, true)}
		input.CapacityObservations = []scheduler.RecognizedExhaustionObservation{active}
		if condition == "all-supervised-exhausted" {
			input.CapacityObservations = append(input.CapacityObservations, observation("survivor", 51, now.Add(-time.Hour)))
		}
	case "expired-observation":
		input.CapacityObservations = []scheduler.RecognizedExhaustionObservation{observation("remote", 50, now.Add(-3*time.Hour))}
	case "malformed-observation":
		active.TTLSeconds = 0
		input.CapacityObservations = []scheduler.RecognizedExhaustionObservation{active}
	default:
		panic("unknown frozen condition")
	}
	return input
}

func recordCheck(version uint16, payload map[string]any, at time.Time) map[string]any {
	r := records.Record{LedgerFormat: records.LedgerFormat, GraphID: "caplab-private-witness", Seq: 101,
		Type: "scheduling_decision", SchemaVersion: version, WrittenAt: at,
		Actor: records.Actor{Component: "driver", Instance: "caplab-witness"}, Causes: []uint64{100},
		PrevRecordHash: hash("prior-record"), Payload: payload}
	canonical, err := r.CanonicalBytes()
	result := map[string]any{"encode_error": message(err), "decode_error": "", "canonical_sha256": ""}
	if err == nil {
		result["canonical_sha256"] = hash(string(canonical))
		decoded, decodeErr := records.DecodeCanonical(canonical)
		result["decode_error"] = message(decodeErr)
		result["decoded_schema_version"] = decoded.SchemaVersion
	}
	return result
}

func selected(e scheduler.SchedulerEvaluation) []string {
	ids := []string{}
	for _, binding := range e.Bindings {
		ids = append(ids, binding.BackendID)
	}
	return ids
}

func main() {
	conditions := []string{"ordinary-local", "local-unrelated-active", "exhausted-fallback-local", "supervised-failover",
		"all-supervised-exhausted", "expired-observation", "malformed-observation"}
	results := []map[string]any{}
	for _, condition := range conditions {
		input := fixture(condition)
		stamp := scheduler.DecisionSchemaVersion(input)
		evaluation, err := scheduler.Evaluate(input)
		row := map[string]any{"condition": condition, "input": input, "stamp": stamp, "evaluation_error": message(err)}
		if err == nil {
			payload := evaluation.SchedulingDecisionPayload()
			row["evaluation_version"], row["evaluation_id"] = evaluation.SchemaVersion, evaluation.EvaluationID
			row["selected"], row["refusals"], row["deferrals"] = selected(evaluation), evaluation.Refusals, evaluation.Deferrals
			row["payload"] = payload
			row["stamped_record"] = recordCheck(stamp, payload, input.AsOf)
			row["evaluation_record"] = recordCheck(evaluation.SchemaVersion, payload, input.AsOf)
			// This intervention tests the consequence of a missing observation.
			// It is not a general decoder or a complete record-to-input replay.
			without := input
			without.CapacityObservations = nil
			counterfactual, counterErr := scheduler.Evaluate(without)
			row["without_observations"] = map[string]any{"error": message(counterErr), "selected": selected(counterfactual),
				"evaluation_version": counterfactual.SchemaVersion}
		}
		results = append(results, row)
	}
	if err := json.NewEncoder(os.Stdout).Encode(map[string]any{"schema": "caplab.scheduler-witness-output/v1", "observations": results}); err != nil {
		panic(err)
	}
}
