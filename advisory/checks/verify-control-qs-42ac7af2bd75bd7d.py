"""Deterministic re-runnable check for control qs-42ac7af2bd75bd7d
(ADR 0057, "Authorize the rebound-host dual-slot exclusive launch").

Allegation (fable 5.1 and gemini 3.8, independently): the ADR states the host
has 24,564 MiB total GPU memory and that r1's preflight recorded 24,854 MiB
peak allocator demand, then authorizes running r2 after temporarily unloading
the resident 8 GB model. A demand larger than the whole card cannot be met by
freeing part of it; the capacity rationale contradicts its own figures.

In-set check: both figures appear in the body; the demand exceeds the total;
and the decision relies on unloading the resident model to make room. All
three hold => the control is DEFECTIVE (the refusal was correct).

Exit 0 = DEFECTIVE. Exit 1 = SOUND on this test.
"""
import hashlib, re, sys
sys.path.insert(0, "/home/halbritt/git/caplab/src")
from caplab.advisory import cas

SHA = "42ac7af2bd75bd7d"  # substrate id suffix; the body is the CAS entry below
BODY_SHA = None
import json
for line in open("/home/halbritt/git/caplab/advisory/substrates.jsonl", encoding="utf-8"):
    rec = json.loads(line)
    if rec["substrate_id"] == "qs-42ac7af2bd75bd7d":
        BODY_SHA = rec["sha256"]
doc = cas.load(BODY_SHA)
assert doc is not None, "control body missing from the CAS"

def mib(label_regex):
    m = re.search(label_regex, doc)
    return int(m.group(1).replace(",", "")) if m else None

total = mib(r"([\d,]+) MiB total memory")
demand = mib(r"([\d,]+) MiB peak allocator demand")
unload = bool(re.search(r"temporarily unload", doc))
results = {"total_mib": total, "peak_demand_mib": demand,
           "demand_exceeds_total": (total is not None and demand is not None and demand > total),
           "decision_relies_on_unloading_resident_model": unload}
print(json.dumps(results, indent=1))
defective = results["demand_exceeds_total"] and unload
print("VERDICT:", "control is DEFECTIVE: the authorized remedy (unload an 8 GB resident model) "
      "cannot satisfy a demand that exceeds the card's total memory" if defective
      else "control is SOUND on this test")
sys.exit(0 if defective else 1)
