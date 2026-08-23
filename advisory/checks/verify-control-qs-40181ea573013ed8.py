"""Deterministic re-runnable check for control qs-40181ea573013ed8
(freshness-needs-no-judgment implementation plan).

Allegations (deepseek v4 flash + pro): (1) the completion standard omits the
target-state's machine-core property fixtures (per
catalog/target-states/freshness-needs-no-judgment.yaml); (2) the embedded work
graph does not lower canonically as schema v2 (missing schema_version/plan/
index per schema/work-graph.schema.json); (3-5) required implementation-plan
stage sections — migration and rollout, risk register, milestones, phases and
dependency rationale — are absent per catalog/artifact-kinds/
implementation-plan.yaml.

In-set adjudication: every allegation's normative source (the target-state
yaml, the work-graph schema, the artifact-kind catalog) is an out-of-set file
— OUT-OF-CONTRACT by the audit standard; recorded, never scored. This is the
exact pattern the 2026-08-23 rulings named: importing an out-of-set obligation
into an in-set contract. What IS in-set checkable is the document's own
consistency: every packet's derived_from anchor resolves to a heading in the
doc, depends_on is closed over declared packet ids, the acceptance mapping
covers C1-C6 and references only elements the doc defines, and the fenced
graph parses. The oracle also records (not scores) that the alleged missing
section headings are indeed absent, so the factual predicate of allegations
(3-5) is preserved for any future Principal ruling that the artifact-kind
catalog binds in-contract.

Exit 0 = control is DEFECTIVE (an in-set inconsistency exists).
Exit 1 = SOUND on the in-set test; out-of-contract residue recorded.
"""
import hashlib, json, re, sys

PATH = ("/home/halbritt/.local/share/striatum/exchange/"
        "019f22ef-0cb4-780f-9b82-b210bab24325/dispatch/"
        "822676378a36b799f28e5c94f8b72ec2da396d6a2d88adf89f67e9352338a8a5/"
        "inputs/00-striatum-next-passes-freshness-needs-no-judgment-implementation-plan")
SHA = "40181ea573013ed8e513bbb0887adafc88929642ab037e0c97ccc27c117a6f60"

raw = open(PATH, "rb").read()
assert hashlib.sha256(raw).hexdigest() == SHA, "substrate body hash mismatch"
doc = raw.decode("utf-8")
results = {}

# In-set consistency: fenced graph parses; anchors and dependencies resolve.
graph_src = re.search(r"```striatum-work-graph\n(.*?)```", doc, re.S).group(1)
graph = json.loads(graph_src)
anchors = set(re.findall(r"\{#(el:[a-z0-9-]+)\}", doc))
ids = {p["id"] for p in graph["packets"]}
results["packet_count"] = len(graph["packets"])
results["unresolved_derived_from"] = [
    p["derived_from"].lstrip("#") for p in graph["packets"]
    if p["derived_from"].lstrip("#") not in anchors]
results["unresolved_depends_on"] = [
    d for p in graph["packets"] for d in p["depends_on"] if d not in ids]
# Acceptance mapping names C1-C6, and each ordered-work element the mapping
# leans on exists as a heading.
results["acceptance_mapping_covers_C1_C6"] = all(
    re.search(rf"\| C{i} ", doc) for i in range(1, 7))
results["seven_ordered_elements_present"] = all(
    f"Element {i} -" in doc for i in range(1, 8))
# The declared kind is internally restated consistently.
results["kind_declared_implementation_plan"] = (
    "Artifact kind: implementation-plan" in doc)
results["target_declared"] = "Target: freshness-needs-no-judgment@1" in doc

# Factual predicates of the out-of-contract allegations, recorded not scored.
low = doc.lower()
results["recorded_absent_migration_rollout_section"] = not re.search(
    r"^#+.*(migration|rollout)", low, re.M)
results["recorded_absent_risk_register_section"] = not re.search(
    r"^#+.*risk", low, re.M)
results["recorded_no_milestones_named"] = "milestone" not in low
results["recorded_graph_lacks_schema_version_plan_index"] = not any(
    k in graph for k in ("schema_version", "plan", "index"))
results["recorded_completion_std_names_no_property_fixtures"] = (
    "fixture" not in doc.split("## Completion Standard")[1].lower())

results["out_of_contract"] = [
    "required-section list lives in catalog/artifact-kinds/"
    "implementation-plan.yaml, outside the set",
    "machine-core fixture clause lives in catalog/target-states/"
    "freshness-needs-no-judgment.yaml, outside the set",
    "canonical lowering shape lives in schema/work-graph.schema.json, "
    "outside the set",
]

defective = bool(results["unresolved_derived_from"]
                 or results["unresolved_depends_on"]
                 or not results["acceptance_mapping_covers_C1_C6"]
                 or not results["seven_ordered_elements_present"]
                 or not results["kind_declared_implementation_plan"])
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND (in-set); allegations out-of-contract")
sys.exit(0 if defective else 1)
