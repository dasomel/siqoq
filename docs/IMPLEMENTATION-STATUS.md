# Implementation Status

Last verified: 2026-09-09 against `main`

This snapshot records the executable scope currently present on the default branch. Siqoq is still an early-bootstrap / architecture-validation project; the target architecture and planned capabilities in `README.md` and `docs/roadmap.md` are not implementation claims.

## Implemented

- Python package/bootstrap structure under `src/siqoq/`.
- A small CLI entrypoint and semantic-event model that provide the initial executable core for validating interfaces before larger runtime choices are locked in.
- Unit-test and CI foundations, Makefile/development workflow, contribution/security guidance, and repository-level agent instructions.
- Architecture, principles, roadmap, and development documentation for the simulation-first Physical AI direction.

## Planned / not yet claimed

- Isaac Sim/Gazebo integration beyond documented direction.
- Real camera/LiDAR/IMU adapters as a complete hardware abstraction layer.
- Production vision runtime, TensorRT/Jetson optimization, NATS/MQTT event infrastructure, K3s deployment, ROS 2 bridge, actuator control, fleet/GitOps management, or a complete end-to-end perception → action runtime.
- Production readiness or hardware coverage beyond paths backed by executable evidence on `main`.

## Evidence

- `README.md` — explicitly labels the project `Early bootstrap / architecture validation`.
- `src/siqoq/cli.py`
- `src/siqoq/events.py`
- `tests/`
- `.github/workflows/ci.yml`
- `docs/architecture.md`
- `docs/roadmap.md`
