from __future__ import annotations

import argparse
import json

from . import telemetry
from .capabilities import discover
from .events import SemanticEvent
from .fleet import FleetInventory
from .placement import run_placement_check
from .scenario import ScenarioConfig, run_scenario
from .transport import StdoutTransport
from .workload import WorkloadSpec


def run_demo() -> int:
    with telemetry.start_span("siqoq.demo.generate_event"):
        event = SemanticEvent.detected(
            source="sim.camera.front",
            object_name="person",
            confidence=0.94,
        )
        StdoutTransport().publish(event)
    return 0


def run_workload_validate_command(spec_path: str) -> int:
    spec = WorkloadSpec.from_json(spec_path)
    reasons = spec.validate_against(discover())
    print(
        json.dumps(
            {"name": spec.name, "satisfiable": not reasons, "reasons": reasons},
            indent=2,
        )
    )
    return 0


def run_fleet_list_command(inventory_path: str) -> int:
    inventory = FleetInventory.from_jsonl(inventory_path)
    print(json.dumps([entry.to_dict() for entry in inventory.entries], indent=2))
    return 0


def run_fleet_query_command(inventory_path: str, require: list[str]) -> int:
    inventory = FleetInventory.from_jsonl(inventory_path)
    required = {name: True for name in require}
    matches = inventory.find_matching(required)
    print(json.dumps([entry.node_id for entry in matches], indent=2))
    return 0


def run_scenario_command(config_path: str) -> int:
    config = ScenarioConfig.from_json(config_path)
    summary = run_scenario(config)
    print(summary.to_json())
    return 0


def run_capabilities_command() -> int:
    print(json.dumps(discover().to_dict(), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="siqoq")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("demo", help="Run the hardware-free semantic-event demo")
    subparsers.add_parser(
        "capabilities", help="Report best-effort runtime capabilities as JSON"
    )

    scenario_parser = subparsers.add_parser(
        "scenario", help="Run a reproducible fixture-driven scenario"
    )
    scenario_subparsers = scenario_parser.add_subparsers(
        dest="scenario_command", required=True
    )
    scenario_run_parser = scenario_subparsers.add_parser(
        "run", help="Run a scenario end-to-end from a config file"
    )
    scenario_run_parser.add_argument("--config", required=True, help="Path to scenario config JSON")

    workload_parser = subparsers.add_parser(
        "workload", help="Declarative workload spec operations"
    )
    workload_subparsers = workload_parser.add_subparsers(
        dest="workload_command", required=True
    )
    workload_validate_parser = workload_subparsers.add_parser(
        "validate", help="Validate a workload spec against this node's runtime capabilities"
    )
    workload_validate_parser.add_argument(
        "--spec", required=True, help="Path to workload spec JSON"
    )

    fleet_parser = subparsers.add_parser(
        "fleet", help="Query a local, hardware-free edge fleet inventory"
    )
    fleet_subparsers = fleet_parser.add_subparsers(dest="fleet_command", required=True)

    fleet_list_parser = fleet_subparsers.add_parser(
        "list", help="List all fleet inventory entries as JSON"
    )
    fleet_list_parser.add_argument(
        "--inventory", required=True, help="Path to fleet inventory JSONL file"
    )

    fleet_query_parser = fleet_subparsers.add_parser(
        "query", help="List node_ids matching required capabilities"
    )
    fleet_query_parser.add_argument(
        "--inventory", required=True, help="Path to fleet inventory JSONL file"
    )
    fleet_query_parser.add_argument(
        "--require",
        action="append",
        default=[],
        help="Required capability field name (repeatable)",
    )

    placement_parser = subparsers.add_parser(
        "placement", help="Check workload placement against node capabilities"
    )
    placement_subparsers = placement_parser.add_subparsers(
        dest="placement_command", required=True
    )
    placement_check_parser = placement_subparsers.add_parser(
        "check", help="Print eligible and rejected nodes as JSON"
    )
    placement_check_parser.add_argument(
        "--nodes", required=True, help="Path to node capabilities JSON mapping"
    )
    placement_check_parser.add_argument(
        "--require", action="append", default=[], help="Required capability (repeatable)"
    )

    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "demo":
        return run_demo()
    if args.command == "capabilities":
        return run_capabilities_command()
    if args.command == "scenario" and args.scenario_command == "run":
        return run_scenario_command(args.config)
    if args.command == "workload" and args.workload_command == "validate":
        return run_workload_validate_command(args.spec)
    if args.command == "fleet" and args.fleet_command == "list":
        return run_fleet_list_command(args.inventory)
    if args.command == "fleet" and args.fleet_command == "query":
        return run_fleet_query_command(args.inventory, args.require)
    if args.command == "placement" and args.placement_command == "check":
        return run_placement_check(args.nodes, args.require)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
