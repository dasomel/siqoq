from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters import (
    AllowListSafetyGate,
    GeneratedSensor,
    MemoryTransport,
    MockActionAdapter,
    StaticInference,
)
from .pipeline import NoOpPolicy, SiqoqPipeline
from .runtime import RuntimeManifest, discover_capabilities
from .scenarios import run_fixture_scenario, validate_fixture


def run_demo() -> int:
    transport = MemoryTransport()
    pipeline = SiqoqPipeline(
        sensor=GeneratedSensor(count=1),
        inference=StaticInference(),
        transport=transport,
        policy=NoOpPolicy(),
        safety=AllowListSafetyGate(),
        action=MockActionAdapter(),
    )
    result = pipeline.run_once()
    for event in result.events:
        print(event.to_json())
    return 0


def run_inspect() -> int:
    capabilities = discover_capabilities()
    payload = {
        "manifest": json.loads(RuntimeManifest().to_json()),
        "capabilities": {
            "architecture": capabilities.architecture,
            "accelerator": capabilities.accelerator,
            "sensors": list(capabilities.sensors),
            "actuators": list(capabilities.actuators),
        },
    }
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return 0


def run_scenario(path: str, name: str, output: str | None) -> int:
    summary = run_fixture_scenario(path, name=name)
    payload = summary.to_json()
    if output:
        destination = Path(output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


def run_validate_fixture(path: str) -> int:
    try:
        sample_count = validate_fixture(path)
    except ValueError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"valid": True, "samples": sample_count}, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="siqoq")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("demo", help="Run the hardware-free perception pipeline demo")
    subparsers.add_parser("inspect", help="Show the local runtime manifest and capabilities")

    scenario = subparsers.add_parser(
        "scenario",
        help="Run a deterministic JSONL fixture scenario",
    )
    scenario.add_argument("fixture", help="Path to a JSONL SensorSample fixture")
    scenario.add_argument("--name", default="fixture", help="Scenario name for the JSON summary")
    scenario.add_argument("--output", help="Optional path for the JSON scenario summary")

    validate = subparsers.add_parser(
        "validate-fixture",
        help="Validate a deterministic JSONL SensorSample fixture",
    )
    validate.add_argument("fixture", help="Path to a JSONL SensorSample fixture")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "demo":
        return run_demo()
    if args.command == "inspect":
        return run_inspect()
    if args.command == "scenario":
        return run_scenario(args.fixture, args.name, args.output)
    if args.command == "validate-fixture":
        return run_validate_fixture(args.fixture)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
