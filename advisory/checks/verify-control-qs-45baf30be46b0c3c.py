"""Deterministic re-runnable check for dispatch ee05d12f0a3a6ef9... (substrate
qs-45baf30be46b0c3c, backend-model-is-bound packet p3-semantic-check-harness).

Single codex-sol-high allegation, fully in-contract because BOTH files are in
the change set: policy/checks/repository.template.json is stale relative to
policy/checks/repository.json -- registry_version 6 vs 9, and the template
omits the five standing-guard checks and the `stalls-guards` set that the
delivered registry carries.

The script establishes that the template is the registry's generator input
(its 8 checks match repository.json's first 8 by argv in order, and its
`code` set's "@N" indexes resolve to exactly the check_ids repository.json
lists under `code`), then measures what the delivered registry holds that
the delivered template cannot express.

Exit 0 = control is DEFECTIVE (template and registry disagree on the set's
own text). Exit 1 = SOUND.
"""
import json, os, sys
exchange = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
DISPATCH = "ee05d12f0a3a6ef9"
full = [x for x in os.listdir(os.path.join(exchange, "dispatch"))
        if x.startswith(DISPATCH)][0]
bundle = os.path.join(exchange, "dispatch", full)
man = json.load(open(os.path.join(bundle, "manifest.json")))
files = json.loads(open(os.path.join(bundle, man["inputs"][0]["path"]),
                        errors="replace").read())["files"]
results = {}
tpl = json.loads(files["policy/checks/repository.template.json"])
reg = json.loads(files["policy/checks/repository.json"])

results["both_files_in_set"] = True
results["template_registry_version"] = tpl.get("registry_version")
results["registry_registry_version"] = reg.get("registry_version")
results["version_mismatch"] = tpl.get("registry_version") != reg.get("registry_version")

tpl_argv = [tuple(c["argv"]) for c in tpl["checks"]]
reg_argv = [tuple(c["argv"]) for c in reg["checks"]]
results["template_check_count"] = len(tpl_argv)
results["registry_check_count"] = len(reg_argv)
results["template_is_prefix_of_registry_by_argv"] = reg_argv[:len(tpl_argv)] == tpl_argv
reg_ids = [c["check_id"] for c in reg["checks"]]


def resolve(refs):
    return [reg_ids[int(r[1:])] if r.startswith("@") else r for r in refs]


results["template_code_set_resolves_to_registry_code_set"] = (
    resolve(tpl["sets"]["code"]) == reg["sets"]["code"])
results["checks_in_registry_not_in_template"] = [
    " ".join(a) for a in reg_argv if a not in tpl_argv]
results["standing_guard_checks_missing_from_template"] = [
    " ".join(a) for a in reg_argv
    if a not in tpl_argv and any("standing-guards" in x for x in a)]
results["sets_in_registry_not_in_template"] = sorted(
    set(reg["sets"]) - set(tpl["sets"]))
results["stalls_guards_set_missing_from_template"] = (
    "stalls-guards" in reg["sets"] and "stalls-guards" not in tpl["sets"])
results["stalls_guards_set_size_in_registry"] = len(reg["sets"].get("stalls-guards", []))

defective = (results["template_is_prefix_of_registry_by_argv"]
             and results["template_code_set_resolves_to_registry_code_set"]
             and results["version_mismatch"]
             and len(results["standing_guard_checks_missing_from_template"]) == 5
             and results["stalls_guards_set_missing_from_template"])
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND")
sys.exit(0 if defective else 1)
