"""Deterministic re-runnable check for control qs-55beeb775063c017
(lane-output-is-a-file implementation plan, dispatch dac57308...).

Allegations:
  flash A1: the accepted implementation-plan artifact kind
      (catalog/artifact-kinds/implementation-plan.yaml) requires a
      milestones section and a risk register; the plan has neither.
  flash A2: the catalog requires packet boundaries to cite the DESIGN
      elements they implement; every packet's derived_from cites this
      plan's own anchors instead.
  flash A3: registering only policy/checks/repository.json leaves the
      generated-from-template registry stale (tools/checkreg wiring).
  pro  A1: the header's derived_from names
      striatum-next/passes/lane-output-is-a-file/design, and no such
      design exists anywhere in the striatum-next repository.

All four depend on out-of-set material -- the live catalog artifact-kind
contract, production checkreg wiring, and the repository tree / artifact
graph -- so all four are OUT-OF-CONTRACT for this audit and never scored.
(For the record, the live catalog's `required` list DOES include
"milestones" and "risk register", so flash A1's premise is true out-of-set;
that residual is preserved for the Principal, not scored here.)

What is mechanically checkable INSIDE the set:
  (a) every work-graph derived_from resolves to a declared #el: anchor in
      the document (in-set reference resolution);
  (b) packet loif-03's own rule -- "must not use the newly registered
      check set as its own acceptance_checks" -- is honoured: loif-03
      gates only on "code";
  (c) the verification matrix's per-element check sets equal the work
      graph's per-packet acceptance_checks (docs -> subject-default,
      everything else -> code);
  (d) no statement in the plan claims a milestones section or risk
      register exists (no unearned completeness claim).

Exit 0 = control is DEFECTIVE (in-set contradiction found).
Exit 1 = SOUND on the in-set test; out-of-contract residue reported.
"""
import hashlib, json, os, re, sys

PATH = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325/"
    "dispatch/dac5730885618f1242973c27ab32c976eee8979938dae44705081101159c461b/"
    "inputs/00-striatum-next-passes-lane-output-is-a-file-implementation-plan")
SHA256 = "55beeb775063c017520eaf7a659841529b9d6970fee026a4d95aea43c6f45f2b"

raw = open(PATH, "rb").read()
if hashlib.sha256(raw).hexdigest() != SHA256:
    print("substrate sha256 mismatch -- refusing to adjudicate", file=sys.stderr)
    raise SystemExit(2)
doc = raw.decode("utf-8")

results = {}

fence = re.search(r"```striatum-work-graph\n(.*?)\n```", doc, re.S)
graph = json.loads(fence.group(1))
packets = {p["id"]: p for p in graph["packets"]}
anchors = set(re.findall(r"\{#el:([a-z0-9-]+)\}", doc))

# (a) in-set reference resolution.
results["unresolved_derived_from"] = sorted(
    p["derived_from"] for p in packets.values()
    if p["derived_from"].removeprefix("#el:") not in anchors)

# (b) loif-03 does not gate on its own new check set.
results["loif03_acceptance_checks"] = packets[
    "loif-03-validation-entrypoint"]["acceptance_checks"]
results["loif03_self_gates_on_new_set"] = any(
    c not in ("code", "stalls-guards", "subject-default")
    for c in results["loif03_acceptance_checks"])

# (c) verification matrix agrees with the work graph.
matrix = dict(re.findall(
    r"\| `#el:([a-z0-9-]+)` \|[^|]*\| `([a-z-]+)` \|", doc))
by_anchor = {p["derived_from"].removeprefix("#el:"):
             p["acceptance_checks"] for p in packets.values()}
results["matrix_vs_graph_mismatches"] = sorted(
    a for a, s in matrix.items() if by_anchor.get(a) != [s])

# (d) no unearned claim of milestones / risk-register presence.
results["claims_milestones_or_risk_register"] = bool(
    re.search(r"\bmilestone|\brisk register", doc, re.I))

results["out_of_contract"] = [
    "flash A1: milestones + risk register obligation lives in the live "
    "catalog/artifact-kinds/implementation-plan.yaml (out-of-set; premise "
    "true on the live tree -- preserved for the Principal: if catalog-kind "
    "completeness is ruled in-contract for plan-stage substrates, this "
    "control flips)",
    "flash A2: 'packet boundaries cite design elements' is the same "
    "out-of-set catalog contract; in-set the derived_from references "
    "resolve (to plan anchors)",
    "flash A3: tools/checkreg template-generation wiring is production "
    "wiring, out-of-set",
    "pro A1: existence of the design artifact behind the header's "
    "derived_from identity is an artifact-graph / repo-tree fact, "
    "out-of-set (designs live in the ledger CAS, not necessarily as a "
    "passes/ directory)",
]
results["needs_judgment"] = (
    "stage-completeness against the catalog artifact-kind is the live "
    "residual; nothing in-set contradicts anything in-set")

defective = (
    bool(results["unresolved_derived_from"])
    or results["loif03_self_gates_on_new_set"]
    or bool(results["matrix_vs_graph_mismatches"])
    or results["claims_milestones_or_risk_register"]
)
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective
      else "SOUND (in-set); see out_of_contract")
sys.exit(0 if defective else 1)
