import pytest

from walletd.errors import (
    CurrencyMismatch,
    InsufficientFunds,
    InvalidAmount,
    WalletNotActive,
    WalletNotFound,
)
from walletd.ledger import Ledger
from walletd.services import WalletService
from walletd.store import WalletStore


@pytest.fixture()
def ledger():
    return Ledger()


@pytest.fixture()
def service(ledger):
    return WalletService(WalletStore(), ledger)


def test_top_up_increases_balance_and_hits_ledger(service, ledger):
    w = service.open_wallet("cus_ada")
    assert service.top_up(w.id, 500, memo="card") == 500
    entries = ledger.entries_for(w.id)
    assert [e.kind for e in entries] == ["topup"]
    assert entries[-1].balance_after_cents == 500


def test_top_up_rejects_nonpositive_amounts(service):
    w = service.open_wallet("cus_ada")
    with pytest.raises(InvalidAmount):
        service.top_up(w.id, 0)


def test_charge_within_balance(service, ledger):
    w = service.open_wallet("cus_bee")
    service.top_up(w.id, 800)
    assert service.charge(w.id, 300, memo="april usage") == 500
    assert ledger.entries_for(w.id)[-1].amount_cents == -300


def test_charge_beyond_balance_is_refused(service):
    w = service.open_wallet("cus_bee")
    service.top_up(w.id, 200)
    with pytest.raises(InsufficientFunds):
        service.charge(w.id, 900)
    # a refused charge must leave the balance untouched
    assert service.charge(w.id, 200) == 0


def test_charge_requires_active_wallet(service):
    w = service.open_wallet("cus_cyn")
    service.top_up(w.id, 400)
    service.freeze(w.id)
    with pytest.raises(WalletNotActive):
        service.charge(w.id, 100)


def test_goodwill_credit_lands_on_frozen_wallet(service):
    w = service.open_wallet("cus_cyn")
    service.top_up(w.id, 100)
    service.freeze(w.id)
    assert service.apply_adjustment(w.id, 250, memo="goodwill") == 350


def test_adjustment_reclaims_credit_within_balance(service, ledger):
    w = service.open_wallet("cus_dot")
    service.top_up(w.id, 1000)
    assert service.apply_adjustment(w.id, -300, memo="billing correction") == 700
    assert ledger.entries_for(w.id)[-1].kind == "adjustment"


def test_transfer_moves_funds_between_wallets(service):
    a = service.open_wallet("cus_eve")
    b = service.open_wallet("cus_eve")
    service.top_up(a.id, 900)
    assert service.transfer(a.id, b.id, 400) == (500, 400)


def test_transfer_beyond_balance_is_refused(service):
    a = service.open_wallet("cus_eve")
    b = service.open_wallet("cus_eve")
    service.top_up(a.id, 100)
    with pytest.raises(InsufficientFunds):
        service.transfer(a.id, b.id, 400)


def test_transfer_requires_matching_currency(service):
    a = service.open_wallet("cus_fay", currency="USD")
    b = service.open_wallet("cus_fay", currency="EUR")
    service.top_up(a.id, 100)
    with pytest.raises(CurrencyMismatch):
        service.transfer(a.id, b.id, 50)


def test_unknown_wallet_raises(service):
    with pytest.raises(WalletNotFound):
        service.charge("wal_missing", 100)


def test_close_requires_drained_wallet(service):
    w = service.open_wallet("cus_gus")
    service.top_up(w.id, 50)
    with pytest.raises(InvalidAmount):
        service.close(w.id)
    service.charge(w.id, 50)
    service.close(w.id)
