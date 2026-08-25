# Contributing to Siqoq

Siqoq follows the issue-first and reviewable-change principles used by OpenForge.

## Before coding

For non-trivial work, start from an issue. The issue should describe:

- problem and motivation
- affected architecture/components
- alternatives or constraints
- acceptance criteria
- test/validation strategy

## Pull requests

Keep pull requests focused. Include tests and documentation when behavior or interfaces change. Link the relevant issue.

## Hardware work

Hardware-dependent features should include a simulator, fake adapter, or recorded fixture whenever practical so CI and contributors are not blocked by device ownership.

## Local checks

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
ruff check .
pytest
python -m build
```

## AI-assisted contributions

AI tools may be used, but contributors are responsible for correctness, licensing, security, tests, and reviewability. Do not include secrets, proprietary source material, or unreviewed generated binaries.
