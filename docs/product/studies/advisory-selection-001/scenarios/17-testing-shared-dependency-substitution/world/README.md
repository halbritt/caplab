# ledgerlib

A small posting ledger: accounts, categorised postings, monthly statements,
and read-side reports. SQLite persistence, no third-party runtime
dependencies.

## Layout

- `ledgerlib/models.py` — value objects (`Money`, `Account`, `Posting`, `Statement`)
- `ledgerlib/store.py` — SQLite persistence (`SqliteStore`)
- `ledgerlib/policy.py` — category validation/normalisation (`CategoryRules`)
- `ledgerlib/ledger.py` — posting workflow (`Ledger`)
- `ledgerlib/reports.py` — read-side summaries (`ReportBuilder`)
- `ledgerlib/testing.py` — pytest fixtures for this suite and downstream users
- `tests/` — the test suite

## Running the tests

```
python3 -m pytest -q
```
