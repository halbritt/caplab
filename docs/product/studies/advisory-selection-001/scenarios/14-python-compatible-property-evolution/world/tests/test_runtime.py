import json

import pytest

from upmon.control import handle_command
from upmon.probe import ProbeJob
from upmon.runtime import RuntimeController, UnknownFieldError, UnknownJobError


def _controller():
    jobs = [
        ProbeJob("edge", "https://edge.example/health", poll_interval=30),
        ProbeJob("db", "https://db.example/health", poll_interval=300, retries=4),
    ]
    return RuntimeController(jobs), jobs


def test_update_applies_and_returns_snapshot():
    ctrl, jobs = _controller()
    snap = ctrl.apply_update("edge", {"timeout": 3.0, "enabled": False})
    assert snap["timeout"] == 3.0
    assert snap["enabled"] is False
    assert jobs[0].enabled is False


def test_update_can_slow_a_job_down():
    ctrl, jobs = _controller()
    snap = ctrl.apply_update("db", {"poll_interval": 900.0})
    assert snap["poll_interval"] == 900.0
    assert jobs[1].poll_interval == 900.0


def test_unknown_job_rejected():
    ctrl, _ = _controller()
    with pytest.raises(UnknownJobError):
        ctrl.apply_update("cache", {"enabled": False})


def test_unknown_field_rejected():
    ctrl, jobs = _controller()
    with pytest.raises(UnknownFieldError):
        ctrl.apply_update("edge", {"name": "edge2"})
    assert jobs[0].name == "edge"


def test_control_update_round_trip():
    ctrl, _ = _controller()
    reply = json.loads(
        handle_command(ctrl, '{"cmd": "update", "job": "db", "set": {"retries": 1}}')
    )
    assert reply["ok"] is True
    assert reply["job"]["retries"] == 1


def test_control_rejects_bad_json():
    ctrl, _ = _controller()
    reply = json.loads(handle_command(ctrl, "{nope"))
    assert reply["ok"] is False
