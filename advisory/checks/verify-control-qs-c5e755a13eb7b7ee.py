"""Deterministic re-runnable check for dispatch f07b350442986111... (substrate
qs-c5e755a13eb7b7ee, work-graph-assembly-b / lowering-rule-declaration change set).

Allegation under test (codex-sol-high refusal): the delivery defines a routing
API (Catalog.RouteSubjectAssembly) but integrates it into no production planning
or lowering path -- its only callers are tests -- so the README and code
comments claiming that matching demands actually lower to subject-assembly are
unearned and the delivery is incomplete.

What is checked, all from the change set's own files:
  * RouteSubjectAssembly is defined, and every call site in the set is in a
    _test.go file (no production caller in the set)                      (premise)
  * the README's sentence about what THE DRIVER does is limited to loading
    the rule and target-kind-checking its route; it does not say the driver
    or a planner routes / lowers demands                                   (defence)
  * that limited claim is earned: LoadCatalog calls loadLoweringRules and
    validateLoweringRules, and the rule file carries the three-conjunct
    trigger plus route.pass: subject-assembly                              (defence)
  * "the demand lowers to ..." sentences describe the rule's declared
    semantics; the code that denotes that semantics (Matches +
    RouteSubjectAssembly) is present and tested                            (defence)
  * comments in lowering_rules.go that mention "the planner" / "the caller"
    are reported; they describe the API's intended consumer, which is
    outside the set                                                        (note)
  * whether the packet's scope required planner integration is decided by
    the Work Graph, which is NOT in the change set -> out of contract.

The allegation is substantiated only if some in-set prose asserts that the
driver/planner routes or lowers demands AND no non-test file in the set calls
the routing API.

Exit 0 = control is DEFECTIVE.  Exit 1 = control is SOUND.
"""
import json, os, re, sys
exchange = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
DISPATCH = "f07b350442986111"
full = [x for x in os.listdir(os.path.join(exchange, "dispatch"))
        if x.startswith(DISPATCH)][0]
bundle = os.path.join(exchange, "dispatch", full)
man = json.load(open(os.path.join(bundle, "manifest.json")))
files = json.loads(open(os.path.join(bundle, man["inputs"][0]["path"]),
                        errors="replace").read())["files"]
results = {}

rules_go = files["internal/driver/lowering_rules.go"]
catalog_go = files["internal/driver/catalog.go"]
readme = files["catalog/pipelines/README.md"]
rule_yaml = files["catalog/pipelines/subject-assembly-lowering.yaml"]
prod_go = {n: c for n, c in files.items()
           if n.endswith(".go") and not n.endswith("_test.go")}
test_go = {n: c for n, c in files.items() if n.endswith("_test.go")}

# --- premise: routing API exists; only test callers in the set --------------
results["route_api_defined"] = bool(
    re.search(r"func \(c Catalog\) RouteSubjectAssembly\(", rules_go))
call = re.compile(r"\.RouteSubjectAssembly\(")
results["production_callers"] = sum(len(call.findall(c)) for c in prod_go.values())
results["test_callers"] = sum(len(call.findall(c)) for c in test_go.values())
results["only_test_callers_in_set"] = (
    results["production_callers"] == 0 and results["test_callers"] > 0)

# --- defence: what does the README actually say the driver does? -----------
driver_sentence = re.search(r"The driver [^.]*\.", readme)
results["readme_driver_sentence"] = driver_sentence.group(0) if driver_sentence else None
results["readme_driver_claim_is_load_and_check"] = bool(
    driver_sentence and "loads every `lowering-rule`" in driver_sentence.group(0)
    and "target-kind-checks each rule's route" in driver_sentence.group(0))
prose = readme + "\n" + "\n".join(
    l for l in (rules_go + "\n" + catalog_go).splitlines() if l.lstrip().startswith("//"))
# A claim that the driver / planner / LoadCatalog itself routes or lowers demands.
results["prose_claims_driver_or_planner_routes"] = bool(
    re.search(r"\b(driver|planner|LoadCatalog)\b[^.\n]*\b(routes|lowers|dispatches)\b", prose, re.I))
results["prose_planner_mentions"] = [
    l.strip() for l in rules_go.splitlines()
    if re.search(r"\b(the planner|the caller)\b", l, re.I)]

# --- defence: the limited claim is earned by in-set code -------------------
load = re.search(r"(?s)func LoadCatalog\(.*?\n}\n", catalog_go).group(0)
results["LoadCatalog_loads_rules"] = 'loadLoweringRules(filepath.Join(root, "pipelines"))' in load
results["LoadCatalog_validates_rules"] = "catalog.validateLoweringRules()" in load
results["rule_declares_three_conjuncts_and_route"] = (
    "demand_kind: change-set" in rule_yaml and "demand_grain: subject" in rule_yaml
    and "work_graph: multi-packet" in rule_yaml and "packet_heads: admitted" in rule_yaml
    and re.search(r"route:\s*\n\s*pass: subject-assembly", rule_yaml) is not None)
results["Matches_evaluates_all_three_conjuncts"] = all(
    s in rules_go for s in ("r.Trigger.DemandGrain", 'r.Trigger.WorkGraph == "multi-packet"',
                            'r.Trigger.PacketHeads == "admitted"'))
results["tests_pin_route_and_conjunction"] = (
    "TestSubjectAssemblyRouteRoutesOnlyRegisteredPass" in files["internal/driver/lowering_rules_test.go"]
    and "TestSubjectAssemblyTriggerRequiresEveryConjunct" in files["internal/driver/lowering_rules_test.go"])

# --- out of contract ------------------------------------------------------
results["note_packet_scope"] = (
    "OUT-OF-CONTRACT: whether this packet was required to wire the routing API "
    "into a planner is decided by the Work Graph packet definition, absent from the set")
results["note_callers_outside_set"] = (
    "OUT-OF-CONTRACT: a caller in a base file not in the set cannot be seen here")

defective = (results["only_test_callers_in_set"]
             and results["prose_claims_driver_or_planner_routes"])
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND")
sys.exit(0 if defective else 1)
