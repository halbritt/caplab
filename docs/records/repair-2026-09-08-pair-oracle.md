# Refuse unverified mechanical defect pairs

Date: 2026-09-08. Observation, execution, and verification under the repository
owner's active CAPLAB improvement goal. The prior goal turn was progress:
`56f9e5c` is present and introduced exact prospective location matching. This
turn addresses whether a proposed pair establishes a defect in the first
place. It makes no model calls and records no human-owned judgment.

## Counterexample and cause

The `unearned_verification_claim` operator adds a claim that a named test
validates records against a shipped JSON Schema before assertion. Its
historical checker treats missing schema-related words in that test file as
proof that no such validation occurs. A test can instead delegate validation
to another module.

`tests/test_advisory_pair_oracle.py` constructs that counterexample from new
local fixture files. The named test calls `support.check` on every record
before its assertion; the helper uses `jsonschema.validate` with the shipped
draft 2020-12 schema. Separate local subprocesses accept an integer ID and
reject a string ID with `ValidationError`. No schema-related marker appears
in the named test. The historical checker nevertheless returns `True` on the
mutant and `False` on the control. The inserted claim describes behavior the
fixture actually performs.

The pool and calibration gate also tested only for explicit rejection:
`False` on the mutant or `True` on the control. `None`, which means the
checker cannot decide, passed through both gates. The pre-repair regression
run passed the independent counterexample and failed four execution-boundary
tests. Log: `/tmp/caplab-oracle-red.log`. These observations impeach the
software's oracle, not a measured binding.

## Repair and preservation

`operators.pair_gate_error` now owns the prospective pair gate. It requires
declared checkability, explicit mutant presence, and explicit control
absence. Unknown or non-boolean answers refuse preparation. It also refuses
`unearned_verification_claim` because that heuristic cannot establish the
claimed absence of behavior. Restoring that class requires independent
behavioral evidence, not a larger vocabulary of schema-related strings.

The pool retains an applicable but unverified cell as incomplete, with an
`oracle unverified` reason and no score. It contributes to the existing
incomplete count and abort policy; it is not relabeled as inapplicable.
Calibration records `injection-failed-gate` and assigns no reference
difficulty flag. Both paths stop before a reviewer invocation.

New rows and summaries name `pair_validation: paired-presence/1`. Resume
refuses older or unknown pair contracts. Scoring rejects unknown versions
and inconsistent row/summary markers. The historical marker checker remains
available for characterization, and historical mutations, rows, summaries,
claims, exports, and adjudications were not rewritten or reissued. The
qualification operator allowlist and gate specification remain unchanged.
The four candidate gate cells for this operator therefore remain visible as
an unresolved preparation gap.

## Limits and next evidence

This repair removes an unsupported ground-truth inference. It does not
establish that every other mechanical checker has semantic validity, that
controls are globally sound, or that a reviewer's explanation is correct.
Other retained operators still use marker-based checks. They need their own
counterexamples and independent behavioral checks before any broad validity
claim. The code-review construct remains a scaffold, and independently
adjudicated production outcomes remain necessary for reviewer ranking under
the confirmed disposition. No injection sweep was resumed.

## Verification

Full `make check` passed **724 tests with four existing skips** in 113.837
seconds. Log: `/tmp/caplab-oracle-make-check.log`. The focused operator, pool,
calibration, tree-v1, scoring, and gate suites also passed before the final
boundary tests were added. The full run includes those additions: explicit
boolean semantics, unknown control/mutant results, declared checkability,
version incompatibility at resume and scoring, and the runnable delegated
validation counterexample. `git diff --check` passed. The skipped campaign
and PostgreSQL integration checks remain outside this verification.

## Engineering guidance

Pincite's validated release supplied packet `pkt-0cc92d678af9add0`, content
SHA-256 `0cc92d678af9add064e4cb8660b58c8ea2e72740204009214c10c1fdc10ed313`,
doctrine `doctrine-f6bbb5196a3f8bf9`, retriever
`retriever-ec995ecdd083b2c8`. The applied concepts were
`testing-test-first-feedback`, `universal-repository-contract-precedence`,
and `universal-preserve-behavior-by-default`. The repository contract calls
for explicit opposing checker results; the counterexample and regression
tests establish why the weaker implementation cannot support that claim.

Leaving the gate unchanged would continue to treat unknown answers as truth
and delegated validation as absent. Extending the regular expression cannot
prove that arbitrary helper calls perform no validation. The repair instead
withholds the unsupported inference and preserves the lost coverage. This is
a semantic defect repair, with no new benchmark admission or deployment.

Material questions concern authority, the pair contract, the counterexample,
preserved evidence, missingness, and verification; the source observations,
owner goal, version checks, and tests above address them. The packet's
remaining generic ingest, deduplication, asynchronous UI, attention-budget,
top-N selection, operational paging, and broader gate-inventory obligations
are nonmaterial to this repair. Configuration-reference validation is covered
here by the version mismatch tests. Production incident prevalence,
eval-versus-serving parity, and whole-instrument semantic validity remain
unverified and explicitly outside the resulting claim. Doctrine provides
engineering guidance, not CAPLAB product authority or acceptance.
