"""Wallet operations.

All money movement funnels through WalletService so that balances and the
ledger stay consistent. Handlers (api.py) and batch jobs (promotions.py)
never touch wallets except through these entry points.
"""

from __future__ import annotations

from .errors import (
    CurrencyMismatch,
    InsufficientFunds,
    InvalidAmount,
    WalletClosed,
    WalletNotActive,
)
from .ledger import Ledger
from .models import LedgerEntry, Wallet, WalletStatus, new_wallet_id
from .store import WalletStore


class WalletService:
    def __init__(self, store: WalletStore, ledger: Ledger) -> None:
        self._store = store
        self._ledger = ledger

    def open_wallet(self, customer_id: str, currency: str = "USD") -> Wallet:
        wallet = Wallet(id=new_wallet_id(), customer_id=customer_id, currency=currency)
        self._store.add(wallet)
        return wallet

    def top_up(self, wallet_id: str, amount_cents: int, memo: str = "") -> int:
        wallet = self._store.get(wallet_id)
        if wallet.status is not WalletStatus.ACTIVE:
            raise WalletNotActive(wallet_id)
        if amount_cents <= 0:
            raise InvalidAmount(f"top-up must be positive, got {amount_cents}")
        wallet.balance_cents += amount_cents
        self._ledger.record(
            LedgerEntry(wallet.id, "topup", amount_cents, wallet.balance_cents, memo)
        )
        return wallet.balance_cents

    def charge(self, wallet_id: str, amount_cents: int, memo: str = "") -> int:
        wallet = self._store.get(wallet_id)
        if wallet.status is not WalletStatus.ACTIVE:
            raise WalletNotActive(wallet_id)
        if amount_cents <= 0:
            raise InvalidAmount(f"charge must be positive, got {amount_cents}")
        if amount_cents > wallet.balance_cents:
            raise InsufficientFunds(wallet.id, amount_cents, wallet.balance_cents)
        wallet.balance_cents -= amount_cents
        self._ledger.record(
            LedgerEntry(wallet.id, "charge", -amount_cents, wallet.balance_cents, memo)
        )
        return wallet.balance_cents

    def apply_adjustment(self, wallet_id: str, amount_cents: int, memo: str = "") -> int:
        """Signed correction: positive for goodwill credit, negative to reclaim
        credit (promo clawbacks, billing corrections). Allowed on frozen
        wallets so support can fix balances during an investigation."""
        wallet = self._store.get(wallet_id)
        if wallet.status is WalletStatus.CLOSED:
            raise WalletClosed(wallet_id)
        if amount_cents == 0:
            raise InvalidAmount("adjustment of zero has no effect")
        wallet.balance_cents += amount_cents
        self._ledger.record(
            LedgerEntry(wallet.id, "adjustment", amount_cents, wallet.balance_cents, memo)
        )
        return wallet.balance_cents

    def transfer(
        self, source_id: str, dest_id: str, amount_cents: int, memo: str = ""
    ) -> tuple[int, int]:
        """Move credit between two wallets of the same customer or team."""
        source = self._store.get(source_id)
        dest = self._store.get(dest_id)
        if source.status is not WalletStatus.ACTIVE:
            raise WalletNotActive(source_id)
        if dest.status is not WalletStatus.ACTIVE:
            raise WalletNotActive(dest_id)
        if source.currency != dest.currency:
            raise CurrencyMismatch(f"{source.currency} -> {dest.currency}")
        if amount_cents <= 0:
            raise InvalidAmount(f"transfer must be positive, got {amount_cents}")
        if amount_cents > source.balance_cents:
            raise InsufficientFunds(source.id, amount_cents, source.balance_cents)
        source.balance_cents -= amount_cents
        dest.balance_cents += amount_cents
        self._ledger.record(
            LedgerEntry(source.id, "transfer_out", -amount_cents, source.balance_cents, memo)
        )
        self._ledger.record(
            LedgerEntry(dest.id, "transfer_in", amount_cents, dest.balance_cents, memo)
        )
        return source.balance_cents, dest.balance_cents

    def freeze(self, wallet_id: str) -> None:
        wallet = self._store.get(wallet_id)
        if wallet.status is WalletStatus.CLOSED:
            raise WalletClosed(wallet_id)
        wallet.status = WalletStatus.FROZEN

    def close(self, wallet_id: str) -> None:
        wallet = self._store.get(wallet_id)
        if wallet.balance_cents != 0:
            raise InvalidAmount(
                f"wallet {wallet_id!r} still holds {wallet.balance_cents}c; "
                "drain before closing"
            )
        wallet.status = WalletStatus.CLOSED
