# Retain bounded temporary files after fixture termination

Date: 2026-09-08. Baseline: `f9834ad`. Authorization under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Extend `scripts/probe_cgroup_resource_limits.py` and add this record. Preserve
the prior committed probe and its retained runs as their original versions.
Use a trusted startup wrapper and a private Unix socket to transfer one
`/scratch` directory descriptor to the supervisor before executing each fixed
fixture. Verify the peer and descriptor, then release the fixture. Keep that
descriptor outside the fixture cgroup until all fixture processes have stopped
and its files have been copied and verified. Close owned sockets/descriptors and
remove only the generated socket path, fixture cgroups and exact unit name.

Run at most three new UUID-named transient user units sequentially under the
existing 128-MiB memory, zero-swap, 64-task and 30-second unit limits. Preserve
the three fixed control/memory/pids fixtures, their 32-MiB memory limits, task
limits, 64-MiB tmpfs ceiling, ten-second process deadline and 200,000-byte stream
allowance. Add a small known binary marker before fixture activity. Retain at
most 40 MiB and 100 entries per fixture through the existing inventory owner;
do not change that owner or its verifier. Verify retained objects after the
service and original namespace are gone. Keep resource events and retained
file integrity separate from native completeness or eligibility.

Retain new probe custody and reports under `/tmp/caplab-retained-mount-*`.
Read official Unix-descriptor and kernel documentation as needed. Run bounded
actual probes, focused negative checks and the repository suite; consolidate
advisory evidence and delete exact named advisory scratch. Commit the script
and this record locally. Authorization expires at commit.

No native harness/model call, historical experimental evidence processing,
study admission, score, ranking, campaign budget, tracker write, external
message or push. Preserve existing runtime/capture owners, tests, world
dossiers, prior evidence, unrelated services/cgroups/timers, `docs/designs/`
and sibling worktrees. No sudo or system unit. Stop on a broader required
effect, unavailable descriptor transfer, changing source after quiescence or
an inability to verify exact owned cleanup. Never fall back to unbounded or
uncontained execution.

## Intended verification

The supervisor must recover the exact marker for all three fixtures after
their processes stop, including the group OOM. The memory case must retain its
partially written payload and independent OOM events. Object bytes and hashes
must verify from host custody after the temporary namespace and generated unit
are gone. A corrupt retained marker or inventory anchor must fail verification.
All previous resource expectations continue to apply. This tests supervisor
survival and orderly retention, not host-crash durability or every failure path.

## Implementation and boundary

The trusted wrapper opens `/scratch` and transfers its directory descriptor
through a Unix socket mounted into the fixture namespace. The socket resides
in the private output root, accepts one connection and closes its listener
before the fixture is released. The receiver checks peer UID/GID and cgroup
membership, one non-truncated descriptor, directory kind and the configured
64-MiB filesystem capacity. It acknowledges the wrapper only after those checks.
The wrapper closes its own descriptor and socket before executing the fixed
fixture. No host custody directory or supervisor control descriptor is passed
to the fixture.

