# Verify advisory byte retention and refuse overwrite races

Date: 2026-09-08. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).
Baseline: `44d945f`.

## Authorization before execution

Repair `src/caplab/advisory/cas.py`, add
`tests/test_advisory_cas_retention.py`, document the bounded behavior in
`docs/product/advisory/README.md`, and complete this record. Tests may create
new synthetic strings, files, corruption, concurrent writers and injected
filesystem failures only under task-owned temporary directories. Every CAS
call in new probes must name its temporary root, or explicitly patch the CAS
default to that temporary root when exercising its write-through caller. Run focused tests and
`make check` before committing.

No live CAS contents, historical campaign or registered evidence may be read,
copied, repaired, registered, rewritten or purged. Do not run harvesting,
calibration, admission, model calls or services. Preserve existing key layout,
UTF-8 body identity, default root, missing-read result, public signatures,
callers, study admission boundaries, and `docs/designs/`. No migration,
credential access, scoring, ranking, placement or acceptance is authorized.

After verification, append bounded progress to CAPLAB-69's description,
preserving its open state and original text. Re-read before writing and stop
on concurrent change. No external comments or messages are authorized.
Authorization expires at commit. Remove only this task's doctrine scratch
after recording the receipt; retain synthetic test and tracker logs.

## Observed boundary and selected repair

`retain()` skips existing files without verifying their bytes. Thus callers
can receive a content identity even when the retained object no longer holds
those bytes. `load()` already rejects hash mismatch, but registration and
successful primary-source loads call `retain()` before returning. The existing
test named for retention mismatch exercises `load()`, not repeat retention.

Two new-object writers share `<hash>.tmp` and each uses `os.replace`. They can
both reach publication after writing the same temporary path, causing one
writer's rename to remove the other's source. A destination that appears
after the existence check is overwritten without a comparison.

Select verified reuse and unique staged writes followed by create-only hard
link publication. If another writer won, verify the retained bytes; never
overwrite that object. Return the hash only after verified retention. Preserve
the existing mismatch failure category and propagate storage failures. Close
read streams explicitly. Remove only the invocation's own temporary stage.
Synchronize the published directory entry; do not infer full crash recovery
or hostile-writer isolation from local success.

The existing runtime filesystem store uses this publication pattern, but its
required root modes, ownership and `objects/sha256/...` key layout differ.
Reusing that adapter directly would require a custody migration. Keep the
repair in the advisory CAS owner without changing callers or formats.

No change would retain the demonstrated unverified-return and shared-stage
paths. A lock alone would not detect an already corrupt object; a unique stage
with replacement would still overwrite a racing destination. Deleting or
repairing corrupt live objects is outside this authorization. Storage success
does not establish evidence admission, truth, independence or study eligibility.
CAPLAB-69's general admission and construction-record requirements remain open.

## Verification-scope correction before further execution

Inspection during the first full suite found that the existing
`PlanningCorpusTest._task` in `tests/test_advisory_corpus.py` calls `cas.retain`
without isolating its default. The focused and first full runs exercised that
helper with literal synthetic fixture strings against the live default CAS.
They cannot be described as entirely temporary-root verification. No store
inventory or historical evidence was requested, but the exact existing/new
object disposition of those calls is unknown. Do not inspect, repair or remove
live objects to retroactively assert isolation.

Extend this scoped authorization to isolate `PlanningCorpusTest` with a
per-test temporary CAS root, restoring the default before cleanup, and make
the helper's retention root explicit. Preserve all test expectations and
production defaults. Finish observing the already-running suite, then rerun
focused and full checks after the fixture repair. The new run is required
because of this demonstrated isolation gap, not an observation timeout.


## Reproduction and preservation checks

The pre-repair five-test run produced three failures and one error:
corrupt reuse returned success, the racing destination was overwritten, a
failed stage sync left temporary bytes, and one simultaneous writer failed
because its shared rename source was gone. The identical replay case passed.
These new probes all used explicit temporary roots. The sixth new test checks
that primary-source loading propagates a corrupt-retention failure while
preserving both source and retained bytes.

After the fixture isolation correction, 37 focused tests passed in 0.437
seconds. Empty and Unicode/CRLF bodies retain their exact UTF-8 identity;
identical replay preserves inode, mtime and bytes. Publication races use real
filesystem operations held at a two-writer barrier, with a five-second barrier
and ten-second future timeout. They verify results and remaining bytes, not
only that a mocked method was called. Injected sync failure is propagated and
leaves no published object or temporary file.

New stages use exclusive creation with normal file creation permissions under
the process umask, preserving the prior permission convention. Hard-link
publication requires local filesystem support; failure is propagated without
falling back to replacement. An object published before a later sync failure
may remain even though the call fails. Process death, disk loss, hostile
modification of the owned root, full directory-chain durability, and recovery
of orphan stages are not verified here. No cleanup scans or startup purges
are introduced. Hash identity and byte availability remain separate from
source truth and admission authority.

The deduplication identity is the SHA256 of exact UTF-8 body bytes, represented
by the existing `<first-two-hex>/<full-hash>` path. Equal body bytes may belong
to different source records; their provenance is owned by those records, not
collapsed into this byte-store key. A same-key conflict is an error, never
last-write-wins or silent success. This repair neither merges metadata records
nor substitutes body identity for source or study identity.

