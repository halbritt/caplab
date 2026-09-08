# Gate observations do not establish semantic conformance

Date: 2026-09-08. Prospective reporting repair under the ongoing CAPLAB
improvement instruction. The confirmed review-instrument disposition remains
in force: no model spend, ranking, qualification claim, or placement decision.

## Observation and contract

At source commit `feb4449`, `scripts/review_gate.py` reported this authored
local response as conforming and credited its natural-case anchor:

```json
{
  "verdict": "reject",
  "findings": [{
    "element_anchor": "result_tree_hash_backup",
    "rationale": "No harm exists. The result is correct."
  }]
}
```

The reproduction is retained in
`/tmp/caplab-gate-semantics-reproduction.json`. It exercises the local
conformance function and the natural-case substring predicate; it is not a
production reviewer observation. The regex recognizes `harm` even when the
sentence denies harm. The substring predicate recognizes `result_tree_hash`
inside a different field name. New executable regressions reproduced both
effects through the natural-case reporting path before the repair.

The frozen production contract
`advisory/criterion/review-pass-contract-649545a9.yaml` requires a refusal to
identify a predicate-blocking defect: a falsified accepted clause, an
in-force decision violation, or demonstrated harm on the changed surface.
A lexical match establishes none of these. Conversely, a concrete description
of data loss can lack every cue word without being unlawful. The existing
report caveat acknowledged that limit, but its `ok` value and `conforming`
count still presented the lexical result as conformance.

## Prospective behavior

New reports use `caplab-review-admission-gate-result/3` and
`review-gate-conformance/2`. Mechanical checks require the supported response
envelope, at least one nonempty anchor on a refusing verdict, and a nonempty
`rationale` for every finding. An unrelated `text` field cannot substitute
for the contract's named field. This remains a subset of structural checks,
not a full review-ledger schema validator.

Failure of a necessary mechanical check produces `ok: false` and status
`failed-mechanical-checks`. Passing those checks produces `ok: null` and
status `unverified`. This also applies to an empty accepting response: the
subset cannot establish all the contract's requirements. The old regex is
retained solely as `rationale_cues_present`, an observation with no pass/fail
effect. There is no new semantic judge or delegated human judgment.

Natural-case reports leave `conforming: null`. They count mechanical passes,
unverified conformance, mechanical failures, and unavailable attempts
separately. Failed execution or manifest verification supplies no observation
to those conformance counts. An aborted pool leaves all natural replicates
unavailable and launches none. Plan output now discloses the limited
conformance assessment before any authorized execution.

The natural case uses the existing `normalized-anchor-exact/1` matcher.
Formatting wrappers and case are normalized; longer unrelated identifiers
are not matches. The new `refused_with_exact_anchor_mention` field counts
observed refusals that mention the exact location. `exact_anchor_mention`
remains an observation about text, including when the rationale is wrong.
Full parsed responses remain in the report for inspection. This does not
establish defect detection or prescribe how a future semantic finding
assessment should handle alternate location syntax.

## Preservation and remaining work

The gate specification, proposed floors, historical results, case content,
and production contract were not changed or reinterpreted as new evidence.
Version 2 reports retain their original lexical meaning. No report was
regenerated, admitted, purged, or superseded. Analog-cell scoring and control
adjudication were unchanged. The untracked `docs/designs/` draft was preserved.

The full conformance floor cannot be evaluated by this report. A later
assessment needs evidence tied to the actual predicate, decision scope,
changed artifact, and stated harm; authorized human-owned judgments must
retain their delegation source and scope. This repair makes the gap explicit
without adopting thresholds or admitting or excluding a reviewer. The wider
production-outcome gap and reviewer-value goal remain unresolved.

## Alternatives and authority