SCM_RIGHTS transfers a reference to an open file description; the receiver gets
its own descriptor. Peer credentials and ancillary-data truncation are distinct
checks. [Linux Unix socket manual](https://man7.org/linux/man-pages/man7/unix.7.html)
The experiment below establishes the retained-directory behavior on this local
Linux substrate; it is not a cross-platform portability claim.

The supervisor runs the existing bounded process capture in one worker thread
while accepting the handshake. Handshake/socket waits and the process owner
have separate bounded waits. After the process returns, cgroup quiescence is
required before inventory. The existing `_Inventory` traverses the directory
through the received descriptor with its normal byte/entry limits and
no-follow/stability checks. Source paths are relative to that descriptor;
`/scratch` in the receipt names the fixture namespace, not a host path.

The new `caplab.retained-mount-inventory/v1` receipt seals source descriptor
identity, namespace scope, limits, entries and hashes. Each fixture observation
links its receipt hash. Resource probe observation and verification schemas are
versioned to v2. No original v1 observation is changed. The shared inventory
verifier checks the retained objects after the service exits, and the probe
separately requires the exact known binary marker and a nonempty partial OOM
payload. Captured-resource expectations remain unchanged.

Descriptor and socket cleanup is explicit. Received descriptors are closed on
invalid handoffs. The accepted descriptor stays open through retention, then
closes before fixture-cgroup removal. The generated socket path is removed on
both success and failure. The outer owner verifies the exact unit's absence.
The runtime/capture library owners remain unchanged; this extends only the
fixed diagnostic script.

## Execution and findings

The first run, `/tmp/caplab-retained-mount-first/`, refused the handshake before
the fixture body ran. The receiver incorrectly required zero returned flags.
A local socketpair reproduction showed that Linux returned the requested
`MSG_CMSG_CLOEXEC` flag (1073741824) alongside one valid descriptor. The check now
allows that flag while rejecting truncation and other flags. The original
failed script is retained at `/tmp/caplab-retained-mount-first-script.py`, with
the hash recorded in that run's sealed intent. Failure streams and cleanup
receipts remain unchanged; the unit was removed.

The corrected script ran under `/tmp/caplab-retained-mount-second/`, unit
`caplab-resource-probe-a8433dba7f8e48349f9b0af29c405419.service`. The process and
retention observations were:

| Fixture | Process/resource observation | Retained content after namespace exit |
| --- | --- | --- |
| Control | Exit 0; no OOM event | 18-byte binary marker and two-byte control file |
| Memory | Signal 9; OOM 1, group OOM 1, OOM-killed processes 4 | Exact marker and 25,878,528-byte partially written payload |
| Pids | Exit 0 after caught task-limit failure; original event expectation passes | Exact marker |

The memory fixture's 25,878,546 retained bytes remained below its 40-MiB copy
allowance. The independent event snapshot still showed 26,181,632 bytes charged
after the fixture processes died, consistent with the retained mount remaining
available. Those values are observations from this run, not native resource
requirements or a guarantee that the same OOM point repeats.

All three inventories and their object hashes verified from host custody after
the service exited. The marker contains a NUL, a non-UTF-8 byte and a newline;
its exact byte match establishes that this path did not depend on text decoding.
The partial payload is preserved evidence of an interrupted writer, not a
completed output or an eligible attempt. No task correctness or reviewer
capability judgment was made.

Five negative checks passed: a wrong inventory anchor, altered retained bytes,
a resealed inventory containing the wrong marker, a regular-file descriptor
and multiple descriptors were all rejected. The two rejected descriptor cases
also verified that the receiving process's open-descriptor count returned to
its prior value. These checks used disposable copies of the small control
inventory and local sockets; they did not mutate the retained runs or create
additional services. Their script and results are
`/tmp/caplab-retained-mount-focused.py` and `focused.json` under the same prefix.

## Remaining requirements

The selected bounded change keeps the existing inventory and verifier owners.
Leaving the prior probe unchanged would preserve its resource-event evidence
but leave temporary-file recovery untested. Writing directly into host custody
would change the fixture's writable-storage boundary. Generalizing the native
launcher now would extend beyond the fixed-fixture evidence. The descriptor
experiment resolves this narrower question at the cost of a socket handshake,
one capture worker and explicit descriptor cleanup. It does not establish
operational cost or justify a reusable native-launcher abstraction.

The durability and security review remains bounded to a trusted wrapper on
this Linux host. Descriptor ownership and rejected-transfer cleanup are checked;
the cases listed below remain explicit uncertainty. No change to the shared
capture owners is needed for this experiment. This is a delegated implementation
decision, not an independent acceptance verdict.

The supervisor and startup wrapper are trusted, and the fixture code remains
fixed. Peer membership and descriptor shape do not authenticate a native
provider or defend against a hostile host actor. The experiment covers fixture
OOM and ordinary supervisor survival. Supervisor death, host crash, disk stalls,
retention-limit failure and other recovery paths need their own treatment.
Keeping a mount reference is not durable storage until the host copy is sealed.

Only `/scratch` is retained here. Full task/runtime/log coverage, inode and
logical-size policies, all writable surfaces, native identity and the final
study stop/disposition mechanism remain incomplete. Resource failure,
retained-byte integrity and native-capture completeness stay separate. This
probe does not select a native launcher or authorize a real episode.

## Verification and advisory closure

`make check` exited 0: 1,163 tests in 148.256 seconds, four skips. The log is
`/tmp/caplab-retained-mount-make-check.log`. The exercised script hash is
`05385fb5727ef9e0a919ebae6c001dfee47235de856fffa61de0d94b90196694`;
it matches the second run's sealed intent and the final source. Six protected
source/record files remain byte-identical to `f9834ad`.

Both exact generated units were read back as `not-found`; their fixture and
parent cgroups and generated socket paths were absent. Two of the permitted
three units were used. The consolidated evidence, source hashes, suite result,
typed advisory observations and cleanup checks are retained in
`/tmp/caplab-retained-mount-verification.json`. Eleven exact advisory scratch
files were deleted after consolidation. Probe custody, source snapshots,
focused-check script/results, logs and the inspected Unix manual remain.

The validated Pincite release at
`/home/halbritt/.local/share/pincite/release`, commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, supplied advisory packet
`pkt-bdcf55b63db715f1`, content SHA-256
`bdcf55b63db715f1bea3e3b758bd78cb780df6ab056afe0873d760194abfc9f1`.
Its corpus is `corpus-2026-07-12-a11702cc9217`, doctrine version
`doctrine-f6bbb5196a3f8bf9`, retriever version `retriever-ec995ecdd083b2c8`.
Four consumed concepts classified as valid packet citations:
`universal-repository-contract-precedence` preserves repository authority;
`universal-explicit-invariants` informs descriptor ownership and failure checks;
`universal-evidence-before-intervention` bounds claims to observed fixtures;
`implementation-placement-by-ownership` keeps traversal and verification in
their existing owners. Retrieval does not confer authority or acceptance.

Fourteen unmet generic obligations remain individually classified with exact
wording and rationale in the verification manifest. Two concern structural
boundary cost/force and one recurring change: no new product abstraction or
maintainability claim is selected. Four concern broader CI, version and static
tool matrices: only this host and the declared repository check are claimed,
with no dependency or toolchain change. One concerns optimization workloads:
no performance claim is made. Six concern Python dynamic class mechanisms:
the operating-system file descriptors used here do not introduce those
mechanisms. These omissions are nonmaterial to the fixed local experiment;
they do not establish broader native-launcher readiness.
