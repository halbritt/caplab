# Non-root routed sandbox compatibility

Baseline `b73ce9b`. Attempt 2's actual native tool failed to create a nested
Bubblewrap UID map. The paired controls reproduced that failure with mapped
UID/GID zero and completed with caller UID/GID 1000, while all five workload
capability sets remained zero and no-new-privs remained set. The current routing
helper explicitly changes to UID/GID zero; a caller-mapped workload alone cannot
satisfy that helper. Historical/native attempt custody remains unchanged.

Under the continuing owner goal and ADR 0026, authorize a bounded investigation
and regression extension in `tests/test_routed_native_network.py` and the existing
`tests/test_capture_network_policy.py` helper. Exercise the production outer
namespace, selected task materialization, real policy and routing, then a nested
Bubblewrap `/usr/bin/true` before checking the permitted fixture response. The
helper may expose the already supported isolated writable procfs mode for this
control. Preserve existing default controls and all-zero workload capability
checks. First retain the mapped-root failure as a regression observation.

Permit fresh private diagnostic source and custody under
`/tmp/caplab-routing-nonroot-*`. A candidate routing-helper experiment may use
the mapped caller UID/GID and the existing four helper capabilities, carried
through exec with explicit inheritable/ambient sets. It may change only its own
helper process credentials inside the owned workload user namespace. Retain the
exact candidate source, command, helper/workload capabilities and all failures.
This is a distinct observed helper configuration, not an unchanged v1 profile.
The parent may create only fresh disconnected namespaces, owned routing helpers,
synthetic endpoints and test custody. Use existing test resource, stream and
deadline limits; cleanup must reap owned processes and preserve parent namespace
and descriptor populations. No installed native harness may execute here.

Do not change the production routing profile until these controls establish its
required identity/capability behavior and the selected change is recorded.
Do not enlarge workload privileges, disable native sandboxing, allow generic
destinations, reinterpret previous routing receipts or relax failed-attempt
criteria. No provider/model calls, real authentication, spending, historical
evidence effects, tracker writes, messages or study execution are authorized.
Preserve unrelated `docs/designs/` and sibling worktrees/services. Stop on changed
source pins, identity disagreement, unexpected privileges or incomplete cleanup.
Retain the evidence and commit the verified regression/record. Any native
adoption requires fresh configuration, preparation and exact execution authority.

The test behavior and interface scope are selected under the existing owner
delegation. The TDD skill's routine planning confirmation is already covered by
that delegation; it does not require another owner interruption.

## Caller-UID helper result and revised control

The new routed/nested regression failed with the current mapped-root profile.
The private caller-UID helper reached TAP creation with exactly the selected
four helper capabilities in all sets, then slirp stopped at `setegid(0)`.
No readiness was admitted. Its custody remains under
`/tmp/caplab-routing-nonroot-candidate/`. The installed-version source retained
at `/tmp/caplab-routed-network-upstream-main.c` shows the sandbox path explicitly
switching a nonzero effective UID to group/user zero. This eliminates that
candidate; no production helper change is selected.

Authorize a second synthetic topology control under
`/tmp/caplab-routing-nonroot-owner-control/`. Keep a mapped-root user namespace
owning the network and create a separate child user namespace with mapped
UID/GID 1000 for the workload. The trusted namespace setup may request
CAP_SETFCAP only to construct that child mapping; the released workload must
still have all five capability sets zero and no-new-privs. The nested control
still runs only `/usr/bin/true` and the fixed task/fixture check.

Private candidate copies of the policy and routing modules may obtain the
network's owning user namespace through the kernel NS_GET_USERNS ioctl, with
exact source and namespace identities retained. Use the unchanged mapped-root
helper source and its original capability profile in that owner namespace.
Observe the workload user namespace separately and require it to differ from
the network owner. This topology is a new experimental configuration, not
proof that the existing production API already enforces that distinction.
Retain raw manifests and any legacy inspector outcome without relabeling it
as verification of the new ownership boundary. No production runtime change
or native attempt is authorized by this control.

