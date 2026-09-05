"""Deterministic re-runnable check for control qs-922bffcd10232e91
(D0013 — Adapter Supervision decision record).

Allegations (fable 5.1 and glm-flash, independently): (a) the decision
record's own H1 anchor is `{#el:rfc-0013-design-adapter-supervision}`, and the
identical anchor appears verbatim inside the "Owning RFC" link text that points
at the RFC 0013 *design* document — one element id names two documents and the
attribute syntax leaks into rendered link text; (b) the "Decided" field carries
no date or context but a generation instruction ("generate and accept the
decision record for RFC 0013 from its accepted stages: ...").

In-set check: both are properties of the text. Either present => DEFECTIVE.
Exit 0 = DEFECTIVE. Exit 1 = SOUND on this test.
"""
import json, re, sys
sys.path.insert(0, "/home/halbritt/git/caplab/src")
from caplab.advisory import cas
BODY_SHA = None
for line in open("/home/halbritt/git/caplab/advisory/substrates.jsonl", encoding="utf-8"):
    rec = json.loads(line)
    if rec["substrate_id"] == "qs-922bffcd10232e91":
        BODY_SHA = rec["sha256"]
doc = cas.load(BODY_SHA)
assert doc is not None, "control body missing from the CAS"
h1 = re.search(r"^# .*\{#el:([a-z0-9-]+)\}", doc, re.M)
h1_anchor = h1.group(1) if h1 else None
link = re.search(r"\*\*Owning RFC:\*\* \[[^\]]*\{#el:([a-z0-9-]+)\}\]\(([^)]+)\)", doc)
link_anchor, link_target = (link.group(1), link.group(2)) if link else (None, None)
decided = re.search(r"\*\*Decided:\*\* (.*)", doc)
decided_text = decided.group(1).strip() if decided else ""
results = {"h1_anchor": h1_anchor, "owning_rfc_link_text_anchor": link_anchor, "owning_rfc_link_target": link_target,
           "anchor_collision_and_leaked_syntax": bool(h1_anchor and link_anchor and h1_anchor == link_anchor),
           "decided_field": decided_text[:120],
           "decided_is_generation_instruction": decided_text.lower().startswith("generate and accept")}
print(json.dumps(results, indent=1))
defective = results["anchor_collision_and_leaked_syntax"] or results["decided_is_generation_instruction"]
print("VERDICT:", "control is DEFECTIVE: " + "; ".join(k for k in ("anchor_collision_and_leaked_syntax", "decided_is_generation_instruction") if results[k])
      if defective else "control is SOUND on this test")
sys.exit(0 if defective else 1)
