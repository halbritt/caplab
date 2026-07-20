---
id: caplab-p13-independent-verification-2026-07-20
artifact_type: verification-record
assertion_type: verification
work_item: CAPLAB-33
campaign: caplab-p13-independent-verification-2026-07-20
authorization: adr-0025
verifier: /root/p13_independent_verifier
verified_at: 2026-07-20
technical_verification: fail
caplab_v0_criteria: unmet
cleanup_status: fail
---

# CAPLAB P13 independent verification

## Verdict and authority ceiling

`technical_verification: FAIL`.

`caplab_v0_criteria: UNMET`.

I am `/root/p13_independent_verifier`, the executor named by
[`adr-0025`](../decisions/adr-0025-caplab-p13-independent-verification-authorization.md).
I did not implement or execute the bound P7 through P11 work. I performed this
campaign in branch `verify/caplab-33-independent` at
`/home/halbritt/git/caplab-wt/verify-caplab-33-independent`.

This verdict is technical verification only. It is not CAPLAB acceptance,
revision, or rejection; it does not alter ADR 0023 or ADR 0024; and it grants no
authority for P12, P14, repair, retry, model calls, training, export,
publication, routing, or deployment.

The technical verdict fails because the one authorized live P7 lifecycle did
not reach ready state or either recomputation. The installed controller refused
`enable` with `campaign state already exists`. The preinstalled cleanup trap
then ran aggregate disablement, but `disable` failed on the prior, already
absent Garage key identity and changed the retained state to
`disable_incomplete`; `verify --phase disabled` therefore failed. External
observations found no live access, and protected data inventories matched, but
those observations cannot replace the frozen controller cleanup oracle.

The v0 criteria remain unmet independently of that technical failure. ADR 0024
selected `no-example-eligible`, authorized no export, and left the required v0
export criterion unmet. A technical pass would not change that decision.

## Frozen identities and custody

The campaign began at `2026-07-20T07:17:35Z`, before ADR 0025's
`2026-07-21T23:59:59Z` expiry. The worktree was clean at authorization commit
`08d989c2e946e8a3e149cb5858d4e018bb01b9d7`. Its sole parent is the clean
product-and-decision baseline
`cc6044fb8418d7ddafa1005e0e941616bd8cdc1f`. Proximal was clean at desired
state `1b79aa07cc4e44e8fc828449f882c6b62008edb6`.

The new evidence root is
`/var/tmp/caplab-p13-verification-2026-07-20`, owned by `root:root` with mode
`0700`. Files inside it are root-owned and mode `0600`, except its mode-`0700`
subdirectories. `SHA256SUMS` covers every retained file other than itself. Its
SHA-256 is
`08e5139f12c0874d73d947b449549480ad84308c5fd3a89cab6e6eea03b9bbef`.

The following source manifests were verified with `sha256sum -c SHA256SUMS`
from inside their evidence roots during the campaign. The P6, P7, P8/P10, and
final P5 purge roots were verified before deterministic replay; the two earlier
P5 recovery roots were verified before the verdict:

| Source evidence | `SHA256SUMS` SHA-256 | Result |
|---|---|---|
| P5 recovery execution, `/var/tmp/caplab-p5-execution.20260716T195028Z` | `ded324dc5063be625de293ee915b9bbdb80db314c70890a2bedfde5b4a439070` | PASS |
| P5 successful isolated restore, `/var/tmp/caplab-p5-execution.20260717T193535Z` | `473bfcead0c8482d4623c604bf03d301ea6085b378c78a9a1db3739cc9e7339b` | PASS |
| P5 exact purge, `/var/tmp/caplab-p5-execution.20260717T220619Z` | `93931de9929b8ae4beedbd91d22a40cf39effa0b1a70486dbcb4bb7163df3e0b` | PASS |
| P6 execution, `/var/tmp/caplab-p6-execution.PZsK9Rnd` | `9b1aae3deaeeebad7553192d493da2bcb7315517e5a3050e87ce9c6be2dcd1ef` | PASS |
| P6 independent verification, `/var/tmp/caplab-p6-independent-verification.PZsK9Rnd` | `fd0199b1c64f74d6019e98a35704cb37af81c4598703ae6cd3ecc4b58f291045` | PASS |
| P7 execution, `/var/tmp/caplab-p7-execution-2026-07-18` | `42b57e7c7dc38786f32267e6e2f63031cc56e335e592688470d47dcee2ac94e6` | PASS |
| P8/P10 execution, `/var/tmp/caplab-p8-p10-execution-2026-07-20` | `89ea1e396eb8023e1430569edcc740642461b8fd7933f97bded61a93e018b016` | PASS |

