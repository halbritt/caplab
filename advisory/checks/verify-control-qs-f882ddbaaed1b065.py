"""Deterministic re-runnable check for dispatch b9919beb2088c641... (substrate
qs-f882ddbaaed1b065, pass backend-role-qualified).

Four allegations (codex-sol-high):
  A1 packet.packet_id is empty                     -> fact checked, verdict-neutral
     (whether empty is "malformed" depends on the change-set schema, not in set)
  A2 docs say Bind serialises the ledger to an audit log / replay is exact;
     Bind only returns an in-memory ledger, ledger lacks backend facts
  A3 CapacitySnapshot.Fresh returns true for future-dated snapshots when
     ttl <= 0, contrary to "never fresh"
  A4 policy-pins.md says zero-sample data disqualifies; reliabilityCheck admits
     zero samples when min_reliability == 0 and the window check passes

A3/A4 are additionally confirmed by compiling and running the delivered Go
package when a `go` toolchain is on PATH (falls back to textual checks only).

Exit 0 = control is DEFECTIVE; exit 1 = SOUND.
"""
import json, os, re, shutil, subprocess, sys, tempfile
exchange = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
DISPATCH = "b9919beb2088c641"
full = [x for x in os.listdir(os.path.join(exchange, "dispatch"))
        if x.startswith(DISPATCH)][0]
bundle = os.path.join(exchange, "dispatch", full)
man = json.load(open(os.path.join(bundle, "manifest.json")))
body = json.loads(open(os.path.join(bundle, man["inputs"][0]["path"]),
                       errors="replace").read())
files = body["files"]
results = {}

# A1: packet identity (fact only; not used in the verdict).
results["a1_packet_id_empty"] = body.get("packet", {}).get("packet_id") == ""
results["a1_change_set_contains_packet_schema"] = any(
    "packet_id" in c for n, c in files.items() if n.endswith(".schema.json"))

# A2: doc claim vs. Bind implementation.
doc = files["docs/backend-role-qualification.md"]
bind = files["internal/driver/bind.go"]
trace = files["internal/scheduler/trace.go"]
results["a2_doc_claims_bind_serialises_for_audit_log"] = bool(re.search(
    r"`Bind` collects the traces.{0,400}?serialises the\s+ledger for the audit log",
    doc, re.S))
results["a2_doc_claims_exact_replay_from_ledger_and_pin"] = (
    "replayed exactly from\nits ledger and the pinned policy" in doc
    or "replayed exactly from its ledger and the pinned policy"
    in " ".join(doc.split()))
results["a2_bind_calls_marshal_or_writes"] = bool(re.search(
    r"Marshal|json\.|os\.|io\.|Write|log\.|audit", bind.replace(
        "// and records a full qualification ledger for audit.", "").replace(
        "so the caller can audit or escalate", "")))
results["a2_marshal_called_anywhere_in_set"] = any(
    re.search(r"\.Marshal\(", c) for n, c in files.items()
    if n.endswith(".go"))
m = re.search(r"type QualificationLedger struct \{(.*?)\n\}", trace, re.S)
ledger_fields = re.findall(r"^\s*(\w+)\s", m.group(1), re.M)
results["a2_ledger_fields"] = ledger_fields
results["a2_ledger_carries_backend_facts"] = any(
    f in ledger_fields for f in ("Backends", "Pool", "Incumbents", "Kinship",
                                 "Candidates"))
a2 = (results["a2_doc_claims_bind_serialises_for_audit_log"]
      and not results["a2_bind_calls_marshal_or_writes"]
      and not results["a2_marshal_called_anywhere_in_set"])

# A3: Fresh contract vs. code (textual).
roles = files["internal/scheduler/roles.go"]
fresh = re.search(r"(// Fresh reports.*?)\nfunc \(s CapacitySnapshot\) Fresh"
                  r"\(now time\.Time, ttl time\.Duration\) bool \{(.*?)\n\}",
                  roles, re.S)
results["a3_contract_says_future_never_fresh"] = (
    "A snapshot dated in the\n// future (negative age) is never fresh."
    in fresh.group(1))
results["a3_contract_also_says_nonpositive_ttl_disables"] = (
    "non-positive ttl disables the freshness requirement" in fresh.group(1))
fbody = fresh.group(2)
results["a3_ttl_guard_returns_true_before_age_check"] = (
    fbody.find("if ttl <= 0 {\n\t\treturn true") != -1
    and fbody.find("if ttl <= 0") < fbody.find("age :="))
a3_text = (results["a3_contract_says_future_never_fresh"]
           and results["a3_ttl_guard_returns_true_before_age_check"])

