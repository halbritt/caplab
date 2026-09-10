# Bind parent-owned routing to collection and inspection

Baseline `e1b60e9`. The non-root topology control succeeded and the reusable
kernel ownership reader passed its tests. Production policy/routing still open
the workload's user namespace, so they cannot yet route that topology. A new
selection must bind the network owner through helper execution and retained
inspection before a native profile can adopt it.

Under the continuing owner goal and ADR 0026, authorize changes to
`capture_network_identity.py`, `capture_network_policy.py`,
`capture_network_transport.py`, `capture_network_verify.py`, the routing
inspection CLI and their focused test helpers/tests. Add a versioned contract
and this record. Select an explicit `namespace_profile="parent-user/v1"` option
for collection and an independent `expected_namespace_profile` for inspection.
The default `workload-user/v1` retains existing v1 behavior and custody formats.
The parent selection uses the checked network-owner descriptors, retains the
ownership snapshot and workload credential observations, and links their hash
through distinct v2 policy/routing records. Helpers retain their original
source, capabilities, syscall restrictions and destination policy. No workload
privilege, endpoint, resource or shutdown criterion is enlarged.

Retained inspection must validate closed schemas, expected profile, owner/parent
relations, observer-coordinate mappings and credential agreement, plus the
existing command, process, stream, policy and lifecycle checks. It must reject
profile relabeling and rehashed ownership contradictions. Retained consistency
is not independent proof that a kernel observation occurred; trusted collection,
authenticated peer lifetime and independent anchors remain caller-owned.

Authorize only new synthetic controls under `/tmp/caplab-parent-routing-*` and
temporary test roots. Tests may use the demonstrated child user-namespace setup,
request CAP_SETFCAP during trusted setup only, then require all five workload
capability sets zero and no-new-privs before handoff. Preserve prior candidate
sources, native attempt custody, default tests and unrelated `docs/designs/`.
Run real routed/nested controls and failure/refusal cases, then the full suite.
No installed native harness, provider/model call, real authentication, spending,
historical evidence effect, tracker write, message, scoring or study execution
is authorized. Stop on identity disagreement, quarantine, unexplained privileges,
source drift or incomplete owned-process cleanup. Retain failures and provenance;
commit and publish verified work under the owner's request to push main.
This bounded authority expires at that commit. Native adoption remains separate.

## Execution and technical verification

Implemented the explicit parent profile in policy installation, routing
collection and retained inspection. Both collectors use the committed kernel
ownership lease and require their snapshots to agree before routing starts.
Policy retains the four UID/GID status values; routing seals the snapshot and
links its hash through command, readiness and terminal records. Inspection
checks closed v2 formats against the caller's profile and existing independent
anchors. The default branches retain the old v1 formats. The CLI exposes
`--namespace-profile` with the legacy default.

The new [contract](../product/contracts/capture-parent-routing-v1.md) describes
these interfaces and their limits. The original policy and routing helper source
strings are byte-identical to baseline, as checked by AST extraction in
`/tmp/caplab-parent-routing-helper-preservation.json`. Their SHA-256 values are
`ca121ada24621144df5fee9cb5057697a4b8e6ba5981b68007528da306f30228`
and `e08d43268ea0681f75e677728747a816f785a7a7d633dde7f45ea2305a46a678`.

The initial regression and first producer run failed at a missing shared test
setup constant, before exercising the intended collection change. After correcting
that test extraction, parent routing and nested execution succeeded but
inspection lacked its new argument. That later failure exercised the missing
inspection interface; the initial import failure is not a behavioral baseline.
These failures are retained in `/tmp/caplab-parent-routing-red.log`,
`/tmp/caplab-parent-routing-producer.log` and
`/tmp/caplab-parent-routing-producer-corrected.log`. Completing the inspector
produced five passing initial identity/integration tests in 2.339 seconds,
retained in `/tmp/caplab-parent-routing-first-green.log`.

The final focused run passed 23 tests in 35.849 seconds, retained in
`/tmp/caplab-parent-routing-focused.log`. Five new integration test methods
cover actual nested Bubblewrap plus selected TCP access; API and CLI inspection;
default/parent profile mismatch; altered snapshot, credential, copy and hash
links; invalid profile selection before peer access; and missing tun, body
exception, timeout and metadata quarantine. Sixteen snapshot contradictions are
rehashed through every copy and link so semantic checks, rather than stale hash
checks alone, must refuse them. Descriptor populations are checked on refusal.
The existing identity, policy, transport and retained-inspection tests also pass.

