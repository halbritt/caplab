# Clear the environment before starting the native launcher

Date: 2026-09-08. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).
Baseline: `f436fe1`.

## Authorization before execution

Repair the outer process environment in
`src/caplab/preference/native_live.py` and
`src/caplab/review_dissent/native_live.py`, add new synthetic tests under
`tests/test_native_launcher_environment.py`, and complete this record.
Use only synthetic ambient values and temporary input/custody fixtures.
Native model, auth and version preflight responses may be replaced inside
tests; do not invoke actual native harnesses or authentication endpoints.
Local Python subprocesses may inspect their own synthetic environment.
Run focused tests and `make check` before committing.

After verification, append progress to CAPLAB-85's description, preserving
its open state and original description. Re-read before updating and stop on
concurrent change. No external comments or messages are authorized. Preserve
historical source/capture custody, frozen manifests, model identities, child
namespace construction, network policy, execution authorization/expiry checks,
and `docs/designs/`. No model spend, historical runner reopening, secret reads,
credential rotation, campaign execution, ranking or placement is authorized.
This authorization expires at commit. Remove only this task's doctrine scratch
after receipts are recorded; retain test logs and tracker receipts.

## Observation and selected repair

The shared contained command specifies `--clearenv` and explicit child HOME,
PATH and LANG. Its outer `subprocess.run` calls omit `env`, including the two
native version probes, bubblewrap version probe, two auth status probes and
both preference/review trial execution paths. Thus the Python subprocess
boundary still passes ambient host variables to the launcher, before its
child-environment policy takes effect.

Select an explicit outer environment containing only fixed PATH and LANG.
Construct a fresh mapping for each call and share that policy from the
existing containment owner. The selected harness configuration remains in
the explicit contained command and mounts. No host credential, proxy, model,
loader, shell, or Python environment override is inherited through this outer
environment mapping. This is a bounded process-environment guarantee, not
proof of provider identity or complete containment.

Leaving the child-only clear unchanged preserves the identified gap. A denylist
would miss unenumerated ambient controls. Disabling all network access would
also block the native harness's provider connection and would require a
separate execution design; it is not part of this repair.

The closed ladder stays closed. CAPLAB-85's historical `run_episode.sh` is not
an active repository runner found in this inspection; this repair does not
claim to modify it. The future shakedown still needs a sealed launcher/runtime
bundle, explicit model pinning and observation, and verified full containment.
The old tracker statement about credential rotation remains outside this
authorization; no credential state is inspected or claimed.

## Scoped fixture amendment before execution

The first focused run passed the environment probes but five existing review
tests failed in setup: their temporary manifest refreshed only the review
runner digest, leaving the shared runtime digest stale. The loader correctly
rejected it. Authorize updating `tests/test_review_dissent_native_live.py` to
bind both current sources in its newly named temporary manifest, and extending
its source mismatch test to protect both checks. No committed campaign
manifest or production validation rule changes.

## Verification and limits

Before repair, two tests produced three failures: all five preflight calls
omitted the outer environment, and a real local Python child under each
production trial executor inherited the synthetic ambient mapping. After
repair, each child reports exactly `PATH=/usr/bin:/bin` and `LANG=C.UTF-8`.
Preflight responses are test doubles; all five invocation arguments have that
mapping and each receives a fresh dictionary. These arguments are the
process-boundary policy under test, not a claim about provider responses.

The focused run passed 25 tests in 0.210 seconds, including preference and
review source-digest rejection, unauthorized preparation refusal, shared
namespace construction and the closed ladder. The temporary review fixture
now binds both current source files. The production loaders still reject
stale source hashes. No frozen manifest was resealed.

`make check` passed 883 tests with four skips in 127.542 seconds. No source or
test changes followed that run. This is technical verification by the executing
agent, not independent acceptance.

The preserved consumers are native preference preflight/trial execution and
native review preflight/trial execution. Their command arguments, namespace
mounts, provider network policy, model selection, capture, timeout/failure
handling, and authority/expiry checks are unchanged. This is a semantic
repair to inherited process state, with no structural campaign or dependency
change. The first-divergence hypothesis was an omitted outer `env` argument;
the synthetic child observation distinguished it from a defect in bubblewrap's
inner environment policy without invoking bubblewrap or a native harness.

