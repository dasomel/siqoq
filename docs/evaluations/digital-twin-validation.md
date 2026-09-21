# Evaluation: Digital-Twin Validation Concepts Spike

Tracks: #68 (part of #11). Related: #7 (Simulation Adapter Contract v0), #20 (scenario and benchmark catalog), #58 (declarative workload specification), #59 (edge fleet inventory), #60 (workload placement), #62 (GitOps deployment flow).

> **Explicit Statement:**
> **No formal digital-twin platform is implemented, executed, or verified in this repository.**
> No digital-twin daemon, real-time device shadow service, or vendor simulation engine (such as NVIDIA Omniverse or AWS IoT TwinMaker) exists in this environment. Everything below is a conceptual and architectural evaluation of how digital-twin validation patterns apply to Siqoq using its existing simulation-first building blocks, without introducing new hardware, vendor platforms, or premature tooling.

## Goal

Evaluate what "digital-twin validation" means for Siqoq: using a simulated environment to validate a workload or software change before it reaches physical hardware, without implementing a full-blown digital-twin platform. Specifically, evaluate how Siqoq's existing simulation-first architecture provides the conceptual building blocks, identify the technical gaps required to validate specific deployment targets, and establish a clear adoption recommendation.

## Background: Digital-Twin Validation in Robotics and Physical-AI

In robotics and cyber-physical systems, a **digital twin** is a virtual model that mirrors the state, capabilities, configuration, and operating environment of a physical device or system.

In continuous integration and continuous deployment (CI/CD) pipelines for physical AI, **digital-twin validation** serves as a pre-hardware verification gate:

1. **Target-Aware Simulation**: A candidate software release (new model weights, updated perception pipeline, modified policy, or revised configuration) is executed against a simulation configured to match the target device's profile and operating environment.
2. **Outcome Comparison (Shadow / Baseline Parity)**: The outputs (semantic events, action decisions, trajectory commands, safety gate triggers, latency bounds) produced by the simulated twin are compared against historical baselines or "last-seen" operational telemetry from the real device.
3. **Pre-Hardware Safety Gate**: If the simulated twin produces unexpected actions, violates safety constraints, or diverges from baseline event sequences, the deployment is blocked before it can cause physical damage, actuator faults, or operational outages on actual hardware.

This pattern shifts physical validation left, bridging the "sim-to-real" gap while keeping physical hardware out of the inner loop of CI.

## What Digital-Twin Validation Means for Siqoq (Grounded in Existing Assets)

Siqoq's core architecture was designed simulation-first from day one (`AGENTS.md`): software paths must be developable and verifiable on a laptop without physical hardware. Rather than requiring external digital-twin software, Siqoq already contains the core primitives that make a lightweight digital-twin validation pattern conceptually viable:

### 1. `GeneratedSensorAdapter` and Simulation Provenance
In `src/siqoq/sensors.py`, `GeneratedSensorAdapter` acts as Siqoq's reference synthetic source. It satisfies the `SensorAdapter` protocol while emitting `SemanticEvent`s tagged with `provenance: "simulated"` (`PROVENANCE_SIMULATED`). 

Crucially, when supplied with an explicit `timestamp` parameter, `GeneratedSensorAdapter` is 100% deterministic and byte-for-byte reproducible across independent runs and machines (`tests/test_sensors.py`). In a digital-twin context, this provides the virtual sensor generator that models expected perception input without physical cameras.

### 2. Simulation Adapter Contract v0
`docs/specs/simulation-adapter-contract.md` formalizes what distinguishes simulated sources from recorded or physical sensors:
- **Strict Determinism**: For identical configuration and `read(count=N)`, simulated adapters yield identical event sequences.
- **Wall-Clock Isolation**: Wall-clock time is strictly isolated from `sequence_hash` and regression comparisons.
- **Simulator SDK Isolation**: Underlying simulation mechanics (whether internal generators or future engines like Isaac Sim or Gazebo) are confined behind `SensorAdapter`, never leaking vendor SDK types into `SemanticEvent` signatures.

This ensures a digital-twin simulation is safe to run in automated pipelines without flaky timing dependencies or vendor lock-in.

### 3. Scenario and Scene Catalog
`docs/specs/scenario-catalog.md` and `tests/test_scenario_catalog.py` (with fixtures in `examples/scenarios/`) provide the scenario execution and outcome capture harness:
- Scenarios bundle `ScenarioConfig` files with expected pass/fail outcomes, event counts, and safety constraints.
- Named, versioned **scenes** (`kind: "scene"`, `version: "1.0.0"`) represent standardized virtual environments (e.g. `scene-single-object`, `scene-multi-step-sequence`).
- Execution produces a `ScenarioSummary` capturing deterministic metrics: `event_count`, `type_counts`, `action_counts`, and a SHA-256 `sequence_hash` over emitted events.
- Deterministic error and safety paths (`sensor-disconnect`, `inference-fallback-on-bad-input`, `action-rejected-by-safety-gate`) allow testing edge cases that would be dangerous or difficult to induce on physical hardware.

