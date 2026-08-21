"""Deterministic re-runnable check for control qs-d24d0d472c7a9316: does the
evidence table in finding-2026-08-16-calibration-not-measurement-equivalent.md
contradict the document's stated sample of 11 cases (8 misses, 3 catches)?

Reviewers refused this control 8 of 12 times on exactly that allegation. The
allegation is arithmetic about the pinned document against the validation
file the document reports on, so it is checkable without judgment:

- Parse the table's Calibration-harness column (caught/total per class).
- Load advisory/calibration/strong-reference-gemini-3-7-flash-high-20260816.jsonl,
  the run the document reports.
- The allegation is TRUE (control defective) only if a table figure misstates
  the file, or the narrative's 11/8/3 misstates the file.
- If every table row matches the file's per-class counts AND the narrative
  totals match the file's totals, the table is a consistent subset (the file
  spans 9 classes; the table shows the 6 with same-day real-path
  comparisons) and the document contradicts nothing.

Exit 0 = control is SOUND (no figure misstates the file).
Exit 1 = control is DEFECTIVE (a figure misstates the file).
Exit 2 = check could not run.
"""
import json
import os
import re
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", ".."))
PIN = "c4c8e2417e12d971b7d05220a24f7577c2bf454c"
DOC = "docs/records/finding-2026-08-16-calibration-not-measurement-equivalent.md"
VALIDATION = os.path.join(
    REPO, "advisory", "calibration",
    "strong-reference-gemini-3-7-flash-high-20260816.jsonl")

CATCH_FLAGS = {"validated-hard", "validated-hard-weak-evidence"}

body = subprocess.run(["git", "-C", REPO, "show", f"{PIN}:{DOC}"],
                      capture_output=True, text=True)
if body.returncode != 0:
    print("cannot read pinned document:", body.stderr.strip())
    sys.exit(2)

# Table rows: | `class` | n/n caught | c/t |
table = {}
for m in re.finditer(r"\|\s*`(\w+)`\s*\|[^|]*\|\s*(\d+)/(\d+)\s*\|",
                     body.stdout):
    table[m.group(1)] = (int(m.group(2)), int(m.group(3)))
if len(table) != 6:
    print(f"expected 6 table rows, parsed {len(table)}: {sorted(table)}")
    sys.exit(2)

rows = [json.loads(l) for l in open(VALIDATION, encoding="utf-8") if l.strip()]
file_by_class = {}
for r in rows:
    op = r["case"]["operator"]
    caught, total = file_by_class.get(op, (0, 0))
    flag = str(r.get("difficulty_flag") or r.get("status") or "")
    file_by_class[op] = (caught + (flag in CATCH_FLAGS), total + 1)

results = {"table": table, "file_by_class": file_by_class}
mismatches = [f"{op}: table {table[op]} vs file {file_by_class.get(op)}"
              for op in table if table[op] != file_by_class.get(op)]
results["table_rows_matching_file"] = len(table) - len(mismatches)
results["table_mismatches"] = mismatches

file_total = sum(t for _, t in file_by_class.values())
file_catches = sum(c for c, _ in file_by_class.values())
narrative_11 = bool(re.search(r"11 `?pending-strong-reference`? cases",
                              body.stdout))
narrative_8_of_11 = bool(re.search(r"returned 8\s*\nof 11 as strong misses",
                                   body.stdout))
results["file_totals"] = {"cases": file_total, "catches": file_catches,
                          "misses": file_total - file_catches}
results["narrative_states_11_cases"] = narrative_11
results["narrative_states_8_misses"] = narrative_8_of_11
narrative_matches_file = (narrative_11 and narrative_8_of_11
                          and file_total == 11 and file_catches == 3)
results["narrative_matches_file"] = narrative_matches_file
results["table_is_subset_of_file"] = (
    not mismatches and len(file_by_class) > len(table))

print(json.dumps(results, indent=2, sort_keys=True))
defective = bool(mismatches) or not narrative_matches_file
print("VERDICT:", "control is DEFECTIVE (a figure misstates the file)"
      if defective else
      "control is SOUND: every table row and the narrative totals match the "
      "validation file; the table is a consistent 6-of-9-class subset, not a "
      "contradiction")
sys.exit(1 if defective else 0)
