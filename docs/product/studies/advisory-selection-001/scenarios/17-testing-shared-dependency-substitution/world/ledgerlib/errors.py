"""Exception types raised by ledgerlib."""


class LedgerError(Exception):
    """Base class for all ledgerlib errors."""


class DuplicateAccountError(LedgerError):
    def __init__(self, account_id: str) -> None:
        super().__init__(f"account already exists: {account_id!r}")
        self.account_id = account_id


class UnknownAccountError(LedgerError):
    def __init__(self, account_id: str) -> None:
        super().__init__(f"no such account: {account_id!r}")
        self.account_id = account_id


class UnknownCategoryError(LedgerError):
    def __init__(self, category: str) -> None:
        super().__init__(f"category not allowed: {category!r}")
        self.category = category


class CurrencyMismatchError(LedgerError):
    """Raised when arithmetic mixes two currencies."""
