# Gazebo Integration Spike

Status: evaluation only. **No Gazebo capability is implemented.** This document is
research and design analysis for issue #43 (part of #7); it does not add code or a
dependency to Siqoq.

## What Gazebo provides

Modern Gazebo (formerly "Ignition Gazebo", now `gz-sim`, current stable line "Harmonic",
with "Jetty" as the newer release) ships camera/sensor simulation through the
`gz-sensors` library, which generates data for 2D/3D cameras, depth/RGBD cameras, LiDAR,
IMU, GPS, contact and force-torque sensors from within a running simulation world.

Sensor data leaves the simulator process over **Gazebo Transport (`gz-transport`)**, a
TCP/IP pub/sub messaging layer independent of ROS. A camera sensor publishes
`gz.msgs.Image` (and `gz.msgs.CameraInfo`) on a topic such as `/camera/image`, and any
process on the network can subscribe using:

- the `gz topic` CLI, for inspection (`gz topic -l | grep image`, `gz topic -i --topic ...`),
- the C++ `gz-transport` API, or
- **Python bindings** (`gz.transport13`+, package name varies by Gazebo version) that
  expose publisher/subscriber/service objects directly.

There are two paths to get that data into an external (non-Gazebo) process:

1. **Direct `gz-transport` subscription** — a Python or C++ process subscribes to the
   `gz.msgs.Image` topic directly. No ROS 2 install required, only Gazebo's own
   transport libraries.
2. **`ros_gz` bridge** — the `ros_gz_bridge` (`parameter_bridge`) or the dedicated
   `ros_gz_image` package republishes `gz.msgs.Image` as ROS 2 `sensor_msgs/msg/Image`,
   using `image_transport` for optional compression. This requires a working ROS 2
   installation in addition to Gazebo.

Both paths require **a running Gazebo simulation process** — there is no way to get
camera data without the simulator actually running the world.

## What a `SensorAdapter`-conformant wrapper would need

Per `docs/specs/sensor-contract.md` (Sensor Contract v0), `siqoq.sensors.SensorAdapter`
only requires:

```python
class SensorAdapter(Protocol):
    def read(self, *, count: int) -> Iterator[SemanticEvent]: ...
```

A Gazebo adapter (e.g. `GazeboSensorAdapter`) would sit entirely inside an adapter
module and would need to:

1. Open a `gz-transport` (or `ros_gz`-bridged ROS 2) subscription to the camera topic
   at construction/`open()` time.
2. Convert each incoming `gz.msgs.Image` (or bridged `sensor_msgs/msg/Image`) into
   Siqoq's existing frame representation — likely composing with the frame-level
   `FrameSensor` contract (`open`/`read`/`close`, normalized `Frame` = `FrameMetadata` +
   `payload: bytes`), the same way `UsbWebcamFrameSensor` wraps a real camera today.
3. Feed frames through the existing `InferenceAdapter` pipeline to produce
   `SemanticEvent`s, so `read(count=N)` yields events identical in shape to
   `GeneratedSensorAdapter`/`FixtureSensorAdapter` output.
4. Translate simulator-side identity (world name, model name, sensor topic) into the
   contract's plain string `source` field.

Critically, **no `gz`, `gz-transport`, or ROS 2 type may appear in `siqoq.sensors` or
`siqoq.video_sensors`.** Those SDK types must be fully contained inside the adapter
module (e.g. `siqoq.adapters.gazebo`), converted to `Frame`/`SemanticEvent` at the
boundary — consistent with the existing rule that no vendor SDK type (OpenCV `Mat`,
codec frame object) leaks into the frame contract.

## Licensing and dependency footprint

- Gazebo (`gz-sim`, `gz-sensors`, `gz-transport`) is **Apache License 2.0**, confirmed
  across the `gazebosim` GitHub organization — compatible with Siqoq's own Apache 2.0
  license.
- Dependency footprint is **not pip-installable in isolation**. It requires either:
  - a full Gazebo installation (system packages/apt, or a container) running an actual
    simulation process, plus `gz-transport` Python bindings to subscribe from Python; or
  - a full ROS 2 installation plus the `ros_gz` bridge packages, if going through
    `sensor_msgs/msg/Image` instead of raw `gz.msgs.Image`.
- Confirmed in this environment: Gazebo/ROS 2 are not installable here, matching the
  issue's stated constraint. No commands were run against a live Gazebo instance; this
  evaluation is based on documentation only.

## Can this remain fully optional?

Yes. Structurally this is the same shape as the planned ROS 2 bridge (#9) and the
existing physical-camera adapters: an adapter module that:

- is only imported when explicitly selected (e.g. via config/entry point), never at
  package import time,
- has its extra dependencies (`gz-transport` Python bindings, or `ros_gz` + ROS 2) declared
  as an optional extra (e.g. `pip install siqoq[gazebo]`), not a base dependency,
  and
- is excluded from the default `make verify` path — `make verify` continues to prove
  only Ruff/pytest/build on the base install, not any Gazebo/ROS 2 behavior.

This preserves the "laptop-only base install" guarantee in `AGENTS.md` and
`docs/architecture.md` (simulation-first, hardware/simulator optional and replaceable).

## Recommendation

**Adopt later, behind an optional adapter.** Reasoning:

- The `SensorAdapter`/`FrameSensor` contracts already generalize cleanly to a Gazebo
  source; no contract change is needed to accommodate it later.
- No current Siqoq milestone needs simulator-grade physics/rendering — the MVP's
  "simulated camera" need is already served by `GeneratedSensorAdapter` and recorded
  fixtures at far lower dependency cost.
- Gazebo/ROS 2 cannot be installed or exercised in this environment today, so adopting
  now would ship an untested adapter with no CI coverage.
- The dependency (a whole simulator process, plus either `gz-transport` bindings or a
  ROS 2 stack) is heavy enough that it must never become part of the base install path.

**Do not adopt now; do not rule out.**

## Next steps if/when adopted

1. Decide transport path first: raw `gz-transport` (lighter, no ROS 2 needed) vs.
   `ros_gz_bridge`/`ros_gz_image` (heavier, but reuses the ROS 2 bridge work already
   planned for #9 — natural to build them together if the ROS 2 path is chosen).
2. Add `siqoq.adapters.gazebo` (or similar) implementing `SensorAdapter`/`FrameSensor`
   with `gz-transport`/`ros_gz` types fully contained inside the module.
3. Declare an optional extra (e.g. `siqoq[gazebo]`) so the base install stays untouched.
4. Add a CI job that only runs when a Gazebo/ROS 2 runtime is available (self-hosted
   runner or container image), separate from the default laptop-only `make verify` gate.
5. Add conformance tests reusing the existing `SensorAdapter`/`FrameSensor` test suite
   (`tests/test_sensors.py`-style) against the new adapter, run only in that gated job.
6. If `ros_gz_bridge` is chosen, coordinate directly with the Phase 4 ROS 2 bridge
   effort (#9) since both would share the ROS 2 dependency and bridge infrastructure.
