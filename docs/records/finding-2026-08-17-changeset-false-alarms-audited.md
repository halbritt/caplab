# Finding — the change-set false alarms, audited: one real defect, one systematic reviewer error

- Date: 2026-08-17
- Scope: the 12 change-set controls drawn by sweep 20260817 (8 refused, 3
  cleared, 1 never asked). Every preserved refusal rationale was verified
  against the artifact bytes; every `result_tree_hash` allegation was
  replayed through striatum-next's own production arithmetic
  (`internal/changeset` + `internal/gitanchor`, imported read-only), with
  every base body fetched from the graph object store and sha256-verified
  before use.
- Harness preserved at `advisory/checks/hashcheck/` (Go source; build with
  the `replace` directive it carries, run
  `hashcheck -cs <artifact.json> -objects <bodies> -repo ~/git/striatum-next`).

## Verdicts

| substrate | operator drawn | verdict on the refusal |
|---|---|---|
| `qs-45baf30be46b0c3c` | base_dropped | **justified — control defective.** Ships a checks template (registry_version 6, 8 checks) contradicting the registry beside it (version 9, 13 checks, incl. the 5 stalls-guards checks the template lacks). Adjudicated defective, mechanical-oracle: `advisory/checks/verify-control-ee05d12f.py`. Its second allegation (external base-pin mismatch) remains unverifiable and is no part of the basis. |
| `qs-f0a17ff6921f7a0e` | hash_mismatch | **unjustified on all three counts.** The "Go syntax error" file is gofmt-clean (the quotes are escaped); the "un-trimmed HasPrefix" line trims; the declared result_tree_hash reproduces exactly. |
| `qs-a6b8ea770b60d003` | hollow_delivery | **unjustified.** Declared hash reproduces exactly; production `Apply` clean. |
| `qs-a07e9e0e09a4aceb` | hollow_delivery | **unjustified.** Declared hash reproduces; the reviewer's "actual" equals the wrong-semantics replay. |
| `qs-d98bbffcdcd43f21` | requirement_inversion | **unjustified.** Declared hash reproduces; the reviewer's "actual" is byte-for-byte the unexpanded-anchor arithmetic. |
| `qs-c5e755a13eb7b7ee` | unearned_verification_claim | **unjustified on both counts.** HasPrefix claim contradicts the code it cites; declared hash reproduces. |
| `qs-f90cc496593e109e` | hash_mismatch | **unsupported.** The anchors it names exist as quoted, but the "design clause C3" and required anchor spellings appear nowhere in the artifact and nowhere greppable in striatum-next. |
| `qs-9f2748c49dd3313e` | base_dropped | **unauditable.** 2 of 3 replicates refused, but the row retained only the accepting replicate's empty findings. Bounded internal scan found nothing. |

Cleared controls: `qs-aae295d9adf3871e` and `qs-5e5d3de24830be23` pass a
bounded internal-consistency scan; `qs-840e91ecf808ddf2` has one minor doc
omission (an undocumented `--catalog-overlay` flag), below defect grade.
The never-asked control `qs-63c927db22c142d9` verifies clean — see below.

## The systematic error: hashing the unexpanded base

Six of six audited `result_tree_hash` allegations are false, and the failure
has a mechanical fingerprint. The contract (`deriveResultTreeHash`) expands
git anchors into real files before applying the overlay; the reviewer's
"actual" hashes come from overlaying onto the **unexpanded** composed base.
In three cases the reviewer's number is byte-for-byte the wrong-semantics
replay. The subject is attempting hash verification it cannot perform, on
exactly the artifact class that carries declared hashes — which is most of
why change sets attract false alarms while documents (no declared hashes)
sit at zero.

A cautionary replication: one of this audit's own agents first "confirmed"
`qs-63c927db22c142d9` defective using the same unexpanded arithmetic. Only
replay through the production packages settled it — the declared hash
reproduces exactly. A hash allegation is not audited until the production
arithmetic has run.

## What follows

- The false-alarm metric now conditions on the `ee05d12f` adjudication;
  among the sweep's 45 clean pairs, one refusal leaves the denominator and
  five remain, every one with mechanically refuted grounds.
- The five refuted refusals are candidates for `sound` adjudications. The
  refutations are rerunnable, but "sound" asserts more than "this allegation
  is false", so those dispositions are proposed to the Principal rather than
  recorded here.
- The row schema retains findings only from the representative replicate,
  which is how `qs-9f2748c49dd3313e`'s refusal reasons were lost. Same
  recurring shape: the record that would explain the outcome is the one not
  written.

## What this does not establish

- Full soundness of any control; the scans were bounded and allegation-led.
- Anything about other Bindings — the unexpanded-anchor error is this
  subject's observed behavior, and whether siblings share it is exactly the
  kind of discriminating question a matched second Binding can answer.
- Nothing about the sealed partition.
