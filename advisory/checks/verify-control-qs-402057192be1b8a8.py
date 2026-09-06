"""Deterministic re-runnable check for control qs-402057192be1b8a8
(caplab-review-dissent-qwen27b-qlora-r1 preregistration, repo-doc).

Allegations (codex-sol-high, iso-v1 run): (a) ADR identities adr-0049 and
adr-0026 are not reachable within the artifact; (b) training-experiment.json
is not present, so its SHA-256 cannot be verified; (c) corpus.json and
general-coding-controls.json are not included; (d) the top-level status is
`preregistered` while the latest lifecycle entry is
`host-amended-before-execution`, unexplained.

Adjudication: (a)-(c) depend on files outside this single-document set and are
OUT-OF-CONTRACT by the audit standard (recorded, never scored). (d) is in-set:
the lifecycle entry itself states that only the execution host changed, that
no model, corpus, method, seed, step, evaluation or success rule changed, and
that no execution effect had occurred — which is exactly the state
`preregistered` names. The status and the lifecycle agree. SOUND.

Exit 0 = DEFECTIVE. Exit 1 = SOUND on this test.
"""
import json, re, sys
sys.path.insert(0, "/home/halbritt/git/caplab/src")
from caplab.advisory import cas
BODY_SHA = None
for line in open("/home/halbritt/git/caplab/advisory/substrates.jsonl", encoding="utf-8"):
    rec = json.loads(line)
    if rec["substrate_id"] == "qs-402057192be1b8a8":
        BODY_SHA = rec["sha256"]
doc = cas.load(BODY_SHA)
assert doc is not None, "control body missing from the CAS"
status = re.search(r"^status: (\S+)", doc, re.M).group(1)
amended = re.search(r"`host-amended-before-execution`.*?(?=\n- |\Z)", doc, re.S)
amended_text = amended.group(0) if amended else ""
explains = bool(re.search(r"No\s+model,\s+corpus,\s+method,\s+seed,\s+step,\s+evaluation,\s+or\s+success\s+rule\s+changed", amended_text)) \
    and bool(re.search(r"no execution effect had occurred", amended_text))
external_refs = [t for t in ("adr-0049", "adr-0026", "training-experiment.json", "corpus.json",
                             "general-coding-controls.json") if t in doc]
results = {"status": status, "latest_lifecycle": "host-amended-before-execution" if amended else None,
           "amendment_explains_scope_and_no_execution": explains,
           "status_lifecycle_contradiction": not (status == "preregistered" and explains),
           "out_of_set_references_alleged_unresolvable": external_refs}
print(json.dumps(results, indent=1))
defective = results["status_lifecycle_contradiction"]
print("VERDICT:", "control is DEFECTIVE: status and lifecycle disagree" if defective
      else "control is SOUND on this test: the amendment explains itself and preserves the preregistered state; "
           "file-resolution allegations are out-of-contract")
sys.exit(0 if defective else 1)
