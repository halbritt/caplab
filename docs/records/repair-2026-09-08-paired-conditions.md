# Verify common conditions before comparing reviewers

Date: 2026-09-08. Observation, execution, and verification under the active
CAPLAB improvement goal. The previous goal turn was progress: `07c2020` is
present and freezes resumable experiments. This continuation makes those
specifications part of the paired comparison's evidence requirements. No
model calls, historical reanalysis, or human-owned judgments were performed.

## Reproduction

At `07c2020`, the paired comparison checked completion and matched usable
rows by `dispatch_id`. It did not read the frozen experiment specifications.
Duplicate IDs overwrote earlier observations, and missing rows disappeared
through intersection. Thus two runs with the same case IDs but different
timeouts, replication, seeds, workers, or source code could produce a
nominally matched contrast. Altered backend labels and unmatched defect
anchors also passed through that path.

Constructed local subprocess runs reproduced those conditions. The initial
six-test regression run failed thirteen assertions and one new-output
expectation; log `/tmp/caplab-compare-red.log`. This is evidence about the
comparison software, not a measured model difference.

## Prospective comparison contract

When either run carries a frozen specification, both must carry one. The
comparison verifies the retained specification digests and their summary
references. It compares all recorded conditions using canonical hashes,
except for three explicitly subject-owned fields: backend label, declaration
hash, and declared lane limit. Those fields remain visible for each subject;
the native configurations are not replaced or forced to be identical.

Common conditions include the ordered plan and anchor membership, selection
mode, seed, partition, sampling parameters, timeout, replication, requested
workers, environment, base registry, validator contracts, Python version,
and instrument source hashes. A missing required field or unknown selection
mode refuses comparison. Unknown additional fields are treated as common
conditions and must also agree.

Every planned row must appear exactly once. Its case identity, anchor status,
backend, specification reference, and validator versions must match the frozen
plan. A usable row must carry valid-response flags, boolean observations,
and the expected environment. A non-usable row must be genuinely
operator-inapplicable and carry no attempt evidence; preparation failures
cannot disappear as missing data. Summary coverage counts are recomputed
from the rows and must agree. Both runs must have the same measured case set,
including anchor assignments. Anchor cases remain outside the breadth
contrast.

For paired breadth rows, defect anchors, prompt profiles, base manifests,
base sources, operator labels, and preambles must agree. A surviving
intersection is insufficient when the planned populations differ. The
`caplab-paired-conditions/1` basis records the common-condition hash,
each run-specification and result-file hash, each subject's declared
configuration identity, and planned, paired, inapplicable, and anchor counts.

Targeted-reproduction and admission-gate runs still produce descriptive
paired counts. Their p-value and significance fields are `null`: cases
selected on earlier outcomes cannot become discovery evidence merely because
their execution conditions match. Seeded draws and profile remeasurements
retain their declared selection modes and existing numerical calculations.

## Preservation and limits

The legacy unversioned comparison path keeps its numerical behavior and
selection annotation rules. New output explicitly labels that basis
`unverified-historical`; it does not imply that common conditions were
verified. Frozen rows cannot be routed into it by merely removing a
summary reference. No historical results or reports were regenerated,
rewritten, admitted, or superseded. The untracked design draft was preserved.

Common recorded conditions are necessary, but do not establish native
Binding identity, executable runtime equivalence, semantic correctness of
findings, sound controls, independence of sampled cases, or real-world
reviewer value. A frozen specification cannot attest to external executable
or account-state changes it never captured. The numerical calculations and
historical adjudication semantics are unchanged; this repair does not
revalidate them. The confirmed disposition still prohibits reviewer ranking
from the injection instrument. The production-outcome requirement and wider
goal remain unresolved.

## Verification

Full `make check` passed **742 tests with four existing skips** in 114.147
seconds (`/tmp/caplab-compare-make-check.log`). The final legacy-basis label
was then added, and all 25 comparison tests passed
(`/tmp/caplab-compare-final-focused.log`). The earlier combined comparison,
pool, and scoring run passed 126 tests. The skipped campaign and PostgreSQL
integration checks remain outside this verification. `git diff --check`
passed. No model was invoked.

## Engineering guidance and alternatives

The repository contracts and confirmed disposition govern this repair.
Retrieved guidance supplied `testing-test-first-feedback`,
`universal-repository-contract-precedence`, and
`universal-preserve-behavior-by-default`. The evidence packet was
`pkt-00fbe73f1d8f4978`, SHA-256
`00fbe73f1d8f497872be62d40080d7bdcf4e989b6fd1df8a17df00f721d0d3d4`,
from release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8`. Its authority ceiling was
execution within the authorized repair scope, without human acceptance.
Source locators are the comparator, run-specification producer, pool runner,
comparison tests, and verification logs named above. The packet preceded the
final historical-basis wording; the subsequent focused test verifies that
wording separately.

Leaving the comparator unchanged, or checking only seed and case IDs, would
retain the demonstrated false pairing. Requiring identical whole run
specifications would prevent comparison of distinct declared subjects.
Adding a warning after computing statistics would still expose numbers from
unmatched conditions. The implemented check validates shared conditions
before arithmetic while preserving the three declared subject differences.

Material evidence obligations concern authority, the distinction between
subject identity and common conditions, complete population accounting,
configuration references, and executable regression checks. Source inspection
and the retained tests cover these bounded claims. Within each frozen plan,
the substrate/operator/seed tuple identifies an assignment; duplicate tuples
and duplicate result rows are rejected rather than silently overwritten.
The complete enumerated plan is reconciled against results and summary
counts. These checks address the applicable population and identity concerns.

The packet's remaining traversal, asynchronous UI, presentation-budget,
top-N ordering, paging, and whole-system gate-inventory obligations are
nonmaterial to this comparator repair: it does not perform those operations.
Production incident frequency, native serving parity, semantic truth, and
independent sampling remain unverified. They are material to broader reviewer
value claims, so this record makes none. Historical compatibility is checked
by existing numerical tests; future experiment coverage is not inferred from
those tests. No additional structural refactoring was needed. The stop
boundary remains any claim requiring native execution, new measurement,
historical evidence mutation, ranking, or human-owned acceptance beyond the
active authorization.
