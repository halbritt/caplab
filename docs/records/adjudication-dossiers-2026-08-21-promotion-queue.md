# Control-soundness dossiers — the promotion queue of 2026-08-20

> **NOTE 2026-08-22** (`erratum-2026-08-22-changeset-contract-quarantine.md`): all eight control-soundness
> adjudications stand. Separately, cell `qs-aae295d9adf3871e` is
> quarantined from promotion — its *measurement* ran the contaminated
> v1 change-set contract; its control remains adjudicated sound.

- Date: 2026-08-21
- Purpose: evidence for the seven control-soundness adjudications that stand
  between the reproduced separators and promotion
  (`report-2026-08-20-targeted-reproduction.md`). Each `sound`/`defective`
  disposition needs a mechanical oracle or a named human adjudication; a
  model review alone is neither — it supplies the argument. The audits below
  are the arguments. **Dispositions recorded here: one (mechanical oracle).
  The other six await the Principal's individual rulings.**
- Method: each control was independently audited for refusal-grade internal
  defects — internal contradictions, self-refuting claims about the
  artifact's own content, broken internal cross-references, arithmetic that
  does not close. Style, debatable judgments, and claims about external
  systems were out of scope, matching the adjudication module's definition.

## Adjudicated: qs-d24d0d472c7a9316 — SOUND (mechanical oracle)

`caplab docs/records/finding-2026-08-16-calibration-not-measurement-equivalent.md`
@ `c4c8e241`. Refused 8 of 12 reviews, all alleging the evidence table
(8 cases, 2 catches) contradicts the stated sample (11 cases, 3 catches).
The rerunnable check `advisory/checks/verify-control-qs-d24d0d47.py` parses
the pinned table and compares both table and narrative against the
validation file the document reports
(`advisory/calibration/strong-reference-gemini-3-7-flash-high-20260816.jsonl`):
every table row matches the file's per-class counts exactly, the narrative
totals match the file exactly, and the table is a consistent 6-of-9-class
subset — the three omitted classes had no same-day real-path comparison.
Nothing in the document misstates the data; the refusals misread an
unlabeled subset. Disposition `sound` recorded 2026-08-21 on
mechanical-oracle basis. **Its separator (`swapped_section_bodies`) is the
campaign's first promoted case.**

## Awaiting ruling (six)

Review history counts every usable control replicate across all sweeps and
subjects (2026-08-16 through 2026-08-20).

### 1. qs-5ebab1a249b89eb2 — striatum proposal "backends own their config, b"

Exchange dispatch `7f54b2a9…`, fate final. History: 19 reviews, 2 refusals —
both minority replicates of `claude-harm-fable-5-high` in one sweep, texts
not retained (representative capture keeps the majority-aligned replicate);
no articulated allegation stands. Audit: clean. The one superficially tense
passage — "rejected at its acceptance gate" beside "review 12389
`accept_with_findings`" — resolves as two distinct process events (a gate
rejection on a stale intent pin vs. a content review), and the incorporated
minor finding the Status section promises is delivered twice in the body.
Proposed: **sound**.

### 2. qs-8f41b707cb15f6d9 — caplab P11 eligibility decision proposal

`docs/records/caplab-p11-eligibility-decision-proposal-2026-07-20.md`
@ `c4c8e241`. History: 15 reviews, 0 refusals. Audit: clean. The apparent
tension "zero mechanical exclusions" vs "every candidate derived-not-eligible"
is resolved by the document itself (ineligibility is pending absent human
review, not exclusion). No internal anchors exist to break; no arithmetic
fails. Proposed: **sound**.

### 3. qs-aae295d9adf3871e — striatum change set "claim surface inventory"

Exchange dispatch `63008b24…`, fate final. History: 24 reviews, 0 refusals.
Audit: clean on every mechanical check — pinned base hash byte-identical to
the packet's `base.content_hash`, the four-overlay list holds four entries,
all 24 anchors unique, all 80 matrix rows use the document's closed
vocabularies, the five-of-eight runtime-doc claim enumerates correctly.
Residual: one debatable single-row classification (probe row "one side only"
vs. near-identical text classified "both sides separate" elsewhere), ~15%
confidence, outside the defect definition. Proposed: **sound**.

### 4. qs-aba90dbe009e7ea2 — caplab ADR 0048 (local-qwen contrastive export)

`docs/decisions/adr-0048-local-qwen-contrastive-export.md` @ `c4c8e241`.
History: 21 reviews, 0 refusals. Audit: clean; all counts close (8-call
campaign = 7 valid + 1 truncated; 7 exported = 3 training + 4 development =
6 SFT + 1 preference). Proposed: **sound**.

### 5. qs-afa3ff9b86200498 — caplab ADR 0063 (bounded codex live Revbench)

`docs/decisions/adr-0063-bounded-codex-live-revbench-execution.md`
@ `c4c8e241`. History: 15 reviews, 0 refusals. Audit: clean — six cited
concepts vs. six listed, packet ids match their hash prefixes, frontmatter
matches body, credential key-shape rules do not swallow their own allowlist.
Residual: "refresh forbidden" vs. "rotation among tested behaviors", judged
compatible (testing behavior under rotation ≠ supporting refresh), low
confidence. Proposed: **sound**.

### 6. qs-ec76afd5d7b27ffd — striatum-next closure postmortem

`docs/audits/SEMANTIC_AND_DURABLE_CLOSURE_FULL_RUN_POSTMORTEM_2026-07-21.md`
@ `dc794628`. History: 12 reviews, 0 refusals. Audit: clean at unusual
depth — all register sequences complete (T01–T45, O01–O21, A1–A12, 20
escalation rows), every stated duration re-derives to the second, the
32-packet sum and 21→30→32 evolution cohere, all 16 contents anchors
resolve. Residual: a "four vs three/five" tension in the recovery-count
family with a consistent in-document reconciliation (four zero-run plan
records across three defect shapes within five repairs), low-to-medium
confidence, not X-and-not-X. Proposed: **sound**.

## What a ruling does

Each `sound` ruling is recorded in `advisory/control-adjudications.jsonl`
with the Principal as named authority and the audit above as the accepted
basis; the corresponding separator then promotes on the next gate run. A
`defective` ruling excludes the separator and its control from false-alarm
scoring — the correct outcome if the Principal reads a residual differently
than the audit did. Rulings are individual; nothing here batches them.

## Rulings — 2026-08-21

The Principal ruled all six remaining controls **sound**, individually named
in `advisory/control-adjudications.jsonl` with each dossier audit as the
accepted basis. With the oracle case, all seven queue controls are
adjudicated sound.

Gate outcome on re-run: **7 promoted, 0 withheld on adjudication** — the
campaign's first promoted discrimination corpus. All seven cells separate
`agy-gemini-3-7-flash-high` from `agy-gemini-3-7-flash-medium` in the high
direction across two sweeps each. The 12 remaining withheld entries stay at
"seen in 1 sweep", which is regression to the mean, not backlog. Three
false-alarm pairs on other controls remain unaudited and join the standing
audit backlog.
