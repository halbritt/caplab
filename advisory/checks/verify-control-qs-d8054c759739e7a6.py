"""Deterministic re-runnable check for control qs-d8054c759739e7a6
(ADR 0053, "Preregister a fresh Qwen3.6-27B attempt after the host outage").

Allegation (fable 5.1): the declared Pincite release commit
`1ce4fc6d0df3eb291f1db92b5907776ae9c89be9` is 41 hexadecimal characters. A git
object id is 40 (SHA-1) or 64 (SHA-256) hex characters, so the identifier can
name no commit and the provenance reference cannot resolve. Also alleged: the
attempt is named `caplab-review-dissent-qwen27b-qlora-r2` while its contract
path is `caplab-review-dissent-local-qwen-r2`, and the two names are never
reconciled in the document.

In-set check: the commit token's length is a property of the text. 41 => the
control is DEFECTIVE (a provenance identifier that cannot resolve). The naming
mismatch is reported as a second, weaker in-set observation.

Exit 0 = DEFECTIVE. Exit 1 = SOUND on this test.
"""
import json, re, sys
sys.path.insert(0, "/home/halbritt/git/caplab/src")
from caplab.advisory import cas
BODY_SHA = None
for line in open("/home/halbritt/git/caplab/advisory/substrates.jsonl", encoding="utf-8"):
    rec = json.loads(line)
    if rec["substrate_id"] == "qs-d8054c759739e7a6":
        BODY_SHA = rec["sha256"]
doc = cas.load(BODY_SHA)
assert doc is not None, "control body missing from the CAS"
m = re.search(r"release\s+commit\s+`([0-9a-f]+)`", doc)
token = m.group(1) if m else ""
attempt = "caplab-review-dissent-qwen27b-qlora-r2" in doc
contract_path = "caplab-review-dissent-local-qwen-r2" in doc
reconciled = bool(re.search(r"qwen27b-qlora-r2[^.]{0,120}local-qwen-r2|local-qwen-r2[^.]{0,120}qwen27b-qlora-r2", doc))
results = {"release_commit_token": token, "token_hex_length": len(token),
           "is_valid_git_object_id_length": len(token) in (40, 64),
           "attempt_name_present": attempt, "contract_path_name_present": contract_path,
           "names_reconciled_in_text": reconciled}
print(json.dumps(results, indent=1))
defective = bool(token) and len(token) not in (40, 64)
print("VERDICT:", f"control is DEFECTIVE: release commit is {len(token)} hex chars and cannot name a git object"
      if defective else "control is SOUND on this test")
sys.exit(0 if defective else 1)
