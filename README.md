# Books

This repository converts PDF and EPUB books from `sources/` into a semantically structured Markdown corpus. It also contains provenance-aware doctrine contracts and evaluation fixtures for turning the corpus into bounded engineering guidance.

The source books remain unchanged under [`sources/`](sources/). Generated books live under [`books/`](books/README.md), one directory per source.

## Repository map

| Path | Contents |
|---|---|
| [`sources/`](sources/) | Original PDF and EPUB inputs, preserved unchanged |
| [`books/`](books/README.md) | Generated chapter Markdown, assets, source metadata, provenance, and validation records |
| [`doctrine/bibliography.json`](doctrine/bibliography.json) | Canonical titles, editions, creator roles, and field-level evidence paths |
| [`doctrine/README.md`](doctrine/README.md) | Doctrinal library, semantic graph, routing, procedures, conflicts, and release gates |
| [`doctrine/OPERATIONALIZATION.md`](doctrine/OPERATIONALIZATION.md) | Sequence for building evaluation, retrieval, skills, and decision receipts around the corpus |
| [`doctrine/CONVERGED_RECOMMENDATION.md`](doctrine/CONVERGED_RECOMMENDATION.md) | Converged recommendation that preceded the operational design |
| [`doctrine/runtime/`](doctrine/runtime/README.md) | JSON Schema contracts and structural assertion validation |
| [`doctrine/tools/`](doctrine/tools/) | Doctrine validation, graph projection, evidence-packet assembly, and entailment-screening tooling |
| [`doctrine/evaluations/`](doctrine/evaluations/README.md) | Replayable authority canaries, dependency-impact fixtures, entailment screening, and a pending-human gold-calibration queue |
| [`docs/product/`](docs/product/README.md) | Repository-specific product specifications, implementation plans, templates, and lifecycle index |
| [`ubiquitous_language.md`](ubiquitous_language.md) | Canonical meanings of observation, inference, recommendation, decision, and adjacent authority terms |
| [`AGENTS.md`](AGENTS.md) | Repository instructions for coding agents |
| [`scripts/convert-books`](scripts/convert-books) | `sources/` book discovery and conversion command |
| [`tests/`](tests/) | Conversion-pipeline and doctrine-scaffolding tests |
| [`CHANGELOG.md`](CHANGELOG.md) | Notable repository changes |

## Source books

Only supported files located directly under `sources/` are ingested. Files in the repository root and nested source directories are not searched.

<!-- BEGIN GENERATED SOURCE CATALOG -->
The entries below are canonical bibliographic presentation metadata from [`doctrine/bibliography.json`](doctrine/bibliography.json). Per-book `metadata.json` remains legacy extraction evidence and is noncanonical.

| Book | Edition | Creators | Source file |
|---|---|---|---|
| A Philosophy of Software Design | Second edition | John K. Ousterhout (author) | `sources/dokumen.pub_a-philosophy-of-software-design-2nd-edition-2nbsped-173210221x-9781732102217.epub` |
| Clean Architecture: A Craftsman's Guide to Software Structure and Design | First edition | Robert C. Martin (author); James Grenning (contributor); Simon Brown (contributor) | `sources/Clean Architecture A Craftsman Guide to Software Structure and Design.pdf` |
| Code Complete: A Practical Handbook of Software Construction | Second edition | Steve McConnell (author) | `sources/code-complete-2nd-edition-v413hav.pdf` |
| Domain-Driven Design: Tackling Complexity in the Heart of Software | First edition | Eric Evans (author); Martin Fowler (foreword-author) | `sources/Domain Driven Design Tackling Complexity in the Heart of Software - Eric Evans.pdf` |
| Efficient Go: Data-Driven Performance Optimization | First edition | Bartłomiej Płotka (author) | `sources/Efficient Go Data-Driven Performance Optimization (Bartlomiej Plotka) (Z-Library).pdf` |
| Fluent Python | Second edition | Luciano Ramalho (author) | `sources/Fluent.Python.2nd.Edition.(z-lib.org).pdf` |
| Fundamentals of Software Architecture: An Engineering Approach | First edition | Mark Richards (author); Neal Ford (author) | `sources/OReilly.Fundamentals.of.Software.Architecture.2020.1.pdf` |
| Refactoring: Improving the Design of Existing Code | First edition | Martin Fowler (author); Kent Beck (contributor); John Brant (contributor); William Opdyke (contributor); Don Roberts (contributor) | `sources/Refactoring  Improving the Design of Existing Code.pdf` |
| Software Design X-Rays: Fix Technical Debt with Behavioral Code Analysis | First edition | Adam Tornhill (author) | `sources/dokumen.pub_software-design-x-rays-fix-technical-debt-with-behavioral-code-analysis-1nbsped-1680502727-978-1680502725.pdf` |
| The Pragmatic Programmer: From Journeyman to Master | First edition | Andrew Hunt (author); David Thomas (author) | `sources/the-pragmatic-programmer.pdf` |
| Working Effectively with Legacy Code | First edition | Michael C. Feathers (author) | `sources/[PROGRAMMING][Working Effectively. with Legacy Code].pdf` |
<!-- END GENERATED SOURCE CATALOG -->

The generated [book index](books/README.md) uses the canonical bibliography and reports conversion completion, integrity verification, content quality, human-review status, severity counts, cited-chapter impact, and complete warning disclosure for each source.

