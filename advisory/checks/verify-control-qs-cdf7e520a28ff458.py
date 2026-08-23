"""Deterministic re-runnable check for control qs-cdf7e520a28ff458
(work-graph-doc implementation plan, dispatch 0647e7d0...).

Allegations:
  flash (4): the derives-from design does not exist in the repository; the
      target directory docs/concepts/ does not exist; RQ-317 resolves to no
      tracker record; the P1-P8 chain cannot be cross-checked against the
      absent design's stage boundaries. Every one of these tests the plan
      against the REPOSITORY, not against the plan's own content — all four
      are OUT-OF-CONTRACT for this audit.
  pro (1): W2 assigns the inline definition of "Work Graph" to the Overview
      while "the design's Q4" allegedly fixes the owning section
      differently. The design is not in the set, so the comparison is
      out-of-contract; the in-set scoreable core is only whether the plan
      contradicts ITSELF about where each term is defined.

Mechanically checkable in-set (the plan's internal consistency):
  (a) AC-anchors says "all nine slugs" and W1 lays down exactly nine
      distinct anchors (six top-level + three subsections);
  (b) AC-vocab says "All nine terms" and enumerates exactly nine;
  (c) every packet acceptance_checks entry resolves to a defined AC-* id,
      every derived_from anchor exists as a heading anchor, and the
      declared serialized chain is genuine (P1<-P2<-...<-P8, one shared
      write scope);
  (d) exactly one work item claims the inline definition of "Work Graph",
      and it is W2/Overview — no in-set statement assigns it elsewhere.

Exit 0 = control is DEFECTIVE (in-set contradiction). Exit 1 = sound in-set.
"""
import hashlib, json, os, re, sys

PATH = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325/"
    "dispatch/0647e7d0bbacc9a022cbc5a5309ca2dbce0c6fe6452c0d5f174cdf97e54306e8/"
    "inputs/00-striatum-next-intents-work-graph-doc-implementation-plan")
SHA256 = "cdf7e520a28ff458393a54a588ba4fac0b04c3a50c807217847d6ec4c932e144"

raw = open(PATH, "rb").read()
assert hashlib.sha256(raw).hexdigest() == SHA256, "substrate body hash mismatch"
doc = raw.decode("utf-8")
results = {"sha256_verified": True}

# (a) nine anchors laid down by W1.
w1 = re.search(r"### W1 — .*?(?=\n### )", doc, re.S).group(0)
# "slug" is W1's literal placeholder ("Every heading carries its {#el:slug}
# anchor"), not a laid-down anchor.
w1_anchors = [a for a in re.findall(r"`\{#el:([a-z0-9-]+)\}`", w1)
              if a != "slug"]
results["w1_anchor_slugs"] = sorted(set(w1_anchors))
results["w1_anchor_count"] = len(set(w1_anchors))
results["ac_anchors_says_nine"] = "all nine slugs" in doc

# (b) nine terms in AC-vocab.
vocab = re.search(r"\*\*AC-vocab\*\* — All nine terms \(([^)]+)\)", doc)
terms = [t.strip() for t in vocab.group(1).split(",")] if vocab else []
results["ac_vocab_terms"] = terms
results["ac_vocab_term_count"] = len(terms)

# (c) work-graph block resolves against the plan's own definitions.
block = re.search(r"```striatum-work-graph\n(.*?)```", doc, re.S).group(1)
wg = json.loads(block)
ac_ids = set(re.findall(r"\*\*(AC-[a-z-]+)\*\*", doc))
anchors = set(re.findall(r"\{#el:([a-z0-9-]+)\}", doc))
unresolved_checks, unresolved_anchors, chain_ok = [], [], True
prev = None
scopes = set()
for p in wg["packets"]:
    for c in p["acceptance_checks"]:
        if c not in ac_ids:
            unresolved_checks.append((p["id"], c))
    if p["derived_from"].removeprefix("el:") not in anchors:
        unresolved_anchors.append((p["id"], p["derived_from"]))
    if p["depends_on"] != ([] if prev is None else [prev]):
        chain_ok = False
    prev = p["id"]
    scopes.update(p["write_scope"])
results["packet_count"] = len(wg["packets"])
results["unresolved_acceptance_checks"] = unresolved_checks
results["unresolved_derived_from_anchors"] = unresolved_anchors
results["serialized_chain_as_declared"] = chain_ok
results["single_shared_write_scope"] = (
    scopes == {"docs/concepts/work-graph-build-flow.md"})

# (d) exactly one in-set assignment of the Work Graph inline definition.
assigning = []
for m in re.finditer(r"### (W\d+) — .*?(?=\n### |\Z)", doc, re.S):
    if re.search(r"Define\s+\*Work Graph\*", m.group(0)):
        assigning.append(m.group(1))
results["work_items_defining_work_graph"] = assigning

results["out_of_contract"] = [
    "existence of striatum-next/intents/work-graph-doc/design in the repo",
    "existence of docs/concepts/ in the repo",
    "resolvability of RQ-317 against any tracker",
    "the design's Q4 / C11 content (design document is not in the set)",
]

defective = (
    results["w1_anchor_count"] != 9
    or not results["ac_anchors_says_nine"]
    or results["ac_vocab_term_count"] != 9
    or unresolved_checks or unresolved_anchors or not chain_ok
    or not results["single_shared_write_scope"]
    or assigning != ["W2"]
)
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else
      "SOUND (in-set); all reviewer allegations out-of-contract")
sys.exit(0 if defective else 1)
