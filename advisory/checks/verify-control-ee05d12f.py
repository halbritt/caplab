"""Deterministic re-runnable check for dispatch ee05d12f...: the change set
ships a checks template that contradicts the registry it generates.

The change set delivers both `policy/checks/repository.template.json` and
`policy/checks/repository.json`, and striatum-next's own tooling documents
the template as the source that generates the registry
(`tools/checkreg/main.go`: `checkreg -template repository.template.json >
repository.json`). The shipped template is registry_version 6 with 8 checks
and 2 sets; the shipped registry is version 9 with 13 checks and 23 sets,
including a `stalls-guards` set whose five check ids the template does not
contain. Regenerating from the shipped template would silently drop the
standing guard checks and roll the registry back three versions."""
import json
import os
import sys

exchange = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
DISPATCH = "ee05d12f0a3a6ef9"
full = [x for x in os.listdir(os.path.join(exchange, "dispatch"))
        if x.startswith(DISPATCH)][0]
bundle = os.path.join(exchange, "dispatch", full)
man = json.load(open(os.path.join(bundle, "manifest.json")))
files = json.loads(open(os.path.join(bundle, man["inputs"][0]["path"]),
                        errors="replace").read())["files"]
template = json.loads(files["policy/checks/repository.template.json"])
registry = json.loads(files["policy/checks/repository.json"])
results = {
    "template_registry_version": template.get("registry_version"),
    "registry_registry_version": registry.get("registry_version"),
    "template_checks": len(template.get("checks") or []),
    "registry_checks": len(registry.get("checks") or []),
    "template_sets": len(template.get("sets") or {}),
    "registry_sets": len(registry.get("sets") or {}),
    "registry_has_stalls_guards": "stalls-guards" in (registry.get("sets") or {}),
    "template_has_stalls_guards": "stalls-guards" in (template.get("sets") or {}),
}
template_check_ids = {c.get("check_id") or c.get("id")
                      for c in template.get("checks") or []}
guard_ids = (registry.get("sets") or {}).get("stalls-guards") or []
results["stalls_guard_checks"] = len(guard_ids)
results["stalls_guard_checks_missing_from_template"] = sum(
    1 for check_id in guard_ids if check_id not in template_check_ids)
defective = (
    results["template_registry_version"] != results["registry_registry_version"]
    and results["registry_has_stalls_guards"]
    and not results["template_has_stalls_guards"]
    and results["stalls_guard_checks_missing_from_template"]
    == results["stalls_guard_checks"] > 0)
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
sys.exit(0 if defective else 1)
