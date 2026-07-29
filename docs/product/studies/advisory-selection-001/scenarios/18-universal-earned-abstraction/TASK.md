# JSONL report: dashboard shows zero hours for every project

Since we pointed the finance dashboard at the JSONL report feed, every
project's total reads 0. The importer treats `hours` as text and sums
nothing. The CSV report still opens fine in a spreadsheet.

Reproduce:

    python3 -m worklog report --input sample/worklog.jsonl --format jsonl

Expected lines like `{"project": "acme", "hours": 9.25, "entries": 3,
"last_day": "2026-07-21"}` — numbers as numbers. Actual: `"hours": "9.25"`
and `"entries": "3"`, every value quoted as text. Also, the line for the
one project whose name contains a quote character gets rejected by the
importer as malformed. Please fix the JSONL report output.
