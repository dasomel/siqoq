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

## Hardware-specific work

Hardware support must be implemented behind an adapter and include one of:

- a simulator
- a fake/mock implementation
- recorded test data

This keeps CI and basic development independent from device availability.

## AI coding tools

AI coding assistants are welcome, but contributors remain responsible for correctness, licensing, security, tests, and reviewability. Do not commit secrets, copied proprietary code, or generated large binary assets.
