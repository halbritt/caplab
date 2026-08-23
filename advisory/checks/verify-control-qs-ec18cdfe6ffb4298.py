"""Deterministic re-runnable check for dispatch 838b7f43... (control
qs-ec18cdfe6ffb4298, subject striatum-next/passes/work-graph-assembly-c/design,
RQ-105497 — a 46KB design document, the dispatch's sole input).

Allegations (oc-deepseek-v4-pro):
  A1: #el:iface-fixture-store declares guard entrypoint
      `go run ./tools/standing-guards/wgi-subject-assembly` and states it
      "resolves to the pinned guard check id"
      4cfe89f9ce1527a41ea164e83e5e910b1a29294450653afeda115ab39ebc3a82,
      but the registry (policy/checks/repository.json) registers that id
      with a different argv (./tools/standing-guards/
      wgi-subject-assembles-from-packets).
  A2: the header cites "the accepted design-convergence@3 pass contract",
      but catalog/passes/design-convergence.yaml is now contract_version 4.

Contract position: both allegations depend on out-of-set files (the check
registry; the catalog). OUT-OF-CONTRACT — recorded, never scored. Out-of-set
fact-check for the record: A1 is TRUE against the live registry (4cfe89f9's
argv is `go run ./tools/standing-guards/wgi-subject-assembles-from-packets`,
delivery_status red) and A2 is TRUE against the live catalog
(contract_version: 4). Neither fact is derivable from the set.

What is mechanically checkable INSIDE the set:
  (a) the document tells ONE consistent entrypoint story: the pinned check id
      appears with a single value, exactly one standing-guard entrypoint name
      is ever associated with it, and no second in-set statement gives a
      different argv/entrypoint for that id;
  (b) the document cites ONE design-convergence contract version (no in-set
      statement names a conflicting version).

Exit 0 = control is DEFECTIVE (in-set contradiction found).
Exit 1 = SOUND on the in-set test; out-of-set residue reported, not scored.
"""
import hashlib, json, os, re, sys

PATH = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325/"
    "dispatch/838b7f43a6a99760b724f5b394e2b40982511745a0e2c32347f040255ce6f495/"
    "inputs/00-striatum-next-passes-work-graph-assembly-c-design")
SHA = "ec18cdfe6ffb42983ed7d53a6c1c78635708371029d8649f7faa49e908aa89d5"

raw = open(PATH, "rb").read()
if hashlib.sha256(raw).hexdigest() != SHA:
    print("FATAL: substrate sha256 mismatch — refusing to adjudicate")
    sys.exit(2)
doc = raw.decode("utf-8")
results = {"substrate_sha256_verified": True}

# (a) one consistent entrypoint story for the pinned check id.
ids = set(re.findall(r"\b[0-9a-f]{64}\b", doc))
results["check_ids_cited"] = sorted(ids)
results["single_check_id"] = len(ids) == 1
guards = set(re.findall(r"tools/standing-guards/([A-Za-z0-9_-]+)", doc))
results["guard_entrypoints_named"] = sorted(guards)
results["single_guard_entrypoint"] = len(guards) == 1
results["entrypoint_is_wgi_subject_assembly"] = guards == {"wgi-subject-assembly"}
results["claims_resolves_to_pinned_id"] = (
    "resolves to the pinned guard check id" in doc)
# any in-set statement of a registry argv that conflicts?
results["inset_conflicting_argv_statements"] = len(
    re.findall(r"argv", doc, re.I))

# (b) one design-convergence contract version cited.
dc_versions = set(re.findall(r"design-convergence@(\d+)", doc))
results["design_convergence_versions_cited"] = sorted(dc_versions)
results["single_dc_version"] = len(dc_versions) <= 1

results["out_of_contract"] = [
    "A1: the id->argv binding lives in policy/checks/repository.json "
    "(out-of-set). Live registry fact, recorded not scored: 4cfe89f9's argv "
    "is `go run ./tools/standing-guards/wgi-subject-assembles-from-packets` "
    "(delivery_status red) — the design's `wgi-subject-assembly` name does "
    "NOT match; the allegation is true out-of-set.",
    "A2: contract_version lives in catalog/passes/design-convergence.yaml "
    "(out-of-set). Live catalog fact: contract_version: 4 — the @3 citation "
    "is stale out-of-set; whether it was current at the pinned review "
    "environment would need the sealed environment, also out-of-set.",
]

defective = (
    not results["single_check_id"]
    or not results["single_guard_entrypoint"]
    or not results["single_dc_version"]
    or results["inset_conflicting_argv_statements"] > 0
)
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else
      "SOUND (in-set); both allegations out-of-contract")
sys.exit(0 if defective else 1)
