"""Deterministic re-runnable check for dispatch 614cac3616cf7fea... (substrate
qs-af9054a1808cceba, semantic-and-durable-closure / P01c-application-record-contract
change set).

Allegations under test (codex-sol-high refusal), all against
src/semantic_closure/model/application/application.go:

  A1  Record.Validate enforces no equality among duplicated bindings
      (movement.operation_key vs operation_key; product.linked/materialized
      _tree_hash vs the top-level pair; target_context.request_ref vs
      request_ref), so a contradictory record can be sealed and accepted.
  A2  ObjectPin.validate checks address only syntactically, never that it
      equals "sha256/" + content_hash, so one pin can name two blobs.
  A3  Validate accepts an empty content_hash although the schema and the
      catalog declare content_hash required; the runtime validator does not
      implement the declared contract.

What is checked, all from the change set's own files:
  * A1 premise: Validate contains no cross-field equality for any of the
    three pairs; the set's own validRecord() fixture seals with
    operation_key != movement.operation_key.
  * A1 contract side: no in-set text (schema, catalog, Go doc) states that
    any of those pairs must be equal.  Without that text the "contradiction"
    has only one side in the set -> reported as NEEDS-JUDGMENT, not scored.
  * A2 premise: ObjectPin.validate has no address == "sha256/"+content_hash
    comparison.
  * A2 contract side: the only in-set wording is "content-addressed" plus the
    address pattern ^sha256/<64hex>$; no text says address must equal
    sha256/content_hash -> NEEDS-JUDGMENT, not scored.
  * A3 premise: schema "required" lists content_hash; Validate guards the
    hash check with `r.ContentHash != ""`; the test names the case
    "malformed content_hash when set".
  * A3 defence: Validate is documented as structural; Seal calls Validate
    BEFORE computing the hash (so it must accept an unsealed builder);
    VerifyContentHash refuses an empty hash; ParseRecord = Validate +
    VerifyContentHash and is documented as refusing unsealed records; the
    catalog's own "required" line is "a self-referential content hash
    computed over the canonical record body", which ParseRecord enforces.
    A3 is a contradiction only if NO ingestion path in the set refuses an
    empty content_hash.
  * optional: if a `go` toolchain is on PATH the delivered package is
    compiled and the three runtime facts are probed directly; the probe
    must agree with the static reading or the script aborts.

The control is DEFECTIVE only if A3's contradiction holds (schema requires,
no in-set accept path enforces) or an in-set text requires equality for
A1/A2 while the validator omits the check.

Exit 0 = control is DEFECTIVE.  Exit 1 = control is SOUND.
"""
import json, os, re, shutil, subprocess, sys, tempfile
exchange = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
DISPATCH = "614cac3616cf7fea"
full = [x for x in os.listdir(os.path.join(exchange, "dispatch"))
        if x.startswith(DISPATCH)][0]
bundle = os.path.join(exchange, "dispatch", full)
man = json.load(open(os.path.join(bundle, "manifest.json")))
files = json.loads(open(os.path.join(bundle, man["inputs"][0]["path"]),
                        errors="replace").read())["files"]
results = {}

GO = "src/semantic_closure/model/application/application.go"
SCHEMA = "schemas/semantic-closure/application/application-record.schema.json"
CATALOG = "catalog/semantic-closure/application/application-record.yaml"
TEST = "tests/semantic-closure/model/application/application_test.go"
go, schema_txt, catalog, test = files[GO], files[SCHEMA], files[CATALOG], files[TEST]
schema = json.loads(schema_txt)
everything = "\n".join(files.values())

def func(signature):
    """Body of the Go func whose header starts with `func <signature>`."""
    return re.search(r"(?s)func %s.*?\n}\n" % re.escape(signature), go).group(0)

validate = func("(r Record) Validate()")
objpin = func("(o ObjectPin) validate(")
seal = func("Seal(")
verify = func("VerifyContentHash(")
parse = func("ParseRecord(")

