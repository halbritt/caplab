"""Deterministic re-runnable check for control qs-a17d0d0b23b2ad0f
(capability-aware-placement-f implementation plan, dispatch 726b14eb...).

Allegations (oc-deepseek-v4-pro):
  (1) W14 criterion 9 says of "the four states of W22.3" that "the last
      produces a reason list of exactly [not_available]", while W22.3
      enumerates the four degraded read states with Absence FIRST and
      assigns [not_available] to "the first"; the revision record even
      fixes [not_available] as "the first member of the closed ordered
      set" (C27(b)) and claims W22.3 and W14.9 "are restated to agree".
  (2) The revision-delta "Edited" row and the work-graph RPL-008 delta
      paragraph both name SIX rewritten purposes (p14, p15, p18, p20,
      p21, p22), while "Nothing sound was disturbed" says "the five
      edited purposes" (and the work-graph intro speaks of "seven other
      purposes").

Both are wholly in-set: every cited statement lives in this one document.
The document's own claim of agreement between W14.9 and W22.3 makes (1) a
claims-versus-content defect on any reading.

Exit 0 = control is DEFECTIVE (in-set contradiction found).
Exit 1 = sound on the in-set test.
"""
import hashlib, json, os, re, sys

PATH = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325/"
    "dispatch/726b14eba7612839abad55e6043be48b8f3d0176a51d4772f7574b8dea7cfc04/"
    "inputs/00-striatum-next-passes-capability-aware-placement-f-implementation-plan")
SHA256 = "a17d0d0b23b2ad0f0ed9d6301dbfcec0e7b6e4f6905ce26ca9d2490a699ccb18"

raw = open(PATH, "rb").read()
assert hashlib.sha256(raw).hexdigest() == SHA256, "substrate body hash mismatch"
doc = raw.decode("utf-8")
results = {"sha256_verified": True}

# --- Allegation 1: W14.9 vs W22.3 -----------------------------------------
w14_9_says_last = bool(re.search(
    r"the four states of\s+\[W22\]\(#el:w22-live-evidence-path\)\.3, of which "
    r"the last produces a reason list\s+of exactly `\[not_available\]`", doc))
w22_3_says_first = bool(re.search(
    r"an `excluded` slot\*\*\s+—\s+the first with a reason list of\s+"
    r"exactly `\[not_available\]`", doc))
absence_enumerated_first = bool(re.search(
    r"Absence, an unreadable or truncated body, a claimed derivation\s+"
    r"version this consumer does not implement, and a boundary ahead of the "
    r"ledger", doc))
claims_restated_to_agree = bool(re.search(
    r"\[W22\]\(#el:w22-live-evidence-path\)\.3 and "
    r"\[W14\]\(#el:w14-driver-wiring\)\.9 are\s+restated to agree", doc))
first_member_of_closed_set = "first member of the closed ordered set" in doc
results.update({
    "w14_9_says_last_produces_not_available": w14_9_says_last,
    "w22_3_says_first_produces_not_available": w22_3_says_first,
    "w22_3_enumerates_absence_first": absence_enumerated_first,
    "doc_claims_w14_9_and_w22_3_restated_to_agree": claims_restated_to_agree,
    "doc_fixes_not_available_as_first_member": first_member_of_closed_set,
})
defect_1 = w14_9_says_last and w22_3_says_first and absence_enumerated_first

# --- Allegation 2: edited-purposes count ----------------------------------
m = re.search(r"the `purpose` of ((?:`p\d+`(?:, | and )?)+)", doc)
edited_ids = re.findall(r"`(p\d+)`", m.group(1)) if m else []
five_claim = "the five edited purposes" in doc
seven_other = "the clauses appended to seven other purposes" in doc
rewrites = re.search(
    r"rewrites the\s+`purpose` of ((?:`p\d+`(?:, | and )?)+)", doc)
rewrite_ids = re.findall(r"`(p\d+)`", rewrites.group(1)) if rewrites else []
results.update({
    "edited_row_purpose_ids": edited_ids,
    "edited_row_purpose_count": len(edited_ids),
    "workgraph_rewrite_ids": rewrite_ids,
    "prose_says_five_edited_purposes": five_claim,
    "intro_says_seven_other_purposes": seven_other,
})
# The delta table classifies p22's purpose under "Edited" (not "Added"), so
# the prose count of five contradicts the table's own six-member Edited set.
defect_2 = five_claim and len(edited_ids) == 6 and "p22" in edited_ids

defective = defect_1 or defect_2
results["defect_w14_9_contradicts_w22_3"] = defect_1
results["defect_edited_purpose_count"] = defect_2
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND (in-set)")
sys.exit(0 if defective else 1)
