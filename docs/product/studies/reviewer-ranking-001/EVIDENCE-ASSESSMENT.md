# Evidence assessment of reported findings

Status: development challenge. No production scorer or reviewer ranking is
accepted by this contract. The [authorization](../../../records/authorization-2026-09-10-reviewer-evidence-assessor.md)
names one native assessor invocation with original source and independent
observations. Its task is to assess existing claims, not discover bugs or
rank their authors.

The desired scoring behavior is to preserve a real defect even when it was
absent from an initial answer key, reject an independently contradicted claim,
and retain uncertainty when a requirement or causal attribution cannot be
established. A plausible mechanism is insufficient for an actionable defect
when the required behavior is disputed. The reviewer author's confidence and
blocking recommendation are separate observations.

| Assessment | Required meaning |
| --- | --- |
| Confirmed introduced defect | Independent evidence supports the behavior, an applicable requirement violation and attribution to the change. |
| Refuted claim | Independent evidence contradicts the concrete defect claim in its stated scenario. |
| Unresolved | Behavior, requirement scope or attribution lacks sufficient support. Absence of evidence is not refutation. |
| Mixed | A finding combines supported or refuted premises with materially unresolved scope or applicability. Preserve the component distinctions. |
| No defect claim | The text contains no concrete defect proposition, such as audit keywords alone. |

Preserve `claim_status` and `acceptance_effect` exactly from the source report.
An underlying proposition can be true after its author withdraws the finding;
the withdrawal must still survive. An advisory concern is not a blocker, and a
confirmed defect does not independently establish that blocking is proportionate.
A future ranking policy must define active-report credit and incorrect-blocker
treatment prospectively. This challenge computes neither.

Within a report, duplicate root-cause claims retain distinct occurrence IDs
and point to the first occurrence. They do not create additional defects.
Duplicate links must not cross reports; later comparative analysis retains
case and incident grouping separately from finding occurrence identity.

## Evidence and blinding

The challenge uses five complete natural finding occurrences from two native
reviews of one already exposed newsroom change. Six controlled occurrences
exercise reversed input conditions, a precisely wrong version premise,
duplicates, withdrawal and keyword-only text. They form seven documents and
are scorer challenges, never reviewer performance measurements.

The assessor receives the original base/current trees and documentation,
original witness methods and captured observations, and upstream versioned
source references. Source reports are preserved unchanged outside the mount;
inside, neutral IDs replace author/run identity metadata. Natural finding text,
qualifications and limitations are retained. This withholds explicit author
identity but cannot guarantee that style is unrecognizable.

Expected assessments and original/synthetic provenance stay outside the task
mount and are frozen before execution. The expectations are primary-agent
judgments grounded in independent evidence. They are not an independently
adjudicated gold standard. Prior verdicts are withheld. The evidence packet
contains actual observations and method inputs rather than prior assessment
conclusions. The original projects and witness programs must not be executed
by this assessor.

## Verification limits

The output must preserve every finding, its reported stance/effect and its
duplicate relationship, and supply a reason and precise evidence locators.
The checker compares the frozen expectations and confirms that cited paths
and line ranges exist. It also checks whether required evidence categories
are present. These checks do not establish that a citation supports the prose.
A test deliberately supplies unrelated literal text with the correct label:
structural checks pass while `semantic_support_verified` stays false.

A separate content inspection must check the actual reasoning against cited
source, relevant controls, requirement scope and attribution before declaring
even this bounded challenge passed. Preserve every mismatch; do not amend
frozen expected labels after seeing output. General scorer validity still
requires prospective natural reports from other cases and families, richer
adversarial challenges and separation from the eventual held-out comparison.
