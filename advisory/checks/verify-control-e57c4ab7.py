"""Deterministic re-runnable check for dispatch e57c4ab7...: two claims the
change set makes about itself that its own files contradict."""
import json, os, re, sys
exchange = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
DISPATCH = "e57c4ab70e2b4c8e"
full = [x for x in os.listdir(os.path.join(exchange, "dispatch"))
        if x.startswith(DISPATCH)][0]
bundle = os.path.join(exchange, "dispatch", full)
man = json.load(open(os.path.join(bundle, "manifest.json")))
files = json.loads(open(os.path.join(bundle, man["inputs"][0]["path"]),
                        errors="replace").read())["files"]
results = {}
# Check 1: README claims schema validation; the test loads no schema.
readme = next(c for n, c in files.items()
              if n.endswith("refusal/README.md")
              and "schema_validation_test.go" in c)
test = next(c for n, c in files.items() if n.endswith("schema_validation_test.go"))
results["readme_claims_schema_validation"] = bool(
    re.search(r"`schema_validation_test\.go`:\s*Validates[^\n]*schema",
              readme, re.I))
results["test_loads_schema_file"] = ".schema.json" in test
results["test_uses_schema_library"] = bool(
    re.search(r"jsonschema|santhosh|xeipuuv", test))
# Check 2: schema requires subject_identity; the id hash omits it.
schema = next(json.loads(c) for n, c in files.items()
              if n.endswith(".schema.json")
              and "subject_identity" in c)
required = (schema.get("properties", {}).get("contextual_identity", {})
            .get("required", []))
results["schema_requires_subject_identity"] = "subject_identity" in required
hashers = [c for n, c in files.items()
           if re.search(r"def compute_refusal_id", c)]
results["hashers_found"] = len(hashers)
results["any_hasher_uses_subject_identity"] = any(
    "subject_identity" in re.search(r"(?s)def compute_refusal_id.{0,700}", c).group(0)
    for c in hashers)
defective = (results["readme_claims_schema_validation"]
             and not results["test_loads_schema_file"]
             and not results["test_uses_schema_library"]) or (
    results["schema_requires_subject_identity"]
    and not results["any_hasher_uses_subject_identity"])
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
sys.exit(0 if defective else 1)
