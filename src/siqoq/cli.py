from __future__ import annotations

import argparse
import json

from . import telemetry
from .capabilities import discover
from .events import SemanticEvent
from .scenario import ScenarioConfig, run_scenario
from .transport import StdoutTransport


def run_demo() -> int:
    with telemetry.start_span("siqoq.demo.generate_event"):
        event = SemanticEvent.detected(
            source="sim.camera.front",
            object_name="person",
            confidence=0.94,
        )
        StdoutTransport().publish(event)
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

    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "demo":
        return run_demo()
    if args.command == "capabilities":
        return run_capabilities_command()
    if args.command == "scenario" and args.scenario_command == "run":
        return run_scenario_command(args.config)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
