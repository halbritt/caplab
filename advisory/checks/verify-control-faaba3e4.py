"""Deterministic re-runnable check for dispatch 4b908cfc... (substrate
qs-faaba3e49977ce66, packet P10-bind-delivery-to-current-head): two reviewer
allegations tested against the change set's OWN two files only.

Exit 0 = control is DEFECTIVE (an allegation substantiated by in-set text on
         both sides of a contradiction).
Exit 1 = control is SOUND on the in-set record (no in-set contradiction).

Allegation A (authority): the only application record is an unadmitted
  candidate (admitted=false, movement_recorded=false) that defers the
  authoritative application to driver admission. Those facts are checked and
  confirmed below -- but the change set nowhere claims admission, movement, or
  a sealed record; the "undertaking" the reviewer measures against is the P10
  packet definition in the work graph, which is NOT in the change set. In-set,
  the facts are true and self-consistent; whether a candidate preimage is an
  acceptable P10 deliverable is a contract question this script cannot settle
  (flagged NEEDS-HUMAN in the audit; it does not flip the exit code).

Allegation B (evaluator nodes): the two check nodes carry only check_id, and
  target_check_authority repeats the ids with evaluator_evidence=false. Also
  confirmed -- and also out-of-contract: the record names the P20 change set
  (an ancestor in base_composition, not in this set) as authority for those
  ids, so their existence lives outside the change set by the record's own
  declaration. No in-set text claims the checks are defined here.
"""
import json, os, sys
exchange = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
DISPATCH = "4b908cfceb510be1"
full = [x for x in os.listdir(os.path.join(exchange, "dispatch"))
        if x.startswith(DISPATCH)][0]
bundle = os.path.join(exchange, "dispatch", full)
man = json.load(open(os.path.join(bundle, "manifest.json")))
cs = json.loads(open(os.path.join(bundle, man["inputs"][0]["path"]),
                     errors="replace").read())
files = cs["files"]
results = {"in_set_files": sorted(files)}
app_path = "ledger/RQ-57950/applications/delivery-to-current-head.json"
root_path = "ledger/RQ-57950/applications/closure-subject.product-tree-root.json"
app = json.loads(files[app_path])
root = json.loads(files[root_path])

# --- Allegation A: facts as alleged -------------------------------------
auth = app.get("authority", {})
results["A_kind_is_candidate"] = app.get("kind") == "application-record-candidate"
results["A_admitted_false"] = auth.get("admitted") is False
results["A_movement_recorded_false"] = auth.get("movement_recorded") is False
results["A_note_defers_authoritative_record"] = (
    "binds the complete application preimage" in auth.get("note", "")
    and "supplies the authoritative run, movement, licensing, Product occurrence, and sealed v2 application record"
    in auth.get("note", ""))
results["A_only_application_record_in_set"] = (
    sum(1 for n in files if n.startswith("ledger/RQ-57950/applications/")
        and n.endswith(".json") and "application" in json.loads(files[n]).get("kind", "")) == 1)
# The other side of a would-be contradiction: does any in-set text claim the
# application is admitted / moved / sealed / the authoritative record?
raw = "\n".join(files.values())
results["A_no_in_set_claim_of_admission"] = (
    '"admitted": true' not in raw and '"movement_recorded": true' not in raw
    and app.get("claim") == "asserted" and root.get("claim") == "asserted"
    and "sealed" not in app.get("kind", ""))
# The only in-set trace of the "undertaking" is the packet anchor name; the
# packet's purpose/outputs live in the work graph (out of set).
results["A_undertaking_in_set_is_anchor_name_only"] = (
    cs["packet"]["packet_anchor"] == "P10-bind-delivery-to-current-head"
    and not any(n.startswith("ledger/RQ-57950/work-graphs/") for n in files))
# Internal consistency of what IS claimed: root record pins the application by
# path + content_hash, tree roots agree with base_composition.
results["A_root_pins_application_hash"] = (
    root["application"]["path"] == app_path
    and root["application"]["content_hash"] == app["content_hash"])
results["A_tree_roots_consistent"] = (
    root["linked_tree_hash"] == cs["base_composition"]["resulting_base_hash"]
    == app["current_integrated_head"]["linked_tree_hash"]
    and root["tree_root"] == app["evaluator_subject"]["tree_root"]
    == app["current_integrated_head"]["materialized_tree_hash"])
results["A_in_set_contradiction"] = not (
    results["A_no_in_set_claim_of_admission"]
    and results["A_root_pins_application_hash"]
    and results["A_tree_roots_consistent"])

# --- Allegation B: facts as alleged -------------------------------------
nodes = app["target"]["declaration"]["evaluator"]["nodes"]
check_nodes = [n for n in nodes if n.get("kind") == "check"]
check_ids = [n["check_id"] for n in check_nodes]
results["B_check_nodes_carry_only_check_id"] = (
    len(check_nodes) == 2
    and all(set(n) == {"id", "kind", "check_id", "expected_result"} for n in check_nodes))
tca = app["target_check_authority"]
results["B_authority_repeats_ids"] = sorted(tca["check_ids"]) == sorted(check_ids)
results["B_evaluator_evidence_false"] = tca.get("evaluator_evidence") is False
results["B_no_in_set_check_definition"] = not any(
    n not in (app_path, root_path) and any(c in files[n] for c in check_ids)
    for n in files)
# The record's own declaration of where the checks live: P20, an ancestor.
p20 = tca["authority_change_set"]["identity"]
results["B_authority_names_P20_change_set"] = p20.endswith(
    "/P20-authorize-target-checks/change-set")
results["B_P20_is_ancestor_not_in_set"] = (
    any(a["change_set"]["identity"] == p20
        and a["change_set"]["content_hash"] == tca["authority_change_set"]["content_hash"]
        for a in cs["base_composition"]["ancestors"])
    and not any("P20" in n for n in files))
results["B_no_in_set_claim_checks_defined_here"] = (
    "runnable" not in raw and "command" not in raw.lower())
results["B_in_set_contradiction"] = not (
    results["B_authority_names_P20_change_set"]
    and results["B_P20_is_ancestor_not_in_set"]
    and results["B_no_in_set_claim_checks_defined_here"])

defective = results["A_in_set_contradiction"] or results["B_in_set_contradiction"]
results["control_is_defective"] = defective
results["needs_human"] = (
    "Allegation A facts are true in-set; whether P10 may deliver an unadmitted "
    "candidate preimage depends on the work-graph packet definition (out of set).")
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else
      "SOUND on in-set record (allegation A needs a human reading of the P10 packet contract)")
sys.exit(0 if defective else 1)
