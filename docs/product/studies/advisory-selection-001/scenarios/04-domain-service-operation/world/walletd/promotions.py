"""Promotional credit grants and the nightly expiry clawback batch."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .services import WalletService


@dataclass(frozen=True)
class PromoGrant:
    promo_code: str
    wallet_id: str
    amount_cents: int
    expires_at: datetime


def grant_promo(service: WalletService, grant: PromoGrant) -> int:
    """Credit a promotional grant to its wallet. Returns the new balance."""
    return service.apply_adjustment(
        grant.wallet_id, grant.amount_cents, memo=f"promo {grant.promo_code}"
    )


def run_clawback_batch(
    service: WalletService,
    grants: list[PromoGrant],
    now: datetime | None = None,
) -> list[tuple[str, str]]:
    """Reclaim expired promotional credit. Runs nightly from cron in the
    sandbox and from the billing scheduler in production."""
    now = now or datetime.now(timezone.utc)
    results: list[tuple[str, str]] = []
    for grant in grants:
        if grant.expires_at > now:
            results.append((grant.wallet_id, "still-active"))
            continue
        service.apply_adjustment(
            grant.wallet_id,
            -grant.amount_cents,
            memo=f"promo {grant.promo_code} expired",
        )
        results.append((grant.wallet_id, "reclaimed"))
    return results