A fresh retained control at `/tmp/caplab-parent-routing-retained-control` used
nine pinned changed Python sources and produced a successful v2 observation.
`source-pins.json`, `inspection-inputs.json`, `inspection.json`, `result.json`
and the complete new routing/attempt custody preserve its configuration and
results. Its identity hash is
`33f8f2c62fc0466dcdfcb7f0c1a48d8b53c77e012f217ed8d653f64919ad437a`.
The test observed an actual nested `bwrap ... /usr/bin/true`, allowed destination
access, and refusal of a wrong port and internal address in a disconnected
outer network. Trusted topology setup requested CAP_SETFCAP before dropping all
workload capabilities; this is a test setup effect, not a native launch change.

`/tmp/caplab-parent-routing-preservation.json` records revalidation of all 217
private artifacts in the preceding topology manifest and all 197 private
artifacts in the second native-attempt manifest. Their original bytes remain
unchanged. The nine current Python source pins still match the retained control.
Ruff formatting, Ruff F checks and `git diff --check` passed.

## Advisory basis and boundaries

The validated Pincite release remains
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Its retrieval-state gate passed with
source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9` and retriever `retriever-ec995ecdd083b2c8`.
The initial packet is `pkt-0c418038a70f0cef`; the evidence-backed packet is
`pkt-d83f30e9bc3b163e`, content SHA-256
`d83f30e9bc3b163eefdf5a5bd0d7691dd42bbcfdc6bfc1c30e860eb4f3910a0c`.
Both JSON packets and Markdown renders are retained under
`/tmp/caplab-parent-routing-doctrine-{initial,final}.{json,md}`.

Four typed evidence records, the decision receipt and citation observations
are retained under that prefix. Receipt validation first refused a missing
`depends_on` field; it passed after the dependency was stated explicitly. Both
served packets have citation classifications. Used concepts are
`operations-least-privilege`, `python-structured-cleanup`,
`universal-preserve-behavior-by-default`,
`universal-repository-contract-precedence`,
`agent-conduct-authority-bounded-action` and
`universal-evidence-before-intervention`. Repository source locators remain
foreign citations, not doctrine corpus sources.

No material advisory obligation remains for this bounded integration claim.
`/tmp/caplab-parent-routing-obligations.json` individually classifies 20 missing
obligations as nonmaterial: fourteen performance/baseline/metric requirements,
four cross-version/CI/toolchain-policy requirements, one container-image policy
and one representative non-ASCII requirement. This change makes no performance,
observer-cost, CI matrix, container or text-transformation claim. Real retained
JSON/CLI round trips and failure behavior are covered by tests.

Keeping mapped root as the only workload profile leaves the demonstrated UID-map
failure unresolved. Inferring profile selection from custody would remove an
independent selection check. Changing helper privileges is unnecessary under
the observed parent topology. The selected option adds explicit collection and
inspection while leaving native adoption for its own preparation and authority.
Reopen on owner/credential disagreement, legacy compatibility drift, unexpected
helper lifetime or privileges, or failure when this topology reaches native
execution.

These are execution and technical verification observations, not independent
acceptance or reviewer measurement. The actual routed native attempt remains a
preserved failure. Native profile adoption, a newly prepared and authorized
one-shot diagnostic, representative repair measurements and observer-cost
assessment remain material work toward CAPLAB-84 and the continuing goal.

## Full-suite result

`CAPLAB_TEST_WEBSOCKETS_ROOT=/tmp/caplab-native-transport-deps/websockets
make check` passed 1,479 tests in 209.904 seconds with four existing skips. The
log is `/tmp/caplab-parent-routing-full-suite.log`. The skipped cases require
the separately authorized P4 live campaign or a PostgreSQL integration DSN;
this run makes no verification claim for those environments. No Python source
changed between the retained control, full-suite run and publication checks.

The retained verification manifest is `/tmp/caplab-parent-routing-verification.json`,
SHA-256 `dde22f179c5cb62e7ed2d99206b0454873711de1f17664e602d68108b6de576f`.
It identifies 72 private artifacts and 10 source/contract pins. The final
record is committed separately to avoid a self-referential hash.
