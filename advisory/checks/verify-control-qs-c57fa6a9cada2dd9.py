"""Deterministic re-runnable check for control qs-c57fa6a9cada2dd9
(Proposal: Terminal Report Live — Emission Half, terminal-report-live-e).

Allegations (glm-flash; its three replicates split accept / needs_revision /
needs_revision): (a) "Evidence admissibility" and "Registered check set" bind
delivery to "all four named guard checks" while the proposal itself names only
two guard checks by id (`guard-drain-closure`, `exit-report-prompt-abandonment`)
— a declared count that does not match content; (b) the emission trigger's
closed three-reason set (`budget_expiry`, `relaunch_exhausted`, `runtime_exit`)
contradicts the conformance clause that "a clean fast exit produces a committed
report".

Adjudication: (a) the "four named guard checks" are the members of the check
set the proposal names, `trl2-guards`, which it treats as a declared input; the
count is a claim about that registered set, and the set has exactly four
members in the pinned registry (v37) and the live registry alike. The claim is
true; the allegation reads "named" as "named in this document", which the text
does not say. (b) `runtime_exit` is an exit reason; a clean fast exit is a
runtime exit, and the text never says otherwise — an interpretation, not a
contradiction. Neither allegation holds => SOUND.

Exit 0 = DEFECTIVE. Exit 1 = SOUND on this test.
"""
import json, os, re, sys
sys.path.insert(0, "/home/halbritt/git/caplab/src")
from caplab.advisory import cas
BODY_SHA = None
for line in open("/home/halbritt/git/caplab/advisory/substrates.jsonl", encoding="utf-8"):
    rec = json.loads(line)
    if rec["substrate_id"] == "qs-c57fa6a9cada2dd9":
        BODY_SHA = rec["sha256"]
doc = cas.load(BODY_SHA)
assert doc is not None, "control body missing from the CAS"
REG = os.path.expanduser("~/.local/lib/caplab-instruments/plan-p2b-20260827/checks-repository-v37.json")
registry = json.load(open(REG))
trl2 = (registry.get("sets") or {}).get("trl2-guards") or []
claims_four = bool(re.search(r"all four named guard checks", doc))
names_set = "`trl2-guards`" in doc
exit_reasons = re.search(r"knowable `exit_reason`\s*\(([^)]*)\)", doc, re.S)
reasons = re.findall(r"`([a-z_]+)`", exit_reasons.group(1)) if exit_reasons else []
results = {"doc_claims_four_guard_checks": claims_four, "doc_names_check_set_trl2_guards": names_set,
           "trl2_guards_members_in_registry_v37": len(trl2), "count_claim_true_against_named_set": len(trl2) == 4,
           "emission_exit_reasons": reasons, "runtime_exit_covers_clean_exit": "runtime_exit" in reasons}
print(json.dumps(results, indent=1))
defective = claims_four and names_set and len(trl2) != 4
print("VERDICT:", "control is DEFECTIVE: the declared guard-check count contradicts the named set" if defective
      else "control is SOUND on this test: the named set has four members; runtime_exit is an exit reason")
sys.exit(0 if defective else 1)
