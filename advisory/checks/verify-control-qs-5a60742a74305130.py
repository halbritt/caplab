"""Deterministic re-runnable check for control qs-5a60742a74305130
(check-registries-portable-b implementation plan, dispatch 264e6659...).

Allegations (oc-deepseek-v4-pro only):
  A1: the plan asserts check id 62d3fbf5... "is the registered
      `go test ./...` check", but in the live registry
      (policy/checks/repository.json, registry_version 34) that id
      resolves to nothing. -- OUT-OF-CONTRACT: the registry is not in the
      set; the claim is uncomputable from the plan's own content. (For
      the record, sibling control qs-40583720's in-set registry pin at
      registry_version 13 uses exactly this id for the go-test
      semantic-closure-suite check, so the id is not an invention.)
  A2: packet 02 declares "Verification mapping: design clauses C2 and
      C3", but the consolidated Verification Mapping's C2 row enumerates
      packets 01, 03, 04, 05, 06, 08 -- omitting 02 -- an alleged
      internal inconsistency.

A2 is in-set and its facts are real (this script verifies them). The
verdict turns on whether an under-inclusive summary row CONTRADICTS the
per-packet declaration. The row asserts no exclusivity ("C2: packets 01,
03, 04, 05, 06, and 08 remove workstation-local identity assumptions..."),
and the same summary is demonstrably coarse elsewhere: it collapses C5-C8
into a single row and likewise omits packet 01's C7/C8 and packet 05's C7.
Both statements can be true at once; nothing in-set denies packet 02's C2
coverage. This oracle therefore encodes the non-exhaustive-summary
reading: DEFECTIVE only if the summary claims exclusivity while omitting
02, or if any mapping reference fails to resolve in-set.

Exit 0 = control is DEFECTIVE. Exit 1 = SOUND on the in-set test.
"""
import hashlib, json, os, re, sys

PATH = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325/"
    "dispatch/264e6659389ea250854485f6674518dfbe217a97c5d5a1c61943e9180df874c0/"
    "inputs/00-striatum-next-passes-check-registries-portable-b-implementation-plan")
SHA256 = "5a60742a7430513044e4e35ad55e95abac5aebae71606460c55ffdbb03b377fd"

raw = open(PATH, "rb").read()
if hashlib.sha256(raw).hexdigest() != SHA256:
    print("substrate sha256 mismatch -- refusing to adjudicate", file=sys.stderr)
    raise SystemExit(2)
doc = raw.decode("utf-8")

results = {}

# A2 facts: packet 02's own mapping claims C2 and C3.
p02 = re.search(r"### Packet 02:.*?(?=### Packet 03:)", doc, re.S).group(0)
results["packet02_claims_C2_C3"] = (
    "Verification mapping: design clauses C2 and C3." in p02)

# The consolidated C2 row.
c2row = re.search(r"- C2: packets ([^\n]*)", doc).group(1)
c2pkts = set(re.findall(r"0\d", c2row))
results["consolidated_C2_row"] = "C2: packets " + c2row
results["consolidated_C2_omits_02"] = "02" not in c2pkts

# Does the summary claim exclusivity anywhere?
summary = re.search(r"## Verification Mapping.*?(?=## Review Minor)", doc, re.S).group(0)
results["summary_claims_exclusivity"] = bool(
    re.search(r"\bonly\b|\bexclusively\b|\bexhaustive\b|no other packet",
              summary, re.I))
# Nothing in-set denies packet 02 C2 coverage.
results["inset_denial_of_p02_C2"] = bool(
    re.search(r"packet 02[^.\n]*not[^.\n]*C2", doc, re.I))

# The summary is coarse elsewhere too (supports the non-exhaustive reading).
results["summary_also_omits_p01_C7C8_and_p05_C7"] = (
    "C1, C2, C7, and C8" in doc          # packet 01's own mapping
    and "C2, C3, and C7" in doc          # packet 05's own mapping
    and "C7: " not in summary            # no dedicated C7 row
    and "C5 through C8: packet 07" in summary)

# Reference resolution: every work-graph derived_from resolves in-doc,
# every clause named by a packet mapping is a C1..C10 the summary knows.
fence = re.search(r"```striatum-work-graph\n(.*?)\n```", doc, re.S)
graph = json.loads(fence.group(1))
anchors = set(re.findall(r"\{#el:([a-z0-9-]+)\}", doc))
results["unresolved_derived_from"] = sorted(
    p["derived_from"] for p in graph["packets"]
    if p["derived_from"].lstrip("#el:") not in anchors
    and p["derived_from"].removeprefix("#el:") not in anchors)

results["out_of_contract"] = [
    "A1: whether 62d3fbf5... resolves in the live registry at "
    "registry_version 34 (policy/checks/repository.json is not in-set; "
    "the plan is a re-issue of RQ-8523-era work, and the sibling control "
    "qs-40583720 pins this exact id as the go-test check at registry v13)",
]
results["needs_judgment"] = (
    "whether a consolidated verification-mapping row purports "
    "exhaustiveness; this oracle encodes the non-exhaustive reading "
    "(no exclusivity claim in-set, summary demonstrably coarse for "
    "C5-C8 as well)")

defective = (
    (results["consolidated_C2_omits_02"]
     and results["summary_claims_exclusivity"])
    or results["inset_denial_of_p02_C2"]
    or bool(results["unresolved_derived_from"])
)
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective
      else "SOUND (in-set); see out_of_contract and needs_judgment")
sys.exit(0 if defective else 1)
