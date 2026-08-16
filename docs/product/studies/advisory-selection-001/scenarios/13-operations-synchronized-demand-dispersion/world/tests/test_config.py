import pytest

from edgeagent.config import AgentConfig


def test_from_mapping_applies_defaults():
    config = AgentConfig.from_mapping(
        {"device_id": "t-9", "control_plane_url": "https://cp.example.test"}
    )
    assert config.sync_interval_seconds == 600.0
    assert config.telemetry_batch_size == 50


def test_from_mapping_reads_overrides():
    config = AgentConfig.from_mapping(
        {
            "device_id": "t-9",
            "control_plane_url": "https://cp.example.test",
            "sync_interval_seconds": 120,
            "telemetry_batch_size": 5,
        }
    )
    assert config.sync_interval_seconds == 120.0
    assert config.telemetry_batch_size == 5


def test_rejects_bad_values():
    with pytest.raises(ValueError):
        AgentConfig(device_id="", control_plane_url="https://cp.example.test")
    with pytest.raises(ValueError):
        AgentConfig(
            device_id="t-9",
            control_plane_url="https://cp.example.test",
            sync_interval_seconds=0,
        )
