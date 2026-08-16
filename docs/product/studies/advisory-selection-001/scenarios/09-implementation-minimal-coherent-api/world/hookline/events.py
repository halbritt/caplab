"""Event payloads delivered by hookline."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Event:
    kind: str
    data: dict
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def to_payload(self) -> bytes:
        return json.dumps(
            {"id": self.id, "kind": self.kind, "data": self.data},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
