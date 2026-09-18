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
```

The first demo uses generated/synthetic events and requires no camera or accelerator.

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
```

## Repository layout

```text
src/siqoq/          core package
examples/           runnable examples
docs/               architecture and guides
.github/             CI and contribution automation
tests/               automated tests
```

## Container build

A multi-stage `Dockerfile` at the repo root builds the base package (no vendor/hardware
extras) for both `amd64` and `arm64`. Local reproduction of the CI build:

```bash
docker buildx build --platform linux/amd64,linux/arm64 .
```

By default the image runs `siqoq demo`. Override the command to run a scenario instead:

```bash
docker run --rm -v "$PWD/examples:/app/examples" <image> scenario run --config examples/scenario.json
```

CI builds and smoke-tests the `amd64` image only (`siqoq demo`); `arm64` is built via QEMU
emulation and is build-verified, not run-tested on real ARM64 hardware. A Jetson/CUDA base
image is a separate profile, tracked in a later spike.

## Hardware-specific work

Hardware support must be implemented behind an adapter and include one of:

- a simulator
- a fake/mock implementation
- recorded test data

This keeps CI and basic development independent from device availability.

## AI coding tools

AI coding assistants are welcome, but contributors remain responsible for correctness, licensing, security, tests, and reviewability. Do not commit secrets, copied proprietary code, or generated large binary assets.
