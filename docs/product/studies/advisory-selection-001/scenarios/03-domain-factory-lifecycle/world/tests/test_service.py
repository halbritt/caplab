from decimal import Decimal

import pytest

from vouchercore.errors import DuplicateCode, InsufficientBalance, InvalidVoucher
from vouchercore.factory import VoucherFactory
from vouchercore.ledger import Ledger
from vouchercore.money import MoneyFactory
from vouchercore.service import VoucherService
from vouchercore.voucher import VoucherStatus


@pytest.fixture
def service(tmp_path):
    svc = VoucherService(tmp_path / "vouchers.db")
    yield svc
    svc.close()


def test_issue_returns_active_voucher(service):
    v = service.issue("50.00")
    assert v.status is VoucherStatus.ACTIVE
    assert v.balance.amount == Decimal("50.00")
    assert v.code.startswith("GV-")


def test_issue_rejects_duplicate_code(service):
    service.issue("25.00", code="GV-AAAA-2222")
    with pytest.raises(DuplicateCode):
        service.issue("10.00", code="GV-AAAA-2222")


def test_redeem_reduces_balance(service):
    v = service.issue("50.00")
    remaining = service.redeem(v.code, "20.00")
    assert remaining.amount == Decimal("30.00")
    assert service.check_balance(v.code).amount == Decimal("30.00")


def test_redeem_beyond_balance_is_refused(service):
    v = service.issue("30.00")
    with pytest.raises(InsufficientBalance):
        service.redeem(v.code, "40.00")


def test_full_redemption_reports_zero_remaining(service):
    v = service.issue("20.00")
    remaining = service.redeem(v.code, "20.00")
    assert remaining.is_zero()


def test_redeeming_a_non_active_voucher_is_refused():
    v = VoucherFactory().build(code="GV-UNIT-0001", amount="20.00", currency="EUR")
    v.status = VoucherStatus.VOID
    with pytest.raises(InvalidVoucher):
        v.redeem(MoneyFactory.create("5.00", "EUR"))


def test_outstanding_total_sums_issued_vouchers(service, tmp_path):
    service.issue("50.00")
    service.issue("30.00")
    ledger = Ledger(tmp_path / "vouchers.db")
    try:
        assert ledger.outstanding_total() == Decimal("80.00")
    finally:
        ledger.close()