The demonstrated current risk is ambient inheritance at these seven process
invocations. The selected repair costs one shared helper and six call-site
arguments. No change would retain that observed behavior; an enumerated
denylist would leave unknown variables inherited. Full native compatibility
remains unverified: no real native version, auth, or provider call was made.
Reopen on an authorized representative shakedown that requires additional
outer environment state; freeze any deliberate addition in its new Binding.
Do not restore ambient inheritance as an implicit compatibility fallback.

CAPLAB-85 remains open. These tests establish a bounded environment property,
not complete containment, model observation, study readiness, acceptance,
reviewer capability, or a selection recommendation.

Logs retained locally:
`/tmp/caplab-launcher-env-red.log`,
`/tmp/caplab-launcher-env-focused.log`, and
`/tmp/caplab-launcher-env-make-check.log`.

## Advisory doctrine receipt

Validated release `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`; corpus
`corpus-2026-07-12-a11702cc9217`; doctrine
`doctrine-f6bbb5196a3f8bf9`; retriever
`retriever-ec995ecdd083b2c8`. Final packet `pkt-b245c1adae341ba0`,
content SHA256
`b245c1adae341ba0630d1ca6d919d4fff7449fc774005234fd6aa6f3daab53fc`.
Two typed-evidence gathering passes; authority ceiling execute under ADR 0026.

Applied `implementation-placement-by-ownership` for the existing shared owner,
`universal-evidence-before-intervention` for the reproduced child boundary,
`universal-preserve-behavior-by-default` for protected launch and custody policy,
and `operations-external-capability-verification` to withhold live compatibility.
Advisory retrieval does not authorize or accept this repair.

Remaining obligations are nonmaterial to this bounded claim for the reasons
below; external verification remains required before a live compatibility claim.

| Concept | Remaining requirements | Scope disposition |
| --- | --- | --- |
| `data-dedup-key-identity-completeness` | an explicit enumeration of the record's identity dimensions matched against the key's columns; logical-identity definition of the affected record; the conflict-handling semantics at that key - abort update or silent drop | No record identity, key or conflict policy changes. |
| `data-ingest-population-scoping` | a dry-run enumeration with counts compared against expectation; the discovery pattern shown to match the specification's depth and class constraints; the input population specification; the specified input population stated precisely | No ingestion, traversal or population selection occurs. |
| `implementation-config-reference-validation` | a load-time or gate check resolving every reference against them; a named-identifier failure on mismatch; the consumer's defined identifier and enum sets | No identifier or enum schema changes; existing source-digest rejection is exercised. |
| `implementation-placement-by-ownership` | recurring change evidence when available | Current shared ownership and the direct reproduction suffice; no recurring-change claim. |
| `implementation-rank-before-truncate` | the match-text composition enumerated field by field; the scan shown to score the full bounded set before truncation; the selection contract stated; the selection contract stated - relevance-ordered top-N versus first-N | No ranking, search or truncation is introduced. |
| `operations-external-capability-verification` | access to the real device or endpoint; an end-to-end verification artifact against the actual device or endpoint; the real system's own statement of its capability - device configuration output wire capture or endpoint self-description | Material to live compatibility, which is explicitly withheld; nonmaterial to the synthetic process-environment property. |
| `operations-gate-authoritative-signal` | eval-versus-serving configuration parity; inventory of gates and the signals they observe; proof the check reads that signal rather than a derived view; the authoritative signal named for each gate | No new external readiness or serving-parity claim; the actual synthetic child environment is the bounded oracle. |
| `operations-symptom-cause-monitoring` | current page inventory classified symptom-versus-cause; golden-signal coverage with the error definition stated; the service's user-visible failure modes | No service monitoring, paging or operational coverage claim. |
| `task:defect-repair` | evidence-incidents | No historical incident access needed; the new synthetic reproduction establishes the bounded defect. |

All four recorded doctrine concept citations classified as
`valid-packet-citation`. The task's scratch packets, typed evidence and citation
files were removed after recording this receipt; test and tracker logs remain.

## Planning projection execution

Re-read CAPLAB-85 and verified the full issue data equaled the inspected
snapshot before appending a description-only progress entry. The read-back
verified the exact description and unchanged Ready state, null `completed_at`,
and unrelated issue fields; only description, update time and updater changed.
No comments or messages were sent. Receipts:
`/tmp/caplab-85-before-environment-update.json`,
`/tmp/caplab-85-environment-update.ndjson`,
`/tmp/caplab-85-environment-update-result.json`, and
`/tmp/caplab-85-after-environment-update.json`.
