from datetime import datetime, timedelta, timezone

import pytest

from walletd.ledger import Ledger
from walletd.promotions import PromoGrant, grant_promo, run_clawback_batch
from walletd.services import WalletService
from walletd.store import WalletStore


@pytest.fixture()
def service():
    return WalletService(WalletStore(), Ledger())


def _grant(wallet_id, amount, *, expired):
    delta = timedelta(days=-3 if expired else 3)
    return PromoGrant(
        promo_code="SPRING24",
        wallet_id=wallet_id,
        amount_cents=amount,
        expires_at=datetime.now(timezone.utc) + delta,
    )


def test_grant_then_expiry_clawback_roundtrip(service):
    w = service.open_wallet("cus_gil")
    service.top_up(w.id, 1000)
    grant = _grant(w.id, 500, expired=True)
    grant_promo(service, grant)  # 1500
    service.charge(w.id, 400)  # 1100
    results = run_clawback_batch(service, [grant])
    assert results == [(w.id, "reclaimed")]
    assert service.charge(w.id, 600) == 0  # 1100 - 500 reclaimed leaves 600


def test_unexpired_grants_are_left_alone(service):
    w = service.open_wallet("cus_hal")
    grant = _grant(w.id, 500, expired=False)
    grant_promo(service, grant)
    results = run_clawback_batch(service, [grant])
    assert results == [(w.id, "still-active")]
    assert service.charge(w.id, 500) == 0
