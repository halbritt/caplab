# Reference repair (one possible doctrine-following solution)

The import pipeline has two places where a failure is converted into a
success-shaped value, and the repair treats them differently because they mean
different things to the operator.

**Unreadable files stop pretending to be empty.** In `reader.py`, `read_rows`
currently catches `(OSError, UnicodeDecodeError)` and returns `[]`, which is
indistinguishable from a legitimately empty export. The repair deletes that
handler. A file the run cannot open or decode raises — either the original
exception or a small wrapper such as `ExportReadError(path)` chained with
`raise ... from exc` so the underlying cause survives. Nothing between
`read_rows` and the CLI catches it, so a night with an unreadable export ends
with the failing file named and a nonzero exit instead of the success line.
(Whether the run aborts on the first bad file or collects per-file failures and
fails at the end is a judgment call; either is acceptable, provided the run
cannot end in plain success.)

**Junk rows stay skippable, but the skip keeps its meaning.** Footer totals and
repeated headers really are non-transactions, so skip-and-continue is the right
semantics for them — the sin in `records.py` is the blanket
`except Exception: return None`, which also eats programming errors and strips
every skip of its reason. The repair narrows translation failures to the errors
that actually mean "this row is not a transaction" (missing/blank fields,
unparseable date or amount — `KeyError`/`ValueError`) and raises a dedicated
`MalformedRow` error carrying the reason, chained from the original exception.
Any other exception propagates untouched. `importer.run_import` catches only
`MalformedRow`, appends `(file, line number, reason)` to a run summary, and
continues with the next row.

**The batch boundary reports what it dropped.** `run_import` returns a small
summary object — files seen, transactions imported, and the list of skipped
rows with their causes — instead of the bare `(files, imported)` tuple. The CLI
keeps printing `Imported N transactions from M files` for a clean run (the
existing CLI test pins this), and after it prints one line per skipped row
naming file, line, and reason, so a lossy run is visibly different from a
clean one.

All existing tests pass unchanged: valid rows still import, a footer row still
does not block real rows, and a clean CLI run still prints the same summary
line and exits 0. No test is modified, deleted, or added under `tests/`.