The owner-namespace control reached authenticated mount handoff, which refused
ambiguous stacked mounts: the second Bubblewrap layer added another procfs over
the existing isolated procfs. Preserve that failed control. Authorize one fresh
correction at `/tmp/caplab-routing-nonroot-owner-proc-control/`, changing only
the second setup layer to reuse the existing procfs. It shares the PID namespace,
so no new procfs is selected there. The final nested command still creates its
own procfs after handoff. Keep all other topology, limits and refusal checks.

Reusing procfs removed the stacked-mount refusal, but handoff then rejected the
changed writable-mount set. The extra Bubblewrap projection is unsuitable for
preserving the existing capture mounts. Preserve that failure. Authorize a fresh
control at `/tmp/caplab-routing-nonroot-owner-userns-control/`: replace only that
second mount-projecting layer with an in-process child user namespace. The trusted
setup records its pre-transition UID/GID and namespaces, unshares CLONE_NEWUSER,
writes the single mapping from child UID/GID 1000 to parent zero and denies
setgroups, then drops all bounding/ambient/permitted/effective/inheritable
capabilities and sets no-new-privs before executing the synthetic producer.
Record the resulting maps and capability fields. Keep all mount, network,
routing, task, stream, deadline and refusal criteria unchanged. No native
execution or production profile change is granted.

## Selected ownership boundary implementation

The in-process user-namespace control completed: nested Bubblewrap returned
zero, the prepared task bytes remained readable and the restricted fixture
replied. The workload user namespace differs from the network owner while its
network, mount and PID namespaces remain unchanged. All workload capability
sets are zero with no-new-privs. The unchanged helper capability profile works
in the network owner namespace. The legacy routing inspector refuses the
experimental ownership field; that refusal is preserved.

Select a reusable read-only kernel ownership boundary before modifying either
production routing profile. Under ADR 0026, authorize
`src/caplab/capture_network_identity.py`, its focused tests, a versioned contract
and this record. Open namespace descriptors from the authenticated blocked peer,
derive the network owner with NS_GET_USERNS, and distinguish same-user and
immediate-parent ownership profiles. For the parent profile, require the kernel
parent of the workload user namespace to equal the network owner and require
the fixed non-root single UID/GID mapping. Refuse supervisor network/user
namespaces, nonzero workload capabilities, invalid profiles and inconsistent
relations before yielding helper descriptors. Own and close every descriptor
on success and failure; do not enter or mutate any namespace in this reader.

Tests may create fresh owned synthetic user/network/PID namespaces using the
verified setup, including refusal controls, but no installed native harness.
Retain the red routed regression and all candidate sources outside the repo;
restore its pending changes to the old test files before adding the new focused
tests, so the existing root profile is not silently redefined. This preserves
the regression evidence for the later explicit native profile change. Run the
focused and full suites, retain advisory/verification provenance and commit the
new boundary. Production routing and native adoption remain subsequent material
work, not completion inferred from this helper.

## Implementation verification

The new API is `open_capture_network_namespaces(peer_pid, profile=...)` with
closed `workload-user/v1` and `parent-user/v1` profiles. Its descriptor lease
uses kernel owner/parent ioctls and closes all owned descriptors on every exit.
The mapping check uses the observer's proc coordinates: internal UID/GID 1000
maps singly to the observer UID/GID. It does not mislabel those values as IDs
in the workload's immediate parent or claim that the owner's UID/GID zero exists.
Those helper-execution properties remain separate checks.

