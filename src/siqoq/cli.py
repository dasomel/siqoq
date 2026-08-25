from __future__ import annotations

import argparse

from .events import SemanticEvent


def run_demo() -> int:
    event = SemanticEvent.detected(
        source="sim.camera.front",
        object_name="person",
        confidence=0.94,
    )
    print(event.to_json())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="siqoq")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("demo", help="Run the hardware-free semantic-event demo")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "demo":
        return run_demo()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
