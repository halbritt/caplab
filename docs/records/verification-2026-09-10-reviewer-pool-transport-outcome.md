# Undelivered questions and missing answers entered pool measurements

An independent subprocess witness reproduces the defects addressed by fixed
sample change `c8f097a0934bfa380e7c9c5cda4f11ea4ac2b454` in CAPLAB's historical
pool runner. The original runner sends oversized argument prompts to stdin,
which its argument-mode endpoint does not read. It also counts a pair with
one absent response as usable and writes numeric aggregate rates.

The sampled repair restores oversized pool-body delivery and excludes absent
or timed-out responses. It still counts a parseable object without a verdict
as a usable response. This remaining validity gap predates the repair. The
successful fixes therefore supply bounded preservation evidence, not a
whole-patch clean label.

## Observed outcomes

Three exact revisions were executed twice: introducing commit
`9cb8d6561176e9d3d7b530eae3f40954744d1766`, sampled base
`1517d426afbced67422a4097c0d5fd92d7200287`, and sampled repair
`c8f097a0934bfa380e7c9c5cda4f11ea4ac2b454`. Nine conditions per execution give
54 diagnostic observations. Both repetitions agree on all assessed
properties. Related revisions and repetitions do not create independent
review cases.

| Condition | Introduction and base | Sampled repair |
| --- | --- | --- |
| Argument prompt, 100,000 bytes | All bytes received | All bytes received |
| Argument prompt, 100,001 bytes | Endpoint launches with no prompt; silent stdin fallback | Explicit refusal before endpoint launch |
| Stdin prompt, 100,001 bytes | All bytes received | All bytes received |
| Healthy inline pair | Both bodies and scripted verdicts received; one usable pair | Same |
| Healthy oversized pair | Both endpoints receive no prompt; pair discarded | Both complete bodies read from spill files; one usable pair |
| Empty control response | One usable pair; false-alarm rate 0 | Pair discarded; rates absent |
| Empty mutant response | One usable pair; catch rate 0 | Pair discarded; rates absent |
| Timed-out mutant | One usable pair; catch rate 0 | Pair discarded; timeout recorded; rates absent |
| Parseable mutant object without a verdict | One usable pair; catch rate 0 | Same inherited validity failure |

The last condition returns `{"status":"completed-without-a-verdict"}` from
the endpoint. The original runner extracts a dictionary and the repair's new
guard accepts it because `doc` is not `None`. The resulting row has no mutant
verdict but contributes one usable pair to `summary.json`. This is an observed
denominator error against the required response contract; it is not a
judgment about whether a model's free-text finding is correct.

The exact original `invoke` and `run_pool` functions run without patching.
The witness checks the original persisted result row and aggregate summary,
not merely a reconstructed calculation. Thus the missing-response defect is
visible in the pool's actual output denominator.

## Independent basis and what the fixture measures

The product specification requires valid attempts and reported missingness
and failures for estimates. Its relevant revision predates these changes:
`docs/product/specs/spec-agent-capability-lab.md`, last changed at
`63e99e54e3fba98dfa18a6f4d4b42b9b2b9d4985` on 2026-07-20. The historical
prompt in `calibrate.py` explicitly enumerates the allowed verdicts. Neither
no response nor an unrelated JSON object is one of those verdicts. The
declared `prompt_mode` and the endpoint's actual input channel independently
establish whether the intended bytes arrived.

The endpoint is a new deterministic Python subprocess. It reads only its
declared argument or stdin channel, or the spill file explicitly named in the
prompt. It retains the complete received prompt and body with byte counts and
hashes. Configured responses are valid JSON verdicts, empty output, a five-
second sleep interrupted by the original 0.5-second subprocess timeout, or
the object with no verdict. Full response bytes are retained when emitted.

These are scripted transport outcomes, not native reviewer judgments.
Historical operator/checker functions prepare two distinct bodies so the
original pool path executes; their claimed artifact defects do not provide
reviewer-ranking truth. No historical test function, model, provider or real
pool is executed. This experiment measures faults in the historical software
being considered as a review case. It does not revive that pool's synthetic
instrument as the ranking instrument.

The transport result applies to an argument-only endpoint. It does not
establish that every native CLI ignores stdin, attribute the historical paid
sweep's failures to this cause, or show that a model obeys a file-read
instruction. The repaired endpoint proves that the named file is accessible
and preserves the intended body bytes.

Criteria and fixture bytes were frozen before execution. The checker was
written afterward to apply those criteria to captured evidence. It compares
received body hashes, contract-valid responses, original rows and aggregate
denominators. Parser success alone cannot satisfy the valid-response check.

## Preparation, custody and validation

The [first preparation](authorization-2026-09-10-reviewer-pool-transport-witness.md)
stopped before execution because `git archive` expanded the historical
`export-subst` attribute in `src/caplab/_source_commit.txt`. Its Git blob hash
no longer matched the tracked literal file. That rejected preparation remains
preserved. The [second authorization](authorization-2026-09-10-reviewer-pool-transport-witness-2.md)
uses raw `git cat-file blob` bytes with the same receiver, probe, fixtures and
criteria. No source correction or expected-result change was made.

The corrected source custody contains 407 original files across three
revisions. Source membership and hashes were checked before and after
execution. Python 3.12.3, standard-library and PyYAML files were pinned; the
657-file runtime inventory remained unchanged. Executions use an empty home,
read-only original source and a network-isolated namespace. All newly written
pool data and spill files stay inside private captures. The six executions
took 6.03 seconds and retained 608 capture files.

Private custody is under
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/pool-transport-witness-2`,
with the failed first preparation in its `pool-transport-witness-1` sibling.
The [receipt](../product/studies/reviewer-ranking-001/pool-transport-development-receipt.json)
pins both preparations, exact sources, process outputs, full capture
inventories and verification. Corrected plan SHA-256:
`956d612eb86dd6ebdb75290d289d478b0d3905235cc1474e67f738c5d0746e91`.
Verification SHA-256:
`14cd8aa7ef633bdf47f248a82e4cdb5b2ab61feafb10c1129bb04806740c1d16`.

Five new checker tests challenge absent/invalid responses, timeout missingness,
disagreeing denominators, duplicate/corrupted delivery receipts and explicit
refusal versus silent nondelivery. All five pass.
`make check` passes: 1,526 tests in 211.28 seconds, with seven skips. All 107
receipt file hashes were rechecked before landing.

## Coverage and remaining work

The 607-change census and fixed 32-change selection were reproduced from their
content hashes. The sampled repair's exact base, tree and changed blobs match.
All three revisions are eligible census members, but only the repair was in
the fixed sample. Its ancestors were investigated because of the repair;
they cannot be presented as independently sampled cases or held-out evidence.

This adds actual CAPLAB transport/validity behavior to the feasibility work,
alongside the Council, newsroom and Striatum witnesses. Explicit case
admission and change attribution remain separate from reproduction. The
selected newsroom publication-date repair still needs behavioral verification;
remaining fixed-sample coverage, unseen-review scoring and held-out native
comparisons remain open. No reviewer ranking is accepted.
