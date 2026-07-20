---
artifact_type: decision-support-record
title: BOOKS-1–6 ownership review and CAPLAB execution order
status: recorded
recorded_at: 2026-07-20
decision_authority: adr-0026
decision_record: adr-0029
plane_scope:
  - BOOKS-1
  - BOOKS-2
  - BOOKS-3
  - BOOKS-4
  - BOOKS-5
  - BOOKS-6
  - CAPLAB-6
  - CAPLAB-7
  - CAPLAB-8
  - CAPLAB-9
  - CAPLAB-10
  - CAPLAB-11
  - CAPLAB-12
  - CAPLAB-13
  - CAPLAB-14
  - CAPLAB-15
  - CAPLAB-16
  - CAPLAB-17
  - CAPLAB-40
  - CAPLAB-41
  - CAPLAB-42
  - CAPLAB-43
---

# BOOKS-1–6 ownership review and CAPLAB execution order

## Review method

The review compared each live Books work item with its implementation commit,
the active CAPLAB tree, the historical tree under `history/ethogram/`, and the
current Pincite checkout at
`65bc86d2555223279e3c0c6cf16be00cce116883`. Plane supplied planning state;
repository contents supplied implementation observations.

Pincite advisory packet `pkt-02960654e0a0ba29` supported the ownership
decision. Its captured response SHA-256 is
`2670974aa4aea1ff0b6ef1ff33df7582862bcfc8ded0674106fb276761c1c232`.
The packet is advice, not CAPLAB authority.

## Item-by-item disposition

| Item | Source locator | Observation | Disposition |
|---|---|---|---|
| BOOKS-1 | `4a1e2cb4c6bc14a43d8154620a1c8785b1c3113c`; `doctrine/cmd/assemble-packet/`, `doctrine/internal/packet/`, `doctrine/runtime/doctrine-index.sqlite3` | The historical commit introduced the Go and SQLite assembler. The active implementation now exists in Pincite under `doctrine/cmd/pincite-packet-build/`, `doctrine/internal/packet/`, and its release state. | Pincite-owned. No CAPLAB migration. |
| BOOKS-2 | `759e4015bfa6e369c3e4d9f04253631c257c0c52`; `doctrine/evaluations/{baselines/repository.json,regression-gate.json,regression-gate.schema.json,snapshot.schema.json}`, `doctrine/tools/evaluation_regression_gate.py` | The gate behavior is absent from active CAPLAB code and present only in historical custody. | Translate the contract into CAPLAB-42; do not admit its historical baseline. |
| BOOKS-3 | `a7e4bffc4b582cc29da9f00452429138b9b73bab`, `ebcdc772dc1b6500671c281ab2b10cc7dbab70d3`, `c5ff6d2d12db29fc7b5b029596f04d2279ea180d`; `doctrine/evaluations/robustness/injection-probe-*` | This is a Doctrine-specific preregistration and result series in historical custody. | Preserve as history. CAPLAB-43 assesses later admission; it is excluded from CAPLAB-11. |
| BOOKS-4 | `3abb7509fe410a46ec2c9cf8e0ef054154d4aa8b`; `doctrine/evaluations/replay-fixture.schema.json`, `doctrine/evaluations/replay-fixtures/`, `doctrine/tools/check_evaluation_fixtures.py` | Fixture-schema, manifest, and hygiene behavior is reusable; the example fixtures are historical evidence. | Reimplement the behavior with fresh synthetic CAPLAB fixtures in CAPLAB-41. Do not copy the historical fixtures. |
| BOOKS-5 | `4a89c600488a4fb5f69f3ac7f6ec76f218ce7c31`; `doctrine/evaluations/error-taxonomy{.json,.schema.json}`, `doctrine/tools/evaluation_outcomes.py` | Explicit model-versus-infrastructure failure boundaries are reusable platform behavior. | Translate the taxonomy contract into CAPLAB-41; do not copy result summaries. |
| BOOKS-6 | `f860157b5485ae4fafb4fcc4a298b5a668b952d6`; `doctrine/evaluations/gate-defect-event.schema.json`, `doctrine/tools/evaluation_defect_ledger.py`, `doctrine/tools/evaluation_mode.py` | Mode refusal and durable gate-defect behavior are reusable platform controls. | Reimplement mode matching in CAPLAB-41 and the snapshot/ledger gate in CAPLAB-42. |

No historical governing record, model output, run result, baseline, fixture, or
gold judgment was copied, admitted, registered, rewritten, or purged during
this review. The commits and paths above remain custody locators, not CAPLAB
registration.

