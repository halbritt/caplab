# Reddit recovery exceeds its promised deadline during an active response

The selected newsroom change `544f7e3c43eaa0c06cf17d9e93613d33c0cfb66f`
adds a Reddit recovery path whose documented three-minute budget does not
bound an active HTTP response. Two original `RedditAdapter.harvest(24)` calls
completed successfully after 190.12 and 190.14 seconds, persisted the response
and marked it live. The configured recovery budget remained 180 seconds.

This is the first bounded behavioral witness for a selected change in the
501+ line stratum. It covers the recovery deadline, candidate filtering and
pool reopen. Worker deadlines, curator retries, trace handling, timers,
Twitter behavior and other parts of this large change remain unverified.

## Observations and controls

Each condition ran twice through unchanged production Python source, real
urllib HTTPS, the original feed parser and a disposable SQLite database.
The local endpoint served the same valid Atom feed containing one fresh,
one stale and one future post. A fresh adapter then read the harvested pool.

| Property | Ordinary response | Active slow response |
| --- | --- | --- |
| Harvest duration, repetitions 1 and 2 | 0.032 and 0.045 seconds | 190.119 and 190.142 seconds |
| Configured recovery budget | 180 seconds | 180 seconds |
| Largest recorded delivery gap | Under 0.001 seconds | Under 1.002 seconds |
| Socket inactivity timeout | 30 seconds | 30 seconds |
| Harvest result | Success | Success beyond budget |
| Candidate set | Fresh post only | Fresh post only |
| Durable feed | Exact response stored, status live | Exact response stored, status live |
| Fresh adapter reads persisted candidate | Yes | Yes |
| Additional HTTP request on reopen | None | None |

The slow endpoint sends one whitespace byte per second for 190 seconds,
then the complete feed. The resulting body is valid Atom. Recorded byte
activity stays well below the unchanged socket inactivity timeout, so this
exercises a response that remains active past the overall budget. Source
clocks, sleep calls, deadline constants and request functions are not patched.
The real monotonic clock bounds the harvest independently of its result.

The checker separates eventual success, deadline compliance, filtering and
persistence. It checks the original constants, endpoint timing against the
harvest interval, response validity, SQLite bytes, capture inventories and
agreement between repetitions. Four checker tests cover successful but late
persistence, invalid inactivity gaps, missing endpoint requests and the
distinction between ordinary completion and timely rejection.

## Expected behavior and attribution

The selected change's README explicitly describes a three-minute recovery
budget. Its newly added `newsroom/sources/reddit_state.py` sets
`RECOVERY_SECONDS = 180`, but checks remaining time only between requests.
It calls the original `feeds._fetch_feed`, whose urllib request has a
30-second inactivity timeout followed by a full-body read. The success path
stores and returns that body without another deadline check. The observed
delivery and elapsed time establish the mismatch with the promised bound.
The pre-execution criteria allowed two seconds of timing tolerance; both
slow runs exceed even that allowance by more than eight seconds.

The module and harvest API are new in this selected change. Its base
`1bfe5a656bcb2c663891afd5f980211a3ef144a8` was materialized to establish
source identity and absence of the new module, but was not executed. No
passing base execution is invented for an API that did not exist. The
unbounded read primitive predates the change; the defect assessed here is
the new recovery path's failure to enforce its newly promised overall bound.

This establishes a reproducible trigger, not its prevalence on real Reddit.
The endpoint is an environment fixture. No model reviewer was measured by
this execution, and test success supplies no reviewer-quality score.

## Execution and custody

The [first authorization](authorization-2026-09-10-reviewer-reddit-recovery-witness.md)
and [corrected authorization](authorization-2026-09-10-reviewer-reddit-recovery-witness-2.md)
name the exact historical copies, private endpoint/database and bounded
execution effects. Attempt 1 failed to bind HTTPS port 443 inside the private
namespace before constructing the adapter or running a harvest. Its plan,
runner, output and process receipts remain preserved as a fixture failure.

Attempt 2 adds only the isolated namespace's low-port binding capability,
using the already established local HTTPS mechanism and a fresh test
certificate. Source, feed, probe and criteria remain unchanged. The user and
network namespaces isolate this capability from the host. Source is read-only;
real provider credentials, home, queues and services are not exposed.

Raw Git blobs preserve 91 source/configuration files across the change and
base. Source, fixture and runtime identities were checked before and after
execution. Four executions finished in 382.30 seconds and retained 24 capture
files, including complete response bodies, delivery timestamps and original
SQLite databases. The separate verifier assesses the retained observations
against the criteria frozen before execution.

Private custody is
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/reddit-recovery-witness-2`.
The [receipt](../product/studies/reviewer-ranking-001/reddit-recovery-development-receipt.json)
pins 57 current artifact hashes, the failed attempt's custody, source
identities and verification. Plan SHA-256:
`c34639643cbc3a0134d9d450192c73e8dc3fd82b071051f8f50fba2790db2b8c`.
Verification SHA-256:
`ae90ff38769a59b3fafbd68da7f92f278cb7267233902c917577bf38e5b8005d`.

`make check` passes: 1,535 tests in 209.25 seconds, with seven skips.
All 68 current, failed-attempt and verifier-support receipt hashes match;
the verifier reproduces exactly and all 32 coverage identities remain in
the fixed selection. These checks validate the repository and retained
evidence, not the unfinished ranking instrument.

## Effect on the ranking study

The frozen sample reproduces exactly from its content-checked census. This
change's base, tree and changed blobs match that selection. The
[coverage projection](../product/studies/reviewer-ranking-001/FEASIBILITY.md)
now records seven bounded changes, two trees executed only as other cases'
bases and 23 changes without an established behavioral witness. The selected
base's separate Particle change remains pending because copying source does
not verify behavior. No selected case is replaced.

The deadline failure is a candidate defect family for later admission.
Passing filtering and persistence establish only the named control
properties. The full change is not labeled clean. Case admission, remaining
coverage, unseen natural-review scoring and held-out native comparisons
remain open. No reviewer ranking is accepted.
