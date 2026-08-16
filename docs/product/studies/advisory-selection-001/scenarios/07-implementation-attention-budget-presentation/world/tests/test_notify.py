from datetime import datetime, timezone

from opsdigest.notify import Outbox

NOW = datetime(2026, 7, 28, 6, 0, tzinfo=timezone.utc)


def test_outbox_writes_dated_file(tmp_path):
    outbox = Outbox(tmp_path / "outbox")
    path = outbox.deliver("Ops digest for 2026-07-28\n", now=NOW)
    assert path.name == "digest-20260728.txt"
    assert path.read_text(encoding="utf-8") == "Ops digest for 2026-07-28\n"


def test_outbox_creates_directory(tmp_path):
    outbox = Outbox(tmp_path / "deep" / "outbox")
    path = outbox.deliver("x\n", now=NOW)
    assert path.exists()
