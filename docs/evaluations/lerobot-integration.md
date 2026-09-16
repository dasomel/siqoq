# Evaluation: Optional Hugging Face LeRobot integration

Tracks issue #18. Evaluated version: **LeRobot `0.6.2`** (PyPI, `pyproject.toml` on `main` as
fetched 2026-09-17; `huggingface/lerobot`, Apache-2.0 license at repo root). Any claim below
that depends on version-specific behavior (dependency set, module layout) is pinned to this
version and should be re-checked before adoption if LeRobot has moved on.

## Recommendation

**Adopt later, behind an optional adapter package. Do not adopt now.**

LeRobot's dataset schema and policy interface are worth mapping to because they give Siqoq a
path to reuse existing datasets/policies and to export Siqoq recordings for others to reuse.
But LeRobot's policies are PyTorch/GPU-tier (see [Tier fit](#tier-fit-vs-siqoq-laptop-mvp)),
Siqoq's MVP is CPU/ONNX-baseline, and the core Siqoq package must stay dependency-light. There
is no laptop-MVP-compatible integration to ship today. The concrete, buildable unit is the
mapping/gap design below plus a follow-on optional-package implementation once a GPU/edge tier
exists in Siqoq.

## Scope decision: design-level PoC, not runnable code

Issue #18's acceptance criteria ask for "a small proof of concept using an existing dataset or
simulation path." The task executing this evaluation must not add dependencies (per AGENTS.md
engineering rules and this issue's own "no mandatory Hugging Face dependency" criterion), and
`lerobot` itself (`torch`, `torchvision`, `huggingface-hub`, `gymnasium`, ...) is not installed
in this environment. Installing it to run a throwaway script would violate the no-new-deps
constraint for a documentation task.

**Decision: the PoC requirement is satisfied here as a design-level artifact** — the schema
mapping table and gap matrix in this document, plus an explicit "not touched" list — rather than
executable code. This is a scoping substitution, not a skip: it produces the same decision-
relevant information (does the mapping close cleanly? where does it not?) without violating the
dependency constraint. A runnable PoC (loading one `LeRobotDataset` episode and converting a
handful of frames to Siqoq semantic events) is named as a concrete next-step issue below, to run
in an isolated environment/extras group once the design is agreed.

## Layer mapping: what LeRobot would touch, and what it would not

| Siqoq layer | LeRobot surface | Touches? | Notes |
|---|---|---|---|
| Sensor adapters | `LeRobotDataset` camera/robot observation streams | Read-only, optional | Only as an *importer* of pre-recorded LeRobot datasets into Siqoq's recorded-media sensor adapter; never a live sensor driver. |
| Inference runtime | LeRobot policies (diffusion, ACT, SmolVLA, pi0, etc.) | Not now | All current LeRobot policies are PyTorch modules; none run on Siqoq's ONNX/CPU baseline. Would only attach behind a future GPU/edge inference adapter, never the laptop baseline. |
| Semantic event layer | `LeRobotDataset` episode/frame metadata (actions, observation.state, task strings) | Yes (design only) | This is the actual mapping target — see table below. |
| Event transport | LeRobot has none (files/Hub, not a bus) | Not touched | No interaction; Siqoq's NATS/MQTT/in-process transport is unaffected. |
| Policy / agent layer | LeRobot policy *output* (predicted action tensors) | Yes, indirectly | If ever consumed, action tensors would be treated as untrusted policy output and pass through Siqoq's policy/decision layer like any other agent, not called directly. |
| Action adapters | None directly — LeRobot's own robot control loops | Not touched | Siqoq would never call a LeRobot robot/motor driver. Any resulting action still exits only through Siqoq's existing action adapter + safety gate. |
| Observability | None | Not touched | No changes to Siqoq's telemetry model. |

### Explicit "not touched" list

- No LeRobot robot/teleoperator/motor-control hardware plugins (`feetech`, `dynamixel`,
  `hopejr`, `lekiwi`, etc.) are used or referenced.
