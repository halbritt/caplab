"""Deterministic re-runnable check for dispatch 71ac079a... (substrate
qs-a190c423a1dcce98, capability-aware-placement-d guards-only packet).

Reviewer allegations, and what is checked against the change set's OWN files:

  1. "CHANGELOG claims the packet declares acceptance_checks but the delivered
     packet has no acceptance_checks field."  -> The change set's `packet` is a
     four-field packet-element ANCHOR, and the in-set CHANGELOG itself names
     exactly those four fields as the anchor. The `acceptance_checks` the
     CHANGELOG cites belong to the work-graph packet element, which is not in
     the set. Recorded as consistent / out-of-contract; never counts as defect.
  2-4. "Each guard greps source tokens and tests its own local reimplementation;
     it never exercises ProjectBackends / scheduler.Bind / LoadOrEmpty / the
     objective ordering, so the CHANGELOG's 'proves ...' is unearned."
     -> Checked mechanically: CHANGELOG says each guard "proves" a property of
     the machinery; each guard imports stdlib only, contains no call into the
     machinery, and backs the strongest claim (declarations never mutated,
     byte-for-byte Bind equivalence) with a strings.Contains token only.

Exit 0 = control is DEFECTIVE (at least one allegation substantiated in-set).
Exit 1 = control is SOUND.
"""
import json, os, re, sys

exchange = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
DISPATCH = "71ac079a557a687d"
full = [x for x in os.listdir(os.path.join(exchange, "dispatch"))
        if x.startswith(DISPATCH)][0]
bundle = os.path.join(exchange, "dispatch", full)
man = json.load(open(os.path.join(bundle, "manifest.json")))
body = json.loads(open(os.path.join(bundle, man["inputs"][0]["path"]),
                       errors="replace").read())
files = body["files"]
results = {}

# --- Allegation 1: packet anchor vs CHANGELOG's "acceptance_checks" ---------
changelog = files["CHANGELOG.md"]
anchor_keys = sorted((body.get("packet") or {}).keys())
results["packet_anchor_keys"] = anchor_keys
results["packet_anchor_has_acceptance_checks"] = "acceptance_checks" in anchor_keys
results["changelog_cites_packet_acceptance_checks"] = bool(re.search(
    r"the packet's own `acceptance_checks` names `code`, `placement-guards`, and `stalls-guards`",
    changelog))
# The CHANGELOG's own definition of what the change set's packet field is:
m = re.search(r"restores the full v2 packet-element anchor \(([^)]*)\)", changelog)
named = sorted(re.findall(r"`([a-z_]+)`", m.group(1))) if m else []
results["changelog_named_anchor_fields"] = named
# base_composition is a sibling top-level key, not a packet sub-field.
results["anchor_matches_changelog_definition"] = (
    sorted(k for k in named if k != "base_composition") == anchor_keys)
results["allegation_1_out_of_contract"] = (
    results["anchor_matches_changelog_definition"]
    and not results["packet_anchor_has_acceptance_checks"])

# --- Allegations 2-4: guards "prove" vs token-grep + local mirror -----------
GUARDS = {
    "prior": ("tools/standing-guards/placement-prior-stays-model-scoped/main.go",
              r"placement-prior-stays-model-scoped` proves a model-scoped observation[^;]*no declaration mutated",
              ["ProjectBackends"],
              ["input declarations are never mutated"],
              "func attachedPrior("),
    "degrade": ("tools/standing-guards/placement-degrades-to-declared-order/main.go",
                r"placement-degrades-to-declared-order` proves the default objective reproduces `scheduler\.Bind`'s own \(Rank, id\) order byte-for-byte",
                ["scheduler.Bind", "LoadOrEmpty"],
                ["declaredOrder is the byte-for-byte reproduction of scheduler.Bind's internal"],
                "func declaredOrder("),
    "objectives": ("tools/standing-guards/placement-objectives-stay-independent/main.go",
                   r"placement-objectives-stay-independent` proves the highest-quality and cheapest-acceptable objectives diverge[^;]*deterministically",
                   ["orderingFor", "ProjectBackends"],
                   ["case ObjectiveHighestQuality:", "sort.SliceStable(ranked"],
                   "func qualityLess("),
}

def import_block(src):
    m = re.search(r"(?s)import \((.*?)\)", src)
    return re.findall(r'"([^"]+)"', m.group(1)) if m else []

def calls(src, name):
    """Call expressions `name(` outside comments and string literals."""
    code = re.sub(r"//[^\n]*", "", src)
    code = re.sub(r'"(?:\\.|[^"\\])*"', '""', code)
    code = re.sub(r"`[^`]*`", "``", code)
    return len(re.findall(re.escape(name) + r"\(", code))

any_guard_defective = False
for key, (path, claim_re, machinery, tokens, mirror) in GUARDS.items():
    src = files[path]
    imports = import_block(src)
    r = {
        "changelog_claims_proves": bool(re.search(claim_re, changelog)),
        "imports": imports,
        "imports_only_stdlib": all("." not in i.split("/")[0] and "internal" not in i
                                   for i in imports),
        "machinery_call_counts": {n: calls(src, n.split(".")[-1]) for n in machinery},
        "checks_tokens_by_string_contains": all(
            ('"%s"' % t in src or "`%s`" % t in src) and "mustContain(" in src
            for t in tokens),
        "defines_local_mirror": mirror in src,
    }
    r["never_invokes_machinery"] = all(v == 0 for v in r["machinery_call_counts"].values())
    r["substantiated"] = (r["changelog_claims_proves"] and r["imports_only_stdlib"]
                          and r["never_invokes_machinery"]
                          and r["checks_tokens_by_string_contains"]
                          and r["defines_local_mirror"])
    any_guard_defective |= r["substantiated"]
    results["guard_" + key] = r

# Allegation 3 sub-claim: header "claims an unreadable-snapshot case no fixture
# provides". Recorded for the record; the header's oracle bullet lists exactly
# the two fixture cases, so this sub-claim is NOT counted toward defectiveness.
deg_src = files[GUARDS["degrade"][0]]
fx = json.loads(files["testdata/placement/degrades_to_declared_order.json"])
results["degrade_snapshot_fixture_cases"] = [c["name"] for c in fx["snapshot_cases"]]
results["degrade_header_mentions_unreadable"] = "unreadable" in deg_src
results["degrade_oracle_bullet_lists_only_absent_and_malformed"] = bool(re.search(
    r"snapshot-load oracle: an absent path and a malformed snapshot file", deg_src))
results["degrade_fixture_has_unreadable_case"] = any(
    "unreadable" in c["name"] for c in fx["snapshot_cases"])

defective = any_guard_defective
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND")
sys.exit(0 if defective else 1)
