from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from . import telemetry
from .actuation import ActionResult
from .capabilities import discover
from .events import SemanticEvent
from .fleet import FleetInventory, aggregate_results
from .placement import run_placement_check
from .scenario import ScenarioConfig, run_scenario
from .skills import classify, list_catalog
from .trace import build_trace
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


def run_fleet_observe_command(results_dir: str) -> int:
    print(aggregate_results(results_dir).to_json())
    return 0


def run_skills_list_command() -> int:
    print(json.dumps([asdict(skill) for skill in list_catalog()], indent=2))
    return 0


def run_skills_classify_command(event_type: str) -> int:
    event = SemanticEvent(
        type=event_type,
        source="cli.skills.classify",
        object="unknown",
        confidence=0.0,
        timestamp="1970-01-01T00:00:00+00:00",
    )
    print(json.dumps(classify(event), indent=2))
    return 0


def run_trace_build_command(
    event_path: str, action_path: str | None, include_metadata: bool
) -> int:
    with open(event_path, encoding="utf-8") as handle:
        event_data = json.load(handle)
    event = SemanticEvent(**event_data)

    result = None
    if action_path is not None:
        with open(action_path, encoding="utf-8") as handle:
            action_data = json.load(handle)
        result = ActionResult(
            action=action_data["action"],
            event_type=action_data["event_type"],
            outcome=action_data["outcome"],
            correlation_id=action_data.get("correlation_id"),
            timestamp=action_data["timestamp"],
        )

    trace = build_trace(event, result, include_metadata=include_metadata)
    print(trace.to_json())
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

    fleet_observe_parser = fleet_subparsers.add_parser(
        "observe", help="Aggregate per-node scenario results as JSON"
    )
    fleet_observe_parser.add_argument(
        "--results-dir", required=True, help="Directory containing per-node result JSON files"
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

    skills_parser = subparsers.add_parser(
        "skills", help="Semantic event skill catalog operations"
    )
    skills_subparsers = skills_parser.add_subparsers(dest="skills_command", required=True)
    skills_subparsers.add_parser("list", help="List the built-in skill catalog as JSON")
    skills_classify_parser = skills_subparsers.add_parser(
        "classify", help="List skill names matching a semantic event type"
    )
    skills_classify_parser.add_argument(
        "--event-type", required=True, help="Semantic event type, e.g. object.detected"
    )

    trace_parser = subparsers.add_parser(
        "trace", help="Assemble end-to-end decision traces"
    )
    trace_subparsers = trace_parser.add_subparsers(dest="trace_command", required=True)
    trace_build_parser = trace_subparsers.add_parser(
        "build", help="Build a DecisionTrace from an event (and optional action result)"
    )
    trace_build_parser.add_argument(
        "--event-json", required=True, help="Path to SemanticEvent JSON"
    )
    trace_build_parser.add_argument(
        "--action-json", default=None, help="Path to ActionResult JSON (optional)"
    )
    trace_build_parser.add_argument(
        "--include-metadata",
        action="store_true",
        help="Include the event's raw metadata (verbose, non-default; may leak sensitive data)",
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
    if args.command == "fleet" and args.fleet_command == "observe":
        return run_fleet_observe_command(args.results_dir)
    if args.command == "placement" and args.placement_command == "check":
        return run_placement_check(args.nodes, args.require)
    if args.command == "skills" and args.skills_command == "list":
        return run_skills_list_command()
    if args.command == "skills" and args.skills_command == "classify":
        return run_skills_classify_command(args.event_type)
    if args.command == "trace" and args.trace_command == "build":
        return run_trace_build_command(
            args.event_json, args.action_json, args.include_metadata
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
