"""Deterministic re-runnable check for dispatch 1ff35885... (control
qs-d79e9a1668416a7d, packet fnnj-003-verification-base-discovery).

Allegation (codex-sol-high): the delivery only computes a SignalDemandPlan and
never integrates it into a verification-signal demand site or enforces
DemandSignal, so the doc claims "never spends signal attempts on an unresolvable
base" and "discovers freshness conditions at verification demand sites" are
overclaims.

What is mechanically checkable INSIDE the change set:
  (a) the two claim sentences are present in base.go;
  (b) no non-test file in the set reads DemandSignal or calls
      PlanBeforeSignalDemand (the set has no demand site);
  (c) the function's own output is consistent with its claim: DemandSignal is
      derived from Resolvable(), so an unresolvable base yields DemandSignal=false;
  (d) no in-set text claims that the set wires/integrates a demand site.

Only (a)+(b)+(c)/(d) together would be an in-set contradiction: a wiring claim
with no wiring, or a function whose output belies its own sentence. Whether the
packet was obliged to deliver the integration lives in the work graph, which is
not in the set (out-of-contract), and whether "never spends signal attempts" is a
promise about the function or about the system is a reading question.

Exit 0 = control is DEFECTIVE (in-set contradiction found).
Exit 1 = SOUND on the in-set test; `needs_judgment` reports the residual.
"""
import json, os, re, sys
exchange = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
DISPATCH = "1ff35885260cc6b8"
full = [x for x in os.listdir(os.path.join(exchange, "dispatch"))
        if x.startswith(DISPATCH)][0]
bundle = os.path.join(exchange, "dispatch", full)
man = json.load(open(os.path.join(bundle, "manifest.json")))
files = json.loads(open(os.path.join(bundle, man["inputs"][0]["path"]),
                        errors="replace").read())["files"]
results = {"files_in_set": sorted(files)}
base_go = next(c for n, c in files.items() if n.endswith("verification/base.go"))
nontest = {n: c for n, c in files.items()
           if n.endswith(".go") and not n.endswith("_test.go")}

# (a) the claims, verbatim.
results["claim_never_spends_signal_attempts"] = bool(re.search(
    r"It never spends signal attempts on an\s+// unresolvable base\.", base_go))
results["claim_discovers_at_demand_sites"] = (
    "// Package verification discovers freshness conditions at verification demand sites."
    in base_go)

# (b) no consumer of the plan anywhere in the set's non-test code.
def strip_comments(src):
    return re.sub(r"//[^\n]*", "", src)
code = {n: strip_comments(c) for n, c in nontest.items()}
results["nontest_reads_of_DemandSignal"] = sum(
    len(re.findall(r"\.DemandSignal\b", c)) for c in code.values())
results["nontest_callsites_PlanBeforeSignalDemand"] = sum(
    len(re.findall(r"(?<!func )PlanBeforeSignalDemand\(", c)) for c in code.values())
results["nontest_files"] = sorted(nontest)

# (c) the function's own output honours the sentence: DemandSignal comes from
# Resolvable(), and Resolvable() is the pinned==current hash comparison.
fn = re.search(r"(?s)func PlanBeforeSignalDemand\(.*?\n}\n", base_go).group(0)
results["demand_signal_derived_from_resolvable"] = (
    "demandSignal := base.Resolvable()" in fn
    and fn.count("DemandSignal: demandSignal") == 2)
results["resolvable_is_hash_equality"] = (
    "return base.PinnedBaseHash == base.CurrentBaseHash" in base_go)
results["function_has_side_effects"] = bool(
    re.search(r"\b(go |chan |os\.|net\.|http\.|exec\.)", strip_comments(fn)))

# (d) does any in-set text claim the set itself wires/integrates a demand site?
alltext = "\n".join(files.values())
results["inset_claims_integration_or_wiring"] = bool(re.search(
    r"\b(wires?|wired|integrat\w*|hooks? into|installs?)\b", alltext, re.I))

# Out-of-contract residue, reported not scored.
results["out_of_contract"] = [
    "packet scope (was demand-site integration owed by fnnj-003?) lives in the "
    "work graph, not in the set",
    "actual demand sites / callers live outside the set",
    "algebra.InvalidateAll (which the in-set test expects to error on empty "
    "SubjectID/SignalID) is outside the set",
]
results["needs_judgment"] = (
    "whether 'never spends signal attempts' promises function behaviour (held "
    "in-set: DemandSignal=false when unresolvable) or system behaviour (not "
    "enforceable by a pure planning function with no in-set caller)")

defective = (
    results["claim_never_spends_signal_attempts"]
    and not results["demand_signal_derived_from_resolvable"]
) or (
    results["inset_claims_integration_or_wiring"]
    and results["nontest_reads_of_DemandSignal"] == 0
    and results["nontest_callsites_PlanBeforeSignalDemand"] == 0
)
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND (in-set); see needs_judgment")
sys.exit(0 if defective else 1)
