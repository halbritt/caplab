"""Deterministic re-runnable check for dispatch 3e2fbb059771ee2f... (substrate
qs-d98bbffcdcd43f21, packet P17-admit-closure-observation).

Allegation (codex-sol-high): context.json#note admits request_ref/run_ref are
unobserved build-time placeholders from an execution-free lane, while
admission-decision.json and journal.json assert a fresh, exact durable Store
result with concrete sequence_ref/admission_ref values.

Exit 0 = control is DEFECTIVE (the contradiction is present in the set's own
text); exit 1 = SOUND.
"""
import json, os, re, sys
exchange = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
DISPATCH = "3e2fbb059771ee2f"
full = [x for x in os.listdir(os.path.join(exchange, "dispatch"))
        if x.startswith(DISPATCH)][0]
bundle = os.path.join(exchange, "dispatch", full)
man = json.load(open(os.path.join(bundle, "manifest.json")))
files = json.loads(open(os.path.join(bundle, man["inputs"][0]["path"]),
                        errors="replace").read())["files"]
results = {}
D = "ledger/RQ-57950/admissions/0003-closure-observation/"
ctx = json.loads(files[D + "context.json"])
dec = json.loads(files[D + "admission-decision.json"])
jnl = json.loads(files[D + "journal.json"])

# Side A: context.json admits the lane is execution-free and cannot observe
# Store-reserved sequencing; request_ref/run_ref are placeholders.
note = ctx["note"]
results["ctx_admits_placeholders"] = bool(re.search(
    r"request_ref and run_ref[^.]*build-time placeholders", note))
results["ctx_admits_execution_free_lane"] = (
    "execution-free build lane cannot observe" in note)
results["ctx_cites_store_reserves_admit_sequencing"] = bool(re.search(
    r"reserves OpenRun/Admit sequencing to the Store", note))
results["ctx_run_ref_values"] = {
    "lawful_context": ctx["lawful_context"]["run_ref"],
    "producing_context": ctx["producing_context"]["run_ref"]}

# Side B: decision + journal assert an executed, fresh, exact durable cut with
# concrete Admit-sequence numbers.
cut = dec["recovery"]["cut"]
results["decision_recovery_outcome"] = dec["recovery"]["outcome"]
results["decision_cut_state"] = cut["state"]
results["decision_cut_sequence_ref"] = cut["sequence_ref"]
results["decision_admission_ref"] = dec["admitted_evidence"]["admission_ref"]
results["decision_says_admission_ref_is_cut_sequence_ref"] = (
    "admission_ref is the committing durable cut's sequence_ref" in dec["note"])
results["decision_distinguishes_real_driver_run"] = (
    "a real Driver-owned run replays this identical seam" in dec["note"])
results["journal_recovery_outcome"] = jnl["recovery_outcome"]
results["journal_claims_reconcile_appended"] = bool(re.search(
    r"The exact durable-cut journal .*reconcile\.Reconcile appended",
    jnl["note"]))
results["journal_cut_sequence_refs"] = [c["sequence_ref"] for c in jnl["cuts"]]
results["journal_result_cut_is_concrete"] = any(
    c["state"] == "result" and isinstance(c["sequence_ref"], int)
    for c in jnl["cuts"])
# No in-set text marks the cut/admission sequence numbers as placeholders.
all_text = "\n".join(files.values())
results["any_text_marks_cut_sequence_as_placeholder"] = bool(re.search(
    r"(sequence_ref|admission_ref)[^.]{0,120}placeholder", all_text))

defective = (
    results["ctx_admits_placeholders"]
    and results["ctx_admits_execution_free_lane"]
    and results["ctx_cites_store_reserves_admit_sequencing"]
    and results["decision_recovery_outcome"] == "fresh"
    and results["decision_cut_state"] == "result"
    and isinstance(results["decision_admission_ref"], int)
    and results["decision_says_admission_ref_is_cut_sequence_ref"]
    and results["journal_claims_reconcile_appended"]
    and results["journal_recovery_outcome"] == "fresh"
    and results["journal_result_cut_is_concrete"]
    and not results["any_text_marks_cut_sequence_as_placeholder"])
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND")
sys.exit(0 if defective else 1)
