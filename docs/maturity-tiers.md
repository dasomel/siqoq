# Maturity Tiers (S0–S5) / 성숙도 단계 (S0–S5)

Siqoq adopts a staged maturity model inspired by the Microsoft Physical AI Toolchain's
T0–T5 graduated adoption path (laptop-first, no cloud/Kubernetes until justified, later
tiers add k3s/GitOps/fleet). Siqoq's version keeps a smaller, vendor-neutral scope and
uses the tier names `S0`–`S5` (not `T0`–`T5`) to avoid implying a 1:1 mapping to
Microsoft's toolchain.

Siqoq는 Microsoft Physical AI Toolchain의 T0–T5 단계적 도입 모델에서 영감을 받은 단계형
성숙도 모델을 채택한다. 랩톱에서 시작해 클라우드/쿠버네티스 없이 진행하고, 필요성이
입증된 뒤에야 k3s/GitOps/플릿 기능을 추가하는 원칙은 동일하지만, Siqoq는 더 작고
벤더 중립적인 범위를 유지하며 단계 이름도 `S0`–`S5`로 구분해 Microsoft 툴체인과의
1:1 대응을 암시하지 않는다.

**Hard rule / 원칙:** no tier requires infrastructure from a later tier. Each tier's
minimum requirements are satisfiable using only what earlier tiers already established
(laptop, then simulation, then optional edge/robot/fleet hardware). This is verified
tier-by-tier in the table below — every "Minimum requirements" row lists only
dependencies introduced at or before that tier.

어떤 단계도 이후 단계의 인프라를 전제로 하지 않는다. 각 단계의 "최소 요구사항"은 그
단계 또는 이전 단계에서 이미 확보된 것만으로 충족되어야 하며, 아래 표에서 이를
단계별로 확인할 수 있다.

## Tier table / 단계 표

| Tier | Name (EN) | 이름 (KO) |
|---|---|---|
| S0 | Laptop / generated & recorded data | 랩톱 / 생성·녹화 데이터 |
| S1 | Laptop / real USB sensor | 랩톱 / 실제 USB 센서 |
| S2 | Simulation / deterministic scenarios | 시뮬레이션 / 결정론적 시나리오 |
| S3 | Edge / Jetson, ARM, x86 | 엣지 / Jetson, ARM, x86 |
| S4 | Physical action / ROS 2, MCU, robot | 물리적 동작 / ROS 2, MCU, 로봇 |
| S5 | Fleet / GitOps, optional Kubernetes | 플릿 / GitOps, 선택적 쿠버네티스 |

## Per-tier detail / 단계별 상세

### S0 — Laptop / generated & recorded data (랩톱 / 생성·녹화 데이터)

- **Entry criteria / 진입 조건:** none — this is the starting tier. 시작 단계이므로 진입
  조건이 없다.
- **Minimum requirements / 최소 요구사항:** macOS/Linux laptop, Python environment from
  `pyproject.toml`, no camera or network hardware. Uses only recorded/generated inputs
  (see `src/siqoq/events.py` for the semantic event contract this tier must emit).
  랩톱과 Python 환경만 있으면 되고, 카메라나 네트워크 하드웨어는 불필요하다.
- **Demo command / 데모 명령:** `python -m siqoq.cli` (verify exact invocation against
  `src/siqoq/cli.py` before publishing a specific flag set — CLI surface is still
  evolving). 정확한 실행 인자는 `src/siqoq/cli.py`의 현재 구현을 확인해야 한다.
- **Exit / graduation criteria / 졸업 조건:** semantic events are emitted for
  generated/recorded input and covered by automated tests; ready to add a real sensor
  without changing the event contract. 생성·녹화 입력에 대해 시맨틱 이벤트가 발행되고
  테스트로 검증되면 다음 단계로 넘어간다.
- **Dependencies newly required / 신규 필수 의존성:** none beyond the Python baseline.
- **Verification note:** a green `make verify` proves this tier (pure software, no
  device). It does NOT prove S1+ hardware behavior.

### S1 — Laptop / real USB sensor (랩톱 / 실제 USB 센서)

- **Entry criteria:** S0 exit criteria met (stable semantic event contract on
  generated/recorded input).
- **Minimum requirements:** a USB/UVC webcam or similar USB sensor attached to the same
  development laptop; a sensor adapter that emits the same event schema as S0's
  generated/recorded path. This repo does not yet contain a merged USB sensor adapter in
  this worktree — status here is "not yet exercised," per AGENTS.md, not a claim of a
  working implementation. USB 웹캠 등 실제 USB 센서가 필요하며, 이 워크트리에는 아직
  병합된 USB 센서 어댑터가 없어 "아직 검증되지 않음" 상태다.
