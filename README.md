# Historical agent-judgment studies

This repository preserves the source studies, evaluation instruments,
adjudication records, checked-in aggregates, and reviewer-facing projections
from the former Books workspace. Its final repository name is pending an owner
choice.

Two products that began here now have separate authority:

- Pincite owns the engineering-doctrine corpus and retrieval runtime in
  [`halbritt/pincite`](https://github.com/halbritt/pincite). This repository
  consumes it through the exact dependency recorded in
  [`pincite-dependency.json`](pincite-dependency.json).
- The standalone `/home/halbritt/git/caplab` repository owns current CAPLAB
  product and runtime development. The CAPLAB material retained here records
  source-study history and evidence custody; it is not the current CAPLAB
  product authority.

## Repository map

| Path | Contents |
|---|---|
| [`caplab/`](caplab/) | Historical study tooling, Pincite dependency verification, and the preserved Study 001 dashboard |
| [`docs/product/`](docs/product/README.md) | Source product specifications, plans, and capability cards retained for provenance |
| [`docs/agent-judgment/`](docs/agent-judgment/README.md) | Evaluation operation and extension guidance |
| [`doctrine/evaluations/`](doctrine/evaluations/README.md) | Evaluation contracts, fixtures, adjudication records, and preserved experiment reports |
| [`doctrine/tools/`](doctrine/tools/) | Historical evaluation, projection, replay, and adjudication tools |
| [`docs/decisions/`](docs/decisions/README.md) | Architecture decisions and their authority boundaries |
| [`docs/domain/`](docs/domain/README.md) | Historical study domain language and current context map |
| [`tests/`](tests/) | Hermetic repository tests and pinned-Pincite integration checks |
| [`ubiquitous_language.md`](ubiquitous_language.md) | Canonical assertion, evaluation, and decision vocabulary |

The retained `doctrine/evaluations/` path is a stable historical artifact
namespace, not a claim that this repository owns Pincite doctrine or current
CAPLAB product development. Sealed Harbor records may also retain old `books`
repository paths. Those bytes are experiment provenance and are not live
repository configuration.

## Pincite dependency

The default validated release location is:

```text
~/.local/share/pincite/release
```

Override it with `PINCITE_RELEASE_HOME`. Repository tooling fails closed unless
that checkout is at the exact pinned commit and its Pincite retrieval-state
gate reports the expected corpus and doctrine identities:

```bash
make pincite-check
```

The dependency manifest pins the repository, release tag, commit, corpus ID,
and doctrine ID. Updating it is an explicit compatibility decision, not an
incidental consequence of a newer Pincite checkout.

## Checks

Install the small Python dependency set:

```bash
python3 -m pip install -r requirements.txt
```

Run the hermetic repository suite:

```bash
make test
```

Run the complete local gate against the pinned Pincite release:

```bash
make check
```

GitHub Actions runs the hermetic suite. The full integration gate is local
because the Pincite repository and release checkout are private dependencies.

## Evaluation and dashboard entrypoints

Start with [`docs/agent-judgment/README.md`](docs/agent-judgment/README.md) for
the behavioral evaluation harness and
[`caplab/dashboard/README.md`](caplab/dashboard/README.md) for the Study 001
review dashboard.

Machine screening, mechanical grading, and deterministic projections are
observations of instrument output. They are not human adjudication,
verification, acceptance, or authority to promote a broader capability claim.

## Assertion discipline

Repository analysis follows [`ubiquitous_language.md`](ubiquitous_language.md):

- observations retain inspectable evidence and provenance;
- inferences state uncertainty and credible rivals;
- recommendations remain distinct from decisions;
- decisions name an owner and authority source; and
- authorization, execution, verification, and acceptance remain separate.