The independent P5 promotion-readiness report has SHA-256
`7a8d8e6f8688f69fd35ce9d3720dac4b7aa6d942c5c65c5f4ff0c849eb93c2ad`;
the P5 purge report has SHA-256
`751a27c2900d7271c50749cfc45c5775c4f84eb9e1c44b0cc755376bf416ba50`;
and the P6 independent report has SHA-256
`00fcc64de6b46d3baa9b3ad037f8f0f4225e53832b1fae965e9532d8199e6f69`.

## Commands and methods

The repository gate was:

```text
PYTHONDONTWRITEBYTECODE=1 make check
```

It ran 105 tests successfully; four local-integration tests were skipped by
their explicit opt-in gate. Targeted `unittest` invocations separately
exercised the valid, invalid, missing, altered, ambiguous, duplicate,
interrupted, claim-ceiling, and incomplete-lineage oracles. The first targeted
command named three correct tests under the wrong class names and returned 1.
The corrected command ran those three tests successfully. The complete
repository gate had already run the same tests successfully. This was a
verifier command-selection error, not a product mismatch, and it changed no
product or protected state.

For P6, I verified all 681 preservation-manifest members in place and read the
three selected Git blobs with `git show <commit>:<path>`. Their SHA-256 values
were:

- preregistration:
  `4d8b1418172a0fc6b042efcca6dad96a5dcb08c7ded4006804fce7aa18ff3eb9`;
- result record:
  `870a96b8b528dee1c85337d83662d9900a1fccd7531c181914ed948d02ed0bf4`;
  and
- result CSV:
  `af8d64fde0b7a93773dfc2ac36651d61ee7259095eef792fa7515810a57a2374`.

`build_manifest(source_set(), git_reader=SubprocessGitReader(...))` rebuilt the
registration from those immutable sources. The first invocation correctly
refused `/home/halbritt/git/ethogram` because it is a symlink. Repeating the
same read-only derivation through the non-symlink verifier worktree succeeded
and produced bytes identical to the independently copied sealed registration.
The file SHA-256 is
`e4bd6763e7b37067ea61a1057878641bb484f8ef713e4fa25d80c5484d546992`;
its content identity is
`d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e`.
It contains 684 records, 325 unique content identities, 20 assignments, 20
first attempts, 20 outcomes, eleven required global identity kinds, no broken
assignment-attempt-outcome link, and only `restricted-admission` dispositions.

For P8 and P10, I copied only `registration.json`, `recomputation.json`, the
selected capability card, and ADR 0006 into the verification root. The
provenance receipt retains each source locator, destination, and byte hash. I
then ran each current model-free command twice:

```text
sudo /usr/bin/env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/halbritt/git/caplab-wt/verify-caplab-33-independent/src python3 -m caplab.profile --recomputation /var/tmp/caplab-p13-verification-2026-07-20/independent-inputs/recomputation.json --card /var/tmp/caplab-p13-verification-2026-07-20/independent-inputs/card.md --selection /var/tmp/caplab-p13-verification-2026-07-20/independent-inputs/selection.md
sudo /usr/bin/env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/halbritt/git/caplab-wt/verify-caplab-33-independent/src python3 -m caplab.training_candidates --recomputation /var/tmp/caplab-p13-verification-2026-07-20/independent-inputs/recomputation.json --registration /var/tmp/caplab-p13-verification-2026-07-20/independent-inputs/registration.json
```

Both pairs were byte-identical and matched the sealed execution outputs. The
profile file SHA-256 is
`2c637d554fef3cc8fa0863d7fc922df0452025f0441d813643809269dd639c0e`
and its manifest identity is
`641965dc30fd0dbfca81d56bb05282b01e8e079285ab605c12672e92f3971ef0`.
The candidate file SHA-256 is
`a1aa5c63dddccd19853c1b560e619ae269b92185669d88c71766030ac316d4fa`
and its manifest identity is
`0eeed6348f87d03143ad44c4b9d5440140957c33f32b70e456d80d493aad4a73`.

I altered one promoted-claim field at a time, recomputed the input content
identity, and asked the profile builder to process task-family, cross-task,
model-wide, preference, mechanism, safety, universal-ranking, and Striatum-
placement promotions. Every attempt raised `ProfileMismatch` at the claim
ceiling. I also assigned half of the 20 candidates to `train` and half to
`test`. The one `checkout-retries-study-001` group then spanned both splits;
the manifest's `cross_split_reuse: prohibited` policy made the violation
observable and the independent checker refused it.

