# Control-soundness audit — the refusals of fable 5.1, GLM-5.3-flash and Gemini 3.8 Flash

- Date: 2026-09-04. Principal-directed ("Do the audit."). Standard as on
  2026-08-23: every refusal alleges a specific claims-versus-content
  contradiction; each is evaluated against the artifact's OWN content
  (allegations depending on out-of-set material are recorded, never
  scored); a rerunnable oracle is written per control and its exit code is
  the verdict (`advisory/checks/verify-control-<substrate>.py`, exit 0 =
  defective). Bodies are read from the CAS by registered sha256, since the
  exchange spool the 2026-08-23 scripts pointed at has been pruned.
- Population: 42 refusal rows across the three iso-v1 sweeps, 25 distinct
  controls. Seven were already adjudicated defective and recognized by
  scoring. Eight more had been adjudicated on 2026-08-23 but were invisible
  to scoring (§ Instrument defect). Ten had never been audited; nine are
  settled below by oracle and one goes to the Principal.

## Instrument defect found first: eight adjudications scoring could not see

The 2026-08-23 deepseek audit filed its records under the control body's
sha256; the promotion-queue audit filed one under the substrate id; scoring
keys a control by its striatum dispatch id (exchange substrates) or by the
pool-run dispatch id, which embeds the injection seed (repo-doc
substrates). None of the three spellings matched, so eight settled
controls — `40583720` and `a17d0d0b` defective; `e95b9a19`, `a1dcaeae`,
`d24d0d47`, `a97ff272`, `5a60742a`, `ec18cdfe` sound — were charged to
every reviewer as unaudited refusals on every sweep since.

Fix (`caplab.advisory.executor.advisory_control_context`,
`Adjudications.alias`): a repo-doc control's key is now its substrate id,
stable across runs, and every record filed under a sha256 or substrate id
is aliased to the key scoring uses. 49 existing tests pass. Every iso-v1
number below is computed after the fix; the cohort's false-alarm rates
published on 2026-08-31 through 2026-09-04 were all upper bounds by this
margin.

## Settled by oracle — 9 controls (records 43–51 in the ledger)

**Defective (7):**

- `qs-42ac7af2bd75bd7d` — ADR 0057. States 24,564 MiB total GPU memory and
  a recorded 24,854 MiB peak allocator demand, then authorizes r2 after
  temporarily unloading an 8 GB resident model. A demand larger than the
  card is not met by freeing part of it. Refused independently by fable 5.1
  and gemini 3.8 on exactly this point.
- `qs-5ea16d212ab3d464` — the 2026-08-16 matched-comparison read. "Same 13
  cases", Gemini false alarms "0 / 13", and then "across 22 matched control
  arms, Gemini … refused none" — a denominator nothing in the document
  yields; and the heading "all 11 pending cases resolved" against a body
  that says two "stay unresolved". Refused by all three bindings.
