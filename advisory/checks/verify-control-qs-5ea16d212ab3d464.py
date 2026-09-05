"""Deterministic re-runnable check for control qs-5ea16d212ab3d464
("Read — does the Gemini lead survive matched comparison?", 2026-08-16).

Allegations (fable 5.1, gemini 3.8, glm-flash, independently):
 (a) the document says both subjects were measured on the same 13 cases and
     tabulates Gemini's false alarms as 0 / 13, then states "across 22 matched
     control arms, Gemini 3.7 Flash high refused none" while Sonnet is 5 of 13
     — a denominator the document cannot account for inside a matched frame;
 (b) the heading "Case pool: all 11 pending cases resolved" and the sentence
     "None was silently dropped" are contradicted by the same section's
     statement that two cases "stay unresolved pending a third reference or a
     substrate audit".

In-set check: both are properties of the text alone. Either present =>
DEFECTIVE. Exit 0 = DEFECTIVE. Exit 1 = SOUND on this test.
"""
import json, re, sys
sys.path.insert(0, "/home/halbritt/git/caplab/src")
from caplab.advisory import cas
BODY_SHA = None
for line in open("/home/halbritt/git/caplab/advisory/substrates.jsonl", encoding="utf-8"):
    rec = json.loads(line)
    if rec["substrate_id"] == "qs-5ea16d212ab3d464":
        BODY_SHA = rec["sha256"]
doc = cas.load(BODY_SHA)
assert doc is not None, "control body missing from the CAS"
same_13 = bool(re.search(r"same 13 cases", doc))
fa_0_of_13 = bool(re.search(r"0 / 13", doc))
twenty_two = bool(re.search(r"across 22 matched control arms", doc))
heading_resolved = bool(re.search(r"^## Case pool: all 11 pending cases resolved", doc, re.M))
stay_unresolved = bool(re.search(r"stay\s+unresolved\s+pending", doc))
results = {"same_13_cases": same_13, "false_alarms_0_of_13": fa_0_of_13,
           "claims_22_matched_control_arms": twenty_two,
           "denominator_contradiction": same_13 and fa_0_of_13 and twenty_two,
           "heading_all_resolved": heading_resolved, "body_says_two_stay_unresolved": stay_unresolved,
           "resolution_contradiction": heading_resolved and stay_unresolved}
print(json.dumps(results, indent=1))
defective = results["denominator_contradiction"] or results["resolution_contradiction"]
print("VERDICT:", "control is DEFECTIVE: " + ("; ".join(k for k in ("denominator_contradiction", "resolution_contradiction") if results[k]))
      if defective else "control is SOUND on this test")
sys.exit(0 if defective else 1)
