"""Deterministic re-runnable check for control qs-7438efc689422484
(fleet-catalog-resolution @2 proposal).

Allegations (deepseek v4 flash + pro): (1) flash — the cited
docs/reference/deferrals.md does not exist in the repository, nor does the
capture path or the prior-lineage identities; (2) pro — the file exists but
carries no deferral named "Fleet overlay auto-resolution"; (3) pro — the
proposal's premise is stale: registration-derived overlay resolution is
already delivered in the repository, so the to-be-delivered target state
already holds.

In-set adjudication: every allegation resolves against the base repository
tree (deferrals.md content, driver code, graph identities) — OUT-OF-CONTRACT
by the audit standard; recorded, never scored. (Flash and pro even contradict
each other on whether deferrals.md exists, which itself shows the fact is
out-of-set.) What IS in-set checkable: the proposal's internal consistency —
its element anchors all resolve, the subject/predicate-version claims are
restated consistently between header, motivation, and capture context, the
non-goals do not contradict the target state, and the deferral it cites is
named identically at both citation sites.

Exit 0 = control is DEFECTIVE (in-set inconsistency found).
Exit 1 = SOUND on the in-set test; out-of-contract residue recorded.
"""
import hashlib, json, re, sys

PATH = ("/home/halbritt/.local/share/striatum/exchange/"
        "019f22ef-0cb4-780f-9b82-b210bab24325/dispatch/"
        "05bad9afcab5496e3edc36ffc481b583296038a0d187fec68ce622f735cc82c5/"
        "inputs/00-striatum-next-passes-fleet-catalog-resolution-v2-proposal")
SHA = "7438efc689422484ea2dda0177a8e0202cdcff60307a932a1f2a1eed7919e71d"

raw = open(PATH, "rb").read()
assert hashlib.sha256(raw).hexdigest() == SHA, "substrate body hash mismatch"
doc = raw.decode("utf-8")
results = {}

# In-set element anchors all present.
anchors = set(re.findall(r"\{#(el:[a-z-]+)\}", doc))
results["anchors"] = sorted(anchors)
results["expected_anchors_present"] = {
    "el:proposal", "el:problem", "el:motivation", "el:target-state",
    "el:candidate-direction", "el:non-goals", "el:constraints",
    "el:context"} <= anchors

# Subject and predicate version consistent across header and motivation.
results["header_declares_v2"] = bool(re.search(
    r"subject: `fleet-catalog-resolution` \(predicate version 2", doc))
results["motivation_restates_v2_accepted"] = (
    "carries `fleet-catalog-resolution` at predicate version 2" in doc)

# The deferral is cited by one name at both sites (problem + capture context).
cites = re.findall(r"[\"“]Fleet overlay auto-resolution[\"”]", doc)
results["deferral_name_citation_count"] = len(cites)
results["deferral_cited_consistently"] = len(cites) == 2
results["deferral_path_cited"] = doc.count("docs/reference/deferrals.md") == 2

# The proposal consistently frames the capability as NOT yet delivered
# (problem: flag must be hand-passed) and never also claims it delivered —
# the in-set half of pro allegation (3).
results["premise_flag_required_today"] = (
    "must hand-pass `-catalog-overlay" in doc)
results["no_inset_claim_already_delivered"] = not re.search(
    r"(already|now) (derives|resolves) the overlay from (the |its )?registration",
    doc)

results["out_of_contract"] = [
    "existence/content of docs/reference/deferrals.md lives in the base tree, "
    "outside the set (flash says absent, pro says present-but-unnamed — "
    "mutually contradictory allegations about an out-of-set file)",
    "whether registration-derived overlay resolution is already delivered "
    "lives in driver code and the registry, outside the set",
    "capture path and prior-lineage identities resolve against the graph "
    "store, outside the set",
]

defective = not all([
    results["expected_anchors_present"],
    results["header_declares_v2"],
    results["motivation_restates_v2_accepted"],
    results["deferral_cited_consistently"],
    results["premise_flag_required_today"],
    results["no_inset_claim_already_delivered"]])
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND (in-set); allegations out-of-contract")
sys.exit(0 if defective else 1)