The public caller inventory is `calibrate.load_substrate_body`,
`planning_corpus.harvest_planning_tasks` and planning prompt loading. Their code and admission
meaning remain unchanged; corrupt retention now fails before their success
path. The shared helper owns this semantic repair. No dependency, public
signature, content-key layout, root location, body encoding or missing-read
contract changes. The test-only isolation correction is separately recorded
above and does not change production roots.

Retained logs: `/tmp/caplab-cas-retain-red.log`,
`/tmp/caplab-cas-retain-focused.log`,
`/tmp/caplab-cas-retain-make-check.log`,
`/tmp/caplab-cas-retain-isolated-focused.log`, and
`/tmp/caplab-cas-retain-isolated-make-check.log`.

## Advisory doctrine receipt

Release `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f` passed the retrieval-state
gate. Corpus `corpus-2026-07-12-a11702cc9217`; doctrine
`doctrine-f6bbb5196a3f8bf9`; retriever
`retriever-ec995ecdd083b2c8`. Final packet `pkt-7d76b83e845bd38f`,
content SHA256 `7d76b83e845bd38f44a277b068a239dab55c260238b5ebc672fac53827e66db9`.
Two typed-evidence gathering passes; execute ceiling bounded by ADR 0026 and
this scoped record.

Applied `implementation-placement-by-ownership` for the existing CAS owner;
`data-dedup-key-identity-completeness` to keep byte identity separate from source
records; `universal-repository-contract-precedence` to preserve custody and
admission policy; and `agent-conduct-authority-bounded-action` to disclose and
correct test isolation without inventing authority to inspect or purge the live
store. Retrieval does not authorize or accept the repair.

Remaining obligations are nonmaterial to the bounded repair claim:

| Concept | Remaining requirements | Scope disposition |
| --- | --- | --- |
| `data-ingest-population-scoping` | a dry-run enumeration with counts compared against expectation; the discovery pattern shown to match the specification's depth and class constraints; the input population specification; the specified input population stated precisely | No ingest, traversal or historical population collection is executed. New probes name temporary roots; the existing test lapse and correction are disclosed. |
| `implementation-config-reference-validation` | a load-time or gate check resolving every reference against them; a named-identifier failure on mismatch; the consumer's defined identifier and enum sets | No configuration schema or enum changes. Existing public roots and key formats remain unchanged. |
| `implementation-placement-by-ownership` | recurring change evidence when available | The reproduced failure and current caller path suffice; no recurring-change claim. |
| `implementation-rank-before-truncate` | the match-text composition enumerated field by field; the scan shown to score the full bounded set before truncation; the selection contract stated; the selection contract stated - relevance-ordered top-N versus first-N | No search, ranking or truncation is implemented. |
| `operations-external-capability-verification` | access to the real device or endpoint; an end-to-end verification artifact against the actual device or endpoint; the real system's own statement of its capability - device configuration output wire capture or endpoint self-description | Local temporary-filesystem behavior is tested. Full crash recovery, production-store audit and hostile-root isolation are explicitly unclaimed. |
| `operations-gate-authoritative-signal` | eval-versus-serving configuration parity; inventory of gates and the signals they observe; proof the check reads that signal rather than a derived view; the authoritative signal named for each gate | No external readiness or serving gate changes; actual retained synthetic bytes and raised errors are the bounded oracle. |
| `operations-symptom-cause-monitoring` | current page inventory classified symptom-versus-cause; golden-signal coverage with the error definition stated; the service's user-visible failure modes | No monitoring or service-health claim is made. |
| `task:defect-repair` | evidence-incidents | New deterministic reproductions establish the failures; no historical incident or live-store audit is needed. |


## Final verification and planning projection

After the isolation correction, `make check` passed 889 tests with four skips
in 119.896 seconds. No source or test changes followed this run. The earlier
full run also passed, but cannot substantiate isolated storage effects.
`/tmp/caplab-cas-retain-default-fixture-exposure.json` names the four candidate
object keys derived from the existing helper's literal fixture inputs, without
reading the live store. Prior object presence and exact effects remain unknown.
No cleanup or repair of those objects was attempted.

`git diff --check` and the new local documentation link checks passed. The
verification covers the exercised filesystem and caller behavior; it is not
independent acceptance, historical-store reconciliation or study admission.
All four doctrine citations classified as `valid-packet-citation`. The task's
packet, evidence and citation scratch files were removed after recording this
receipt; test, fixture-exposure and tracker receipts remain.

CAPLAB-69 was re-read immediately before updating and matched the full
pre-update snapshot. Read-back verified the exact appended description,
unchanged Backlog state and null completion time, with all unrelated fields
preserved. Only `updated_at` and `description_html` changed. No comments or
messages were sent. Receipts:
`/tmp/caplab-69-before-cas-update.json`,
`/tmp/caplab-69-immediate-cas-update.json`,
`/tmp/caplab-69-cas-update.ndjson`,
`/tmp/caplab-69-cas-update-result.json`, and
`/tmp/caplab-69-after-cas-update.json`.
