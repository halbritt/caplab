from decimal import Decimal

import pytest

from vouchercore.errors import VoucherNotFound
from vouchercore.factory import VoucherFactory
from vouchercore.ledger import Ledger
from vouchercore.money import MoneyFactory
from vouchercore.store import VoucherStore
from vouchercore.voucher import VoucherStatus


@pytest.fixture
def store(tmp_path):
    s = VoucherStore(tmp_path / "vouchers.db")
    yield s
    s.close()


def test_round_trip_preserves_customer_facing_state(store):
    v = VoucherFactory().build(code="GV-TEST-0001", amount="75.00", currency="EUR")
    store.save(v)
    loaded = store.load("GV-TEST-0001")
    assert loaded.code == "GV-TEST-0001"
    assert loaded.balance.amount == Decimal("75.00")
    assert loaded.balance.currency == "EUR"
    assert loaded.status is VoucherStatus.ACTIVE


def test_load_unknown_code_raises(store):
    with pytest.raises(VoucherNotFound):
        store.load("GV-NOPE-0000")


def test_issue_writes_one_audit_entry(store, tmp_path):
    v = VoucherFactory().build(code="GV-TEST-0002", amount="10.00", currency="EUR")
    store.save(v)
    ledger = Ledger(tmp_path / "vouchers.db")
    try:
        history = ledger.issuance_history("GV-TEST-0002")
        assert len(history) == 1
        assert history[0]["details"]["amount"] == "10.00"
    finally:
        ledger.close()


def test_redemption_is_audited(store, tmp_path):
    v = VoucherFactory().build(code="GV-TEST-0003", amount="40.00", currency="EUR")
    store.save(v)
    loaded = store.load("GV-TEST-0003")
    loaded.redeem(MoneyFactory.create("15.00", "EUR"))
    store.save(loaded)
    ledger = Ledger(tmp_path / "vouchers.db")
    try:
        kinds = [entry["kind"] for entry in ledger.activity("GV-TEST-0003")]
        assert "redeemed" in kinds
    finally:
        ledger.close()
