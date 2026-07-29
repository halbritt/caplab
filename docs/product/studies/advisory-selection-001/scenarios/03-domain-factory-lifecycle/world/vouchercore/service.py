"""Application-facing operations: what the shop actually calls."""

from __future__ import annotations

from pathlib import Path

from vouchercore.errors import DuplicateCode
from vouchercore.factory import DEFAULT_VALID_DAYS, VoucherFactory, generate_code
from vouchercore.money import Money, MoneyFactory
from vouchercore.store import VoucherStore
from vouchercore.voucher import Voucher


class VoucherService:
    """Issue, redeem, and inspect gift vouchers."""

    def __init__(self, db_path: str | Path) -> None:
        self._store = VoucherStore(db_path)
        self._factory = VoucherFactory()

    def close(self) -> None:
        self._store.close()

    def issue(
        self,
        amount: object,
        currency: str = "EUR",
        code: str | None = None,
        valid_days: int = DEFAULT_VALID_DAYS,
    ) -> Voucher:
        code = (code or generate_code()).strip().upper()
        if self._store.exists(code):
            raise DuplicateCode(f"a voucher with code {code} already exists")
        voucher = self._factory.build(
            code=code, amount=amount, currency=currency, valid_days=valid_days
        )
        self._store.save(voucher)
        return voucher

    def redeem(self, code: str, amount: object, currency: str = "EUR") -> Money:
        voucher = self._store.load(code)
        remaining = voucher.redeem(MoneyFactory.create(amount, currency))
        self._store.save(voucher)
        return remaining

    def check_balance(self, code: str) -> Money:
        return self._store.load(code).balance
