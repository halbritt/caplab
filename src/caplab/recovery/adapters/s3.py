"""P5-only Garage adapter with explicit replacement and removal authority."""

from __future__ import annotations

import re
from typing import Any

from caplab.runtime.adapters.s3 import S3ObjectStore
from caplab.runtime.canonical import sha256_hex
from caplab.runtime.errors import ObjectMismatch
from caplab.runtime.models import object_key


CONTENT_KEY = re.compile(r"\Aobjects/sha256/([0-9a-f]{2})/([0-9a-f]{64})\Z")


def _require_key(key: str) -> None:
    match = CONTENT_KEY.fullmatch(key)
    if match is None or match.group(1) != match.group(2)[:2]:
        raise ValueError("Garage key is not a canonical content-addressed key")


class S3CustodyStore:
    def __init__(self, client: Any, bucket: str) -> None:
        self._reader = S3ObjectStore(client, bucket)
        self.client = client
        self.bucket = bucket

    @classmethod
    def from_settings(
        cls,
        *,
        endpoint_url: str,
        region: str,
        bucket: str,
        access_key_id: str,
        secret_access_key: str,
    ) -> "S3CustodyStore":
        ordinary = S3ObjectStore.from_settings(
            endpoint_url=endpoint_url,
            region=region,
            bucket=bucket,
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
        )
        return cls(ordinary.client, ordinary.bucket)

    def read(self, key: str) -> bytes | None:
        _require_key(key)
        return self._reader.read(key)

    def replace(self, key: str, data: bytes) -> None:
        _require_key(key)
        if not isinstance(data, bytes):
            raise TypeError("Garage replacement payload must be bytes")
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data)

    def write(self, key: str, data: bytes) -> None:
        expected = object_key(sha256_hex(data))
        if key != expected:
            raise ValueError("Garage key must be derived from the supplied bytes")
        existing = self.read(key)
        if existing is not None and existing != data:
            raise ObjectMismatch(f"refusing non-identical object at {key}")
        if existing is None:
            self.client.put_object(Bucket=self.bucket, Key=key, Body=data)

    def remove(self, key: str) -> None:
        _require_key(key)
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def keys(self) -> set[str]:
        keys: set[str] = set()
        continuation: str | None = None
        while True:
            arguments: dict[str, Any] = {
                "Bucket": self.bucket,
                "Prefix": "objects/sha256/",
            }
            if continuation is not None:
                arguments["ContinuationToken"] = continuation
            response = self.client.list_objects_v2(**arguments)
            contents = response.get("Contents", [])
            if not isinstance(contents, list):
                raise RuntimeError("S3 ListObjectsV2 returned invalid Contents")
            for item in contents:
                if not isinstance(item, dict) or not isinstance(item.get("Key"), str):
                    raise RuntimeError("S3 ListObjectsV2 returned an invalid key entry")
                key = item["Key"]
                _require_key(key)
                keys.add(key)
            if response.get("IsTruncated") is not True:
                return keys
            token = response.get("NextContinuationToken")
            if not isinstance(token, str) or not token:
                raise RuntimeError(
                    "truncated S3 listing omitted its continuation token"
                )
            continuation = token
