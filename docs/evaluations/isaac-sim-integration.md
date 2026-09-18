# Evaluation: NVIDIA Isaac Sim integration spike

Status: evaluation only. No Isaac Sim capability is implemented, and no code or
dependency has been added to this repository as a result of this document.
See issue #42 (part of #7).

## What Isaac Sim provides for synthetic sensor data

Isaac Sim is NVIDIA's Omniverse Kit-based robotics simulator. Relevant to Siqoq's
camera/sensor path:

- **Camera prims + render products.** A camera sensor is a USD prim; camera data
  (RGB, depth, semantic/instance segmentation, bounding boxes, normals) is pulled
  off a "render product" attached to that prim. Render products can be created by
  several extensions, most commonly `omni.replicator` (the "Replicator" synthetic
  data toolkit).
- **`isaacsim.sensors.camera.Camera`** (namespace-packaged Python API) wraps prim
  creation, render product attachment, and per-frame data retrieval (`get_rgba()`,
  `get_depth()`, etc.) for both the GUI and standalone-Python workflows.
- **Replicator annotators** attach to a render product to emit specific channels
  (RGB, depth, segmentation, bounding box, normals) and support lens-distortion
  models (fisheye, OpenCV-style, LUT) and calibration-to-Omniverse-unit conversion
  — i.e. it can be tuned to approximate a specific real lens.
- **Standalone Python mode.** Isaac Sim ships as `isaacsim` namespace packages
  installable with `pip install isaacsim[extscache]==<version> --extra-index-url
  https://pypi.nvidia.com`, letting a script boot a minimal Kit app headlessly and
  drive cameras without the full GUI editor.

