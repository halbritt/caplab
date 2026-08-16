"""Delivery of signed events to subscriber endpoints."""

from __future__ import annotations

import time

from .retry import RetryPolicy
from .signing import sign_payload
from .transport import TransportError


class DeliveryError(Exception):
    def __init__(self, url: str, attempts: int, last_status: int | None):
        self.url = url
        self.attempts = attempts
        self.last_status = last_status
        super().__init__(
            f"delivery to {url} failed after {attempts} attempts "
            f"(last status: {last_status})"
        )


class DeliveryService:
    def __init__(self, transport, signing_secret: bytes, sleep=time.sleep):
        self._transport = transport
        self._secret = signing_secret
        self._sleep = sleep

    def send(self, event, url, **options):
        """Deliver an event to a subscriber endpoint."""
        policy = RetryPolicy.from_options(options)
        timeout = float(options.get("timeout", 5.0))
        body = event.to_payload()
        headers = {
            "Content-Type": "application/json",
            "X-Hookline-Event": event.kind,
            "X-Hookline-Signature": sign_payload(self._secret, body),
        }
        last_status = None
        for attempt in range(1, policy.max_attempts + 1):
            if attempt > 1:
                self._sleep(policy.delay_before(attempt))
            try:
                response = self._transport.post(url, body, headers, timeout=timeout)
            except TransportError:
                last_status = None
                continue
            if response.status < 500:
                return response
            last_status = response.status
        raise DeliveryError(url, policy.max_attempts, last_status)
