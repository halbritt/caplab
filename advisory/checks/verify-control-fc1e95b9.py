"""Deterministic re-runnable check for dispatch b755eb26... (substrate
qs-fc1e95b9755ee36e): the change set's own internal/driver/verify.go claims a
flake-specific "plan nothing" path in classifyDualSignalNonProgress, while its
own candidacy code makes that path unreachable through planDualSignal.

Exit 0 = control is DEFECTIVE (allegation substantiated in-set).
Exit 1 = control is SOUND (allegation not substantiated by in-set text).

Chain the allegation names, every link quoted from the in-set file:
  1. qualifySignalCandidate returns (_, false, nil) when reportOverFlakeBar(...)
     -> a flaked report is never a candidate;
  2. signalStates appends the ordinal to `missing` when no version qualifies;
  3. dualSignalSatisfied is false iff missing non-empty OR no independent
     assignment -- there is no separate flake test after independence, so
     "independent assignment exists yet unsatisfied" cannot occur;
  4. planDualSignal reaches classifyDualSignalNonProgress only when unsatisfied,
     with the same (qualified, missing) accounting;
  5. classifyDualSignalNonProgress tests len(missing) > 0 FIRST and redispatches
     those ordinals as head-moved / fresh-signal; the `independentSignalAssignment
     ... ok` branch (the claimed flake path) is only reached with missing empty,
     which via planDualSignal implies the assignment is NOT independent.
  The only test of the flake path feeds synthetic `qualified` with missing=nil
  directly into classifyDualSignalNonProgress; no test drives a flake through
  planDualSignal.
"""
import json, os, re, sys
exchange = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
DISPATCH = "b755eb26e98d8187"
full = [x for x in os.listdir(os.path.join(exchange, "dispatch"))
        if x.startswith(DISPATCH)][0]
bundle = os.path.join(exchange, "dispatch", full)
man = json.load(open(os.path.join(bundle, "manifest.json")))
files = json.loads(open(os.path.join(bundle, man["inputs"][0]["path"]),
                        errors="replace").read())["files"]
src = files["internal/driver/verify.go"]
test = files["internal/driver/verify_test.go"]
results = {}


def func_body(code, name):
    """Return the body text of top-level Go func `name` (brace-balanced)."""
    m = re.search(r"\nfunc (?:\([^)]*\) )?" + re.escape(name) + r"\(", code)
    if not m:
        return None
    i = code.index("{", m.end())
    depth, j = 0, i
    while j < len(code):
        if code[j] == "{":
            depth += 1
        elif code[j] == "}":
            depth -= 1
            if depth == 0:
                return code[i:j + 1]
        j += 1
    return None


qualify = func_body(src, "qualifySignalCandidate")
states = func_body(src, "signalStates")
satisfied = func_body(src, "dualSignalSatisfied")
plan = func_body(src, "planDualSignal")
classify = func_body(src, "classifyDualSignalNonProgress")
results["all_functions_present"] = all(
    b is not None for b in (qualify, states, satisfied, plan, classify))

# 1. The flake bar is applied at candidacy: a flaked report is not a candidate.
results["qualify_excludes_over_flake_bar"] = bool(re.search(
    r"reportOverFlakeBar\(state, report, head\.ContentHash\)\s*\{\s*\n\s*return qualifiedSignal\{\}, false, nil",
    qualify or ""))
# 2. A signal with no qualifying candidate is marked missing.
results["signalStates_marks_unqualified_missing"] = bool(re.search(
    r"if !signalQualified \{\s*\n\s*missing = append\(missing, signal\)", states or ""))
# 3. dualSignalSatisfied has no flake test beyond candidacy: its only two
#    unsatisfied branches are missing non-empty and no independent assignment.
results["satisfied_checks_only_missing_and_independence"] = (
    "len(missing) > 0" in (satisfied or "")
    and "independentSignalAssignment(qualified)" in (satisfied or "")
    and not re.search(r"[Ff]lake", satisfied or ""))