### 4. Workload Specs and Capability Matching
- `WorkloadSpec` (`docs/specs/workload-spec.md`, `src/siqoq/workload.py`) declaratively binds a scenario configuration to required device capabilities (`RuntimeCapabilities`).
- `FleetInventory` and `FleetEntry` (`src/siqoq/fleet.py`, issue #59) maintain snapshots of node capabilities (`vision_extra_available`, `gpu_probe_tool_available`, OS, architecture) and `last_seen` timestamps.
- `placement.place()` (`src/siqoq/placement.py`, issue #60) deterministically filters eligible nodes based on these capabilities.

Together, these components provide:
- A virtual perception generator (`GeneratedSensorAdapter`)
- A deterministic simulation execution harness (`ScenarioCatalog`)
- A standardized outcome format (`ScenarioSummary`)
- A declarative representation of target node capabilities (`FleetEntry` / `RuntimeCapabilities`)

In Siqoq, a "digital twin" is not a heavyweight 3D visual avatar; it is a **deterministic, capability-bounded virtual execution of the perception-policy loop running against simulated sensor contracts**.

## The Gap: Validating a Specific Real Deployment Target

While the foundation exists, Siqoq's current simulated scenarios are **generic**: they test whether code works against a synthetic fixture in the abstract, not whether a change will behave correctly on a **specific real node** (e.g. `node-jetson-01` vs `node-laptop-02`).

To elevate an existing simulated scenario run to true "digital-twin validation" of a specific target, four distinct technical gaps must be bridged:

### 1. Binding Scenario Configuration to Fleet Node Capabilities
Currently, scenario configs (`examples/scenarios/*.json`) are static documents. `WorkloadSpec.validate_against(node.capabilities)` provides a boolean gating check (is this workload satisfiable on this node?), but it does not parameterize the simulation to mirror that node's real operational constraints.
- **The Gap**: A target-aware binding mechanism. To validate a workload for a specific node in `FleetInventory`, the simulation harness would need to configure the simulated adapter using that node's recorded profile — for example, matching the node's camera resolution, configured inference adapter type (`MockInferenceAdapter` vs `OnnxCvInferenceAdapter`), available hardware acceleration, and transport options.

### 2. Node Execution Baseline and Telemetry Ingestion
In `src/siqoq/fleet.py`, `FleetEntry` stores only static metadata:
```python
@dataclass(slots=True, frozen=True)
class FleetEntry:
    node_id: str
    capabilities: RuntimeCapabilities
    last_seen: str
```
- **The Gap**: `FleetEntry` contains no operational history, run records, or telemetry snapshots. A digital twin cannot validate a change against "that node's actual last-seen real results" because those results are nowhere in the data model.
- **What is Needed**: A mechanism to ingest and store node execution baselines (e.g. a `last_run_summary: ScenarioSummary` or recorded telemetry digest) containing baseline `sequence_hash`, `action_counts`, event distributions, or recorded input fixtures captured during actual on-device runs.

### 3. Twin-vs-Real Outcome Comparator
`test_scenario_catalog.py` currently compares a run's `CatalogResult` against static assertions defined in `catalog.json` (`expected_outcome: "success"`, `min_event_count: 3`).
- **The Gap**: An outcome comparator that takes two `ScenarioSummary` objects — the candidate twin run and the target node's real baseline — and evaluates parity:
  - **Action Invariance**: Did the candidate workload trigger identical policy actions and safety gate decisions (`action_counts`) as the real baseline?
  - **Event Parity**: Did the simulated event sequence match expected event types and ordering, or did safety-critical detections drop below baseline thresholds?
  - **Contract Conformance**: Did the candidate violate any invariants enforced on the real device?

### 4. Integration into Pre-Deployment Gating
Currently, scenarios run via `siqoq scenario run` or `pytest`.
- **The Gap**: A deployment workflow hook. In `docs/specs/gitops-deployment-flow.md` (#62), rollout is modeled as updating a node's WorkloadSpec digest in Git. Digital-twin validation would serve as the automated gate: before committing a digest change for `node-jetson-01`, CI runs the candidate workload against `node-jetson-01`'s twin configuration, compares the result to `node-jetson-01`'s baseline, and approves or aborts the rollout.

## Evaluation of Adoption Options

### Option 1: Adopt-Now (as a documented pattern reusing existing tools, no new code)
- **Concept**: Document how developers can author a `ScenarioConfig` mirroring a target node's expected input, validate it with `siqoq workload validate`, run it via `siqoq scenario run`, and manually inspect `ScenarioSummary.to_json()` before updating physical devices.
- **Pros**: Zero code, zero new dependencies, immediate conceptual guidance for manual testing.
- **Cons**: Calling manual scenario execution "digital-twin validation" is misleading. Without node-bound parameterization or automated comparison against real telemetry baselines, it is simply manual unit/scenario testing. It risks introducing buzzword inflation into a codebase that values strict, verified claims.

### Option 2: Adopt-Later (needs new tooling and code)
- **Concept**: Formally schedule digital-twin validation tooling for Phase 5 (Fleet mode), after physical edge deployments, telemetry ingestion, and real node baselines exist.
- **Pros**:
  - Respects OpenForge and `AGENTS.md` principles: "Make the smallest coherent change that solves the requested problem", "Do not introduce fleet/GitOps complexity before the single-node/software-first path needs it."
  - Avoids building speculative comparison tooling when there are no real physical nodes reporting telemetry.
  - Aligns with the planned evolution of `FleetInventory` (#59), workload placement (#60), and GitOps rollouts (#62).
- **Cons**: Defers automated twin validation until edge deployment infrastructure matures.

### Option 3: Do-Not-Adopt
- **Concept**: Permanently reject digital-twin validation as out of scope for Siqoq.
- **Pros**: Minimal scope.
- **Cons**: Unjustified. Siqoq is explicitly a physical-AI runtime. Validating changes on simulated models before triggering physical actuators or edge deployments is core to the project's long-term safety and simulation-first vision.

## Recommendation: adopt-later

**Recommendation: adopt-later (needs new tooling and code).**

Reasoning:
1. **Premature at Single-Node / Bootstrap Phase**: Siqoq is currently validating its single-node core contracts (`SensorAdapter`, `FrameSensor`, `InferenceAdapter`, `Policy`). The fleet inventory (`src/siqoq/fleet.py`) and placement logic (`src/siqoq/placement.py`) are lightweight in-process fixtures without real network or device connections. Building an automated digital-twin validation engine before real nodes exist would violate `AGENTS.md`'s prohibition against premature fleet complexity.
2. **Missing Telemetry Feedback Loop**: True digital-twin validation requires comparing simulated runs against real on-device telemetry. `FleetEntry` currently has no telemetry storage, and `src/siqoq/telemetry.py` provides only optional OpenTelemetry hooks. Building a comparator before having real node telemetry to compare against would result in unverified, speculative code.
3. **Existing Scenarios Already Protect CI**: For current development, the existing scenario catalog (`docs/specs/scenario-catalog.md`) and deterministic fixtures already provide robust regression protection in CI without needing the "digital twin" label.
4. **Not Rejected (Not Do-Not-Adopt)**: The architectural alignment is strong. The combination of `GeneratedSensorAdapter`, deterministic `sequence_hash`, declarative `WorkloadSpec`, and `FleetInventory` means Siqoq will not need to rewrite its architecture to support digital-twin validation when multi-node fleets are deployed.

## Revisit Conditions and Next Steps (When Adopted Later)

Revisit when:
1. **Real Fleet Telemetry Ingestion Exists**: Real edge nodes are reporting runtime metrics or execution summaries back to a fleet record (e.g. extending `FleetEntry` or telemetry storage with `last_seen_summary` or event traces).
2. **GitOps Rollout Controller is Implemented**: The deployment flow outlined in `docs/specs/gitops-deployment-flow.md` is implemented, creating a concrete need for a pre-rollout validation gate.
3. **High-Fidelity Simulator Adapters are Available**: When optional simulation bridges (e.g. Isaac Sim per `docs/evaluations/isaac-sim-integration.md` or Gazebo per `docs/evaluations/gazebo-integration.md`) provide sensor streams calibrated to specific physical camera/lens setups.

### Implementation Steps When Reopened:
1. **Telemetry Store Extension**: Add an optional execution summary record to `FleetEntry` (e.g. storing `baseline_summary: ScenarioSummary` or reference event hashes from the node's last healthy deployment).
2. **Node-Bound Scenario Parameterizer**: Add a helper (`siqoq.scenario.bind_to_node(scenario_config, fleet_entry)`) that tunes scenario parameters (frame rate, resolution, model selection) to match the node's `RuntimeCapabilities`.
3. **Outcome Comparator Utility**: Implement a deterministic diffing utility (e.g. `siqoq.scenario.compare_summaries(twin_summary, baseline_summary)`) that evaluates action equivalence, safety gate compliance, and event sequence compatibility.
4. **Pre-Rollout Gating Hook**: Wire the comparator into CI or the GitOps reconciler to block rollout commits if twin validation fails.
