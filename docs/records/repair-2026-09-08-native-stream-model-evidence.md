# Preserve contradictory native streaming model evidence

Date: 2026-09-08. Baseline: `067cf6b`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Repair `assess_native_review_model` in `src/caplab/review_dissent/native.py`,
add `tests/test_review_stream_identity.py`, extend the existing identity-stop
tests where necessary, update the review-dissent README and add a versioned
contract. Permitted effects include this record, synthetic in-memory events,
new temporary fixture captures, focused/full tests, a baseline parity probe and
a local commit. Read current code/contracts and official public documentation.
No native launch, model spend, historical capture inspection/copy/rescoring,
source binding renewal, tracker write or external message. Preserve existing
launch commands, frozen manifests, task semantics, unrelated files and services.
Preserve `docs/designs/`. Retain verification probes/logs; delete only named
doctrine scratch after recording receipts. Authorization expires at commit.
Stop on unexplained changes to ordinary trace results or required broader effects.

## Selected repair and preservation boundary

Current assessment reads completed assistant model fields and system fallback
notices, but ignores `stream_event.message_start` model fields and explicit
fallback markers inside message content or usage iterations. Select rejection
of contradictory evidence on those exposed surfaces. No change leaves a
matching final message able to hide an earlier reported substitution. Replacing
the harness or enabling new capture flags would change the Binding and is not
part of this repair.

Keep existing initialization/completed-message/terminal requirements; partial
messages alone cannot establish completion or model agreement. Retain ordinary
result fields exactly, adding optional streaming observations only when present.
Keep aggregate `modelUsage` advisory: auxiliary model names alone still do not
prove primary response authorship. A structured `fallback_message` iteration is
an explicit fallback marker, not merely an auxiliary usage name. Any explicit
fallback withholds attribution even if its model details are absent. Missing or
malformed partial identity evidence prevents agreement, while explicit mismatch
still takes precedence. Unknown well-formed partial event types remain retained
raw evidence without new identity meaning.

This is a semantic repair of native-reported configuration consistency, not
provider authentication, independent capability verification or live emission
proof. Model mismatches must still withhold the score and halt the existing
continuation gate while preserving assigned slots. Native capture integration,
session linkage and model/account compatibility remain unverified.

## Execution and evidence

The initial eight new tests produced 17 failing assertions and one error in
0.069 seconds: `/tmp/caplab-native-stream-red.log`. The baseline reported
`native-model-match` despite synthetic off-pin partial models or explicit
fallback content/usage markers. It also accepted malformed partial identity
surfaces. The missing `stream_models` observation caused the expected-field
error. These are local synthetic reproductions, not an allegation about a
historical episode or a live CLI/account.

The repair adds optional line-addressed partial model/error observations and
source-addressed fallback observations. It checks only named native fields;
quoted examples, tool arguments and unrelated auxiliary usage names are not
interpreted as substitutions. The parser owns newly decoded event dictionaries
within one synchronous call; input bytes and the caller's configured subject
are borrowed without mutation. No worker, retained cache or shared mutable
state is added. Duplicate evidence surfaces are retained without claiming
independent events. The new contract states the precise field coverage and the
remaining sequencing, identity and capture limits.

Twenty focused tests passed in 1.192 seconds:
`/tmp/caplab-native-stream-focused.log`. This includes eight new parser/scoring
tests and the existing continuation suite with one new partial-model case.
The continuation case writes a new synthetic capture, seals its observation,
reloads custody and verifies that preparation refuses the next slot before
rendering; the original stdout and two unattempted primary slots survive.
Matching partial messages preserve the requirement for a completed response.
Missing/malformed partial fields withhold attribution, and an explicit fallback
still takes precedence over missing evidence.

