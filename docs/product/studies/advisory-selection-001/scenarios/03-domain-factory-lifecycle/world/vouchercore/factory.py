"""Assembly of voucher aggregates and voucher-code generation."""

from __future__ import annotations

import re
import secrets
from datetime import timedelta

from vouchercore.errors import InvalidVoucher
from vouchercore.money import MoneyFactory
from vouchercore.voucher import Voucher, VoucherStatus, utcnow

# No ambiguous glyphs (0/O, 1/I/L) — these codes get read out over the phone.
_CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
_CODE_PATTERN = re.compile(r"^GV-[A-Z0-9]{4}-[A-Z0-9]{4}$")

DEFAULT_VALID_DAYS = 365


def generate_code() -> str:
    def chunk() -> str:
        return "".join(secrets.choice(_CODE_ALPHABET) for _ in range(4))

    return f"GV-{chunk()}-{chunk()}"


def new_voucher_id() -> str:
    return secrets.token_hex(16)


class VoucherFactory:
    """Builds voucher aggregates for the service and storage layers."""

    def build(
        self,
        code: str,
        amount: object,
        currency: str,
        valid_days: int = DEFAULT_VALID_DAYS,
    ) -> Voucher:
        voucher = Voucher()
        voucher.voucher_id = new_voucher_id()
        voucher.code = code.strip().upper()
        voucher.balance = MoneyFactory.create(amount, currency)
        voucher.status = VoucherStatus.ACTIVE
        voucher.issued_at = utcnow()
        voucher.expires_at = voucher.issued_at + timedelta(days=valid_days)
        voucher.record_event(
            "issued",
            amount=str(voucher.balance.amount),
            currency=voucher.balance.currency,
        )
        self._check(voucher)
        return voucher

    def _check(self, voucher: Voucher) -> None:
        if not _CODE_PATTERN.match(voucher.code or ""):
            raise InvalidVoucher(f"malformed voucher code: {voucher.code!r}")
        if voucher.balance is None or voucher.balance.amount <= 0:
            raise InvalidVoucher("a voucher must be issued with a positive balance")
        if voucher.expires_at <= voucher.issued_at:
            raise InvalidVoucher("expiry must fall after issue")
