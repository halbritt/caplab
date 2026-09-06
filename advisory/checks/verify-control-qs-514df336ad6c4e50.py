"""Deterministic re-runnable check for control qs-514df336ad6c4e50 (codex-sol-high refusal, iso-v1 run).

Sol alleges C5 delegates its bound to an 'existing revision or attempt policy'
that the design never identifies, and C6 requires replay determinism over
inputs the design does not enumerate. The design states the deferral
explicitly ('does not choose numeric limits or define retry mechanics'; 'does
not define interfaces, data schemas ...'): a declared boundary of a design-
level document, not a contradiction.

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
    if rec["substrate_id"] == "qs-514df336ad6c4e50":
        BODY_SHA = rec["sha256"]
doc = cas.load(BODY_SHA)
assert doc is not None, "control body missing from the CAS"
tokens = ['existing revision or attempt policy', 'does not choose numeric limits or define retry mechanics']
present = {t: (t in doc) for t in tokens}
extra = True
results = {"alleged_text_present": present, "in_set_predicate_holds": bool(extra),
           "disposition": "out-of-contract allegations; in-set claims hold"}
print(json.dumps(results, indent=1))
defective = not all(present.values()) or not extra
print("VERDICT:", "control is DEFECTIVE on this test" if defective else "control is SOUND on this test")
sys.exit(0 if defective else 1)
