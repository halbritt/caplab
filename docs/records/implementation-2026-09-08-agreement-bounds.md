# Conservative simultaneous bounds for coding agreement

Date: 2026-09-08. Baseline: `571372a`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Add `src/caplab/code_agreement_bounds.py`, focused synthetic tests in
`tests/test_code_agreement_bounds.py`, a contract guide and this record. Add an
explicit optional mode to `scripts/code_agreement.py` and link its guide from
the existing agreement guide. Preserve existing agreement/reference APIs,
default CLI outputs, input validation and all historical evidence.

Implement a deterministic Hoeffding/union-bound diagnostic conditional on
independent identically distributed complete episode pairs within each
world/code. Confidence is an explicit caller parameter, with no default study
value or passing threshold. Include every declared world/code in the family
size; preserve missingness and undefined point estimates. Report conservative
bounds for defined population kappa and state when undefined population kappa
cannot be excluded. No claim about missing episodes or clustered data is made.

Test only newly authored synthetic inputs, including degenerate labels,
missingness, multiplicity and invalid arguments. Verify arithmetic against
independent calculations and bounded numerical experiments, run the documented
CLI example and `make check`. Keep receipts under
`/tmp/caplab-agreement-bounds-*`; consolidate advisory evidence before deleting
only its named scratch inputs. Commit the authorized files locally; authority
expires at commit. Stop on a broader effect or unsupported coverage claim.

No study method/parameter freeze, actual coder qualification, model call,
archived-data processing, evidence admission, ranking, human-time commitment,
tracker write, campaign execution, message, push or dependency change. Preserve
unrelated `docs/designs/`, worktrees, services and prior artifacts.

## Decision and preservation boundary

The current agreement diagnostic reports point estimates only; CAPLAB-77 now
requires a prespecified uncertainty method for actual comparison. Add an
optional conservative method without adopting it for that study. Its explicit
assumptions may rule it out for a clustered or adaptive design.

Leaving uncertainty entirely to ad hoc analysis keeps a known reporting gap.
A resampling interval would require choices about clusters and degenerate
resamples that this input schema does not encode. A point estimate plus a
normal approximation can be misleading near a boundary. This selected method
has a short concentration-bound derivation and deliberately gives up tightness.
It does not claim to be the most efficient interval or a substitute for the
eventual study-specific analysis.

The new module consumes the existing validated descriptive report; its
arithmetic does not mutate input or replace the agreement/reference owner.
The CLI mode is mutually exclusive with supplied-reference comparison, so
agreement bounds cannot be mistaken for accuracy bounds. The default two CLI
modes and their schemas remain unchanged. The new output embeds the original
agreement report and names its own schema and method.

## Implementation and focused verification

The new `build_iid_agreement_bounds` API and `--iid-confidence` CLI option
produce `caplab-code-agreement-bounds-report/1`. The
[guide](../product/contracts/code-agreement-bounds-v1.md) states the sampling
conditions, family allocation, kappa transformation, undefined-population
warning and floating-point limits. The method uses three bounded proportions
per declared row and transforms their simultaneous region conservatively;
the existing input validation, point estimates and reference comparison remain
their current owners. No dependency or numerical study parameter changed.

All 33 focused tests passed in 1.024 seconds, including nine new tests and the
existing agreement/reference tests. A 60-digit Decimal calculation checks the
balanced-perfect lower endpoint independently of the rational implementation.
Other checks exercise small and constant samples, empty-row multiplicity,
missingness, monotonicity with sample size/confidence, coder/order symmetry,
invalid values and actual CLI mode selection. Tests use real data and the real
CLI; they do not mock statistical internals or call models.

The documented example ran successfully with one complete pair and one
unavailable coder judgment. Its point kappa remains undefined, its kappa bounds
are [-1,1], and the undefined-population warning remains true. Default and
reference-mode stdout/stderr match the baseline CLI byte-for-byte on that new
synthetic input. The compatibility receipt is
`/tmp/caplab-agreement-bounds-compatibility.json`.

A separate finite-grid check used seven constructed sample tables and all
four-cell joint distributions with denominator 20. For the 327 grid points
inside their rate rectangles, the transformed chance-agreement and defined
kappa bounds enclosed the exact rational values; degenerate population points
kept the warning. This checks the transformation on a finite set, not empirical
coverage or coder accuracy. Script, report and log are
`/tmp/caplab-agreement-bounds-grid.py`, `grid.json` and `grid.log` under that
prefix. Focused and example logs/inputs/outputs are retained there as well.

The primary source was inspected as rendered pages from the retained Hoeffding
paper: Theorem 1, equation 2.3, printed page 15. The first Stanford URL returned
404; the cited RPI copy supplied the original paper. Text extraction yielded no
text from the scanned page, so the actual theorem was read from its rendered
image. The PDF and rendered pages remain under the same `/tmp` prefix.

## Scope of the result

The report exposes uncertainty that a point estimate omits. Its wide bounds
are a consequence of a conservative method, not measured instability of any
real coder. Independent episode sampling, outcome-independent inclusion,
adequate handling of clustering/missingness and study-wide multiplicity remain
design requirements. The method does not resolve those requirements through
an option name. CAPLAB-71 has not adopted the method; CAPLAB-77 still needs
actual repair coding evidence and CAPLAB-65/66 retain accuracy and blinding
requirements. No roadmap item is closed by this implementation.

## Final verification and advisory provenance

`make check` exited 0: 1,172 tests in 207.669 seconds, four skips. The log is
`/tmp/caplab-agreement-bounds-make-check.log`. Ten protected instruction,
contract, source and test files remain byte-identical to baseline. New/changed
source hashes, primary-source custody, focused/full-suite results, CLI
compatibility, grid checks and advisory evidence are consolidated in
`/tmp/caplab-agreement-bounds-verification.json`. Links and documented output
claims were checked against current files and the executed example.

The validated Pincite release is
`/home/halbritt/.local/share/pincite/release`, commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Final packet
`pkt-727f45639065ef11` has content SHA-256
`727f45639065ef1145736b0f40b6ca314435625238666345604a672b91269383`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`.
Four consumed concepts classified as valid packet citations:
`universal-repository-contract-precedence` preserves study decision owners;
`universal-evidence-before-intervention` ties the feature to the point-estimate
gap; `universal-preserve-behavior-by-default` keeps the existing report modes;
`python-runtime-static-boundary` requires input/confidence checks rather than
trusting annotations. Doctrine supplies engineering guidance, not the
statistical derivation or independent acceptance.

Eighteen unmet advisory obligations are retained individually with their exact
wording and nonmaterial classification in the manifest. Four concern broader
toolchain/version matrices, four annotation/checker or observed-defect evidence,
five managed-resource lifecycles, and five text/byte protocols. No dependency,
static-checker, resource-lifecycle or encoding change is made, and no repaired
production incident is claimed. Existing validation and CLI owners remain in
use; the actual new arithmetic and invalid-input behavior were exercised.

The pre-verification decision snapshot remains at
`/tmp/caplab-agreement-bounds-decision-before-verification.md`, allowing the
typed evidence's source hash to be checked after this record was extended.
Eleven exact advisory scratch files were removed after consolidation. Test
logs, synthetic inputs/results, the baseline CLI snapshot and primary-source
files remain. No model, historical episode, tracker or study execution occurred.
