import json
import subprocess
import sys
from pathlib import Path

from siqoq.capabilities import RuntimeCapabilities
from siqoq.placement import place


def node(**overrides: bool) -> RuntimeCapabilities:
    values = {
        "os_name": "Linux",
        "arch": "x86_64",
        "vision_extra_available": False,
        "transport_nats_available": False,
        "transport_mqtt_available": False,
        "observability_extra_available": False,
        "gpu_probe_tool_available": False,
    }
    values.update(overrides)
    return RuntimeCapabilities(**values)


def test_place_has_no_eligible_node() -> None:
    result = place({"vision_extra_available": True}, {"node-a": node()})

    assert result == {
        "eligible": [],
        "rejected": {
            "node-a": ["vision_extra_available is False, required True"],
        },
    }


def test_place_has_exactly_one_eligible_node() -> None:
    result = place(
        {"transport_nats_available": True},
        {"node-b": node(), "node-a": node(transport_nats_available=True)},
    )

    assert result["eligible"] == ["node-a"]
    assert result["rejected"] == {
        "node-b": ["transport_nats_available is False, required True"]
    }


def test_place_has_multiple_eligible_nodes_in_sorted_order() -> None:
    result = place(
        {"gpu_probe_tool_available": True},
        {
            "node-c": node(gpu_probe_tool_available=True),
            "node-a": node(gpu_probe_tool_available=True),
        },
    )

    assert result == {"eligible": ["node-a", "node-c"], "rejected": {}}


def test_place_reports_one_missing_optional_extra() -> None:
    result = place(
        {
            "vision_extra_available": True,
            "observability_extra_available": True,
        },
        {"node-a": node(vision_extra_available=True)},
    )

    assert result["rejected"] == {
        "node-a": ["observability_extra_available is False, required True"]
    }


def test_placement_cli_prints_place_result(tmp_path: Path) -> None:
    nodes_path = tmp_path / "nodes.json"
    nodes_path.write_text(
        json.dumps({"node-z": node(vision_extra_available=True).to_dict()}),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "siqoq.cli",
            "placement",
            "check",
            "--nodes",
            str(nodes_path),
            "--require",
            "vision_extra_available",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(completed.stdout) == {"eligible": ["node-z"], "rejected": {}}
