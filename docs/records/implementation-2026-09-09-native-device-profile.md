# Supply the basic devices required by nested Bubblewrap

Baseline `47d8482`. Primary agent under ADR 0026 and the continuing CAPLAB goal.
The previous native stdout and rollout agree that nested Bubblewrap failed
binding absent `/dev/zero`. The current handoff allows only null and urandom.
Published Bubblewrap 0.9.0 `SETUP_MOUNT_DEV` binds null, zero, full, random,
urandom and tty. The host binary reports 0.9.0; the bundled binary reports
`bubblewrap built for Codex`, so upstream source is advisory, not a claim of
installed-build equivalence. Read-only version inspection launched no Codex
agent or provider request.

Source: https://github.com/containers/bubblewrap/blob/v0.9.0/bubblewrap.c#L1202

## Decision and prospective authorization

Authorize an explicit `bwrap-basic-v1` selection through the existing
`usable_devices` keyword on mount coverage and handoff. Literal false and true
preserve their existing no-device and two-device profiles and receipt fields.
Reject every other selection. The named profile permits exactly six writable
device mounts, retaining all procfs, root, tmpfs and unexpected-mount checks.
It records its profile name and separately validated device observations.

Validate each opened O_PATH/no-follow descriptor as the exact Linux character
device: null 1:3, zero 1:5, full 1:7, random 1:8, urandom 1:9, tty 5:0. Check
identity before any read/write operation. Require the peer's kernel stat record
to show no controlling terminal; never open tty for I/O from the supervisor.
Use bounded nonblocking reads for random devices, exact zero-byte checks for
zero/full, a discarded null write and an expected ENOSPC full write. Retain
counts and predicates, not random bytes. Revalidate the named profile and
recorded predicates during custody inspection. Recorded verification does not
reconstruct live devices after exit.

Modify only the two existing probe helpers, focused tests in
`tests/test_nested_procfs.py`, a new device-profile contract and this record.
Reuse the existing paused-peer fixture and nested sandbox witness. First require
the real nested `--dev /dev` setup with the full outer profile; then test wrong
character identity, omitted/extra mounts, invalid selections and inconsistent
recorded observations. Preserve all existing caller behavior and receipts.
Run focused and required full checks, retaining failures and source snapshots
under `/tmp/caplab-basic-devices-*`, then commit locally. These delegated
interface and test choices satisfy the TDD planning gate under ADR 0026.

Permit bounded synthetic execution of the exact installed bundled Bubblewrap
component with the fixed local Python witness, after the host-Bubblewrap fixture
passes. Pin its bytes and retain command/output evidence. This is not permission
to run Codex CLI, a model or provider. Bound synthetic captures to 10 seconds,
10,000 stream bytes and the existing five 64-MiB tmpfs mounts; retain namespace,
capability and NoNewPrivs checks. No real credentials, external network, host
terminal I/O, tracker write, message, push, historical research evidence effect,
study adoption or independent acceptance. Preserve unrelated `docs/designs/`,
worktrees and services. Stop on unexplained check or cleanup failure. This
scope expires at its verified local commit; a native attempt needs a new record.

Adding only zero would leave the next source-declared device absent. Mounting
the whole host /dev would expose unrelated devices. Changing every legacy
caller would widen scope. The named closed profile serves the observed nested
sandbox requirement without admitting arbitrary device names or paths.

Authorize one additional rejection fixture using a newly allocated private
pseudo-terminal and an owned Python child session. Give that child its private
terminal, require live device inspection to reject it before device I/O, then
close the release pipe, reap the child and close both PTY descriptors. Never
open, read or write the operator's controlling terminal. This fixture verifies
the terminal guard against real kernel state rather than only a modified record.

## Implementation and observed checks

The initial real nested-device test failed because the old mount gate rejected
the additional writable devices. The first implementation reached the expected
full-device ENOSPC but exposed a missing `errno` import; that source error was
corrected and its log retained. The same nested fixture then completed the exact
UTF-8 witness with `--dev /dev`. Existing true/false callers keep their topology
and receipt fields. The named profile supplies deterministic recorded predicates
from live descriptor and kernel checks, and custody inspection validates them.

