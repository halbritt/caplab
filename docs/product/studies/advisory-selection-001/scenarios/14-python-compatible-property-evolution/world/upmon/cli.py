"""Entry point: ``python -m upmon /etc/upmon/config.json``."""

from __future__ import annotations

import sys

from upmon.config import build_jobs, load_config
from upmon.prober import http_probe
from upmon.scheduler import Scheduler


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: upmon CONFIG.json", file=sys.stderr)
        return 2
    jobs = build_jobs(load_config(argv[0]))
    Scheduler(jobs, http_probe).run_forever()
    return 0