Recovery was assessed only from the sealed P5 records and manifests plus the
hermetic synthetic recovery tests. I did not run a live recovery, restore,
repair, or purge.

## Live P7 attempt and cleanup

Before `enable`, installed identities matched the frozen P7 surface:

| Surface | SHA-256 |
|---|---|
| `/etc/caplab/P7_SOURCE_COMMIT` | `c8b6e84e664ad080915af35416f91fb20b2a59f4cf9eee8d7a6193443215d0a6` |
| `/etc/caplab/recomputation.toml` | `0e11bb08976526f1217cf9ceef3a39bd6e960b5d8ee8fd84b63f80c0e36ecbca` |
| `/usr/local/libexec/caplab-p7-accessctl` | `312d110853d5c540e03c4ea94a72c5c9db402518820cf2c1efa095db22e5df46` |
| expiry service | `a853a0c79e5c89174d4ff65bef77fd553e1a38ebc4f0fec0bb50500d43e183e5` |
| expiry timer | `8e18f83e68d6a558818ec01bf023fc96b557a20af9ef3c3a216ecfd3fcd17941` |
| copied runtime Python | `1643dacd9feaedc58f3cc581e4d22577dfe25c09b10282936186ccf0f2e61118` |

The pre-enable `verify --phase disabled` returned 0. I installed an `EXIT` trap
that called only `caplab-p7-accessctl disable` and then
`caplab-p7-accessctl verify --phase disabled` before invoking `enable`.

The ordered results were:

| Step | Status | Observation |
|---|---:|---|
| `/usr/local/libexec/caplab-p7-accessctl enable` | 1 | `campaign state already exists` |
| cleanup-trap `disable` | 1 | prior key identity `GK6473d175f1ed35ed47d94b32` could not be deleted because it was already absent |
| cleanup-trap `verify --phase disabled` | 1 | retained campaign state phase differed |
| first frozen recomputation | not run | ready state was never established |
| second frozen recomputation | not run | ready state was never established |

The frozen recomputation command below was therefore never invoked:

```text
sudo -n -u caplab_reader -- /usr/bin/env -i PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 /opt/caplab/p7/bf6de2b24ac61e82107208cdc609c7e534c6eaaa/bin/python -m caplab.recomputation --config /etc/caplab/recomputation.toml recompute
```

The controller checks the retained state path before creating a new key,
credential, or database login. The refusal therefore preceded new reader
access. The conservative trap still ran because partial enablement had to be
treated as possible until external state was inspected.

At `2026-07-20T07:27:14Z`, external observations showed:

- `caplab_reader`, `caplab_writer`, and `caplab_verifier` were `NOLOGIN` with
  unusable passwords;
- reader sessions and reader processes were zero;
- no `caplab-p7-reader` Garage alias existed;
- `/etc/caplab/credentials/caplab_reader/garage.json` was absent; and
- the `caplab_reader` OS account was locked.

The CAPLAB PostgreSQL dump before and after the attempt was byte-identical,
with SHA-256
`ea4ed04555f7f5fe2fda5676d4fe7bede0473a1d15061c061bb27e6a80ad2b27`.
The Garage bucket summary was byte-identical, with SHA-256
`3638e83066816e80b07a6bd4cbfea8fe93c38133f3237d8f857254bd0d3bdc67`.
All `/nvr/caplab/v0` paths and byte hashes were byte-identical, with inventory
SHA-256
`ca04b6d13b8d21d7aa1930ae9c48da4cea51399c42f3c2f7fe380c409c89ae1f`.

Cleanup nevertheless fails its frozen criterion. The retained state file is
root-owned mode `0600`, has SHA-256
`87b2493047dba924e0eba30c3aa837f4714b748b6414f1c8bc6c8282176c213a`,
and records `phase=disable_incomplete`. No repair or retry was attempted.

## Bounded non-export observation

At `2026-07-20T07:29:30Z`, I inspected only the CAPLAB-controlled surfaces
named by the proposal:

- the bound Git tree at
  `08d989c2e946e8a3e149cb5858d4e018bb01b9d7`;
- the retained P7 and P8/P10 evidence roots;
- the `caplab_v0` database schema;
- Garage bucket `caplab-v0`;
- `/nvr/caplab/v0`; and
- configured paths under `/etc/caplab` and `/opt/caplab`, excluding credential
  contents.

