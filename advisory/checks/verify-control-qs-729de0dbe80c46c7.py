"""Deterministic re-runnable check for dispatch b1f68ef0... (control
qs-729de0dbe80c46c7, subject striatum-next/passes/lint-rfcs-verification-
check/design, RQ-8499 — a design document, the dispatch's sole input).

Allegations (oc-deepseek-v4-flash + oc-deepseek-v4-pro), all eight:
  F1/P4: from-proposal identity does not resolve.  [graph store]
  F2: the premise that lint-rfcs's verdict is enforced in the build, not the
      claim, and the three properties "currently unmet", is contradicted by
      policy/checks/repository.json, which already registers lint-rfcs.
                                                   [policy registry]
  F3: clauses C1-C6 describe a state that already holds. [policy registry]
  P1: "lint-rfcs tool already exists" is false — no such tool in "this
      repository"; make check is just `check: test`.  [base tree]
  P2: policy/ and repository.json do not exist.       [base tree]
  P3: no gofmtcheck registry entry exists.            [policy registry]
  P5: registry and verifier are absent, so premises unearned. [base tree]

Contract position: every allegation depends on out-of-set content.
OUT-OF-CONTRACT — recorded, never scored. Out-of-set fact-check for the
record: P1/P2/P3/P5 were resolved against the WRONG repository — the cited
symptoms (`check: test` Makefile, history/ and advisory/ data dumps) match
~/git/caplab, not the design's declared repo striatum-next, where
tools/lint-rfcs, policy/checks/repository.json, and the gofmtcheck entry all
exist. F2/F3's "already registered" is true against the LIVE registry, but
the registration IS this design's own delivery (landed 2026-07-07 as
`lint-rfcs-is-a-verification-check@1`, commit 18b2e3c) — the premise was
true at the design's base; staleness-vs-base needs the pinned tree,
out-of-set either way.

What is mechanically checkable INSIDE the set:
  (a) the from-proposal identity is cited once, consistently, and shares the
      design's own declared identity stem (one in-set identity story);
  (b) the registration story is internally consistent: the doc claims
      gofmtcheck IS registered and lint-rfcs is NOT-yet; defective would be
      the doc also asserting somewhere that lint-rfcs is already in the
      registry (asserting and denying the same in-set premise);
  (c) the "already exists" claim is about the TOOL, while the delta claimed
      is the REGISTRY ENTRY — the doc must never claim the entry exists.

Reading encoded: the registry's actual contents are out-of-set; only an
internal assert-and-deny would convict.

Exit 0 = control is DEFECTIVE (in-set contradiction found).
Exit 1 = SOUND on the in-set test; out-of-set residue reported, not scored.
"""
import hashlib, json, os, re, sys

PATH = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325/"
    "dispatch/b1f68ef0d028552cc99ec602ad01b6cd8a3837b9d04f0b9daf0645f2ac2f7ee3/"
    "inputs/00-striatum-next-passes-lint-rfcs-verification-check-design")
SHA = "729de0dbe80c46c78216fd6910b30d6bdd150605fab2fd80656e85d7d081b169"

raw = open(PATH, "rb").read()
if hashlib.sha256(raw).hexdigest() != SHA:
    print("FATAL: substrate sha256 mismatch — refusing to adjudicate")
    sys.exit(2)
doc = raw.decode("utf-8")
results = {"substrate_sha256_verified": True}

# (a) one identity story.
ident = re.search(r"- identity: (\S+)", doc).group(1)
prop = re.search(r"- from-proposal: (\S+)", doc).group(1)
results["identity"] = ident
results["from_proposal"] = prop
results["proposal_shares_identity_stem"] = (
    prop.rsplit("/", 1)[0] == ident.rsplit("/", 1)[0]
    and prop.endswith("/proposal") and ident.endswith("/design"))
results["single_proposal_citation"] = doc.count(prop) == 1

# (b)+(c) internal registration story: tool exists; entry is the new delta.
results["claims_tool_exists"] = "`lint-rfcs` tool already exists" in doc
results["claims_enforced_in_build"] = (
    "enforced inside the build (`make check`) rather than inside the claim"
    in doc)
results["claims_properties_unmet"] = "currently unmet" in doc
results["delta_is_adding_one_entry"] = (
    "adding one registry\nentry to `policy/checks/repository.json`" in doc
    or "adding exactly one entry to `policy/checks/repository.json`" in doc)
# Defect trigger: any in-set sentence asserting lint-rfcs is ALREADY
# registered / already in the registry / already a verification check.
already = re.findall(
    r"[^.\n]*lint-rfcs[^.\n]*already (?:registered|in the registry|a "
    r"registered check|gates? verification)[^.\n]*", doc, re.I)
results["inset_assertions_lint_rfcs_already_registered"] = already
# The gofmtcheck claim is the opposite pole and must stay consistent too:
results["gofmtcheck_cited_as_existing_entry"] = (
    "the existing\n`gofmtcheck` entry" in doc
    or "the existing `gofmtcheck` entry" in doc
    or "same shape as the existing" in doc)

results["out_of_contract"] = [
    "F1/P4 proposal resolution: graph store, out-of-set.",
    "F2/F3 'already registered' staleness: policy/checks/repository.json, "
    "out-of-set. Live-registry fact, recorded not scored: lint-rfcs IS "
    "registered today, but that registration is this design's own delivery "
    "(2026-07-07, commit 18b2e3c) — the premise was true at authoring.",
    "P1/P2/P3/P5 tool/registry/verifier absence: base tree, out-of-set — "
    "and resolved against the wrong repository (symptoms match caplab, not "
    "the declared striatum-next, which has tools/lint-rfcs, policy/checks/"
    "repository.json, and the gofmtcheck entry).",
]

defective = (
    not results["proposal_shares_identity_stem"]
    or bool(already)
    or (results["claims_properties_unmet"]
        and not results["delta_is_adding_one_entry"])
)
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else
      "SOUND (in-set); all eight allegations out-of-contract")
sys.exit(0 if defective else 1)
