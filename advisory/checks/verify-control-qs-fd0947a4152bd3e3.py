"""Deterministic re-runnable check for control qs-fd0947a4152bd3e3
(check-registries-portable implementation plan, revision).

Allegations (deepseek v4 flash): the Revision Note cites review ledgers
`evidence/review/striatum-next-passes-check-registries-portable-implementation-plan/10860`
and `/10611` that resolve nowhere in the striatum-next working tree or git
history, and the "prior plan" whose fixes are carried forward is likewise
absent.

In-set adjudication: review ledgers are provenance-ledger evidence, and the
prior plan is a prior artifact version — both live in the graph store / base
repository, not in this single-document set. Whether they resolve is
OUT-OF-CONTRACT by the audit standard (allegations depending on out-of-set
files are recorded, never scored). What IS in-set checkable is whether the
Revision Note's claims about this document's own content hold:
  (a) "The fenced work graph no longer references AC-* labels" — no AC-*
      appears in the fenced striatum-work-graph;
  (b) packet acceptance_checks use only the named set names
      {code, subject-default, stalls-guards};
  (c) the carried-forward 10611 fixes are actually present in the document
      (two-tier guard split; fixture-binary resolver testing; workstation
      proof as explicit operator evidence OE-01..OE-03).

Exit 0 = control is DEFECTIVE (an in-set revision-note claim is false).
Exit 1 = SOUND on the in-set test; the ledger-resolution residue is recorded.
"""
import hashlib, json, re, sys

PATH = ("/home/halbritt/.local/share/striatum/exchange/"
        "019f22ef-0cb4-780f-9b82-b210bab24325/dispatch/"
        "6cba7512d976297ac16be1ba12aaae2539a1703328e6ae82369cf02b06bbee64/"
        "inputs/00-striatum-next-passes-check-registries-portable-implementation-plan")
SHA = "fd0947a4152bd3e33bfa98aae591ddf22991daae7aa0872412ebf82246b537db"

raw = open(PATH, "rb").read()
assert hashlib.sha256(raw).hexdigest() == SHA, "substrate body hash mismatch"
doc = raw.decode("utf-8")
results = {}

# The contested citations are present (the allegation targets real text)...
results["cites_ledger_10860"] = (
    "evidence/review/striatum-next-passes-check-registries-portable-"
    "implementation-plan/10860" in doc)
results["cites_ledger_10611"] = "ledger\n10611" in doc or "ledger 10611" in doc

# (a)+(b): the fenced work graph honours the revision-note claims.
graph_src = re.search(r"```striatum-work-graph\n(.*?)```", doc, re.S).group(1)
graph = json.loads(graph_src)
results["fenced_graph_has_no_AC_labels"] = not re.search(r"\bAC-\d", graph_src)
acs = sorted({c for p in graph["packets"] for c in p["acceptance_checks"]})
results["acceptance_checks_used"] = acs
results["only_named_registry_sets_used"] = set(acs) <= {
    "code", "subject-default", "stalls-guards"}

# (c): the carried-forward fixes exist in this document.
results["two_tier_guard_split_present"] = (
    "Tier H - hermetic" in doc and "Tier W - workstation-coupled" in doc)
results["fixture_binary_resolver_testing_present"] = bool(
    re.search(r"fixture\s+roots, fixture\s*\nexecutables|test-constructed fixture roots", doc))
results["workstation_proof_as_operator_evidence"] = (
    "OE-01" in doc and "OE-02" in doc and "OE-03" in doc
    and "Operator Evidence Outside Work Graph" in doc)

# In-set reference resolution: every derived_from anchor exists in the doc.
anchors = set(re.findall(r"\{#(el:[a-z0-9-]+)\}", doc))
derived = [p["derived_from"].lstrip("#") for p in graph["packets"]]
results["unresolved_derived_from_anchors"] = [a for a in derived if a not in anchors]

results["out_of_contract"] = [
    "whether evidence/review/.../10860 and /10611 exist lives in the graph "
    "store / base repository, outside this single-document set",
    "whether a prior plan version exists lives in artifact-version history, "
    "outside the set",
]

defective = not all([
    results["fenced_graph_has_no_AC_labels"],
    results["only_named_registry_sets_used"],
    results["two_tier_guard_split_present"],
    results["fixture_binary_resolver_testing_present"],
    results["workstation_proof_as_operator_evidence"],
    not results["unresolved_derived_from_anchors"]])
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND (in-set); allegations out-of-contract")
sys.exit(0 if defective else 1)
