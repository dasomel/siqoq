# Evaluation: Pre-Physical-Execution Validation in a smolvm MicroVM (Phase A)

Tracks: #74.

> **Explicit Statement:**
> **No smolvm/libkrun microVM, or any other sandbox/isolation layer, is implemented,
> configured, or executed in this repository.** No `Vagrantfile`/VM image/`.smolvm`
> config, no isolation crate/dependency, and no CI job invoking a microVM exists today.
> Everything below is a read-only inventory of the current execution/loading surface and
> how it relates to physical actuation, as the grounding needed before any Phase B design
> work begins.

## Goal

Answer, with file/line evidence, whether Siqoq has a dynamic code/policy execution path
today that untrusted (AI- or user-generated) input can reach, trace every such path to
whether it can influence a physical action, and define the forbidden host/device
interfaces a future sandbox stage would need to block — without designing or
implementing the sandbox itself (Phase B–D).

## Headline finding: no dynamic code execution path exists today

Grepping `src/siqoq/*.py` for `subprocess`, `os.system`, `os.popen`, `eval(`, `exec(`,
`__import__`, `pickle`, `yaml.load`/`unsafe_load`, `Popen`, `entry_points`, `dlopen`, and
`ctypes` returns **zero matches**. `docs/security/model-and-policy-loading.md:3-4` states
this explicitly: *"Status: draft policy. No model/policy loading code exists yet (only
`src/siqoq/events.py`, `src/siqoq/cli.py`)."* `docs/specs/mcu-boundary-contract.md:3-4`
and `docs/specs/runtime-capability-outline.md:1-3` make the same "not implemented yet"
statement for the MCU adapter and capability registry respectively.

The only dynamic-name-resolution pattern in the codebase is an explicit, closed
allowlist, not open dispatch: `scenario.py:14-18`'s `_KNOWN_ERROR_TYPES` dict, whose
comment reads *"Kept as an explicit allowlist (not eval/getattr on arbitrary names) so a
catalog file can never be used to reference or construct an arbitrary type."*

This changes Phase B–D's scope: there is no existing "run generated code" feature to
retrofit a sandbox around. The smolvm stage would be **new infrastructure introduced
ahead of a dynamic-execution feature**, not a hardening of one that already ships. Any
Phase B design must first name the specific future feature (e.g. an ONNX model loader,
per `docs/security/model-and-policy-loading.md`, or a future skill/policy plugin loader)
that would actually need it, per `AGENTS.md`'s "avoid prematurely hardening" and "make
the smallest coherent change" rules.

## 1. Execution/loading path inventory

All file-accepting or data-loading entry points found in `src/siqoq/*.py`, in the order
`AGENTS.md`'s module list was checked:

