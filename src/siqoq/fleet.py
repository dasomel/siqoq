"""Edge fleet inventory (single-process, hardware-free).

Implements the "edge fleet inventory" scope item from issue #59: a way to
record and query multiple nodes' `RuntimeCapabilities` (see
`siqoq.capabilities`) without a real fleet/network service. The inventory
is populated from a local JSONL file, one entry per line, matching the
existing fixture convention used under `tests/fixtures/`.

Reuses `RuntimeCapabilities` verbatim rather than duplicating its fields, so
a fleet entry's capability shape can never drift from the single-process
discovery shape.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .capabilities import RuntimeCapabilities

_CAPABILITY_FIELDS = (
    "os_name",
    "arch",
    "vision_extra_available",
    "transport_nats_available",
    "transport_mqtt_available",
    "observability_extra_available",
    "gpu_probe_tool_available",
)


@dataclass(slots=True, frozen=True)
class FleetEntry:
    """A single fleet node's last-reported capabilities snapshot."""

    node_id: str
    capabilities: RuntimeCapabilities
    last_seen: str

    def to_dict(self) -> dict[str, object]:
        return {
            "node_id": self.node_id,
            "capabilities": self.capabilities.to_dict(),
            "last_seen": self.last_seen,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> FleetEntry:
        caps_payload = payload["capabilities"]
        assert isinstance(caps_payload, dict)
        capabilities = RuntimeCapabilities(
            **{field: caps_payload[field] for field in _CAPABILITY_FIELDS}
        )
        return cls(
            node_id=str(payload["node_id"]),
            capabilities=capabilities,
            last_seen=str(payload["last_seen"]),
        )


class FleetInventory:
    """A queryable list of `FleetEntry` records, backed by a JSONL file.

    Pure local file I/O: no network calls or fleet-manager service are
    involved. The file is a stand-in for what a real fleet would report.
    """

    def __init__(self, entries: list[FleetEntry] | None = None) -> None:
        self._entries: list[FleetEntry] = list(entries) if entries else []

    @property
    def entries(self) -> list[FleetEntry]:
        return list(self._entries)

    @classmethod
    def from_jsonl(cls, path: str | Path) -> FleetInventory:
        entries: list[FleetEntry] = []
        with Path(path).open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                entries.append(FleetEntry.from_dict(json.loads(line)))
        return cls(entries)

    def to_jsonl(self, path: str | Path) -> None:
        with Path(path).open("w", encoding="utf-8") as handle:
            for entry in self._entries:
                handle.write(json.dumps(entry.to_dict()) + "\n")

    def find_matching(self, required: dict[str, bool]) -> list[FleetEntry]:
        """Return entries whose capabilities satisfy all required fields.

        `required` maps a `RuntimeCapabilities` boolean field name (e.g.
        `"vision_extra_available"`) to the value it must hold. Unknown field
        names raise `AttributeError`, matching normal attribute access.
        """
        matches = []
        for entry in self._entries:
            caps = entry.capabilities
            if all(getattr(caps, field) == value for field, value in required.items()):
                matches.append(entry)
        return matches


__all__ = ["FleetEntry", "FleetInventory"]
