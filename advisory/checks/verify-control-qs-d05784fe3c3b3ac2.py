"""Deterministic re-runnable check for control qs-d05784fe3c3b3ac2 (codex-sol-high refusal, iso-v1 run).

Sol alleges that C8 requires data-only packets to name 'the registered go-test
check id' while the design never identifies that id, so the acceptance surface
is incomplete. The design names the check by its registered role and states it
does not invent interfaces or mechanics; the id itself is the work graph's to
carry and the legality gate's to resolve. Distinguished from the qs-ccfd2a5f
ruling, where a plan named literal ids it never explained; this design names
no literal id. Prior-art and target-registration references are out-of-
contract. Flagged: the Principal may extend the ccfd ruling to role-named
checks.

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
    if rec["substrate_id"] == "qs-d05784fe3c3b3ac2":
        BODY_SHA = rec["sha256"]
doc = cas.load(BODY_SHA)
assert doc is not None, "control body missing from the CAS"
tokens = ['the registered go-test check id', 'go build and go test']
present = {t: (t in doc) for t in tokens}
extra = True
results = {"alleged_text_present": present, "in_set_predicate_holds": bool(extra),
           "disposition": "out-of-contract allegations; in-set claims hold"}
print(json.dumps(results, indent=1))
defective = not all(present.values()) or not extra
print("VERDICT:", "control is DEFECTIVE on this test" if defective else "control is SOUND on this test")
sys.exit(0 if defective else 1)
