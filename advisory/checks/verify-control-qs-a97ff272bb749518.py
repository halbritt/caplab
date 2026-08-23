"""Deterministic re-runnable check for control qs-a97ff272bb749518
(decision record D0009 — Provenance Ledger and Artifact Store).

Allegations (deepseek v4 flash + pro): (1) the declared implementation pin
`c005567787cb3486` no longer matches rfcs/0009-.../implementation.md (which
now hashes 5ba060d4...); (2) D0009.C5 declares "the registry began with 33 v1
types" while catalog/ledger-record-types/ holds 34 (and design.md's own table
lists 34); (3) D0009.C9 claims embedded per-store transactional cursors and
`reconcile --migrate`, both deferred in the shipped implementation.

In-set adjudication: all three allegations resolve against out-of-set content
— the RFC documents, the catalog directory, and the shipped Go implementation
live in the base tree, not in this single-document set. OUT-OF-CONTRACT by the
audit standard; recorded, never scored. (A pin going stale when its cited
document later moves is moreover the documented degrade-gracefully behavior of
decision records, and "began with 33" is a historical claim no in-set content
contradicts.) What IS in-set checkable: the record's own declared metadata is
well-formed and internally consistent — three distinct 16-hex pins, thirteen
clauses D0009.C1..C13 each declared exactly once, no in-set enumeration of
record types contradicting the "33" count, and no clause contradicting
another on the C9 cursor/migrate claims.

Exit 0 = control is DEFECTIVE (in-set contradiction found).
Exit 1 = SOUND on the in-set test; out-of-contract residue recorded.
"""
import hashlib, json, re, sys

PATH = ("/home/halbritt/.local/share/striatum/exchange/"
        "019f22ef-0cb4-780f-9b82-b210bab24325/cas/"
        "a97ff272bb749518b9100e6261401cb58c7592e365739754fa93357a5c5a4e77")
SHA = "a97ff272bb749518b9100e6261401cb58c7592e365739754fa93357a5c5a4e77"

raw = open(PATH, "rb").read()
assert hashlib.sha256(raw).hexdigest() == SHA, "substrate body hash mismatch"
doc = raw.decode("utf-8")
results = {}

# Declared pins: three distinct 16-hex identities, incl. the contested one.
pins = re.findall(r"(proposal|design|implementation) `([0-9a-f]{16})`", doc)
results["pins"] = dict(pins)
results["three_distinct_wellformed_pins"] = (
    len(pins) == 3 and len({h for _, h in pins}) == 3)
results["contested_impl_pin_declared"] = (
    results["pins"].get("implementation") == "c005567787cb3486")

# Clause structure: C1..C13 each exactly once, in order.
clauses = re.findall(r"\*\*D0009\.C(\d+) ", doc)
results["clauses_declared"] = clauses
results["clauses_C1_to_C13_exactly_once"] = clauses == [str(i) for i in range(1, 14)]

# The contested C5 count: present, and no in-set enumeration contradicts it
# (the record never lists the record types; the only other number near the
# claim is the v2 rollout reference, not a count of v1 types).
results["c5_claims_began_with_33"] = "began with 33 v1 types" in doc
results["no_inset_type_enumeration"] = not re.search(
    r"\b34\b", doc) and "artifact_admitted" in doc  # names examples, no census

# The contested C9 claims: stated once, contradicted nowhere in-set.
results["c9_claims_embedded_cursors"] = (
    "each embed their own transactional cursor" in doc)
results["c9_claims_reconcile_migrate"] = (
    "`reconcile --migrate` is the explicit offline refold" in doc)
results["no_inset_statement_of_deferral"] = not re.search(
    r"deferred|not yet|unimplemented", doc, re.I)

results["out_of_contract"] = [
    "current bytes of rfcs/0009-provenance-ledger-and-artifact-store/"
    "implementation.md live in the base tree, outside the set",
    "the census of catalog/ledger-record-types/ and design.md's registry "
    "table live in the base tree, outside the set",
    "whether shipped code embeds cursors or ships reconcile --migrate lives "
    "in internal/, outside the set",
]

defective = not all([
    results["three_distinct_wellformed_pins"],
    results["contested_impl_pin_declared"],
    results["clauses_C1_to_C13_exactly_once"],
    results["c5_claims_began_with_33"],
    results["no_inset_type_enumeration"],
    results["c9_claims_embedded_cursors"],
    results["c9_claims_reconcile_migrate"],
    results["no_inset_statement_of_deferral"]])
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND (in-set); allegations out-of-contract")
sys.exit(0 if defective else 1)
