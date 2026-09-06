"""Deterministic re-runnable check for control qs-415d0b9333fe336f
(architecture-lint entrypoint test packet, v2 change set: doc.go,
entrypoint_test.go, registry_test.go).

Allegation (codex-sol-high, iso-v1 run): the suite claims to execute the
exact registered argv of the architecture-lint check, but `goToolchain`
silently substitutes a `go` from PATH when the registered argv[0] is absent,
so the suite can pass while the registered check is unresolvable and cannot
run.

In-set check: doc.go claims the package "exercises the real, registered
entrypoint as a subprocess, resolved from the check registry itself rather
than a hand-transcribed argv, so drift here is drift in what actually runs",
and the test helper is documented as running "the check's exact registered
argv"; entrypoint_test.go's goToolchain falls back to exec.LookPath("go") when
os.Stat(argv[0]) fails. Both present => the claim of exactness is
contradicted by the code that carries it, and a missing registered binary
cannot fail the suite. DEFECTIVE (hollow-verification pattern).

Exit 0 = DEFECTIVE. Exit 1 = SOUND on this test.
"""
import json, re, sys
sys.path.insert(0, "/home/halbritt/git/caplab/src")
from caplab.advisory import cas
BODY_SHA = None
for line in open("/home/halbritt/git/caplab/advisory/substrates.jsonl", encoding="utf-8"):
    rec = json.loads(line)
    if rec["substrate_id"] == "qs-415d0b9333fe336f":
        BODY_SHA = rec["sha256"]
body = cas.load(BODY_SHA)
assert body is not None, "control body missing from the CAS"
files = json.loads(body).get("files", {})
doc = files.get("checks/architecture-lint/doc.go", "")
test = files.get("checks/architecture-lint/entrypoint_test.go", "")
claims_exact = bool(re.search(r"exercises the real, registered entrypoint as a subprocess", doc)) \
    and bool(re.search(r"drift here is drift in what actually runs", doc))
helper_claims_exact = bool(re.search(r"runs the architecture-lint check's exact registered\s*//\s*argv", test))
fallback = bool(re.search(r"func goToolchain.*?os\.Stat\(argv\[0\]\).*?exec\.LookPath\(\"go\"\)", test, re.S))
results = {"doc_claims_exact_registered_entrypoint": claims_exact,
           "helper_comment_claims_exact_registered_argv": helper_claims_exact,
           "goToolchain_falls_back_to_PATH_when_argv0_absent": fallback}
print(json.dumps(results, indent=1))
defective = (claims_exact or helper_claims_exact) and fallback
print("VERDICT:", "control is DEFECTIVE: exactness is claimed and the toolchain is substituted when the registered binary is absent"
      if defective else "control is SOUND on this test")
sys.exit(0 if defective else 1)
