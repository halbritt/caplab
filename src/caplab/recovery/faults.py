"""Explicit P5-only fault injection around the ordinary metadata protocol."""

from __future__ import annotations

from typing import Any

from caplab.runtime.models import RegistrationIntent

from .errors import InjectedInterruption


class InterruptAfterEvent:
    """Raise once after a selected verified-write event has been retained."""

    def __init__(self, metadata: Any, event_type: str) -> None:
        if event_type not in {"object-verified", "local-copy-verified"}:
            raise ValueError("unsupported P5 interruption checkpoint")
        self.metadata = metadata
        self.event_type = event_type
        self.triggered = False

    def claim_operation(self, intent: RegistrationIntent) -> bool:
        return self.metadata.claim_operation(intent)

    def object_guard(self, content_sha256: str) -> Any:
        return self.metadata.object_guard(content_sha256)

    def append_event(self, operation_id: str, event_type: str) -> None:
        self.metadata.append_event(operation_id, event_type)
        if event_type == self.event_type and not self.triggered:
            self.triggered = True
            raise InjectedInterruption(f"injected {event_type} interruption")

    def finalize_registration(self, intent: RegistrationIntent) -> dict[str, Any]:
        return self.metadata.finalize_registration(intent)

    def registration_for_operation(self, operation_id: str) -> dict[str, Any] | None:
        return self.metadata.registration_for_operation(operation_id)

    def operation_for_operation(self, operation_id: str) -> dict[str, Any] | None:
        return self.metadata.operation_for_operation(operation_id)