The reviewed governing contracts and excluded evidence retain these Git blob
identities:

| Item | Source path | Git blob |
|---|---|---|
| BOOKS-1 | `docs/decisions/adr-0003-compiled-doctrine-retrieval.md` | `94771ee7951137af4c402d6273b0b598b86329a6` |
| BOOKS-2 | `doctrine/evaluations/regression-gate.schema.json` | `968cf14950c2f11a83e2e127e6ddd2173c413e3f` |
| BOOKS-2 | `doctrine/evaluations/snapshot.schema.json` | `918c50abfd44e586cfb0532359650f473406919c` |
| BOOKS-3 | `doctrine/evaluations/robustness/injection-probe-preregistration.json` | `9e6190afac70bd1ee2cd034455a82f1888c716fe` |
| BOOKS-3 | `doctrine/evaluations/robustness/injection-probe-summary-2026-07-17-diagnostic.json` | `169ff9a2bbdea5a42a44676b605e3db1699b670f` |
| BOOKS-4 | `doctrine/evaluations/replay-fixture.schema.json` | `887f450bf9b7e414e4baaff7db4bbdbb175dce83` |
| BOOKS-4 | `doctrine/evaluations/replay-fixtures/manifest.json` | `8fa523376bf29623fe2ff724dfc0c90909d71160` |
| BOOKS-5 | `doctrine/evaluations/error-taxonomy.schema.json` | `75300ce0af93ba2019f15cd398ac70441d2ee9ed` |
| BOOKS-5 | `doctrine/evaluations/error-taxonomy.json` | `a7ca2a6de81c14d53d564a4e0f31791e388071bc` |
| BOOKS-6 | `doctrine/evaluations/gate-defect-event.schema.json` | `13927b6d19d8d1a0338575741b68578815ec6f2d` |
| BOOKS-6 | `doctrine/tools/evaluation_defect_ledger.py` | `3a0df18664a31bc84082b24721abc7a03a07c37f` |
| BOOKS-6 | `doctrine/tools/evaluation_mode.py` | `e294e6b09949141a284269162d08d22cb29b9f76` |

## Combined execution order

This is a topological priority order for one executor. It front-loads
model-free product decisions and platform controls before any live study or
training effect.

1. **CAPLAB-40** — bind BOOKS custody and ownership. This record and ADR 0029
   complete that decision gate.
2. **CAPLAB-6** — preregister the exact Fable-versus-GPT preference hypothesis.
3. **CAPLAB-9** — decide whether two Striatum pass profiles are acceptable
   inputs.
4. **CAPLAB-41** — prove a synthetic replay through CAPLAB-native failure and
   mode boundaries.
5. **CAPLAB-42** — add snapshot comparison and durable defect recording.
6. **CAPLAB-7** — build the blinded preference study on the frozen hypothesis
   and evaluation controls.
7. **CAPLAB-11** — select the second, non-Doctrine study.
8. **CAPLAB-43** — assess BOOKS-3 only as a later Doctrine-study candidate.
9. **CAPLAB-12** — implement and model-free qualify the selected second study.
10. **CAPLAB-8** — authorize, run, and adjudicate the first preference study.
11. **CAPLAB-13** — authorize and run second-study calibration.
12. **CAPLAB-10** — produce the Striatum lane-fit report from accepted inputs
    and completed preference evidence.
13. **CAPLAB-14** — export only a separately validated and authorized
    contrastive corpus.
14. **CAPLAB-15** — preregister one open-model tuning experiment.
15. **CAPLAB-16** — authorize training and run the held-out evaluation.
16. **CAPLAB-17** — decide the next scheduler-policy and model-development
    step from the two completed evidence streams.

CAPLAB-41 is blocked by CAPLAB-40; CAPLAB-42 by CAPLAB-41; CAPLAB-43 by
CAPLAB-40; and CAPLAB-7 and CAPLAB-12 by CAPLAB-42. Existing ticket
dependencies still apply. This ordering does not turn a Plane relation into
authorization or make a later result accepted.

## Triage result

BOOKS-1 does not belong in CAPLAB. BOOKS-2, BOOKS-4, BOOKS-5, and BOOKS-6
contain behaviors that belong in CAPLAB but require fresh CAPLAB-native
execution. BOOKS-3 is a possible later study source, not current CAPLAB work.
The original six Books tickets remain Done in their historical project; the
new CAPLAB work is represented by CAPLAB-40 through CAPLAB-43.
