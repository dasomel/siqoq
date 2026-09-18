# Evaluation: ROS 2 bridge integration spike

Tracking: #54 (part of #9). Related: #51 (prospective `ActionResult`/actuator
adapter contract — may not exist in this worktree yet; referenced here only
to describe the mapping, not implemented or depended on).

**No ROS 2 capability has been implemented, run, or verified anywhere in
this repository.** ROS 2 requires a full system-level distro install, not
available in this environment. Everything below is a design evaluation based
on public `rclpy`/ROS 2 documentation, not on running any ROS 2 node,
publisher, subscriber, or bridge against this codebase.

## Goal

Evaluate what a ROS 2 bridge would require to carry Siqoq's semantic events
and (future) action results across a ROS 2 graph, without adding the
dependency now and without implying ROS 2 becomes a required core
dependency.

## rclpy background

`rclpy` is ROS 2's Python client library, distributed per-distro (Humble,
Jazzy, Kilted, Rolling, …) as part of a full ROS 2 install — not a standalone
`pip` package for most Linux distros (some Rolling/experimental wheels exist
but are not the mainstream install path). A minimal ROS 2 Python program:

- creates an `rclpy.node.Node`
- calls `node.create_publisher(MsgType, topic, qos)` /
  `node.create_subscription(MsgType, topic, callback, qos)`
- messages are typed classes generated from `.msg`/`.srv` IDL files (e.g.
  `std_msgs/String`, `vision_msgs/Detection2DArray`, custom `.msg` packages)
- `rclpy.spin(node)` runs the executor loop