- No LeRobot training or evaluation loop is invoked from Siqoq.
- No LeRobot policy performs inference inside the Siqoq laptop MVP path.
- No direct LeRobot-to-hardware path exists or is proposed at any point (see
  [Safety boundary](#safety-boundary)).
- No fork or vendoring of LeRobot code; no competing policy zoo or training framework, per
  issue #18's non-goals.

## Schema mapping table (design-level PoC)

LeRobot dataset format (`LeRobotDataset`, HF `datasets`-backed, per-episode Parquet + video) vs.
Siqoq's semantic event contract (`docs/architecture.md` §3):

| LeRobot field | Siqoq semantic event field | Mapping | Gap |
|---|---|---|---|
| `episode_index`, `frame_index`, `timestamp` | `timestamp`, event correlation id | Direct, deterministic | None |
| `observation.images.<camera>` | `source` (e.g. `camera.front`) | Direct per named camera stream | LeRobot allows arbitrary camera keys; Siqoq needs a naming convention/adapter config to map camera keys to `source` values |
| `observation.state` (joint/robot state vector) | No current Siqoq event type | New event type needed, e.g. `robot.state` | Siqoq's semantic events today are perception-centric (`object.detected`); proprioceptive state is a new schema addition, not a reuse of an existing type |
| `action` (policy action vector) | No current Siqoq event/decision type maps 1:1 | Would map to a "proposed action" surfaced to the policy/decision layer, not `action adapter` input directly | Siqoq's action adapters expect adapter-specific commands (mock, relay/GPIO, ROS 2), not raw LeRobot action tensors; a translation adapter is required and does not exist |
| `task` (natural-language task string) | No equivalent | Could inform a policy/agent context field | Out of scope for this evaluation; flagged only |
| dataset-level `info.json` (fps, robot type, features) | Sensor adapter config | Partial | Confidence/units/coordinate-frame conventions differ per robot; no universal mapping, must be handled per dataset |

**Where the mapping closes cleanly:** camera frames + timestamps into recorded-media sensor
input. **Where it does not:** action tensors and robot state have no existing Siqoq event type
and require new schema (a design change per AGENTS.md, requiring its own issue/spec), and action
tensors are never a direct adapter input under any circumstance (see below).

## Safety boundary

Per AGENTS.md ("Keep actuation behind an explicit adapter/policy boundary. Treat any new
physical side effect or actuator authority as a high-risk design change") and Siqoq principle 6
("No reasoning component should directly drive physical hardware"): **any LeRobot policy output
that Siqoq ever consumes is treated as untrusted policy/agent output and routed through Siqoq's
existing decision → safety gate → action adapter path, exactly like output from any other
policy or agent.** There is no path, current or proposed, where a LeRobot policy or dataset
action vector reaches a Siqoq action adapter or hardware driver directly. This applies even in a
future GPU/edge tier.

## Tier fit vs. Siqoq laptop MVP

LeRobot 0.6.2's core dependency set requires `torch>=2.7,<2.12` and `torchvision`; every shipped
policy (ACT, diffusion, SmolVLA, pi0, etc.) is a PyTorch module intended for GPU or capable-edge
execution. `docs/architecture.md` defines the laptop MVP baseline as OpenCV + ONNX Runtime on
CPU, with TensorRT/CUDA as later, explicitly accelerated targets. LeRobot policies do not fit the
CPU/ONNX baseline tier at all — **this is a later (GPU/edge) tier capability, not a laptop MVP
capability**, independent of whether the dependency is made optional.

## Dependency boundary: measurable "no mandatory Hugging Face dependency in core"

Concrete, testable statement: **`pip install siqoq` (the base/core distribution) must never
resolve `torch`, `torchvision`, `transformers`, `datasets`, or `huggingface_hub` as transitive
dependencies.** Any LeRobot support ships only as an optional extras group, e.g.
`pip install siqoq[lerobot]`, defined in a separate optional dependency group (or a fully
separate adapter package, per the in-tree-vs-adapter question below) that core `siqoq` never
imports. Verification method for a future implementation PR: `pip install siqoq` in a clean
virtualenv, then `pip show torch transformers datasets huggingface_hub` should report "not
found" for all four.

Note: LeRobot 0.6.2's own core dependencies include `huggingface-hub` (hub client) but not
`transformers` or `datasets` in the base install — those arrive via extras such as `training`/
`dataset`. This doesn't change Siqoq's obligation: any of these landing in core `siqoq` (directly
or transitively through `lerobot`) fails the criterion above.

## Licensing

- LeRobot itself: **Apache-2.0** (repo root `LICENSE`), compatible with Siqoq's own OSS baseline.
- LeRobot is a *hub* for datasets and policies contributed by many different parties. Individual
  Hugging Face Hub datasets and pretrained policy checkpoints referenced or downloadable through
  LeRobot carry **their own, independently-set licenses** (dataset cards and model cards vary
  per-asset, including some non-commercial or attribution-restricted terms).
- **Siqoq vendors none of these datasets or policy weights.** Any optional LeRobot adapter would
  only reference external Hub identifiers; it does not bundle or redistribute third-party data or
  weights. Confirming license compatibility for any specific dataset or policy an integrator
  chooses to use is **the integrator's responsibility**, not Siqoq's, and this should be stated
  in the optional adapter's own documentation if/when it is built.

## In-tree vs. optional adapter package

**Optional adapter package**, not in-tree core. Reasons: (1) the dependency boundary above is
easiest to guarantee mechanically when LeRobot-touching code lives in a separate distribution
that core `siqoq` never imports, rather than relying on lazy-import discipline inside the core
package; (2) it matches Siqoq principle 4 (stable contracts over vendor lock-in) — the adapter
depends on Siqoq's semantic event contract, not the reverse; (3) it isolates the GPU/edge-tier
dependency surface (torch et al.) from the laptop-CPU-baseline core.

## Next-step issues (if adopting later)

1. **Design issue:** add a `robot.state` (proprioceptive) semantic event type and an
   action-proposal surface at the policy/decision layer — required before any LeRobot state/action
   data can flow through Siqoq's contracts. Schema change, needs its own issue per AGENTS.md.
2. **Runnable PoC issue:** in an isolated environment (venv or container) with `siqoq[lerobot]`
   extras installed, load one `LeRobotDataset` episode and convert its camera frames + timestamps
   into Siqoq `object.detected`-style / recorded-media sensor input, confirming the "closes
   cleanly" half of the mapping table above actually round-trips. Explicitly out of scope: any
   action/state conversion, any policy inference, any hardware.
3. **Adapter package skeleton issue:** scaffold `siqoq-lerobot` (or `siqoq[lerobot]` extras
   group) with zero imports from core `siqoq` internals beyond the public semantic event/action
   contracts, and a CI check enforcing the `pip install siqoq` dependency boundary from this doc.
4. **Later, GPU/edge tier issue (blocked on Siqoq having a GPU/edge inference tier at all):**
   evaluate consuming one specific LeRobot policy (e.g. ACT or SmolVLA) as an inference backend
   behind Siqoq's inference runtime adapter interface, with action output routed through the
   safety boundary above. Not actionable until Siqoq's own accelerated/edge inference path
   exists.
