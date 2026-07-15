"""Garage S3 byte adapter with no delete surface."""

from __future__ import annotations

from contextlib import closing
from typing import Any

from botocore.exceptions import ClientError

from ..canonical import sha256_hex
from ..models import object_key


class S3ObjectStore:
    def __init__(self, client: Any, bucket: str) -> None:
        if not bucket:
            raise ValueError("S3 bucket must not be empty")
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
    ) -> "S3ObjectStore":
        import boto3
        from botocore.config import Config

        client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
                proxies={},
            ),
        )
        return cls(client, bucket)

    @staticmethod
    def _missing(error: BaseException) -> bool:
        response = getattr(error, "response", None)
        if not isinstance(response, dict):
            return False
        details = response.get("Error")
        if not isinstance(details, dict):
            return False
        return str(details.get("Code")) in {"404", "NoSuchKey", "NotFound"}

    def read(self, key: str) -> bytes | None:
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
        except ClientError as error:
            if self._missing(error):
                return None
            raise
        body = response.get("Body")
        if body is None or not hasattr(body, "read") or not hasattr(body, "close"):
            raise RuntimeError("S3 GetObject returned no closeable body")
        with closing(body):
            payload = body.read()
        if not isinstance(payload, bytes):
            raise RuntimeError("S3 GetObject body did not return bytes")
        return payload

    def write(self, key: str, data: bytes) -> None:
        expected = object_key(sha256_hex(data))
        if key != expected:
            raise ValueError("S3 key must be derived from the supplied bytes")
        self.client.put_object(Bucket=self.bucket, Key=expected, Body=data)
