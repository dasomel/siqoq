"""Deterministic placement of workloads onto capable runtime nodes."""

from __future__ import annotations

import json
from pathlib import Path

from .capabilities import RuntimeCapabilities


def place(
    required_capabilities: dict[str, bool],
    nodes: dict[str, RuntimeCapabilities],
) -> dict[str, list[str] | dict[str, list[str]]]:
    """Return eligible nodes and capability-specific rejection reasons."""
    eligible: list[str] = []
    rejected: dict[str, list[str]] = {}

    for node_id in sorted(nodes):
        node = nodes[node_id]
        missing = [
            f"{name} is {getattr(node, name)}, required {required}"
            for name, required in sorted(required_capabilities.items())
            if getattr(node, name) != required
        ]
        if missing:
            rejected[node_id] = missing
        else:
            eligible.append(node_id)

    return {"eligible": eligible, "rejected": rejected}


def _load_nodes(path: str) -> dict[str, RuntimeCapabilities]:
    with Path(path).open(encoding="utf-8") as file:
        raw_nodes = json.load(file)
    return {node_id: RuntimeCapabilities(**values) for node_id, values in raw_nodes.items()}


def run_placement_check(nodes_path: str, required: list[str]) -> int:
    """Load a node mapping, place a workload, and print the result as JSON."""
    result = place({name: True for name in required}, _load_nodes(nodes_path))
    print(json.dumps(result, indent=2))
    return 0