# --- A1 -----------------------------------------------------------------
pairs = {
    "movement.operation_key_vs_operation_key":
        r"Movement\.OperationKey\s*[!=]=\s*r\.OperationKey|r\.OperationKey\s*[!=]=\s*r\.Movement\.OperationKey",
    "product.linked_tree_hash_vs_linked_tree_hash":
        r"Product\.LinkedTreeHash\s*[!=]=\s*r\.LinkedTreeHash|r\.LinkedTreeHash\s*[!=]=\s*r\.Product\.LinkedTreeHash",
    "product.materialized_tree_hash_vs_materialized_tree_hash":
        r"Product\.MaterializedTreeHash\s*[!=]=\s*r\.MaterializedTreeHash|r\.MaterializedTreeHash\s*[!=]=\s*r\.Product\.MaterializedTreeHash",
    "target_context.request_ref_vs_request_ref":
        r"TargetContext\.RequestRef\s*[!=]=\s*r\.RequestRef|r\.RequestRef\s*[!=]=\s*r\.TargetContext\.RequestRef",
}
results["A1_validate_compares_pair"] = {k: bool(re.search(v, go)) for k, v in pairs.items()}
results["A1_validator_enforces_no_pair"] = not any(results["A1_validate_compares_pair"].values())
fixture = re.search(r"(?s)func validRecord\(\).*?\n}\n", test).group(0)
top_key = re.search(r"\n\t\tOperationKey:\s*(\w+)", fixture).group(1)
mov_key = re.search(r"Movement: application\.MovementPin\{.*?OperationKey:\s*(\w+)", fixture, re.S).group(1)
results["A1_fixture_operation_key_vs_movement"] = {"operation_key": top_key, "movement.operation_key": mov_key}
results["A1_fixture_models_operation_keys_as_distinct"] = top_key != mov_key
# Contract side: does any in-set text require equality for these pairs?
equality_words = r"(must (be )?equal|must match|equal to|same as|mirror|identical|duplicate|agree with|consistent with)"
results["A1_in_set_text_requires_equality"] = bool(re.search(
    r"(?i)(operation_key|linked_tree_hash|materialized_tree_hash|request_ref)[^\n]{0,120}" + equality_words
    + r"|" + equality_words + r"[^\n]{0,120}(operation_key|linked_tree_hash|materialized_tree_hash|request_ref)",
    everything))
results["A1_status"] = ("NEEDS-JUDGMENT: validator omits the checks, but no in-set text "
                        "declares the pairs must agree; the fixture itself uses distinct "
                        "operation_key values")

# --- A2 -----------------------------------------------------------------
results["A2_objectpin_checks_address_equals_hash"] = bool(
    re.search(r'"sha256/"\s*\+\s*o\.ContentHash|o\.Address\s*!=\s*"sha256/"', objpin))
results["A2_objectpin_address_is_regex_only"] = "objectAddr.MatchString(o.Address)" in objpin
results["A2_schema_address_pattern"] = schema["$defs"]["objectPin"]["properties"]["address"].get("pattern")
results["A2_in_set_says_content_addressed"] = bool(re.search(r"content-addressed", go + schema_txt + catalog))
results["A2_in_set_text_requires_address_equals_hash"] = bool(re.search(
    r"(?i)address[^\n]{0,120}(equal|match|derived from|same)[^\n]{0,60}content_hash"
    r"|content_hash[^\n]{0,120}(equal|match|derived)[^\n]{0,60}address", everything))
results["A2_status"] = ("NEEDS-JUDGMENT: validator accepts address sha256/X with content_hash Y; "
                        "the requirement that they agree is implied by 'content-addressed' and the "
                        "sha256/<hash> form, not stated")

# --- A3 -----------------------------------------------------------------
results["A3_schema_requires_content_hash"] = "content_hash" in schema["required"]
results["A3_catalog_requires_self_hash"] = bool(
    re.search(r"a self-referential content hash computed over the canonical record body", catalog))
results["A3_validate_accepts_empty_content_hash"] = bool(
    re.search(r'r\.ContentHash != ""\s*&&\s*!hexHash\.MatchString\(r\.ContentHash\)', validate))
results["A3_test_names_case_when_set"] = '"malformed content_hash when set"' in test
results["A3_validate_doc_is_structural"] = bool(
    re.search(r"// Validate checks structural correctness of all record fields\.", go))
results["A3_seal_validates_before_hashing"] = (
    seal.index("r.Validate()") < seal.index("ComputeContentHash(r)"))
results["A3_verify_refuses_empty"] = 'if r.ContentHash == ""' in verify and "not sealed" in verify
results["A3_parse_calls_validate_then_verify"] = (
    "r.Validate()" in parse and "VerifyContentHash(r)" in parse
    and parse.index("r.Validate()") < parse.index("VerifyContentHash(r)"))
results["A3_parse_doc_refuses_unsealed"] = bool(
    re.search(r"// ParseRecord .*?verifies the mandatory\n// content hash .*?Refuses unsealed", go, re.S))
