"""Deterministic re-runnable check for control qs-425bccdb287d3654
(backends-own-their-config-b p1-adapter-config-contract-and-metadata change set).

Allegations (deepseek v4 flash + pro): (1) README/schema assert dispatch-time
behavior (Lane Supervisor env injection; absent config dir fails dispatch
closed) the delivered code does not provide; (2) glm/backend.yaml scheduler_hints
rank=1 "while Claude is disabled for spend exhaustion" contradicts its own
status: disabled ("Review routes to codex (rank=2) meanwhile") and contradicts
claude-code/backend.yaml status: accepted ("the monthly spend-limit trip has
reset"), all dated 2026-07-09; (3) claude-harm/backend.yaml contradicts itself
on the same date: status says the .claude-harm account "probes healthy again;
spend-limit trip reset" while scheduler_hints say it "is now the spend-limited
one".

In-set adjudication:
  - Allegation (1) is NOT sustained: the set discloses in three places that
    dispatch injection is a later packet ("this pass's later packets";
    "until dispatch injection (p4) makes the declared entry live"; "until
    dispatch injection (p4) lands") — the ruled qs-d79e9a1668416a7d
    library-then-wiring standard applies; whether p4 delivers is out-of-set.
  - Allegations (2) and (3) ARE in-set contradictions: same-date, present-tense
    statements about the same facts (is the claude account spend-limited?
    is glm the preferred live review lane?) that cannot simultaneously hold,
    inside one change set (internal-consistency prong of the review contract).

Exit 0 = control is DEFECTIVE (the contradictory statement pairs are present).
Exit 1 = sound (pairs absent).
"""
import hashlib, json, re, sys

PATH = ("/home/halbritt/.local/share/striatum/exchange/"
        "019f22ef-0cb4-780f-9b82-b210bab24325/dispatch/"
        "3952b19c64f017f0ec821e7c31e7e3936819cdb5fc77b77b82d31f142bb37473/"
        "inputs/00-striatum-next-passes-backends-own-their-config-b-packets-"
        "p1-adapter-config-contract-and-metadata-change-set")
SHA = "425bccdb287d365434c476e2b6eb61c4d0170b7241e56e0ccbecef4ac0bac48c"

raw = open(PATH, "rb").read()
assert hashlib.sha256(raw).hexdigest() == SHA, "substrate body hash mismatch"
files = json.loads(raw)["files"]
results = {"files_in_set": sorted(files)}

harm = files["backends/claude-harm/backend.yaml"]
glm = files["backends/glm/backend.yaml"]
cc = files["backends/claude-code/backend.yaml"]
readme = files["backends/README.md"]

# --- Contradiction A (single file, claude-harm, both blocks dated 2026-07-09):
# status: healthy / spend-limit trip reset  vs  hints: now the spend-limited one.
status_block = harm[harm.index("status:"):harm.index("agent_runtimes:")]
hints_block = harm[harm.index("scheduler_hints:"):]
results["harm_status_says_healthy_reset"] = bool(
    re.search(r"probes healthy again", status_block)
    and re.search(r"spend-limit trip reset", status_block)
    and re.search(r"^status: accepted", status_block))
results["harm_status_dated_2026_07_09"] = "2026-07-09" in status_block
results["harm_hints_say_now_spend_limited"] = bool(
    re.search(r"is now the spend-limited one", hints_block))
results["harm_hints_dated_2026_07_09"] = "2026-07-09" in hints_block
contradiction_a = all([
    results["harm_status_says_healthy_reset"],
    results["harm_status_dated_2026_07_09"],
    results["harm_hints_say_now_spend_limited"],
    results["harm_hints_dated_2026_07_09"]])

# --- Contradiction B (cross-file + glm-internal, all dated 2026-07-09):
# glm hints assert Claude is disabled for spend exhaustion and glm rank=1 is
# the preferred review lane; claude-code status (accepted) asserts the trip
# reset; glm's own status is disabled with review routed to codex meanwhile.
glm_hints = glm[glm.index("scheduler_hints:"):glm.index("# v5 (2026-07-08)")]
results["glm_hints_claude_disabled_for_spend"] = bool(
    re.search(r"while Claude is disabled for spend exhaustion", glm_hints))
results["glm_hints_preferred_review_lane"] = bool(
    re.search(r"preferred independent review replacement lane", glm_hints))
results["glm_hints_dated_2026_07_09"] = "2026-07-09" in glm_hints
results["glm_status_disabled_reviews_to_codex"] = bool(
    re.search(r"^status: disabled", glm, re.M)
    and re.search(r"Review routes to codex \(rank=2, frontier\)\s*\n\s*# meanwhile", glm))
cc_status = cc[cc.index("status:"):cc.index("agent_runtimes:")]
results["cc_status_accepted_trip_reset"] = bool(
    re.search(r"^status: accepted", cc_status)
    and re.search(r"monthly spend-limit\s*\n\s*# trip has reset", cc_status))
results["cc_status_dated_2026_07_09"] = "2026-07-09" in cc_status
contradiction_b = all([
    results["glm_hints_claude_disabled_for_spend"],
    results["glm_hints_preferred_review_lane"],
    results["glm_hints_dated_2026_07_09"],
    results["glm_status_disabled_reviews_to_codex"],
    results["cc_status_accepted_trip_reset"],
    results["cc_status_dated_2026_07_09"]])

# --- Allegation (1), NOT scored as defect: the set discloses wiring is later.
results["readme_discloses_later_packets"] = (
    "this pass's later packets" in readme)
def uncomment(y):  # join yaml comment-wrapped prose for phrase matching
    return re.sub(r"\s*\n\s*#\s*", " ", y)
results["yaml_discloses_p4_injection_pending"] = (
    "until dispatch injection (p4) makes the declared entry live" in uncomment(cc)
    and "until dispatch injection (p4) lands" in uncomment(harm))
results["out_of_contract"] = [
    "whether the Lane Supervisor / p4 actually delivers injection lives in "
    "later packets and internal/backend/supervise, outside the set",
    "claude-code's 'after glm/kimi were disabled' is past-tense history; "
    "kimi's accepted status now does not falsify it in-set",
]

defective = contradiction_a or contradiction_b
results["contradiction_a_claude_harm_same_file_same_date"] = contradiction_a
results["contradiction_b_glm_vs_claude_code_same_date"] = contradiction_b
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND (in-set)")
sys.exit(0 if defective else 1)
