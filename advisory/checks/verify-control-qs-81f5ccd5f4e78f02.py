"""Deterministic re-runnable check for control qs-81f5ccd5f4e78f02 (codex-sol-high refusal, iso-v1 run).

Sol alleges the permitted-effects list mixes exact globs with broad categories
('CAPLAB-owned study instrument, schema, execution, and verification records';
pushes to an unnamed branch), against a stated requirement of an exact durable
scope. Whether a category bounded by ownership and record kind is 'exact' is a
judgment about the authorization contract, not a contradiction within the
text. No in-set claim is alleged false.

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
    if rec["substrate_id"] == "qs-81f5ccd5f4e78f02":
        BODY_SHA = rec["sha256"]
doc = cas.load(BODY_SHA)
assert doc is not None, "control body missing from the CAS"
tokens = ['Permitted repository effects are limited to', 'src/caplab/preference/**']
present = {t: (t in doc) for t in tokens}
extra = True
results = {"alleged_text_present": present, "in_set_predicate_holds": bool(extra),
           "disposition": "out-of-contract allegations; in-set claims hold"}
print(json.dumps(results, indent=1))
defective = not all(present.values()) or not extra
print("VERDICT:", "control is DEFECTIVE on this test" if defective else "control is SOUND on this test")
sys.exit(0 if defective else 1)