The Git source tree has no P12, dataset, or export package or path. The current
CLI help exposes no export command. The retained P7 and P8/P10 roots have no
path containing `P12`, `dataset`, or `export`. The database has no table or
column name containing those terms. Its one P4 artifact plus 325 P6 study
objects account for the Garage bucket's 326 objects and all 326 independent-
copy paths; the expected and observed `/nvr` key lists were identical. No
configured runtime path contains those terms.

This establishes only that no authorized or materialized P12 bundle,
manifest, dependency, command, or authorization was observed on those named
surfaces at that time. It does not prove that unrelated systems contain no
copied bytes. Technical bounded non-export is PASS; the required v0 export
criterion is `UNMET BY DECISION`.

## Criterion ledger

| # | Criterion group | Status | Evidence and limit |
|---:|---|---|---|
| 1 | Verifier independence, frozen authority, and source custody | PASS | Fresh named executor; clean authorization commit and baseline; exact Proximal identity; all bound source manifests verified from inside their roots. |
| 2 | Repository and hermetic fixture gates | PASS | `make check`: 105 passed, four opt-in integration tests skipped. Corrected targeted valid, invalid, missing, altered, ambiguous, duplicate, interrupted, claim, and lineage oracles passed. |
| 3 | Selected-input and P6 registration identity | PASS | All 681 preservation members and three Git blobs matched; source rebuild was byte-identical to the sealed 684-record registration and its `d2d4...` content identity. |
| 4 | P7 recomputation and historical match | FAIL | Sealed P7 outputs are byte-identical and self-consistent at manifest `68845...` and normalized result `6c4d...`; the mandatory fresh live replay could not start because controller `enable` refused the retained state. |
| 5 | P8 profile and claim ceiling | PASS | Two independent replays matched the sealed `641965...` profile; status remains `pending-human-inference`; every named broader promotion was refused. |
| 6 | P10 candidate lineage and family-safe split | PASS | Two independent replays matched `0eeed...`; 20 `derived-not-eligible` candidates, zero exclusions, complete lineage, one protected group; attempted cross-split reuse of that group was refused. |
| 7 | P5 database, Garage, and independent-copy recovery evidence | PASS | Sealed P5 recovery, successful isolated-restore, and purge manifests verified; independent report hashes matched; isolated synthetic recovery tests passed. No live recovery effect was exercised. |
| 8 | ADR 0023 inference refusal | PASS | Owner, authority, `refuse` disposition, and separate immutable P8 proposal verified; no capability inference was synthesized. |
| 9 | ADR 0024 eligibility decision and bounded non-export observation | UNMET BY DECISION | Decision is `no-example-eligible`; bounded technical non-export checks passed; no export is authorized; v0 export criterion remains unmet. |
| 10 | Access closure, preservation, and evidence sealing | FAIL | External access is effectively closed and protected inventories match, but aggregate controller disablement and its required disabled-phase oracle failed; evidence sealing passed separately. |
| 11 | Residual failures and unverifiable claims | FAIL | Fresh live P7 replay is not verified; retained controller state is `disable_incomplete`; no repair or retry is authorized. |

## Doctrine use and remaining obligations

Pincite packet `pkt-80e80a140d5aa507` was assembled from validated release
commit `65bc86d2555223279e3c0c6cf16be00cce116883`. Its JSON SHA-256 is
`ac6ac066df0e5a2139342ed0f2ff17a3deea1b1c5e2abb4ef139b81cc41c6e66`.
Its authority ceiling is `recommend`; repository authority and current runtime
facts govern this verdict.

The packet's remaining architecture-decision, co-change, version-history,
intervention, and no-change-option obligations are nonmaterial to this frozen
verification verdict. This campaign selects no architecture, proposes no
intervention, changes no product behavior, and makes no refactoring or repair
recommendation. The material authority, accepted-contract, test-oracle,
preservation, source-structure, runtime-state, and bounded-absence obligations
were satisfied by the typed records retained with the packet. The verdict does
not rely on a doctrine-backed conclusion.

## Residual failures and next authority

The residual technical failures are:

1. the installed controller cannot begin the ADR 0025 lifecycle while the
   prior P7 campaign state exists;
2. aggregate disablement cannot convert that state to its required disabled
   phase because the retained prior Garage key identity is already absent; and
3. the current live P7 recomputation and historical match were not exercised.

The exact one-attempt P13 authority is consumed by this stopped campaign. ADR
0025 grants no repair, state rewrite, controller change, or retry. P14 cannot
accept CAPLAB v0 under the current plan because technical verification failed
and the required export criterion is unmet. Any repair or repeat verification
requires a new owner decision and exact authorization.