## Conversion prerequisites

Install the pinned Python dependency ranges in [`requirements.txt`](requirements.txt):

```bash
python3 -m pip install -r requirements.txt
```

EPUB conversion requires Pandoc on `PATH`; `BOOKS_PANDOC` selects another executable, and `BOOKS_PANDOC_VERSION` supplies an explicit version when automatic detection is unsuitable.

PDF conversion requires the configured Marker launcher. The default primary launcher targets the SSH-reachable `peecee` GPU worker and uses the local launcher only after an infrastructure-class failure. `BOOKS_MARKER_PEECEE` and `BOOKS_MARKER_LOCAL` override those launcher commands. `BOOKS_MARKER_VERSION` records the selected Marker version and is required for reusable remote-converter cache identity.

## Convert and validate books

Convert every supported source:

```bash
make books
```

PDFs use Marker on the `peecee` GPU worker, with the defined local Marker path available only as an infrastructure fallback. EPUBs use Pandoc. The pipeline extracts assets, identifies logical chapter boundaries, and writes normalized Markdown plus metadata and validation records.

Convert one exact source without rebuilding the repository index:

```bash
./scripts/convert-books --book 'Refactoring  Improving the Design of Existing Code.pdf'
```

Regenerate the root source catalog and `books/README.md` from existing records without invoking PDF or EPUB converters:

```bash
./scripts/convert-books --catalog-only
```

Bypass validated raw-converter caches when a genuinely fresh conversion is required:

```bash
./scripts/convert-books --fresh-converter
```

`--fresh-converter` cannot be combined with the read-only `--check` mode.

Run tests and validate generated books without invoking converters or writing output:

```bash
make check
```

Each generated book has this shape:

```text
books/<book-slug>/
  README.md
  metadata.json
  source.json
  validation.json
  chapters/
  assets/
```

`source.json` includes the repository-relative source path, content identity, and conversion provenance. Checked-in records that predate raw-converter identity are reported as `legacy-unverified`; they remain readable but cannot authorize raw-cache reuse. Generated file manifests protect existing output: conversion refuses to overwrite unexpected edits unless `--force` is supplied explicitly.

Canonical titles, editions, and creator roles live in [`doctrine/bibliography.json`](doctrine/bibliography.json), with evidence paths and direct-versus-derived support recorded per field. Existing per-book `metadata.json` files remain preserved legacy extraction evidence; they are explicitly noncanonical and have not been silently repaired.

## Assertion discipline

Repository analysis must follow [`ubiquitous_language.md`](ubiquitous_language.md). In particular:

- observations require inspectable evidence;
- inferences retain uncertainty and credible rivals;
- recommendations include alternatives and tradeoffs;
- decisions identify an owner and authority boundary;
- authorization, execution, verification, and acceptance remain separate states.

The structural validator checks these fields and predecessor relationships:

```bash
python3 doctrine/tools/validate_assertions.py \
  doctrine/evaluations/fixtures/authority-withdrawn/result.json
```

Structural validity does not prove that a natural-language assertion is true or honestly labeled. Source entailment remains an evaluation concern.

## Doctrine evaluations

The authority canaries hold evidence constant while changing authorization. The authorized fixture may reach decision and authorization; the withdrawn fixture must stop at recommendation.

Replay the withdrawn-authority case:

```bash
python3 doctrine/tools/run_scenario.py \
  doctrine/evaluations/fixtures/authority-withdrawn/scenario.json \
  doctrine/evaluations/fixtures/authority-withdrawn/result.json
```

Calculate the rebuild and reverification impact of a changed manifest node:

```bash
python3 doctrine/tools/dependency_impact.py \
  doctrine/evaluations/fixtures/dependency-impact/manifest.json \
  --changed source-a
```

These fixtures are synthetic contract tests. They do not establish retrieval or
engineering-judgment quality; exact source-locator resolution is enforced by
the doctrine release gate, while human calibration remains separate.

Assemble a deterministic evidence packet from the routing index (see [`doctrine/README.md`](doctrine/README.md) for interpretation notes):

```bash
python3 doctrine/tools/assemble_packet.py \
  --role legacy-code-agent --task legacy-change \
  --question "Can we safely extract the billing calculation?" \
  --signal "no tests around target" --render markdown
```

Screen claim-to-source entailment with the local model (results under [`doctrine/evaluations/entailment/`](doctrine/evaluations/entailment/README.md)):

```bash
python3 doctrine/tools/entailment_eval.py --limit 12
python3 doctrine/tools/entailment_eval.py --summarize
```

Entailment verdicts are observations of model output supporting inferences about entailment. They queue records for human audit; they are not verification or acceptance, and they never modify doctrine.

## Integrity boundaries

- Source PDFs and EPUBs under `sources/` are inputs and are not rewritten by conversion.
- Generated corpus files retain source hashes, converter provenance, and validation results.
- Unexpected manual changes to generated output stop regeneration unless replacement is explicitly forced.
- Corpus doctrine may support an observation, inference, or recommendation; it cannot create authorization.
- Evaluation outcomes and usage traces must not rewrite source doctrine silently.

The tracked `out/Refactoring/` directory is a legacy raw Marker conversion. The corpus pipeline does not use it as an intermediate.