Rejection checks cover a real urandom device bound at zero, absent/extra device
mounts, ambiguous flag values, arbitrary profile names and missing/contradictory
device observations, including bool/integer confusion. The private-terminal
child is rejected from its real kernel stat record. Its release pipe closes
before the child is reaped, and the PTY closes after reaping to avoid a hangup
race. Descriptor counts return to baseline. The 21-test adjacent selection
passed before the private-terminal test was added; that test passed separately.

A separate fixed control executed the installed bundled Bubblewrap component,
SHA-256 `77360cb751ccedc5971391444ac86a8a33c15b04d6b4a6fe45f5d25496e62c4c`,
under an isolated outer sandbox with all six devices. Its nested `--dev /dev`
command completed `CAPLAB café bundled devices` plus a newline in `/work`.
The outer process had zero capabilities, NoNewPrivs and no controlling terminal;
opening its tty returned ENXIO. The binary hash was unchanged afterward.
The control retains intent, process capture, stdout and verification under
`/tmp/caplab-basic-devices-bundled-control/`. It executed no Codex agent or model.

The existing handoff remains the owner of device release checks; no parallel
adapter, arbitrary device registry or global topology change was introduced.
The added record verifier checks consistency after exit, not live safety. The
profile keyword reuses the existing interface to preserve its current callers;
no unrelated request-object migration is part of this semantic extension.

`make check` passed: 1,343 tests in 167.728 seconds, four skips. All six added
tests ran without skips. Log: `/tmp/caplab-basic-devices-make-check.log`.
No runtime or test source changed after this run. Ruff F and diff checks pass.
The bundled control's binary, capture receipt and exact stdout hashes were
checked again, as was the successful recorded witness. Full installed-Codex
adoption remains unverified; the changed custody branch has focused predicate
coverage but has not yet inspected a new completed native attempt.

## Advisory closeout

The validated Doctrine release gate matched source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
The release commit remains `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`.
Initial packet `pkt-74d5f7e358da2b11` and five typed evidence records produced
`pkt-21dde246f1c131f7`, SHA-256
`21dde246f1c131f7329b549f18a05fb87b39a0eedfa0d1452465af754f2b3fd8`.
Both Markdown packets were read. Versions: corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`, schema `evidence-packet/3`.

Twenty-five obligations remain in the archived packet. Eighteen concern
deduplication (3), bulk-ingest populations (4), async UI (4), declarative
references (3) and ranking (4); these are nonmaterial to the device profile,
which changes and certifies none of those product paths. Three external-system
obligations and one evaluation/serving-parity obligation remain material to a
working native/provider integration or study-readiness claim, which is withheld.
Three monitoring obligations are nonmaterial because no service or paging
policy changed. Direct device/kernel reads, the source gate inventory and
provisional native-integration status are explicit in the evidence records.

Applied concepts: repository-contract precedence, evidence before intervention,
separation of semantic and structural changes, default-behavior preservation
and authority-bounded action. The AI failure modes check focused on arbitrary
device admission, opening an unchecked device, accidental terminal I/O, hiding
ENOSPC or nonblocking-read failures, bool/integer confusion and treating a
synthetic component witness as native-agent success. The TDD fixture exposed
the initial incompatibility and the missing import; neither failed result was
reclassified. No reviewer qualification or independent acceptance is inferred.

## Final custody

`/tmp/caplab-basic-devices-verification.json`, SHA-256
`1a56033d9a6ea88da5ad4eeae684583f42608013213c67021f7409ed79659c20`,
retains 23 artifact hashes, four current source identities, three prior source
snapshots and 11 embedded advisory scratch files removed after archival.
Source, snapshot, artifact and embedded hashes passed verification. The full
suite log and bundled-binary identity still match. Five citation observations
classified as valid packet citations. No Codex agent/model/provider attempt,
real credential, tracker write, message, push or historical research evidence
effect occurred. The next native diagnostic may adopt this committed profile
only under a new prospective authorization. The CAPLAB goal remains incomplete.