# A4: fail-closed doc vs. reliabilityCheck (textual).
pins = files["docs/policy-pins.md"]
cap = files["internal/scheduler/capacity.go"]
results["a4_doc_says_zero_sample_disqualifies"] = bool(re.search(
    r"Every predicate is designed to fail closed: missing, stale, or\s+"
    r"zero-sample data\s+disqualifies rather than admits", pins))
results["a4_doc_admits_only_positive_floor_excludes"] = (
    "any positive floor also excludes" in " ".join(pins.split()))
rc = re.search(r"func reliabilityCheck\(.*?\n\}", cap, re.S).group(0)
results["a4_reliability_check_has_no_sample_count_guard"] = not re.search(
    r"Samples\(\)\s*(==|<=|<)\s*0|Samples\(\)\s*==\s*0", rc)
results["a4_reliability_fails_only_on_strict_less_than_floor"] = (
    "rate < pin.MinReliability" in rc)
results["a4_success_rate_zero_samples_is_zero"] = bool(re.search(
    r"if n == 0 \{\n\t\treturn 0", roles))
a4_text = (results["a4_doc_says_zero_sample_disqualifies"]
           and results["a4_reliability_check_has_no_sample_count_guard"]
           and results["a4_reliability_fails_only_on_strict_less_than_floor"]
           and results["a4_success_rate_zero_samples_is_zero"])

# Behavioural confirmation of A3/A4 by running the delivered package.
GO_PROBE = '''package scheduler

import (
	"testing"
	"time"
)

func TestProbeFreshFutureTTLZero(t *testing.T) {
	now := time.Date(2026, 7, 9, 12, 0, 0, 0, time.UTC)
	s := CapacitySnapshot{ObservedAt: now.Add(time.Hour)} // future-dated
	if s.Fresh(now, time.Minute) {
		t.Fatalf("PROBE_A3_POSITIVE_TTL_FUTURE_FRESH")
	}
	if s.Fresh(now, 0) {
		t.Fatalf("PROBE_A3_FUTURE_DATED_IS_FRESH_WHEN_TTL_ZERO")
	}
}

func TestProbeZeroSamplesAdmitted(t *testing.T) {
	now := time.Date(2026, 7, 9, 12, 0, 0, 0, time.UTC)
	m := ReliabilityMetrics{} // zero samples
	r := reliabilityCheck(m, PolicyPin{MinReliability: 0, ReliabilityWindow: 0}, now)
	if r.Passed {
		t.Fatalf("PROBE_A4_ZERO_SAMPLES_PASS_WITH_ZERO_FLOOR")
	}
}
'''
go = shutil.which("go") or os.path.expanduser("~/.local/bin/go")
results["go_probe_ran"] = False
if os.path.exists(go):
    tmp = tempfile.mkdtemp(prefix="verify-f882-", dir=os.environ.get(
        "CAPLAB_SCRATCH") or None)
    try:
        for n, c in files.items():
            if n.startswith("internal/scheduler/") and n.endswith(".go") \
                    and not n.endswith("_test.go"):
                p = os.path.join(tmp, n)
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "w").write(c)
        open(os.path.join(tmp, "go.mod"), "w").write(
            "module striatum-next\n\ngo 1.23\n")
        open(os.path.join(tmp, "internal/scheduler/probe_test.go"),
             "w").write(GO_PROBE)
        env = dict(os.environ, GOFLAGS="-mod=mod", GOTOOLCHAIN="local",
                   GOCACHE=os.path.join(tmp, "gocache"),
                   GOPATH=os.path.join(tmp, "gopath"))
        out = subprocess.run([go, "test", "./internal/scheduler/", "-run",
                              "TestProbe", "-count=1"], cwd=tmp, env=env,
                             capture_output=True, text=True, timeout=300)
        results["go_probe_ran"] = "ok" in out.stdout or "FAIL" in out.stdout
        results["go_probe_output"] = (out.stdout + out.stderr).strip()[-1500:]
        results["a3_go_confirms_future_fresh_when_ttl_zero"] = (
            "PROBE_A3_FUTURE_DATED_IS_FRESH_WHEN_TTL_ZERO" in out.stdout)
        results["a4_go_confirms_zero_samples_pass"] = (
            "PROBE_A4_ZERO_SAMPLES_PASS_WITH_ZERO_FLOOR" in out.stdout)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

a3 = a3_text and (not results["go_probe_ran"]
                  or results["a3_go_confirms_future_fresh_when_ttl_zero"])
a4 = a4_text and (not results["go_probe_ran"]
                  or results["a4_go_confirms_zero_samples_pass"])
results["a2_substantiated"] = a2
results["a3_substantiated"] = a3
results["a4_substantiated"] = a4
defective = a2 or a3 or a4
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND")
sys.exit(0 if defective else 1)
