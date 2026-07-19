# CAPLAB-39 repository migration record

## Scope and authority

**Decision:** ADR 0019 selects `halbritt/caplab` and
`/home/halbritt/git/caplab` as the canonical repository identities.

**Authorization:** the repository owner's direct 2026-07-19 instruction and
Plane work item CAPLAB-39 authorize history-preserving consolidation, GitHub
rename, local path migration, active-reference updates, verification, commit,
and push. Destructive removal of the former checkout remains outside the
executed effects; an exact recovery path is retained.

## Pre-migration observations

- Standalone CAPLAB was clean at
  `49aabe939270a29de3d98c731c4f37e72a512a7e`, with 36 commits, one branch,
  no tags, and no remote.
- The published checkout was at
  `16f9d7a0766281d1a0264ca5d335f3049fbf557b`, with 111 commits, seven local
  branches beyond `main`, no tags or releases, and one merged pull request.
- The two histories had unrelated roots and neither HEAD was available in the
  other object database.
- The former checkout held 511 MiB of untracked `.book-work/` content and a
  6.3 MiB untracked `doctrine/bin/` artifact.
- Several long-running Codex sessions, shells, Plane transports, and one
  already-running historical adjudication process had the former checkout's
  directory inode as their working directory. No systemd unit, container, cron
  entry, or symlink resolved through the Ethogram name.
- CAPLAB's baseline gate passed 102 tests with four authorized live skips.
  The former repository's hermetic gate passed 93 tests.

## Preservation and execution

Two complete bundles were created and verified before repository mutation:

| Repository state | Bundle | SHA-256 |
|---|---|---|
| Standalone CAPLAB | `/var/tmp/caplab-39-caplab-before-2026-07-19.bundle` | `05a7b7c045f7936b0adafb6d0a575da2ffdcbb24fe0fb736aa5601d55a04f80a` |
| Former Ethogram | `/var/tmp/caplab-39-ethogram-before-2026-07-19.bundle` | `d38aef315e534405a000b7b4b27cbba51cdb40cef9ff1239a0618d438cc44769` |

The canonical-identity decision and root metadata were committed as
`f3cbb3367e224b44c506e3cbdf55e8247db4f7a7`. The former tracked tree was
imported at `history/ethogram/` by consolidation commit
`32273ebd164c925a5c2860fe60b91513fcdb60aa`, whose parents are the CAPLAB
decision commit and former `main` tip
`16f9d7a0766281d1a0264ca5d335f3049fbf557b`.

The following former branch tips were preserved exactly:

| Branch | Tip |
|---|---|
| `agent/books-backlog-drain` | `f860157b5485ae4fafb4fcc4a298b5a668b952d6` |
| `agent/caplab-runtime-decision` | `cdbb5120d1d450763fca2a8aca172f6308413440` |
| `agent/evidence-governed-doctrine-remediation` | `b4434076d9034a724cac049f1cab9c0f15ba58c1` |
| `agent/luna-bv-confirmation` | `dbe6f7e8b988823c754ad232c74ad414119a3375` |
| `agent/luna-literal-calibration` | `ea606cae3860d10658b0a7f4b575ed805541d507` |
| `agent/native-codex-seam` | `9d352eb37ab342f331fca1609c8220cc906d74bd` |
| `frontier-checkout-screen` | `d95d37bf1817d2df2bfc4c89d843004445b025af` |

GitHub repository object `1296585434` was renamed from
`halbritt/ethogram` to `halbritt/caplab`. Both the canonical and former GitHub
slugs resolve to the canonical name after the rename.

The former local checkout was atomically moved to
`/home/halbritt/git/ethogram-recovery-2026-07-19`, preserving its Git metadata
and both untracked paths. Its fetch remote names canonical CAPLAB and its push
URL is disabled. `/home/halbritt/git/ethogram` is now a compatibility symlink
to `/home/halbritt/git/caplab`. Processes that already held the former
directory open retained that inode through the rename and now resolve to the
recovery path. No process was terminated.

## Doctrine receipt

The migration decision used Pincite packet `pkt-36813c30aaddd50c`, content
SHA-256 `36813c30aaddd50c09c6a41a4b53033010e7a2e356f318a6acad59a83faa69d9`,
corpus `corpus-2026-07-12-d2ea7b94a1ce`, doctrine
`doctrine-a90ee3f1cf7b6f26`, and retriever
`retriever-1392f38f05a41086` from release commit
`95ddd1c408348f2079180476fb188262cfe43985`.

The packet's authority ceiling was recommendation; execution authority came
from the owner and CAPLAB-39. Its sole unmet obligation was “telemetry where
available,” classified nonmaterial because no repository-consumer telemetry
exists and direct process, path, unit, container, cron, remote, and source
inventories covered the migration boundary.

## Verification criteria

Verification requires the following post-push observations:

- both original histories are ancestors of canonical `main`;
- all preserved branch tips resolve locally and on GitHub;
- root `make check` passes;
- `make test` passes from `history/ethogram/`;
- the GitHub repository ID, canonical slug, former-slug redirect, description,
  default branch, and visibility match ADR 0019;
- active source and fleet references use CAPLAB, while historical uses of
  “Ethogram” remain scoped to history and this migration record;
- the recovery checkout and both bundle objects remain readable; and
- canonical `main` is clean and synchronized with `origin/main`.

Passing verification is not owner acceptance and does not authorize P7, P8,
P10, model calls, evidence export, or training.

## CI correction

The first canonical GitHub Actions run, `29702961943`, failed before the suite
because the clean runner did not have `botocore`; the initial workflow invoked
`make check` without installing CAPLAB's dependency lock. A regression contract
now requires the workflow to install
`src/caplab/runtime/requirements.lock` with `--require-hashes` before the gate.
The local gate passed 104 tests with four authorized live skips after this
correction. Final verification still requires the corrected GitHub Actions run
to pass.