The first focused run failed because the new module did not exist. After
implementation, the isolated test fixture lacked the private `/tmp` needed by
nested Bubblewrap; adding that owned tmpfs corrected the fixture. Four focused
methods then passed. They use actual kernel namespaces and include an extra
child holding CAP_NET_ADMIN: its nested command executes, but adding an nft
table to the ancestor-owned network returns Operation not permitted. Wrong
profiles, mappings, grandparent ownership, privileged peers and supervisor/self
inputs are refused. Descriptor populations agree after successful reads,
refusals and a caller exception; yielded descriptors are non-inheritable and
closed after context exit. No internal production function is mocked.

The full suite completed with exit zero: 1,474 tests, four skips, 208.666 seconds,
at `/tmp/caplab-routing-nonroot-make-check.log`. Both final source hashes in
`/tmp/caplab-routing-nonroot-final-source.json` match. New files were formatted
and passed Ruff F checks; diff and repository link checks passed. Source review
checked FD acquisition/closure, syscall failure propagation, closed profile
validation, bounded ASCII reads and observer-coordinate mapping comparisons.
The API writes no artifacts and exposes no new network listener. Authentication,
blocked lifetime, persistence and execution authority remain caller-owned.

The successful private topology source is under
`/tmp/caplab-routing-nonroot-owner-userns-control/capture/`. Its experimental
policy/routing copies select the network owner; the legacy inspector explicitly
returns `invalid policy preflight` for the additional ownership field. Preserve
that separation. The prior caller-UID and extra-mount candidates remain failed;
the original mapped-root routed regression sources are retained as
`/tmp/caplab-routing-nonroot-pending-test_routed_native_network.py` and
`/tmp/caplab-routing-nonroot-pending-test_capture_network_policy.py`.

The next integration must bind an explicit ownership profile into policy and
routing collection and retained inspection, then a distinct native launch and
preparation profile. Trusted setup needs the demonstrated child user-namespace
transition before final privilege dropping, without another mount projection.
Actual native execution needs fresh source/configuration/input pins and a new
one-attempt authorization; neither prior native allowance is renewed. The
ownership reader alone does not complete that integration or CAPLAB-84.

## Advisory provenance

The validated Pincite release gate passed with source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
release `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Initial packet
`pkt-f5e4c57eb4226942`, four inspected typed evidence records and one reassembly
produced `pkt-f791148078fed199`, content SHA-256
`f791148078fed199bf711c05cdc1830eaf575fa339bb019b689bd976a6f10e86`.
Versions: `corpus-2026-07-12-a11702cc9217`, `doctrine-f6bbb5196a3f8bf9`,
`retriever-ec995ecdd083b2c8`. Repository instructions and delegated authority
remain governing; advisory retrieval creates no new execution permission.

The receipt `/tmp/caplab-routing-nonroot-decision-receipt.json` scopes its
verification to the new ownership reader and synthetic controls. It applies
least privilege, structured cleanup, preservation, contract precedence,
authority boundaries and evidence before intervention. All 21 remaining
obligations are individually classified in
`/tmp/caplab-routing-nonroot-obligations.json`: 14 concern performance claims
not made here, four concern CI/version/tooling matrices, one image-rebuild
policy and two text transformation/round-trip evidence. They are nonmaterial
to this bounded kernel reader. Production/native integration and representative
repair measurements remain material work outside this verified claim.

Evidence and receipt schemas validated. Citation classifications were retained
for both served packets: six used concepts are valid packet citations and local
source/record locators are classified separately as foreign citations. The
private sources, observations, failures and advisory artifacts are retained;
no historical evidence was rewritten or admitted, no installed native harness
ran, and no provider/model calls, spending, score or independent acceptance
occurred in this investigation.

Final manifest `/tmp/caplab-routing-nonroot-verification.json` retains 217
artifact identities and the two new Python source hashes, SHA-256
`965145f5be86583be1fc095e7dd272f3c642787163666169757794f54ff6b304`.
It includes all control generations, the successful kernel tests, full-suite
log, retained upstream source references, advisory records and receipt. This
bounded implementation authority expires at its verified commit; the broader
CAPLAB improvement goal remains active.
