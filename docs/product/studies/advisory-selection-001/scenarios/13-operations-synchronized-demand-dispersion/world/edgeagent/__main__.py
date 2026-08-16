"""Run a device agent from a provisioning document.

Usage:

    python -m edgeagent /etc/edgeagent/provisioning.json
"""

from __future__ import annotations

import json
import logging
import sys

from .agent import EdgeAgent
from .config import AgentConfig
from .transport import ControlPlaneClient


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    with open(argv[0], encoding="utf-8") as fh:
        config = AgentConfig.from_mapping(json.load(fh))
    client = ControlPlaneClient(config.control_plane_url)
    EdgeAgent(config, client).start()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