results["A3_test_parse_refuses_unsealed"] = "TestParseRecord_RefusesUnsealed" in test
results["A3_in_set_claims_validate_implements_schema"] = bool(
    re.search(r"(?i)Validate\b[^\n]{0,100}(schema|json schema)", go + catalog))
results["A3_contract_enforced_at_ingestion"] = (
    results["A3_verify_refuses_empty"] and results["A3_parse_calls_validate_then_verify"])

# --- optional runtime probe ------------------------------------------------
goexe = shutil.which("go") or (os.path.expanduser("~/.local/bin/go")
                               if os.path.exists(os.path.expanduser("~/.local/bin/go")) else None)
if goexe:
    tmp = tempfile.mkdtemp(prefix="verify-af9054a1-")
    for rel, content in files.items():
        p = os.path.join(tmp, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(content)
    open(os.path.join(tmp, "go.mod"), "w").write("module github.com/halbritt/striatum-next\ngo 1.22\n")
    probe = '''package application_test
import ("encoding/json"; "testing"
  "github.com/halbritt/striatum-next/src/semantic_closure/model/application")
func TestCaplabProbe(t *testing.T) {
  r := validRecord()
  r.Movement.OperationKey = testHashG; r.Product.LinkedTreeHash = testHashG
  r.Product.MaterializedTreeHash = testHashG; r.TargetContext.RequestRef = 41
  if _, err := application.Seal(r); err == nil { t.Log("PROBE A1 seal-accepts-contradictory-pairs") }
  r = validRecord(); r.TargetContext.ProjectionObject.Address = "sha256/" + testHashG
  if _, err := application.Seal(r); err == nil { t.Log("PROBE A2 seal-accepts-mismatched-object-pin") }
  r = validRecord(); r.ContentHash = ""
  if err := r.Validate(); err == nil { t.Log("PROBE A3 validate-accepts-empty-hash") }
  b, _ := json.Marshal(r)
  if _, err := application.ParseRecord(b); err != nil { t.Log("PROBE A3 parse-refuses-empty-hash") }
}
'''
    open(os.path.join(tmp, os.path.dirname(TEST), "caplab_probe_test.go"), "w").write(probe)
    out = subprocess.run([goexe, "test", "./tests/...", "-run", "TestCaplabProbe|Test", "-v"],
                         cwd=tmp, capture_output=True, text=True,
                         env={**os.environ, "GOFLAGS": "-mod=mod", "GOTOOLCHAIN": "local"})
    probes = sorted(set(re.findall(r"PROBE (A\d \S+)", out.stdout)))
    results["go_probe"] = {"ok": out.returncode == 0, "delivered_tests_pass": "\nok " in out.stdout or out.stdout.startswith("ok "),
                           "observed": probes}
    shutil.rmtree(tmp, ignore_errors=True)
    expected = {"A1 seal-accepts-contradictory-pairs", "A2 seal-accepts-mismatched-object-pin",
                "A3 validate-accepts-empty-hash", "A3 parse-refuses-empty-hash"}
    if out.returncode == 0 and set(probes) != expected:
        print(json.dumps(results, indent=2, sort_keys=True))
        print("ABORT: go probe disagrees with static reading", file=sys.stderr)
        sys.exit(2)
else:
    results["go_probe"] = "skipped: no go toolchain on PATH"

# --- verdict ---------------------------------------------------------------
a3_contradiction = (results["A3_schema_requires_content_hash"]
                    and results["A3_validate_accepts_empty_content_hash"]
                    and (not results["A3_contract_enforced_at_ingestion"]
                         or results["A3_in_set_claims_validate_implements_schema"]))
a1_contradiction = results["A1_validator_enforces_no_pair"] and results["A1_in_set_text_requires_equality"]
a2_contradiction = (not results["A2_objectpin_checks_address_equals_hash"]
                    and results["A2_in_set_text_requires_address_equals_hash"])
defective = a3_contradiction or a1_contradiction or a2_contradiction
results["control_is_defective"] = defective
results["needs_judgment"] = [k for k, v in (("A1", not a1_contradiction and results["A1_validator_enforces_no_pair"]),
                                            ("A2", not a2_contradiction and not results["A2_objectpin_checks_address_equals_hash"]))
                             if v]
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND (A1, A2 flagged NEEDS-JUDGMENT)")
sys.exit(0 if defective else 1)
