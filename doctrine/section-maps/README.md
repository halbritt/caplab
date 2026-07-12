# Per-book section maps

One tracked YAML file per source book (`<book-slug>.yaml`, schema
`section-map/1`) classifying every ATX heading in every converted chapter as
either a genuine **`section`** boundary or **`embedded`** content.

The corpus conversion flattened many books' heading hierarchies: callout boxes
(WARNING/TIP/NOTE), example/figure/table captions, definition-list items, and
subsection children became sibling ATX headings of the genuine sections.
Section extraction that stops at the next same-or-higher-level heading
therefore truncates cited sections. These maps are the recorded judgment layer
that lets extraction distinguish a real section boundary from flattened
embedded content, without ever rewriting the provenance-stable chapter files.

## Schema

```yaml
schema_version: section-map/1
book: <book-slug>
chapters:
  - path: books/<slug>/chapters/<file>.md   # repo-relative
    chapter_sha256: <sha256 of the chapter file bytes>
    headings:
      - line: <1-based line number of the ATX heading>
        level: <1-6>                        # number of leading '#'
        text: <exact heading text after the hashes, stripped>
        role: section | embedded
        classified_by: rule:<rule-name> | model | human
        note: <optional short string>
```

`embedded` means the heading's content belongs to the enclosing section;
`section` means the heading starts a new logical unit of the chapter.

## Epistemics of `classified_by`

Following [ubiquitous_language.md](../../ubiquitous_language.md), the three
provenance classes make different kinds of claims and must not be conflated:

- **`rule:<name>`** entries are **observations** of deterministic pattern
  matches against the chapter bytes recorded in `chapter_sha256`. The rule
  ladder, in priority order: `rule:chapter-title` (first heading of a
  chapter), `rule:callout` (WARNING/TIP/NOTE/CAUTION/IMPORTANT/SIDEBAR/KEY
  POINT/CHECKLIST/cc2e.com keywords), `rule:caption`
  (`Example|Figure|Table|Listing N-N` patterns), `rule:numbered-book`
  (books with ≥50 `N.N `-prefixed headings: numbered headings are sections,
  unnumbered headings at the book's flat dominant level are embedded),
  `rule:toc` (heading appears in the book's converted table-of-contents
  chapter), and `rule:cited` (heading is cited by a doctrine concept
  locator). Cited headings are ground truth sections: `rule:cited` overrides
  an embedded classification from an earlier rule and records the override in
  `note`.
- **`model`** entries are **model classifications** of the headings the rules
  could not decide (one local-model request per chapter, with the heading list
  and nearby text as context). They are screening evidence subject to the
  release-gate oracle, not verification and not acceptance. When a model
  response cannot be parsed, the affected headings default to `role: section`
  with `note: unparseable-default-section` — the safe direction, because it
  can only under-extend a section, never wrongly swallow a sibling section.
- **`human`** entries are **authoritative judgments**. `--write` preserves
  them verbatim: it never reclassifies or drops them, even when the chapter
  hash changes (entries whose heading text disappears from a rewritten chapter
  are kept and surfaced by `--check` for human resolution).

## Rebuild and check

```bash
python3 doctrine/tools/build_section_map.py --write               # all books
python3 doctrine/tools/build_section_map.py --write --book <slug> # one book
python3 doctrine/tools/build_section_map.py --check               # verify
python3 doctrine/tools/build_section_map.py --stats               # counts
```

`--write` recomputes rule classifications, reuses existing model entries for
chapters whose `chapter_sha256` is unchanged (so repeated `--write` is
byte-stable and makes no model calls when inputs are unchanged), rebuilds the
non-human entries of any chapter whose hash changed, and writes atomically.
Model classification uses the local OpenAI-compatible server
(`http://localhost:8081/v1` by default; override with `--endpoint`).

`--check` is model-free and fails listing problems: a book or chapter without
map coverage, a stale `chapter_sha256`, any heading present in a chapter file
but absent from the map (or vice versa), and any cited-locator heading whose
role is not `section`.

## Overriding a heading

Edit the heading's entry in the book's map file: set `role` to the correct
value, set `classified_by: human`, and optionally record a short `note` with
the evidence reviewed. Subsequent `--write` runs preserve the entry; `--check`
still enforces that cited headings are sections, so a human override cannot
silently demote a heading that doctrine cites.
