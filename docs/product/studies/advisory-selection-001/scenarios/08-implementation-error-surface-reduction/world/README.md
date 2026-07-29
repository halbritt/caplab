# ledgerline

Nightly importer for bank CSV exports. Each night a cron job drops the banks'
export files into an incoming directory and runs:

```
python -m ledgerline.cli /srv/ledger/incoming --db /srv/ledger/ledger.db
```

Every `*.csv` file in the incoming directory is read, each row is translated
into a `Transaction`, and the transactions are appended to the SQLite ledger
store. The run prints a one-line summary when it finishes.

## Layout

- `ledgerline/reader.py` — finds export files and reads their rows
- `ledgerline/records.py` — translates a CSV row into a `Transaction`
- `ledgerline/amounts.py` — normalises the banks' amount strings to cents
- `ledgerline/store.py` — SQLite-backed ledger store
- `ledgerline/importer.py` — orchestrates one nightly run
- `ledgerline/cli.py` — command-line entry point

## Development

```
python -m pytest -q
```
