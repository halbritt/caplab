"""Deterministic re-runnable check for dispatch 8dca0ebcc322e399... (substrate
qs-6ebd7c873056feb1, p3-terminal-detector change set).

Allegation under test (codex-sol-high refusal): the documentation claims
Diagnostic retains the RAW provider text / machine discriminators and can
reproduce the classification, but newDiagnostic passes all three strings through
redactProviderText (control chars -> space, truncate to 1024 runes), so the
delivered behaviour differs from the documented one.

What is checked, all from the change set's own files:
  * the docs do use the "RETAINS the raw provider text" wording           (premise)
  * newDiagnostic does route all three vendor strings via redactProviderText (premise)
  * redactProviderText does strip control chars and truncate to 1024 runes   (premise)
  * the SAME Diagnostic type doc, the struct field doc, the newDiagnostic doc,
    the Payload doc and the package-level constant doc all state that the
    retained text is control-stripped and length-bounded at mint time; and a
    test in the set asserts exactly that behaviour.                       (defence)
  * "can reproduce the classification" depends on taxonomy.Classify, which is
    NOT in the change set -> out of contract, reported but not scored.

The allegation is substantiated only if the docs claim raw retention AND the
code transforms AND the docs nowhere disclose the transformation.

Exit 0 = control is DEFECTIVE.  Exit 1 = control is SOUND.
"""
import json, os, re, sys
exchange = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
DISPATCH = "8dca0ebcc322e399"
full = [x for x in os.listdir(os.path.join(exchange, "dispatch"))
        if x.startswith(DISPATCH)][0]
bundle = os.path.join(exchange, "dispatch", full)
man = json.load(open(os.path.join(bundle, "manifest.json")))
files = json.loads(open(os.path.join(bundle, man["inputs"][0]["path"]),
                        errors="replace").read())["files"]
results = {}

diag = next(c for n, c in files.items() if n.endswith("exhaustion/diagnostic.go"))
tests = "\n".join(c for n, c in files.items() if n.endswith("_test.go"))

# --- premises -------------------------------------------------------------
results["docs_say_retains_raw_provider_text"] = bool(
    re.search(r"RETAINS the raw provider text", diag))
new_diag = re.search(r"(?s)func newDiagnostic\(.*?\n}\n", diag).group(0)
results["newDiagnostic_redacts_all_three_strings"] = all(
    f"{f}: " in new_diag and f"redactProviderText(signal.Response.{f})" in new_diag
    for f in ("ProviderErrorCode", "ProviderErrorType", "Message"))
redact = re.search(r"(?s)func redactProviderText\(.*?\n}\n", diag).group(0)
results["redact_strips_control_chars"] = "unicode.IsControl(r)" in redact
results["redact_truncates_to_1024_runes"] = (
    "runes[:maxDiagnosticMessageRunes]" in redact
    and bool(re.search(r"maxDiagnosticMessageRunes\s*=\s*1024", diag)))

# --- defence: does the documentation itself disclose the transformation? ---
type_doc = re.search(r"(?s)// Diagnostic is the sensitive record.*?\ntype Diagnostic struct", diag).group(0)
results["type_doc_discloses_strip_and_bound"] = (
    "control-stripped and" in type_doc and "length-bounded at mint time" in type_doc
    and "redactProviderText" in type_doc)
struct_body = re.search(r"(?s)type Diagnostic struct \{.*?\n}\n", diag).group(0)
results["field_doc_discloses_strip_and_bound"] = bool(
    re.search(r"control-stripped and length-bounded at mint", struct_body))
results["newDiagnostic_doc_discloses"] = bool(
    re.search(r"(?s)// newDiagnostic.*?control-stripped and length-bounded.*?\nfunc newDiagnostic", diag))
results["payload_doc_discloses"] = bool(
    re.search(r"(?s)// Payload projects.*?already control-stripped and bounded.*?\nfunc \(d Diagnostic\) Payload", diag))
results["const_doc_discloses"] = bool(
    re.search(r"(?s)// maxDiagnosticMessageRunes bounds.*?control-character-stripped and length-bounded.*?\nconst maxDiagnosticMessageRunes", diag))
results["test_asserts_strip_and_bound"] = (
    "TestInterceptSanitizesRetainedProviderText" in tests
    and "> 1024" in tests and "r < 0x20 || r == 0x7f" in tests)
results["docs_claim_verbatim_or_byte_exact"] = bool(
    re.search(r"verbatim|byte-exact|byte-for-byte|unmodified|untouched",
              "\n".join(c for n, c in files.items() if not n.endswith("_test.go")), re.I))

# --- out of contract ------------------------------------------------------
results["taxonomy_Classify_in_change_set"] = any(
    re.search(r"func Classify\(", c) for c in files.values())
results["note_reproduce_classification"] = (
    "OUT-OF-CONTRACT: whether the redacted discriminators suffice to reproduce "
    "taxonomy.Classify is decided by internal/execution/taxonomy, absent from the set")

disclosed = (results["type_doc_discloses_strip_and_bound"]
             and results["field_doc_discloses_strip_and_bound"]
             and results["newDiagnostic_doc_discloses"])
defective = (results["docs_say_retains_raw_provider_text"]
             and results["newDiagnostic_redacts_all_three_strings"]
             and results["redact_strips_control_chars"]
             and results["redact_truncates_to_1024_runes"]
             and (not disclosed or results["docs_claim_verbatim_or_byte_exact"]))
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND")
sys.exit(0 if defective else 1)
