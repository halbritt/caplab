from datetime import date

from ledgerline.records import Transaction
from ledgerline.store import LedgerStore


def test_roundtrip(tmp_path):
    store = LedgerStore(tmp_path / "ledger.db")
    try:
        store.add(
            Transaction(
                posted=date(2026, 3, 14),
                account="coastal-checking",
                amount_cents=4250,
                memo="coffee",
            )
        )
        store.add(
            Transaction(
                posted=date(2026, 3, 15),
                account="harbor-savings",
                amount_cents=100000,
                memo="transfer",
            )
        )
        assert store.count() == 2
        coastal = store.transactions_for("coastal-checking")
        assert len(coastal) == 1
        assert coastal[0].amount_cents == 4250
        assert coastal[0].memo == "coffee"
    finally:
        store.close()
