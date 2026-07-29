import pytest

from walletd.api import handle_charge, handle_top_up, handle_transfer
from walletd.ledger import Ledger
from walletd.services import WalletService
from walletd.store import WalletStore


@pytest.fixture()
def service():
    return WalletService(WalletStore(), Ledger())


def test_handle_charge_happy_path(service):
    w = service.open_wallet("cus_ida")
    handle_top_up(service, {"wallet_id": w.id, "amount_cents": 700})
    resp = handle_charge(service, {"wallet_id": w.id, "amount_cents": 250, "memo": "usage"})
    assert resp == {"ok": True, "balance_cents": 450}


def test_handle_charge_translates_refusal(service):
    w = service.open_wallet("cus_ida")
    resp = handle_charge(service, {"wallet_id": w.id, "amount_cents": 250})
    assert resp["ok"] is False
    assert resp["error"] == "InsufficientFunds"


def test_handle_transfer_happy_path(service):
    a = service.open_wallet("cus_joy")
    b = service.open_wallet("cus_joy")
    handle_top_up(service, {"wallet_id": a.id, "amount_cents": 600})
    resp = handle_transfer(
        service, {"source_id": a.id, "dest_id": b.id, "amount_cents": 200}
    )
    assert resp == {
        "ok": True,
        "source_balance_cents": 400,
        "dest_balance_cents": 200,
    }
