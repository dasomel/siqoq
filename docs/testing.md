# Testing

Status: v0. Everything below is hardware-free unless stated otherwise; a passing
`make verify` does not prove camera/device, ONNX/TensorRT, NATS/MQTT, ROS 2,
Kubernetes/K3s, or real actuator behavior (see `AGENTS.md`).

## Baseline (matches CI)

```bash
python3.12 -m venv .venv && source .venv/bin/activate
make install   # pip install -e '.[dev]'
make verify    # ruff check . && pytest && python -m build
```

Individual steps: `make lint`, `make test`, `make build`.

## Optional extras (vision / transport / observability)

The base install stays zero-dependency (`pyproject.toml`'s `dependencies = []`).
`inference.py`'s ONNX/OpenCV backend, `transport.py`'s NATS/MQTT adapters, and
`telemetry.py`'s OpenTelemetry spans/counters skip their real-backend tests
unless their extra is installed.

```bash
make install-full   # pip install -e '.[dev,vision,transport,observability]'
make verify-full    # install-full, then verify
```

## Exercising the CLI directly

```bash
siqoq demo                                                    # generated/simulated scenario
siqoq scenario run --config examples/scenario.json            # fixture-driven scenario
siqoq scenario run --config examples/scenarios/scene_multi_step_sequence.json
siqoq capabilities                                            # this node's RuntimeCapabilities
siqoq workload validate --spec examples/workloads/fixture_detection_workload.json
siqoq fleet list --inventory examples/fleet/inventory.jsonl
siqoq fleet query --inventory examples/fleet/inventory.jsonl --require vision_extra_available
siqoq fleet observe --results-dir examples/fleet/results
siqoq placement check --nodes examples/nodes.json --require vision_extra_available
siqoq skills list
siqoq skills classify --event-type object.detected
siqoq trace build --event-json <path> [--action-json <path>] [--include-metadata]
siqoq ui serve [--port 8000] [--fleet-inventory <path>] [--scenario-catalog <path>]
```

`trace build` redacts event metadata by default; pass `--include-metadata` only
when you explicitly need the raw metadata for debugging (see
`docs/specs/decision-trace.md`).

## Simulation regression gate

`tests/test_scenario_catalog.py` runs every entry in
`examples/scenarios/catalog.json` and asserts each one's `sequence_hash`/outcome.
A failing entry fails `pytest`, which fails CI's `test` job — this is the
existing "simulation validation gates risky changes" mechanism referenced in
Phase 6 (issue #66); no separate gating job exists or is needed.

## Container build

```bash
make container              # docker buildx build --platform linux/amd64,linux/arm64 .
make container-run          # build the amd64 image and run `siqoq demo` inside it (matches CI)
make container-run-native   # build+run for the detected host architecture, no emulation
```

CI builds both architectures via QEMU emulation; only amd64 is actually
run-tested (see `.github/workflows/ci.yml`'s `container` job and
`docs/evaluations/jetson-deployment-profile.md` for why arm64/Jetson stops at
build-only here). `container-run` intentionally forces amd64 for CI parity —
on an arm64 host (e.g. Apple Silicon) this runs under QEMU and prints a
harmless `platform ... does not match the detected host platform` warning.
Use `container-run-native` for local iteration instead; it detects `uname -m`
and builds/runs for that architecture directly, with no emulation warning.

## What a green run does and does not prove

| Command | Proves | Does not prove |
|---|---|---|
| `make verify` | Lint clean, unit tests pass, package builds | Any real hardware/device/network path |
| `siqoq scenario run` | Deterministic simulated/fixture pipeline | Real camera/inference/actuator behavior |
| `make container` | Image builds for both architectures | ARM64 correctness on real hardware (QEMU-emulated only) |

For hardware/edge/simulation-specific claims, state explicitly which path was
exercised, per `AGENTS.md`'s verification section.
