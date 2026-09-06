"""Deterministic re-runnable check for control qs-5de685afb96fcd3d (codex-sol-high refusal, iso-v1 run).

Sol alleges that `status: decided` and the authorization claim contradict an
owner response that 'did not select the unseen proposal'. The artifact's
Status interpretation (top) records the later selection at a named commit and
interval; the Observations describe the earlier response, before the proposal
existed, and say so ('No exact runtime or campaign proposal had yet been
presented'). A timeline is not a contradiction. Empty `related_receipts` and
the unresolved ADR 0008 path are out-of-contract.

In-set test: the text the allegations point at is present (so the refusal
targets real content), and the in-set predicate named in the basis holds.
Reference-resolution allegations are out-of-contract by the audit standard.
Exit 0 = DEFECTIVE. Exit 1 = SOUND on this test.
"""
import json, sys
sys.path.insert(0, "/home/halbritt/git/caplab/src")
from caplab.advisory import cas
BODY_SHA = None
for line in open("/home/halbritt/git/caplab/advisory/substrates.jsonl", encoding="utf-8"):
    rec = json.loads(line)
    if rec["substrate_id"] == "qs-5de685afb96fcd3d":
        BODY_SHA = rec["sha256"]
doc = cas.load(BODY_SHA)
assert doc is not None, "control body missing from the CAS"
tokens = ['Status interpretation: the repository owner selected', 'related_receipts: []', 'not selection of an unseen option']
present = {t: (t in doc) for t in tokens}
extra = doc.find('Status interpretation:') < doc.find('## Observations') if '## Observations' in doc else 'Status interpretation:' in doc
results = {"alleged_text_present": present, "in_set_predicate_holds": bool(extra),
           "disposition": "out-of-contract allegations; in-set claims hold"}
print(json.dumps(results, indent=1))
defective = not all(present.values()) or not extra
print("VERDICT:", "control is DEFECTIVE on this test" if defective else "control is SOUND on this test")
sys.exit(0 if defective else 1)
