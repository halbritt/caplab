# quoteflow

Shipping quote calculator for the two parcel services we resell (standard
road and express air). The sales desk uses the CLI; the nightly invoicing
job imports the package directly.

## Usage

```bash
python -m quoteflow.cli express 10 --postcode 0872 --promo SAVE15
python -m quoteflow.cli standard 2 --postcode 3000 --dims 40x30x20
```

## Layout

- `quoteflow/standard.py`, `quoteflow/express.py` — one quoting module per service
- `quoteflow/tariffs.py` — 2025 rate card constants
- `quoteflow/surcharges.py` — remote-area and oversize fees
- `quoteflow/promo.py` — promotional code table
- `docs/pricing-rules.md` — the business rules every total must follow;
  finance audits quotes against this document

## Tests

```bash
python -m pytest -q
```
