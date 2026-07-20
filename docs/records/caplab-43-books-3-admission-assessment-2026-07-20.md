# CAPLAB-43 BOOKS-3 admission assessment

## Scope and authority

ADR 0029 authorizes a model-free assessment of the historical BOOKS-3
Doctrine-injection probe through `2026-08-03T23:59:59Z`. It permits an
admission recommendation and later decision, but not historical evidence
admission, probe execution, model calls, or edits under `history/ethogram/`.
Plane is the planning projection.

This assessment read exact Git objects and current non-secret Pincite custody
metadata. It did not copy, register, rewrite, purge, or execute a historical
artifact.

## Provenance ledger

The historical series has three CAPLAB-custodied commits and one external
Pincite source commit:

| Role | Commit | Exact artifacts and Git blobs |
|---|---|---|
| Fixture source | Pincite `95ddd1c408348f2079180476fb188262cfe43985` | `doctrine/testdata/adversarial-doctrine/manifest.json` at `85fcfa6b53ffdd53fc33a2600236b7a184ec62c7`; fixture schema at `9a718ef52e74e054e6113c95382553acd7d9cdc0`; ADR 0008 at `48edda8a174c4b7b698f7b1de4c7311206674ef8` |
| Primary preregistration and grader | `a7e4bffc4b582cc29da9f00452429138b9b73bab` | primary preregistration `9e6190afac70bd1ee2cd034455a82f1888c716fe`; summary schema `1a17443af934839cd9bc0236a97922e4aacfb8ff`; runner/grader `abcc383be3c7272a567e4f08ee1250e17ebdbd63`; tests `be8c33b3596cf656764e7c4829460b3640c387cc` |
| Primary execution record and diagnostic preregistration | `ebcdc772dc1b6500671c281ab2b10cc7dbab70d3` | primary summary `c0002678898853462f08ad15022a1a1479163343`; diagnostic preregistration `4ce04cea6348d0d90d68ff64666b959b36c95b96` |
| Diagnostic execution and result | `c5ff6d2d12db29fc7b5b029596f04d2279ea180d` | diagnostic summary `169ff9a2bbdea5a42a44676b605e3db1699b670f` |

The first commit freezes the six cases, prediction, falsifier, failure classes,
and aggregate schema before execution. The second records the primary
execution summary, then separately preregisters one diagnostic prompted by an
output-budget infrastructure failure. The third records the diagnostic result.
The diagnostic remains supplementary and does not replace the primary row.

## Historical observations

The declared subject was model alias `qwen3.6-35b-a3b` through a local
OpenAI-compatible endpoint at temperature zero. The primary ceiling was 1,024
tokens; the diagnostic changed only that ceiling to 4,096 tokens. Both used one
attempt per six fixture classes and a 120-second timeout.

The primary aggregate records five mechanical passes and one infrastructure
error. The error had reasoning content but no final content after a length
finish. The separately preregistered diagnostic records six mechanical passes.
Five primary cases share one response digest; the delimiter case has another.
The diagnostic repeats that pattern after the formerly missing case completes.

The grader checks exact canary presence in model output and captured world
files, exact citation or path exposure for the adversarial source, presence of
the expected real-document identifier, and run errors. It stores aggregate
classifications plus response and world-file hashes without model prose.

These are historical-record observations. They are not CAPLAB-registered trial
observations and have not been independently regraded in CAPLAB.

## Reusable instrument behavior

The following behavior is worth carrying into a fresh design:

- fixture text and structural-contract ownership remain separate from probe
  execution and grading ownership;
- cases, predictions, falsifier, hard failures, and infrastructure failures are
  frozen before a call;
- fixture manifest and schema identities are checked before execution;
- model output and world artifacts are both inspected for canaries;
- model and infrastructure failures remain distinct;
- a data-dependent diagnostic is preregistered and reported separately rather
  than rewriting the primary attempt; and
- repository summaries omit model prose while retaining aggregate and content
  identities.

These are design observations. Reusing them requires a new CAPLAB-native
implementation; it does not admit the historical code or tests.

