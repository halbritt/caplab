"""Provisioning and configuration for one device agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

DEFAULT_SYNC_INTERVAL_SECONDS = 600.0
DEFAULT_TELEMETRY_BATCH_SIZE = 50


@dataclass(frozen=True)
class AgentConfig:
    """Static configuration for one device agent.

    Provisioning documents are written by the enrollment service and
    dropped onto the device at install time; they change rarely.
    """

    device_id: str
    control_plane_url: str
    sync_interval_seconds: float = DEFAULT_SYNC_INTERVAL_SECONDS
    telemetry_batch_size: int = DEFAULT_TELEMETRY_BATCH_SIZE

    def __post_init__(self) -> None:
        if not self.device_id:
            raise ValueError("device_id must be non-empty")
        if not self.control_plane_url:
            raise ValueError("control_plane_url must be non-empty")
        if self.sync_interval_seconds <= 0:
            raise ValueError("sync_interval_seconds must be positive")
        if self.telemetry_batch_size < 1:
            raise ValueError("telemetry_batch_size must be at least 1")

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "AgentConfig":
        """Build a config from a parsed provisioning document."""
        return cls(
            device_id=str(raw["device_id"]),
            control_plane_url=str(raw["control_plane_url"]),
            sync_interval_seconds=float(
                raw.get("sync_interval_seconds", DEFAULT_SYNC_INTERVAL_SECONDS)
            ),
            telemetry_batch_size=int(
                raw.get("telemetry_batch_size", DEFAULT_TELEMETRY_BATCH_SIZE)
            ),
        )