| Symbol | File:line | What it loads | Mechanism |
|---|---|---|---|
| `WorkloadSpec.from_json` | `src/siqoq/workload.py:38-46` | Workload spec JSON | `json.loads` + dataclass field assignment |
| `ScenarioConfig.from_json` | `src/siqoq/scenario.py:40-50` | Scenario config JSON | `json.loads` + dataclass field assignment |
| `ScenarioConfig.build_adapter` | `src/siqoq/scenario.py:52-59` | Selects `GeneratedSensorAdapter` or `FixtureSensorAdapter` by string match | `if/elif` on a literal string, not `getattr`/`eval` |
| `load_catalog` | `src/siqoq/scenario.py:189-191` | Scenario/scene catalog JSON | `json.loads` |
| `CatalogEntry.from_dict` | `src/siqoq/scenario.py:166-178` | One catalog row | Plain dict field extraction |
| `run_catalog_entry` | `src/siqoq/scenario.py:194-201` | Resolves `entry.config_path` relative to `base_dir`, then calls `ScenarioConfig.from_json` | Path join + JSON load |
| `FixtureSensorAdapter.read` | `src/siqoq/sensors.py:121-140` | Recorded sensor sample JSONL | Line-by-line `json.loads` + `SensorSample.from_record` (schema-validated) |
| `RecordedVideoFileSensor` (frame fixture) | `src/siqoq/video_sensors.py:98-101` (`open()` reads a JSONL frame fixture; `read()` at lines 103-119 parses each line) | Recorded video frame JSONL | `json.loads` per line, `base64` frame payload decode |
| `UsbWebcamFrameSensor.read` (real camera) | `src/siqoq/video_sensors.py:155-172` (`open()`, deferred `cv2` import, `cv2.VideoCapture(self.device)` at line 163), `174-193` (`read()`) | Live USB/UVC camera frames | `cv2.VideoCapture.read()`; real hardware **input** path (camera capture), read-only — never writes to the device; requires the optional `vision` extra; not wired to any CLI/scenario/ui path today (`grep -rn UsbWebcamFrameSensor src/siqoq/*.py` shows only its own module and `gpio.py`'s docstring mention, no caller in `cli.py`/`scenario.py`/`ui.py`/`policy.py`/`actuation.py`) |
| `FixtureLidarSensor.read` | `src/siqoq/spatial_sensors.py:241-244` (`open()`), `246-261` (`read()`) | Recorded LiDAR scan JSONL | Line-by-line `json.loads`, not wired into `ScenarioConfig.build_adapter` (`scenario.py:52-59` only handles `"generated"`/`"fixture"` via `sensors.py`; `spatial_sensors` is never imported outside itself — confirmed by `grep -rn spatial_sensors src/siqoq/*.py`) |
| `FixtureDepthSensor.read` | `src/siqoq/spatial_sensors.py:288-291` (`open()`), `293-308` (`read()`) | Recorded depth-frame JSONL | Same as `FixtureLidarSensor`: `json.loads` per line, not wired into any scenario/CLI path |
| `FixtureImuSensor.read` | `src/siqoq/spatial_sensors.py:335-338` (`open()`), `340-356` (`read()`) | Recorded IMU sample JSONL | Same as above: `json.loads` per line, not wired into any scenario/CLI path |
| `FleetInventory.from_jsonl` | `src/siqoq/fleet.py:77-86` | Fleet node capability snapshots | Line-by-line `json.loads` + `FleetEntry.from_dict` |
| `aggregate_results` | `src/siqoq/fleet.py:129-155` | Per-node `ScenarioSummary` result files in a directory | `json.loads` per file, wrapped in `try/except (OSError, json.JSONDecodeError)` |
| `_load_nodes` | `src/siqoq/placement.py:34-37` | Node capability mapping JSON | `json.loads` + `RuntimeCapabilities(**values)` |
| `run_trace_build_command` | `src/siqoq/cli.py:81-102` | `SemanticEvent`/`ActionResult` JSON files named on the CLI (`--event-json`, `--action-json`) | `json.load` + dataclass construction (`SemanticEvent(**event_data)`) |
| `OnnxCvInferenceAdapter.__init__` | `src/siqoq/inference.py:81-93` | ONNX model file (path supplied by caller, no built-in CLI wiring today) | `onnxruntime.InferenceSession(str(model_path))`, deferred import; requires the optional `vision` extra |
| `_module_available` | `src/siqoq/capabilities.py:24-36` | Nothing external — probes `importlib.util.find_spec` for installed extras (`cv2`, `onnxruntime`, `nats`, `paho.mqtt.client`, `opentelemetry`) | Import probing only, never imports/executes the module |
| `run_ui_serve_command` / `ui.serve` | `src/siqoq/cli.py:117-130`, `src/siqoq/ui.py:164-179` | Reads fleet inventory/results/scenario catalog paths given on the CLI and serves them over `http.server` | `Path.exists`/`json.dumps`, stdlib `ThreadingHTTPServer`, GET-only HTTP surface (`do_GET` only, no `do_POST`/`do_PUT`/`do_DELETE` — confirmed by grep). **Fixed by #75**: `GET /api/snapshot` (`ui.py:146-149`) calls `_scenario_catalog_snapshot` (`ui.py:60-73`) → `run_catalog_entry(..., write_output=False)` (`ui.py:70`) → `run_scenario`, and `run_catalog_entry` with `write_output=False` now runs the scenario against a copy of its config with `output_path` cleared (`scenario.py:194-209`) instead of opening it for writing (`scenario.py:107-109`), so the read-only GET path no longer has a file-write side effect. It still re-runs every catalog scenario on each request; `docs/specs/web-dashboard.md:36`'s "no write endpoint" claim now holds for effects as well as HTTP methods |

No `subprocess`/process-spawn call, no deserialization of pickled/executable objects, and
no dynamic module import driven by file content exist anywhere in this list.
`OnnxCvInferenceAdapter` is the only path that loads a binary model artifact, and it is
not wired to any CLI subcommand or default construction path today — it must be
instantiated directly by a caller with a `model_path`.

## 2. Inputs that may be AI- or user-generated

| Input | Path | Trust rationale |
|---|---|---|
| Workload spec JSON | `workload.py:38` (`WorkloadSpec.from_json`) | User- or tooling-authored; issue #58 describes it as declarative and portable, i.e. meant to be authored outside the core team |
| Scenario config JSON | `scenario.py:40` (`ScenarioConfig.from_json`) | Same as above; also referenced from scenario/scene catalogs |
| Scenario/scene catalog JSON | `scenario.py:189` (`load_catalog`) | Test-authoring surface; `kind: "scene"` entries are explicitly a "bundle... standing in for a simulated environment" per `scenario.py:147-153` docstring |
| Sensor fixture JSONL | `sensors.py:127` (`FixtureSensorAdapter.read`) | Recorded/synthetic sensor samples; schema-checked field-by-field in `SensorSample.from_record` (`sensors.py:43-68`), no code paths |
| Video frame fixture JSONL | `video_sensors.py:98-119` (`RecordedVideoFileSensor`) | Same category as sensor fixtures |
| LiDAR/depth/IMU fixture JSONL | `spatial_sensors.py:241-261, 288-308, 335-356` (`FixtureLidarSensor`/`FixtureDepthSensor`/`FixtureImuSensor`) | Same category as sensor fixtures; not currently reachable via `ScenarioConfig`/CLI (see Table 1) |
| Fleet inventory JSONL | `fleet.py:77` (`FleetInventory.from_jsonl`) | Reports node capabilities; could be populated by an untrusted/compromised edge node in a future fleet deployment |
| Node capability mapping JSON | `placement.py:34` (`_load_nodes`) | Same category as fleet inventory |
| `SemanticEvent`/`ActionResult` JSON (trace CLI) | `cli.py:84-98` | Could originate from an untrusted upstream stage (e.g. inference output) replayed for RCA |
| Future: model/policy artifacts | Not implemented — see `docs/security/model-and-policy-loading.md:3` | Explicitly named by that draft policy as the highest-risk future AI-generated/downloaded input (ONNX weights, policy/config) |
| Future: MCU commands | Not implemented — see `docs/specs/mcu-boundary-contract.md:3` | Would be the output of a policy decision, not raw user input, but crosses into physical actuation |

Everything above is **schema-validated structured data (JSON/JSONL), never source code or
serialized objects**. There is no path today where an AI- or user-supplied *file* is
interpreted as executable logic; the closest analog is `ScenarioConfig.adapter`, a string
matched against a two-item allowlist (`scenario.py:52-59`).

## 3. Trust/reachability classification

| Path | Input source | Trust level | Reaches action path? | Evidence |
|---|---|---|---|---|
| `WorkloadSpec.from_json` → `validate_against` | User/tooling-authored file | Untrusted | No — only compares booleans, never invoked from `policy.py`/`actuation.py` | `workload.py:38-73`; no import of `policy`/`actuation` in `workload.py` |
| `ScenarioConfig.from_json` → `run_scenario` | User/tooling-authored file | Untrusted | Via `SafetyGate`/`decide()` | `scenario.py:96-136` calls `policy.decide()` at lines 114-118 (imported `scenario.py:10`) with `SafetyGate` gating every action |
| `load_catalog`/`run_catalog_entry` | User/tooling-authored file | Untrusted | Via `SafetyGate`/`decide()` (same as above, one hop further) | `scenario.py:194-204` calls `run_scenario` |
| `FixtureSensorAdapter`/`RecordedVideoFileSensor` | Recorded/synthetic fixture file | Untrusted (schema-checked) | Via `SafetyGate`/`decide()`, as the sensor feeding a scenario run | `sensors.py:121-140`; consumed by `scenario.build_adapter` (`scenario.py:52-59`) |
| `FixtureLidarSensor`/`FixtureDepthSensor`/`FixtureImuSensor` | Recorded/synthetic fixture file | Untrusted (not schema-validated the way `SensorSample.from_record` is) | No — `spatial_sensors.py` is never imported by `scenario.py`, `cli.py`, `ui.py`, `policy.py`, or `actuation.py` (`grep -rn spatial_sensors src/siqoq/*.py` returns nothing outside the module itself), so these adapters cannot currently feed `policy.decide()` at all | `spatial_sensors.py:229-368`; `scenario.py:52-59`'s `build_adapter` only constructs `GeneratedSensorAdapter`/`FixtureSensorAdapter` from `sensors.py` |
| `FleetInventory.from_jsonl`/`aggregate_results` | Node-reported or user file | Untrusted | No — feeds `siqoq fleet list/query/observe` CLI output and the read-only dashboard only | `fleet.py`; no import of `policy`/`actuation` anywhere in `fleet.py` |
| `_load_nodes`/`placement.place` | User-authored node mapping | Untrusted | No — pure filter/report, no action decision | `placement.py:1-8` (imports); no import of `policy`/`actuation` anywhere in `placement.py` |
| `run_trace_build_command` (trace CLI) | Upstream event/action JSON, replayed | Untrusted | No — read-only reconstruction of a *past* decision for display, never re-decided or re-executed | `cli.py:81-102`; `build_trace` (`trace.py:51-76`) only reads fields, calls no policy/actuation function |
| `OnnxCvInferenceAdapter.infer` | Model file + frame | Untrusted (not yet wired to any CLI/default path) | Would reach `policy.decide()` **if** wired into a real pipeline (its `Detection.to_semantic_event()` output matches what `policy.decide()` consumes), but no such wiring exists today | `inference.py:81-104`; no caller of `OnnxCvInferenceAdapter` exists outside tests (per grep of `src/siqoq/`) |
| `siqoq ui serve` dashboard | Fleet/scenario files named on CLI | Untrusted (files); dashboard HTTP surface is GET-only and, as of #75, side-effect-free | Reaches `SafetyGate`/`decide()` the same as direct CLI use. **Fixed by #75**: `_scenario_catalog_snapshot` calls `run_catalog_entry(..., write_output=False)`, which runs the scenario against a copy of its config with `output_path` cleared (`scenario.py:194-209`) instead of writing to `config.output_path` (`scenario.py:107-109`), so `GET /api/snapshot` no longer writes to the host filesystem. Still reaches only `MockActuatorAdapter` (no actuation) via `SafetyGate`. This confirms the "read-only, no write endpoints" characterization in this table and in `ui.py`'s module docstring/`docs/specs/web-dashboard.md:36` ("There is no write endpoint anywhere in this module") now holds for both HTTP *methods* (only `do_GET` exists) and *effects* (a `GET` no longer writes) | `ui.py:60-73` (`_scenario_catalog_snapshot` calls `run_catalog_entry` with `write_output=False`), `ui.py:132-159` (handler class defines only `do_GET`; `grep -n 'do_POST\|do_PUT\|do_DELETE' src/siqoq/ui.py` returns nothing), `scenario.py:194-209` (`run_catalog_entry`'s `write_output` parameter clears `output_path` via `dataclasses.replace`) |
| `UsbWebcamFrameSensor` (live camera) | Physical USB/UVC device | N/A (hardware input, not a file) | No — not wired into `ScenarioConfig.build_adapter` (`scenario.py:52-59`, only `"generated"`/`"fixture"`) or any CLI/`ui.py` path; reachable only by direct instantiation (same unwired status as `OnnxCvInferenceAdapter`) | `video_sensors.py:134-207`; grep of `cli.py`/`scenario.py`/`ui.py`/`policy.py`/`actuation.py` shows no reference |
| `policy.decide()` | `SemanticEvent` (from any adapter above) | N/A (internal) | **Is** the SafetyGate boundary | `policy.py:47-65`; `_ACTION_BY_TYPE` is a closed dict (`policy.py:15-17`), `mock` is pinned `True` (`policy.py:34`) |
| `MockActuatorAdapter.execute` | `MockAction` from `decide()` | N/A (internal) | Terminal "action" step, but no I/O | `actuation.py:48-70`; a module-level `#:` comment block (`actuation.py:11-18`, not a docstring — `actuation.py` has no module docstring) states it is "the ONLY place `policy.decide()` output is wired to something that 'executes' an action," and performs no I/O |
| GPIO (`gpio.py`) | N/A | N/A | Not reachable at all — `RealGpioAdapter.open()` raises `NotImplementedError` unconditionally, and no module imports `gpio.py` outside tests | `gpio.py:101-108`; grep of `src/siqoq/*.py` shows no `from .gpio import` / `import siqoq.gpio` outside `gpio.py` itself |
| `RealLidarSensor` (`spatial_sensors.py`) | N/A | N/A | Not reachable at all — same unimplemented-stub pattern as `RealGpioAdapter`: `open()` unconditionally raises `NotImplementedError`, and (per the row above) `spatial_sensors.py` is never imported elsewhere in `src/siqoq/` | `spatial_sensors.py:382-388` |
| MCU adapter | N/A | N/A | Does not exist | `docs/specs/mcu-boundary-contract.md:3-4` |

**Summary of the "reaches action path?" column:** every path that can influence
`policy.decide()`'s output goes through `SafetyGate`, and every `MockAction` that reaches
`actuation.py` terminates in `MockActuatorAdapter`, which performs **no I/O of any kind**
(`actuation.py:48-70`). There is currently no code path — direct or via SafetyGate — that
reaches a real actuator, GPIO pin, or MCU, because none of those adapters exist yet
(`gpio.py`'s `RealGpioAdapter` and the MCU boundary are both unimplemented stubs).

## 4. Forbidden host/device interfaces during sandbox execution

Scoped to what the current code actually touches or is documented to touch next, per the
issue's instruction to tie this to real usage rather than a generic hardening checklist:

| Interface | Forbid in sandbox? | Why (evidence) |
|---|---|---|
| Outbound network | Yes, except an explicit allowlisted fetch during artifact load | Nothing in `src/siqoq/*.py` opens an *outbound* socket today (`transport.py`'s `NatsTransport`/`MqttTransport` require a caller-supplied, already-connected client — `transport.py:88-96, 113-121` — so the transport module itself never dials out). Correction: this is narrower than a blanket "nothing opens a socket" claim — `ui.serve` does bind a *listening* (inbound) socket for the dashboard HTTP server via `ThreadingHTTPServer((host, port), ...)` (`ui.py:172`), host configurable with `--host` (`cli.py:250`, default `127.0.0.1`). That's inbound/local, not outbound, and out of scope for this "outbound network" row, but is a real socket and belongs in the sandbox's threat model regardless of direction. `docs/security/model-and-policy-loading.md:48-52` (rule 7) already mandates "network access restricted to the allowlisted source during fetch only (no ambient network authority during inference/decision)" for the future model/policy loader this sandbox would front |
| Serial/USB/GPIO/`/dev/*` | Yes, unconditionally | Correction: only **two** `/dev/*` literals exist in `src/siqoq/` today (confirmed by `grep -rn '/dev/' src/siqoq/*.py`): `gpio.py:99` (`RealGpioAdapter.chip = "/dev/gpiochip0"`) and `spatial_sensors.py:380` (`RealLidarSensor.device = "/dev/lidar0"`) — both still documented `NotImplementedError` stubs (`gpio.py:101-108`, `spatial_sensors.py:382-388`), never real hardware access. `UsbWebcamFrameSensor` no longer has a `/dev/*` literal or a stub body: `device` now defaults to `0` (`video_sensors.py:147`) and `open()` calls `cv2.VideoCapture(self.device)` (`video_sensors.py:163`) — a real, read-only camera **input** path (requires the `vision` extra), not an actuation path, and not currently wired into any CLI/scenario/`ui.py` flow (see Table 1/3 above). Issue #74's own non-goals list USB/GPIO passthrough; a future sandbox must still forbid camera/`/dev/*` device access even though this path is unreachable from Siqoq's own code today |
| Host filesystem mounts (outside a scoped scratch/cache dir) | Yes, except a read-only pinned artifact cache | `docs/security/model-and-policy-loading.md:48-52` (rule 7) already specifies "a scoped read-only artifact cache directory, no writes outside it" for artifact loading — the sandbox should enforce exactly this scope, not host-wide access |
| Environment variables / secrets | Yes | No `src/siqoq/*.py` module reads `os.environ` today (absent from the grep results); nothing currently depends on ambient secrets, so a sandboxed load should start from an empty/allowlisted env by default |
| System clock / wall-clock assumptions | Isolate, do not forbid outright | `docs/specs/simulation-adapter-contract.md:43-44` already requires "No wall-clock leakage into any value that is hashed or compared in a test or scenario summary"; `GeneratedSensorAdapter`'s deterministic mode (`sensors.py:98-118`, fixed `timestamp`) is the existing pattern to reuse rather than trusting the VM's clock for reproducibility |
| Process spawning inside the sandboxed code itself | Yes | No `subprocess`/`Popen` call exists in `src/siqoq/*.py` today (confirmed by grep); a sandboxed artifact/policy load should not need to spawn child processes, and any future need is itself a design-change trigger per `docs/security/model-and-policy-loading.md:44-47` (rule 6, "No remote code execution") |
| Direct actuator/MCU authority from inside the VM | Yes, absolutely | This is the core purpose of the proposed stage: the smolvm run must never hold `ActuatorAdapter`/GPIO/MCU authority. Today this is enforced by absence (no adapter exists to grant), but the sandbox boundary must make it structural, not incidental, once adapters are implemented |
| Real-time/low-latency guarantees | Non-goal, per issue #74 | `docs/specs/mcu-boundary-contract.md`'s fail-safe section already places real-time safety obligations on MCU firmware, not Siqoq software, for exactly this reason — a microVM has no business making real-time claims either |

## Where the sandbox stage would sit relative to SafetyGate

Per issue #74's own pipeline (generated/user code → smolvm isolated execution →
simulation/static/runtime checks → SafetyGate → explicit approval/policy → physical
action), the natural insertion point in the existing code is **upstream of, and separate
from**, `policy.SafetyGate`:

```
[future: AI/user-generated policy, model, or skill artifact]
        |
        v
[Phase B: smolvm isolated execution]  <-- does not exist today; net-new
        |
        v
[Phase C: simulation/static/runtime checks]  <-- ScenarioCatalog / run_catalog_entry
        |                                          already provide the "run against a
        |                                          simulated fixture and assert an
        |                                          outcome" pattern (scenario.py:189-255)
        v
SemanticEvent  --->  policy.decide()  --->  SafetyGate.approve()  --->  MockAction
                                                                            |
                                                                            v
                                                            actuation.MockActuatorAdapter
                                                            (no I/O; real adapter = future,
                                                             high-risk design change)
```

`SafetyGate` (`policy.py:37-44`) is unchanged by this proposal: it remains the
authoritative, mock-only decision gate. The microVM is strictly a **containment
mechanism for code/artifact execution that happens before a `SemanticEvent` or
`MockAction` ever exists**, not a replacement decision-maker. This matches issue #74's
explicit statement that the VM is containment/validation, not a SafetyGate replacement.

## Gaps Phase B–D would need to fill

1. **No artifact loader to sandbox yet.** `docs/security/model-and-policy-loading.md`
   defines rules for a loader that does not exist (`model-and-policy-loading.md:3-4`).
   Phase B cannot design a microVM boundary around a load path until that loader (or an
   equivalent dynamic-skill/policy mechanism) has an approved design — otherwise the
   sandbox has nothing concrete to isolate.
2. **No signature/provenance scheme chosen.** Flagged as an open gap in
   `docs/security/model-and-policy-loading.md`'s "Gaps flagged" section — needed before
   integrity verification (rule 4) can gate sandbox exit.
3. **No `RuntimeCapabilities` field for sandbox/isolation availability.** The existing
   `RuntimeCapabilities` dataclass (`capabilities.py:44-54`) has no
   `sandbox_extra_available`-style field; Phase B would need to decide whether smolvm
   availability is a capability like `vision_extra_available` (`capabilities.py:78`,
   detected via `_extra_available`) or an entirely separate discovery mechanism, since
   smolvm/libkrun is a host binary/VMM dependency, not a Python import.
4. **No defined output contract from the sandbox back to Siqoq.** `ScenarioSummary`
   (`scenario.py:62-85`) is the closest existing "structured, hashable result of a bounded
   run" shape; Phase B should evaluate reusing that shape (or a variant) as the sandbox's
   result envelope rather than inventing a new one, per `AGENTS.md`'s "preserve explicit
   interfaces" guidance.
5. **No policy on what happens when smolvm itself is unavailable** (e.g. non-Linux dev
   laptop, no libkrun installed). The existing pattern for optional
   hardware/dependency-gated features is "fail closed and report unavailable" (e.g.
   `ui.py:46-56`'s `_fleet_inventory_snapshot` for a missing file, or
   `gpio.py:101-108`'s `NotImplementedError` for unimplemented real hardware) — Phase B
   should decide whether a missing sandbox degrades to "cannot validate, refuse to
   proceed to SafetyGate" (fail closed, consistent with
   `model-and-policy-loading.md:56-58` rule 9) rather than silently skipping isolation.
6. **CI/dev-workstation feasibility is unverified.** No `make verify` target, Dockerfile
   stage, or CI job references smolvm/libkrun today (`Makefile:1-57`, `Dockerfile:1-25`
   checked); Phase B needs to establish whether microVM execution is feasible inside the
   existing CI containers before committing to it as a hard gate.

## Phase B feasibility: smolvm/libkrun (surveyed 2026-09-28)

**smolvm is not installed on this evaluation host; nothing in this section was executed
locally.** Everything below is a documentation survey of the upstream project (source
links inline), not a local test — every runtime/CLI claim is marked "per upstream docs,
not exercised."

**Project status.** smolvm (`github.com/smol-machines/smolvm`, Apache-2.0): latest
release `v1.19.3` (2026-09-27); `v1.19.1`–`v1.19.3` shipped within two days of each other —
a fast-moving project, so any PoC must pin an exact version rather than tracking `latest`.

**Host support.**

| Host | Backend | Notes |
|---|---|---|
| macOS arm64 | Hypervisor.framework | No documented equivalent-strength sandboxing beyond the hypervisor itself (see threat model below) |
| Linux | KVM (`/dev/kvm`) | Required for VM boot |
| GitHub-hosted runners | Generally unusable | smolvm's own CI skips VM tests on hosted runners — a CI hard gate on this repo would need self-hosted/KVM-capable runners |
| Inside Docker | Needs `--device /dev/kvm` on a Linux host | Not possible from Docker Desktop on macOS; relevant to this repo's existing `Dockerfile`/`ci.yml`, which builds linux/amd64+arm64 images today |

**Image/network/mount model (per upstream docs, not exercised).**
- Boots a pinned OCI image by digest (`--image repo@sha256:<digest>`).
- Networking is disabled by default — quoting smolvm's `docs/security-model.md`:
  *"Networking is disabled by default."*
- Host mounts require explicit `-v`; protected host config/log trees are blocked unless
  `--allow-system-mounts`.
- No USB/GPIO/PCI passthrough — virtio devices only. virtio-vsock is reported (per this
  survey, **not locally verified**) to always be on, because the in-guest `smolvm-agent`
  control channel needs it.

**Evidence surface (per upstream docs, not exercised).** Guest exit code is forwarded to
the host; `exec --timeout` returns `124` on timeout; smolvm's own version is available via
`smolvm --version`; the booted image's digest is available via machine-status JSON.
**Gap:** libkrun's version is not exposed at runtime — it's build-time provenance only —
which is a gap against issue #74 Phase C's "record smolvm/libkrun versions" evidence
requirement.

**Threat model (verbatim quotes).**

> "The libkrun security model is primarily defined by the consideration that both the
> guest and the VMM pertain to the same security context." — and — "Think about the guest
> and the VMM as a single entity. To prevent the guest from accessing host's resources, you
> need to use the host's OS security features to run the VMM inside an isolated context."
> (libkrun maintainer `slp`, https://github.com/libkrun/libkrun/discussions/538)

The same maintainer advises that, for completely untrusted payloads, libkrun needs
*additional* host-side isolation — Linux namespaces (as `crun`+libkrun does) — and advises
avoiding virtio-fs, virtio-gpu, and virtio-vsock. This is in tension with smolvm's
always-on vsock control channel noted above.

> "The `smolvm` CLI and VMM processes run with the permissions of the invoking host
> user." — and — "Releases are not currently signed or accompanied by provenance
> attestations, and the installer permits installation when the checksum file cannot be
> downloaded." (smolvm `docs/security-model.md`)

**Implications for #74** (keep concise):
1. smolvm alone is **not** a sufficient containment boundary for untrusted code ahead of a
   physical-action path — the VMM must itself run under host OS confinement (a dedicated
   unprivileged user; namespaces/seccomp/Landlock on Linux). There is no documented
   equivalent-strength option on macOS, so a macOS dev-laptop run is a convenience, not a
   security boundary.
2. The host process running the VMM must hold **no** actuator/GPIO/serial authority at
   all, because guest ≈ VMM ≈ invoking host user under this model.
3. Supply chain: pin the binary by exact version and verify its checksum out-of-band —
   releases are unsigned and the installer can silently skip checksum verification.
4. `SafetyGate` stays the independent authority: sandbox success never authorizes a
   physical action (that remains issue #74 Phase D, unchanged by this survey).

**Alternatives (survey-level only, not evaluated):**

| Alternative | One-line note |
|---|---|
| Firecracker | Hardened multi-tenant VMM with `jailer`; Linux/KVM only |
| gVisor | User-space kernel sandbox; Linux only |
| Kata Containers | VM-isolated OCI runtime; heavier than a plain container |
| krunvm | Same libkrun trust model/caveats as smolvm |
| Apple Virtualization.framework | macOS only |

## Recommendation

Proceed to Phase B, but scope it narrowly: Phase B's first deliverable should be
**naming the specific artifact type(s) the sandbox will contain** (most likely: ONNX
model loading per `docs/security/model-and-policy-loading.md`, since that is the only
future dynamic-artifact path already documented) rather than a general-purpose "run
arbitrary code" sandbox. Building smolvm isolation before any dynamic-execution feature
exists would itself violate `AGENTS.md`'s "avoid prematurely hardening one hardware/vendor
path" and "do not introduce fleet/GitOps complexity before the single-node/software-first
path needs it" — the same reasoning `docs/evaluations/digital-twin-validation.md` applied
to recommend "adopt-later" for digital-twin validation. Revisit Phase B once either (a)
the model/policy loader in `docs/security/model-and-policy-loading.md` has an accepted
Change Package, or (b) a concrete skill/policy-plugin mechanism is proposed that would
execute user- or AI-authored logic beyond today's schema-validated JSON/JSONL configs.

When Phase B starts, its Change Package is Class D per `AGENTS.md` (release/deployment/
security-boundary change) and must include, per the smolvm/libkrun survey above: (a) a
host-level VMM confinement design (dedicated unprivileged user plus namespaces/seccomp/
Landlock on Linux; an explicit statement that macOS offers no equivalent-strength option);
(b) a decision on KVM-capable CI/self-hosted runners, since GitHub-hosted runners cannot
run smolvm's VM tests; (c) a binary pinning/checksum policy, since smolvm releases are
unsigned; and (d) how the libkrun-version evidence gap (not exposed at runtime) is closed
before Phase C's version-recording requirement can be satisfied. If smolvm/libkrun's
same-security-context model is judged unacceptable for this use case, Phase B should
consider Firecracker+jailer or gVisor on Linux instead.
