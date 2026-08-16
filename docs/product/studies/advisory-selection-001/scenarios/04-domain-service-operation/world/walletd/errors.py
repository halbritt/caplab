"""Failure types for the wallet subsystem."""


class WalletError(Exception):
    """Base class for wallet failures the API layer knows how to render."""


class WalletNotFound(WalletError):
    def __init__(self, wallet_id: str) -> None:
        super().__init__(f"no wallet {wallet_id!r}")
        self.wallet_id = wallet_id


class WalletNotActive(WalletError):
    """Spending operations require an ACTIVE wallet."""

    def __init__(self, wallet_id: str) -> None:
        super().__init__(f"wallet {wallet_id!r} is not active")
        self.wallet_id = wallet_id


class WalletClosed(WalletError):
    def __init__(self, wallet_id: str) -> None:
        super().__init__(f"wallet {wallet_id!r} is closed")
        self.wallet_id = wallet_id


class InsufficientFunds(WalletError):
    def __init__(self, wallet_id: str, requested_cents: int, available_cents: int) -> None:
        super().__init__(
            f"wallet {wallet_id!r}: requested {requested_cents}c, "
            f"available {available_cents}c"
        )
        self.wallet_id = wallet_id
        self.requested_cents = requested_cents
        self.available_cents = available_cents


class CurrencyMismatch(WalletError):
    pass


class InvalidAmount(WalletError):
    pass
