# A real provider-lifetime defect and a bounded repair control

CAPLAB reproduced an actual Council runtime defect using independently
constructed HTTP interactions. In both the original implementation and the
sampled repair's base, response-body reads outlasted the configured timeout,
and cancelled requests still returned successful replies. The sampled repair
enforced those limits while preserving ordinary completion.

This is **one related failure family**, with executable evidence for named
properties. It is not 36 independent defects, a whole-patch clean label, a
qualified reviewer, or a ranking result. No reviewer or external provider was
called. Council's current checkout was not changed.

## Selection, source and requirement

The fixed feasibility sample selected Council change
`19fb83494cf3ec8e338d748f566be3df21088a40` without reading its correctness
outcome. Its first-parent base is
`32c9f09674b27b185abb7498883d9d3495ac4951`. Blame identifies
`9c66a76836245fbc8d203812a4a36f475341ce0e` as the original introduction of
the affected provider code. That earlier revision was added as a lineage
diagnostic, not substituted for a sampled case or represented as a random
draw. No defect was injected and no repair was reversed to manufacture a bug.
The lifetime defect predates `32c9f09674`'s Codex-handle change. Its presence
in that tree does not make it a defect introduced by that changeset, and must
not earn change-review credit on the separately sampled Codex-handle case.

At the base, `src/v3/deepseek-runtime.ts` creates a timeout and cancellation
listener around `fetch`, removes both in `finally`, and then consumes the
response body in its caller. The repair keeps body consumption inside that
lifetime and checks already-aborted signals before dispatch and tool work.

The base's `PROTOCOL-v3.md` already defines the member timeout setting and
states that zero disables the Council timeout. The runtime exposes a service
cancellation signal and typed cancellation failures. These contracts predate
the CAPLAB witness and its outputs. The HTTP response/body distinction also
exists in the [Fetch standard](https://fetch.spec.whatwg.org/#fetch-method).
Node documents the signal's already-aborted state and its notification
behavior in its [AbortSignal API](https://nodejs.org/api/globals.html#class-abortsignal).
Those sources explain the mechanism; the retained local execution establishes
what the installed Node 24.19.0 and exact Council revisions actually did.

The [development receipt](../product/studies/reviewer-ranking-001/timeout-development-receipt.json)
names the original source commits, trees, blobs, content hashes and lengths
for the protocol and runtime files. The full plan retains all 507 copied
source files across three snapshots. The repair author's regression tests
were inspected but were not executed or used as the witness implementation.
The witness calls the actual exported `runDeepSeekMemberTurn` function; it
does not extract/rewrite that function or substitute a toy implementation.

## Frozen method and observed results

The witness and [criteria](../product/studies/reviewer-ranking-001/development-witnesses/council-provider-lifetime/criteria.json)
were written before their first execution. Each source revision was run three
times per condition in a fresh Bubblewrap namespace, using only loopback HTTP,
read-only source/dependencies, a cleared environment, empty home, private
temporary storage and synthetic credentials. Each observation records the
loaded runtime hash, network-namespace identity, request count, ordered
server/cancellation/return events, actual result, and timing.

| Condition | Original introduction | Sampled base | Repair |
|---|---|---|---|
| Ordinary response | 3/3 successful replies; 24–26 ms | 3/3 successful replies; 23 ms | 3/3 successful replies; 23–25 ms |
| Body delayed 2 seconds; timeout 300 ms | 3/3 incorrect successes after 2,021–2,027 ms | 3/3 incorrect successes after 2,020–2,052 ms | 3/3 `provider_timeout` results after 318–319 ms |
| Cancel during body; timeout 5 seconds | 3/3 incorrect successes after 2,021–2,027 ms | 3/3 incorrect successes after 2,021–2,033 ms | 3/3 `provider_cancelled` results after 124–126 ms |
| Already-aborted service signal | 3/3 requests dispatched and successful | 3/3 requests dispatched and successful | 3/3 refusals before dispatch; zero requests |

Elapsed values are measured from entry into the exported runtime function,
so they include its local bookkeeping. For the delayed-body criteria, the
upper assessment bound is one second after headers, with the body scheduled
for two seconds; this tolerates scheduling overhead without mistaking an
eventual successful reply for enforcement of a 300 ms timeout. The body
completion event must also be absent before the timeout/cancellation return.

All 36 diagnostic processes completed normally in 36.8 seconds total. All
three ordinary controls passed on each revision. The two old revisions
violated each of the three lifetime/cancellation properties in all three
repetitions; the repair satisfied them. Input inventories were rechecked
before and after execution, including source bytes, Node/Bubblewrap hashes
and 6,633 dependency entries. No source or dependency drift was observed.

## Reproduction and custody

Authorization is recorded in
`authorization-2026-09-10-reviewer-timeout-witness.md`. The consumed run lives
at `/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/timeout-witness-1`.
It retains the plan, criteria, source snapshots, probe, per-slot launch and
completion records, raw stdout/stderr, terminal run record and verification.
Exclusive creation of the run-start marker prevents replay under the same
run identity. Source custody is local diagnostic material, not experimental
admission or imported human judgment.

Recompute the interpretation without rerunning the experiment:

```bash
python3 scripts/verify_reviewer_timeout_witness.py \
  --root /home/halbritt/.local/share/caplab/reviewer-ranking-001/development/timeout-witness-1 \
  --plan-sha256 f81ab8a4aea1751c6a4cf95b814d374a5a935d5eb868c939113ec6f0a88399b9 \
  --criteria-sha256 59c8d85a1a1a756fce3650180ef8601b7b6b4b0f369bc76375b30ea97513411d \
  --out /tmp/caplab-timeout-verification-new.json
```

The verifier checks the frozen identities, expected slot set, process
completion, source linkage, event chronology and behavioral conditions.
Missing or contradictory observations fail verification; they are not scored
as defects. Four adversarial tests cover late returns with a plausible timeout
code, success after a late body, unavailable/malformed observations, and a
cancelled status that hides an actual request. Execution isolation was checked
by the runner and retained launch arguments; this offline verifier does not
independently establish complete kernel capture or third-party attestation.

The repository check completed with **1,519 tests, four skips and no failures**
in 211.975 seconds, using the pinned WebSocket test dependency. Its log is
`/tmp/caplab-reviewer-timeout-check.log`. The tracked receipt's raw-file hashes
were rechecked against retained custody after verification.

## What this permits next

This family supplies actual defect evidence and a repair that is sound for
the observed timeout/cancellation behaviors. It does not establish that the
repair has no other defects or that any other sampled change is clean.
The 32-case sample stays intact and its overall outcome coverage remains
incomplete. Frontend coverage, other languages and other failure mechanisms
remain required work; this convenient executable case cannot replace them.

Review attribution is still open. An ordinary reviewer must see the original
change, base and legitimate requirements, without the future repair or hidden
witness. Credit requires a substantive finding attributable to the observed
failure. A keyword, location guess, generic warning, or a verification agent
discovering the defect on the reviewer's behalf cannot earn credit. Native
capture and automated finding verification must be challenged before this
family supports even a bounded reviewer comparison.

The original case and repair are development-exposed and cannot be reused as
unseen held-out evidence. Prior model exposure to the source is unknown. The
source history identifies Git authorship, not which model may have authored
or seen it. No production placement or historical qualification changes follow
from this diagnostic.
