"""Deterministic re-runnable check for control qs-42bc0f9e052bfa57
(agy-role-obligation-declaration change set, dispatch 24478236...).

Allegation (flash + pro, same substance): the RFC addendum's Motivation and
backend.yaml's header assert IN PRESENT TENSE that "the scheduler, the
adapter/supervisor, and the admission seal all read this table", while the
delivered files contain no reader and the same document's Compatibility
section says the two declaration readers "surface the field in a later
change-set". Alleged: in-set internal contradiction.

The tension is wholly in-set, but its resolution follows the recorded
2026-08-23 rulings (spec-voice vs behavioral claim; docs that disclose are
not hiding — qs-d79e9a1668416a7d, qs-6ebd7c87): the document is an RFC
schema addendum whose present tense is the normative contract ("must be
decided from a declaration ... design C1, C3"), the Compatibility section
explicitly and adjacently discloses that the readers land in a later
change-set, and the declaration withholds every role and forbids every pass
type, so no live behavior can be misrepresented by the gap.

This oracle encodes the RULED READING (spec-voice + honest disclosure =
sound): defective iff the present-tense reader claim exists AND the set
neither delivers a reader NOR discloses the deferral. The alternative
strict reading (present tense = current-behavior claim, contradiction
regardless of disclosure) would flip the verdict; that reading is recorded
here, not encoded.

Exit 0 = control is DEFECTIVE. Exit 1 = sound under the ruled reading.
"""
import hashlib, json, os, re, sys

PATH = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325/"
    "dispatch/24478236c84b8699d1017f7aa92873c3a6a97ca2ec6e026097bccdca173e0dcf/"
    "inputs/00-striatum-next-passes-agy-lane-is-robust-change-set")
SHA256 = "42bc0f9e052bfa5753dd81eee577b96a6586804ecb0c052ca43e2494b24ccf92"

raw = open(PATH, "rb").read()
assert hashlib.sha256(raw).hexdigest() == SHA256, "substrate body hash mismatch"
cs = json.loads(raw)
files = cs["files"]
results = {"sha256_verified": True, "files_in_set": sorted(files)}
yaml_body = files["backends/agy/backend.yaml"]
md = files["rfcs/0007-agent-runtimes-and-execution-backends/"
           "role-obligation-coverage.md"]

# The contested present-tense claims.
results["yaml_header_reader_claim"] = bool(re.search(
    r"the scheduler, adapter, and admission seal\s*#? ?read the pass-type "
    r"support lists and the role_obligation_coverage table", yaml_body.replace("\n# ", " ")))
results["md_motivation_reader_claim"] = bool(re.search(
    r"The scheduler \(admission/withholding\), the adapter/supervisor "
    r"\(collect/commit\), and the admission seal all read this table\.", md))

# No reader implementation is in the set.
results["go_files_in_set"] = [n for n in files if n.endswith(".go")]

# The in-set disclosure that the readers land later.
results["compatibility_disclosure"] = bool(re.search(
    r"The two hand-rolled declaration readers \(`internal/backend/llm/"
    r"config\.go`,\s*`internal/driver/catalog\.go`\) surface the field in a "
    r"later change-set", md))

# The declaration ships fail-closed: nothing is qualified, so no live
# behavior exists for the spec sentence to misdescribe.
results["all_roles_withheld"] = (
    yaml_body.count("withheld: true") == 3
    and "supported_pass_types: []" in yaml_body)

results["out_of_contract"] = [
    "whether the scheduler/adapter/seal in the production tree read the "
    "table (their code is outside the set)",
    "whether the packet owed reader wiring (work-graph body not in set)",
]
results["contract_reading_encoded"] = (
    "spec-voice + adjacent Compatibility disclosure + fully-withheld "
    "declaration = sound (per the 2026-08-23 principal rulings); the strict "
    "present-tense-as-behavior reading would score this defective")

claim = (results["yaml_header_reader_claim"]
         or results["md_motivation_reader_claim"])
defective = claim and not results["go_files_in_set"] \
    and not results["compatibility_disclosure"]
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else
      "SOUND under the ruled spec-voice/disclosure reading")
sys.exit(0 if defective else 1)
