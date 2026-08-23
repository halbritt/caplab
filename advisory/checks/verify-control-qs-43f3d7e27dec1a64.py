"""Deterministic re-runnable check for dispatch 1c9196ec53a203d1... (substrate
qs-43f3d7e27dec1a64, the capability-aware-placement guards product artifact).

Tests the codex-sol-high allegations against the change set's OWN content:

  A1  CHANGELOG "Unreleased" says this build "restores the full v2
      packet-element anchor (work_graph_identity, work_graph_version_hash,
      packet_anchor, packet_element_hash, base_composition)"; the envelope
      must actually carry them.                                  [in-contract]
  A2  CHANGELOG says "the packet's own acceptance_checks names code,
      placement-guards, stalls-guards". The envelope has no such field, but
      the claim is about the packet element, which is not in the set ->
      recorded, NOT used for the verdict (see report).           [judgment]
  A3-A5  CHANGELOG says each guard "proves" properties of ProjectBackends /
      scheduler.Bind / LoadOrEmpty / orderingFor; each guard must then
      actually import or invoke that machinery rather than grep tokens out
      of the source file and exercise a local mirror.            [in-contract]

Exit 0 = control is DEFECTIVE (at least one in-contract allegation holds on
the set's own text). Exit 1 = SOUND.
"""
import json, os, re, sys
exchange = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
DISPATCH = "1c9196ec53a203d1"
full = [x for x in os.listdir(os.path.join(exchange, "dispatch"))
        if x.startswith(DISPATCH)][0]
bundle = os.path.join(exchange, "dispatch", full)
man = json.load(open(os.path.join(bundle, "manifest.json")))
cs = json.loads(open(os.path.join(bundle, man["inputs"][0]["path"]),
                     errors="replace").read())
files = cs["files"]
results = {}

changelog = files["CHANGELOG.md"]
unreleased = changelog.split("\n## ", 2)[1] if "\n## Unreleased" in changelog else ""
results["changelog_has_unreleased_section"] = unreleased.startswith("Unreleased")

# --- A1: v2 packet-element anchor claimed vs envelope ---------------------
V2_FIELDS = ["work_graph_identity", "work_graph_version_hash", "packet_anchor",
             "packet_element_hash", "base_composition"]
results["changelog_claims_v2_anchor_restored"] = bool(re.search(
    r"restores the full v2 packet-element anchor \(`work_graph_identity`, "
    r"`work_graph_version_hash`, `packet_anchor`, `packet_element_hash`, "
    r"`base_composition`\)", unreleased))
results["envelope_schema_version"] = cs.get("schema_version")
results["envelope_top_level_keys"] = sorted(cs.keys())
blob = json.dumps({k: v for k, v in cs.items() if k != "files"})
results["v2_fields_present_in_envelope"] = [f for f in V2_FIELDS if f in blob]
results["envelope_has_packet_pin"] = "packet" in cs
results["envelope_has_base_pin"] = "base" in cs
a1 = (results["changelog_claims_v2_anchor_restored"]
      and not results["v2_fields_present_in_envelope"]
      and not results["envelope_has_packet_pin"])
results["A1_substantiated"] = a1

# --- A2: acceptance_checks (recorded only; claim is about the packet) -----
results["changelog_claims_packet_acceptance_checks"] = bool(re.search(
    r"packet's own `acceptance_checks` names `code`, `placement-guards`, "
    r"and `stalls-guards`", unreleased))
results["acceptance_checks_anywhere_in_envelope"] = "acceptance_checks" in blob
results["A2_note"] = ("claim is about the packet element, which is not in the "
                      "change set; not counted toward the verdict")

# --- A3-A5: guards grep tokens + run local mirrors, never call machinery --
STDLIB = {"encoding/json", "fmt", "os", "path/filepath", "sort", "strings"}
GUARDS = {
    "A3": ("tools/standing-guards/placement-prior-stays-model-scoped/main.go",
           r"proves a model-scoped observation priors every tuple",
           ["ProjectBackends"], r"func attachedPrior\("),
    "A4": ("tools/standing-guards/placement-degrades-to-declared-order/main.go",
           r"proves the default objective reproduces `scheduler\.Bind`'s own "
           r"\(Rank, id\) order byte-for-byte",
           ["scheduler.Bind", "observations.LoadOrEmpty"],
           r"func declaredOrder\(|func snapshotObservationCount\("),
    "A5": ("tools/standing-guards/placement-objectives-stay-independent/main.go",
           r"proves the highest-quality and cheapest-acceptable objectives diverge",
           ["orderingFor", "ProjectBackends"], r"func qualityLess\(|func costLess\("),
}
for tag, (path, claim_re, machinery, mirror_re) in GUARDS.items():
    src = files[path]
    imports = re.search(r"(?s)import \((.*?)\)", src).group(1)
    imported = re.findall(r'"([^"]+)"', imports)
    r = {
        "changelog_claims_proof": bool(re.search(claim_re, unreleased)),
        "imports": imported,
        "imports_any_internal_package": any(
            p not in STDLIB for p in imported),
        "greps_machinery_tokens": "mustContain(" in src and "strings.Contains(s, t)" in src,
        "has_local_mirror_function": bool(re.search(mirror_re, src)),
        "mirror_self_described": bool(re.search(r"//\s*\w+ mirrors internal/", src)),
        "machinery_symbols_only_in_comments_or_strings": all(
            not re.search(r"(?m)^[^/\"\n]*\b" + re.escape(m.split(".")[-1]) + r"\(",
                          src) for m in machinery),
    }
    r["substantiated"] = (r["changelog_claims_proof"]
                          and not r["imports_any_internal_package"]
                          and r["greps_machinery_tokens"]
                          and r["has_local_mirror_function"]
                          and r["machinery_symbols_only_in_comments_or_strings"])
    results[tag + "_" + os.path.basename(os.path.dirname(path))] = r

guard_defects = [k for k, v in results.items()
                 if isinstance(v, dict) and v.get("substantiated")]
defective = a1 or bool(guard_defects)
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND",
      "(A1=%s; guards=%s)" % (a1, guard_defects))
sys.exit(0 if defective else 1)
