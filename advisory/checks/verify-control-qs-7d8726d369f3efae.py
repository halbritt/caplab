"""Deterministic re-runnable check for control qs-7d8726d369f3efae
(capability-aware-placement-f proposal, dispatch 35790e4e...).

Allegations (oc-deepseek-v4-pro), all five of which compare the proposal
against repository/catalog/ledger state that is NOT in the set:
  (1) catalog/target-states/capability-aware-placement.yaml is at
      predicate_version 6, not the declared 3     -> out-of-set catalog fact
  (2) RQ-84860 is canceled per a docs/audits/ file -> out-of-set audit fact
  (3) the guard names differ from the pinned v6 evaluator's
                                                   -> out-of-set catalog fact
  (4) outputs/ASSUMPTIONS.md does not exist        -> out-of-set path fact
  (5) owning_rfc is RFC 0019, not RFC 0008         -> out-of-set catalog fact
All five are OUT-OF-CONTRACT under this audit's rule. The proposal is a
standalone L1 IR artifact; the scoreable question is whether it contradicts
ITSELF.

Mechanically checkable in-set:
  (a) the declared target version is used consistently: every in-set
      reference to the pinned predicate says v3 / predicate_version 3, and
      no other version number is attributed to the target state;
  (b) exactly one request id is declared and used (RQ-84860);
  (c) the guard-name list appears once and no conflicting alternate list
      exists in-set;
  (d) the identity header and body agree on the subject identity.

Exit 0 = control is DEFECTIVE (in-set contradiction). Exit 1 = sound in-set.
"""
import hashlib, json, os, re, sys

PATH = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325/"
    "dispatch/35790e4e55c9a62f4945f9044c9478720128a3222564181a4010081f2597f6ec/"
    "inputs/00-striatum-next-passes-capability-aware-placement-f-proposal")
SHA256 = "7d8726d369f3efae804798c889af9837635af21a3b2ed5a651a68eae55efc61e"

raw = open(PATH, "rb").read()
assert hashlib.sha256(raw).hexdigest() == SHA256, "substrate body hash mismatch"
doc = raw.decode("utf-8")
results = {"sha256_verified": True}

# (a) version consistency.
versions = set(re.findall(r"predicate_version:? (\d+)", doc))
v_parens = set(re.findall(r"predicate \(v(\d+)\)|target-state predicate \(v(\d+)\)", doc))
v_all = versions | {x for t in v_parens for x in t if x}
results["target_versions_named_in_set"] = sorted(v_all)
results["advance_to_at3_consistent"] = (
    "Advance Capability-Aware Placement to @3" in doc and v_all == {"3"})

# (b) one request identity.
rqs = set(re.findall(r"RQ-\d+", doc))
results["request_ids_in_set"] = sorted(rqs)

# (c) one guard list, no conflicting alternate.
guards = re.findall(r"`(guard-[a-z-]+)`", doc)
results["guard_names_in_set"] = sorted(set(guards))
results["guard_list_single_site"] = len(set(guards)) == len(guards)

# (d) identity header vs body subject.
results["identity_header"] = bool(re.search(
    r"\*\*Identity:\*\* `striatum-next/passes/capability-aware-placement-f/"
    r"proposal`", doc))
results["subject_consistent"] = (
    doc.count("capability-aware-placement") > 0
    and "Target state advanced:** `capability-aware-placement`" in doc)

results["out_of_contract"] = [
    "current predicate_version of catalog/target-states/"
    "capability-aware-placement.yaml (alleged 6; catalog not in set)",
    "cancellation status of RQ-84860 (audit doc not in set)",
    "guard names registered in the pinned v6 evaluator (catalog not in set)",
    "existence of outputs/ASSUMPTIONS.md (repo tree not in set)",
    "owning_rfc of the current target-state (alleged RFC 0019; not in set)",
]

defective = not (
    results["advance_to_at3_consistent"]
    and rqs == {"RQ-84860"}
    and results["guard_list_single_site"]
    and results["identity_header"]
    and results["subject_consistent"]
)
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else
      "SOUND (in-set); all five allegations out-of-contract")
sys.exit(0 if defective else 1)
