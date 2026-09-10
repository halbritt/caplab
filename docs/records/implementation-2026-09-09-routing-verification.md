# Inspect retained routing before native integration

Baseline `9e74701`. The primary agent selects this feature under the continuing
CAPLAB goal and [ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).
The existing native inspector accepts only offline network observations. The
routing context retains policy, command, readiness and terminal records, but
its reusable consumer currently ends at a pure supplied-rules comparison.
A retained bundle needs a bounded reader before a routed native profile can
use it as evidence. Private fixture verification is not that product interface.

Authorize a new `src/caplab/capture_network_verify.py`, read-only CLI
`scripts/inspect_capture_routing.py`, integration tests, a versioned contract
and this record. The input is one completed routing custody root, an exact
policy with independent hash, independent readiness and terminal byte hashes,
and the authenticated handoff peer PID. The reader must validate all linked
records, actual stream bytes, fixed command configuration, selected rules,
namespace and peer agreement, and monotonic lifecycle order. It must refuse
incomplete or contradictory custody without creating a success report.

Fresh tests may execute the existing disconnected outer-namespace routing
fixture, with its fixed local TCP sentinels, deadlines, bounded captures and
owned namespace cleanup. Authorize generating and deliberately corrupting only
new synthetic test custody, retaining private diagnostics and advisory evidence
under `/tmp/caplab-routing-verification-*`. Do not mutate or copy historical
experiment custody. Run focused tests and the full suite, retain source pins
and check results, then commit locally. This scope expires at that commit.
Preserve unrelated `docs/designs/`, worktrees, services and existing native
profiles. No native/provider/model call, spend, tracker write, study freeze,
admission, score, qualification, deployment or push is part of this effect.

The caller owns independent anchors, authenticated handoff provenance and a
stable private root. This reader can establish retained consistency; command
intent plus captured output is not independent proof of actual execution.
Tool hashes remain observed inputs, not a selected tool allowlist. Do not claim
continuous transport liveness, native containment, task success or acceptance.
Missing files and malformed documents are refusals, not retries or repaired
evidence. All owned descriptors must close on every path. Stop on unexplained
fixture escape, source drift, failed cleanup or conflicting accepted contracts.

Alternatives: leave verification in private scripts, teach the offline native
inspector to trust routing producer booleans, or implement a standalone reader
that the later native integration can call. Select the last: the first leaves
no reusable inspection boundary and the second would accept contradictions.
This is a new feature, with no changes to producer behavior or historical data.

## Execution and bounded verification

The initial real-fixture test failed because the inspector module was absent.
The first reader verified normal routing, file hashes, selected rules and
lifecycle links. Rehashed configuration controls then exposed eleven admitted
contradictions: altered helper commands, environment, descriptors, source/tool
hash fields, stream allowance and an extra command field. The fixed-profile
checks now refuse these. A subsequent process-schema check exposed an admitted
extra field and malformed wall timestamp; both are now refused. The CLI test
failed until its entry point existed. The raw red/green logs are preserved under
`/tmp/caplab-routing-verification-`; failed tests were not relabeled as passes.

The final focused run passed fourteen tests in 22.815 seconds, including six
new integration methods. The new tests use fresh kernel routing custody and
real API/CLI reads. They exercise twenty-one rehashed configuration/observation
contradictions, four rehashed rules/capability-stream contradictions, independent
anchor refusal, and missing, changed, oversized, symlink and FIFO files. They
also inspect actual body-error and timeout captures as refusals. No internal
functions or infrastructure are mocked. Tests mutate only their newly generated
synthetic files and restore those between cases; historical evidence is untouched.

The retained final probe is `/tmp/caplab-routing-verification-probe.py`, with
log `/tmp/caplab-routing-verification-probe.log` and new custody under
`/tmp/caplab-routing-verification-private-final`. It records three separate
controls: normal routing, a body exception after readiness and a real helper
timeout after body completion. Normal API and CLI reports agree. The other two
controls are refused by the completed-bundle reader without replacing their
raw evidence. Normal readiness bytes match the authenticated handoff observation;
the peer matches that handoff. Negative controls have no success claim.

