"""Shard math: which shard a customer lands in, which shards a host owns."""

from __future__ import annotations

import zlib

from meterd.config import FleetConfig


def shard_of(customer: str, shard_count: int) -> int:
    """Stable customer-to-shard mapping.

    Ingest and the rollup workers must agree on this, so it is a pure
    function of the customer id.
    """
    return zlib.crc32(customer.encode("utf-8")) % shard_count


def shards_for(hostname: str, cfg: FleetConfig) -> tuple[int, ...]:
    """Shards owned by *hostname* per the fleet file.

    Hosts absent from the fleet file own no shards; provisioning is
    expected to add each worker when it is imaged.
    """
    return cfg.assignments.get(hostname, ())
