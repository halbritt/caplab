"""Request handlers for the billing sandbox.

Each handler takes a decoded JSON payload, invokes wallet operations, and
returns a plain dict ready for serialisation. The production deployment
mounts these behind FastAPI routes; the sandbox calls them directly.
"""

from __future__ import annotations

from typing import Any, Mapping

from .errors import WalletError
from .services import WalletService


def _failure(exc: WalletError) -> dict[str, Any]:
    return {"ok": False, "error": type(exc).__name__, "detail": str(exc)}


def handle_top_up(service: WalletService, payload: Mapping[str, Any]) -> dict[str, Any]:
    try:
        balance = service.top_up(
            payload["wallet_id"], int(payload["amount_cents"]), payload.get("memo", "")
        )
    except WalletError as exc:
        return _failure(exc)
    return {"ok": True, "balance_cents": balance}


def handle_charge(service: WalletService, payload: Mapping[str, Any]) -> dict[str, Any]:
    try:
        balance = service.charge(
            payload["wallet_id"], int(payload["amount_cents"]), payload.get("memo", "")
        )
    except WalletError as exc:
        return _failure(exc)
    return {"ok": True, "balance_cents": balance}


def handle_transfer(service: WalletService, payload: Mapping[str, Any]) -> dict[str, Any]:
    try:
        source_balance, dest_balance = service.transfer(
            payload["source_id"],
            payload["dest_id"],
            int(payload["amount_cents"]),
            payload.get("memo", ""),
        )
    except WalletError as exc:
        return _failure(exc)
    return {
        "ok": True,
        "source_balance_cents": source_balance,
        "dest_balance_cents": dest_balance,
    }
