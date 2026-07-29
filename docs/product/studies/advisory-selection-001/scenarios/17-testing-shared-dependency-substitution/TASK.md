# Suite gives different answers depending on how you invoke it

The ledgerlib suite is green on CI and on a fresh checkout. But while working
on the report builder I ran the two files I had open,

    python3 -m pytest tests/test_reports.py tests/test_ledger.py

and `test_march_statement_lists_every_posting` failed, reporting 5 statement
lines where it expected 3. The full suite passes. That two-file command fails
every time. Priya hit something similar last sprint: her new test file made
untouched tests fail, so she reverted it.

Expected: a test passes or fails the same way no matter which other files run
alongside it. Actual: the outcome depends on the invocation. The library
itself behaves fine in production.
