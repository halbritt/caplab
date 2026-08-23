"""Deterministic re-runnable check for dispatch f42f9365... (substrate
qs-641d18fb33495aba, work-graph-assembly-b / lowering-context-pin packet).

Reviewer allegations, checked against the change set's OWN files:

  A. "Production dispatch (dispatchPlannedStep, expected != nil) makes
     dispatchStepResolved call openPlannedRun and return BEFORE the new
     lowering_context field is added to openPayload; the delivered files do not
     modify that opening path."  -> Checked structurally in session.go: the
     `if expected != nil { ... openPlannedRun ... }` block precedes the
     `openPayload["lowering_context"]` line, every branch of that block returns,
     openPlannedRun is not defined in any delivered file, and the in-set comment
     says dispatchStep (expected == nil) is "retained for focused package tests".
     Claim side in-set: environment.go says the context "is recorded verbatim
     into plan and run provenance (the plan_record and its dispatched
     pass_run_opened)".
  B. "Plan dedupe compares a content hash that excludes lowering_context and
     never compares the recorded context."  -> Checked: planContent hashes only
     unmet + planned_runs; planRecordIsRedundant never references the context;
     PlanState.LoweringContext is folded (fold.go) but never read in session.go.
     Claim side in-set: "so a later reader can prove which lowering rules
     governed a plan without re-reading the catalog".

Exit 0 = control is DEFECTIVE (at least one allegation substantiated in-set).
Exit 1 = control is SOUND.
"""
import json, os, re, sys

exchange = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
DISPATCH = "f42f936578bd0c86"
full = [x for x in os.listdir(os.path.join(exchange, "dispatch"))
        if x.startswith(DISPATCH)][0]
bundle = os.path.join(exchange, "dispatch", full)
man = json.load(open(os.path.join(bundle, "manifest.json")))
files = json.loads(open(os.path.join(bundle, man["inputs"][0]["path"]),
                        errors="replace").read())["files"]
session = files["internal/driver/session.go"]
env = files["internal/driver/environment.go"]
fold = files["internal/driver/fold.go"]
results = {}

def func_body(src, signature_re):
    """Text of a top-level Go func from its signature to the next top-level '}'."""
    m = re.search(signature_re, src)
    if not m:
        return ""
    end = src.find("\n}\n", m.start())
    return src[m.start():end + 3]

# --- Allegation A --------------------------------------------------------
env_flat = re.sub(r"\s*\n//\s*", " ", env)  # join wrapped comment lines
results["claim_run_provenance_carries_context_env"] = (
    "recorded verbatim into plan and run provenance (the plan_record and its "
    "dispatched pass_run_opened)" in env_flat)
results["claim_run_provenance_carries_context_session"] = (
    "Run provenance carries the same declared lowering-rule-set context" in session)
results["production_dispatch_uses_dispatchPlannedStep"] = (
    "s.dispatchPlannedStep(state, request, &plan.PlannedRuns[i], report)" in
    func_body(session, r"func \(s \*Session\) dispatch\(report \*Report\)"))
results["dispatchPlannedStep_passes_planned_as_expected"] = (
    "return s.dispatchStepResolved(state, request, planned.Step, report, nil, planned)"
    in session)
results["dispatchStep_is_test_only_per_comment"] = (
    "dispatchStep is retained for focused package tests. Production dispatch uses\n"
    "// dispatchPlannedStep" in session)

dsr = func_body(session, r"func \(s \*Session\) dispatchStepResolved\(")
open_block = re.search(
    r"(?s)\n\tif expected != nil \{\n\t\tplan := state\.Plans\[request\.Seq\]\n"
    r"\t\topened, reused, err := s\.openPlannedRun\(.*?\n\t\}\n", dsr)
ctx_line = dsr.find('openPayload["lowering_context"] = context')
results["openPlannedRun_block_found"] = open_block is not None
results["lowering_context_added_to_openPayload"] = ctx_line >= 0
if open_block:
    blk = open_block.group(0)
    results["openPlannedRun_block_precedes_lowering_context_line"] = open_block.end() <= ctx_line
    # every branch of the block ends in a return: count `return` vs `if`/`}` tail
    tail = blk.rstrip().rsplit("\n", 2)
    results["openPlannedRun_block_ends_with_return"] = tail[-2].strip() == "return 1, nil"
    results["openPlannedRun_block_mentions_lowering"] = "lowering" in blk
    # the only non-returning path inside would be an `if` without a return;
    # check each `if ... {` inside has a `return` before its closing brace.
    inner = blk[blk.find("openPlannedRun"):]
    ifs = re.findall(r"(?s)\n\t\t\tif [^\n]*\{\n(.*?)\n\t\t\t\}", inner)
    results["every_inner_branch_returns"] = all("return " in b for b in ifs)
results["openPlannedRun_defined_in_set"] = any(
    re.search(r"func \(s \*Session\) openPlannedRun\(", c) for c in files.values())
results["dead_expected_branch_after_return"] = (
    'if expected != nil {\n\t\topenPayload["plan_step_hash"] = expected.PlanStepHash' in dsr
    and dsr.find('openPayload["plan_step_hash"]') > (open_block.end() if open_block else -1))
results["fold_reads_run_lowering_context"] = (
    'run.LoweringContext = loweringRuleContextFromValue(payload["lowering_context"])' in fold)

allegation_a = (results["claim_run_provenance_carries_context_env"]
                and results["production_dispatch_uses_dispatchPlannedStep"]
                and results["dispatchPlannedStep_passes_planned_as_expected"]
                and results["openPlannedRun_block_found"]
                and results["openPlannedRun_block_precedes_lowering_context_line"]
                and results["openPlannedRun_block_ends_with_return"]
                and results["every_inner_branch_returns"]
                and not results["openPlannedRun_block_mentions_lowering"]
                and not results["openPlannedRun_defined_in_set"])
results["allegation_A_substantiated"] = allegation_a

# --- Allegation B --------------------------------------------------------
pc = func_body(session, r"func planContent\(")
pri = func_body(session, r"func planRecordIsRedundant\(")
results["claim_reader_can_prove_which_rules_governed_plan"] = (
    "a later reader can prove which lowering rules governed a plan" in env_flat)
results["planContent_hashes_only_unmet_and_planned_runs"] = (
    '"unmet":' in pc and '"planned_runs":' in pc and "lowering" not in pc.lower())
results["planRecordIsRedundant_ignores_lowering_context"] = (
    bool(pri) and "lowering" not in pri.lower())
results["planRecordIsRedundant_gates_plan_record_write"] = (
    "if planRecordIsRedundant(state, state.Plans[request.Seq], hash) {\n\t\t\tcontinue" in session)
results["PlanState_has_LoweringContext_field"] = (
    'plan.LoweringContext = loweringRuleContextFromValue(payload["lowering_context"])' in fold)
results["session_never_reads_LoweringContext"] = ".LoweringContext" not in session
results["hash_exclusion_is_documented_design"] = (
    "never folded into the plan content hash" in session)
allegation_b = (results["claim_reader_can_prove_which_rules_governed_plan"]
                and results["planContent_hashes_only_unmet_and_planned_runs"]
                and results["planRecordIsRedundant_ignores_lowering_context"]
                and results["planRecordIsRedundant_gates_plan_record_write"]
                and results["PlanState_has_LoweringContext_field"]
                and results["session_never_reads_LoweringContext"])
results["allegation_B_substantiated"] = allegation_b

defective = allegation_a or allegation_b
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND")
sys.exit(0 if defective else 1)
