"""Deterministic re-runnable check for control qs-e95b9a190bea1f12
(terminal-report-live implementation plan, dispatch e38df1b0...).

Allegations (oc-deepseek-v4-flash + oc-deepseek-v4-pro): (1) the revision
header's references to inputs/90-diagnostic-... and inputs/91-diagnostic-...
do not resolve; (2)-(6) the Grounding section and W1 describe repository
state (pass_run_closed at schema_version 1, no trl2-guards evaluator, no
exitReason field, missing write_scope paths, registry "v7" vs live v34)
that disagrees with the live tree at HEAD, and W5-W7 re-deliver merged @1
work.

Every state-mismatch allegation compares the plan to the live repository
tree or the live check registry: OUT-OF-CONTRACT for this audit (the set
is the single plan document; no repo file and no registry is in-set). The
inputs/9x references point at sibling dispatch inputs, i.e. at the dispatch
packaging, not at in-set content -- also out-of-contract (the control
re-dispatch ships only the subject).

What is mechanically checkable INSIDE the set:
  (a) the Status claim "`acceptance_checks` now names only registered v7
      sets: `stalls-guards` on every packet, and `code` on every packet"
      matches the packet graph: every packet's acceptance_checks is exactly
      {stalls-guards, code};
  (b) the Status claim that `terminal-report-conformance` and
      `terminal-report-docs-and-fences` "remain packet IDs only; they are
      not acceptance checks" holds: no packet id appears in any
      acceptance_checks list;
  (c) every packet's derived_from resolves to an #el: anchor present in
      the document;
  (d) the plan's rollout claim "no packet is gated by a check or set that
      the packet itself delivers" is not contradicted in-set (no packet
      names a new terminal-report-specific check).

Exit 0 = control is DEFECTIVE (an in-set claims-versus-content
contradiction found). Exit 1 = SOUND on the in-set test.
"""
import hashlib, json, os, re, sys

PATH = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325/"
    "dispatch/e38df1b049479ea84711d1df5b368dbbdb05a304d611f1c086885ea6f656cffc/"
    "inputs/00-striatum-next-passes-terminal-report-live-implementation-plan")
SHA256 = "e95b9a190bea1f12edeb1d069f9f44f741b8adc81cf9fea1641345c250db550a"

raw = open(PATH, "rb").read()
if hashlib.sha256(raw).hexdigest() != SHA256:
    print("substrate sha256 mismatch -- refusing to adjudicate", file=sys.stderr)
    raise SystemExit(2)
doc = raw.decode("utf-8")

results = {}

fence = re.search(r"```striatum-work-graph\n(.*?)\n```", doc, re.S)
graph = json.loads(fence.group(1))
packets = graph["packets"]
results["packet_ids"] = [p["id"] for p in packets]

# (a) every packet binds exactly stalls-guards + code.
results["every_packet_binds_exactly_stalls_guards_and_code"] = all(
    sorted(p["acceptance_checks"]) == ["code", "stalls-guards"] for p in packets)

# (b) no packet id is used as an acceptance check anywhere.
ids = {p["id"] for p in packets}
results["packet_id_used_as_acceptance_check"] = sorted(
    ids & {c for p in packets for c in p["acceptance_checks"]})

# (c) derived_from anchors resolve to declared #el: anchors in the doc.
anchors = set(re.findall(r"\{#el:([a-z0-9-]+)\}", doc))
results["unresolved_derived_from"] = sorted(
    p["derived_from"] for p in packets if p["derived_from"] not in anchors)

# (d) no terminal-report-specific check name in any acceptance_checks.
results["nonregistered_style_checks_named"] = sorted(
    {c for p in packets for c in p["acceptance_checks"]}
    - {"code", "stalls-guards"})

# Status-claim sentences present, so (a)/(b) are the claims under test.
results["claim_only_registered_sets"] = (
    "`acceptance_checks` now names only registered v7 sets" in doc)
results["claim_packet_ids_not_checks"] = (
    "remain packet IDs only; they are not acceptance checks" in doc)

results["out_of_contract"] = [
    "inputs/90-diagnostic-* and inputs/91-diagnostic-* resolve against the "
    "dispatch bundle (production revision context), not against in-set "
    "content; the control re-dispatch ships only the subject",
    "catalog/ledger-record-types/pass_run_closed.yaml and "
    "schema/ledger-records/pass_run_closed.schema.json version claims are "
    "about the live tree at HEAD",
    "trl2-guards evaluator obligation lives in the live "
    "catalog/target-states/terminal-report-live.yaml",
    "registry 'v7' vs live registry_version 34 is about "
    "policy/checks/repository.json, not in-set",
    "W5-W7 re-delivery-of-merged-@1 and write_scope paths absent at HEAD "
    "are live-tree comparisons",
]
results["needs_judgment"] = (
    "whether a plan whose Grounding snapshot has been outrun by the live "
    "tree is stale (an invalidation matter) rather than internally "
    "defective; staleness is not adjudicable from the set")

defective = (
    (results["claim_only_registered_sets"]
     and not results["every_packet_binds_exactly_stalls_guards_and_code"])
    or (results["claim_packet_ids_not_checks"]
        and bool(results["packet_id_used_as_acceptance_check"]))
    or bool(results["unresolved_derived_from"])
    or bool(results["nonregistered_style_checks_named"])
)
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND (in-set); see out_of_contract")
sys.exit(0 if defective else 1)