Leaving the existing caveat and numeric conformance count would preserve the
demonstrated overclaim for report consumers. A more elaborate regex would
still confuse descriptions with proof and could penalize legitimate wording.
Automatically selecting a semantic judge would introduce a new instrument
and authority requirement without independent validation. The implemented
repair reports the mechanically observed facts and leaves full conformance
unverified. No structural redesign or new dependency was needed.

The local counterexample distinguishes the defect from a parser or transport
failure: its JSON envelope and execution fixture are valid. The first
divergence is the conversion of a keyword match into `ok: true`, followed by
its contribution to the `conforming` count. The anchor divergence is the
substring check itself. Existing execution and population checks remain in
place. Tests assert report values and retained responses, not the choice of
regex implementation or internal call ordering.

Authority extends to prospective implementation and local verification under
the ongoing improvement request. It does not adopt the proposed gate floors,
assess a real reviewer, or record human acceptance. Native execution,
historical evidence effects, and any new semantic adjudication mechanism
remain outside this repair. The future trigger is an authorized assessment
contract with independently grounded evidence, not merely more cue words.

## Verification

The pre-repair regression run failed with three assertions and four missing
output-field errors (`/tmp/caplab-gate-semantics-red.log`). After repair,
the 91 gate and pool-runner tests passed
(`/tmp/caplab-gate-semantics-focused.log`). The fixtures cover negated cue
words, a concrete rationale without cue words, missing or blank rationales,
malformed outputs, substring anchors, formatting normalization, failed
execution, manifest failure, and pool-abort reporting. An earlier focused
command used a nonexistent test-module name; the corrected command used
`test_review_gate` and `test_advisory_pool_runner`.

The local `--plan fixture` command retained the 67-call declared plan and
reported the new assessment limit without invoking a model
(`/tmp/caplab-gate-semantics-plan.json`). Full `make check` passed 745 tests
with four existing skips in 118.714 seconds
(`/tmp/caplab-gate-semantics-make-check.log`). The skipped campaign and
PostgreSQL integration tests are outside this verification. The post-repair
local counterexample output is `/tmp/caplab-gate-semantics-after.json`.

## Engineering guidance

Repository requirements govern the repair. Retrieved guidance supplied
`testing-test-first-feedback`, `universal-repository-contract-precedence`,
and `agent-conduct-authority-bounded-action`. The final packet is
`pkt-38bd166261e6f2f1`, SHA-256
`38bd166261e6f2f14f1930b1924d45014253a487a0cc5f59ca0d83e17e3a60aa`,
from release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8`. Its execution ceiling remains
bounded by the authority described above. Evidence locators are the frozen
contract, script, response validator, gate tests, and local logs in this
record. The record is verification of an implementation change, not human
acceptance.

The material obligations concern the semantic contract, report consumers,
first divergence, authority, historical preservation, and regression
protection. The inspected contract, source, counterexamples, and tests cover
those bounded claims. The remaining packet obligations are classified below:

- Population traversal and deduplication identity are nonmaterial to this
  repair; it changes neither discovery nor case keys. Existing missingness,
  duplicate-cell, and attempt accounting tests remain in the passing suite.
- Asynchronous UI, presentation budgets, top-N ordering, and paging are
  nonmaterial; no such mechanism is changed or claimed to be verified.
- Declarative configuration-reference validation is nonmaterial to the new
  report labels. The consumed verdict set and response shape are checked by
  the existing validator; no new external schema or symbolic target is
  introduced. Full production-schema validation remains expressly unclaimed.
- Real endpoint access, capability self-description, and end-to-end native
  verification are unverified and outside this local repair. They remain
  material prerequisites for any live Binding or reviewer capability claim.
- Production incident prevalence, current operational cost over an interval,
  and predicted future change frequency are unknown. They are nonmaterial
  to correcting the reproduced report semantics and cannot support a claim
  about practical reviewer performance or measured operational benefit.

No further evidence-gathering claim is inferred from the passing test count.
Future semantic assessment must satisfy its own material obligations before
changing the unverified status.
