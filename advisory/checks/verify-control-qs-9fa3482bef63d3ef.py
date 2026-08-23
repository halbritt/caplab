"""Deterministic re-runnable check for dispatch c778cba8...: the three
codex-sol-high refusal allegations against control qs-9fa3482bef63d3ef
(stalls-need-no-judgment-c change set), tested against the change set's OWN
content only.

Allegation 1 — base.product_identity and base.content_hash are both empty.
  In-set fact (the change set states no base pin at all; packet fields are
  empty too). SUBSTANTIATED as a fact of the artifact; whether that blocks
  integration is the exchange's rule, noted but not needed.

Allegation 2 — policy/checks/repository.json names eight standing-guard
  entrypoints whose sources are not in the delivered files. True as a count,
  but the registry is a whole-file replacement and the set's own reference.md
  calls five of them "the five prior guards" of "the existing stalls-guards
  packet-acceptance set"; whether they exist in the base tree is out of set.
  OUT-OF-CONTRACT.

Allegation 3 — BoundsExhausted.MarshalJSON omits dedupe_key while
  docs/stalls-need-no-judgment/reference.md lists dedupe_key as a common
  Bounds-Exhausted record field. Both sides are in-set. SUBSTANTIATED.
  (Nuance, also in-set: the planner/close and admission seams build their own
  records that DO carry dedupe_key; the escalations package's self-described
  "registered record shape" is the one that omits it.)

Exit 0 = control is DEFECTIVE. Exit 1 = SOUND."""
import json, os, re, sys
exchange = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
DISPATCH = "c778cba8b60583e9"
full = [x for x in os.listdir(os.path.join(exchange, "dispatch"))
        if x.startswith(DISPATCH)][0]
bundle = os.path.join(exchange, "dispatch", full)
man = json.load(open(os.path.join(bundle, "manifest.json")))
body = json.loads(open(os.path.join(bundle, man["inputs"][0]["path"]),
                       errors="replace").read())
files = body["files"]
results = {}

# ---- Allegation 1: empty base pin -----------------------------------------
base = body.get("base", {})
results["a1_base"] = base
results["a1_packet"] = body.get("packet")
results["a1_base_product_identity_empty"] = base.get("product_identity", "") == ""
results["a1_base_content_hash_empty"] = base.get("content_hash", "") == ""
results["a1_result_tree_hash_present"] = bool(body.get("result_tree_hash"))
results["a1_substantiated"] = (results["a1_base_product_identity_empty"]
                               and results["a1_base_content_hash_empty"])

# ---- Allegation 2: registry entrypoints absent from the delivered files ----
reg = json.loads(files["policy/checks/repository.json"])
named = sorted({a[2:] for c in reg["checks"] for a in c["argv"]
                if a.startswith("./tools/")})
missing = [p for p in named if p + "/main.go" not in files]
present = [p for p in named if p + "/main.go" in files]
results["a2_registry_tool_entrypoints"] = named
results["a2_entrypoints_in_set"] = present
results["a2_entrypoints_not_in_set"] = missing
results["a2_missing_count"] = len(missing)
ref = files["docs/stalls-need-no-judgment/reference.md"]
results["a2_reference_calls_five_guards_prior_existing"] = (
    "The existing `stalls-guards` packet-acceptance set remains available and\n"
    "unchanged. It carries the five prior guards" in ref)
results["a2_base_tree_in_set"] = False  # a change set is a delta; no tree
results["a2_verdict"] = ("OUT-OF-CONTRACT (8 entrypoints absent from the delta; "
                         "existence is a base-tree question; reference.md "
                         "labels five as prior/existing)")

# ---- Allegation 3: dedupe_key missing from BoundsExhausted.MarshalJSON ----
ctor = files["internal/escalations/escalation_constructor.go"]
bounds_section = re.search(
    r"(?s)## Bounds-Exhausted Record.*?(?=\n## )", ref).group(0)
results["a3_reference_lists_dedupe_key_common_field"] = bool(
    re.search(r"\| `dedupe_key` \| Stable key equal to the escalation identity \|",
              bounds_section))
marshal = re.search(r"(?s)func \(e BoundsExhausted\) MarshalJSON\(\).*?\n}\n",
                    ctor).group(0)
emitted = re.findall(r'json:"([a-z_]+)"', marshal)
results["a3_marshaljson_emitted_fields"] = emitted
results["a3_marshaljson_emits_dedupe_key"] = "dedupe_key" in emitted
results["a3_marshaljson_self_describes_registered_shape"] = (
    "MarshalJSON emits the registered record shape" in ctor)
results["a3_dedupekey_method_exists_but_unserialized"] = (
    "func (e BoundsExhausted) DedupeKey() string" in ctor)
# Nuance: other in-set writers do emit dedupe_key with their own shapes.
results["a3_close_seam_record_has_dedupe_key"] = (
    'DedupeKey     string        `json:"dedupe_key"`'
    in files["internal/planner/close/stall_totality.go"])
results["a3_admission_record_has_dedupe_key"] = (
    '`json:"dedupe_key"`' in files["internal/admission/oscillation.go"])
results["a3_substantiated"] = (
    results["a3_reference_lists_dedupe_key_common_field"]
    and not results["a3_marshaljson_emits_dedupe_key"])

defective = results["a3_substantiated"] or results["a1_substantiated"]
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND")
sys.exit(0 if defective else 1)
