# First reviewer case evidence registered and reconciled

Registered **40 content identities** for the scheduler and effort-parser
development cases in Garage, an independent `/nvr` copy, and CAPLAB's
append-only PostgreSQL admission tables. The read-only verifier reconciled
every identity. Replaying the same manifest added no registration or audit
event. Temporary access was revoked after verification.

The exact registration is
`reviewer-ranking-001-development-cases-001`, manifest SHA-256
`737dc5e9e7b9db5d3aa179b00487b053f94bace86373b25030e1312ed449fa50`.
It contains zero trial assignments, attempts, outcomes and model identities.
Registration preserves evidence; the [case judgment](decision-2026-09-10-reviewer-development-case-admission.md)
separately determines its permitted use.

## Source checks

The [authorization](authorization-2026-09-10-reviewer-case-evidence-registration.md)
names the historical copying and registration effects. Preparation checked
207 original receipt members and preserved eight uncompressed archives with
21,018 member entries. These include failed preparations, original source
snapshots, probes, compiled scheduler witnesses, process captures, verification
methods and the Council dependency closure. One derived Python bytecode file
was excluded and recorded. All uncompressed payloads passed the existing
credential scan. No original evidence was modified.

The full bundle is 657,318,760 bytes. Archive membership and every member's
bytes were rechecked against the original custody before registration. Source
commit, path, content hash and custody remain in the registered provenance
index and original plans. The case-scope document's base/change identities
also match those plans. The Go toolchain and module closure remain external,
hash-inventoried reproduction prerequisites. This is not a portable runtime
or a claim that all environmental dependencies have been registered.

Read-only recomputation of the scheduler record, scheduler graph and effort
verification results equals the three original JSON results exactly:

| Verification | SHA-256 |
|---|---|
| Scheduler record | `fa0497396d21e47f6284d0a2284ad09fe1fd529ed1cb44d5e6151677162ccca0` |
| Scheduler graph | `554256ea2e73ee15fc29850a6c703421a3232a6454eeb504f78ec040fd25c265` |
| Effort control | `93dd19be4780633fe545dacfdace8fe6eff9f1f3c6cc268ce8d52bf6c69db9d4` |

The public receipt retains the machine-checked hashes and comparison output.
No target-repository program, model or native reviewer executed in this step.

## Storage and access verification

Used the existing admission service and adapters at CAPLAB commit
`19d0400`, under a separate frozen plan. The expired Study 001 CLI and its
configuration were not used or changed. A root-owned stage pins 2,695 runtime
file/symlink entries. The writer could read but could not modify the source
bundle. The command rejected execution by an unauthorized role.

Source verification passed as `caplab_writer`. Admission wrote the frozen
manifest through the existing content-addressed stores and metadata service.
Verification ran as `caplab_verifier` with read-only Garage and PostgreSQL
permissions. The final PostgreSQL readback equals the complete prepared
manifest, and all 40 relational evidence records equal their manifest entries.
The prior Study 001 registration's manifest and body hashes are unchanged.

The writer and verifier Garage keys were revoked, their transient secret files
removed, and both PostgreSQL roles restored to `NOLOGIN` with zero sessions.
The 45-minute cleanup timer was disarmed only after successful cleanup.
A final readback confirms these states. No existing object was deleted.

Seven admission-service tests pass, covering source identity, credential
rejection, deduplication and refusal to freeze metadata after source drift.
The actual storage execution supplies the durable-store evidence. Tests alone
do not establish it.

## Receipt and limits

The [receipt](../product/studies/reviewer-ranking-001/case-registration-development-receipt.json)
anchors the 40 registered objects, 30 preparation files and 29 execution files.
Private preparation is under
`~/.local/share/caplab/reviewer-ranking-001/development/case-registration-1`;
the root-owned execution stage is
`/var/tmp/caplab-reviewer-case-registration-1`. No credentials remain there.
The first receipt-generation method used an incorrect provenance field name;
its failure and correction are retained. It changed no registered evidence.

Storage reconciliation proves the named custody properties. Case truth,
scorer validity, representative sampling and comparative reviewer performance
require their own evidence and judgments. No ranking is accepted here.
