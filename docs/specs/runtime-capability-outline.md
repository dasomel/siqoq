# Runtime/Capability Contract Outline

Status: outline only. No runtime registry, discovery mechanism, or
enforcement exists yet in the codebase; this document describes the shape
a future capability declaration could take, so Sensor/Semantic
Event/Action Contract v0 consumers have a shared vocabulary for what a
given runtime supports. Do not build enforcement against this outline
without a follow-up issue — see AGENTS.md's "smallest coherent change" and
"avoid prematurely hardening" rules.

## Motivation

`docs/architecture.md`'s deployment modes table (Laptop / Simulation / Edge
/ Fleet) already implies each mode supports a different subset of
sensor/inference/transport/action adapters. A capability declaration would
let a runtime state this explicitly instead of callers probing by trial and
error (e.g. catching `NotImplementedError` from `UsbWebcamFrameSensor`).

## Sketch (illustrative, not implemented)

A runtime capability declaration would be a small, additive, pure-data
structure, e.g.:

```python
@dataclass(slots=True, frozen=True)
class RuntimeCapabilities:
    supports_fixture_sensors: bool = True
    supports_generated_sensors: bool = True
    supports_physical_sensors: bool = False
    supports_mock_actuation_only: bool = True   # mirrors Action Contract v0 "mock" review
    supports_onnx_inference: bool = False
    supports_transport: tuple[str, ...] = ("in_memory", "stdout", "file")
```

Each field maps to an existing contract concept already in this codebase
(Sensor Contract v0 layers, Action Contract v0's `mock` field, transport
adapters in `siqoq.transport`) rather than inventing new categories.

## Example declarations by deployment mode

| Mode | fixture sensors | generated sensors | physical sensors | mock-only actuation | onnx inference | transport |
|---|---|---|---|---|---|---|
| Laptop | yes | yes | no | yes | optional | in_memory/stdout/file |
| Simulation | yes | yes | no | yes | optional | pluggable |
| Edge | yes | no | yes | policy-dependent | yes | nats/mqtt |
| Fleet (planned) | yes | no | yes | policy-dependent | yes | managed messaging |

This table is descriptive today (matches deployment modes in
`docs/architecture.md`), not something any code currently reads or
enforces.

## Non-goals (for this issue)

- No runtime registry, plugin discovery, or capability-negotiation
  protocol is added here.
- No existing adapter is required to implement `RuntimeCapabilities`.
- This outline does not gate CI or `make verify`.

A follow-up issue should scope: where capabilities are declared (per-
adapter class attribute vs. a runtime-level object), how `mock-only
actuation` interacts with `SafetyGate`, and whether capability mismatches
should fail fast or degrade gracefully.
