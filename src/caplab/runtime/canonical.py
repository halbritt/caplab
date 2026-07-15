"""A deliberately small canonical JSON boundary for durable identities."""

from __future__ import annotations

import hashlib
import json
import unicodedata
from collections.abc import Mapping
from typing import Any


class CanonicalizationError(ValueError):
    """A value cannot be represented without an ambiguous identity."""


def _normalize(value: Any) -> Any:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        raise CanonicalizationError("floating-point values are not identity-safe")
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    if isinstance(value, Mapping):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise CanonicalizationError("object keys must be strings")
            normalized_key = unicodedata.normalize("NFC", key)
            if normalized_key in normalized:
                raise CanonicalizationError(
                    f"object keys collide after NFC normalization: {normalized_key!r}"
                )
            normalized[normalized_key] = _normalize(item)
        return normalized
    raise CanonicalizationError(f"unsupported canonical JSON value: {type(value).__name__}")


def canonical_json(value: Any) -> bytes:
    """Encode the supported JSON subset as normalized UTF-8 bytes."""

    try:
        return json.dumps(
            _normalize(value),
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        if isinstance(error, CanonicalizationError):
            raise
        raise CanonicalizationError(str(error)) from error


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
