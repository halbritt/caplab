"""Domain errors for vouchercore."""


class VoucherError(Exception):
    """Base class for all voucher domain errors."""


class InvalidAmount(VoucherError):
    """A monetary amount or currency that the shop does not accept."""


class CurrencyMismatch(VoucherError):
    """Two amounts in different currencies were combined."""


class InvalidVoucher(VoucherError):
    """The voucher is malformed, expired, or not in a usable state."""


class DuplicateCode(VoucherError):
    """A voucher with this code has already been issued."""


class VoucherNotFound(VoucherError):
    """No voucher with the given code exists."""


class InsufficientBalance(VoucherError):
    """The redemption amount exceeds the remaining balance."""
