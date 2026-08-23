"""Deterministic re-runnable check for dispatch 6595e5ae...: the two
codex-sol-high refusal allegations against control qs-c70d14e4ac76d99c
(agy-lane-is-robust / scheduler-qualification-withholding-network), tested
against the change set's OWN files only.

Allegation 1 — "Bind never calls Admit/AdmitRun, so withheld roles can still
  be bound and dispatched, contradicting documented pre-dispatch admission."
  The bare fact is true in-set, but the change set states it itself
  (qualification.go: "changes no behavior of Bind or Decide"; design.md: the
  admission surface is "a distinct, earlier gate"; scheduler.go: the scheduler
  is "a pure library the Driver invokes"). Whether the Driver sequences
  AdmitRun before Bind lives in internal/driver, which is NOT in the set —
  out-of-contract. Not a mechanical in-set contradiction.

Allegation 2 — "Authorize matches only backend and role; never validates
  endpoint or credential scope." Mechanically true in-set; whether that
  contradicts the policy/design prose ("authorizes that backend, endpoint,
  and credential scope for the role") turns on whether the grant is meant to
  *assign* the endpoint/scope (the code's model) or *match* a declared one
  (the reviewer's model). The scheduler-facing Declaration carries no
  endpoint/scope field to match against. NEEDS-JUDGMENT; recorded, not
  counted as defective here.

Exit 0 = control is DEFECTIVE (a mechanical in-set contradiction was found).
Exit 1 = SOUND on mechanically settleable grounds (allegation 2 still needs a
human reading)."""
import json, os, re, sys
exchange = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
DISPATCH = "6595e5ae0b4ff5a8"
full = [x for x in os.listdir(os.path.join(exchange, "dispatch"))
        if x.startswith(DISPATCH)][0]
bundle = os.path.join(exchange, "dispatch", full)
man = json.load(open(os.path.join(bundle, "manifest.json")))
body = json.loads(open(os.path.join(bundle, man["inputs"][0]["path"]),
                       errors="replace").read())
files = body["files"]
results = {"files_in_set": sorted(files)}

sched = files["internal/scheduler/scheduler.go"]
qual = files["internal/scheduler/qualification.go"]
design = files["rfcs/0008-scheduler-and-capacity-policy/design.md"]
policy = files["policy/scheduler.yaml"]

# ---- Allegation 1: Bind never calls Admit / AdmitRun -----------------------
bind_body = re.search(r"(?s)func Bind\(.*?\n}\n", sched).group(0)
results["a1_bind_calls_admit"] = bool(re.search(r"\bAdmit(Run)?\(", bind_body))
results["a1_scheduler_go_mentions_admit_anywhere"] = bool(
    re.search(r"\bAdmit(Run)?\(", sched))
results["a1_qualification_disclaims_bind_change"] = bool(re.search(
    r"it changes no\s+(//\s*)?behavior of Bind or Decide", qual))
results["a1_design_calls_admission_distinct_earlier_gate"] = (
    "A distinct, earlier gate decides whether a backend is *eligible at all*"
    in design)
results["a1_design_says_withholding_is_pre_dispatch"] = (
    "A withholding is a **pre-dispatch** refusal of admission" in design)
results["a1_scheduler_is_driver_invoked_library"] = (
    "a pure library the\n// Driver invokes" in sched)
results["a1_driver_package_in_set"] = any(
    n.startswith("internal/driver/") for n in files)
results["a1_test_asserts_bind_unchanged"] = (
    "TestBindUnaffectedByQualificationFields"
    in files["internal/scheduler/qualification_test.go"])
# A contradiction would need the set to claim Bind itself admits. It does not:
# it disclaims that and places the call in the (out-of-set) Driver.
results["a1_in_set_contradiction"] = (
    results["a1_bind_calls_admit"] is False
    and not results["a1_qualification_disclaims_bind_change"])
results["a1_verdict"] = ("OUT-OF-CONTRACT (fact true and self-stated; "
                         "consequence depends on internal/driver, not in set)")

# ---- Allegation 2: Authorize ignores endpoint / credential scope -----------
auth_fn = re.search(r"(?s)func \(a VendorAuthorization\) Authorize\((.*?)\).*?\n}\n",
                    qual)
results["a2_authorize_params"] = auth_fn.group(1).strip()
results["a2_authorize_compares_endpoint_or_scope"] = bool(
    re.search(r"\.(Endpoint|CredentialScope)\s*==", auth_fn.group(0)))
results["a2_any_endpoint_scope_comparison_in_qualification_go"] = bool(
    re.search(r"\.(Endpoint|CredentialScope)\s*[=!]=", qual))
decl_struct = re.search(r"(?s)type Declaration struct \{.*?\n}\n", sched).group(0)
results["a2_declaration_has_endpoint_or_scope_field"] = bool(
    re.search(r"\n\s+(Endpoint|CredentialScope|RequiredEndpoint)\s", decl_struct))
results["a2_policy_claims_backend_endpoint_scope_authorized"] = (
    "a grant below authorizes that backend, endpoint, and credential scope\n"
    "  # for the role" in policy)
results["a2_qualification_header_claims_endpoint_scope_role"] = (
    "the vendor endpoint, credential scope, and role a vendor-endpoint-only\n"
    "//     backend reaches are authorized by policy/scheduler.yaml" in qual)
results["a2_design_says_grant_is_tuple_assigned_by_policy"] = (
    "this block only grants a `{backend, endpoint, credential_scope, roles}` tuple"
    in design)
results["a2_design_says_vendor_unauthorized_keyed_on_backend_and_role"] = (
    "not authorized by `vendor_authorization` for this backend and role" in design)
results["a2_verdict"] = ("NEEDS-JUDGMENT (code matches (backend, role) only; "
                         "prose names endpoint+scope; no in-set declared "
                         "endpoint/scope exists to mismatch against)")

defective = bool(results["a1_in_set_contradiction"])
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else
      "SOUND (mechanical); allegation 2 NEEDS-JUDGMENT")
sys.exit(0 if defective else 1)
