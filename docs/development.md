# Development Guide

## Local baseline

The initial developer experience targets macOS and Linux without requiring special hardware.

Prerequisites:

- Python 3.12+
- Git
- optional Docker/Podman

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
siqoq demo
siqoq inspect
```

`siqoq demo` runs the hardware-free perception pipeline using a generated sensor, deterministic static inference, semantic-event output, a no-op policy, and a mock-safe action path.

`siqoq inspect` prints the current runtime manifest and best-effort local capability discovery without requiring vendor SDKs.

## Current skeleton boundaries

The initial implementation intentionally uses only lightweight Python contracts and mock adapters:

```text
GeneratedSensor
      ↓
StaticInference
      ↓
SemanticEvent
      ↓
MemoryTransport
      ↓
NoOpPolicy
      ↓
AllowListSafetyGate
      ↓
MockActionAdapter
```

This is not the final implementation architecture. It is the executable seam used to attach recorded video, webcam, ONNX Runtime, NATS/MQTT, simulation, Jetson/TensorRT, and physical action adapters in later issues.

## Development workflow

1. Create or choose an issue.
2. Analyze the affected architecture and existing contracts before editing code.
3. Implement the smallest coherent change.
4. Add or update tests.
5. Update documentation when behavior or interfaces change.
6. Run local checks.
7. Open a focused pull request linked to the issue.

## Commands

```bash
ruff check .
pytest
python -m build
siqoq demo
siqoq inspect
```

## Repository layout

```text
src/siqoq/
  contracts.py      vendor-neutral data/protocol contracts
  events.py         semantic-event envelope
  adapters.py       initial generated/mock adapters
  pipeline.py       perception-to-action composition
  runtime.py        runtime manifest/capability bootstrap
  cli.py            local CLI
examples/           runnable examples
docs/               architecture and guides
.github/             CI and contribution automation
tests/               automated tests
```

## Hardware-specific work

Hardware support must be implemented behind an adapter and include one of:

- a simulator
- a fake/mock implementation
- recorded test data

This keeps CI and basic development independent from device availability.

The default action path must remain safe: physical actions require explicit configuration and must pass an action/safety boundary. Mock/no-op behavior is preferred for default development and CI.

## AI coding tools

AI coding assistants are welcome, but contributors remain responsible for correctness, licensing, security, tests, and reviewability. Do not commit secrets, copied proprietary code, or generated large binary assets.
