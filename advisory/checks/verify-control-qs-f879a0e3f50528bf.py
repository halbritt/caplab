"""Deterministic re-runnable check for dispatch acf925f3... (control
qs-f879a0e3f50528bf, subject striatum-next/cli/cancel-verb/design — a design
document, the dispatch's sole input).

Allegations (oc-deepseek-v4-flash):
  A1: the prior-review ledger `evidence/review/striatum-next-cli-cancel-verb-
      design/2093` (load-bearing for the C3 decide-before-seal reorder) does
      not resolve: no `evidence/` directory in halbritt/striatum-next at
      head fbfbdbf.
  A2: `sealIfDueLocked` is cited at `internal/store/ledger.go:290`, but at
      base fbfbdbf it is defined at line 293 and line 290 holds an unrelated
      element (`return *g.activeCache, true`).

Contract position: both allegations depend on out-of-set content (the graph
store's evidence records; the base git tree). OUT-OF-CONTRACT — recorded,
never scored. Out-of-set fact-check for the record: A1 mistakes a provenance
evidence identity for a git path (review ledgers live in the graph store, not
the repository tree); A2 is factually wrong even out-of-set — at fbfbdbf,
ledger.go line 290 is the opening line of sealIfDueLocked's own doc comment
("// sealIfDueLocked rolls the active segment ..."), with the func keyword at
293; the citation points at the element it names.

What is mechanically checkable INSIDE the set:
  (a) every citation of the prior review uses one identity (".../2093") —
      no in-set statement gives a conflicting review identity;
  (b) the seam order story is internally consistent: C3's normative order
      places admit(all) BEFORE sealIfDueLocked, the old Admit/ReStamp
      composition is stated with sealIfDueLocked BEFORE the decision, and no
      in-set statement asserts the new seam seals before deciding;
  (c) sealIfDueLocked carries exactly one in-set line citation — no second,
      differing line number for the same symbol.

Exit 0 = control is DEFECTIVE (in-set contradiction found).
Exit 1 = SOUND on the in-set test; out-of-set residue reported, not scored.
"""
import hashlib, json, os, re, sys

PATH = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325/"
    "dispatch/acf925f3b09f1dab700e06da57b14360904825c81d9255e0164e19d0c1da9818/"
    "inputs/00-striatum-next-cli-cancel-verb-design")
SHA = "f879a0e3f50528bf190379fdce83440d8ee74fa130681adf2966b608a44c3a19"

raw = open(PATH, "rb").read()
if hashlib.sha256(raw).hexdigest() != SHA:
    print("FATAL: substrate sha256 mismatch — refusing to adjudicate")
    sys.exit(2)
doc = raw.decode("utf-8")
results = {"substrate_sha256_verified": True}

# (a) one review identity throughout.
rev_ids = set(re.findall(r"evidence/review/[A-Za-z0-9/_-]+/\d+", doc))
results["review_identities_cited"] = sorted(rev_ids)
results["single_review_identity"] = rev_ids == {
    "evidence/review/striatum-next-cli-cancel-verb-design/2093"}
results["review_2093_mentions"] = len(re.findall(r"review 2093|2093's", doc))

# (b) seam-order internal consistency.
c3 = re.search(r"\*\*C3 — .*?(?=\n- \*\*C4|\Z)", doc, re.S)
c3_text = c3.group(0) if c3 else ""
results["c3_found"] = bool(c3)
# normative new order: admit(all) before sealIfDueLocked inside C3's order.
order = re.search(
    r"`TryAppendLock` → `recoverAndScanActive` → `Records\(\)` → "
    r"`admit\(all\)` →.*?`sealIfDueLocked` → `appendLocked`",
    c3_text, re.S)
results["c3_decide_before_seal_order_stated"] = bool(order)
# old composition: seal before decide, attributed to Admit/ReStamp.
old = re.search(
    r"TryAppendLock → recoverAndScanActive → sealIfDueLocked → Records\(\) "
    r"→ decide → appendLocked", doc)
results["old_admit_restamp_order_stated"] = bool(old)
results["asymmetry_acknowledged"] = (
    "intentionally differs from `Admit`/`ReStamp`" in doc)
# no in-set claim that the NEW seam seals before deciding: in every arrow
# chain containing both admit(all) and sealIfDueLocked, admit comes first.
# (A plain proximity grep misfires on line 106's guard sentence, which warns
# AGAINST "reordering AppendRecordIf back to seal-before-decide".)
# A seal-first chain is only a contradiction when asserted of the CURRENT
# design; the doc lawfully recites the refused prior version's order ("the
# prior C3 mandated the store sequence ...", line 12) and Admit/ReStamp's.
bad_chains = []
for mm in re.finditer(r"(?:`?\w+(?:\(\w*\))?`? → )+`?\w+(?:\(\w*\))?`?", doc):
    c = mm.group(0)
    if not ("admit(all)" in c and "sealIfDueLocked" in c
            and c.index("sealIfDueLocked") < c.index("admit(all)")):
        continue
    ctx = doc[max(0, mm.start() - 250):mm.start()]
    attributed_to_prior = bool(re.search(
        r"prior|refused|Admit`?/`?ReStamp|review 2093", ctx, re.I))
    if not attributed_to_prior:
        bad_chains.append(c)
results["current_seam_chains_with_seal_before_admit"] = bad_chains
results["new_seam_never_claimed_seal_first"] = not bad_chains

# (c) one line citation for sealIfDueLocked.
lines = set(re.findall(r"sealIfDueLocked[^\n]{0,40}?ledger\.go:(\d+)", doc)) | \
        set(re.findall(r"ledger\.go:(\d+)[^\n]{0,40}?sealIfDueLocked", doc)) | \
        set(re.findall(r"`sealIfDueLocked` \(`internal/store/ledger\.go:(\d+)`\)", doc))
results["sealIfDueLocked_line_citations"] = sorted(lines)
results["single_line_citation"] = len(lines) <= 1

results["out_of_contract"] = [
    "A1: evidence/review/.../2093 is a graph-store evidence identity; its "
    "resolution lives in the provenance ledger, out-of-set (and it is not a "
    "git path, so its absence from the fbfbdbf tree proves nothing).",
    "A2: the ledger.go line number is a claim about the out-of-set base "
    "tree. Out-of-set fact, recorded not scored: at fbfbdbf line 290 is the "
    "first line of sealIfDueLocked's doc comment (func at 293); the flash "
    "claim that 290 holds `return *g.activeCache, true` is false.",
]

defective = (
    not results["single_review_identity"]
    or not results["c3_decide_before_seal_order_stated"]
    or not results["old_admit_restamp_order_stated"]
    or not results["new_seam_never_claimed_seal_first"]
    or not results["single_line_citation"]
)
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else
      "SOUND (in-set); both allegations out-of-contract")
sys.exit(0 if defective else 1)
