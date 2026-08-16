"""Control-socket command handling.

The transport (a Unix socket served next to the scheduler by the deployment
wrapper) is thin; all command behavior lives in :func:`handle_command` so it
can be tested without a socket.  ``upmonctl`` sends one JSON object per line
and reads one JSON reply per line.
"""

from __future__ import annotations

import json

from upmon.runtime import RuntimeController, UnknownFieldError, UnknownJobError


def handle_command(controller: RuntimeController, line: str) -> str:
    """Execute one JSON command line and return one JSON reply line."""
    try:
        msg = json.loads(line)
    except json.JSONDecodeError:
        return json.dumps({"ok": False, "error": "bad json"})

    cmd = msg.get("cmd")
    if cmd == "status":
        return json.dumps({"ok": True, "jobs": controller.status()})
    if cmd == "update":
        try:
            snap = controller.apply_update(msg.get("job", ""), msg.get("set", {}))
        except UnknownJobError as exc:
            return json.dumps({"ok": False, "error": f"unknown job: {exc.args[0]}"})
        except UnknownFieldError as exc:
            return json.dumps(
                {"ok": False, "error": f"field not runtime-mutable: {exc.args[0]}"}
            )
        return json.dumps({"ok": True, "job": snap})
    return json.dumps({"ok": False, "error": f"unknown cmd: {cmd!r}"})
