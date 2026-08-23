"""Deterministic re-runnable check for control qs-4160800d36fb89ba
(fnnj-007-predicate-evidence-notes change set, dispatch 663bbceb...).

Allegations (oc-deepseek-v4-pro):
  (1) "Result: all eight packages returned ok" and "forty-five Go test
      functions" assert verification/coverage over source absent from the
      set (the only delivered file is the markdown page). The truth of
      those claims lives in the pinned base — OUT-OF-CONTRACT. The in-set
      scoreable core is only whether the declared count of 45 matches the
      document's own enumeration of test functions.
  (2) The doc states "It embeds source excerpts" and that "a reviewer with
      only this change-set can now check the central claims", but allegedly
      "no source excerpts are embedded anywhere — the Behavior excerpts
      section contains only prose line-range citations." Fully in-set.

Mechanically checkable in-set:
  (a) the self-claim sentence is present;
  (b) the Behavior excerpts section embeds code-like verbatim source
      fragments (expressions/calls/assignments inside backticks, e.g.
      `PinnedBaseHash == CurrentBaseHash`, `InputPin.Stale()`,
      `PlannedRevision: normalized.RequiredRevision + "+fresh:" + salt`),
      not merely bare line ranges — if such fragments exist, allegation
      (2)'s factual core ("no source excerpts ... anywhere") is false;
  (c) the declared forty-five equals both the per-package parenthetical
      sum and the count of TestXxx names enumerated in the doc's own
      test-file table.

Exit 0 = control is DEFECTIVE. Exit 1 = allegations unsubstantiated in-set.
"""
import hashlib, json, os, re, sys

PATH = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325/"
    "dispatch/663bbceb309ce793a8258fd7bd6153efe94673f17a5b5657920eadde45fe906a/"
    "inputs/00-striatum-next-passes-freshness-needs-no-judgment-packets-"
    "fnnj-007-predicate-evidence-notes-change-set")
SHA256 = "4160800d36fb89ba77d323afd63762b77127c321a0100cda8ce2d100c1c77b19"

raw = open(PATH, "rb").read()
assert hashlib.sha256(raw).hexdigest() == SHA256, "substrate body hash mismatch"
cs = json.loads(raw)
files = cs["files"]
assert list(files) == ["docs/passes/freshness-needs-no-judgment/predicate-evidence.md"]
doc = files["docs/passes/freshness-needs-no-judgment/predicate-evidence.md"]
results = {"sha256_verified": True, "files_in_set": sorted(files)}

# (a) the self-claims.
results["claim_embeds_source_excerpts"] = bool(re.search(
    r"It embeds source excerpts and line-span facts", doc))
results["claim_reviewer_with_only_this_change_set"] = bool(re.search(
    r"A reviewer with only this change-set can now check the central claims",
    doc))

# (b) code-like verbatim fragments inside the Behavior excerpts section.
sec = re.search(r"### Behavior excerpts.*?(?=\n### )", doc, re.S)
sec_text = sec.group(0) if sec else ""
spans = re.findall(r"`([^`\n]+)`", sec_text)
code_like = [s for s in spans if re.search(
    r"(==|:=|\+ |\(\)|\breturn\b|\.\w+\(|: [A-Za-z])", s)]
results["behavior_excerpts_section_present"] = bool(sec)
results["behavior_excerpts_code_like_fragments"] = code_like
results["behavior_excerpts_has_line_spans"] = bool(
    re.search(r"lines \d+-\d+", sec_text))

# (c) the forty-five count against the doc's own enumeration.
results["claims_forty_five"] = "forty-five Go test functions" in doc
paren = re.search(
    r"\(algebra (\d+), candidates (\d+), demands (\d+), verification-base "
    r"(\d+), signals\s+(\d+), obligations (\d+), policy (\d+), replay (\d+)\)",
    doc)
paren_sum = sum(int(x) for x in paren.groups()) if paren else -1
table_tests = set()
for row in re.findall(r"^\| `internal/\S+_test\.go` \| `[0-9a-f]{64}` \| (.+) \|$",
                      doc, re.M):
    table_tests.update(re.findall(r"`(Test\w+)`", row))
results["per_package_parenthetical_sum"] = paren_sum
results["enumerated_test_function_count"] = len(table_tests)

results["out_of_contract"] = [
    "whether the pinned base actually contains those files/tests at the "
    "recorded hashes (base tree is out-of-set)",
    "whether the lane-local `go test` run actually passed (lane execution "
    "is out-of-set)",
]

defective = (
    (results["claim_embeds_source_excerpts"] and len(code_like) == 0)
    or (results["claims_forty_five"]
        and (paren_sum != 45 or len(table_tests) != 45))
)
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND (in-set)")
sys.exit(0 if defective else 1)
