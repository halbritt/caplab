# vouchercore

Gift-voucher backend for the shop: issue prepaid voucher codes, redeem
against them at checkout, and give finance the numbers they reconcile
month-end against.

## Layout

- `vouchercore/money.py` — monetary amounts
- `vouchercore/voucher.py` — the voucher itself and its state changes
- `vouchercore/factory.py` — voucher assembly and code generation
- `vouchercore/store.py` — SQLite persistence plus the append-only audit log
- `vouchercore/ledger.py` — finance/support reports (read-only)
- `vouchercore/service.py` — the operations the shop calls

## Running tests

From this directory:

    python3 -m pytest -q