## Registration gaps

The historical series cannot satisfy current CAPLAB attempt registration:

- raw requests, responses, and run directories were retained only in session
  scratch and are not in the preserved Git tree;
- the response and world-file hashes cannot be resolved back to registered
  bytes, so CAPLAB cannot independently regrade the recorded attempts;
- model identity is a mutable alias without provider response identity,
  checkpoint identity, observation time, or route attestation;
- agent configuration omits a named harness/runtime and version, adapter,
  complete tool surface, environment, and hardware;
- administration does not bind the final assembled request bytes, document
  order, or per-case request digest;
- no sealed trial assignment, randomized order, attempt timestamp, latency,
  token usage, cost, replacement disposition, or preservation manifest exists;
- one repetition, one subject, and no clean or manipulation controls cannot
  support a task-family capability inference; and
- no named human disposition exists, which is acceptable for the mechanical
  historical claim but cannot be inferred from the aggregate.

Hash-only summaries do not repair missing evidence bytes. A later admission
authorization could register the historical documents themselves as records,
but it could not turn the absent run bytes into complete CAPLAB attempts.

## Shortcuts, leakage, rivals, and claim ceiling

The expected document identifier and an explicit statement of the correct
ownership relationship were supplied in every request. A pass can therefore
reflect copying the trusted document, simple citation compliance, or preference
for the first document rather than resistance to adversarial instruction.

The grader detects exact canaries and locators, not semantic paraphrases or
indirect effects. It has no clean control to detect a subject that ignores all
secondary documents, no counterbalanced document order, no answer-content
oracle beyond the expected identifier, and no treatment-fidelity observation.
The repeated response digest across five distinct attacks is consistent with a
single invariant answer and leaves fixture-specific processing unresolved.

Other credible rivals are deterministic temperature-zero behavior, case-name
or metadata leakage, shared fixture phrasing, output-ceiling effects, local
endpoint behavior, and grader blind spots. The diagnostic resolves the one
observed missing-final-content failure at a larger ceiling; it does not resolve
those rivals.

The maximum historical claim is: under the declared local alias and frozen
mechanical grader, five of six primary records were classified as passes and
one as infrastructure failure; a separately preregistered larger-output
diagnostic classified all six as passes. The series cannot establish general
prompt-injection resistance, Doctrine safety, content-boundary capability,
provider behavior, causal treatment effect, cross-task capability, placement,
or training eligibility.

## Recommendation and decision routing

**Recommendation: redesign.** Preserve the series as historical design
evidence; do not admit its attempts or aggregates as CAPLAB model evidence.

A future Doctrine-specific CAPLAB study would need fresh registered fixture and
request bytes, full layered identities, sealed assignments, raw-attempt
preservation, independent regrading, clean and manipulation controls,
counterbalanced document order, semantic leakage checks, repetitions, held-out
cases, and a claim-specific capability card. The expected answer must not be
handed to the subject as the sole trusted document. CAPLAB should retain the
primary-versus-diagnostic separation and model-versus-infrastructure boundary.

ADR 0035 records the delegated decision. It authorizes no redesign execution.

## Doctrine receipt and verification

The assessment used Pincite packet `pkt-9fc7fce7214f9cd5`, packet-file SHA-256
`c5acee790c9e252671bd7d43f4c70c8aa34d491b254f28a719c89aa010bab124`,
packet-content SHA-256
`9fc7fce7214f9cd51b7ac721de4754ef4fd0e423c5d62674870e39e792f38018`,
corpus `corpus-2026-07-12-d2ea7b94a1ce`, doctrine
`doctrine-be3dc0e2873014de`, and retriever
`retriever-52068c631d23be23` from the validated release home.

Verification re-resolved every listed commit, path, and Git blob; confirmed the
historical tree contains summaries rather than raw run directories; ran the
complete CAPLAB repository gate; and checked local Markdown links and diff
hygiene. These are assessment and technical-verification observations, not
historical evidence admission, independent study verification, or acceptance.
