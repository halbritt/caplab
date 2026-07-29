"""Drains the outbox and hands each pending entry to hookline.

Production runs ``flush`` on a one-minute timer.
"""

from __future__ import annotations

from dataclasses import dataclass

from hookline.delivery import DeliveryError


@dataclass
class OutboxEntry:
    event: object
    url: str
    done: bool = False
    error: str | None = None


class Outbox:
    def __init__(self):
        self._entries: list[OutboxEntry] = []

    def add(self, event, url) -> None:
        self._entries.append(OutboxEntry(event, url))

    def pending(self) -> list[OutboxEntry]:
        return [e for e in self._entries if not e.done and e.error is None]


def flush(outbox: Outbox, service) -> int:
    """Send every pending entry once; park entries that exhaust their attempts.

    Partner endpoints rate-limit aggressively, so retries are meant to be
    spaced out rather than fired back-to-back.
    """
    delivered = 0
    for entry in outbox.pending():
        try:
            service.send(entry.event, entry.url, max_attempts=5, backoff=2.0, timeout=10.0)
        except DeliveryError as err:
            entry.error = str(err)
        else:
            entry.done = True
            delivered += 1
    return delivered
