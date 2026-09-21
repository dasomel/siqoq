from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from siqoq.capabilities import RuntimeCapabilities
from siqoq.fleet import FleetEntry, FleetInventory

EXAMPLE_INVENTORY = Path(__file__).resolve().parents[1] / "examples" / "fleet" / "inventory.jsonl"


def _caps(**overrides: bool | str) -> RuntimeCapabilities:
    base = dict(
        os_name="Linux",
        arch="x86_64",
        vision_extra_available=False,
        transport_nats_available=False,
        transport_mqtt_available=False,
        observability_extra_available=False,
        gpu_probe_tool_available=False,
    )
    base.update(overrides)
    return RuntimeCapabilities(**base)


def test_load_save_roundtrip(tmp_path: Path) -> None:
    entries = [
        FleetEntry(
            node_id="n1",
            capabilities=_caps(vision_extra_available=True),
            last_seen="2026-09-20T00:00:00Z",
        ),
        FleetEntry(
            node_id="n2",
            capabilities=_caps(),
            last_seen="2026-09-20T00:01:00Z",
        ),
    ]
    inventory = FleetInventory(entries)
    out_path = tmp_path / "roundtrip.jsonl"
    inventory.to_jsonl(out_path)

    loaded = FleetInventory.from_jsonl(out_path)
    assert [e.to_dict() for e in loaded.entries] == [e.to_dict() for e in entries]


def test_example_inventory_loads() -> None:
    inventory = FleetInventory.from_jsonl(EXAMPLE_INVENTORY)
    assert len(inventory.entries) >= 3


def test_find_matching_zero_matches() -> None:
    inventory = FleetInventory.from_jsonl(EXAMPLE_INVENTORY)
    matches = inventory.find_matching(
        {
            "vision_extra_available": True,
            "gpu_probe_tool_available": True,
            "transport_mqtt_available": True,
        }
    )
    assert matches == []


def test_find_matching_one_match() -> None:
    inventory = FleetInventory.from_jsonl(EXAMPLE_INVENTORY)
    matches = inventory.find_matching({"vision_extra_available": True})
    assert [e.node_id for e in matches] == ["edge-node-01"]


def test_find_matching_multiple_matches() -> None:
    inventory = FleetInventory.from_jsonl(EXAMPLE_INVENTORY)
    matches = inventory.find_matching({"transport_nats_available": True})
    assert {e.node_id for e in matches} == {"edge-node-01", "edge-node-02"}


def test_find_matching_capability_no_node_has() -> None:
    inventory = FleetInventory.from_jsonl(EXAMPLE_INVENTORY)
    matches = inventory.find_matching({"os_name": "Windows"})
    assert matches == []


def test_cli_fleet_list_prints_json() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "siqoq.cli", "fleet", "list", "--inventory", str(EXAMPLE_INVENTORY)],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert len(payload) >= 3
    assert payload[0]["node_id"]


def test_cli_fleet_query_prints_matching_node_ids() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "siqoq.cli",
            "fleet",
            "query",
            "--inventory",
            str(EXAMPLE_INVENTORY),
            "--require",
            "vision_extra_available",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload == ["edge-node-01"]
