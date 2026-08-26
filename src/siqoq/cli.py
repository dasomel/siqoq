from __future__ import annotations

import argparse
import json

from .adapters import (
    AllowListSafetyGate,
    GeneratedSensor,
    MemoryTransport,
    MockActionAdapter,
    StaticInference,
)
from .pipeline import NoOpPolicy, SiqoqPipeline
from .runtime import RuntimeManifest, discover_capabilities


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="siqoq")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("demo", help="Run the hardware-free perception pipeline demo")
    subparsers.add_parser("inspect", help="Show the local runtime manifest and capabilities")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "demo":
        return run_demo()
    if args.command == "inspect":
        return run_inspect()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
