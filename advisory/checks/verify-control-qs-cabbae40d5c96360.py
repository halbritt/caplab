"""Deterministic re-runnable check for dispatch b259a09f... (control
qs-cabbae40d5c96360, packet packet-08-integration-verification).

Allegation (codex-sol-high): the package doc overclaims — the tests construct
the engine directly rather than invoking the driver, and load a copied testdata
check registry whose entries are only resolved, never executed, so they do not
establish that the whole pass is exercised "exactly as the driver wires them".

What is mechanically checkable INSIDE the change set:
  (a) the claim sentences are present in placement_test.go;
  (b) the test imports no driver package and calls nothing named driver; it
      builds the engine via ranking.LoadCatalog + pass.LoadFloors + pass.NewEngine;
  (c) the registry is used only through ResolveSet / ResolveEntries / Set — no
      execution path;
  (d) whether any in-set text claims driver INVOCATION (as opposed to
      equivalence with the driver's wiring) or check EXECUTION (as opposed to
      selection);
  (e) every component the doc enumerates as "the WHOLE pass" (floor check,
      ranking function, placement-kind separation, pass runner registration) is
      actually driven by some test in the file.

An in-set contradiction exists only if (d) claims invocation/execution and
(b)/(c) show none, or if (e) names a component no test touches. Equivalence
with the driver's wiring and fidelity of the testdata registry to the
repository registry both depend on files outside the set (out-of-contract).

Exit 0 = control is DEFECTIVE (in-set contradiction found).
Exit 1 = SOUND on the in-set test; `out_of_contract` reports the residual.
"""
import json, os, re, sys
exchange = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
DISPATCH = "b259a09ffe23269e"
full = [x for x in os.listdir(os.path.join(exchange, "dispatch"))
        if x.startswith(DISPATCH)][0]
bundle = os.path.join(exchange, "dispatch", full)
man = json.load(open(os.path.join(bundle, "manifest.json")))
body = json.loads(open(os.path.join(bundle, man["inputs"][0]["path"]),
                       errors="replace").read())
files = body["files"]
results = {"files_in_set": sorted(files)}
test = next(c for n, c in files.items() if n.endswith("placement_test.go"))
comments = "\n".join(re.findall(r"//[^\n]*", test))
code = re.sub(r"//[^\n]*", "", test)

# (a) the claims, verbatim.
results["claim_whole_pass"] = "it drives the WHOLE pass over pinned catalog fixtures" in test
results["claim_exactly_as_driver_wires"] = bool(re.search(
    r"end to end, exactly as the driver\s+// wires them", test))
results["claim_same_catalogs_driver_parses"] = "the\n// same two catalogs the driver parses" in test
results["claim_fixture_is_real_registry"] = "the fixture is the real registry" in test
results["claim_selection_rule"] = "confirms the\n// corrected class-aware selection rule" in test

# (b) no driver in the test.
imports = re.findall(r'"(github\.com/[^"]+)"', test)
results["imports"] = imports
results["imports_driver_package"] = any("driver" in p for p in imports)
results["code_references_driver_identifier"] = bool(
    re.search(r"\b[dD]river\b", code))
results["engine_built_by_hand"] = all(s in code for s in (
    "ranking.LoadCatalog(", "pass.LoadFloors(", "pass.NewEngine("))

# (c) registry is resolve-only.
reg_methods = sorted(set(re.findall(r"registry\.(\w+)\(", code)))
results["registry_methods_called"] = reg_methods
results["registry_executes_anything"] = any(
    re.search(r"run|exec|invoke|start", m, re.I) for m in reg_methods)
results["registry_loaded_from_testdata"] = 'fixture("checks-registry.json")' in code

# (d) does any in-set text claim driver invocation or check execution?
results["doc_claims_driver_invocation"] = bool(re.search(
    r"(invok\w*|call\w*|run\w*|launch\w*|through|via) the driver", comments, re.I))
results["doc_claims_checks_executed"] = bool(re.search(
    r"(execut\w*|run\w*) (the |every |each |all )?(check|registry)", comments, re.I))

# (e) every enumerated "WHOLE pass" component is driven by some test.
components = {
    "floor check": r"engine\.Screen\(",
    "ranking function": r"engine\.Rank\(",
    "placement-kind separation": r"kinds\.(SoleSignal|AdditionalSignal|Primary)",
    "pass runner registration": r"reg\.Register(Contract|Candidate)\(|local\.DefaultPlacementRegistry\(",
}
results["enumerated_components_driven"] = {
    k: bool(re.search(v, code)) for k, v in components.items()}
results["doc_enumerates_components"] = bool(re.search(
    r"the\s+// floor check, the ranking function, the placement-kind separation, and the pass\s+// runner registration", test))

# Self-consistency of the fixtures the test leans on (in-set only).
wg = json.loads(files["internal/placement/testdata/work-graph.json"])
reg = json.loads(files["internal/placement/testdata/checks-registry.json"])
p08 = next(p for p in wg["packets"] if p["id"] == "packet-08-integration-verification")
results["work_graph_packet08_scope_matches_set"] = all(
    any(n.startswith(s) for s in p08["write_scope"]) for n in files)
results["registry_has_subject_default_set"] = bool(reg["sets"].get("subject-default"))
results["work_graph_names_driver_scope"] = any(
    "internal/driver/" in p.get("write_scope", []) for p in wg["packets"])

results["out_of_contract"] = [
    "whether internal/driver wires LoadCatalog+LoadFloors+NewEngine identically "
    "(the driver is not in the set; the work-graph fixture only names its scope)",
    "whether testdata/checks-registry.json byte-matches the repository registry "
    "(checks.Load's content-address re-verification is outside the set)",
    "whether testdata/*.yaml mirror catalog/placement-classes and "
    "catalog/governed-declarations (those catalogs are outside the set)",
]

defective = (
    (results["doc_claims_driver_invocation"]
     and not results["imports_driver_package"]
     and not results["code_references_driver_identifier"])
    or (results["doc_claims_checks_executed"]
        and not results["registry_executes_anything"])
    or (results["doc_enumerates_components"]
        and not all(results["enumerated_components_driven"].values()))
)
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND (in-set); see out_of_contract")
sys.exit(0 if defective else 1)