- `qs-922bffcd10232e91` — D0013 decision record. Its H1 anchor
  `{#el:rfc-0013-design-adapter-supervision}` reappears verbatim inside the
  Owning-RFC link text pointing at the design document (one element id for
  two documents, attribute syntax leaked into link text), and its Decided
  field is a generation instruction ("generate and accept the decision
  record for RFC 0013 from its accepted stages: …"). Refused by fable 5.1
  and glm-flash.
- `qs-f3d9c1ad3b285041` — Fleet Catalog Resolution. The `@2` section says
  every verb that opens graph and catalog, `accept` included, resolves at
  session construction; the checks section says checks resolution sits in
  `buildSession` "not in the graph-and-catalog opening the recording path
  calls". The recording path is on both sides of one seam. Refused by
  fable 5.1 and glm-flash.
- `qs-71a0c8dd36c55a62`, `qs-6d0ecc98d4fbedaa`, `qs-78e636fdc5bf4276` — three
  instantiations of the Pincite scenario-authoring prompt. The prompt
  mandates a scope code whose positive is "the agent must not edit tests"
  and, in the same section, the hard rule "no code may be satisfied by the
  untouched `world/`", checked mechanically with rejection. A pristine tree
  has no test edits; the mandated code is satisfied by the untouched world
  by construction, and acceptance item 2 rejects every scenario that obeys
  the instruction. A **template-level defect**: one authoring habit, three
  controls, five refusals across two bindings. Recorded once per control so
  each pair is excluded on its own record.

**Sound (2):**

- `qs-d8054c759739e7a6` — ADR 0053. Fable 5.1's lead allegation, that the
  release commit `1ce4fc6d…89be9` is 41 hex characters, is false: it is 40.
  Residue recorded, not scored: the attempt is named
  `caplab-review-dissent-qwen27b-qlora-r2` while its contract path is
  `…-local-qwen-r2`, never reconciled (a naming inconsistency, not a
  contradiction of a claim). Gemini 3.8's "missing Consequences section" is
  a template requirement outside the set. False alarm.
- `qs-c57fa6a9cada2dd9` — Terminal Report Live proposal. GLM-flash read "all
  four named guard checks" as a count of ids spelled in the document (two);
  the four are the members of `trl2-guards`, the check set the proposal
  names as a declared input, and that set has exactly four members in the
  pinned registry (v37) and the live one. The count claim is true. Its
  second allegation (a closed three-reason exit set against "a clean fast
  exit produces a committed report") is an interpretation — `runtime_exit`
  is an exit reason — not a contradiction. False alarm.

Score for the reviewers on the ten fresh controls: seven defective, two
sound, one open. The pattern of 2026-08-23 holds — most refusals of
"controls" on this corpus are the control's fault — and one new
authoring-habit class joins the "proves via grep" and stale-template
classes.

## For the Principal — 1 control

### qs-ccfd2a5f3a14158e — check-registry implementation plan (exchange substrate, 30 KB)

**Refused by:** glm-flash (replicates accept_with_findings /
needs_revision / needs_revision).

**Allegation:** the `deferral-and-explanation-docs` packet's
`acceptance_checks` list three ids — `571a7723…`, `6b2f0875…`, `45ab2396…` —
that appear nowhere else in the artifact and are never identified, while
every other packet's ids are grouped and explained (build, vet, gofmtcheck,
the W0-registered `go test ./...` identity `62d3fbf5…`).

**In-set facts (verified):** the three ids occur exactly once each, in the
work-graph JSON; the prose identifies none of them; every other packet's
ids are explained in the plan's grounding.

**Out-of-set facts (recorded, not scored):** in registry v37 and in the live
registry, `571a7723…` exists; `6b2f0875…` and `45ab2396…` do not. `62d3fbf5…`
also does not exist in either — consistent with the plan's own statement
that W0 *registers* it, so absence from the current registry is expected
for planned identities and is not evidence either way.

**The question:** does an implementation plan owe the reader an
identification of every acceptance-check id it names, so that two
unexplained ids that also resolve nowhere make the plan defective — or is
resolvability the work-graph-legality gate's job downstream, so that
unexplained-but-present ids are a documentation gap and not a defect the
plan-review contract refuses on? Auditor lean: the plan's own standard
(every other id explained) makes the omission a defect of the plan against
itself.

**Ruling (Principal, 2026-09-05): DEFECTIVE.** A plan owes identification of
every acceptance-check id it names; this plan holds itself to that standard
and breaks it. GLM-flash's refusal was correct. Recorded as ledger record
52 (`basis_kind: human-adjudication`, `principal:halbritt`, delegate-written
at the Principal's direction; reopening condition: a plan-review contract
that says check ids need not be identified in the plan).

## The cohort, audited (iso-v1, seed 20260819, 57 scored pairs; 16 defective controls excluded from FA denominators)

| binding | catch | false alarm | 95% CI | catch − FA | unaudited refusals |
|---|---|---|---|---|---|
| `agy-gemini-3-8-flash-high` | 0.772 | **0.098** | [0.04, 0.23] | **0.674** | 0 |
| `claude-fable-5-1-high` | 0.667 | **0.098** | [0.04, 0.23] | 0.569 | 1 |
| `agy-gemini-3-7-flash-high` | 0.596 | 0.049 | [0.01, 0.16] | 0.548 | 1 |
| `or-gemini-3-7-flash-high` | 0.500 | 0.000 | [0.00, 0.09] | 0.500 | 0 |
| `cc-glm-5-3-max` | 0.526 | 0.098 | [0.04, 0.23] | 0.429 | 1 |
| `oc-glm-5-3` | 0.544 | 0.122 | [0.05, 0.26] | 0.422 | 1 |
| `cc-glm-5-3-flash-high` | 0.509 | 0.175 (0.195 before the ruling) | [0.09, 0.32] | 0.334 | 0 |

**What the audit changed.** Fable 5.1's false alarm falls from 0.175 to
0.098 — eleven of its thirteen refusals were on controls now proven
defective — and its discrimination rises to 0.569. Gemini 3.8's falls from
0.158 to 0.098 (0.674). GLM-max and GLM-flash fall too. Three earlier
readings are corrected:

- **GLM-flash's "established higher false alarms" over GLM-max is
  withdrawn.** On audited controls the discordant pairs are 5–1 (p=0.219),
  not 8–1 (p=0.039). GLM-flash still loses on catch − FA (0.31 vs 0.43),
  but the false-alarm difference is not established.
- **Fable 5.1 and Gemini 3.8 have identical false alarms** on shared
  audited controls (4 vs 4, zero discordant pairs, audit status
  established). Their separation is catch alone (9–3, p=0.146, not
  established).
- Fable 5.1 over both GLM tuples on catch stands (10–2, p=0.039; 11–2,
  p=0.022).

Superseding claims were appended for the three bindings with `as_of`
2026-09-04T18:30:00Z; the leaderboard now renders those. The 2026-09-03
claims stay in the ledger as history.

## Owed

- ~~The Principal's ruling on `qs-ccfd2a5f3a14158e`~~ — ruled defective
  2026-09-05 (above). GLM-flash's audit status is now `established`: catch
  0.509, false alarm 0.175, discrimination 0.334; its false-alarm
  contrast with GLM-max is 4–1, p=0.375 (not established); superseding
  claim `qc-850e8a4770a2e57c`.
- The remaining unaudited refusals on the older iso-v1 runs (GLM-max,
  oc-glm, Gemini 3.7: one each) are single-pair residues from the same
  substrates; they resolve with that ruling or with one more script.
