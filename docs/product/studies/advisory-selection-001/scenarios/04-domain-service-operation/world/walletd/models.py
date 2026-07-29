"""Records for the wallet subsystem.

Wallets hold prepaid credit in integer cents. Every balance movement is
mirrored into the ledger (see ledger.py) so statements can be rebuilt from
the entry stream alone.
"""

from __future__ import annotations

import enum
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


class WalletStatus(str, enum.Enum):
    ACTIVE = "active"
    FROZEN = "frozen"  # spending blocked; support corrections still allowed
    CLOSED = "closed"


def new_wallet_id() -> str:
    return f"wal_{uuid.uuid4().hex[:12]}"


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Wallet:
    """A customer's prepaid credit balance."""

    id: str
    customer_id: str
    currency: str = "USD"
    balance_cents: int = 0
    status: WalletStatus = WalletStatus.ACTIVE
    opened_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class LedgerEntry:
    """One movement on one wallet. Amounts are signed; negative means funds
    left the wallet."""

    wallet_id: str
    kind: str  # topup | charge | adjustment | transfer_in | transfer_out
    amount_cents: int
    balance_after_cents: int
    memo: str = ""
    at: datetime = field(default_factory=_now)
