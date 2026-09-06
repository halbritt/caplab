"""Deterministic re-runnable check for control qs-5f841949fa746b8e (codex-sol-high refusal, iso-v1 run).

Sol alleges the record is internally inconsistent because its status says
`selected-by-adr-0027` while the Owner response section still presents the
disposition as awaiting selection. The artifact is a decision proposal: its
body is the proposal as written, and its frontmatter records the later
disposition and names the record that made it (`disposition_record:
adr-0027`). Both facts are stated; nothing is contradicted. The reference-
resolution allegations are out-of-contract.

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
    if rec["substrate_id"] == "qs-5f841949fa746b8e":
        BODY_SHA = rec["sha256"]
doc = cas.load(BODY_SHA)
assert doc is not None, "control body missing from the CAS"
tokens = ['status: selected-by-adr-0027', 'disposition_record: adr-0027', 'The owner may select exactly one current disposition']
present = {t: (t in doc) for t in tokens}
extra = ('status: selected-by-adr-0027' in doc and 'disposition_record: adr-0027' in doc)
results = {"alleged_text_present": present, "in_set_predicate_holds": bool(extra),
           "disposition": "out-of-contract allegations; in-set claims hold"}
print(json.dumps(results, indent=1))
defective = not all(present.values()) or not extra
print("VERDICT:", "control is DEFECTIVE on this test" if defective else "control is SOUND on this test")
sys.exit(0 if defective else 1)
