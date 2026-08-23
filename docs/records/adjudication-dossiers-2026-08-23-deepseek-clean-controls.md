# Control-soundness audit — the opencode-deepseek refusals, and the 20260819 cohort correction

- Date: 2026-08-23. Trigger: the Principal requested an audit of the
  unaudited false-alarm refusals behind `oc-deepseek-v4-flash` (16) and
  `oc-deepseek-v4-pro` (20) on the seed-20260819 synthetic-contract cohort.
- Method: the union of both arms' refused controls (32 distinct substrates)
  minus 7 already adjudicated left 25; 18 bodies resolved and
  sha256-verified (17 from the exchange, 1 from the CAS), audited by four
  parallel auditors against in-set content only (out-of-contract
  allegations recorded, never scored), one rerunnable oracle per control
  (`advisory/checks/verify-control-qs-*.py`, exit 0 = defective), every
  oracle re-run independently by the assembling session before any ledger
  write. All 18 reproduce.

## Settled by oracle — 18 controls (records 25–42 in the ledger)

**Defective (3):**
- `qs-a17d0d0b23b2ad0f` — W14.9 says the last state yields `not_available`,
  W22.3 says the first; the document claims the two were "restated to
  agree", and carries five-vs-six-vs-seven edited-purpose counts.
- `qs-425bccdb287d3654` — mutually exclusive same-date spend-state
  declarations (claude-harm status contradicts its own scheduler_hints;
  glm contradicts claude-code).
- `qs-40583720e067908f` — the `d98bbffc` pattern again: fabricated
  `execution.exit_code: 0` receipts beside a sibling "does not itself
  execute" disclaimer — receipts assert executed checks the set concedes
  never ran.

**Sound (15):** `qs-40181ea5`, `qs-4160800d`, `qs-42bc0f9e`, `qs-55beeb77`,
`qs-5a60742a`, `qs-729de0db`, `qs-7438efc6`, `qs-7d8726d3`, `qs-a1dcaeae`,
`qs-a97ff272`, `qs-cdf7e520`, `qs-e95b9a19`, `qs-ec18cdfe`, `qs-f879a0e3`,
`qs-fd0947a4`. Every scored allegation on these imports out-of-set state —
base tree, live registry, catalog, ledger, production wiring — the exact
false-alarm pattern the Principal's 2026-08-23 rulings named on Sol, now
demonstrated across a second model family. The batch applied the recorded
precedents (library-then-wiring per the `qs-d79e9a16` ruling; the
disclosure rule per `qs-6ebd7c87`); `qs-42bc0f9e`'s oracle records the
strict alternative reading should the Principal wish to rule it explicitly.
One preserved residual: `qs-55beeb77` flips defective only if catalog-kind
stage-completeness is ever ruled in-contract for plan-stage substrates.

**Mounting finding (recorded, not scored):** on `qs-a1dcaeae` and
`qs-729de0db`, the deepseek-pro reviewers demonstrably resolved file
references against the **wrong repository** — caplab-shaped symptoms
(`check: test` Makefile, `history/`, `advisory/`, no `policy/`) — i.e. the
opencode mounting let the reviewer wander the harness's own checkout
instead of judging the set. A read-only cousin of the
2026-08-23 replay-escape incident, and an opencode-harness defect in its
own right.

## Unauditable — 7 controls (bodies unrecoverable)

- `qs-40be7cf187a4e288` — refused by oc-deepseek-v4-pro
- `qs-41241900113d9862` — refused by both arms
- `qs-4298b5676c10ee3b` — refused by oc-deepseek-v4-flash
- `qs-5ea16d212ab3d464` — refused by both arms
- `qs-5f841949fa746b8e` — refused by oc-deepseek-v4-flash
- `qs-922bffcd10232e91` — refused by oc-deepseek-v4-pro
- `qs-f3d9c1ad3b285041` — refused by both arms

Their exchange dispatch directories were reaped before the striatum CAS
existed (2026-08-23); the substrate registry pins sha256 only. These stay
`unaudited` in every FA figure. Retention lesson: substrate bodies should
enter the CAS at registration — the CAS now provides exactly that surface.

## The cohort correction

Eleven of the 57 breadth controls are now adjudicated defective (eight from
the Sol-audit era, three here), so every seed-20260819 subject's FA
corrects. Per subject, over breadth cells only (anchors excluded, as the
claims exclude them): FA_min counts adjudicated-sound refusals alone;
FA_max adds still-unaudited refusals.

| subject | defective excl | FA (sound) | FA (unaudited) | clean n | FA_min | FA_max |
|---|---|---|---|---|---|---|
| or-gemini-3-7-flash-high | 11 | 0 | 1 | 46 | 0.000 | 0.022 |
| codex-sol-high | 11 | 1 | 3 | 46 | 0.022 | 0.087 |
| agy-gemini-3-7-flash-medium | 11 | 1 | 4 | 46 | 0.022 | 0.109 |
| glm-5-3-max | 11 | 2 | 4 | 46 | 0.043 | 0.130 |
| or-ox-alpha | 11 | 2 | 5 | 46 | 0.043 | 0.152 |
| agy-gemini-3-7-flash-high | 11 | 3 | 3 | 46 | 0.065 | 0.130 |
| cc-glm-5-3-max | 11 | 4 | 3 | 46 | 0.087 | 0.152 |
| deepseek-v4-flash | 11 | 5 | 7 | 46 | 0.109 | 0.261 |
| oc-glm-5-3 | 11 | 5 | 5 | 46 | 0.109 | 0.217 |
| oc-deepseek-v4-flash | 11 | 10 | 4 | 46 | 0.217 | 0.304 |
| oc-deepseek-v4-pro | 11 | 12 | 3 | 46 | 0.261 | 0.326 |
| codex-harm-sol-max (partial run) | 3 | 1 | 2 | 19 | 0.053 | 0.158 |

Readings:

1. **The deepseek refusal tax is confirmed, not excused.** Both opencode
   arms keep the cohort's worst FA even after eleven defective controls
   leave every denominator — their refusals were overwhelmingly of
   genuinely sound controls (12 and 10 adjudicated-sound refusals; no other
   subject exceeds 5). The family's failure shape is the ruled pattern:
   importing out-of-set obligations, compounded for pro by resolving
   against the wrong tree entirely.
2. **codex-sol-high's 20260819 FA was mostly defective-control artifact**:
   corrected to 0.022–0.087 from the claimed 0.196. Its clean-v2-contract
   FA of 0.600 (the 20260823 remeasurement, Principal-adjudicated) is a
   different instrument and stands; the v1-changeset quarantine on
   20260819 rows also stands. No class change follows from this table
   alone.
3. **Every seed-20260819 claim needs adjudication-aware re-minting** — the
   recorded claims carry `unaudited_refusals` counts and denominators that
   this audit supersedes. Re-minting is the measurement pipeline's step;
   the leaderboard regenerates from the claims.

Records: adjudication ledger `advisory/control-adjudications.jsonl`
(records 25–42, basis_kind mechanical-oracle), oracles in
`advisory/checks/`, auditor analysis by four parallel Claude agents at
Principal request, oracles re-verified by the assembling session.
