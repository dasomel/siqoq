# Declarative Workload Specification (issue #58)

Status: implemented (`siqoq.workload.WorkloadSpec`).

A workload spec is a small, portable, declarative JSON document describing
one unit of work to run on a node: which scenario to run, resource hints,
and the runtime capabilities the node must have. It reuses
`siqoq.scenario.ScenarioConfig` (issue #24) for "what to run" and
`siqoq.capabilities.RuntimeCapabilities` (issue #45) for "what this node can
do" instead of inventing parallel formats for either concern.

Kubernetes is not required to author, validate, or run a workload spec: it
is authored as a plain JSON file and validated/run with the `siqoq` CLI or
the `siqoq.workload` module directly, on a laptop exactly as it would be (in
principle) on any edge profile whose `RuntimeCapabilities` match.

## Fields

```python
@dataclass(slots=True, frozen=True)
class WorkloadSpec:
    name: str
    scenario_config_path: str
    required_capabilities: dict[str, bool]
    resource_hints: dict[str, Any] | None = None
```

- `name: str` — a human-readable identifier for the workload.
- `scenario_config_path: str` — path to a `ScenarioConfig` JSON file (see
  `docs/specs/scenario-fixtures.md`). Resolved as given (relative to the
  current working directory, matching `ScenarioConfig.from_json`'s own
  convention); the workload spec does not reinvent scenario configuration.
- `required_capabilities: dict[str, bool]` — a subset of
  `RuntimeCapabilities.to_dict()`'s boolean keys (e.g.
  `vision_extra_available`, `transport_nats_available`,
  `transport_mqtt_available`, `observability_extra_available`,
  `gpu_probe_tool_available`) that must equal the given boolean on the
  target node. A key not present in `RuntimeCapabilities` is itself reported
  as an unsatisfiable reason, never silently ignored.
- `resource_hints: dict[str, Any] | None` — free-form, e.g.
  `{"min_memory_mb": 512}`. **Advisory only**: nothing in this format
  enforces resource hints; they exist for a human or a future scheduler to
  read, not for `validate_against` to check.

## Example

`examples/workloads/fixture_detection_workload.json`:

```json
{
  "name": "fixture-detection-laptop",
  "scenario_config_path": "examples/scenarios/fixture_detection.json",
  "required_capabilities": {
    "vision_extra_available": false
  },
  "resource_hints": {
    "min_memory_mb": 512
  }
}
```

## Validation

`WorkloadSpec.validate_against(capabilities: RuntimeCapabilities) -> list[str]`
returns an empty list when the spec is satisfiable, or a list of explicit,
actionable reasons otherwise (one per mismatched or unknown key) — a
capability mismatch is always a stated reason, never a silent no-op.

## CLI

```
siqoq workload validate --spec examples/workloads/fixture_detection_workload.json
```

Prints JSON to stdout, e.g. (pass case, on a CPU-only laptop):

```json
{
  "name": "fixture-detection-laptop",
  "satisfiable": true,
  "reasons": []
}
```

Fail case (spec requires `vision_extra_available: true` on a node without
the vision extra installed):

```json
{
  "name": "needs-vision",
  "satisfiable": false,
  "reasons": [
    "required capability 'vision_extra_available' is False on this node (needed: True)"
  ]
}
```

## Compatibility rules

- **Breaking**: removing/renaming a `WorkloadSpec` field, or changing
  `validate_against`'s meaning of an empty list.
- **Compatible / additive**: adding a new optional field with a default, or
  adding new `RuntimeCapabilities` fields that specs may reference.

## Non-goals (for this issue)

- No scheduler, node registry, or capability-negotiation protocol.
- `resource_hints` is never enforced.
- No Kubernetes manifest generation.