The baseline probe compares complete assessment dictionaries across 48 ordinary
traces: matching/mismatching initialization, matching/mismatching/missing
response model, success/error result, auxiliary usage and final-newline presence.
Every field matches `067cf6b`; no comparison field is excluded. A retained
counterexample changes from `native-model-match` to `model-mismatch` solely
because the partial model observation is no longer ignored. Probe and result:
`/tmp/caplab-native-stream-parity.py` and `/tmp/caplab-native-stream-parity.json`.

Official Claude streaming and fallback documentation was opened on September 8;
the exact URLs and supported fields are linked from the
[contract](../product/contracts/native-stream-model-evidence-v1.md). The documents
support fixture shapes, not installed emission or API/proxy substitution. Source
and direct-import checks are retained in
`/tmp/caplab-native-stream-source-check.json`. The pre-existing unused `tempfile`
import is preserved outside the repair scope. Python 3.12.3 and the repository's
existing `make check`/unittest route are used, with no dependency change.

The accepted capture design supplies the expected need for partial observations;
no-change risk is the reproduced false agreement. The bounded repair preserves
ordinary outputs and leaves native launch configuration, frozen source seals,
publication and historical replay untouched. Recovery remains the existing
identity stop: no retry or re-attribution is introduced. Review this boundary
again if native field formats or capture requirements change; do not treat
this check as authentication or a full transcript validator.

## Doctrine receipt

The release retrieval gate passed at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Corpus:
`corpus-2026-07-12-a11702cc9217`; doctrine: `doctrine-f6bbb5196a3f8bf9`;
retriever: `retriever-ec995ecdd083b2c8`. Final packet:
`pkt-e38f92a68c1a0d3c`, content SHA-256
`e38f92a68c1a0d3cdacb7747c6849932128883c5dc3c2f9abb911e4e119de965`.
One evidence-gathering pass supplied five typed records. Four citations
classified as `valid-packet-citation`: `universal-evidence-before-intervention`
for the false-agreement reproduction; `universal-preserve-behavior-by-default`
for whole-result parity; `implementation-explicit-failure-policy` for score
withholding and the existing preparation stop; and
`agent-conduct-authority-bounded-action` for synthetic-only execution.

All fifteen unmet obligations are nonmaterial to the scoped parser repair:

| Concept | Exact unmet requirements | Reason |
|---|---|---|
| `domain-identity-entity` | expert distinction of sameness over time; identity scenarios; identity source and comparison rules; lifecycle or reference consequences | No Entity, identity lifecycle or domain identity rule is introduced. The repair preserves the existing exact configured/native model comparison. |
| `domain-language-model-loop` | authoritative examples; authoritative expert examples; feedback from implementation and usage; model expressed in executable behavior; terms whose meanings affect decisions | No new domain model or terminology is selected. The existing glossary and accepted capture design govern the narrower field-parsing repair. |
| `domain-modeling-investment-gate` | business differentiation and product lifespan; business-value and expert-access evidence; expert access and feedback cadence; recurring ambiguity, contradiction, or rule defect; team capacity to sustain the model | No deep modeling investment or expert-access claim is made. This is direct parser and failure-policy work. |
| `python-repository-shaped-idiom` | formatter linter and type-checker configuration | No formatter/checker policy change or static conformance claim. |

## Completion checks and remaining work

`make check` passed 1,008 tests with four skips in 127.224 seconds:
`/tmp/caplab-native-stream-make-check.log`. Verified source/test hashes remained
unchanged after that run began. The documentation pass checked named fields,
versions, local links and the limits on emission/completeness claims. It kept
the distinction between explicit fallback markers and mere auxiliary names.

The consolidated receipt is `/tmp/caplab-native-stream-verification.json`.
Eleven named doctrine scratch files were removed after retaining packet,
obligation and citation receipts; regression logs and parity evidence remain.
The refreshed planning snapshot is `/tmp/caplab-native-stream-roadmap.json`.
No planning projection was mutated. Native session/child capture, bounded
adapter integration, containment and representative legibility/cost/blinding
measurements remain required. The repair does not complete the CAPLAB goal.