Sources: [rclpy — ROS Package Overview](https://index.ros.org/p/rclpy/), [Writing a simple service and client (Python) — ROS 2 Jazzy docs](https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Service-And-Client.html), [Client libraries — ROS 2 Kilted docs](https://docs.ros.org/en/kilted/Concepts/Basic/About-Client-Libraries.html)

## Mapping to Siqoq's contracts

| Siqoq concept | ROS 2 equivalent | Direction |
|---|---|---|
| `SemanticEvent` (events.py) — `object.detected` etc. | A publisher on a detection topic, e.g. `/siqoq/semantic_events`, using either a generic message (`std_msgs/String` carrying `SemanticEvent.to_json()`) or a purpose-built custom message (`SemanticEvent.msg` mirroring `type`/`source`/`object`/`confidence`/`timestamp`/`schema_version`/`correlation_id`/`metadata`) | Siqoq → ROS 2 graph |
| Future `ActionResult` (per #51, not present in this worktree) | A subscription on an action/command topic, or a ROS 2 service/action server if request/response or long-running actuation semantics are needed | ROS 2 graph → Siqoq, or Siqoq → ROS 2 actuator node |
| `schema_version` / additive-only `to_json()` contract | Custom message versioning is coarser-grained (a new `.msg` file or field requires a package rebuild across all consumers) — this is a real mismatch, not just a translation detail | n/a |
| `correlation_id` | Carried as a message field or ROS 2's own message header/timestamp correlation, not a native ROS 2 concept | n/a |

A generic `std_msgs/String` + JSON payload is the lower-friction bridge: it
reuses `SemanticEvent.to_json()` unchanged and avoids owning a custom ROS 2
message package. A typed custom message gives ROS 2-native tooling (e.g.
`ros2 topic echo` with structured fields, `rqt` introspection) at the cost of
maintaining and versioning a separate IDL package in lockstep with the Python
dataclass — a second schema to keep additive-compatible.

## Adapter boundary

A `Ros2Bridge` class (name illustrative) would live outside
`events.py`/`policy.py`, e.g. `siqoq/adapters/ros2_bridge.py` or an optional
sub-package, and would own:

- the `rclpy` import and node lifecycle (`init`/`spin`/`shutdown`)
- publisher/subscription creation and QoS profile selection
- translation both ways: `SemanticEvent` → ROS 2 message on publish,
  ROS 2 message → Siqoq's own action/result type on receive

**What stays behind the boundary (must never leak into core):**

- `rclpy` itself and any `import rclpy` / `from rclpy...` statement
- Generated ROS 2 message classes (`std_msgs.msg.String`,
  `vision_msgs.msg.Detection2DArray`, any custom `.msg`-generated type)
- ROS 2 QoS profile objects, node/executor lifecycle management
- ROS 2-specific error types (`rclpy.exceptions.*`)

**What must never leak into `events.py` / `policy.py` (or a future
`scenario.py`):** no `rclpy` import, no ROS 2 message type in a function
signature or dataclass field, no ROS 2-specific exception handling. Those
modules continue to only know about `SemanticEvent` and the eventual
`ActionResult` — plain Python dataclasses with no transport awareness. This
mirrors the existing pattern in `docs/specs/action-contract.md`, where
`MockAction`/`decide()` have zero actuator-SDK imports; the same "no vendor
type in core contract signatures" check that already applies to
`sensors.py`/`events.py` extends to ROS 2 message types.

## Optionality: enforcement, not aspiration

Per issue #54's acceptance criterion and Phase 4, ROS 2 must remain optional,
never a required core dependency. Concretely, that means:

- **Lazy import**: `Ros2Bridge.__init__` (or a module-level factory) performs
  `import rclpy` inside the function/class, not at module top-level, so
  importing `siqoq` or any core module never touches `rclpy`.
- **Optional extra**: ROS 2-bridge dependencies (if any pure-Python glue is
  ever pip-installable) would be declared under an optional extras group
  (e.g. `pip install siqoq[ros2]`), never in the base `dependencies` list in
  `pyproject.toml`. In practice, because `rclpy` mainly ships via full ROS 2
  distro install rather than PyPI, the extras group would document the
  system-level prerequisite rather than pull it in via pip alone.
- **Verification**: `make verify` (Ruff, pytest, package build) must pass
  with zero ROS 2 installed — this is the enforcement mechanism, not a
  claim. This evaluation does not add the bridge, so `make verify` today is
  unaffected by ROS 2 either way; the requirement is what any future
  implementation PR must demonstrate before merge.

## Dependency footprint

- ROS 2 is not a simple `pip install` for most target distros — it is a
  full system-level install (apt repositories, a source workspace build via
  `colcon`, or a container image) providing the DDS middleware, message
  generation toolchain, and `rclpy` bindings together. This is a
  meaningfully heavier footprint than any other current or evaluated Siqoq
  dependency (NATS/MQTT clients, ONNX Runtime, TensorRT container layers).
- Distro/version considerations: ROS 2 ships named distros with defined EOL
  windows (Humble is the long-lived LTS-style release many production robots
  still target; Jazzy is the newer LTS-style release; Kilted/Rolling track
  newer development). A bridge implementation would need to pin a supported
  distro and track its EOL, similar to how `docs/evaluations/jetson-deployment-profile.md`
  pins an L4T/JetPack version rather than tracking "latest."
- No package manifest, container base image, or CI job in this repository
  currently references ROS 2, `rclpy`, or any `ros-*` package — this
  evaluation does not change that.

Sources: [rclpy — ROS Package Overview](https://index.ros.org/p/rclpy/), [Client libraries — ROS 2 Kilted documentation](https://docs.ros.org/en/kilted/Concepts/Basic/About-Client-Libraries.html)

## Recommendation: adopt-later

- **Not do-not-adopt**: `docs/architecture.md` already lists "ROS 2 bridge"
  as a potential action-adapter target, and the adapter boundary described
  above (an isolated `Ros2Bridge` translating to/from `SemanticEvent`/
  `ActionResult`) is compatible with the existing architecture without any
  core contract change.
- **Not adopt-now**: no ROS 2 install exists in this environment to build,
  run, or verify a bridge against; the prospective `ActionResult`/
  `ActuatorAdapter` contract this bridge would consume on the action side
  (per #51) does not exist in this worktree yet, so there is no stable
  action-side contract to bridge to today. Writing a `Ros2Bridge` now would
  be untested against real ROS 2 behavior and would risk being merged as if
  verified when it isn't.
- Revisit once: (a) #51's `ActionResult`/`ActuatorAdapter` contract lands,
  and (b) a ROS 2 install (container image or dev machine with a supported
  distro) is available for actual publish/subscribe verification, ideally
  against `ros2 topic echo`/a minimal listener node as the acceptance check.

## Explicit non-claim

No ROS 2 node, publisher, subscriber, bridge, or `rclpy` call has been
implemented, run, or verified in this repository as part of this evaluation
or any prior work. All statements above are derived from public ROS 2/`rclpy`
documentation, not from running anything on this repo's code.
