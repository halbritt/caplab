# Architecture decision records

This directory holds architectural selections that outlive one implementation
session. ADRs preserve the decision question, evidence, alternatives, owner,
authority, consequences, and reopening conditions. They do not replace product
specifications, implementation plans, decision receipts, or verification.

## Identity and lifecycle

ADR filenames use `adr-NNNN-<slug>.md`. Numbers are assigned once and never
reused.

| Status | Meaning |
|---|---|
| `draft` | Incomplete working record; no selection |
| `proposed` | Reviewable recommendation; no selection |
| `decided` | A named owner selected an option within stated authority |
| `rejected` | A named owner declined the proposal |
| `superseded` | A later, reciprocally linked ADR replaced this decision |
| `withdrawn` | The proposal was removed before selection, with a reason |

`decided` does not mean implementation was authorized, executed, verified, or
accepted. Those states remain separate under the repository's
[ubiquitous language](../../ubiquitous_language.md).

## Authoring and supersession

1. Copy [`adr-template.md`](adr-template.md) and assign the next unused number.
2. Record observations and evidence before inferences or recommendations.
3. Leave the decision section unresolved while the status is `draft` or
   `proposed`.
4. Set `decision_owner`, `decision_authority`, and `decided_at` only when that
   owner selects an option.
5. Record implementation authorization separately.
6. Supersede an ADR with a new ADR and reciprocal `supersedes` and
   `superseded_by` links. Do not rewrite the old rationale to match the new
   decision.

A `decision-receipt/2` may provide evidence and assertion lineage to an ADR. It
does not select the option automatically.

## Artifact boundaries

| Artifact | Governs |
|---|---|
| ADR | Selected architectural choice and rationale |
| Product specification | Observable product or research capability |
| Implementation plan | Proposed or authorized execution sequence |
| Decision receipt | Evidence and assertion lineage for one question |
| Verification record | Evidence that execution met stated criteria |
| Acceptance record | Owner judgment that verified results are sufficient |

## Index

| ID | Title | Status | Decision owner | Affected surface |
|---|---|---|---|---|
| [`adr-0001`](adr-0001-domain-documentation-authority.md) | Domain documentation authority | decided | repository owner | repository documentation |
| [`adr-0002`](adr-0002-agent-capability-lab-v0.md) | Agent Capability Lab v0 product boundary | decided | repository owner | Agent Capability Lab |
