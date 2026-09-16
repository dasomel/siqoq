# Evaluation: Windows Support and CI Strategy

Source issue: #23, "[EVALUATION] Evaluate Windows support and CI strategy".

## Actual current CI state vs. issue assumption

The issue body assumes a multi-OS CI matrix already exists and asks whether to extend it
to Windows. That premise does not match the repo. As of this evaluation, `.github/workflows/ci.yml`
runs a **single job on `ubuntu-latest`**:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: pip
      - run: python -m pip install --upgrade pip
      - run: pip install -e '.[dev]'
      - run: ruff check .
      - run: pytest
      - run: python -m build
```

There is no macOS or ARM64 runner, and no OS matrix at all. Any decision framed as "add
Windows to the existing matrix" needs to instead be framed as "add the first non-Linux
runner."

Additionally, `pyproject.toml` declares `dependencies = []`: the package is pure Python
with no OpenCV/UVC camera, ONNX/TensorRT, or ROS 2 dependency in `src/siqoq` yet. The
problems that usually make Windows support hard for a physical-AI stack (native camera
drivers, GPU inference backends, ROS 2 tooling) do not exist in this codebase today. On
the current dependency surface, Windows compatibility is almost certainly trivial to
verify and maintain.

## Recommendation

- **Do not** add Windows to the required/blocking CI gate yet. There is no code today
  that Windows compatibility would meaningfully protect, and a blocking gate on unproven
  ground adds friction for no evaluated benefit.
- **Do** add a non-blocking `windows-latest` smoke job now, x64 only:
  - `ruff check .`
  - `pytest`
  - `python -m build`

  This costs little, gives early signal if a future dependency silently breaks Windows,
  and matches AGENTS.md's guidance to avoid prematurely hardening one hardware/vendor
  path — a smoke job commits to nothing beyond "the pure-Python path still installs and
  tests pass on Windows."
- **Defer** any native-Windows PoC and any WSL2-vs-native decision until a hardware/device
  adapter (camera, ROS 2, ONNX/TensorRT) is actually proposed. Those are the dependencies
  that would actually determine whether native Windows, WSL2, or "Linux/Jetson only" is the
  right answer, and none of them exist in the repo yet.

## Cost note

GitHub-hosted Windows runners bill at roughly 2x the minutes of Linux runners for the same
wall-clock job. That is a secondary reason to keep the Windows job non-blocking and smoke-only
rather than a full duplicate matrix (lint + test + build across OSes) until there's a concrete
reason to run more on it.

## Re-evaluation trigger

Re-run this evaluation when the first camera/serial/ROS2 (or ONNX/TensorRT) adapter PR is
opened. At that point, re-check whether the new dependency has known Windows support, and
decide then whether the smoke job needs to become blocking, gain a real matrix, or whether
Windows should be explicitly declared unsupported.
