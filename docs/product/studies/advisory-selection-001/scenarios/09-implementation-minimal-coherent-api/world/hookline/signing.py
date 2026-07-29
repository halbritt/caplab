"""Payload signing.

Subscribers verify the ``X-Hookline-Signature`` header before trusting a
delivery. The signature is an HMAC-SHA256 of the raw request body.
"""

from __future__ import annotations

import hashlib
import hmac


def sign_payload(secret: bytes, body: bytes) -> str:
    return hmac.new(secret, body, hashlib.sha256).hexdigest()


def verify_signature(secret: bytes, body: bytes, signature: str) -> bool:
    return hmac.compare_digest(sign_payload(secret, body), signature)
