from __future__ import annotations

import argparse

from .adapters import AllowListSafetyGate, GeneratedSensor, MemoryTransport, MockActionAdapter, StaticInference
from .pipeline import NoOpPolicy, SiqoqPipeline


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="siqoq")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("demo", help="Run the hardware-free perception pipeline demo")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "demo":
        return run_demo()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
