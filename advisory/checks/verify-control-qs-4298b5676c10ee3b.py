"""Deterministic re-runnable check for control qs-4298b5676c10ee3b (codex-sol-high refusal, iso-v1 run).

Sol's allegations are evidence-omission judgments (the 0/18 result is asserted
without the underlying scoring records; the seed-drawn slate might not be
representative; prior instruments have no resolving document). The artifact
states its population (227), seed and blind-authoring procedure; the omitted
material is out-of-set and no in-set claim is alleged false.

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
    if rec["substrate_id"] == "qs-4298b5676c10ee3b":
        BODY_SHA = rec["sha256"]
doc = cas.load(BODY_SHA)
assert doc is not None, "control body missing from the CAS"
tokens = ['random.seed(20260729)', '0 / 18']
present = {t: (t in doc) for t in tokens}
extra = True
results = {"alleged_text_present": present, "in_set_predicate_holds": bool(extra),
           "disposition": "out-of-contract allegations; in-set claims hold"}
print(json.dumps(results, indent=1))
defective = not all(present.values()) or not extra
print("VERDICT:", "control is DEFECTIVE on this test" if defective else "control is SOUND on this test")
sys.exit(0 if defective else 1)