- **Demo command / example:** not yet exercised in this worktree — no committed
  USB-sensor CLI path to point to yet.
- **Exit criteria:** real USB sensor input produces the same semantic event shape as
  simulated/recorded input, with tests or manual evidence showing sensor-swap
  compatibility.
- **Dependencies newly required:** OS-level USB camera access (e.g., OpenCV `VideoCapture`
  against a device index) — no new network/cluster dependency.
- **Verification note:** `make verify` cannot prove USB camera behavior; requires
  physical-device evidence collected on a machine with the sensor attached.

### S2 — Simulation / deterministic scenarios (시뮬레이션 / 결정론적 시나리오)

- **Entry criteria:** S0 semantic event contract exists (S2 does not require S1; it is a
  parallel non-hardware path per `docs/architecture.md`'s "Simulation mode").
- **Minimum requirements:** deterministic scenario/fixture definitions that a simulated
  sensor adapter can replay without physical hardware or a simulator install being
  mandatory for CI. In this worktree, no merged `scenario.py`/simulation fixtures exist
  yet — treat as "not yet exercised."
- **Demo command / example:** not yet exercised in this worktree.
- **Exit criteria:** the same downstream pipeline consumes both simulated and
  recorded/real camera input without code changes (per Phase 2 / issue #7 acceptance
  criteria), and at least one deterministic scenario runs reproducibly (CI or documented
  local workflow).
- **Dependencies newly required:** none that require cloud or Kubernetes; a simulator
  (e.g., Isaac Sim/Gazebo) is an optional later integration per
  `docs/architecture.md` non-goals, not a required dependency for the deterministic
  fixture path.
- **Verification note:** `make verify` proves the deterministic-fixture path only if
  fixtures run in CI; it does not prove full simulator (Isaac Sim/Gazebo) integration.

### S3 — Edge / Jetson, ARM, x86 (엣지 / Jetson, ARM, x86)

- **Entry criteria:** S1 (real sensor path validated) and S2 (simulation/deterministic
  path validated) both met, per `docs/architecture.md`'s statement that the baseline
  runtime must work on a laptop before any accelerator-specific path is introduced.
- **Minimum requirements:** ARM64/x86 container build and a device capability discovery
  step; CPU baseline (OpenCV/ONNX Runtime) must keep working per Phase 3 / issue #8
  acceptance criteria. No Jetson-specific behavior is implemented in this worktree —
  kept conservative and stub-level per AGENTS.md.
- **Demo command / example:** not yet exercised in this worktree — no Jetson/ARM
  deployment bundle exists yet.
- **Exit criteria:** same semantic event contract works on laptop and edge hardware;
  edge-specific code isolated behind adapters/profiles; baseline CPU path continues to
  work; deployment and rollback steps documented (Phase 3 acceptance criteria, issue #8).
- **Dependencies newly required:** ARM64 container tooling, optional TensorRT adapter on
  Jetson. Still no cluster/Kubernetes dependency.
- **Verification note:** `make verify` runs on the development laptop's Python
  environment and proves none of this tier's device-specific behavior; Jetson/ARM/x86
  edge claims require evidence gathered on that actual hardware.

### S4 — Physical action / ROS 2, MCU, robot (물리적 동작 / ROS 2, MCU, 로봇)

- **Entry criteria:** S3 edge runtime validated (or bypassed only if actuation is tested
  against a non-edge host — not recommended; edge validation should precede physical
  actuation).
- **Minimum requirements:** a safety/policy gate in front of any actuator adapter (see
  `src/siqoq/events.py`/future policy module and `docs/architecture.md`'s "Action
  adapters" layer), plus a mock actuator adapter for CI. Real ROS 2/MCU/robot hardware is
  not present in this worktree — stub-level only, per AGENTS.md's actuation-as-high-risk
  guidance.
- **Demo command / example:** not yet exercised in this worktree; when implemented, a
  mock-actuator demo should run without any physical device attached, per Phase 4 /
  issue #9's mock-path requirement.
- **Exit criteria:** reasoning components never directly control hardware; mock path
  exists for CI/local testing; action requests/results observable and traceable; unsafe
  defaults avoided; ROS 2 remains optional, not a core dependency (Phase 4 acceptance
  criteria, issue #9).
- **Dependencies newly required:** ROS 2 bridge and MCU/GPIO adapters — both optional
  integrations, isolated behind the action-adapter boundary. No cluster/Kubernetes
  dependency.
- **Verification note:** `make verify` can prove the mock-actuator path only; it never
  proves real ROS 2/MCU/robot behavior. Any such claim requires evidence from real
  hardware runs.

### S5 — Fleet / GitOps, optional Kubernetes (플릿 / GitOps, 선택적 쿠버네티스)

- **Entry criteria:** S3 (single edge node stable) and S4 (safe actuation boundary
  validated on at least one node), per Phase 5 / issue #10's framing of fleet operation
  "after the single-node runtime is stable."
- **Minimum requirements:** declarative workload spec and GitOps deployment flow across
  multiple edge nodes; Kubernetes/K3s remains optional, only adopted if a single-node
  workflow proves insufficient (per `docs/architecture.md` non-goals and this issue's
  constraint to keep cloud/K8s optional until justified). Nothing in this worktree
  implements fleet management yet.
- **Demo command / example:** not yet exercised in this worktree — no fleet/GitOps
  tooling exists yet.
- **Exit criteria:** Kubernetes remains optional for local/single-node use; workload
  definitions portable across supported edge profiles; rollout/rollback documented and
  observable; fleet inventory exposes capabilities without vendor-specific core APIs
  (Phase 5 acceptance criteria, issue #10).
- **Dependencies newly required:** GitOps tooling and, optionally, K3s/Kubernetes — the
  only tier where a cluster dependency may appear, and only if justified.
- **Verification note:** `make verify` proves none of this tier's multi-node/fleet
  behavior; fleet claims require evidence from a real multi-node deployment.

## Roadmap phase mapping / 로드맵 단계 매핑

| Tier | Primary roadmap phase(s) | GitHub issue |
|---|---|---|
| S0 | Phase 1 — laptop-first vision pipeline | #1 |
| S1 | Phase 1 — laptop-first vision pipeline (real-sensor slice) | #1 |
| S2 | Phase 2 — simulation adapters and deterministic scenes | #7 |
| S3 | Phase 3 — edge runtime and NVIDIA Jetson profile | #8 |
| S4 | Phase 4 — robotics bridge and safe actuation | #9 |
| S5 | Phase 5 — cloud-native operations and fleet management; Phase 6 — AI skills, routing, simulation CI, fleet observability (builds on S5's fleet layer) | #10, #11 |

S0 and S1 both map to Phase 1 (issue #1) because Phase 1's scope covers "recorded video
and webcam inputs" together; S1 is the real-sensor slice of that same epic, not a
separate phase. Phase 6 (issue #11) is layered on top of the S5 fleet/observability
surface rather than introducing its own tier, per issue #11's requirement that
higher-level features stay "layered on stable sensor/event/action contracts."

S0와 S1은 모두 Phase 1(issue #1)에 대응한다. Phase 1의 범위가 "녹화 영상과 웹캠 입력"을
함께 다루기 때문이며, S1은 그중 실제 센서를 사용하는 부분을 가리킨다. Phase 6(issue
#11)은 별도 단계를 만들지 않고 S5의 플릿/관측성 위에 얹히는 계층이다.

## No-forward-dependency check / 선행 의존성 검증

Explicit statement required by acceptance criteria: **no tier's minimum requirements or
demo command depend on infrastructure introduced at a strictly later tier.**

- S0: laptop + Python only — introduces nothing later tiers must remove. ✓
- S1: adds a USB sensor — does not require S2 simulation, S3 edge, S4 actuation, or S5
  fleet infra. ✓
- S2: adds deterministic scenario fixtures — does not require S3 edge hardware or S4/S5
  infra; runs on the same laptop as S0/S1. ✓
- S3: adds ARM/x86/Jetson container builds — requires S1+S2 validated contracts but no
  S4 actuation or S5 GitOps/Kubernetes. ✓
- S4: adds ROS 2/MCU/actuator adapters — requires S3's edge runtime but no S5
  fleet/GitOps/Kubernetes. ✓
- S5: adds GitOps and optional Kubernetes — the only tier allowed to introduce a cluster
  dependency, and only because every earlier tier already works without one. ✓

## Relationship to README / architecture terminology

`README.md`'s "Deployment modes" language (Laptop / Simulation / Edge / Fleet) and
`docs/architecture.md`'s `Deployment modes` table map onto this tier model as follows:
Laptop mode → S0/S1, Simulation mode → S2, Edge mode → S3 (S4 sits on top of Edge mode
once actuation is added), Fleet mode (planned) → S5. This document is the canonical,
more granular breakdown; README and architecture docs link here rather than duplicating
tier detail.