The retained report is `verification.json` in that root, SHA-256
`1c9b46a39dd6d6e969882bcd9776b6347ef2b13bceb3f2b1232c78003b86f773`.
It preserves each source/tool hash and each inspected custody file hash. Nine
source files and four installed tool hashes agree before and after. All three
controls preserve their producer descriptor population and the outer caller's
user/network/PID namespaces and descriptor population. Inspection changes no
custody bytes. This is local verification of constructed controls, not an
independent containment judgment or representative repair result.

The [versioned contract](../product/contracts/capture-network-verification-v1.md)
states caller-owned private ancestry and anchor provenance, fixed read bounds,
error propagation, and the absence of execution/containment acceptance. The
reader uses existing no-follow file reads, process payload verification and
policy comparison. It validates runtime values rather than relying on type
annotations. Fixed command expectations are explicit beside receipt checks;
there is no generic verifier registry, configurable payload traversal, retry,
evidence repair or new producer behavior. The test and AI-failure-mode guard
passes checked these boundaries. CLI help and the actual success/refusal paths
match the documented flags and exit behavior.

The existing CAPLAB-84 decision still requires native integration and separately
authorized representative repair measurements. This feature supplies a retained
routing reader for that integration. It does not complete the shakedown or the
reviewer-capability goal, and it leaves the offline native profile unchanged.

## Final checks and advisory record

The full final-source suite returned exit zero: 1,464 tests, four skips,
192.532 seconds. Its command was `CAPLAB_TEST_WEBSOCKETS_ROOT=/tmp/caplab-native-transport-deps/websockets
make check`, using the retained test dependency. The log is
`/tmp/caplab-routing-verification-make-check-final.log`. All three new Python
source hashes in `/tmp/caplab-routing-verification-final-source.sha256` still
match after completion. Ruff F, format and diff checks passed on these files.
The observed interpreter is Python 3.12.3 and formatter is Ruff 0.15.17; no
other platform or version matrix is claimed.

The validated Pincite release gate passed at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial packet `pkt-23c29d261d428119` was reassembled with four typed evidence
records into `pkt-87574cfe60927b39`, content SHA-256
`87574cfe60927b39f501926c0c00610aa619fd277667f0fb8359d34c380cc65a`.
Corpus is `corpus-2026-07-12-a11702cc9217`, doctrine is
`doctrine-f6bbb5196a3f8bf9`, and retriever is `retriever-ec995ecdd083b2c8`.

Twenty remaining advisory obligations are individually classified in
`/tmp/caplab-routing-verification-obligations.json`. Fourteen concern performance
objectives, instrumentation and representative baselines: no performance or
repair-cost improvement is claimed. Four concern concurrency selection: the
new reader is sequential and its existing fixture lifecycle is directly tested.
The version matrix remains untested beyond the observed environment. The last
obligation concerns representative non-ASCII data: this profile uses fixed
structural names and byte-preserving streams, with no general language or text
normalization claim. These omissions are nonmaterial to the selected bounded
consistency reader; none supplies missing native or measurement evidence.

The schema-validated `decision-receipt/2`, evidence records, packet JSON and
Markdown, and citation observations remain under the same private prefix.
The receipt records scoped selection and focused verification, not independent
acceptance. Applied concepts were `python-text-bytes-boundary`,
`agent-conduct-authority-bounded-action`, `implementation-explicit-failure-policy`,
`universal-repository-contract-precedence`, `universal-evidence-before-intervention`
and `universal-preserve-behavior-by-default`. Consumption classification records
all six as valid packet citations for each served packet. The two local source
locators in the decision receipt classify as foreign citations, not doctrine
citations. No foreign doctrine authority is inferred from local source paths.

Final source and private-artifact hashes are retained in
`/tmp/caplab-routing-verification-verification.json`. All diagnostic process
handles were collected as terminal. Raw failures, the new retained controls,
source snapshots and advisory provenance remain available for review.
