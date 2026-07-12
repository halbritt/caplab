# HowTo: add a source book

Adding a book has two independent phases. **Phase 1 (corpus)** converts the
file into chaptered Markdown with provenance and takes minutes of attention.
**Phase 2 (doctrine)** registers the book as a doctrine source and extracts
concept support from it — that is an extraction campaign, not a checklist
step, and most books stop after Phase 1 until someone runs one.

## Phase 1 — convert into the corpus

### 1. Put the file in `sources/`

Drop the `.pdf` or `.epub` directly under `sources/` — discovery is
non-recursive and only those two suffixes are ingested; files in the
repository root or nested directories are ignored. The filename becomes part
of the book's slug, so a sane name helps, but originals are preserved
unchanged either way (they are inputs and are never rewritten).

### 2. Prerequisites

```bash
python3 -m pip install -r requirements.txt
```

- **EPUBs** need Pandoc on `PATH` (`BOOKS_PANDOC` overrides the executable).
- **PDFs** use Marker on the `peecee` GPU worker over SSH, falling back to the
  local Marker launcher only on infrastructure failure (`BOOKS_MARKER_PEECEE`
  / `BOOKS_MARKER_LOCAL` override the launchers). Set `BOOKS_MARKER_VERSION`
  — it is required for reusable remote-converter cache identity.

### 3. Convert

```bash
# One book, by exact source filename (does not rebuild the repo index):
./scripts/convert-books --book 'My New Book.pdf'

# Or everything not yet converted:
make books
```

Output lands in `books/<slug>/` — `chapters/`, `assets/`, `source.json`
(conversion provenance), `metadata.json` (extraction evidence, noncanonical),
`validation.json`, and a per-book README. Conversion refuses to overwrite
unexpected manual edits unless `--force` is given; `--fresh-converter`
bypasses validated raw-converter caches when you need a genuinely fresh run.

### 4. Review the validation record

Read `books/<slug>/validation.json` (or the warnings in the book README).
Table damage, duplicate headings, and low-confidence chapter boundaries are
recorded, not fatal — but know what you ingested before anything cites it.

### 5. Add canonical bibliography metadata

`doctrine/bibliography.json` is the canonical source of titles, editions, and
creator roles (roles: author, contributor, editor, translator,
foreword-author), each field with an evidence path. Add an entry for the new
book; without one its catalog rows fall back to extraction metadata and are
explicitly marked noncanonical. Then regenerate the catalogs:

```bash
./scripts/convert-books --catalog-only
```

### 6. Build the section map

Every book with a `chapters/` directory must have a tracked section map
(`doctrine/section-maps/<slug>.yaml`) classifying each heading as a genuine
section boundary or conversion-flattened embedded content — the release gate
fails without it. The builder needs the local llama server
(`http://localhost:8081/v1`) for headings its rules can't decide:

```bash
python3 doctrine/tools/build_section_map.py --write --book <slug>
python3 doctrine/tools/build_section_map.py --check
```

Spot-check the generated map (see `doctrine/section-maps/README.md` for the
epistemics and how to pin or human-override a heading).

### 7. Run the gate and commit

```bash
make check
```

Commit the source file, the generated `books/<slug>/` tree, the bibliography
entry, the regenerated catalogs, and the section map together. Source
binaries are large; that is expected — this repository stays private and
tracks them deliberately.

## Phase 2 — register as a doctrine source (optional, later)

Only needed when the book should back doctrine concepts:

1. Register a `SRC-*` entry in `doctrine/sources.yaml` (id, title, authors,
   corpus path, source sha256, chapter count, source roles). Traceability
   coverage totals derive from this registry, so registration obligates full
   chapter coverage.
2. Add the source's contributions to `doctrine/corpus-map.yaml` and record an
   extraction ledger under `doctrine/_work/extractions/`.
3. Extract: concept `source_support` entries (exact chapter-heading locators),
   graph formulations via `sync_concepts_to_graph.py --write`, routing via
   `build_routing_index.py`, and `traceability.yaml` updates.
4. Re-run the doctrine gates: `validate_doctrine.py`,
   `build_gold_queue.py --write && --check`, `make check`.
5. Screen the new citations:
   `python3 doctrine/tools/entailment_eval.py --source SRC-<ID> ...`
   (see `doctrine/evaluations/entailment/README.md`), then audit any flags in
   the adjudication bench at http://100.85.100.81:8788/.

This phase is where the real cost lives — the original 11-book extraction was
a multi-agent campaign. Treat it as its own project with its own review.

## Troubleshooting

- **peecee unreachable:** conversion falls back to the local Marker launcher
  and records `fallbacks_used` in `source.json`; slower but equivalent.
- **"refusing to overwrite" on reconversion:** the generated tree has manual
  edits; inspect them, then rerun with `--force` if replacement is intended.
- **Section-map `--check` staleness after editing a chapter:** rerun
  `build_section_map.py --write` — human/pinned heading entries survive the
  rebuild; rule and model entries are recomputed.
