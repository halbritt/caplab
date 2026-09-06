---
plan_id: tree-v1-review-environment
revision: 2
artifact_type: plan
status: approved  # Principal, council topic caplab #50, 2026-09-06
supersedes: plan-tree-v1-review-environment revision 1 (CAPLAB execution delegate, 2026-09-06)
decision_owner: repository-owner
author: council scribe (fable), from synthesis-2026-09-06-tree-v1.md
intended_path: docs/product/plans/plan-tree-v1-review-environment.md
---

# Plan: a review environment with the pinned base present (`tree-v1`), revision 2

This revision replaces the delegate's plan of 2026-09-06 in full. Nothing in
revision 1 survives by reference; where this document is silent, revision 1
does not apply. Decisions the Principal has already taken are recorded in §12
so the executing delegate does not re-ask them.

## 0. What is wrong, stated correctly

`iso-v1` (2026-08-23) put every review lane under bubblewrap with `~/git`
masked by a tmpfs, a neutral case-workspace cwd, and review preamble v2
("the filesystem is not the artifact; judge references only against the
artifact's own content"). It was not an accident. The read-only bind of that
morning produced wrong-universe resolution (`finding-2026-08-23-wrong-universe-resolution.md`:
reviews resolving striatum-next references against the caplab checkout), and
masking was the deliberate second step.

Three consequences follow, and the plan must answer all three, not one:

1. **Two levers moved at once.** The tree was removed and the preamble told
   subjects not to look for it. Per-substrate rows from the two Sol sweeps
   on seed 20260819 show the shift is not uniform:

   | substrate (pairs) | pre-isolation controls refused | `iso-v1` controls refused |
   |---|---|---|
   | repo-doc (26) | 4 | 26 |
   | exchange prose (18) | 2 | 18 |
   | change set (25) | 11 | 21 |

   The exchange-prose references Sol refused on (escalations, receipts,
   execution contracts, ADR ids) do not live in any git tree, yet
   pre-isolation Sol cleared 16 of 18 of those controls. The pre-isolation
   codex transcripts do not exist on this host, so how it cleared them
   cannot be recovered. No stop rule in this plan is anchored on the
   pre-isolation 0.20 false-alarm figure.

2. **Neither existing cohort measured reference resolution correctly.**
   Pre-isolation rows resolved against the live checkout, which is the
   wrong tree for exchange artifacts. `iso-v1` rows resolved against
   nothing. `tree-v1` is the first environment that supplies the right tree.

3. **The adjudication ledger is partly a ledger about `iso-v1`.** Of 71
   control adjudications, 36 rest on the out-of-contract rule (25 sound,
   11 defective): the mechanical check verifies that the alleged text is
   present in the artifact and then rules reference resolution
   out-of-contract. Under `tree-v1` reference resolution is in-contract, so
   those labels must be re-derived before any scored run.

Separately, and more urgent than the tree: **the current sandbox is not the
containment the records describe.** `pool_runner.sandbox_argv` binds `/`
read-only, then the whole home directory writable, then a tmpfs over
`~/git`. Inside every lane today the following are readable and writable:
`~/.local/share/striatum` (136 GB: graph store, exchange, keys, deploys),
`~/.cache` (74 GB), and `~/.config/plane` (API tokens). `treeguard` watches
tracked files in two git checkouts and nothing else. Revision 1 §7 stated
that the store stays masked; it does not.

## 1. Facts established (all checked on 2026-09-06)

| fact | value | where |
|---|---|---|
| substrates in the registry | 652 (309 repo-doc at two commits, `c4c8e24…` ×191 and `dc79462…` ×118; the rest exchange) | `advisory/substrates.jsonl` |
| the seed-20260819 draw | 69 pairs: 26 repo-doc (`v1`), 25 change set (`v2-changeset`), 18 exchange prose (`v1`) | any `iso-*` `results.jsonl` |
| change-set bodies carry | `base_composition` (product plus ancestors with `content_hash`, `identity`, `version_seq`), `result_tree_hash`, `resulting_base_hash`, per-file `content_hash` | spilled prompts under `iso-codex-sol-high-20260819/workspace/` |
| change-set base coverage | 81/81 products, 593/593 ancestors in the graph store (revision 1 §1, not re-verified here) | graph store `~/.local/share/striatum/graphs/019f22ef-…` |
| `hash_mismatch` operator | skips every sha256 under `base` / `base_composition`; can land on `packet_element_hash` and `work_graph_version_hash`, which no environment makes checkable | `instrument_defects.hash_mismatch` |
| adjudication ledger | 71 records; 58 mechanical-oracle, 13 human or principal; 36 grounded in the out-of-contract rule | `advisory/control-adjudications.jsonl`, `advisory/checks/verify-control-*.py` |
| full striatum-next archive | 27 MB (vendor 1.2 MB) | `git archive HEAD` |
| harness config | each cohort harness runs with its own config directory under `~/.local/share/striatum/harness-config/` (`CLAUDE_CONFIG_DIR`, `CODEX_HOME`, `HOME` for agy); the claude-code one declares no MCP servers; lanes take API keys from environment; opencode alone uses the real home | `~/git/striatum-next/backends/*/backend.yaml` |
| the real `~/.claude.json` | declares MCP servers for Plane, RunPod, Home Assistant, and a personal database; no cohort binding loads it | `~/.claude.json` |
| striatum-next root | carries `AGENTS.md` and `CLAUDE.md` (17.7 KB, operational directives) plus `.claude/` and `.agents/` | checkout root |
| board cohort | `CURRENT_COHORT = ("caplab-advisory", "synthetic-contract", "20260819", "iso-v1")` | `scripts/build_leaderboard.py` |

## 2. What `tree-v1` is

### 2.1 Environment

`ENVIRONMENT_VERSION = "tree-v1"` opens a new cohort. Environment, profile,
preamble version, operator version, and base source are claim identity.
Rows and claims on `tree-v1` never pool with `iso-v1` or pre-isolation rows.

### 2.2 Containment (two stages)

**Stage A, lands first, before any other work.** Amend `sandbox_argv`:

- tmpfs over `~/.local/share/striatum`, then re-bind
  `~/.local/share/striatum/harness-config/<harness in use>` writable on top;
- tmpfs over `~/.local/share/striatum-tuner`, `~/.config/plane`, and
  `~/.cache`, re-binding `~/.cache/go-build` writable for agy (its
  declaration sets `GOCACHE` there);
- home otherwise writable only for `~/.config/opencode` and
  `~/.local/share/opencode`;
- `~/git` stays masked; the case workspace stays the only writable path
  the subject is pointed at; `/tmp` stays shared; `--die-with-parent` stays.

No model process launches under the old mount. Static work (§4, §5) may
proceed in parallel.

**Stage B, lands before any model process (probes, dry run, sweeps).** The
allowlisted synthetic home: tmpfs over all of home, then bind only the
harness's own config directory (or the opencode directories), the case
workspace, and `/tmp`. Because striatum already segregates harness state,
this is a small change to the same function. It makes the credential scope
structural rather than declaration-dependent.

**Accepted residuals, recorded on the environment definition:**

- The subject can read its own harness's inference credentials. Verified
  inference-scoped for all eight cohort harnesses on 2026-09-06; re-verify
  whenever a backend declaration changes.
- Network stays open. Every binding reaches its model over the network and
  bwrap cannot filter by port. The controls against remote-commit escape are
  the masked checkouts, the masked store, and the tree guard.

**Tree guard** extends to the materialized base: manifest digest checked
before and after every attempt (§2.4).

### 2.3 Materialization

Before a case's arms run, the case's base is written as plain files to
`<workspace>/<case>/base/`, then re-bound read-only on top of the writable
workspace bind. Materializers:

| substrate | materializer | base source recorded | status |
|---|---|---|---|
| change set | `composed-product`: the `observed_product` snapshot plus every ancestor change set in application order, `deletes` honoured | product object hash, ancestor chain | exact |
| repo-doc | `git-archive` at the pinned commit, materialized once per commit and bound read-only per case | repo, commit | exact |
| exchange prose | `product-head-at-seq`: the ledger locates the run's seq, the repository snapshot object current at that seq is read from the graph store | object hash, seq | exact where it resolves |
| exchange prose, referenced objects | `exchange-objects`: every escalation, receipt, contract, or other exchange object the artifact names, resolved by identity from the graph store, placed under `<workspace>/<case>/evidence/exchange/` | object identities | exact where it resolves |
| any | `git-at-time` (checkout at the last commit before the run timestamp, repository resolved per case, never hardcoded) | repo, commit, commit distance from the true base if known | **diagnostic only; never on a scored row** |

A case whose exact base or a required referenced object does not resolve is
`unscorable_missing_base`. It is excluded from every scored denominator and
counted in the coverage report.

Shared per-commit archives are safe only with all three guards: the shared
source is immutable, its manifest digest is checked per attempt, and
case-specific material goes to the per-case `evidence/` directory, never
beneath the shared tree.

### 2.4 Manifest

`<workspace>/<case>/base-manifest.json`, written at materialization,
verified before and after every attempt, digest recorded on every row:

- `base_source`, base identity (object hash or repo plus commit), the
  ancestor chain in application order with hashes;
- for every entry: normalized path, type, mode, symlink target, content
  digest;
- every entry removed or transformed for the subject-visible view (§2.6),
  with the exact-snapshot digest and the view digest both recorded;
- file count and bytes.

Materialization rejects: symlinks to absolute paths, `..` components,
device and socket files, duplicate normalized paths, case-fold collisions.

### 2.5 Sandbox and cwd

Same bwrap as §2.2 with `<workspace>/<case>/base` and
`<workspace>/<case>/evidence` re-bound read-only. cwd is the case workspace.
The only writable paths are the workspace root (prompt spill file, and any
copy the subject makes of `base/` to apply or diff) and the harness's own
config directory.

### 2.6 Harness instruction files

The exact snapshot is what the oracle (§6) and anchoring verify; it is
never filtered. Whether the subject sees the same bytes is decided by probe:

1. Probe each harness for whether it loads `AGENTS.md`, `CLAUDE.md`,
   `.agents/`, or `.claude/` from a subdirectory of the workspace when it
   reads files there.
2. Where a harness loads them, prefer a harness configuration that disables
   project-instruction discovery for that invocation.
3. Where no such configuration exists, the subject sees one canonical
   filtered view, byte-identical for every harness, with both digests and
   the mechanism recorded on the row. Never a per-harness tree.

### 2.7 Contract

New profile ids `v1-tree` (prose, repo-doc) and `v3-changeset`. The review
preamble bumps to version 3 and replaces its second paragraph with:

> The repository tree this artifact belongs to is at `<workspace>/base`,
> read-only. It is an unpacked snapshot: there is no `.git` directory and no
> commit history; inspect files directly. Exchange objects the artifact
> names, where they were recoverable, are under `<workspace>/evidence/`.
> Resolve the artifact's references, paths, and hashes against those trees
> and nothing else. You may copy `base/` elsewhere in the workspace to apply
> a change set or compute a diff. Anything else on the filesystem is your
> execution environment, not the repository.

`v3-changeset` drops v2's "the base tree is NOT available to you" and
restores anchoring as a checkable claim: declared base hashes are checked
against `base/`; a change set's `result_tree_hash` is checked against the
virtually applied result, not the unmodified base.

`v1-tree` adds, for prose: the tree is the before-state for resolving
references. A base that already contains the artifact's proposed work is not
evidence that the artifact's claims are sound.

The contract lists what `base/` and `evidence/` contain and do not contain
for the case, so "not reachable from the artifact" is not a legitimate
refusal for a named object that was materialized, and is a legitimate
finding only for an object that was not.

### 2.8 Operators

Operators are versioned with the profile. `hash_mismatch` v3: may flip base
hashes and tree hashes; refuses to flip hashes no environment makes
checkable (`packet_element_hash`, `work_graph_version_hash`); records the
flipped field's checkability class on the row. Every other operator is
unchanged in behaviour and carries the v3 label.

### 2.9 What does not change

Cases and seed (20260819), mutant generation for every operator except
`hash_mismatch`, scoring, the matched-contrast machinery, the board's rule
that cohorts never merge.

## 3. Static evidence classification (no model calls)

For each of the 18 exchange-prose and 26 repo-doc controls, classify every
reference the artifact makes:

- `artifact-local`: resolvable within the artifact;
- `repository-tree`: a path or document in the repository at the pinned base;
- `exchange-object`: an escalation, receipt, contract, or other object by identity;
- `unavailable-anywhere`: no trace in the graph store or git history.

Outputs: per-case resolvability rate against the materialized base; the
exact-coverage figure for `product-head-at-seq` on the draw; the list of
exchange objects the `exchange-objects` materializer must supply. This is
the prose and repo-doc correctness oracle. It also answers, for free, how
much of Sol's exchange-prose shift the tree can explain. The preamble-only
LLM ablation from the council discussion is run only if this classification
leaves the preamble-versus-tree question open, and then on Sol alone.

## 4. Label revalidation (before any scored run)

Re-run every adjudication grounded in the out-of-contract rule with a
resolution step against the exact base. Each re-run records one outcome:

| outcome | meaning | effect on the case |
|---|---|---|
| `resolved-valid` | the reference resolves and names what the artifact says | label stands |
| `resolved-invalid` | the reference resolves and contradicts the artifact, or does not resolve in an exact base that should contain it | control defective |
| `evidence-unavailable` | the object existed and lost custody | case unscorable |
| `reference-unresolvable-anywhere` | no trace anywhere | case unscorable by default, flagged for audit; never auto-sound, never auto-defective |
| `reference-not-required` | the allegation does not depend on the reference | label stands |

Carry forward only labels formally environment-invariant (mechanical in-set
predicates) or confirmed by re-run. Missing custody never rewrites ground
truth in either direction. Human and principal rulings are re-examined case
by case and re-affirmed or re-ruled by the Principal.

## 5. Stop rule and pre-registration

Sol and Gemini 3.8 run first, as the two ends of the hypothesis. The stop
rule is read per substrate (repo-doc, change set, exchange prose), per
operator, and two-sided: refusals on sound controls within the pre-registered
bound **and** catch held at or above the pre-registered floor. It is read
against revalidated labels only.

Before the dry run, write down for every substrate by operator by direction
cell: the exact denominator, the acceptable count, the confidence method,
and the minimum catch opportunity. Name which cells are decision-grade and
which are diagnostic-only. The scored-pair floor per cell comes from a power
calculation for the effect size the board already calls "established" in
its matched contrasts. A cell below its floor reports descriptively and can
neither trip nor pass the stop rule. Prefer paired changes from `iso-v1` on
the same revalidated cases over any global historical figure.

Pre-registered expectations:

- Sol: refusals of sound controls fall on repo-doc and change sets; catch
  held. Exchange-prose refusals fall only to the extent §3 shows the
  materializers supply what the artifacts reference. High exchange-prose
  refusals with low §3 coverage is a coverage finding, not a stop.
- Every agentic binding: structural catch rises; `hash_mismatch` v3 above
  1/4 for at least the top three; `base_dropped` checkable by all;
  `anchored` rises.
- The two one-shot lanes: no material change. Reason stated on the
  declaration: the adapter is a single API call with no tool loop, so the
  lane cannot open `base/`.
- The tier-1 question (Gemini 3.8 versus fable 5.1) is asked again on this
  cohort; no expectation recorded.

If Sol's decision-grade cells fail in the direction of "tree present, still
refusing sound controls whose references resolve," the plan stops for a
rethink. If they fail in the direction of "catch collapsed," that is a
separate failure with its own rethink; it does not auto-continue.

## 6. Verification before any model is spent

1. **Unit tests** for every materializer, including composition of a
   change-set base from product plus ancestors with `deletes` honoured, and
   rejection of every unsafe entry class in §2.4.
2. **Change-set oracle, two steps, all 81 products, fail closed.** First,
   every declared base hash is checked against the materialized base.
   Second, the change set is applied and `result_tree_hash` recomputed. Any
   mismatch stops the plan.
3. **Prose and repo-doc oracle:** the §3 classification. Every
   `repository-tree` and `exchange-object` reference must resolve in the
   materialized trees, or the case is unscorable.
4. **Manifest verification** before and after every attempt, digest on the row.
5. **Probes**, one per harness (claude-code, agy, codex, opencode, lane),
   run under Stage B containment:
   - answers inside `tree-v1` and can read `base/`;
   - cannot modify, delete, rename, chmod, or create under `base/` or
     `evidence/`;
   - cannot write to the live checkouts, the graph store, the exchange,
     `~/.config/plane`, or a sibling case directory;
   - cannot create a git commit, hook, or lock file that persists outside
     the workspace;
   - symlink and hard-link escape attempts fail;
   - positive fidelity: the probe quotes a nonce planted in `base/`, proving
     the model and not only its launcher received the tree;
   - instruction-loading: whether the harness loads `AGENTS.md` or
     `CLAUDE.md` from `base/` (§2.6);
   - for the one-shot lanes: the declaration states why the lane cannot
     open the tree, and the probe confirms the lane answers.
6. **Dry run:** two cases per profile on one cheap binding, rows inspected
   by hand for the base path appearing in findings the way it should.
7. **Teardown** in a per-attempt `finally` in `scripts/supervise_sweep.py`;
   orphaned workspaces from an aborted session are reclaimed on the next
   supervisor start.

## 7. Disposition of `iso-v1` (Principal, #40; council #41, #43, #46, #47)

- Raw rows stay. The `iso-v1` ordering stays on the board, labelled:
  reference-resolution performance is invalid, the ordering is provisional,
  and it must not be read as evidence against verification-oriented
  bindings.
- Prospective rule: no new qualification or negative-placement decision
  cites the affected `iso-v1` dimensions. Existing permitted tuples
  continue; nothing is newly excluded.
- Sol's permitted tuple stays. Sol's `review: frontier` tier is marked
  provisional now (Principal, #50 item 4). Striatum should not let that tier
  label feed a routing decision before re-measurement.
- Retroactive flips: every original `iso-v1` claim is preserved (claims are
  content-hashed). Where §4 changes a denominator or truth label, the
  corrected `iso-v1` claim is re-emitted labelled as corrected, and any
  downstream consumer that copied the original number is named. Decisions
  remain prospective.
- The `iso-v1` rows remain informative for in-set defect classes and for the
  one-shot lanes; the record says so.
- The precise supersession record and the board sweep (`docs/leaderboard`,
  every export) land when the eight bindings are on `tree-v1`.
- `CURRENT_COHORT` switches to `tree-v1` only then, and the rule is enforced
  in `build_leaderboard.py`, not remembered.

## 8. Order of work

| step | work | model calls | gate to next step |
|---|---|---|---|
| 1 | Stage A containment; provisional `iso-v1` label; Sol tier marked provisional | none | mask verified by a non-model probe (a shell under bwrap cannot write the store) |
| 2 | Static evidence classification; exact-coverage figure on the draw; exchange-object list | none | coverage report written |
| 3 | Label revalidation with §4 outcomes; corrected `iso-v1` re-emissions | none | every out-of-contract label re-derived |
| 4 | Stage B allowlisted home; full probe set (§6.5) | probes only | every probe passes on every harness |
| 5 | Materializers, manifest, both oracles, `hash_mismatch` v3, contract v3, preamble v3; pre-registered cells and floors written | none | oracles pass on all 81 products; §3 references resolve or cases marked unscorable |
| 6 | Commit the Opus `iso-v1` run directory; `ENVIRONMENT_VERSION` bump; dry run | ~4 pairs | rows inspected |
| 7 | Sol and Gemini 3.8, two lanes each, under the §5 stop rule | 2 × 69 pairs | decision-grade cells read |
| 8 | Remaining six `iso-v1` bindings and Opus | 7 × 69 pairs | eight bindings on `tree-v1` |
| 9 | Supersession record, board sweep, `CURRENT_COHORT` switch | none | done |

## 9. Cost

Engineering: containment (both stages), materializers, manifest, two
oracles, operator and contract versioning, probes, classification tooling,
ledger re-runs. Two to three working days, up from revision 1's one, because
revision 1 omitted containment, classification, and revalidation.
Measurement: unchanged from revision 1, 9 sweeps × 69 pairs, two to three
days of wall clock across four accounts, minus every pair marked unscorable.
Disk: 27 MB per repo-doc commit shared across cases, plus ~15 MB per
change-set case, reclaimed after each run.

## 10. Risks, named

- **A forgotten path in the mask.** Stage A is piecewise. Stage B closes it
  structurally before any model runs. The §6.5 probes are the check.
- **Escape into `base/`.** Read-only bind is the control; the probe tests
  it; the manifest digest before and after every attempt notices it.
- **Coverage.** If §3 shows `product-head-at-seq` resolves few of the 18
  prose cases exactly, the prose class is small. It reports as underpowered
  rather than as a noise contrast; nothing is padded with approximate bases.
- **Instruction leakage.** §2.6 makes it a measured, uniform property of the
  environment rather than an accident.
- **OOM.** With the store masked and the base in the workspace there is
  nothing to hunt for. The masks make this true; revision 1 assumed it.
- **Comparability.** `tree-v1` numbers compare to nothing earlier. The board
  never merges cohorts.

## 11. Records this plan owes

- An amendment to `incident-2026-08-23-replay-escape-containment.md` stating
  what the sandbox actually contained between 2026-08-23 and Stage A.
- A finding record for the ledger dependence on the out-of-contract rule (§0.3).
- The coverage report (§3), the revalidation record (§4), the
  pre-registration record (§5), and the probe record (§6.5), each before the
  step that depends on it.
- The supersession record (§7) at step 9.

## 12. Decisions already taken (Principal, #50)

1. `tree-v1` approved as specified here, including exact bases only with the
   exchange-object materializer, the amended order, and the amended stop rule.
2. Residuals in §2.2 accepted, with re-verification on any declaration change.
3. Retroactive rule in §7 confirmed: originals preserved, corrected `iso-v1`
   claims re-emitted and labelled, decisions prospective.
4. Sol's `review: frontier` tier marked provisional now.

Nothing in this plan awaits a further ruling. Work begins at step 1.