# 4. planDualSignal returns early when satisfied and otherwise classifies from
#    the same signalStates accounting.
results["plan_returns_when_satisfied"] = bool(re.search(
    r"satisfied, _, err := s\.dualSignalSatisfied\(state, identity, head\)\s*\n\s*if err != nil \|\| satisfied \{\s*\n\s*return err == nil",
    plan or ""))
results["plan_classifies_from_signalStates"] = (
    "qualified, missing, err := s.signalStates(state, identity, head)" in (plan or "")
    and "s.classifyDualSignalNonProgress(state, identity, head, qualified, missing)" in (plan or ""))
# 5. classify: missing branch first (redispatch as head-moved/fresh-signal),
#    flake "plan nothing" branch only after, gated on an independent assignment.
cb = classify or ""
i_missing = cb.find("if len(missing) > 0 {")
i_indep = cb.find("if _, ok := independentSignalAssignment(qualified); ok {")
results["classify_missing_branch_precedes_flake_branch"] = (
    0 <= i_missing < i_indep)
results["classify_missing_branch_redispatches_missing"] = bool(re.search(
    r"classes\[signal\] = nonProgressHeadMoved\s*\n\s*\} else \{\s*\n\s*classes\[signal\] = nonProgressFreshSignal[\s\S]*?return append\(\[\]int\(nil\), missing\.\.\.\), classes, nil",
    cb))
results["classify_flake_branch_plans_nothing"] = bool(re.search(
    r"independentSignalAssignment\(qualified\); ok \{[\s\S]*?return nil, classes, nil", cb))
# The claim itself: both the function doc and the in-branch comment say the
# over-bar flake case "plans nothing here" / is owned by "the flake path".
results["claim_flake_path_plans_nothing"] = (
    "(an over-bar flake withholding satisfaction, §5.6) plans nothing here" in src
    and "Re-dispatching verification cannot clear\n\t\t// a flake, so plan no signal — the flake path owns the next move." in src)
# The contradicting in-set statement: reportOverFlakeBar's own doc says the
# flaked signal "stays missing and re-dispatchable".
results["reportOverFlakeBar_doc_says_missing_and_redispatchable"] = (
    "the signal stays\n// missing and re-dispatchable" in src)
# signalHeadMoved does not consult the flake bar, so a flaked report attesting
# the current head classifies as fresh-signal (not even head-moved).
moved = func_body(src, "signalHeadMoved") or ""
results["signalHeadMoved_ignores_flakes"] = not re.search(r"[Ff]lake", moved)
# Tests: the only exercise of the flake branch injects synthetic `qualified`
# with missing=nil straight into classifyDualSignalNonProgress; no test sets a
# flake and drives planDualSignal.
results["flake_branch_test_bypasses_planDualSignal"] = bool(re.search(
    r"func TestClassifyDualSignalNonProgressIndependentPairPlansNothing[\s\S]*?qualified := \[\]qualifiedSignal\{[\s\S]*?classifyDualSignalNonProgress\(f\.state, f\.subject, f\.head, qualified, nil\)",
    test))
test_funcs = re.split(r"\nfunc ", test)
results["no_test_drives_flake_through_planDualSignal"] = not any(
    "Flakes[" in f and "planDualSignal(" in f for f in test_funcs)

chain = [
    "all_functions_present",
    "qualify_excludes_over_flake_bar",
    "signalStates_marks_unqualified_missing",
    "satisfied_checks_only_missing_and_independence",
    "plan_returns_when_satisfied",
    "plan_classifies_from_signalStates",
    "classify_missing_branch_precedes_flake_branch",
    "classify_missing_branch_redispatches_missing",
    "classify_flake_branch_plans_nothing",
    "claim_flake_path_plans_nothing",
]
defective = all(results[k] for k in chain)
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND",
      "- flake no-redispatch branch in classifyDualSignalNonProgress is"
      " unreachable via planDualSignal; flaked ordinals are redispatched"
      if defective else "- allegation not substantiated by in-set text")
sys.exit(0 if defective else 1)
