"""In-memory wallet repository.

The production build substitutes a Postgres-backed store exposing the same
interface; nothing outside this module may assume dict-backed storage.
"""

from __future__ import annotations

from .errors import WalletNotFound
from .models import Wallet


class WalletStore:
    def __init__(self) -> None:
        self._by_id: dict[str, Wallet] = {}

    def add(self, wallet: Wallet) -> None:
        if wallet.id in self._by_id:
            raise ValueError(f"duplicate wallet id {wallet.id!r}")
        self._by_id[wallet.id] = wallet

    def get(self, wallet_id: str) -> Wallet:
        try:
            return self._by_id[wallet_id]
        except KeyError:
            raise WalletNotFound(wallet_id) from None

    def for_customer(self, customer_id: str) -> list[Wallet]:
        return [w for w in self._by_id.values() if w.customer_id == customer_id]
