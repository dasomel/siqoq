from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from siqoq.capabilities import RuntimeCapabilities
from siqoq.fleet import FleetEntry, FleetInventory, aggregate_results

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


def test_aggregate_results_sums_node_summaries(tmp_path: Path) -> None:
    (tmp_path / "node-01.json").write_text(
        json.dumps(
            {
                "event_count": 3,
                "type_counts": {"detected": 2, "zone_entered": 1},
                "action_counts": {"noop": 2, "alert": 1},
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "node-02.json").write_text(
        json.dumps(
            {
                "event_count": 2,
                "type_counts": {"detected": 1, "zone_exited": 1},
                "action_counts": {"noop": 1, "alert": 1},
            }
        ),
        encoding="utf-8",
    )

    summary = aggregate_results(tmp_path)
    assert summary.node_count == 2
    assert summary.total_events == 5
    assert summary.event_type_totals == {"detected": 3, "zone_entered": 1, "zone_exited": 1}
    assert summary.action_outcome_totals == {"noop": 3, "alert": 2}


def test_aggregate_results_skips_malformed_json(tmp_path: Path, capsys) -> None:
    (tmp_path / "valid.json").write_text(
        json.dumps({"event_count": 1, "type_counts": {}, "action_counts": {}}),
        encoding="utf-8",
    )
    (tmp_path / "broken.json").write_text("{not json", encoding="utf-8")

    summary = aggregate_results(tmp_path)
    assert summary.node_count == 1
    assert "warning: skipping" in capsys.readouterr().err


def test_aggregate_results_empty_directory_is_zero_summary(tmp_path: Path) -> None:
    assert aggregate_results(tmp_path).to_dict() == {
        "node_count": 0,
        "total_events": 0,
        "event_type_totals": {},
        "action_outcome_totals": {},
    }


def test_cli_fleet_observe_prints_json(tmp_path: Path) -> None:
    (tmp_path / "node.json").write_text(
        json.dumps(
            {"event_count": 4, "type_counts": {"detected": 4}, "action_counts": {"noop": 4}}
        ),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "siqoq.cli", "fleet", "observe", "--results-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(result.stdout)["total_events"] == 4
