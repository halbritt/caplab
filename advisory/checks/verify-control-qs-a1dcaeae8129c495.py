"""Deterministic re-runnable check for dispatch 2e921f25... (control
qs-a1dcaeae8129c495, subject striatum-next/passes/work-graph-assembly-e/
implementation-plan — an L3 plan document with an embedded striatum-work-graph
JSON, the dispatch's sole input).

Allegations (oc-deepseek-v4-flash + oc-deepseek-v4-pro), all seven:
  F1/P3: design anchors .../work-graph-assembly-e/design#el:c1..c9 resolve to
      no existing document.                       [graph store / base tree]
  F2: catalog/irs/ does not exist; the change-set IR home is
      catalog/artifact-kinds/.                    [base tree]
  F3: the `code` set is declared as "build, vet, lint-rfcs, gofmtcheck, and
      tests" but the registered set has four checks and no tests.
                                                  [policy registry]
  P1: every confirmed repository seam fails to resolve. [base tree]
  P2: base input repository-tree@cc5a130... absent from the object store.
                                                  [git object store]
  P4: check id 4cfe89f9... not registered; repository.json absent.
                                                  [policy registry]

Contract position: every allegation depends on out-of-set content (the base
tree, the graph store, the check registry, the git object store).
OUT-OF-CONTRACT — recorded, never scored. Out-of-set fact-check for the
record (striatum-next live): cc5a130d... IS in the object store (a tree
object — `git cat-file -t` says "tree"; P2's probe expected a commit);
policy/checks/repository.json EXISTS and registers 4cfe89f9 with exactly the
argv the plan states (`go run ./tools/standing-guards/
wgi-subject-assembles-from-packets`, delivery_status red), refuting P1/P4's
resolution claims (the pro reviewer resolved against the wrong tree); F2 is
true against the live tree (no catalog/irs/) and F3 is true against the live
registry (code = build, vet, lint-rfcs, gofmtcheck — no test check).

What is mechanically checkable INSIDE the set (the mechanical core):
  (a) the embedded striatum-work-graph JSON parses; index == packet ids;
      depends_on resolve to in-set packet ids;
  (b) each packet's derived_from anchor (el:packet-*) exists in the document;
  (c) each packet's write_scope covers all its repository-path outputs;
  (d) every design anchor cited in the work-graph inputs also appears in the
      prose "Design anchors" lists (one in-set anchor story);
  (e) the guard entrypoint named in confirmed-seams equals the guard
      directory the code packet delivers (one in-set entrypoint story).

Exit 0 = control is DEFECTIVE (in-set contradiction found).
Exit 1 = SOUND on the in-set test; out-of-set residue reported, not scored.
"""
import hashlib, json, os, re, sys

PATH = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325/"
    "dispatch/2e921f25a4aca916dd2b8e36f5c0d825e856d87712de1f2d6bd1bfef86fe4d8f/"
    "inputs/00-striatum-next-passes-work-graph-assembly-e-implementation-plan")
SHA = "a1dcaeae8129c495ab80a7aea5783cbb861fe5bc398d4eb701d835962155ee2f"

raw = open(PATH, "rb").read()
if hashlib.sha256(raw).hexdigest() != SHA:
    print("FATAL: substrate sha256 mismatch — refusing to adjudicate")
    sys.exit(2)
doc = raw.decode("utf-8")
results = {"substrate_sha256_verified": True}

# (a) embedded work graph parses and is self-resolving.
m = re.search(r"```striatum-work-graph\n(.*?)\n```", doc, re.S)
results["work_graph_block_found"] = bool(m)
wg = json.loads(m.group(1))
ids = [p["id"] for p in wg["packets"]]
results["index_matches_packets"] = wg["index"] == ids
results["depends_on_resolve"] = all(
    d in ids for p in wg["packets"] for d in p.get("depends_on", []))

# (b) derived_from anchors exist in the document.
results["derived_from_anchors_exist"] = all(
    ("{#" + p["derived_from"] + "}") in doc for p in wg["packets"])

# (c) write_scope covers repository-path outputs.
def covered(out, scopes):
    return any(out == s or (s.endswith("/") and out.startswith(s))
               or out.startswith(s.rstrip("/") + "/") for s in scopes)
uncovered = [(p["id"], o) for p in wg["packets"] for o in p["outputs"]
             if not covered(o, p["write_scope"])]
results["outputs_uncovered_by_write_scope"] = uncovered

# (d) one in-set design-anchor story: work-graph anchor inputs appear in prose.
wg_anchors = {i.split("#", 1)[1] for p in wg["packets"] for i in p["inputs"]
              if "#el:" in i}
prose = doc[: m.start()]
missing_in_prose = sorted(a for a in wg_anchors
                          if "`" + a + "`" not in prose)
results["wg_anchors_missing_from_prose_lists"] = missing_in_prose

# (e) one entrypoint story.
guards = set(re.findall(r"tools/standing-guards/([A-Za-z0-9_-]+)", doc))
results["guard_entrypoints_named"] = sorted(guards)
results["single_guard_entrypoint"] = guards == {
    "wgi-subject-assembles-from-packets"}

# recorded in-set tension, not scored as contradiction: the confirmed-seams
# survey names catalog/artifact-kinds/change-set.yaml and never mentions
# catalog/irs/change-set.yaml, yet the catalog packet directs "updating" it.
results["catalog_irs_named_in_confirmed_seams"] = (
    "catalog/irs" in doc.split("## Atomic implementation packet")[0])
results["catalog_irs_in_packet_outputs"] = any(
    "catalog/irs/change-set.yaml" in p["outputs"] for p in wg["packets"])

results["out_of_contract"] = [
    "F1/P3 design-document existence: graph store / base tree, out-of-set.",
    "F2 catalog/irs absence: base tree, out-of-set (true against live tree).",
    "F3 code-set membership: policy/checks/repository.json, out-of-set "
    "(true against live registry — no test check in `code`).",
    "P1/P4 seam and registry resolution: base tree/registry, out-of-set — "
    "and refuted against the live striatum-next tree (repository.json "
    "exists; 4cfe89f9 registered with exactly the argv the plan states); "
    "the pro reviewer resolved against the wrong repository.",
    "P2 cc5a130... object-store presence: out-of-set — and refuted: it is a "
    "tree object, present (`git cat-file -t` = tree).",
]

defective = (
    not results["work_graph_block_found"]
    or not results["index_matches_packets"]
    or not results["depends_on_resolve"]
    or not results["derived_from_anchors_exist"]
    or bool(uncovered)
    or bool(missing_in_prose)
    or not results["single_guard_entrypoint"]
)
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else
      "SOUND (in-set); all seven allegations out-of-contract")
sys.exit(0 if defective else 1)
