# Bind native attestation to retained capture bytes

## Decision and authorization

Under ADR 0026 and the active CAPLAB improvement goal, the primary agent
selects a prospective repair to the artifact-rater and retained ladder capture
paths. Attestation must describe the successfully preserved rollout, with the
same hash as the captured source bytes. A custody failure must not leave a
successful pin or accepted judgment. Existing custody must never be replaced;
an exact-byte retry may reuse it, while a mismatch refuses attestation.

Authorized effects are source changes, new disposable fixture executions,
tests, and this record. The public ladder execution boundary stays closed.
No live model calls, historical recovery, historical capture copying or
rewriting, ranking, placement, or tracker writes are authorized. Stop if a
check requires those effects. Revert the source commit to undo the repair;
delete only task-owned temporary fixtures and doctrine inputs. Verify original
counterexamples and relevant callers, then run the repository suite.

## Observation and selected repair

At parent `b043960`, artifact rating and ladder execution attest the source
rollout before copying it. Their later custody hash can therefore describe
different bytes. Artifact recovery can also attest the current source while
retaining an already-existing different capture. The ladder sets `pin_ok`
before copying, so a copy failure can leave the attempt classified as
behavioural despite failed evidence preservation.

The shared rollout owner will preserve one source snapshot with exclusive
creation and restrictive file permissions, attest the retained copy, and
check its hash against that snapshot. Exact existing bytes may be reused;
different existing bytes fail without replacement. Callers assign successful
pin/acceptance only after this operation succeeds. Invalid captures remain
available as failure evidence. This is a semantic repair, not refactoring.

Leaving the paths unchanged permits accepted identity and retained evidence
to disagree. Merely comparing a second source hash after copying still mixes
different reads of a mutable file. The selected operation ties the assertion
to the copied snapshot and verifies the retained bytes. It does not protect
against later out-of-band custody mutation, prove capture completeness, or
attest the provider's actual served model. CAPLAB-79 remains broader than this
repair, and the destination study remains unpreregistered.

## Verification

Three original caller-level counterexamples failed before repair:
`/tmp/caplab-capture-red.log`. A source mutation after the reader returned its
bytes led to an accepted rater record with a different retained rollout;
recovery accepted despite different existing custody; and a blocked ladder
copy destination still produced a behavioural attempt with a successful pin.
All inputs were newly authored fixtures with a fake native process. The
closed public ladder boundary was not bypassed for a live execution.

The repaired focused suite passes eight tests:
`/tmp/caplab-capture-green.log`. It covers the three counterexamples plus
rater custody failure, exact retry without replacement, restrictive new-file
permissions, malformed capture retention, symlink refusal, and a partial
write that fails both attestation and a replacement retry. The rater publishes
no accepted judgment on custody failure. The ladder records infrastructure,
no successful pin, and an unknown attempted status.

Full `make check` passed: 769 tests, four existing skips, 129.118 seconds.
Log: `/tmp/caplab-capture-make-check.log`. The full run includes the existing
public-ladder refusal test. `git diff --check` passed. No independent review
or study acceptance is claimed. The operation verifies byte identity during
capture; it is not a new crash-durable custody-domain implementation.

## Engineering guidance

The validated Pincite release at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f` supplied packet
`pkt-70382b9614a29c52`, content SHA-256
`70382b9614a29c525b5eacf3e2b9041b1960f66594df538dd41f8dd59101d487`,
doctrine `doctrine-f6bbb5196a3f8bf9`, and retriever
`retriever-ec995ecdd083b2c8`. Typed source, contract, and fixture evidence
informed the reassembly. Applied concepts were
`implementation-placement-by-ownership` and
`universal-repository-contract-precedence`; both structured citations were
validated and traced locally.

Material questions are the assertion-to-bytes relationship, write-failure
policy, caller credit, authorized scope, existing-custody preservation, and
verification. The source paths, decision, fixtures, and tests above address
those questions. The parser's UTF-8 contract stays unchanged, and capture
bytes undergo no text normalization. Generic obligations for bulk population
discovery, database deduplication, symbolic configuration references, top-N
selection, operational paging, and eval-versus-serving parity are nonmaterial
to this file-preservation repair. No live incident, provider behavior,
crash-durability, or full-system gate adequacy is claimed from local fixtures.
Temporary packet, evidence, and citation inputs are removed after tracing;
the verification logs remain available.
