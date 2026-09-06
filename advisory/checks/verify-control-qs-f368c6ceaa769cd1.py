"""Deterministic re-runnable check for control qs-f368c6ceaa769cd1
(CAPLAB qualification contract v1, repo-doc, 40 KB).

Allegations (cc-glm-5-3-max, iso-v1 run): (1) the execution-authorization
schema is declared with a closed 15-key "exact keys" list yet live
authorizations must also carry apparatus_ref and custody_domain_id, and the
text "never states that the exact-keys list is variant-relative"; (2) the same
pattern for the reviews schema (execution_intent_ref, process_receipt_refs);
(3) exit code 3 is bound to "read-only integrity reports" with `ok: false`, but
no integrity-report operation or document is defined anywhere in the contract;
(4) `--custody` is said to fail closed while the register synopsis has no such
flag.

Adjudication: (1) and (2) are refuted in-set — the sentence immediately after
each exact-keys list states the variant relation ("Live authorization also
requires ...; local-fixture authorization forbids both fields"; "The live
reviews variant also has ..."). (4) is consistent: an option not offered that
is refused when supplied is what "fails closed" describes. (3) holds: the
contract opens by declaring itself closed-world ("Implementations reject
unknown fields and unsupported normative schema versions") and then binds an
exit code to a document kind ("integrity report", `ok: false`) that appears
nowhere else — no operation produces it, no schema defines it. Under the
2026-09-05 ruling on qs-ccfd2a5f (an artifact that holds itself to naming
everything it references and then does not is defective against its own
standard), applied here by analogy and flagged for the Principal, the control
is DEFECTIVE on (3) alone.

Exit 0 = DEFECTIVE. Exit 1 = SOUND on this test.
"""
import json, re, sys
sys.path.insert(0, "/home/halbritt/git/caplab/src")
from caplab.advisory import cas
BODY_SHA = None
for line in open("/home/halbritt/git/caplab/advisory/substrates.jsonl", encoding="utf-8"):
    rec = json.loads(line)
    if rec["substrate_id"] == "qs-f368c6ceaa769cd1":
        BODY_SHA = rec["sha256"]
doc = cas.load(BODY_SHA)
assert doc is not None, "control body missing from the CAS"
closed_world = bool(re.search(r"Implementations reject\s+unknown fields", doc))
auth_variant_stated = bool(re.search(r"Live authorization also requires `apparatus_ref` and `custody_domain_id`;\s*local-fixture authorization forbids both fields", doc))
reviews_variant_stated = bool(re.search(r"The live reviews variant also has `execution_intent_ref` and the ordered\s*`process_receipt_refs`", doc))
integrity_mentions = [m.start() for m in re.finditer(r"integrity report", doc, re.I)]
integrity_defined = bool(re.search(r"integrity[- ]report[^.]*(has exact keys|schema|`caplab-[a-z-]+integrity)", doc, re.I)) \
    or bool(re.search(r"caplab qualification (verify|check|integrity)", doc))
custody_flag_in_synopsis = bool(re.search(r"caplab qualification register[^\n]*(\n[^\n]*)?--custody", doc))
results = {"closed_world_rule": closed_world,
           "allegation_1_variant_relation_stated": auth_variant_stated,
           "allegation_2_variant_relation_stated": reviews_variant_stated,
           "integrity_report_mentions": len(integrity_mentions),
           "integrity_report_defined_or_produced": integrity_defined,
           "custody_flag_in_register_synopsis": custody_flag_in_synopsis}
print(json.dumps(results, indent=1))
defective = closed_world and len(integrity_mentions) >= 1 and not integrity_defined
print("VERDICT:", "control is DEFECTIVE: a closed-world contract binds an exit code to a document kind it never defines or produces"
      if defective else "control is SOUND on this test")
sys.exit(0 if defective else 1)
