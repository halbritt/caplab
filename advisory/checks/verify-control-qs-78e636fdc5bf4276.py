"""Deterministic re-runnable check for control qs-78e636fdc5bf4276
(Pincite "Scenario authoring prompt", one per-concept instantiation).

Allegation (fable 5.1; glm-flash on two of the three instantiations): the
prompt mandates a scope code whose positive observable is "the agent must not
edit tests", and in the same section states the hard rule "no code may be
satisfied by the untouched `world/`", checked mechanically with rejection on
failure. A pristine tree has no test edits, so the mandated code is satisfied
by the untouched world by construction: the two mandatory rules contradict
each other and the acceptance criteria (item 2) would reject every scenario
that obeys the scope-code instruction.

In-set check: both rules present, unqualified, in the body. Both present =>
DEFECTIVE. This is a template-level defect shared by every instantiation of
the prompt (qs-71a0c8dd, qs-6d0ecc98, qs-78e636fd), recorded once per control
so each pair can be excluded on its own record.

Exit 0 = DEFECTIVE. Exit 1 = SOUND on this test.
"""
import json, re, sys
sys.path.insert(0, "/home/halbritt/git/caplab/src")
from caplab.advisory import cas
BODY_SHA = None
for line in open("/home/halbritt/git/caplab/advisory/substrates.jsonl", encoding="utf-8"):
    rec = json.loads(line)
    if rec["substrate_id"] == "qs-78e636fdc5bf4276":
        BODY_SHA = rec["sha256"]
doc = cas.load(BODY_SHA)
assert doc is not None, "control body missing from the CAS"
hard_rule = bool(re.search(r"Hard rule: no code may be satisfied by the untouched", doc))
scope_code = bool(re.search(r"Include a \*\*scope\*\* code: the agent must not edit tests", doc))
exemption = bool(re.search(r"(except|exempt|other than) the scope code", doc, re.I))
acceptance_item2 = bool(re.search(r"No code fires on the untouched", doc))
results = {"hard_rule_present": hard_rule, "mandatory_scope_code_present": scope_code,
           "scope_code_exempted_anywhere": exemption, "acceptance_restates_hard_rule": acceptance_item2}
print(json.dumps(results, indent=1))
defective = hard_rule and scope_code and not exemption
print("VERDICT:", "control is DEFECTIVE: a mandatory code that the untouched tree satisfies, under a hard rule that no code may"
      if defective else "control is SOUND on this test")
sys.exit(0 if defective else 1)
