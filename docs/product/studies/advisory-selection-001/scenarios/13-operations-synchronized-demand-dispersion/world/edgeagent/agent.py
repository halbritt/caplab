"""The main device agent loop."""

from __future__ import annotations

import logging
import time
from typing import Callable

from .config import AgentConfig
from .scheduler import next_sync_time, seconds_until
from .telemetry import TelemetryBuffer
from .transport import ControlPlaneClient, SyncError

log = logging.getLogger(__name__)

AGENT_VERSION = "0.4.2"


class EdgeAgent:
    """One terminal's sync loop against the control plane."""

    def __init__(
        self,
        config: AgentConfig,
        client: ControlPlaneClient,
        telemetry: TelemetryBuffer | None = None,
        clock: Callable[[], float] = time.time,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._config = config
        self._client = client
        self.telemetry = telemetry or TelemetryBuffer(config.telemetry_batch_size)
        self._clock = clock
        self._sleep = sleep
        self._stopped = False
        self.last_response: dict | None = None

    def stop(self) -> None:
        """Ask the loop to exit before its next cycle."""
        self._stopped = True

    def sync_once(self) -> bool:
        """Perform one check-in. Returns True on success.

        On failure the telemetry batch is put back so nothing is lost;
        the events go out with the next successful check-in.
        """
        batch = self.telemetry.take_batch()
        payload = {
            "device_id": self._config.device_id,
            "agent_version": AGENT_VERSION,
            "sent_at": self._clock(),
            "telemetry": batch,
        }
        try:
            self.last_response = self._client.check_in(payload)
        except SyncError:
            self.telemetry.requeue(batch)
            log.warning("check-in abandoned; will try again next cycle")
            return False
        return True

    def start(self, max_cycles: int | None = None) -> None:
        """Run the sync loop.

        A freshly booted terminal checks in straight away so it picks
        up config without waiting for the next boundary; after that,
        check-ins follow the schedule.

        ``max_cycles`` bounds the number of check-ins (used by tests
        and the one-shot CLI mode); ``None`` means run until ``stop()``.
        """
        cycles = 0
        while not self._stopped:
            self.sync_once()
            cycles += 1
            if max_cycles is not None and cycles >= max_cycles:
                return
            target = next_sync_time(
                self._clock(), self._config.sync_interval_seconds
            )
            self._sleep(seconds_until(self._clock(), target))