Sources: [Camera Sensors — Isaac Sim docs](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/sensors/isaacsim_sensors_camera.html), [What Is Isaac Sim? — standalone Python](https://docs.omniverse.nvidia.com/isaacsim/latest/manual_standalone_python.html), [Python Environment Installation](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/installation/install_python.html), [isaac-sim/IsaacSim on GitHub](https://github.com/isaac-sim/IsaacSim).

## What a SensorAdapter-conformant wrapper would need

Per `docs/specs/sensor-contract.md` (Sensor Contract v0), Siqoq has two layers:
`SensorAdapter.read(count) -> Iterator[SemanticEvent]` (event-level) and
`FrameSensor` (`open`/`read`/`close`, frame-level, `Frame` = normalized
`FrameMetadata` + `bytes` payload, no vendor SDK type in the contract).

Isaac Sim's `Camera.get_rgba()`/`get_depth()` output is frame-level, not
pre-classified events, so it maps to `FrameSensor`, not directly to
`SensorAdapter`:

1. **`IsaacSimFrameSensor` (new, adapter-side only).** Implements `open()` (start
   the Kit app / simulation, create the camera prim + render product),
   `read()` (step simulation, pull the current RGBA/depth buffer, wrap it as
   `Frame(metadata=FrameMetadata(...), payload=<raw bytes>)`, return `None` once
   the scenario/timeline ends), and `close()` (idempotent teardown of the Kit
   app). No `omni.*`, `pxr` (USD), or Replicator type crosses into the return
   value — only the existing `Frame`/`FrameMetadata` shape.
2. **Existing `InferenceAdapter` (`siqoq.inference`), unmodified.** Turns the
   normalized `Frame` into `SemanticEvent`s exactly as it already does for
   `RecordedVideoFileSensor`/webcam sources.
3. **Bridge to `SensorAdapter`.** `docs/specs/sensor-contract.md` already notes
   Siqoq has no shipped `FrameSensor + InferenceAdapter -> SensorAdapter` bridge
   yet ("a straightforward, non-breaking follow-up"). Isaac Sim would be the
   first consumer that makes that bridge necessary, not something Isaac
   Sim-specific — building it once benefits webcam/recorded sources too.
4. **Isolation.** All Omniverse/USD/Replicator imports stay inside the new
   `IsaacSimFrameSensor` module (e.g. `siqoq.video_sensors.isaac_sim`, imported
   lazily). Nothing in `siqoq.sensors`, `siqoq.video_sensors`'s core Protocols,
   or the semantic event contract references Isaac Sim types — consistent with
   AGENTS.md's "keep virtual and physical adapters behind stable interfaces."

## Licensing, hardware, and optionality

- **License.** Isaac Sim (with Omniverse Kit) is free for internal R&D/development
  use. A separate NVIDIA AI Enterprise license is only required if Isaac
  Sim/Omniverse Kit itself is redistributed to third parties or offered as a
  service to third parties — not applicable to using it as a local dev/test tool.
  ([License FAQ](https://docs.isaacsim.omniverse.nvidia.com/6.0.0/common/license-faq.html), [Isaac Sim licensing](https://docs.isaacsim.omniverse.nvidia.com/5.0.0/common/licenses-isaac-sim.html))
- **GPU requirement.** Isaac Sim requires an RT Core-capable NVIDIA GPU (data-center
  cards without RT Cores, e.g. A100/H100, are explicitly unsupported) and
  meaningful VRAM; it does not run on CPU-only laptops or non-NVIDIA GPUs.
  ([Isaac Sim Requirements](https://docs.isaacsim.omniverse.nvidia.com/6.0.0/installation/requirements.html))
- **Optionality.** Yes — cleanly, if confined to the isolation pattern above. An
  `IsaacSimFrameSensor` module can be import-guarded (only imported when
  explicitly selected) and excluded from the base install's dependency set, so
  the laptop-only path (`RecordedVideoFileSensor`, `MockWebcamFrameSensor`,
  `UsbWebcamFrameSensor`) is entirely unaffected whether or not Isaac Sim is
  present.

## Dependency footprint

No lightweight pip client exists for talking to a *running* Isaac Sim instance
over a network protocol the way one might for a database. Two real options,
both heavy:

1. **Standalone Python** — `pip install isaacsim[extscache]==<version>
   --extra-index-url https://pypi.nvidia.com` boots an embedded Kit application
   in-process. This is still a multi-GB install (renderer, USD, Kit extensions)
   requiring the GPU above, even headless.
2. **Full Isaac Sim application** running separately (GUI or headless container),
   driven via its Script Editor or an external connection.

There is no way to get Isaac Sim camera data with a small, pure-Python,
CPU-only dependency. Either path pulls in the full Omniverse/Kit/USD stack.
State this plainly to avoid under-selling the footprint: this is an
optional, GPU-bound, multi-GB adapter, not a normal pip extra.

## Recommendation: adopt later, behind an optional adapter

Do not adopt now. Reasoning:

- Siqoq's MVP contracts (`SensorAdapter`, `FrameSensor`) are still draft/v0 and
  being validated on lightweight sources (recorded video, mock/USB webcam).
  Isaac Sim's heavy footprint and GPU requirement would violate "simulation
  first... developable without physical hardware on day one" if pulled in now,
  and there's no `FrameSensor -> SensorAdapter` bridge yet to attach it to.
- Nothing about Isaac Sim's API is incompatible with the existing contracts —
  the frame-level shape (RGBA/depth buffer + metadata) maps cleanly onto
  `Frame`/`FrameMetadata` with no design change needed later.
- The licensing and optionality story is favorable (free for R&D, cleanly
  isolatable), so there is no reason to reject it outright — only to defer.

## Next steps if adopted later

1. Ship the `FrameSensor + InferenceAdapter -> SensorAdapter` bridge as a
   general improvement first (benefits recorded/webcam sources too, decouples
   it from Isaac Sim specifically).
2. Add `IsaacSimFrameSensor` in its own module, guarded so it is only imported
   when explicitly configured; add `isaacsim` as an optional extra (e.g.
   `siqoq[isaac-sim]`), never a base dependency.
3. Validate against the existing `tests/test_sensors.py`-style conformance
   suite using a CI-skippable marker (Isaac Sim needs an RT Core GPU CI runners
   are unlikely to have); document the specific simulation path exercised per
   AGENTS.md's verification section ("a green Python gate does not prove...").
4. Confirm current license terms and GPU requirements again at implementation
   time — Isaac Sim versioning and NVIDIA's licensing FAQ have both changed
   across recent releases (4.x → 6.0.0 docs already differ), so this
   evaluation's citations should be re-checked before code is written.
