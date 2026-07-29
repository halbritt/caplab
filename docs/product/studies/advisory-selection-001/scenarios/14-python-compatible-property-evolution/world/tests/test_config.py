import json

import pytest

from upmon.config import (
    DEFAULT_RETRIES,
    DEFAULT_TIMEOUT,
    MAX_POLL_INTERVAL,
    MIN_POLL_INTERVAL,
    build_jobs,
    load_config,
)


def _write(tmp_path, payload):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(payload))
    return path


def test_startup_pulls_intervals_into_band(tmp_path):
    path = _write(
        tmp_path,
        {
            "jobs": [
                {"name": "edge", "url": "https://edge.example/health", "poll_interval": 0.5},
                {"name": "slow", "url": "https://slow.example/health", "poll_interval": 86400},
            ]
        },
    )
    jobs = build_jobs(load_config(path))
    assert jobs[0].poll_interval == MIN_POLL_INTERVAL
    assert jobs[1].poll_interval == MAX_POLL_INTERVAL


def test_defaults_applied(tmp_path):
    path = _write(
        tmp_path,
        {"jobs": [{"name": "edge", "url": "https://edge.example/health"}]},
    )
    (job,) = build_jobs(load_config(path))
    assert job.poll_interval == 60.0
    assert job.timeout == DEFAULT_TIMEOUT
    assert job.retries == DEFAULT_RETRIES
    assert job.enabled is True


def test_missing_jobs_key_rejected(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{}")
    with pytest.raises(ValueError):
        load_config(path)
